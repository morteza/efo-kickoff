#%% [markdown]

# The following cell prepares the environment, install the dependencies, and loads the tidy dataset as `df`

#%%
#!pip install pymc3 pandas matplotlib numpy seaborn arviz

import matplotlib.pyplot as plt

import pandas as pd
import numpy as np

import pandas as pd
import pymc3 as pm
import numpy as np

from IPython.display import display
import seaborn as sns

from scipy.stats import zscore

sns.set_style('ticks')
az.style.use("arviz-darkgrid")

#csv_path = '/content/drive/My Drive/Colab Notebooks/data/efo_pubmed_hits.20200114_preproc.csv'
csv_path = '/Users/morteza/workspace/efo_kickoff/datasets/efo_pubmed_hits.20200114_tidy.csv'

df = pd.read_csv(csv_path)

no_hits = df[(df.construct_hits==0) | (df.task_hits==0) | (df.hits==0)]
tasks_with_no_hits = no_hits[no_hits.task_hits==0].task.unique()
constructs_with_no_hits = no_hits[no_hits.construct_hits==0].construct.unique()

print(f"The following {len(constructs_with_no_hits)} constructs have zero hits: {', '.join(constructs_with_no_hits)}")
print(f"The following {len(tasks_with_no_hits)} tasks have zero hits: {', '.join(tasks_with_no_hits)}")


# change task and concepts to categories
df['context'] = df['context'].astype('category')
df['construct'] = df['construct'].astype('category')
df['task'] = df['task'].astype('category')

#DEBUG make it one observation per task! it this necessary?
#df = df.sort_values('task', ascending=False).drop_duplicates(['task'])

df = df[~((df.task_hits ==0) | (df.construct_hits==0))]

context_idx = df.context.cat.codes.values
n_context = df.context.cat.categories.size

construct_idx = df.construct.cat.codes.values
n_constructs = df.construct.cat.categories.size

task_idx = df.task.cat.codes.values
n_tasks = df.task.cat.categories.size

n_obs = len(df)

df['hits_zscore'] = zscore(df.hits)
df['task_hits_zscore'] = zscore(df.task_hits)
df['task_construct_zscore'] = zscore(df.construct_hits)

#%%
# Model1 tries to predict/explain the task/construct hits using only an informative normal distribution


with pm.Model() as model1:
  # prior on mean value
  mu = pm.Normal('mu', sigma=100)

  # likelihood
  hits = pm.Normal('hits', mu=mu, sigma=1, observed=df.hits_zscore)

  display(pm.model_to_graphviz(model1))
  display(model1.check_test_point())

  model1_trace = pm.sample(1000, model=model1)

# plot traceplot
az.plot_trace(model1_trace)

#%% model 2: Model task-construct hits with priors on the context, then compare EF to nonEF.
# -----------------------------------------------

sd_contexts = df.groupby('context').std().hits_zscore
hits_grand_mean = df.hits_zscore.mean() #FIXME isn't it zero?!

with pm.Model() as model2:

  # prior on `nu`, a parameter of final StudentT likelihood
  nu_minus_one = pm.Exponential('nu_minus_one',lam=1/29.0) # min(nu) must be 1
  nu = pm.Deterministic('nu', nu_minus_one + 1)

  # context parameters
  context_mu = pm.Normal('context_mu', mu=hits_grand_mean, sigma=sd_contexts*100, shape=n_context)
  context_sigma = pm.Uniform('context_sigma', sd_contexts/1000, sd_contexts*1000, shape=n_context)
  
  # difference between the avergae hits in EF and nonEF
  ef_noef_diff = pm.Deterministic('EF - nonEF', context_mu[0] - context_mu[1])

  # likelihood
  hits = pm.StudentT('hits', nu=nu, mu=context_mu[context_idx], sigma=context_sigma[context_idx], observed=df.hits_zscore)

  display(pm.model_to_graphviz(model2))
  display(model2.check_test_point())
  model2_trace = pm.sample(model=model2)

  # plots
  pm.traceplot(model2_trace, var_names=['context_mu','context_sigma','mi'])
  pm.plot_posterior(model2_trace,
    var_names=['context_mu','context_sigma','EF - nonEF','nu'],
    point_estimate='mode',
    credible_interval=0.95,
    ref_val=0)

#%% Model 3: predict `task-construct` hits, only in EF context, and then compare `construct` model parameters 
# -----------------------------------------------
ef_df = df[df.context=='EF']
ef_construct_mean = ef_df.groupby('construct').mean().construct_hits

ef_construct_idx = ef_df.construct.cat.codes.values
n_ef_constructs = ef_df.construct.cat.categories.size

ef_task_idx = ef_df.task.cat.codes.values
n_ef_tasks = ef_df.task.cat.categories.size

with pm.Model() as model3:

  construct_mu = pm.Normal('construct_mu', mu=ef_construct_mean, sigma=100, shape=n_ef_constructs)
  constructs_sigma = pm.Uniform('construct_sigma', 1/100, 100, shape=n_ef_constructs)

  nu_minus_one = pm.Exponential('nu_minus_one',lam=1/29.0) # min(nu) must be 1
  nu = pm.Deterministic('nu', nu_minus_one+1)

  hits = pm.StudentT('hits', nu=nu, mu=construct_mu[ef_construct_idx], sigma=constructs_sigma[ef_construct_idx], observed=ef_df.hits)

  display(pm.model_to_graphviz(model3))
  display(model3.check_test_point())
  
  model3_trace = pm.sample(model=model3)

  display(pm.model_to_graphviz(model3))

  display(pm.summary(model3_trace))
  pm.forestplot(model3_trace, combined=True, var_names=['construct_mu'], credible_interval=0.95)
  
  pm.traceplot(model3_trace)
  pm.plot_posterior(model3_trace,
    point_estimate='mode',
    credible_interval=0.95,
    ref_val=0)
az.plot_pair(model3_trace,
            var_names=['construct_mu'],
            divergences=True,
            textsize=18)

#%% Model4


#%% Model Comparision: compare models using WAIC criterion
models = {'model1':model1, 'model2': model2, 'model3': model3}
mc_waic = pm.compare(models, ic='WAIC')
pm.compareplot(mc_waic)
