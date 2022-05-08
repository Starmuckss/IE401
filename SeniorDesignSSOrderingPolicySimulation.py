# -*- coding: utf-8 -*-
"""
Created on Fri May  6 20:25:18 2022

@author: HP
"""
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random
import math
import warnings;   warnings.filterwarnings("ignore")
import os
#%% TODO
# Add Exchange Rate + +
# Add Purchase Cost + +
# Add ordering cost + + 
# Add Lead time deviation + + 
# Add distribution
# Calculate q ?
# Total cost u tek göstermek yerine, holding cost order cost gibi ayrı ayrı gösterelim +
#%% DATA PREPARATION

dir_path = os.path.dirname(os.path.realpath(__file__))


raw_materials_in_analysis = ['RM0001','RM0002','RM0003','RM0005','RM0006'] # to use all raw materials use )

starting_inventory_data = pd.read_excel(io="Output Data\\weekly_safety_stocks_1.96.xlsx",sheet_name="starting_inventory") # Starting inventories for each RM
daily_demand = pd.read_excel(io="Output Data\\weekly_safety_stocks_1.96.xlsx",sheet_name="Daily_Demand") # Usage of each RM i in day j
order_data = pd.read_excel("Output Data\\weekly_safety_stocks_1.96.xlsx",sheet_name = "order_data") # Lead Times for each RM
#starting_inventory_data = pd.read_excel(io="data\\MaterialType.xlsx",sheet_name="starting_inventory") # Starting inventories for each RM
reorder_point_data = pd.read_excel("Output Data\\weekly_safety_stocks_1.96.xlsx",sheet_name = "Reorder_Points")
purchase_and_holding_cost_data = pd.read_excel("Output Data\\weekly_safety_stocks_1.96.xlsx",sheet_name = "purchase_and_holding_costs")
max_stocks = pd.read_excel("Output Data\\weekly_safety_stocks_1.96.xlsx",sheet_name = "max_stocks")


raw_materials_in_analysis = list(order_data["MATERIAL NUMBER"])

# Daily Demand Data Manipulation
daily_demand = daily_demand.rename({'Unnamed: 0':'MATERIAL NUMBER'},axis =1)
demand_transposed = daily_demand.T
new_header = demand_transposed.iloc[0] #grab the first row for the header
demand_transposed = demand_transposed[1:] #take the data less the header row
demand_transposed.columns = new_header #se

# Daily Demand Data Manipulation
reorder = reorder_point_data.rename({'Unnamed: 0':'MATERIAL NUMBER'},axis =1)
reorder_transposed = reorder.T
new_header = reorder_transposed.iloc[0] #grab the first row for the header
reorder_transposed = reorder_transposed[1:] #take the data less the header row
reorder_transposed.columns = new_header #se
reorder_transposed.columns  = [x.split("_")[0] for x in reorder_transposed.columns ]

# Weekly standard deviation data preparation
weekly_standard_deviation = pd.read_excel("Output Data\\weekly_safety_stocks_1.96.xlsx",sheet_name = "weekly_startdard_deviation")
weekly_standard_deviation = weekly_standard_deviation.rename({"Unnamed: 0":"MATERIAL NUMBER"},axis=1)
weekly_standard_deviation_used = weekly_standard_deviation[weekly_standard_deviation["MATERIAL NUMBER"].isin(raw_materials_in_analysis)] # take rm's in analysis
weekly_standard_deviation_used.set_index("MATERIAL NUMBER",inplace=True)
weekly_standard_deviation_used_transposed = weekly_standard_deviation_used.transpose()

# ignored_days: 0 usage for all RM's. Holidays (Eid al-Fitr,Eid al-Adha,New Year's Day) (Ramazan,Kurban,Yılbaşı)
#ignored_days = ['2022-05-01 00:00:00','2022-05-02 00:00:00','2022-05-03 00:00:00','2022-05-04 00:00:00','2022-07-09 00:00:00'
#                ,'2022-07-10 00:00:00','2022-07-11 00:00:00','2022-07-12 00:00:00','2023-01-01 00:00:00']
#ignore_timestamps = [datetime.strptime(x, "%Y-%m-%d %H:%M:%S") for x in ignored_days]

#Exchange rate y= 0.01x + 15, y = 15, y = - 0.01x + 15
days = range(0,330)
dollar_tl_increases = [x*0.01 + 15  for x in days ]
dollar_tl_stable = [15 for x in days ]
dollar_tl_decreases = [-x*0.01 + 15  for x in days ]
    

#start_date = datetime.strptime("2022-03-14 00:00:00", "%Y-%m-%d %H:%M:%S")
#%% Simulation
def simulation(rm_id,plot = False,x1 = -1, x2 = 1,
               lt_dev_p = 0,lt_dev_x = 0, exchange_rate = dollar_tl_stable):
    """
    raw_material_id : String, name of the column
    
    x1: float, lower bound for demand deviation
    x2: float, upper bound for demand deviation
    lt_dev_p: float, lead time deviation occurance chance, lt_dev_p = 0.05 means there will be a change in leadtime with 5% chance
    lt_dev_X: float, Lead time deviation rate. lt_dev_x = 1.2 means that lead time will be ---> normal leadtime * lt_dev_x
    exchange_rate: List, Exchange rate for each day in simulation
    
    """
    
    starting_inventory = starting_inventory_data.loc[starting_inventory_data['MATERIAL NUMBER'] == rm_id, 'Starting Inventory'].iloc[0]
    min_batch_size = order_data.loc[order_data['MATERIAL NUMBER'] == rm_id,"MIN BATCH SIZE"].iloc[0]
    purchase_cost =  purchase_and_holding_cost_data.loc[purchase_and_holding_cost_data["MALZEME"] == rm_id,"Purchase Cost"].iloc[0]
    holding_cost =  purchase_and_holding_cost_data.loc[purchase_and_holding_cost_data["MALZEME"] == rm_id,"Holding Cost"].iloc[0]
    order_cost = order_data.loc[order_data['MATERIAL NUMBER'] == rm_id,"Ordering Cost"].iloc[0]
    reorder_point_list = reorder_transposed[rm_id]
    
    usage = demand_transposed[rm_id]
    usage.index = pd.to_datetime(usage.index,errors='ignore')
    #Purchase amount and decision
   
    # Manipulate demand
    demand_df = pd.DataFrame(usage) 
    random.seed(42)
    random_numbers = [(x,random.uniform(x1,x2)) for x in range(1,53)]
    df_random = pd.DataFrame(random_numbers)
    df_random.columns = ["week","random_number"]
    
    weekly_standard_deviation_for_rm_id = pd.DataFrame(weekly_standard_deviation_used_transposed[rm_id])
    weekly_standard_deviation_for_rm_id.index = usage.index
    weekly_standard_deviation_for_rm_id['week'] = weekly_standard_deviation_for_rm_id.index.week
    weekly_standard_deviation_for_rm_id['year'] = weekly_standard_deviation_for_rm_id.index.year    
    
    
    max_stock = max_stocks[rm_id]  #2 cycles of Safety Stock (Daily Run Rate X Lead time)*2 
    
    
    merge = pd.merge(weekly_standard_deviation_for_rm_id,df_random,on="week")
    merge["noise"] = merge[rm_id] * merge["random_number"]
    merge.index = usage.index
    
    usage = usage + merge["noise"] 
    usage_day_index = usage.reset_index(drop=True)
        
    regular_lead_time = math.ceil(order_data.loc[order_data['MATERIAL NUMBER'] == rm_id,
                     'TRANSIT TIME'].iloc[0]) # Deviation added to lead time

    daily_inventory = [] # Hold the daily inventory for graphing purpose
    reorder_points = []
    order_decisions = ["nan" for x in range(0,330)]
    
    days_passed_after_order = 0 # Days passed after an order is given
    stockout_days = 0 # Day count when stockout occurs (Stockout: inventory is negative)
    current_stock = starting_inventory
    order_in_progress = False
    
    total_holding_cost = 0
    total_ordering_cost = 0
    total_purchase_cost = 0
    order_amount = 0
    deviated_lead_time = regular_lead_time
    
    for day in range(0,len(usage)):    
        
        # Start of the day Assumption: Ordered raw materials arrive at the start of the day
        reorder_point = reorder_point_list[day] #calculate reorder_point    
        
        if days_passed_after_order == deviated_lead_time: # if leadtime days passed after order
            current_stock += order_amount
            order_amount = 0 # reset order
            days_passed_after_order = 0
            order_in_progress = False #Order is completed
            
        if current_stock < reorder_point and not order_in_progress: # When under reorder point, give order           
           order_in_progress = True # Start ordering process
           order_amount = max((max_stock[day] - current_stock),min_batch_size) # Decide how much to buy 
           total_ordering_cost += order_cost * exchange_rate[day] # Pay for the ship and container
           total_purchase_cost += purchase_cost * order_amount * exchange_rate[day] # Pay for the RMs
           
           # Lead Time Deviation: # With lt_dev_p chance, lead time deviation occurs
           rand_number = random.uniform(0,1)    
           if rand_number < lt_dev_p:
               deviated_lead_time = math.ceil(regular_lead_time * lt_dev_x)
           else:
               deviated_lead_time = regular_lead_time
           order_decisions[day] = 1
           #print("reorder point = " ,str(reorder_point), "ordered",str(order_amount), "MBS",str(min_batch_size))
        
        
        current_stock = current_stock - usage_day_index.loc[day] # Subtract demand from the inv
        
        #End Of The Day
        
        # Calculate holding cost after demand for that day is fulfilled
        total_holding_cost += max(current_stock,0) * holding_cost * exchange_rate[day] 
        
        if current_stock < 0: # when Inventory is negative, stockout occurs
            stockout_days += 1 
        
        if order_in_progress: # If there is an order in progress, a day has passed after you gave order
            days_passed_after_order += 1
            
        daily_inventory.append(current_stock) # Add current inventory to daily_inventory list to graph it later        
        reorder_points.append(reorder_point)
        #print("daily inv == ", str(current_stock))
    
    if plot:
        fig, ax = plt.subplots() 
        ax.plot(usage.index, daily_inventory, color="C0")
        ax.plot(usage.index,reorder_points,color="grey")
        plt.title(rm_id) 
        plt.ylabel("Inventory")
        plt.xlabel("Date")
        plt.legend(labels=["inventory","reorder point"])

        plt.savefig("Results\\"+rm_id+".png",dpi=200)
     
    total_cost_incurred = total_holding_cost + total_ordering_cost + total_purchase_cost    
    print("Results for",rm_id+":","Total stockouts:", stockout_days,"Cost:", str(total_cost_incurred) )
    return total_cost_incurred
    
# for tpl in [(0,0),(-1,1),(-2,2),(0,1),(0,2)]:
#     total_cost = 0

#     for rm in raw_materials_in_analysis[0:5]:
#         x1 = tpl[0]
#         x2 = tpl[1]
#         cost = simulation(rm,plot = True,x1 = x1,x2 = x2)
#         total_cost += cost

    # print("Total Cost under uncertainty under " + str(x1) + "," +  str(x2) + " is: " + str(total_cost))

index = 0
for rm in raw_materials_in_analysis:    
    cost = simulation(rm,plot = True,x1 = 0,x2 = 0,exchange_rate=dollar_tl_stable)

    #print(rm,index,cost)
    index +=1




