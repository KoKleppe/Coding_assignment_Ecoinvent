#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  2 10:00:38 2018

@author: ko
"""

import os 
from xml.etree import ElementTree as ET
from parse_xml import convert_to_df,retrieve_variables
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def split_string(string,size_constraint):
    
    """
        Splitting string to make sure they fit the text box
    
    """
    
    if (len(string) > size_constraint) & (string.find(",") != -1) :
        string = string[:string.find(",")].capitalize() + "," + "\n" + string[string.find(",")+1:]
    elif (len(string) > size_constraint) & (string.find(",") == -1):
        string = string[:round(len(string)/2)] + "-" + "\n" + string[round(len(string)/2):]
        
    return string


def create_text_string(df,string_list):
    
    """
        Creating text string per exchange group
    """
    
    for count in range(len((df.index))):
        
        # Restrict amount to four digits.
        amount = df["Amount"].iloc[count]
        if (amount > 1000) | (amount < 0.01):
            amount = "{:.1E}".format(amount)
        elif (amount < 1000) & (amount > 100):
            amount = str(round(amount,1))
        elif (amount < 100) & (amount > 10):
            amount = str(round(amount,2))
        elif (amount < 1) | (amount < 10):
            amount = str(round(amount,3))
        else:
            raise ValueError("Amount unaccounted for %d" % amount)
        
        text_string = split_string("* " + amount + " " + df["Unit Name"].iloc[count] + " " + df["Name"].iloc[count],40)
        string_list.append(text_string)
            
    return "\n".join(string_list)

def plot_diagram(plt,patches, activity_name, geo_short_name, ref_product, by_product, input_tech, input_elem, output_elem):
    
    """
    Plotting diagram
    
    """
    
    # Parameters patch and figure.
    a=[0,5]
    c=[20,5]
    d=[7,12.5]
    width = c[0] - a[0]
    height = d[1] - a[1]
    x_lim = (0,100)
    y_lim = (0,50)
    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='equal')
    
    # Arrows.
    ax.annotate("", xy=(35,27.5), xytext=(40,27.5), arrowprops=dict(arrowstyle="<-"))
    ax.annotate("", xy=(60,27.5), xytext=(65,27.5), arrowprops=dict(arrowstyle="<-"))
    ax.annotate("", xy=(50,17.5), xytext=(50,22.5), arrowprops=dict(arrowstyle="<-"))
    ax.annotate("", xy=(50,30), xytext=(50,35), arrowprops=dict(arrowstyle="<-"))
    
    # Creating text box.
    props = dict(boxstyle='round', facecolor='grey', alpha=0.5)
    
    # Activity name & geo_short name.
    
    activity_geo_text = split_string(activity_name,25) + "\n" + "                           " + geo_short_name 
    ax.text(40.5,25.5, activity_geo_text, fontsize=2.5)
    
    ## Intermediary exchange.
    # Reference product.
    
    ref_byproduct_str = ["Reference product and byproducts:"]
    ref_byproduct_str.append(split_string(str(ref_product["Amount"].iloc[0]) + " " + ref_product["Unit Name"].iloc[0] + " " + ref_product["Name"].iloc[0],40))
    ref_byproduct_str = create_text_string(by_product,ref_byproduct_str)
    ax.text(0.75, 0.6, ref_byproduct_str, transform=ax.transAxes, fontsize=2.5,
        verticalalignment='top', bbox=props)

    # Input 
    input_int_str = ["Input techosphere:"]
    input_int_str = create_text_string(input_tech,input_int_str)
    ax.text(0.15, 0.6, input_int_str, transform=ax.transAxes, fontsize=2.5,
    verticalalignment='top', bbox=props)
    
    
    ## Elementary exchange.
    # Output.
    output_elem_str = ["Emissions to environment:"]
    output_elem_str = create_text_string(output_elem,output_elem_str)
    ax.text(0.4, 0.95, output_elem_str, transform=ax.transAxes, fontsize=2.5,
            verticalalignment='top', bbox=props)
    
    # Input.
    intput_elem_str = ["Resource consumptions from environment:"]
    intput_elem_str = create_text_string(input_elem,intput_elem_str)
    ax.text(0.4, 0.3, intput_elem_str, transform=ax.transAxes, fontsize=2.5,
        verticalalignment='top', bbox=props)
    
    # Adding patch
    ax.add_patch(patches.Rectangle((40, 22.5), width, height))
    plt.ylim(y_lim)
    plt.xlim(x_lim)
    
    # Turn axes off
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    return plt

# Dictionary to deal with the pre-fix.
eco = {"Eco":"http://www.EcoInvent.org/EcoSpold02"}

# List of exchanges.
exchange_lst = ["intermediateExchange","elementaryExchange"]

# Specify directory
directory = os.path.abspath(os.path.join("data"))

## Looping through directories. 
for file_name in os.listdir(directory):
    
    """
    Reading in files
    
    """
    
    tree = ET.parse(os.path.abspath(os.path.join("data",file_name)))
    root = tree.getroot()
    
    print(file_name)
    # Accounting for different name_tag activityDataset.
    for elem in root.getchildren():
        name_tag = elem.tag
    
    # Retrieving df.
    df = convert_to_df(root,eco,exchange_lst,name_tag)

    # Retrieving variables.
    activity_name, geo_short_name, ref_product, by_product, input_tech, input_elem, output_elem = retrieve_variables(df,eco,root)
    
    # Creating plot object with variables.
    plot = plot_diagram(plt,patches,activity_name, geo_short_name, ref_product, by_product, input_tech, input_elem, output_elem)
    
    plot.savefig("%s" % (file_name),bbox_inches="tight", format='eps', dpi=1000)
    plot.show()
    
    


