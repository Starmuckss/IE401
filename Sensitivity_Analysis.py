# -*- coding: utf-8 -*-
"""
Created on Fri May 20 23:46:45 2022

@author: HP
"""
import pandas as pd
from SeniorDesignSSOrderingPolicySimulation import Simulation
import random
import numpy as np
import os 
import time

dir_path = os.path.dirname(os.path.realpath(__file__))
output_directory = dir_path + "\\Experiment Results" # Data will be printed out here
if not os.path.exists(output_directory): # create the folder if not exists already
    os.mkdir(output_directory)
most_used_10_rms = ['RM0085','RM0087','RM0049','RM0013','RM0081','RM0017','RM0073','RM0083','RM0108','RM0046']
def single_experiment(rm,service_level,simulation_instance,stockout_occurrence_cost,x1,x2,lead_time_deviation_present,expected_exchange_rate,policy,results,plot=False):
    experiment_results = simulation_instance.simulation(rm,plot = plot,stockout_occurrence_cost=stockout_occurrence_cost,x1 = x1,x2 = x2,lead_time_deviation_present= lead_time_deviation_present,expected_exchange_rate = expected_exchange_rate)
    result = [rm,service_level]
    
    if lead_time_deviation_present:
        lt_dev_present = "Yes"
    else:    
        lt_dev_present = "No"
    result = result +[policy,stockout_occurrence_cost,lt_dev_present,x1,x2,expected_exchange_rate] +  experiment_results
    results.append(result)
    # COLUMNS: RM_ID,Service Level, Policy,stockout_occurrence_cost , Lead Time Deviation Occurs, Demand Deviation Lower Bound, Demand Deviation Upper Bound,
    #Exchange Rate,total_holding_cost,total_ordering_cost,total_purchase_cost,stockout_cost,total_cost_incurred,stockout_days,type_2_service_level
tested_stockout_occurrence_costs = [x for x in range (100000,750000,50000)]    
results = []
random.seed(42)
random_numbers_for_experiment = [(random.uniform(-2,0),random.uniform(0,2),random.randrange(12,20)) for i in range(0,500)]

#%%% No Uncertainties

for rm in most_used_10_rms: 
    start = time.time()

    for service_level in [0.90,0.93,0.95,0.97,0.99]:
        result = [rm,service_level]
        
        simulation_instance = Simulation(rm,service_level)
        simulation_instance.data_prep()
        for stockout_occurrence_cost in tested_stockout_occurrence_costs:
            SS_experiment = single_experiment(rm= rm,service_level = service_level,policy="SS",stockout_occurrence_cost=stockout_occurrence_cost,simulation_instance = simulation_instance,x1=0,x2=0,lead_time_deviation_present=False,expected_exchange_rate = 15,results=results)
            QR_experiment = single_experiment(rm= rm,service_level = service_level,policy="QR",stockout_occurrence_cost=stockout_occurrence_cost,simulation_instance = simulation_instance,x1=0,x2=0,lead_time_deviation_present=False,expected_exchange_rate = 15,results=results)
    end = time.time()

    print(rm,"done in : " + str(end-start))

results_dataframe_for_single_rm = pd.DataFrame(data = results)
column_structure = ["RM ID","Service Level","Policy","Stockout Occurrence Cost","Lead Time Deviation Occurs","Demand Deviation Lower Bound","Demand Deviation Upper Bound",
                    "Exchange Rate","Holding Cost","Ordering Cost","Purchase Cost","Stockout Cost","Total Cost","Days Stockout Occurs","Type 2 Service Level"]
results_dataframe_for_single_rm.columns = column_structure
#Groupby
#averaged_results = results_dataframe_for_single_rm.groupby(["RM ID","Service Level","Policy","Stockout Occurrence Cost"]).mean()
results_dataframe_for_single_rm.to_excel(output_directory+"\\sensitivity_analysis_No_Uncertainties_Stockout_cost.xlsx")    




#%% Uncertainties
for rm in most_used_10_rms: 
    start = time.time()

    for service_level in [0.90,0.93,0.95,0.97,0.99]:
        result = [rm,service_level]
        
        simulation_instance = Simulation(rm,service_level)
        simulation_instance.data_prep()
        for stockout_occurrence_cost in tested_stockout_occurrence_costs:
        
            for lower_bound,upper_bound,expected_exchange_rate in random_numbers_for_experiment:
                
                SS_experiment = single_experiment(rm= rm,service_level = service_level,policy="SS",stockout_occurrence_cost=stockout_occurrence_cost,simulation_instance = simulation_instance,x1=lower_bound,x2=upper_bound,lead_time_deviation_present=True,expected_exchange_rate = expected_exchange_rate,results=results)
                QR_experiment = single_experiment(rm= rm,service_level = service_level,policy="QR",stockout_occurrence_cost=stockout_occurrence_cost,simulation_instance = simulation_instance,x1=lower_bound,x2=upper_bound,lead_time_deviation_present=True,expected_exchange_rate = expected_exchange_rate,results=results)
    end = time.time()

    print(rm,"done in : " + str(end-start))
            
#Save all results    
results_dataframe_for_single_rm = pd.DataFrame(data = results)
column_structure = ["RM ID","Service Level","Policy","Stockout Occurrence Cost","Lead Time Deviation Occurs","Demand Deviation Lower Bound","Demand Deviation Upper Bound",
                    "Exchange Rate","Holding Cost","Ordering Cost","Purchase Cost","Stockout Cost","Total Cost","Days Stockout Occurs","Type 2 Service Level"]
results_dataframe_for_single_rm.columns = column_structure
#Groupby
averaged_results = results_dataframe_for_single_rm.groupby(["RM ID","Service Level","Policy","Stockout Occurrence Cost"]).mean()
averaged_results.reset_index().to_excel(output_directory+"\\sensitivity_analysis_Stockout_cost.xlsx")    
