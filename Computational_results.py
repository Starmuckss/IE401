# -*- coding: utf-8 -*-
"""
Created on Fri May 20 15:16:13 2022

Purpose: Create an excel file showing the best result for each Raw Material

"""
import pandas as pd
from SeniorDesignSSOrderingPolicySimulation import Simulation
import random
import numpy as np
import os 
import matplotlib.pyplot as plt
dir_path = os.path.dirname(os.path.realpath(__file__))
input_directory = dir_path + "\\Experiment Results" # Data will be printed out here


no_uncertainty_results = pd.read_excel(input_directory+"\\Service Level Changes.xlsx")
uncertainty_results = pd.read_excel(input_directory+"\\Experiment_results.xlsx")

uncertainty_info_columns = ["Demand Deviation Lower Bound","Demand Deviation Upper Bound","Exchange Rate"]

no_uncertainty_results.drop(labels= ["Unnamed: 0","Lead Time Deviation Occurs","index"]+uncertainty_info_columns,axis =1 ,inplace = True)
uncertainty_results.drop(labels= ["Unnamed: 0"]+uncertainty_info_columns,axis =1 ,inplace = True)

merged_dataframe = pd.merge(no_uncertainty_results,uncertainty_results,on=["RM ID","Service Level","Policy"])

merged_dataframe = merged_dataframe[["RM ID","Service Level","Policy","Total Cost_x", "Days Stockout Occurs_x","Type 2 Service Level_x","Total Cost_y", "Days Stockout Occurs_y","Type 2 Service Level_y"]]

merged_dataframe.columns = [x.split("_")[0]+" No Uncertainty" if "_x" in x else x for x in merged_dataframe.columns]
merged_dataframe.columns = [x.split("_")[0]+" With Uncertainty" if "_y" in x else x for x in merged_dataframe.columns]

merged_dataframe.to_excel(input_directory+"//Final_decisions_for_each_rm.xlsx")


