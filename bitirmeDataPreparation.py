# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 17:55:59 2022

@author: HP
"""
import pandas as pd
import openpyxl
import matplotlib.pyplot as plt
import math
import time
import datetime as dt

usage_data = pd.read_excel("Safety Stock Çalışma.xlsx",sheet_name="USAGE")
lead_time_data = pd.read_excel("Safety Stock Çalışma.xlsx",sheet_name="DATA")

usage_data # Rows: Material Columns: Time

df = usage_data.transpose() # After transpose: Rows: Time, Columns: Raw Material Data
df = df.rename(columns=df.iloc[0]).drop(df.index[0])
df = df.dropna()

df[df.columns[:]] = df[df.columns[:]].apply(pd.to_numeric) # columns to numeric

clean_df = df.loc[:, (df != 0).any(axis=0)] #Remove raw materials with all 0 values

clean_df.index = pd.to_datetime(clean_df.index ) #Datetime the index

clean_df = clean_df.loc[(df!=0).any(axis=1)] # Remove holiday data, where all rm usage is 0

RM_list = clean_df.columns.copy() # RM names, all 0 RMs removed, (118 Raw materials)

clean_df['week'] = clean_df.index.week # Get week of days in data
clean_df['year'] = clean_df.index.year # Get year of days in data

grouped_by_week_averages = clean_df.groupby(['week','year']).mean() #Weekly averages 
grouped_by_week_std = clean_df.groupby(['week','year']).std() #Weekly standart deviations

for z_score in [1.645,1.96,2.575]: # [90%,95%,99%]
    grouped_by_week_safety_stock = pd.DataFrame()
    
    # Calculate weekly safety stock for each Raw Material
    for rm_id in list(RM_list):
        lead_time = lead_time_data.loc[lead_time_data['MATERIAL NUMBER'] == rm_id, 'TRANSIT TIME'].iloc[0] 
        rm_data = grouped_by_week_std[rm_id]
        safety_stock_data =  rm_data * lead_time * z_score 
        
        if len(grouped_by_week_safety_stock) != 0:
            grouped_by_week_safety_stock[rm_id] = safety_stock_data
        else:
            grouped_by_week_safety_stock = safety_stock_data    
            grouped_by_week_safety_stock = pd.DataFrame(grouped_by_week_safety_stock)
    
    # Prepare data to be used in Cplex, make rows contain RM data again
    grouped_by_week_safety_stock.reset_index()
    grouped_by_week_safety_stock = grouped_by_week_safety_stock.sort_values(['year','week'],ascending=[True,True])
    transposed = grouped_by_week_safety_stock.reset_index()
    transposed = transposed.transpose()
    
    # Lead Times
    lt_data = lead_time_data[lead_time_data['MATERIAL NUMBER'].isin(RM_list)] # Lead times for 118 Raw Materials
    
    # Starting inventory: avg. demand * leadtime * 2 ####!!! RM 160 sıkıntılı
    starting_inventory_list = list()
    
    for rm_id in list(RM_list):
        lead_time = lead_time_data.loc[lead_time_data['MATERIAL NUMBER'] == rm_id, 'TRANSIT TIME'].iloc[0] 
        rm_data = grouped_by_week_averages[rm_id]
        first_week_average_demand = rm_data.loc[11].iloc[0] # 11th week is the first week of the data
        starting_inventory =  first_week_average_demand * lead_time * 2 
        
        starting_inventory_list.append(starting_inventory)
        
    starting_inventory_df = pd.DataFrame(data = {'MATERIAL NUMBER': RM_list,'Starting Inventory': starting_inventory_list})     

    #Costs: Stockout cost, inventory holding costs
    holding_cost =[5 for x in RM_list] # 5 for all of them (Assumption)
    stockout_cost =[1000 for x in RM_list] # 10 for all of them (Assumption)      
    cost_data_dataframe = pd.DataFrame(data = {'MATERIAL NUMBER': RM_list,'Holding Costs': holding_cost,'Stockout Costs':stockout_cost})
    
    #daily Demand 
    daily_demand = clean_df.transpose()
    
    #safety stock
    new = pd.merge(clean_df,grouped_by_week_safety_stock.reset_index(),on='week',how='left')
    new_ss = new[[x for x in new.columns if '_y' in x]]
    transposed_weekly_safety_stock_data = new_ss.transpose()
    
    reorder_points = pd.DataFrame()
    #Reorder Point
    for rm_id in list(RM_list):
        lead_time = lead_time_data.loc[lead_time_data['MATERIAL NUMBER'] == rm_id, 'TRANSIT TIME'].iloc[0] 
        rm_data = grouped_by_week_averages[rm_id]
            
        reorder_point = rm_data * lead_time 
        
        if len(reorder_points) != 0:
            reorder_points[rm_id] = reorder_point
        else:
            reorder_points = reorder_point    
            reorder_points = pd.DataFrame(reorder_point)
        
    merged_with_clean_df = pd.merge(clean_df,reorder_points.reset_index(),on='week',how='left')
    merged_weeks_and_days_rop = merged_with_clean_df[[x for x in merged_with_clean_df.columns if '_y' in x]]
    merged_weeks_and_days_rop = merged_weeks_and_days_rop.transpose()
    
    # Weekly stardard deviation (Will be used for adding noise to the data)
    weekly_startdard_deviation = pd.merge(clean_df,grouped_by_week_std.reset_index(),on='week',how='left')
    weekly_startdard_deviation = weekly_startdard_deviation[[x for x in new.columns if '_y' in x]]
    weekly_startdard_deviation.columns = [x.split("_")[0] for x in weekly_startdard_deviation.columns]
    transposed_weekly_startdard_deviation = weekly_startdard_deviation.transpose() # Transpose to match cplex format
    
    with pd.ExcelWriter("weekly_safety_stocks_"+ str(z_score) + ".xlsx") as writer:
        transposed_weekly_safety_stock_data.to_excel(writer,sheet_name='weekly_safety_stock')
        transposed_weekly_startdard_deviation.to_excel(writer,sheet_name='weekly_startdard_deviation')
        lt_data.to_excel(writer,sheet_name='lead_times')
        starting_inventory_df.to_excel(writer,sheet_name = 'starting_inventory')
        cost_data_dataframe.to_excel(writer,sheet_name = "holding_and_stockout_costs")
        merged_weeks_and_days_rop.to_excel(writer,sheet_name = "Reorder_Points")        
        daily_demand.to_excel(writer,sheet_name = "Daily_Demand") 
#grouped_by_week_safety_stock.to_excel('weekly_safety_stocks.xlsx')
# new = pd.merge(clean_df,grouped_by_week_safety_stock.reset_index(),on='week',how='outer') gibi bir şeyle daily demand we safety_stock

#%%
# Safety Stock = Avg. Weekly Standard dev * Lead Time * z score
 

