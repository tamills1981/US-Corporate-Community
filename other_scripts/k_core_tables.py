# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 13:04:21 2022

@author: millst
"""

import pandas as pd
import os

#Redefine path directory
path = 'C://Users//millst/Box/Research/Elites/Domhoff stuff/Paper/Results'
os.chdir(path)

#Upload data
data = pd.read_csv(r"ppgs_network_2011_node_measures_28-12-2022.csv")

data_k_cores = data[['node', 'core_no']]
data_k_cores = data_k_cores.groupby(by='core_no').agg(lambda x: set(x))
data_k_cores.reset_index(inplace=True)
data_k_cores['orgs_in_group'] = data_k_cores.node.sort_values().apply(lambda x: sorted(x))
data_k_cores['no_orgs_in_group'] = data_k_cores.node.str.len()
data_k_cores = data_k_cores.sort_values(by=['core_no'], ascending=False)
data_k_cores['cum_sum'] = data_k_cores.no_orgs_in_group.cumsum()
data_k_cores = data_k_cores[['core_no', 'no_orgs_in_group', 'cum_sum', 'orgs_in_group']]

k_cores_means = data.groupby(by='core_no').mean()
