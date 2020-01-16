#%% [markdown]
# EFO kickoff project collects several data from PubMed in a wide format. Codes provided below converts the wide format into a tidy format with the following expected structure in each row:
# <context>,<task>,<construct>,<hits>,<task_hits>,<construct_hits>

# the context column is either EF or notEF, which shows that the context in which the query was performed was either executive functions or anything expect executive function. Please refer to my daily log of 20200116 or efo/kickoff codebook for more details on columns.

# The following code expects a csv file (preprocessed csv file), and generated a new csv with _tidy suffix instead of _preproc in the same directory.
#%%

# params
csv_path = "/Users/morteza/workspace/efo_kickoff/datasets/efo_pubmed_hits.20200114_preproc.csv"
output_csv_path = csv_path.replace('_preproc.csv', '_tidy.csv')

import pandas as pd

def tidy_efo_preproc_csv(csv, output_csv):
  df = pd.read_csv(csv)

  tidy_df = pd.DataFrame({
    "context": 'notEF',
    "task": df['task'],
    "construct": df['concept'],
    "hits": df['task_concept_hits'] - df['task_concept_ef_hits'],
    "task_hits": df['task_hits'] - df['task_ef_hits'],
    "construct_hits": df['concept_hits'] - df['concept_ef_hits']
  })

  ef_df = pd.DataFrame({
    "context": 'EF',
    "task": df['task'],
    "construct": df['concept'],
    "hits": df['task_concept_ef_hits'],
    "task_hits": df['task_ef_hits'],
    "construct_hits": df['concept_ef_hits']
  })

  tidy_df = tidy_df.append(ef_df, ignore_index=True)
  
  tidy_df.to_csv(output_csv)
  print(f"Tidy dataset written successfully to {output_csv}")

# make things tidy!
tidy_efo_preproc_csv(csv_path, output_csv_path)