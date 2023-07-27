import pandas as pd
import networkx as nx
import os
from os import listdir
from tqdm import tqdm

PROJECT_DIR = os.path.abspath('')
DATA_DIR = f'{PROJECT_DIR}/pickled_networks/'
OUTPUTS =  f'{PROJECT_DIR}/network_analysis_data_tables/'

#Produce list of files in folder
all_files = listdir(DATA_DIR)

#List of files to exclude from analysis
files_to_exclude =  ['bi_250_corps_2011.gpickle', 'bi_496_2011.gpickle', 
                     'bi_50_200_corps.gpickle', 'bi_50_200_ppgs.gpickle', 
                     'bi_corps_1936.gpickle', 'bi_ppgs_1936.gpickle', 
                     'bi_ppgs_2011.gpickle', 'corp_dir_50_200.gpickle',
                     'bi_ppgs_2011_BC.gpickle', 'bi_250_corps_2011_BC.gpickle']

#Files to analyse
files = [x for x in all_files if x not in files_to_exclude]

#Function filtering for graph components
def connected_component_subgraphs(G_full):
    for c in nx.connected_components(G_full):
        yield G_full.subgraph(c)

#Function returning object name as a string
def name_of_object(arg):
    for name, value in globals().items():
        if value is arg and not name.startswith('_'):
            return name

for filename in tqdm(files):    
    
    #Upload network from folder of pickled networks
    G_full = nx.read_gpickle(DATA_DIR + filename)
        
    #File name with extension removed
    name = filename.split(".")
    name = name[0]
    
    #Check if graph is connected
    is_connected = nx.is_connected(G_full)
    
    #List to populate with nodes outside of the largest component
    lonely_nodes = []
    
    #If graph is not connected then return largest component and append 
    #other nodes to the above list
    if is_connected == True:
        G = G_full.copy()
    else:
        G = max(connected_component_subgraphs(G_full), key=len)
        full_node_list = list(G_full)
        giant_compontent_node_list = list(G)
        for node in (full_node_list):
            if node in giant_compontent_node_list:
                pass
            else:
                lonely_nodes.append(node)
    
    no_nodes_not_in_giant_component = len(lonely_nodes)
    lonely_nodes.sort()
    
    '''This section adds a number of network measures to the graph which are 
    then exported as a CSV file'''
       
    #Create new edge attribute 'distance' as inverse of weights
    for u,v,d in G.edges(data=True):
        d['distance'] = 1 / d['weight']
    
    #Run network measures
    degree = {node:val for (node, val) in G.degree(weight=None)}
    degree_w = {node:val for (node, val) in G.degree(weight='weight')}
    closeness = nx.closeness_centrality(G, u=None, distance=None)
    closeness_w = nx.closeness_centrality(G, u=None, distance='distance')
    betweenness = nx.betweenness_centrality(G, weight=None)
    betweenness_w = nx.betweenness_centrality(G, weight='distance')
    average_neighbour_degree = nx.average_neighbor_degree(G, weight=None)
    average_neighbour_degree_w = nx.average_neighbor_degree(G, weight='weight')
    EVC = nx.eigenvector_centrality(G, weight=None, max_iter=500)
    EVC_w = nx.eigenvector_centrality(G, weight='weight', max_iter=500)
    clustering_co_eff = nx.clustering(G)
    triangles = nx.triangles(G)
    eccentricity = nx.eccentricity(G)
    onion_layer = nx.onion_layers(G)
    core_no = nx.core_number(G)
    
    #Add all results to a list
    node_measures = [degree, degree_w, closeness, closeness_w, betweenness, 
                 betweenness_w, average_neighbour_degree_w, average_neighbour_degree, 
                 EVC, EVC_w, clustering_co_eff, triangles, eccentricity, onion_layer,
                 core_no]
    
    #Loop adding measures to the graph
    for measure in (node_measures):
        measure_name = name_of_object(measure)
        nx.set_node_attributes(G, measure, name=measure_name)
    
    #Create dataframe from the list
    results = dict(G.nodes)
    node_measures = pd.DataFrame.from_dict(results, orient='index')
    node_measures.index.name = 'node'
    
    #Create ranking columns for centrality measures
    
    centrality_measures = ['degree', 'degree_w', 'closeness', 'closeness_w', 
    'betweenness', 'betweenness_w', 'EVC', 'EVC_w']
    
    centrality_ranked = node_measures[centrality_measures].rank(method='min', ascending=False)
    centrality_ranked = centrality_ranked.add_suffix('_ranked')
    
    #Bespoke code to add a connection per bipartite degree as network measure 
    node_measures['bipartite_degree/degree'] = node_measures['degree'] / node_measures['bipartite_degree'] 
    
    '''K-step counts for all nodes in the network plus average degree for nodes
    reached within each step'''
    
    number_of_nodes = G.number_of_nodes() - 1
    
    node_list = list(G)
    
    #Create empty lists for results
    dfs_list = []
    
    for v in (node_list):
        temp_df = pd.DataFrame()
        result = dict()
        
        #Section 1
        
        ego1 = nx.ego_graph(G, v)
        ego1.remove_node(v)
        
        nnodes = ego1.number_of_nodes()
        
        ego1nodes = list(ego1.nodes)
        deg = sum(d for n, d in G.degree(nbunch=ego1nodes)) / float(nnodes)
            
        fraction1 = nnodes / number_of_nodes * 100
        percent1 = round(fraction1, 2)
        
        result['node'] = v
        result['no. 1 step nodes (degree)'] = nnodes
        result['1 step % reached'] = percent1  
        result['1 step nodes average degree'] = deg

        #Section 2
        
        ego2 = nx.ego_graph(G, v, radius=2)
        ego2.remove_node(v)
        
        nnodes = ego2.number_of_nodes()
        
        ego2nodes = list(ego2.nodes)
        deg = sum(d for n, d in G.degree(nbunch=ego2nodes)) / float(nnodes)
        
        fraction2 = nnodes / number_of_nodes * 100
        percent2 = round(fraction2, 2)
        
        result['no. 2 step nodes'] = nnodes
        result['2 step % reached'] = percent2  
        result['2 step nodes average degree'] = deg 
        
        #Section 3
        
        ego3 = nx.ego_graph(G, v, radius=3)
        ego3.remove_node(v)
        
        nnodes = ego3.number_of_nodes()
        
        ego3nodes = list(ego3.nodes)
        deg = sum(d for n, d in G.degree(nbunch=ego3nodes)) / float(nnodes)
        
        fraction3 = nnodes / number_of_nodes * 100
        percent3 = round(fraction3, 2)
        
        result['no. 3 step nodes'] = nnodes
        result['3 step % reached'] = percent3
        result['3 step nodes average degree'] = deg
        
        resultdf = pd.DataFrame.from_dict(result, orient='index')
        resultdf = resultdf.T
        
        temp_df = pd.concat([temp_df, resultdf])
        
        dfs_list.append(temp_df)

    k_steps = pd.concat(dfs_list)
    k_steps = k_steps[['node', 'no. 1 step nodes (degree)', '1 step % reached', '1 step nodes average degree', 'no. 2 step nodes','2 step % reached', '2 step nodes average degree', 'no. 3 step nodes', '3 step % reached', '3 step nodes average degree']]
    k_steps.set_index('node', inplace=True)
    
    node_measures = pd.concat([node_measures,centrality_ranked,k_steps], axis=1)
    node_measures.sort_values('node', inplace=True)
    
    #Export node measures as a CSV file
    csv_name =  name + '_node_measures_' + '.csv'   
    node_measures.to_csv(f'{OUTPUTS}{csv_name}', header = True, index = True)
    
    '''This section produces a dataframe of network level measures which are 
    exported as a CSV'''
    
    number_of_nodes = number_of_nodes + 1
    
    node_data_for_network_measures = (
        node_measures[['degree', '1 step % reached', '2 step % reached', '3 step % reached']]
        .rename(columns = {'degree':'Average Degree'})
        )
        
    number_of_edges = G.number_of_edges()
    density = nx.density(G)
    average_shortest_path_length = nx.average_shortest_path_length(G)
    average_clustering = nx.average_clustering(G)
    diameter = nx.diameter(G)
    radius = nx.radius(G)
    components = nx.number_connected_components(G_full)
    
    averages_for_network_measures = node_data_for_network_measures.mean()
    averages_for_network_measures = averages_for_network_measures.to_frame()
    averages_for_network_measures.reset_index(inplace=True)
    averages_for_network_measures.rename(columns = {'index':'', 0:name}, inplace=True)
    
    data = {'':['Number of Nodes', 'Number of Edges', 'Graph Density', 
            'Average Shortest Path (unweighted)', 'Average Clustering Co-efficient', 
            'Diameter', 'Radius', 'Total Components', 
            'Number of nodes not in giant compontent'],
        name:[number_of_nodes, number_of_edges, density, average_shortest_path_length,
             average_clustering, diameter, radius, components, 
             no_nodes_not_in_giant_component]}
    
    network_measures = pd.DataFrame(data)
    
    network_measures_final = pd.concat([network_measures,averages_for_network_measures])
    network_measures_final.reset_index(drop=True, inplace=True)
    network_measures_final.reindex([0,1,7,2,6,5,4,8,9,10])
    network_measures_final[name] = network_measures_final[name].round(2)
    
    #Export as CSV file
    csv_name =  name + '_network_measures' + '.csv'
    network_measures_final.to_csv(f'{OUTPUTS}{csv_name}', header = True, index = True)    
    
    '''If graph is not fully connected, export nodes not in giant compontent as a
    text file'''
    
    if is_connected == False:
        text_file_name = OUTPUTS + name + '_lonely_nodes' + '.txt'
        textfile = open(text_file_name, "w")
        for node in lonely_nodes:
            textfile.write(node + "\n")
        textfile.close()