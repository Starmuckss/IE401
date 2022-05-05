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

usage_data = pd.read_excel("input data\\Safety Stock Çalışma.xlsx",sheet_name="USAGE")
lead_time_data = pd.read_excel("input data\\Safety Stock Çalışma.xlsx",sheet_name="DATA")
ordering_cost_data = pd.read_excel("input data\\Ordering Cost.xlsx")
material_type_data = pd.read_csv("input data\\MaterialType.csv",sep=";")
material_type_data = material_type_data[["MALZEME","Category"]]

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
grouped_by_week_sum = clean_df.groupby(['week','year']).sum()
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
    
    # Purchase Cost (Dollars per kg)
    purchase_cost = pd.DataFrame(data = {"Category": ["Natural Rubber","Metallic reinforc.","Carbon Black","Chemical","Bead","Synthetic Rubber","Textile reinforc."],
                                         "Purchase Cost": [2,1,3,5,2,1.77,1.18] })
    purchase_cost["Holding Cost"] = 0.10 * (1/365) * purchase_cost["Purchase Cost"] # 10% interest for a dollar annually	 
    purchase_and_holding_costs = pd.merge(material_type_data,purchase_cost,on='Category',how='inner')
    
     # Lead Times
    lt_data = lead_time_data[lead_time_data['MATERIAL NUMBER'].isin(RM_list)] # Lead times for 118 Raw Materials
    
    # Ordering Cost
    order_data = pd.merge(lt_data,ordering_cost_data,on='COUNTRY',how='inner')
    
    
    
    # Prepare data to be used in Cplex, make rows contain RM data again
    grouped_by_week_safety_stock.reset_index()
    grouped_by_week_safety_stock = grouped_by_week_safety_stock.sort_values(['year','week'],ascending=[True,True])
    transposed = grouped_by_week_safety_stock.reset_index()
    transposed = transposed.transpose()
    
    # Weekly Usage Data (FOR DATA ANALYSIS)
    grouped_by_week_sum = grouped_by_week_sum.sort_values(['year','week'],ascending=[True,True])
    
    # Starting inventory: avg. demand * leadtime * 2
    starting_inventory_list = list()
    
    for rm_id in list(RM_list):
        lead_time = lead_time_data.loc[lead_time_data['MATERIAL NUMBER'] == rm_id, 'TRANSIT TIME'].iloc[0] 
        rm_data = grouped_by_week_averages[rm_id]
        first_week_average_demand = rm_data.loc[11].iloc[0] # 11th week is the first week of the data
        starting_inventory =  first_week_average_demand * lead_time * 2 
        
        starting_inventory_list.append(starting_inventory)
        
    starting_inventory_df = pd.DataFrame(data = {'MATERIAL NUMBER': RM_list,'Starting Inventory': starting_inventory_list})     

    
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
    transposed_weekly_startdard_deviation = weekly_startdard_deviation.transpose(   ) # Transpose to match cplex format
    
    
    
    
    
    with pd.ExcelWriter("Output Data\\weekly_safety_stocks_"+ str(z_score) + ".xlsx") as writer:
        transposed_weekly_safety_stock_data.to_excel(writer,sheet_name='weekly_safety_stock')
        transposed_weekly_startdard_deviation.to_excel(writer,sheet_name='weekly_startdard_deviation')
        order_data.to_excel(writer,sheet_name='order_data')
        starting_inventory_df.to_excel(writer,sheet_name = 'starting_inventory')
        purchase_and_holding_costs.to_excel(writer,sheet_name = "purchase_and_holding_costs")
        merged_weeks_and_days_rop.to_excel(writer,sheet_name = "Reorder_Points")        
        daily_demand.to_excel(writer,sheet_name = "Daily_Demand") 
        grouped_by_week_sum.to_excel(writer,sheet_name= "Weekly_Demand")
    
#grouped_by_week_safety_stock.to_excel('weekly_safety_stocks.xlsx')

 

