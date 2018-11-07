#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 07:48:25 2018

@author: ko

To do:
    
    - Quantity up to four digits
    - Betere Layout
    - Anticiperen future test cases
    
"""


import pandas as pd

def convert_to_df(root, eco, exchange_lst, name_tag):
    
    """
    Creating a dataFrame with relevant variables

    """
    
    # Create DataFrame to store and sort exchanges.
    col_names =  ["Name","Unit Name",'Exchange Type', 'Input', 'Amount', "Production Volume Amount"]
    df  = pd.DataFrame(columns = col_names)
    for exchange in exchange_lst:
        ## Reading data into a pandas Dataframe.
        for elem in root.findall("%s/Eco:flowData/Eco:%s" % (name_tag,exchange), eco):
            # Name.
            elem_name = elem.find("./Eco:name",eco)
            name = elem_name.text
                
            # Unit name.
            elem_unit_name = elem.find("./Eco:unitName",eco)
            unit_name = elem_unit_name.text
            
            # Amount.
            # Converting quantity to four digits.
            amount = float(elem.get("amount"))
                
            # Production Volume amount.
            pv_amount = float("nan")
        
            # Output group consists of references products and by products.
            if (elem.find(".//Eco:outputGroup",eco) != None):
                
                if exchange == "intermediateExchange":
                    pv_amount = float(elem.get("productionVolumeAmount"))
                input_group = False
        
            elif elem.find(".//Eco:inputGroup",eco) != None:
                input_group = True
                
            else:
                 raise ValueError("No input and output child")
                
            # Appending row.
            df_2 = pd.DataFrame([[name,unit_name, exchange, input_group, amount, pv_amount]], columns= col_names)
            df = df.append(df_2,ignore_index=True)      
    return df

def subset_df(df,constraint = 5):
    
    """
        Subsetting dataframe to appropriate length exchange group
    """
    
    if len(df) > constraint:
        return df[:constraint]
    else:
        return df
    
def retrieve_variables(df,eco,root):
    
    """
    Sort and return neccesary data for barplot

    """
    # Removing duplicates name and adding their amount.
    df["Amount"] = df.groupby(["Name","Input", "Exchange Type"]).Amount.transform('sum')
    df = df.drop_duplicates(["Name","Input", "Exchange Type"])
    
    # Remove Exchanges with amount = 0.
    df = df[df["Amount"] != 0]
    
    # Retrieving activityName.
    activity_name_elem = root.find(".//Eco:activityName",eco)
    activity_name = activity_name_elem.text
    
    # Retrieving geography short-name field content.
    geo_elem =  root.find(".//Eco:shortname",eco)
    geo_short_name = geo_elem.text
    
    ## Intermediary exchange ###
    ## Retrieve Reference product.
    ref_product = df[(df["Amount"] == 1)]
    
    ## Retrieve Byproducts.
    df_intermediary_output = df[(df["Input"] == False) & (df["Amount"] != 1) & (df["Exchange Type"] == "intermediateExchange")].sort_values(by=['Production Volume Amount'], ascending=False)
    by_product = subset_df(df_intermediary_output,4)
    
    ## Retrieve inputs technosphere.
    df_intermediary_input = df[(df["Input"] == True) & (df["Exchange Type"] == "intermediateExchange")].sort_values(by=['Amount'], ascending=False)
    input_tech = subset_df(df_intermediary_input)
    
    ### Elementary Exchange ###
    ## Retrieve elemental output.
    df_elementary_output = df[(df["Input"] == False) & (df["Exchange Type"] == "elementaryExchange")].sort_values(by=['Amount'], ascending=False)
    output_elem = subset_df(df_elementary_output)
        
    ## Retrieve Elemental input.
    df_elementary_input = df[(df["Input"] == True) & (df["Exchange Type"] == "elementaryExchange")].sort_values(by=['Amount'], ascending=False)
    input_elem = subset_df(df_elementary_input)
    
    
    return activity_name, geo_short_name, ref_product, by_product, input_tech, input_elem, output_elem




