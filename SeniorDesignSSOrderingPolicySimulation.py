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

class Simulation:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    input_directory = dir_path + "\\Data Prep Output" # Data will be printed out here
    
    def __init__(self,rm_id,service_level):
        self.rm_id = rm_id
        self.service_level = service_level
        self.dollar_tl_stable = [15 for x in range(0,330) ]# write a funtion
    
    def data_prep(self): 
        dir_path = os.path.dirname(os.path.realpath(__file__))
        
        self.starting_inventory_data = pd.read_excel(io=self.input_directory+"\\weekly_safety_stocks_"+str(str(self.service_level))+".xlsx",sheet_name="starting_inventory") # Starting inventories for each RM
        daily_demand = pd.read_excel(io=self.input_directory+"\\weekly_safety_stocks_"+str(str(self.service_level))+".xlsx",sheet_name="Daily_Demand") # Usage of each RM i in day j
        self.order_data = pd.read_excel(self.input_directory+"\\weekly_safety_stocks_"+str(str(self.service_level))+".xlsx",sheet_name = "order_data") # Lead Times for each RM
        #starting_inventory_data = pd.read_excel(io="data\\MaterialType.xlsx",sheet_name="starting_inventory") # Starting inventories for each RM
        reorder_point_data = pd.read_excel(self.input_directory+"\\weekly_safety_stocks_"+str(self.service_level)+".xlsx",sheet_name = "Reorder_Points")
        self.purchase_and_holding_cost_data = pd.read_excel(self.input_directory+"\\weekly_safety_stocks_"+str(self.service_level)+".xlsx",sheet_name = "purchase_and_holding_costs")
        self.max_stocks = pd.read_excel(self.input_directory+"\\weekly_safety_stocks_"+str(self.service_level)+".xlsx",sheet_name = "max_stocks")
        
        
        raw_materials_in_analysis = list(self.order_data["MATERIAL NUMBER"])
        
        # Daily Demand Data Manipulation
        daily_demand = daily_demand.rename({'Unnamed: 0':'MATERIAL NUMBER'},axis =1)
        self.demand_transposed = daily_demand.T
        new_header = self.demand_transposed.iloc[0] #grab the first row for the header
        self.demand_transposed = self.demand_transposed[1:] #take the data less the header row
        self.demand_transposed.columns = new_header #se
        
        # Daily Demand Data Manipulation
        reorder = reorder_point_data.rename({'Unnamed: 0':'MATERIAL NUMBER'},axis =1)
        self.reorder_transposed = reorder.T
        new_header = self.reorder_transposed.iloc[0] #grab the first row for the header
        self.reorder_transposed = self.reorder_transposed[1:] #take the data less the header row
        self.reorder_transposed.columns = new_header #se
        self.reorder_transposed.columns  = [x.split("_")[0] for x in self.reorder_transposed.columns ]
        
        # Weekly standard deviation data preparation
        weekly_standard_deviation = pd.read_excel("Output Data\\weekly_safety_stocks_"+str(self.service_level)+".xlsx",sheet_name = "weekly_startdard_deviation")
        weekly_standard_deviation = weekly_standard_deviation.rename({"Unnamed: 0":"MATERIAL NUMBER"},axis=1)
        weekly_standard_deviation_used = weekly_standard_deviation[weekly_standard_deviation["MATERIAL NUMBER"].isin(raw_materials_in_analysis)] # take rm's in analysis
        weekly_standard_deviation_used.set_index("MATERIAL NUMBER",inplace=True)
        self.weekly_standard_deviation_used_transposed = weekly_standard_deviation_used.transpose()
        
#%% Simulation
    def simulation(self,rm_id,plot = False,x1 = 0, x2 = 0,
                   lead_time_deviation_present = False, expected_exchange_rate = 15,
                   policy="SS",max_stock_multiplier = 2,stockout_occurrence_cost=500000):
        """
        raw_material_id : String, name of the column
        
        x1: float, lower bound for demand deviation
        x2: float, upper bound for demand deviation
        lead_time_deviation_present: Boolean, True if lead time deviation can occur, False otherwise
        exchange_rate: List, Exchange rate for each day in simulation
        Policy: String, default = "SS". Select ordering policy, "QR" or "SS"
        """
        
        starting_inventory = self.starting_inventory_data.loc[self.starting_inventory_data['MATERIAL NUMBER'] == rm_id, 'Starting Inventory'].iloc[0]
        min_batch_size = self.order_data.loc[self.order_data['MATERIAL NUMBER'] == rm_id,"MIN BATCH SIZE"].iloc[0]
        purchase_cost =  self.purchase_and_holding_cost_data.loc[self.purchase_and_holding_cost_data["MALZEME"] == rm_id,"Purchase Cost"].iloc[0]
        holding_cost =  self.purchase_and_holding_cost_data.loc[self.purchase_and_holding_cost_data["MALZEME"] == rm_id,"Holding Cost"].iloc[0]
        order_cost = self.order_data.loc[self.order_data['MATERIAL NUMBER'] == rm_id,"Ordering Cost"].iloc[0]
        reorder_point_list = self.reorder_transposed[rm_id]
        
        usage = self.demand_transposed[rm_id]
        usage.index = pd.to_datetime(usage.index,errors='ignore')
        #Purchase amount and decision
       
        # Manipulate demand
        demand_df = pd.DataFrame(usage) 
        #random.seed(42)
        random_numbers = [(x,random.uniform(x1,x2)) for x in range(1,53)]
        df_random = pd.DataFrame(random_numbers)
        df_random.columns = ["week","random_number"]
        
        weekly_standard_deviation_for_rm_id = pd.DataFrame(self.weekly_standard_deviation_used_transposed[rm_id])
        weekly_standard_deviation_for_rm_id.index = usage.index
        weekly_standard_deviation_for_rm_id['week'] = weekly_standard_deviation_for_rm_id.index.week
        weekly_standard_deviation_for_rm_id['year'] = weekly_standard_deviation_for_rm_id.index.year    
        
        #max_stock = self.max_stocks[rm_id]  #2 cycles of Safety Stock (Daily Run Rate X Lead time)*2 
        
        merge = pd.merge(weekly_standard_deviation_for_rm_id,df_random,on="week")
        merge["noise"] = merge[rm_id] * merge["random_number"]
        merge.index = usage.index
        
        usage = usage + merge["noise"] 
        usage_day_index = usage.reset_index(drop=True)
            
        regular_lead_time = math.ceil(self.order_data.loc[self.order_data['MATERIAL NUMBER'] == rm_id,
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
        stockout_cost = 0
        deviated_lead_time = regular_lead_time
        exchange_rate = self.USD_TL_Expectations(todays_exchange_rate=15,expected_exchange_rate = expected_exchange_rate)
        stockout_amount = 0
        
        for day in range(0,len(usage)):    
            
            reorder_point = reorder_point_list[day] #calculate reorder_point    
            current_stock = current_stock - usage_day_index.loc[day] # Subtract demand from the inv
            
            if current_stock < reorder_point and not order_in_progress: # When under reorder point, give order           
               
                order_in_progress = True # Start ordering process
                if policy == "QR":
                    order_amount = min_batch_size # Decide how much to buy 
                elif policy == "SS":
                    max_stock = reorder_point * max_stock_multiplier
                    order_amount = max((max_stock - current_stock),min_batch_size) # Decide how much to buy
               
                total_ordering_cost += order_cost * exchange_rate[day] # Pay for the ship and container
                total_purchase_cost += purchase_cost * order_amount * exchange_rate[day] # Pay for the RMs
            
                #Lead Time Deviation:
                rand_number = random.uniform(0,1)
                if lead_time_deviation_present:
                    if rand_number < 0.50: # No deviation occurs
                        deviated_lead_time = regular_lead_time
                    elif 0.50 < rand_number < 0.70:  # With 20% chance, Lead time deviates 5%
                        deviated_lead_time = math.ceil(regular_lead_time * 1.05)
                    elif 0.70 < rand_number < 0.85:  # With 10% chance, Lead time deviates 10%
                        deviated_lead_time = math.ceil(regular_lead_time * 1.10)
                    elif 0.85 < rand_number < 0.95:  # With 5% chance, Lead time deviates 20%
                        deviated_lead_time = math.ceil(regular_lead_time * 1.15)
                    else: # With 5% chance, Lead time deviates 20%
                        deviated_lead_time = math.ceil(regular_lead_time * 1.20)
                else:
                    deviated_lead_time = regular_lead_time
                order_decisions[day] = 1
                
            if days_passed_after_order == deviated_lead_time: # if leadtime days passed after order
                current_stock += order_amount
                order_amount = 0 # reset order
                days_passed_after_order = 0
                order_in_progress = False #Order is completed
            # Calculate holding cost after demand for that day is fulfilled
            total_holding_cost += max(current_stock,0) * holding_cost * exchange_rate[day] 
            
            if current_stock < 0: # when Inventory is negative, stockout occurs
                stockout_days += 1 
                stockout_cost += stockout_occurrence_cost #TL
                stockout_amount += abs(current_stock)
                
            if order_in_progress: # If there is an order in progress, a day has passed after you gave order
                days_passed_after_order += 1
                
            daily_inventory.append(current_stock) # Add current inventory to daily_inventory list to graph it later        
            reorder_points.append(reorder_point)
        
        if plot:
            fig, ax = plt.subplots() 
            ax.plot(usage.index, daily_inventory, color="C0")
            ax.plot(usage.index,reorder_points,color="grey")
            plt.title(rm_id) 
            plt.ylabel("Inventory")
            plt.xlabel("Date")
            plt.legend(labels=["inventory","reorder point"])
    
            plt.savefig("Results\\"+rm_id+".png",dpi=200)
        
        type_2_service_level = 1 - (stockout_amount / sum(list(usage)))    
        total_cost_incurred = total_holding_cost + total_ordering_cost + total_purchase_cost + stockout_cost    
        # print("Results for",rm_id,"at",str(self.service_level),"service level With " + policy +" policy:" ,"Total stockouts:", stockout_days,"Cost:", str(total_cost_incurred),"Type 2 Service Level: " + str(type_2_service_level))
        return [total_holding_cost,total_ordering_cost,total_purchase_cost,stockout_cost,total_cost_incurred,stockout_days,type_2_service_level]
    
    def get_all_RM_ID(self):
        rm_list = list(self.weekly_standard_deviation_used_transposed.columns)
        return rm_list
    
    def USD_TL_Expectations(self,todays_exchange_rate,expected_exchange_rate,days = 330):
        slope = (expected_exchange_rate - todays_exchange_rate)/days 
        daily_exchange_rates = [x*slope + todays_exchange_rate for x in range(0,days)]
        return daily_exchange_rates
        
        
        