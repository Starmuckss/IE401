# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 12:49:24 2022

@author: HP
"""
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as st
import math
import numpy as np
from datetime import datetime, timedelta
import random

#%% DATA PREPARATION
raw_materials_in_analysis = ['RM0001','RM0002','RM0003','RM0005','RM0006'] # to use all raw materials use raw_materials_in_analysis = list(weekly_startdard_deviation["Unnamed: 0"])

E_inventory = pd.read_excel(io="Results_1.96.xlsx",sheet_name="Inventory") # Starting inventories for each RM

starting_inventory_data = pd.read_excel(io="weekly_safety_stocks_1.96.xlsx",sheet_name="starting_inventory") # Starting inventories for each RM
purchase_decision = pd.read_excel(io="Results_1.96.xlsx",sheet_name="PurchaseBool",header = None) # Buy at day x decisions
purchase_amount = pd.read_excel(io="Results_1.96.xlsx",sheet_name="PurchaseAmount",header=None) # Buy x amount
daily_demand = pd.read_excel(io="weekly_safety_stocks_1.96.xlsx",sheet_name="Daily_Demand") # Usage of each RM i in day j
lead_time_data = pd.read_excel("weekly_safety_stocks_1.96.xlsx",sheet_name = "lead_times") # Lead Times for each RM

purchase_decision.index = raw_materials_in_analysis
purchase_amount.index = raw_materials_in_analysis

# Daily Demand Data Manipulation
daily_demand = daily_demand.rename({'Unnamed: 0':'MATERIAL NUMBER'},axis =1)
demand_transposed = daily_demand.T
new_header = demand_transposed.iloc[0] #grab the first row for the header
demand_transposed = demand_transposed[1:] #take the data less the header row
demand_transposed.columns = new_header #se

# Weekly standard deviation data preparation
weekly_standard_deviation = pd.read_excel("weekly_safety_stocks_1.96.xlsx",sheet_name = "weekly_startdard_deviation")
weekly_standard_deviation = weekly_standard_deviation.rename({"Unnamed: 0":"MATERIAL NUMBER"},axis=1)
weekly_standard_deviation_used = weekly_standard_deviation[weekly_standard_deviation["MATERIAL NUMBER"].isin(raw_materials_in_analysis)] # take rm's in analysis
weekly_standard_deviation_used.set_index("MATERIAL NUMBER",inplace=True)
weekly_standard_deviation_used_transposed = weekly_standard_deviation_used.transpose()

# ignored_days: 0 usage for all RM's. Holidays (Eid al-Fitr,Eid al-Adha,New Year's Day) (Ramazan,Kurban,Yılbaşı)
ignored_days = ['2022-05-01 00:00:00','2022-05-02 00:00:00','2022-05-03 00:00:00','2022-05-04 00:00:00','2022-07-09 00:00:00'
                ,'2022-07-10 00:00:00','2022-07-11 00:00:00','2022-07-12 00:00:00','2023-01-01 00:00:00']
ignore_timestamps = [datetime.strptime(x, "%Y-%m-%d %H:%M:%S") for x in ignored_days]

# Costs
holding_cost = 5
stockout_cost = 1000

#%% Simulation
def simulation(rm_id,demand_forecast_coefficient=1,lead_time_deviation=1,plot = False,start_date = datetime.strptime("2022-03-14 00:00:00", "%Y-%m-%d %H:%M:%S")):
    """
    raw_material_id : String, name of the column
    
    demand_forecast_coefficient : float, added to the simulation to 
    see different behaviors when demand is between 80%-120% of forecast
    default:1
    
    lead_time_deviation: int, deviate the lead_time to see different behaviours
    default: 1
    """
    
    lead_time = lead_time_data.loc[lead_time_data['MATERIAL NUMBER'] == rm_id, 'TRANSIT TIME'].iloc[0] 
    starting_inventory = starting_inventory_data.loc[starting_inventory_data['MATERIAL NUMBER'] == rm_id, 'Starting Inventory'].iloc[0]
    
    usage = demand_transposed[rm_id]
    usage.index = pd.to_datetime(usage.index,errors='ignore')
    #Purchase amount and decision
    order_decision = purchase_decision.loc[rm_id]
    order_amount = purchase_amount.loc[rm_id]
    
    #order_decision.index = usage.index
    #order_amount.index = usage.index

    # Manipulate demand
    demand_df = pd.DataFrame(usage) 
    random.seed(42)
    random_numbers = [(x,random.uniform(-1.5,1.5)) for x in range(1,53)]
    df_random = pd.DataFrame(random_numbers)
    df_random.columns = ["week","random_number"]
    
    weekly_standard_deviation_for_rm_id = pd.DataFrame(weekly_standard_deviation_used_transposed[rm_id])
    weekly_standard_deviation_for_rm_id.index = usage.index
    weekly_standard_deviation_for_rm_id['week'] = weekly_standard_deviation_for_rm_id.index.week
    weekly_standard_deviation_for_rm_id['year'] = weekly_standard_deviation_for_rm_id.index.year    
    

    merge = pd.merge(weekly_standard_deviation_for_rm_id,df_random,on="week")
    merge["noise"] = merge[rm_id] * merge["random_number"]
    merge.index = usage.index
    
    usage = usage + merge["noise"] 
    usage_day_index = usage.reset_index(drop=True)

    
    daily_inventory = [] # Hold the daily inventory for graphing purpose
    order = 0 # Days passed after an order is given
    stockout_days = 0 # Day count when stockout occurs (Stockout: inventory is negative)
    current_stock = starting_inventory
    
    total_cost_incurred = 0
    #day 0 day 1 day 2
    #simulation
    # Solve the issue for current_stock = current_stock - usage_day_index.loc[day-1] # IMPORTANT  
    
    for day in range(1,len(order_amount)):
        
        if day < lead_time:
            current_stock = current_stock - usage_day_index.loc[day-1] # Subtract demand from the inv 
            
        else:
            current_stock = current_stock - usage_day_index.loc[day-1] + order_amount[day - lead_time]
         
        total_cost_incurred += max(current_stock,0) * holding_cost 
        if current_stock < 0: # when Inventory is negative, stockout occurs
            stockout_days += 1 # Ne kadar stockout olduk?
            total_cost_incurred += stockout_cost 
            # bu günleri kaydet 
        daily_inventory.append(current_stock) # Add current inventory to daily_inventory list to graph it later        
    
    
    if plot:
        fig, ax = plt.subplots() 
        ax.plot(usage.index[:-1], daily_inventory, color="C0")
        #ax.plot(example_rm,reorder_point)
        plt.title(rm_id)    
        
    
    print("Results:","Total stockouts:", stockout_days,rm_id, total_cost_incurred )
     # Get the demand of a raw material
    
#simulation('RM0001',plot = True)
simulation('RM0002',plot = True)


    