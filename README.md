# US-Corporate-Community
Scripts, data and networks for 'The Policy-Planning Capacity of the American Corporate Community: Corporations, Policy-Oriented Nonprofits, and the Inner Circle in 1935-1936 and 2010-2011'.

1936_networks.py, 2011_networks and 2011_networks_BC each produce a set of bipartite and single mode networks using the CSVs in the data folder. As detailed in the article, the third of these sets of networks includes the Business Council rather than the Business Roundtable, but is otherwise identical to the second. These networks are exported as pickle and Gephi files in separate subfolders.

networks_analysis.py produces CSVs in the network_analysis_data_tables subfolder that contain a range of network and node level measures for the largest component of these networks. The 'lonely nodes' txt files are lists of individuals or organisations outside of the largest component.

The network measures and Gephi files can be downloaded directly, or the scripts can be run locally with the data folder in the sequence above.