#%% [markdown]
# The following codes query the EFO ontology and retrives tasks and concepts that are assigned with readable labels. Then search PubMed Central for the number of articles on

#%%
# pip install rdflib
from rdflib import OWL, Graph
from rdflib.util import guess_format
from rdflib.namespace import RDFS

from owlready2 import *

import time

from rdflib import URIRef

import random

import pandas as pd

import os

owl_path = "file:///Users/morteza/workspace/ontologies/efo.owl"
owl_prefix = "http://www.semanticweb.org/morteza/ontologies/2019/11/executive-functions-ontology#"

efo = get_ontology(owl_path).load()

# extract class names of the tasks and concepts
#tasks = [t.name for t in efo.search(subclass_of = efo.Task)]
#concepts = [c.name for c in efo.search(subclass_of = efo.ExecutiveFunction)]

# the following code but queries the RDFS labels defined for tasks and concepts
# to query all descendants use "rdfs:subClassOf*" instead.

def query_labels(graph, parent_class):
    class_name = parent_class[1:] if parent_class.startswith(":") else parent_class
    query = f"""
    prefix : <{owl_prefix}>

    SELECT ?label
    WHERE {{
    ?task rdfs:subClassOf* :{class_name};
            rdfs:label ?label
    }}
    """

    # select the all rdfs:labels, flatten the list of labels, and convert them to python string
    labels = [labels for labels in graph.query(query)]
    flatten_labels = [l.toPython() for ll in labels for l in ll]
    return flatten_labels

# preapre RDFLib graph for SPARQL queries
graph = default_world.as_rdflib_graph()

tasks = query_labels(graph, "Task")
concepts = query_labels(graph, "ExecutiveFunction")

print(f"Tasks: {len(tasks)}, Concepts: {len(concepts)}")

time_estimate = len(tasks) * len(concepts)

print(f"it takes ~ {time_estimate}s to query PubMed Central for these tasks and concepts.")

# #%% v2: creates a CSV filled with number of hits but csv file has a column for every hit-query

from metapub import PubMedFetcher
fetcher = PubMedFetcher()

def build_concept_queries(concept):
    return {
        'concept_hits':                     f'("{concept}"[TIAB])',
        'concept_ef_hits':                  f'("{concept}"[TIAB]) AND ("executive function")',
    }

def build_task_queries(task):
    return {
        'task_hits':                        f'("{task}"[TIAB])',
        'task_suffixtask_hits':             f'("{task} task"[TIAB])',
        'task_suffixtest_hits':             f'("{task} test"[TIAB])',
        'task_suffixgame_hits':             f'("{task} game"[TIAB])',
        'task_ef_hits':                     f'("{task}"[TIAB]) AND ("executive function")',
        'task_suffixtask_ef_hits':          f'("{task} task"[TIAB]) AND ("executive function")',
        'task_suffixgame_ef_hits':          f'("{task} game"[TIAB]) AND ("executive function")',
        'task_suffixtest_ef_hits':          f'("{task} test"[TIAB]) AND ("executive function")'
    }

def build_queries(task, concept):
    return {
        'task_concept_ef_hits':             f'("{task}"[TIAB]) AND ("{concept}"[TIAB]) AND ("executive function")',
        'task_suffixtask_concept_ef_hits':  f'("{task} task"[TIAB]) AND ("{concept}"[TIAB]) AND ("executive function")',
        'task_suffixtest_concept_ef_hits':  f'("{task} test"[TIAB]) AND ("{concept}"[TIAB]) AND ("executive function")',
        'task_suffixgame_concept_ef_hits':  f'("{task} game"[TIAB]) AND ("{concept}"[TIAB]) AND ("executive function")',
        'task_concept_hits':                f'("{task}"[TIAB]) AND ("{concept}"[TIAB])',
        'task_suffixtask_concept_hits':     f'("{task} task"[TIAB]) AND ("{concept}"[TIAB])',
        'task_suffixtest_concept_hits':     f'("{task} test"[TIAB]) AND ("{concept}"[TIAB])',
        'task_suffixgame_concept_hits':     f'("{task} game"[TIAB]) AND ("{concept}"[TIAB])'
    }


def query_pubmed(tasks, concepts, csv_file):

    headers = ['task','concept','timestamp_ms']
    headers += build_queries('','').keys()
    header = ','.join(headers)

    try:
        data = pd.read_csv(csv_file)
    except:
        data = pd.DataFrame({'task':[],'concept':[]})
        # create file and headers if does not exist
        if not os.path.exists(csv_file):
            with open(csv_file, 'w'): pass
        with open(csv_file, "r+") as csv:
            if len(csv.read()) == 0:
                print("Empty csv found, generating csv headers...")
                csv.write(header + '\n')

    print('quering...')

    # write queries into the file
    with open(csv_file, "a+",buffering=1) as csv:

        pairs = [(task, concept) for task in tasks for concept in concepts]
        
        # for the sake of making the task of looking at logs less suffering!
        random.shuffle(pairs)

        for task, concept in pairs:
            previously_stored = data[(data.task == task) & (data.concept == concept)]
            if previously_stored.empty:
                millis = int(round(time.time() * 1000))
                csv_cells = [task, concept, str(millis)]
                for qkey, query in build_queries(task, concept).items():
                    print(query)
                    hits = fetcher.pmids_for_query(query=f'{query}', retmax=1000000, pmc_only=False)
                    n_hits = len(hits)
                    csv_cells += [str(n_hits)]

                csv_line = ','.join(csv_cells) + '\n'

                print(csv_line)
                csv.write(csv_line)
            else:
                print(f'skipping <{task},{concept}>...')

def query_pubmed_for_tasks(tasks, csv_file):
    """Peforms PubMed query for a list of EF tasks and stores results in a csv file.
    Each row contains number of results for a single task regardless of related EF concepts."""
    
    headers = ['task','timestamp_ms']
    headers += build_task_queries('').keys()
    header = ','.join(headers)

    try:
        data = pd.read_csv(csv_file)
    except:
        data = pd.DataFrame({'task':[]})
        # create file and headers if does not exist
        if not os.path.exists(csv_file):
            with open(csv_file, 'w'): pass
        with open(csv_file, "r+") as csv:
            if len(csv.read()) == 0:
                print("Empty csv found, generating csv headers...")
                csv.write(header + '\n')

    # task queries
    with open(csv_file, "a+", buffering=1) as csv:
        for task in tasks:
            previously_stored = data[data.task == task]
            if previously_stored.empty:
                millis = int(round(time.time() * 1000))
                csv_cells = [task, str(millis)]
                for qkey, query in build_task_queries(task).items():
                    hits = fetcher.pmids_for_query(query=f'{query}', retmax=1000000, pmc_only=False)
                    n_hits = len(hits)
                    csv_cells += [str(n_hits)]

                #FIXME remove this, this is only for backward-compability with the previous code
                csv_cells += [''] * 10
                csv_line = ','.join(csv_cells) + '\n'

                print(csv_line)
                csv.write(csv_line)


def query_pubmed_for_concepts(concepts, csv_file):
    """Peforms PubMed query for a list of EF concepts and stores results in a csv file.
    Each row contains number of results for a single concept."""
    
    headers = ['concept','timestamp_ms']
    headers += build_concept_queries('').keys()
    header = ','.join(headers)

    try:
        data = pd.read_csv(csv_file)
    except:
        data = pd.DataFrame({'concept':[]})
        # create file and headers if does not exist
        if not os.path.exists(csv_file):
            with open(csv_file, 'w'): pass
        with open(csv_file, "r+") as csv:
            if len(csv.read()) == 0:
                print("Empty csv found, generating csv headers...")
                csv.write(header + '\n')

    # concept queries
    with open(csv_file, "a+", buffering=1) as csv:
        for concept in concepts:
            previously_stored = data[data.concept == concept]
            if previously_stored.empty:
                millis = int(round(time.time() * 1000))
                csv_cells = [concept, str(millis)]
                for qkey, query in build_concept_queries(concept).items():
                    hits = fetcher.pmids_for_query(query=f'{query}', retmax=1000000, pmc_only=False)
                    n_hits = len(hits)
                    csv_cells += [str(n_hits)]

                csv_line = ','.join(csv_cells) + '\n'

                print(csv_line)
                csv.write(csv_line)

#query_pubmed_for_tasks(tasks, "/Users/morteza/workspace/notebooks/efo/data/efo_pubmed_tasks_hits.v2.csv")  

#query_pubmed_for_concepts(concepts, "/Users/morteza/workspace/notebooks/efo/data/efo_pubmed_concepts_hits.v2.csv")  
query_pubmed(tasks, concepts, "/Users/morteza/workspace/notebooks/efo/data/efo_pubmed_hits.v2.csv")


# %%
