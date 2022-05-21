# -*- coding: utf-8 -*-
"""
Created on Sat May 14 12:17:12 2022

@author: HP
"""
import pandas as pd
from SeniorDesignSSOrderingPolicySimulation import Simulation
import random
import numpy as np
import os 

dir_path = os.path.dirname(os.path.realpath(__file__))
output_directory = dir_path + "\\Experiment Results" # Data will be printed out here
if not os.path.exists(output_directory): # create the folder if not exists already
    os.mkdir(output_directory)



# Define USD-TL rates
days= range(0,330)
dollar_tl_increases = [x*0.01 + 15  for x in days ]
dollar_tl_stable = [15 for x in days ]
dollar_tl_decreases = [-x*0.01 + 15  for x in days ]

def single_experiment(rm,service_level,simulation_instance,x1,x2,lt_dev_p,lt_dev_x,exchange_rate,policy,max_stock_multiplier,results,plot):
    experiment_results = simulation_instance.simulation(rm,plot = plot,x1 = x1,x2 = x2,lt_dev_p=lt_dev_p,lt_dev_x=lt_dev_x,exchange_rate=exchange_rate)
    result = [rm,service_level]
    if exchange_rate == dollar_tl_stable:
        exc_rate = "USD-TL Stable"
    elif (exchange_rate == dollar_tl_increases):
        exc_rate = "USD-TL Increases"
    else:
        exc_rate = "USD-TL Decreases"
    
    stockouts = experiment_results[-1]
    result = result +[policy,max_stock_multiplier,x1,x2,lt_dev_p,lt_dev_x,exc_rate] +  experiment_results
    results.append(result)
    
    return stockouts


#%%
### Service level Experiments: Everything is the same, just service levels change, Service Levels: [90%,...99%]
dummy_simulation_instance = Simulation("RM0001",0.90)
dummy_simulation_instance.data_prep()
rm_list = dummy_simulation_instance.get_all_RM_ID()

for rm in rm_list: #
    results = []
   
    for service_level in [0.90,0.95,0.99]:        
        
        simulation_instance = Simulation(rm,service_level)
        simulation_instance.data_prep()   
        max_stock_multiplier = 2 # Starting value
        stockouts = single_experiment(rm=rm,service_level = service_level,simulation_instance=simulation_instance,x1 = 0,x2 = 0,lt_dev_p=0,lt_dev_x=1,exchange_rate=dollar_tl_stable,policy ="SS",max_stock_multiplier=max_stock_multiplier,results=results,plot =False)
        
        res = [stockouts]
        convergence = False
        while stockouts > 330*(1-service_level) and not convergence :
            max_stock_multiplier += 0.05
            stockouts = SS_experiment = single_experiment(rm=rm,service_level = service_level,simulation_instance=simulation_instance,x1 = 0,x2 = 0,lt_dev_p=0,lt_dev_x=1,exchange_rate=dollar_tl_stable,policy ="SS",max_stock_multiplier=max_stock_multiplier,results=results,plot =False)
            res.append(stockouts)
            try:
                if  res[-5] == res[-1]:
                    convergence = True
            except IndexError:
                continue
            
            
results_dataframe_for_single_rm = pd.DataFrame(data = results)
results_dataframe_for_single_rm.columns = ["RM ID","Service Level","Policy","MaxStock Multiplier","lower_bound","upper_bound","lt_dev_p","lt_dev_x","Exchange Rate","Holding Cost","Ordering Cost","Purchase Cost","Total Cost","Days Stockout Occurs"]
results_dataframe_for_single_rm.reset_index().to_excel(output_directory+"\\MaxStock Changes.xlsx")
