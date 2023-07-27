import pandas as pd
import os
import networkx as nx
from networkx.algorithms import bipartite

PROJECT_DIR = os.path.abspath('')
DATA_DIR = f'{PROJECT_DIR}\data'

#Upload the full data as node and edge lists
edges = pd.read_csv(r'data\1936_edges.csv')
nodes = pd.read_csv(r'data\1936_nodes.csv')

'''Produce a bipartite network containing all the data'''

#Create bipartite graph from the companies edge list
bi_full_inc_ppg_members = nx.from_pandas_edgelist(edges, 'source', 'target', ['position'])

#Add node attributes to the network via a dictionary
node_attr = nodes.set_index('Id').to_dict('index')
nx.set_node_attributes(bi_full_inc_ppg_members, node_attr)

#Create smaller graph with membership edges (and now isolated nodes) removed
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

#Create set from PPG member edges
PPG_members = set()
for tuple in member_edges:
    for x in tuple:
        PPG_members.add(x)

#Remove the PPGs from the set
PPG_members.difference_update(PPGs)

#Convert set to list & sort alphabetically
PPG_members = list(PPG_members)
PPG_members.sort()

#Produce lists of foundations and investment banks
foundations = org_cat_list('org_cat', 'Foundation')
IBs = org_cat_list('corp_sub', 'investment bank')

'''Produce a boolean variable to identify bankers'''

#Create list of banks in the data
banks = org_cat_list('corp_sub', 'bank')

#Populate a set with the neighbours of every bank
bankers = set()

for node in (banks):
    neighbours = [n for n in bi_full.neighbors(node)]
    for node in (neighbours):
        bankers.add(node)

#Convert set to list & sort alphabetically
bankers = list(bankers)
bankers.sort()

'''Do the same for the six PPGs'''

PPG_directors = set()

for node in (PPGs):
    neighbours = [n for n in bi_full.neighbors(node)]
    for node in (neighbours):
        PPG_directors.add(node)

#Convert set to list & sort alphabetically
PPG_directors = list(PPG_directors)
PPG_directors.sort()

#Create dataframe of all individuals & add the above variables
all_persons = edges['source']
all_persons.drop_duplicates(inplace=True)
all_persons = all_persons.to_frame()
all_persons.rename(columns = {'source':'Id'}, inplace=True)
all_persons['banker'] = all_persons.isin(bankers)
all_persons['PPG_director'] = all_persons['Id'].isin(PPG_directors)
all_persons['PPG_member'] = all_persons['Id'].isin(PPG_members)
all_persons.set_index('Id', inplace=True)

#Add the person data to networks via a dictionary
all_persons = all_persons.to_dict('Index')
nx.set_node_attributes(bi_full, all_persons)
nx.set_node_attributes(bi_full_inc_ppg_members, all_persons)

'''Create smaller bipartite graph without investment banks or foundations and 
with now isolated directors removed'''

bi_ppgs = bi_full.copy()
bi_ppgs.remove_nodes_from(IBs)
bi_ppgs.remove_nodes_from(foundations)
bi_ppgs.remove_nodes_from(list(nx.isolates(bi_ppgs)))

#Create still smaller bipartite graph with just the corporations
bi_corps = bi_ppgs.copy()
bi_corps.remove_nodes_from(PPGs)
bi_corps.remove_nodes_from(list(nx.isolates(bi_corps)))

'''Add degree counts to those two subnetworks (from both)'''

bipartite_degree = dict(bi_ppgs.degree)
nx.set_node_attributes(bi_ppgs, bipartite_degree, 'bipartite_degree')
nx.set_node_attributes(bi_ppgs, bipartite_degree, 'ppg_bipartite_degree')

bipartite_degree = dict(bi_corps.degree)
nx.set_node_attributes(bi_corps, bipartite_degree, 'bipartite_degree')
nx.set_node_attributes(bi_ppgs, bipartite_degree, 'corp_bipartite_degree')

'''Produce weighed projected graphs from the bipartite corporate network. For 
the individuals network including only the interlockers. Exporting the networks 
as pickle and Gephi files.'''

orgs = [v for v in bi_corps.nodes if bi_corps.nodes[v]['node_type'] == 'org']
corporate_network_1936 = bipartite.overlap_weighted_projected_graph(bi_corps, orgs)

corp_directors = [v for v in bi_corps.nodes if bi_corps.nodes[v]['node_type'] == 'person']
corps_dir_network_1936 = bipartite.overlap_weighted_projected_graph(bi_corps, corp_directors)
non_interlockers = [x for x in bi_corps.nodes() if bi_corps.degree(x) == 1]
for node in non_interlockers:
    if node in orgs:
        non_interlockers.remove(node)
corps_dir_network_1936.remove_nodes_from(non_interlockers)

#Export the three networks
nx.write_gpickle(bi_corps, 'pickled_networks/bi_corps_1936.gpickle')
nx.write_gpickle(corporate_network_1936, 'pickled_networks/corporate_network_1936.gpickle')
nx.write_gpickle(corps_dir_network_1936, 'pickled_networks/corps_dir_network_1936.gpickle')

nx.write_gexf(bi_corps, 'gephi_files/bi_corps_1936.gexf')
nx.write_gexf(corporate_network_1936, 'gephi_files/corporate_network_1936.gexf')
nx.write_gexf(corps_dir_network_1936, 'gephi_files/corps_dir_network_1936.gexf')

'''Produce weighed projected graphs from the bipartite PPGs network; for the 
individuals network including only the interlockers.'''

orgs = [v for v in bi_ppgs.nodes if bi_ppgs.nodes[v]['node_type'] == 'org']
ppgs_network_1936 = bipartite.overlap_weighted_projected_graph(bi_ppgs, orgs)

directors = [v for v in bi_ppgs.nodes if bi_ppgs.nodes[v]['node_type'] == 'person']
ppgs_dir_network_1936 = bipartite.overlap_weighted_projected_graph(bi_ppgs, directors)
non_interlockers = [x for x in bi_ppgs.nodes() if bi_ppgs.degree(x) == 1]
for node in non_interlockers:
    if node in orgs:
        non_interlockers.remove(node)
ppgs_dir_network_1936.remove_nodes_from(non_interlockers)

#Export the networks
nx.write_gpickle(bi_ppgs, 'pickled_networks/bi_ppgs_1936.gpickle')
nx.write_gpickle(ppgs_network_1936, 'pickled_networks/ppgs_network_1936.gpickle')
nx.write_gpickle(ppgs_dir_network_1936, 'pickled_networks/ppgs_dir_network_1936.gpickle')

nx.write_gexf(bi_ppgs, 'gephi_files/bi_ppgs_1936.gexf')
nx.write_gexf(ppgs_network_1936, 'gephi_files/ppgs_network_1936.gexf')
nx.write_gexf(ppgs_dir_network_1936, 'gephi_files/ppgs_dir_network_1936.gexf')