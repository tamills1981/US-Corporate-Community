# -*- coding: utf-8 -*-
"""
Created on Tue May 31 11:07:11 2022

@author: millst
"""

import pandas as pd
import os
import networkx as nx
from datetime import datetime
from pyvis.network import Network

#Define path directory
path = 'C://Users//millst/Box/Research/Elites/Domhoff stuff/Paper/Networks'
os.chdir(path)

filename = 'bi_ppgs_2011.gpickle'

#Upload network
G_full = nx.read_gpickle(filename)

#File name with extension removed
name = filename.split(".")
name = name[0]

#Function filtering for giant component
def connected_component_subgraphs(G_full):
    for c in nx.connected_components(G_full):
        yield G_full.subgraph(c)

G = max(connected_component_subgraphs(G_full), key=len)

#Redefine path directory
path = 'C://Users//millst/Box/Research/Elites/Domhoff stuff/Paper/Results'
os.chdir(path)

node_data = pd.read_csv(r"ppgs_dir_network_2011_node_measures_02-07-2022.csv")

#Filter for nodes of interest
filt = node_data['core_no'] >= 12
#filt = (node_data['PPG_director'] == True) | (node_data['PPG_member'] == True)

#Create list based on filter
ego_nodes = node_data.loc[filt]
ego_nodes = ego_nodes['node'].tolist()

#Produce subnetwork from list
#Populate a list with the ego network of every PPG
subnet_nodes = set()

for node in (ego_nodes):
    neighbours = [n for n in G_full.neighbors(node)]
    for node in (neighbours):
        subnet_nodes.add(node)

for node in (ego_nodes):
    subnet_nodes.add(node)

subnet = G_full.subgraph(subnet_nodes).copy()

#Create dataframe of all nodes and their properties
nodes_df = pd.DataFrame.from_dict(dict(G_full.nodes(data=True)), orient='index')
subnet_nodes_df = nodes_df.loc[subnet]
type_filt = (subnet_nodes_df['node_type'] == 'org')
subnet_orgs_df = subnet_nodes_df.loc[type_filt]
subnet_persons_df = subnet_nodes_df.loc[~type_filt]

#Redefine path directory
path = 'C://Users//millst/Desktop'
os.chdir(path)

#Export as Gephi file
nx.write_gexf(subnet, "2011_k_core.gexf")


