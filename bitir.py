# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 08:29:41 2022

@author: HP
"""
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as st
import math

usage_data = pd.read_excel("Safety Stock Çalışma.xlsx",sheet_name="USAGE")
usage_data.dropna(axis =1,inplace=True)
supply_data = pd.read_excel("Safety Stock Çalışma.xlsx",sheet_name="DATA")

df = usage_data.transpose() # after transpose: Columns have RM data 
df = df.rename(columns=df.iloc[0]).drop(df.index[0]) # First row as column names

df = df.loc[:, (df != 0).any(axis=0)] # drop 0 raw materials

df = df.loc[~(df==0).all(axis=1)] # Drop the days with zero values : New years': 1 Day, Ramadan: 4 Days, Eid-al-Adha (Kurban Bayramı): 4 Days


def simulation(rm_id,demand_forecast_coefficient=1,lead_time_deviation=1,confidence_interval=0.95,plot = False):
    """
    raw_material_id : String, name of the column
    
    demand_forecast_coefficient : float, added to the simulation to 
    see different behaviors when demand is between 80%-120% of forecast
    default:1
    
    lead_time_deviation: int, deviate the lead_time to see different behaviours
    default: 1
    
    confidence_interval: float between 0 and 1. Confidence Interval
    default:  0.95
    
    plot: Boolean, Give True to plot the graph
    default:False
    """
    
    example_rm = df[[rm_id]] # Get the demand of a raw material
        
    df[rm_id] = df[rm_id] * demand_forecast_coefficient  # Apply demand deviation
    
    mean = example_rm[rm_id].mean() # Mean of the yearly demand
    stdev = example_rm[rm_id].std() # Standart Deviation of the yearly demand

    # Get lead time information from supply data dataframe, then add deviation 
    lead_time = math.ceil(supply_data.loc[supply_data['MATERIAL NUMBER'] == rm_id, 'TRANSIT TIME'].iloc[0] * lead_time_deviation) 
    min_batch_size = supply_data.loc[supply_data['MATERIAL NUMBER'] == rm_id, 'MIN BATCH SIZE'].iloc[0] 
    
    # Python works with 1 tail z-score, convert it into 2 tails
    converted = (1 - confidence_interval)/2
    z_score = st.norm.ppf(1-converted)
    
    safety_stock = stdev*z_score*lead_time**(1/2) # Safety stock 
    reorder_point = mean * lead_time + safety_stock # reorder point
    
    starting_stock = mean * lead_time * 2   #başlangıç stoğu = malzemenin günlük kullanım * termin süresi * 2
    current_stock = starting_stock
    
    daily_inventory = [] # Hold the daily inventory for graphing purpose
    order = 0 # Days passed after an order is given
    stockout_days = 0 # Day count when stockout occurs (Stockout: inventory is negative)
    
    #simulation
    for date in example_rm.index:
        current_stock = current_stock - example_rm.loc[date,rm_id] # Subtract demand fro mthe 
        
        if current_stock < reorder_point: # When under reorder point, order min_batch_size of units
            order += 1 
        
        if order >= lead_time: # When order pass lead time, order is fulfilled
            current_stock = current_stock + min_batch_size # add order to current inventory
            order = 0  # reset order      
        
        if current_stock < 0: # when Inventory is negative, stockout occurs
            stockout_days += 1 
        daily_inventory.append(current_stock) # Add current inventory to daily_inventory list to graph it later
    
    if plot:
        fig, ax = plt.subplots() 
        ax.plot(example_rm.index, daily_inventory, color="C0")
        #ax.plot(example_rm,reorder_point)
        plt.title(rm_id)    
    
    print("Results:","Total stockouts:", stockout_days,rm_id,demand_forecast_coefficient,lead_time_deviation,confidence_interval )
#%%
import random
random.seed(42)
for i in range(50):
    demand_forecast_coefficient = random.uniform(0.8,1.2)
    lead_time_deviation = random.uniform(0.8,1.2)
    confidence_interval = 0.99 # change to 0.99 and see results
    simulation('RM0003',demand_forecast_coefficient,lead_time_deviation,confidence_interval,plot=(True))
