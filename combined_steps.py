# -*- coding: utf-8 -*-
"""
Created on Sun May  8 22:51:36 2022

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

dummy_simulation_instance = Simulation("RM0001",0.90)
dummy_simulation_instance.data_prep()
rm_list = dummy_simulation_instance.get_all_RM_ID()

def single_experiment(rm,service_level,simulation_instance,x1,x2,lt_dev_p,lt_dev_x,exchange_rate,policy,max_stock_multiplier,results,plot=False):
    experiment_results = simulation_instance.simulation(rm,plot = plot,x1 = x1,x2 = x2,lt_dev_p=lt_dev_p,lt_dev_x=lt_dev_x,exchange_rate=exchange_rate)
    result = [rm,service_level]
    if exchange_rate == dollar_tl_stable:
        exc_rate = "USD-TL Stable"
    elif (exchange_rate == dollar_tl_increases):
        exc_rate = "USD-TL Increases"
    else:
        exc_rate = "USD-TL Decreases"
        
    result = result +[policy,max_stock_multiplier,x1,x2,lt_dev_p,lt_dev_x,exc_rate] +  experiment_results
    results.append(result)

index = 0
#%%
### Service level Experiments: Everything is the same, just service levels change, Service Levels: [90%,...99%]
for rm in ["RM0013"]: 
    results = []
   
    for service_level in [x/100 for x in range(90,100)]:        
        
        simulation_instance = Simulation(rm,service_level)
        simulation_instance.data_prep()   
        SS_experiment = single_experiment(rm=rm,service_level = service_level,simulation_instance=simulation_instance,x1 = 0,x2 = 0,lt_dev_p=0,lt_dev_x=1,exchange_rate=dollar_tl_stable,policy ="SS",max_stock_multiplier=2,results=results)
        QR_experiment = single_experiment(rm,service_level = service_level,simulation_instance=simulation_instance,x1 = 0,x2 = 0,lt_dev_p=0,lt_dev_x=1,exchange_rate=dollar_tl_stable,policy ="QR",max_stock_multiplier=np.nan,results=results)
            
    results_dataframe_for_single_rm = pd.DataFrame(data = results)
    results_dataframe_for_single_rm.columns = ["RM ID","Service Level","Policy","MaxStock Multiplier","lower_bound","upper_bound","lt_dev_p","lt_dev_x","Exchange Rate","Holding Cost","Ordering Cost","Purchase Cost","Total Cost","Days Stockout Occurs"]
    results_dataframe_for_single_rm.to_excel(output_directory+"\\Service Level Changes.xlsx")

#%%
# Exchange Rate Experiments: Exchange_rate changes, only cost changes here (Bunu kaldırabiliriz, o kadar mantıklı değil)
for rm in ["RM0013"]: 
    results = []
    for service_level in [x/100 for x in range(90,100)]:        
        simulation_instance = Simulation(rm,service_level)
        simulation_instance.data_prep()   
        for usd_tl,string_usd_tl in [(dollar_tl_increases,"USD-TL Increases"),(dollar_tl_stable,"USD-TL Stable"),(dollar_tl_decreases,"USD-TL Decreases")]:
            experiment_results = simulation_instance.simulation(rm,plot = False,x1 = 0,x2 = 0,lt_dev_p=0,lt_dev_x=1,exchange_rate=usd_tl)
            result = [rm,service_level]
            result = result +[0,0,0,1,string_usd_tl] +  experiment_results
            results.append(result)
    results_dataframe_for_single_rm = pd.DataFrame(data = results)
    results_dataframe_for_single_rm.columns = ["RM ID","Service Level","lower_bound","upper_bound","lt_dev_p","lt_dev_x","Exchange Rate","Holding Cost","Ordering Cost","Purchase Cost","Total Cost","Days Stockout Occurs"]
    results_dataframe_for_single_rm.to_excel(output_directory+"\\Exchange Rate Changes.xlsx")        
#%%
# Demand Change Experiments: Only Demand Changes, no deviation on other aspects: 
# Demand Changes increases between (-1,1) Deviations: 50 experiments
# Demand Changes increases between (0,1) Deviations: 50 experiments
# Demand Changes increases between (-2,2) Deviations: 50 experiments
# Demand Changes increases between (0,2) Deviations: 50 experiments
for rm in rm_list: 
    results = []   
    for service_level in [0.90,0.95,0.99]:        
        simulation_instance = Simulation(rm,service_level)
        simulation_instance.data_prep()   
        random.seed(42)
            
        for i in range(0,50):
            limits = (-1,1)
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=limits[0],x2=limits[1],lt_dev_p = 0,lt_dev_x = 1,exchange_rate=dollar_tl_stable,results=results,policy ="QR",max_stock_multiplier=np.nan)
        for i in range(0,50):
            limits = (0,1)
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=limits[0],x2=limits[1],lt_dev_p = 0,lt_dev_x = 1,exchange_rate=dollar_tl_stable,results=results,policy ="QR",max_stock_multiplier=np.nan)
        for i in range(0,50):
            limits = (-2,2)
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=limits[0],x2=limits[1],lt_dev_p = 0,lt_dev_x = 1,exchange_rate=dollar_tl_stable,results=results,policy ="QR",max_stock_multiplier=np.nan)
        for i in range(0,50):
            limits = (0,2)
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=limits[0],x2=limits[1],lt_dev_p = 0,lt_dev_x = 1,exchange_rate=dollar_tl_stable,results=results,policy ="QR",max_stock_multiplier=np.nan)
    
results_dataframe_for_single_rm = pd.DataFrame(data = results)
results_dataframe_for_single_rm.columns = ["RM ID","Service Level","Policy","MaxStock Multiplier","lower_bound","upper_bound","lt_dev_p","lt_dev_x","Exchange Rate","Holding Cost","Ordering Cost","Purchase Cost","Total Cost","Days Stockout Occurs"]
aggregated_demand_deviations = results_dataframe_for_single_rm.groupby(["RM ID","Service Level",
                                             "lower_bound","upper_bound"]).mean()
results_dataframe_for_single_rm.to_excel(output_directory+"\\Demand Changes.xlsx")        

#%%
## Lead Time Deviation Experiments:
    # Demand Changes increases between (-1,1) Deviations: 50 experiments
    # Demand Changes increases between (0,1) Deviations: 50 experiments
    # Demand Changes increases between (-2,2) Deviations: 50 experiments
    # Demand Changes increases between (0,2) Deviations: 50 experiments

for rm in ["RM0013"]: 
    results = []   
    for service_level in [0.90,0.95,0.99]:        
        simulation_instance = Simulation(rm,service_level)
        simulation_instance.data_prep()   
        random.seed(42)
            
        for i in range(0,50):
            lead_time_deviations = [0.1,1.2] 
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=0,x2=0,lt_dev_p = lead_time_deviations[0],lt_dev_x = lead_time_deviations[1],exchange_rate=dollar_tl_stable,results=results)
        for i in range(0,50):
            lead_time_deviations = [0.2,1.2]
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=0,x2=0,lt_dev_p = lead_time_deviations[0],lt_dev_x = lead_time_deviations[1],exchange_rate=dollar_tl_stable,results=results)
        for i in range(0,50):
            lead_time_deviations = [0.1,1.1]
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=0,x2=0,lt_dev_p = lead_time_deviations[0],lt_dev_x = lead_time_deviations[1],exchange_rate=dollar_tl_stable,results=results)
        for i in range(0,50):
            lead_time_deviations = [0.2,1.1]
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=0,x2=0,lt_dev_p = lead_time_deviations[0],lt_dev_x = lead_time_deviations[1],exchange_rate=dollar_tl_stable,results=results)
    
    results_dataframe_for_single_rm = pd.DataFrame(data = results)
    results_dataframe_for_single_rm.columns = ["RM ID","Service Level","lower_bound","upper_bound","lt_dev_p","lt_dev_x","Exchange Rate","Holding Cost","Ordering Cost","Purchase Cost","Total Cost","Days Stockout Occurs"]
    aggregated_lead_time_deviations = results_dataframe_for_single_rm.groupby(["RM ID","Service Level",
                                                 "lt_dev_p","lt_dev_x"]).mean()
    results_dataframe_for_single_rm.to_excel(output_directory+"\\Lead Time Changes.xlsx")        
#%%
## Grand experiment, all parameters are put in at once 
results = []
for rm in rm_list[:10]: 
    
    for service_level in [0.90,0.95,0.99]:
        result = [rm,service_level]
        
        simulation_instance = Simulation(rm,service_level)
        simulation_instance.data_prep()
        single_experiment(rm= rm,service_level = service_level,policy="SS",max_stock_multiplier=2,simulation_instance = simulation_instance,x1=0,x2=0,lt_dev_p = 0,lt_dev_x = 1,exchange_rate=dollar_tl_stable,results=results)
        random.seed(42)
        
        random_numbers_for_exp_1 = [(random.uniform(-2,0),random.uniform(0,2),random.uniform(0,0.30),random.uniform(1,1.2)) for i in range(0,500)]
        for lower_bound,upper_bound,lt_dev_p,lt_dev_x in random_numbers_for_exp_1:
            
            SS_experiment = single_experiment(rm= rm,service_level = service_level,policy="SS",max_stock_multiplier=2,simulation_instance = simulation_instance,x1=lower_bound,x2=upper_bound,lt_dev_p = lt_dev_p,lt_dev_x = lt_dev_x,exchange_rate=dollar_tl_stable,results=results)
            QR_experiment = single_experiment(rm= rm,service_level = service_level,policy="QR",max_stock_multiplier=np.nan,simulation_instance = simulation_instance,x1=lower_bound,x2=upper_bound,lt_dev_p = lt_dev_p,lt_dev_x = lt_dev_x,exchange_rate=dollar_tl_stable,results=results)

#Save all results    
results_dataframe_for_single_rm = pd.DataFrame(data = results)
results_dataframe_for_single_rm.columns = ["RM ID","Service Level","Policy","MaxStock Multiplier","lower_bound","upper_bound","lt_dev_p","lt_dev_x","Exchange Rate","Holding Cost","Ordering Cost","Purchase Cost","Total Cost","Days Stockout Occurs"]    

#Groupby
averaged_results = results_dataframe_for_single_rm.groupby(["RM ID","Service Level","Policy"]).mean()
averaged_results.to_excel(output_directory+"\\Experiment_results.xlsx")






