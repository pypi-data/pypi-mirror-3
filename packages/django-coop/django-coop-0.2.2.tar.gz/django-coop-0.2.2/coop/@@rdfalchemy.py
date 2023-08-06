# -*- coding:utf-8 -*-

import rdflib, rdfalchemy
from rdflib import Namespace, plugin
from rdflib import ConjunctiveGraph as Graph

FOAF = Namespace("http://xmlns.com/foaf/0.1/")

graph = Graph()
graph.parse("http://danbri.org/foaf.rdf")

# tester les données

# plugin.register(
#     "sparql", rdflib.query.Processor,
#     "rdfextras.sparql.processor", "Processor")
# plugin.register(
#     "sparql", rdflib.query.Result,
#     "rdfextras.sparql.query", "SPARQLQueryResult") 

# for row in g.query('SELECT ?a ?b ?aname ?bname WHERE { ?a foaf:knows ?b . OPTIONAL { ?a foaf:name ?aname . ?b foaf:name ?bname . } }',initNs={'foaf':FOAF}):
#     print "friend: %s" % row[1]


class Person(rdfalchemy.rdfSubject):
  rdfalchemy.rdfSubject.db = graph
  rdf_type = FOAF.Person
  name = rdfalchemy.rdfSingle(FOAF.name)
  mbox = rdfalchemy.rdfSingle(FOAF.mbox)


for p in Person.ClassInstances():
    print p.name

