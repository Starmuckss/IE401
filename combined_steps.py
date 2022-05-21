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
dollar_tl_increases = [x*0.01 + 15  for x in days]
dollar_tl_stable = [15 for x in days]
dollar_tl_decreases = [-x*0.01 + 15  for x in days]

most_used_10_rms = ['RM0085','RM0087','RM0049','RM0013','RM0081','RM0017','RM0073','RM0083','RM0108','RM0046']

column_structure = ["RM ID","Service Level","Policy","Lead Time Deviation Occurs","Demand Deviation Lower Bound","Demand Deviation Upper Bound",
                                           "Exchange Rate","Holding Cost","Ordering Cost","Purchase Cost","Stockout Cost","Total Cost","Days Stockout Occurs","Type 2 Service Level"]
def single_experiment(rm,service_level,simulation_instance,x1,x2,lead_time_deviation_present,expected_exchange_rate,policy,results,plot=False):
    experiment_results = simulation_instance.simulation(rm,plot = plot,x1 = x1,x2 = x2,lead_time_deviation_present= lead_time_deviation_present,expected_exchange_rate = expected_exchange_rate)
    result = [rm,service_level]
    
    if lead_time_deviation_present:
        lt_dev_present = "Yes"
    else:    
        lt_dev_present = "No"
    result = result +[policy,lt_dev_present,x1,x2,expected_exchange_rate] +  experiment_results
    results.append(result)
    # COLUMNS: RM_ID,Service Level, Policy, Lead Time Deviation Occurs, Demand Deviation Lower Bound, Demand Deviation Upper Bound, Exchange Rate,total_holding_cost,total_ordering_cost,total_purchase_cost,stockout_cost,total_cost_incurred,stockout_days,type_2_service_level
#%%
### Service level Experiments: Everything is the same, just service levels change, Service Levels: [90%,...99%]
results = []
for rm in most_used_10_rms: 
    for service_level in [x/100 for x in range(90,100)]:        
        simulation_instance = Simulation(rm,service_level)
        simulation_instance.data_prep()   
        SS_experiment = single_experiment(rm=rm,service_level = service_level,simulation_instance=simulation_instance,x1 = 0,x2 = 0,lead_time_deviation_present = False,expected_exchange_rate = 15,policy ="SS",results=results)
        QR_experiment = single_experiment(rm=rm,service_level = service_level,simulation_instance=simulation_instance,x1 = 0,x2 = 0,lead_time_deviation_present=False,expected_exchange_rate = 15,policy ="QR",results=results)
            
results_dataframe_for_single_rm = pd.DataFrame(data = results)
results_dataframe_for_single_rm.columns = column_structure
results_dataframe_for_single_rm.reset_index().to_excel(output_directory+"\\Service Level Changes.xlsx")
      
#%%
# Demand Change Experiments: Only Demand Changes, no deviation on other aspects: 
# Demand Changes increases between (-0.5,0.5) Deviations: 50 experiments
# Demand Changes increases between (-1,1) Deviations: 50 experiments
# Demand Changes increases between (-1.5,1.5) Deviations: 50 experiments
# Demand Changes increases between (-2,2) Deviations: 50 experiments
# Demand Changes increases between (0,1) Deviations: 50 experiments
# Demand Changes increases between (0,2) Deviations: 50 experiments

results = []   
for rm in most_used_10_rms: 
    for service_level in [0.90,0.93,0.95,0.97,0.99]:        
        simulation_instance = Simulation(rm,service_level)
        simulation_instance.data_prep()   
        random.seed(42) 
        for i in range(0,50):
            limits = (0.5,0.5)
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=limits[0],x2=limits[1],lead_time_deviation_present=False,expected_exchange_rate=15,results=results,policy ="QR")
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=limits[0],x2=limits[1],lead_time_deviation_present=False,expected_exchange_rate=15,results=results,policy ="SS")
        for i in range(0,50): 
            limits = (-1,1)
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=limits[0],x2=limits[1],lead_time_deviation_present=False,expected_exchange_rate=15,results=results,policy ="QR")
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=limits[0],x2=limits[1],lead_time_deviation_present=False,expected_exchange_rate=15,results=results,policy ="SS")
        for i in range(0,50):
            limits = (-1.5,1.5)
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=limits[0],x2=limits[1],lead_time_deviation_present=False,expected_exchange_rate=15,results=results,policy ="QR")
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=limits[0],x2=limits[1],lead_time_deviation_present=False,expected_exchange_rate=15,results=results,policy ="SS")
        for i in range(0,50):
            limits = (-2,2)
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=limits[0],x2=limits[1],lead_time_deviation_present=False,expected_exchange_rate=15,results=results,policy ="QR")
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=limits[0],x2=limits[1],lead_time_deviation_present=False,expected_exchange_rate=15,results=results,policy ="SS")
        for i in range(0,50):
            limits = (0,1)
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=limits[0],x2=limits[1],lead_time_deviation_present=False,expected_exchange_rate=15,results=results,policy ="QR")
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=limits[0],x2=limits[1],lead_time_deviation_present=False,expected_exchange_rate=15,results=results,policy ="SS")
        for i in range(0,50):
            limits = (0,2)
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=limits[0],x2=limits[1],lead_time_deviation_present=False,expected_exchange_rate=15,results=results,policy ="QR")
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=limits[0],x2=limits[1],lead_time_deviation_present=False,expected_exchange_rate=15,results=results,policy ="SS")
            
results_dataframe_for_single_rm = pd.DataFrame(data = results)
results_dataframe_for_single_rm.columns = column_structure
aggregated_demand_deviations = results_dataframe_for_single_rm.groupby(["RM ID","Service Level","Policy",
                                             "Demand Deviation Lower Bound","Demand Deviation Upper Bound"]).mean()
aggregated_demand_deviations.reset_index().to_excel(output_directory+"\\Demand Changes.xlsx")        

#%%
## Lead Time Deviation Experiments:
 
results = []   
for rm in most_used_10_rms: 
    for service_level in [0.90,0.93,0.95,0.97,0.99]:        
        simulation_instance = Simulation(rm,service_level)
        simulation_instance.data_prep()   
        random.seed(42)
        for i in range(0,400):
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=0,x2=0,lead_time_deviation_present=True,expected_exchange_rate=15,results=results,policy ="SS")
            single_experiment(rm= rm,service_level = service_level,simulation_instance = simulation_instance,x1=0,x2=0,lead_time_deviation_present=True,expected_exchange_rate=15,results=results,policy ="QR")
    
results_dataframe_for_single_rm = pd.DataFrame(data = results)
results_dataframe_for_single_rm.columns = column_structure
aggregated_lead_time_deviations = results_dataframe_for_single_rm.groupby(["RM ID","Service Level","Policy"]).mean()
aggregated_lead_time_deviations.reset_index().to_excel(output_directory+"\\Lead Time Changes.xlsx")        
#%%
## Grand experiment, all parameters are put in at once 
results = []
for rm in most_used_10_rms: 
    random.seed(42)
    random_numbers_for_experiment = [(random.uniform(-2,0),random.uniform(0,2),random.randrange(12,20)) for i in range(0,500)]

    for service_level in [0.90,0.93,0.95,0.97,0.99]:
        result = [rm,service_level]
        
        simulation_instance = Simulation(rm,service_level)
        simulation_instance.data_prep()
        
        for lower_bound,upper_bound,expected_exchange_rate in random_numbers_for_experiment:
            
            SS_experiment = single_experiment(rm= rm,service_level = service_level,policy="SS",simulation_instance = simulation_instance,x1=lower_bound,x2=upper_bound,lead_time_deviation_present=True,expected_exchange_rate = expected_exchange_rate,results=results)
            QR_experiment = single_experiment(rm= rm,service_level = service_level,policy="QR",simulation_instance = simulation_instance,x1=lower_bound,x2=upper_bound,lead_time_deviation_present=True,expected_exchange_rate = expected_exchange_rate,results=results)

#Save all results    
results_dataframe_for_single_rm = pd.DataFrame(data = results)
results_dataframe_for_single_rm.columns = column_structure
#Groupby
averaged_results = results_dataframe_for_single_rm.groupby(["RM ID","Service Level","Policy"]).mean()
averaged_results.reset_index().to_excel(output_directory+"\\Experiment_results.xlsx")






