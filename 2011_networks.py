import pandas as pd
import os
import networkx as nx
from networkx.algorithms import bipartite

PROJECT_DIR = os.path.abspath('')
DATA_DIR = f'{PROJECT_DIR}\data'

#Upload the full data as node and edge lists
edges = pd.read_csv(r'data\2011_edges.csv', encoding = 'latin1')
nodes = pd.read_csv(r'data\2011_nodes.csv', encoding = 'latin1')

#Fix script coding issue in first column dataframes
nodes.columns.values[0] = 'Id'
edges.columns.values[0] = 'source'

'''Produce a bipartite network containing all the data'''

#Create bipartite graph from the companies edge list
bi_full_inc_ppg_members = nx.from_pandas_edgelist(edges, 'source', 'target', ['position'])

#Add node attributes to the network via a dictionary
node_attr = nodes.set_index('Id').to_dict('index')
nx.set_node_attributes(bi_full_inc_ppg_members, node_attr)

#Create a smaller graph with the membership edges removed
bi_full = bi_full_inc_ppg_members.copy()
member_edges = [(a,b) for a, b, attrs in bi_full.edges(data=True) if attrs['position'] == 'Member']
bi_full.remove_edges_from(member_edges)
bi_full.remove_nodes_from(list(nx.isolates(bi_full)))

#Function returning list of organisation by organisation category 
def org_cat_list(column, category_name):
    filt = (nodes[column] == category_name)
    filter_df = nodes.loc[filt]
    list_of_orgs = filter_df['Id'].tolist()
    
    return list_of_orgs

#List of Policy Planning Groups in the data
PPGs = org_cat_list('org_cat', 'Policy-Planning Group')

#Create list from PPG member edges
PPG_members = set()
for tuple in member_edges:
    for x in tuple:
        PPG_members.add(x)

#Remove PPGs from set
PPG_members.difference_update(PPGs)

#Convert set to list & sort alphabetically
PPG_members = list(PPG_members)
PPG_members.sort()

'''Create list of directors of the six continuity PPGs'''

#Populate a set with the neighbours of every PPG
PPG_directors = set()

for node in (PPGs):
    neighbours = [n for n in bi_full.neighbors(node)]
    for node in (neighbours):
        PPG_directors.add(node)

#Convert set to list & sort alphabetically
PPG_directors = list(PPG_directors)
PPG_directors.sort()

'''Create a list of bank directors'''

#Create list of banks in the top 250 companies
banks = org_cat_list('corp_sub', 'bank')

#Populate a list with neighbour, i.e. director, of every bank
bankers = set()

for node in (banks):
    neighbours = [n for n in bi_full.neighbors(node)]
    for node in (neighbours):
        bankers.add(node)

#Convert set to list & sort alphabetically
bankers = list(bankers)
bankers.sort()

'''Create dataframe of all individuals & add above variables'''
all_persons = edges['source']
all_persons.drop_duplicates(inplace=True)
all_persons = all_persons.to_frame()
all_persons.rename(columns = {'source':'Id'}, inplace=True)
all_persons['banker'] = all_persons.isin(bankers)
all_persons['PPG_director'] = all_persons['Id'].isin(PPG_directors)
all_persons['PPG_member'] = all_persons['Id'].isin(PPG_members)
all_persons.set_index('Id', inplace=True)

#Add person data to both bipartite networks
all_persons = all_persons.to_dict('Index')
nx.set_node_attributes(bi_full_inc_ppg_members, all_persons)
nx.set_node_attributes(bi_full, all_persons)

'''Create bipartite graph without the PPGs'''
bi_250_corps = bi_full.copy()
bi_250_corps.remove_nodes_from(PPGs)
bi_250_corps.remove_nodes_from(list(nx.isolates(bi_250_corps)))

'''Add degree counts to the bipartite networks'''
bipartite_degree = dict(bi_full.degree)
nx.set_node_attributes(bi_full, bipartite_degree, 'bipartite_degree')

bipartite_degree = dict(bi_250_corps.degree)
nx.set_node_attributes(bi_250_corps, bipartite_degree, 'bipartite_degree')
nx.set_node_attributes(bi_full, bipartite_degree, 'corp_bipartite_degree')

'''Produce weighed projected networks from the bipartite corporations only 
network and export as pickle and gephi files.'''

orgs = [v for v in bi_250_corps.nodes if bi_250_corps.nodes[v]['node_type'] == 'org']
corporate_network_2011 = bipartite.overlap_weighted_projected_graph(bi_250_corps, orgs)

directors = [v for v in bi_250_corps.nodes if bi_250_corps.nodes[v]["node_type"] == 'person']
corp_dir_network_2011 = bipartite.overlap_weighted_projected_graph(bi_250_corps, directors)
non_interlockers = [x for x in bi_250_corps.nodes() if bi_250_corps.degree(x) == 1]
for node in non_interlockers:
    if node in orgs:
        non_interlockers.remove(node)
corp_dir_network_2011.remove_nodes_from(non_interlockers)

#Export the networks
nx.write_gpickle(bi_250_corps, 'pickled_networks/bi_250_corps_2011.gpickle')
nx.write_gpickle(corporate_network_2011, 'pickled_networks/corporate_network_2011.gpickle')
nx.write_gpickle(corp_dir_network_2011, 'pickled_networks/corp_dir_network_2011.gpickle')

#Export the networks as Gephi Files
nx.write_gexf(bi_250_corps, 'gephi_files/bi_250_corps_2011.gexf')
nx.write_gexf(corporate_network_2011, 'gephi_files/corporate_network_2011.gexf')
nx.write_gexf(corp_dir_network_2011, 'gephi_files/corp_dir_network_2011.gexf')

'''Produce weighed projected networks from the bipartite PPG network and 
export as pickle and gephi files.'''

orgs = [v for v in bi_full.nodes if bi_full.nodes[v]["node_type"] == 'org']
ppgs_network_2011 = bipartite.overlap_weighted_projected_graph(bi_full, orgs)

directors = [v for v in bi_full.nodes if bi_full.nodes[v]["node_type"] == 'person']
ppgs_dir_network_2011 = bipartite.overlap_weighted_projected_graph(bi_full, directors)
non_interlockers = [x for x in bi_full.nodes() if bi_full.degree(x) == 1]
for node in non_interlockers:
    if node in orgs:
        non_interlockers.remove(node)
ppgs_dir_network_2011.remove_nodes_from(non_interlockers)

#Export the networks
nx.write_gpickle(bi_full, 'pickled_networks/bi_ppgs_2011.gpickle')
nx.write_gpickle(ppgs_network_2011, 'pickled_networks/ppgs_network_2011.gpickle')
nx.write_gpickle(ppgs_dir_network_2011, 'pickled_networks/ppgs_dir_network_2011.gpickle')

#Export the networks as Gephi Files
nx.write_gexf(bi_full, 'gephi_files/bi_ppgs_2011.gexf')
nx.write_gexf(ppgs_network_2011, 'gephi_files/ppgs_network_2011.gexf')
nx.write_gexf(ppgs_dir_network_2011, 'gephi_files/ppgs_dir_network_2011.gexf')