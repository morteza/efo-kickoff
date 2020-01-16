#%% [markdown]
# The following script merges tasks and concepts hits into the efo_pubmed_hits dataset, and then stores
# the result in a csv file. 
#%%

import pandas as pd


# input csv files
data_dir = "/Users/morteza/workspace/notebooks/efo/data/"
data_version = "20200114"
csv_path = f"{data_dir}efo_pubmed_hits.{data_version}.csv"
tasks_csv_path = f"{data_dir}efo_pubmed_tasks_hits.{data_version}.csv"
concepts_csv_path = f"{data_dir}efo_pubmed_concepts_hits.{data_version}.csv"

# output csv file
output_csv_path = f"{data_dir}efo_pubmed_hits.{data_version}_preproc.csv"

def merge_csv_files(tasks_concepts_hits_csv, concepts_hits_csv, tasks_hits_csv):
  """merge tasks, concepts, and tasks-concepts hits data files"""
  # read inputs
  df = pd.read_csv(tasks_concepts_hits_csv)
  df_tasks = pd.read_csv(tasks_hits_csv)
  df_concepts = pd.read_csv(concepts_hits_csv)

  # merge datasets and backup original data columns if any.
  df = df.merge(df_tasks,on='task',suffixes=('_original', '')).merge(df_concepts, on='concept',suffixes=('_original', ''))

  # drop backup columns
  to_drop_cols = df.filter(like = '_original').columns
  df.drop(to_drop_cols, axis='columns', inplace=True)

  return df

def combine_hits(csv_path):
  """WARNING: it's a destructive process, and not tested yet! PC is freezed!"""
  df = pd.read_csv(csv_path)
  df['task_suffixed_hits'] = df['task_suffixtask_hits'] + df['task_suffixtest_hits'] + df['task_suffixgame_hits']
  df['task_suffixed_ef_hits'] = df['task_suffixtask_hits'] + df['task_suffixtest_hits'] + df['task_suffixgame_hits']
  df['task_suffixed_concept_ef_hits'] = (
    df['task_suffixtask_concept_ef_hits'] +
    df['task_suffixtest_concept_ef_hits'] + 
    df['task_suffixgame_concept_ef_hits']
  )
  df['task_suffixed_concept_hits'] = (
    df['task_suffixtask_concept_hits'] +
    df['task_suffixtest_concept_hits'] + 
    df['task_suffixgame_concept_hits']
  )

  to_drop_cols = df.filter(like = ['suffixtest','suffixtask','suffixgame']).columns
  #df.drop(to_drop_cols, axis='columns', inplace=True)

  return df


merge_csv_files(csv_path, concepts_csv_path, tasks_csv_path).to_csv(output_csv_path)
#WARNING combine_hits(output_csv_path).to_csv(output_csv_path)