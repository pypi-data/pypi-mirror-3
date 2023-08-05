from django.db import models
from dag.mixins import GraphMixin

class City(GraphMixin):
    name = models.TextField(unique=True)

    def __unicode__(self):
        return self.name

class Color(GraphMixin):
    name = models.TextField(unique=True)
    
    def __unicode__(self):
        return self.name
