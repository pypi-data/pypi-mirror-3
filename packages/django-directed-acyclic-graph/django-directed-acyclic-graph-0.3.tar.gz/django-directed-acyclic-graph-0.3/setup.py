from distutils.core import setup

setup(
    name='django-directed-acyclic-graph',
    version='0.3',
    author='Chris Mutel',
    author_email='cmutel@gmail.com',
    url='https://bitbucket.org/cmutel/django-directed-acyclic-graph',
    packages=['django_dag', 'django_dag.management', 'django_dag.tests'],
    license='LICENSE.txt',
    long_description=open('README.txt').read(),
)
