#%% [makrdown]
# #Cognitve Tasks Corpus
# This notebook creates a corpus for text analysis of cognitive tasks. It fetches and stores all related PymbMed articles for a set of tasks extected from an ontology.

import owlready2

def load_ontology(path):
  """Loads an OWL ontology from the path, and returns an OwlReady2 World with the  ontology loaded into it.  
  """
  ontology = owlready2.default_world.get_ontology(path).load()
  return ontology

def get_subclasses(
  ontology_path, 
  parent_class, 
  annotation='rdfs:label', 
  nested=False,
  ):
  """Find all subclasses of a given parent_class in an ontology."""

  # either use ':Class' or 'Class' notation
  class_name = parent_class[1:] if parent_class.startswith(":") else parent_class


  #FIXME valid only when ontology is already loaded into the default world
  graph = owlready2.default_world.as_rdflib_graph()
  base_iri = ontology.base_iri

  sparql_query = f"""
    PREFIX : <{base_iri}>

    SELECT ?label
    WHERE {{
    ?task rdfs:subClassOf{'*' if nested else ''} :{class_name};
            {annotation} ?label
    }}
    """

  labels = [labels for labels in graph.query(sparql_query)]
  flatten_labels = [l.toPython() for ll in labels for l in ll]
  return flatten_labels


# main call

ontology = load_ontology('ontologies/efo.owl')
tasks = get_subclasses(ontology, ":CognitiveTask")
print('Loaded',len(tasks), 'tasks from the ontology.')
