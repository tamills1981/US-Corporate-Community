# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 06:51:32 2022

@author: millst
"""

import pandas as pd
import os
import networkx as nx
from networkx.algorithms import bipartite

#Define path directory
path = 'C://Users//millst/Box/Research/Elites/Domhoff stuff/Paper/Networks'
os.chdir(path)

#Define file name
filename = 'bi_ppgs_2011.gpickle'

#Upload network
B = nx.read_gpickle(filename)

#File name with extension removed
name = filename.split(".")
name = name[0]

#Filter for giant component
def connected_component_subgraphs(B):
    for c in nx.connected_components(B):
        yield B.subgraph(c) 
B = max(connected_component_subgraphs(B), key=len)

directors = [v for v in B.nodes if B.nodes[v]["node_type"] == 'person']
G = bipartite.overlap_weighted_projected_graph(B, directors)

figures = dict(G.nodes)
figures = pd.DataFrame.from_dict(figures, orient='index')
figures.index.name = 'node'

director_counts = figures.bipartite_degree.value_counts(ascending=False)
director_percent = figures.bipartite_degree.value_counts(ascending=False, normalize=True) *100
director_figures = pd.merge(director_counts, director_percent, right_index=True, left_index=True)
director_figures.reset_index(inplace=True)
director_figures.rename(columns={"index": 'Bipartite degree', 'bipartite_degree_x': 'Count', 'bipartite_degree_y': "Percent"}, inplace=True)
director_figures.sort_values(by=['Count'], ascending=True, inplace=True)
director_figures.reset_index(inplace=True, drop=True)

path = 'C://Users//millst/Box/Research/Elites/Domhoff stuff/Paper/Data'
os.chdir(path)

#Export as CSV file
csv_name =  name + '_(giant com)_director_figures.csv'
director_figures.to_csv(csv_name, header = True, index = False)