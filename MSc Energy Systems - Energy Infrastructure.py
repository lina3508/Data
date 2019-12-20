#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  8 12:08:46 2019

@author: raifa
"""

print("The program started successfully") #to show that the programm started running
import pandas as pd
import pandapower as pp
import numpy as np
import pandapower.networks as pn

net = pn.GBreducednetwork() #importing the database as the network for pandapower

results=pd.DataFrame() #creating a new dataframe called "results" for adding all the results obtained to selecting the most critical power lines in the UK
results["n_overload"]="" #adding a new column in the "results" for the number of overloaded lines
results["excess_overload"]="" #adding a new column in the "results" for the total overload excess

net.load['p_mw'] = net.load['p_mw'] * 0.8
net.sgen['p_mw'] = net.sgen['p_mw'] * 0.8
net.gen['p_mw'] = net.gen['p_mw'] * 0.8
#scale down the load, generator and static generator since the sum of loads in the GBreducednetwork in 2013 is 56GW and the maximum peak power rating in 2019 is 45GW

pp.runpp(net) #running the powerflow analysis with all lines intact
pp.to_excel(net,"GBreducednetworks.xlsx") #exporting the results into an excel document

results.at[:,"loading_percent"]=net.res_line["loading_percent"] #adding the loading percent for each line into the "results"
results.loc[net.res_line.loading_percent <= 100, 'before_drop_equal_or_greater_than_100'] = 0 
results.loc[net.res_line.loading_percent > 100, 'before_drop_equal_or_greater_than_100'] = 1 
#creating a new column in the results database for the initial overload
#setting the value equal to 0 if the line is not overloaded and 1 if it is

results.loc[net.res_line.loading_percent > 100, 'before_drop_excess_over_100'] = (net.res_line.loading_percent - 100)
results.loc[net.res_line.loading_percent <= 100, 'before_drop_excess_over_100'] = 0
#creating a new column in the results database for the excess overload before the line is dropped
#setting the value equal to the excess overload (if the line is overloaded) and 0 if it is not

x = range(0, len(net.res_line.index)) #setting a loop for dropping every line one at a time for all the index value in net.res_line
for i in x:

    pp.drop_lines(net, [i]) #dropping a line
    
    pp.runpp(net)  #running the powerflow analysis with the line dropped
    
    net.res_line.loc[net.res_line.loading_percent <= 100, 'after_drop_equal_or_greater_than_100'] = 0 
    net.res_line.loc[net.res_line.loading_percent > 100, 'after_drop_equal_or_greater_than_100'] = 1 
    #creating a new column in the net.res_lines database for the number of overloaded lines
    #setting the value equal to 0 if the line is not overloaded and 1 if it is
        
    net.res_line.loc[net.res_line.loading_percent > 100, 'after_drop_excess_over_100'] = (net.res_line.loading_percent - 100)
    net.res_line.loc[net.res_line.loading_percent <= 100, 'after_drop_excess_over_100'] = 0
    #creating a new column in the net.res_lines database for the excess overload
    #setting the value equal to the excess overload (if the line is overloaded) and 0 if it is not

    n_overload = np.sum(net.res_line.after_drop_equal_or_greater_than_100) - np.sum(results.before_drop_equal_or_greater_than_100)
    #creating a new variable to equal to the change in the number of overloaded lines as a result of dropping a given line
    
    excess_overload = np.sum(net.res_line.after_drop_excess_over_100) - np.sum(results.before_drop_excess_over_100)
    #creating a new variable to equal to the change in the excess overloads on the lines as a result of dropping a given line
    
    if results.loading_percent[i] >= 100 :
        n_overload = n_overload + 1
        excess_overload = excess_overload + (results.before_drop_excess_over_100[i])
        #adding 1 if the dropped line was already overloaded, thus counting the number of overloaded line with the dropped line
        #adding the excess overloaded of the dropped line before it was dropped thus calculating the excess including the dropped line
        
    results.at[i,"n_overload"]=n_overload #adding the number of overloaded lines calcualted in the loop to the "results"
    results.at[i,"excess_overload"]= excess_overload #adding the total excess overload on the lines calculated in the loop to the "results"
    
    net = pn.GBreducednetwork() #resetting the network (putting back the droppped line)
    net.load['p_mw'] = net.load['p_mw'] * 0.8
    net.sgen['p_mw'] = net.sgen['p_mw'] * 0.8
    net.gen['p_mw'] = net.gen['p_mw'] * 0.8
    #rescale down the load, generator and static generator since the sum of loads in the GBreducednetwork in 2013 is 56GW and the maximum peak power rating in 2019 is 45GW
    
print(results) #displaying the results
print("Program finished successfully") #signalling the end of the program