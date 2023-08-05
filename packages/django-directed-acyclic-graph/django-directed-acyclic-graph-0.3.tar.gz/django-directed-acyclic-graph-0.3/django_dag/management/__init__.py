from django.db import connection, transaction
from django.db.models import signals
from django_dag import models

def create_tables_and_triggers(sender, **kwargs):
    if sender != models:
        return
    cursor = connection.cursor()
    
    # Test if plpgsql is installed
    TEST_PLPGSQL_SQL = """select count(*) from pg_language where lanname = 'plpgsql'"""
    cursor.execute(TEST_PLPGSQL_SQL)
    plpgsql_installed = cursor.fetchone()[0]
    if not plpgsql_installed:
        INSTALL_PLPGSQL_SQL = """CREATE TRUSTED PROCEDURAL LANGUAGE 'plpgsql' HANDLER plpgsql_call_handler VALIDATOR plpgsql_validator"""
        cursor.execute(INSTALL_PLPGSQL_SQL)
        transaction.commit_unless_managed()
    
    # Exit if already installed
    TEST_FUNCTION_EXISTS = """SELECT count(*) FROM pg_proc where proname = 'enforce_acyclicity'"""
    cursor.execute(TEST_FUNCTION_EXISTS)
    if cursor.fetchone()[0]:
        return
    
    try:
        transaction.enter_transaction_management()
        transaction.managed(True)
        # Set default depth to 0 for database triggers
        DEFAULT_DEPTH_SQL = """alter table dag_transitive_closure alter column depth set default 0"""
        cursor.execute(DEFAULT_DEPTH_SQL)
    
        ADD_EDGE_CHECK_SQL = """ALTER TABLE dag_edge ADD CHECK (node_to_id <> node_from_id)"""
        cursor.execute(ADD_EDGE_CHECK_SQL)
    
        TRANSITIVE_CLOSURE_INDEX_1_SQL = """create index idx_trans_from_graph_to on dag_transitive_closure(node_from_id, graph_id, node_to_id)"""
        cursor.execute(TRANSITIVE_CLOSURE_INDEX_1_SQL)
    
        TRANSITIVE_CLOSURE_INDEX_2_SQL = """create index idx_trans_to_graph on dag_transitive_closure(node_to_id, graph_id)"""
        cursor.execute(TRANSITIVE_CLOSURE_INDEX_2_SQL)
    
        ENFORCE_ACYCLICALITY_FUNCTION = """create function enforce_acyclicity() returns trigger as
        $$
        begin

        if exists(select 1 from dag_transitive_closure where node_to_id=NEW.node_from_id and node_from_id=NEW.node_to_id and graph_id=NEW.graph_id) then
            raise exception 'Inserting (%%,%%) will create a loop.', NEW.node_from_id, NEW.node_to_id;
        end if;

        return NEW;

        end;
        $$ language plpgsql"""
        ENFORCE_ACYCLICALITY_TRIGGER = """create trigger trig_enforce_acyclicity before insert on dag_edge
            for each row execute procedure enforce_acyclicity()"""
        # TODO: Fix. Gives strange error.
        cursor.execute(ENFORCE_ACYCLICALITY_FUNCTION)
        cursor.execute(ENFORCE_ACYCLICALITY_TRIGGER)

        ADD_IMPLIED_EDGES_FUNCTION = """create function add_implied_edges() returns trigger
            as $$
            declare
                id int;
            begin
                id := nextval('dag_transitive_closure_t_edge_id_seq');
                insert into dag_transitive_closure (node_from_id, node_to_id, graph_id, entry_id, direct_id, exit_id, t_edge_id) values (new.node_from_id, new.node_to_id, new.graph_id, id, id, id, id);

                insert into dag_transitive_closure (direct_id, exit_id, entry_id, node_from_id, node_to_id, graph_id, depth)

                    -- Incoming edges.
                    select id, id, t_edge_id, node_from_id, new.node_to_id, new.graph_id, depth + 1
                        from dag_transitive_closure
                        where node_to_id = new.node_from_id
                              and graph_id=new.graph_id

                    union

                    -- Outgoing edges.
                    select id, t_edge_id, id, new.node_from_id, node_to_id, new.graph_id, depth + 1
                        from dag_transitive_closure
                        where node_from_id = new.node_to_id
                              and graph_id=new.graph_id

                    union

                    -- Incoming to outgoing.
                    select a.t_edge_id, id, b.t_edge_id, a.node_from_id, b.node_to_id, new.graph_id, a.depth + b.depth + 1
                        from dag_transitive_closure a
                             cross join dag_transitive_closure b
                        where a.node_to_id = new.node_from_id and b.node_from_id = new.node_to_id
                              and a.graph_id=new.graph_id and b.graph_id=new.graph_id;

                return null;
            end;
            $$ language plpgsql"""
        ADD_IMPLIED_EDGES_TRIGGER = """create trigger trig_add_implied_edges after insert on dag_edge
            for each row execute procedure add_implied_edges()"""
        REMOVE_IMPLIED_EDGES_FUNCTION = """create function remove_implied_edges() returns trigger
            as $$
            begin
                create temporary table purge_list as
                    -- The direct edge.
                    select direct_id as t_edge_id
                    from dag_transitive_closure
                    where node_from_id = old.node_from_id
                          and node_to_id = old.node_to_id
                          and graph_id = old.graph_id;
                while true
                loop
                    insert into purge_list
                    -- Edges dependant of those in the purge list.
                    select t_edge_id
                        from dag_transitive_closure
                        where
                            depth > 0
                            and t_edge_id not in ( select t_edge_id from purge_list )
                            and (
                                entry_id in ( select t_edge_id from purge_list )
                                or exit_id in ( select t_edge_id from purge_list )
                            );
                    if not found then
                        exit;
                    end if;
                end loop;
                delete from dag_transitive_closure
                    where t_edge_id in (
                        select t_edge_id
                        from purge_list
                    );
                drop table purge_list;
                return null;
            end;
            $$ language plpgsql"""
        REMOVE_IMPLIED_EDGES_TRIGGER = """create trigger trig_remove_implied_edges after delete on dag_edge
            for each row execute procedure remove_implied_edges()"""
    
        cursor.execute(ADD_IMPLIED_EDGES_FUNCTION)
        cursor.execute(ADD_IMPLIED_EDGES_TRIGGER)
        cursor.execute(REMOVE_IMPLIED_EDGES_FUNCTION)
        cursor.execute(REMOVE_IMPLIED_EDGES_TRIGGER)
        transaction.commit()
        print "Triggers and tables created successfully"

    except:
        import traceback        
        print traceback.print_exc()
        transaction.rollback()
    
    finally:
        transaction.leave_transaction_management()

signals.post_syncdb.connect(create_tables_and_triggers, 
    dispatch_uid='django_dag.starter.init.tables')