# -*- coding: utf-8 -*-
"""
Created on Sat Apr 16 09:55:31 2022

@author: HP
"""
for i in RawMaterials:
    Demand_i = DailyDemands[i] 
    StartingInventory_i = StartingInventories[i]
    OrderAmount_i = OrderAmounts[i] # Order decisions, output of MILP
    LeadTime_i = LeadTimes[i]
    holdingCost_i = holdingCosts[i]
    stockoutCost_i = stockoutCosts[i]
    WeeklyStandartDeviation_i = WeeklyStandartDeviations[i]
    
    # Add variety to demand 
    # Create a random number list RandomNums for each week in demand data
    for week in Demand_i:
        Noise[week] = RandomNums[week] * WeeklyStandartDeviation_i[week]
        Demand_i[week] += Noise[week] 
    
    total_cost = 0,stockouts = 0, CurrentStock = StartingInventory_i
    
    for day in [1,2,3..330]:
        CurrentStock = CurrentStock + OrderAmount_i[day-LeadTime_i] - Demand_i[day]    
        total_cost_incurred += max(CurrentStock,0) * holdingCost
        
        if CurrentStock < 0:
            stockouts += 1        
            total_cost_incurred += stockoutCost