# EFO Datasets

This document describes different datasets of the EFO  project. All datasets, version with date, are available in the same directory as this manual.

## PubMed Concept Hits

Stored as `efo_pubmed_concepts_hits.<date>.csv`, PubMed Concepts Hits dataset includes the number of search hits for each constructs (i.e., cognitive concepts). The terms are extracted from the EFO ontology with `rdfs:label` annotations of `efo:Construct` as the search terms.

The following table describes the columns of this dataset.

| Column  | Description |
|---      |---|
| concept | search term represented the construct name |
| timestamp_ms    | querying time in millis |
| concept_hits    | number of search hits across all contexts whether EF or not |
| concept_ef_hits | number of search hits only in EF context ( query was constrained with an additional "Executive Function" term) |

## PubMed Tasks Hits

Number of PubMed search hits for tasks are stored in `efo_pubmed_tasks_hits.<date>.csv`. It includes number of hits for a given task in EF context, and also number of hits in general. Task terms are extracted from the EFO ontology, limited to the `rdfs:label` annotiations that belong to a subclass of `efo:Task` class.

The following table describes the columns of the tasks dataset:

| Column  | Description |
|---      |---|
| task            | term used to represent the task in search queries |
| timestamp_ms    | querying time in millis |
| task_hits       | number of search hits across all contexts whether EF or not |
| task_ef_hits    | number of search hits only in EF context (the query was constrained with an additional "Executive Function" term) |

## PubMed Hits

### PubMed Hits - Preprocessed

### PubMed Hits - Tidy