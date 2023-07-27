# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 11:40:42 2022

@author: millst
"""
import pandas as pd
import os

#Define path directory
path = 'C://Users//millst/Box/Research/Elites/Domhoff stuff/Paper/Results'
os.chdir(path)

#Upload data
data = pd.read_csv(r"ppgs_network_1936_node_measures_31-08-2022.csv")

centralities = data[['bipartite_degree', 'degree', 'degree_w', 'closeness', 'closeness_w',
       'betweenness', 'betweenness_w', 'EVC', 'EVC_w', 'core_no', 'onion_layer']]

correlation_matrix = centralities.corr(method='spearman', min_periods=1)

#correlation_matrix.to_csv('ppgs_BR_network_2011_correlation_matrix.csv', header = True, index = True)
