
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[44]:


import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[45]:


# This dictionary maps state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[46]:


def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. '''
    
    # import list
    ut_df = pd.read_table('university_towns.txt', header = None, names = ['RegionName'])

    # Assign States
    ut_df['State'] = None
    for index, row in ut_df.iterrows():
        if row['RegionName'][-6:] == '[edit]':
            state = row[0][:-6]
            row['State'] = state
        else: 
            row['State'] = state

    # Clean Data
    for index, row in ut_df.iterrows():
        if row['RegionName'][-6:] == '[edit]':
            ut_df.drop(index,inplace = True)

    ut_df['RegionName'] = ut_df['RegionName'].str.split('(').str[0].str.strip()    
    ut_df = ut_df[['State', 'RegionName']]

    return ut_df


# In[47]:


def get_list_of_GDP_recession():
    '''Returns a DataFrame of GDP by years and quarters from gdplev.xls. Includes columns detailing
    whether the GDP is deline, in recession, a start quarter of recession, or an end quarter of recession '''
        
    #import and clean
    gdp_df = pd.read_excel('gdplev.xls', skiprows = 7)
    gdp_df = gdp_df.iloc[:, 4:-1]
    gdp_df.rename(columns = {'Unnamed: 4':'Quarter', 'Unnamed: 5':'GDP in billions of current dollars', 'Unnamed: 6': 'GDP'}, inplace = True)
    gdp_df.drop('GDP in billions of current dollars', axis = 1, inplace = True)

    #get diffs column
    gdp_df['diffs'] = np.where(gdp_df['GDP'].diff() > 0, 'increase', 'decline')

    #set In Recession column
    gdp_df['In Recession'] = False
    for index, row in gdp_df.iterrows():
        
        #set variables
        if index+1 in gdp_df.index:
            nex = gdp_df.loc[index+1]
        else: nex = None
        cur = gdp_df.loc[index]
        if index-1 in gdp_df.index:
            prv = gdp_df.loc[index-1]
        else: prv = None

        # assign True if in recession (begins with two periods of decline and ends after two periods of growth)
        if (
            index+1 in gdp_df.index
                #next and current are decline
            and ((nex['diffs'] == 'decline') and (cur['diffs'] == 'decline'))
                #previous is in recession and current or next is decline
            or ((prv['In Recession'] == True) and ((cur['diffs'] == 'decline') or (nex['diffs'] == 'decline') or (prv['diffs'] == 'decline') or (gdp_df.loc[index-2]['diffs'] == 'decline'))) 
           ):
            gdp_df.loc[index,'In Recession'] = True
    
    #set Recession Start column
    gdp_df['Recession Start'] = False
    for index, row in gdp_df.iterrows():
        if(
            ((index-1 not in gdp_df.index) or (gdp_df.loc[index-1,'In Recession'] == False))
            and (gdp_df.loc[index,'In Recession'] == True)
        ):
            gdp_df.loc[index, 'Recession Start'] = True

    #set Recession End column
    gdp_df['Recession End'] = False
    for index, row in gdp_df.iterrows():
        if(
            ((index+1 not in gdp_df.index) or (gdp_df.loc[index+1,'In Recession'] == False))
            and (gdp_df.loc[index,'In Recession'] == True)
        ):
            gdp_df.loc[index, 'Recession End'] = True
    
    return gdp_df


# In[48]:


def get_recession_start(start = '2001q1'):
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    
    gdp_df = get_list_of_GDP_recession()
    
    #get gdp_df after start date
    startrow = (gdp_df.loc[gdp_df['Quarter'] == start].index[0])
    gdp_df = gdp_df.iloc[startrow:]
    
    #return next recession start
    for index, row in gdp_df.iterrows():
        if row['Recession Start'] == True:
            return row['Quarter']
        


# In[49]:


def get_recession_end(start = '2001q1'):
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    
    recession_start = get_recession_start(start)
    gdp_df = get_list_of_GDP_recession()
    
    #get gdp_df after start date
    startrow = (gdp_df.loc[gdp_df['Quarter'] == recession_start].index[0])
    gdp_df = gdp_df.iloc[startrow:]
    
    #return end of recession
    for index, row in gdp_df.iterrows():
        if row['Recession End'] == True:
            return row['Quarter']


# In[50]:


def get_recession_bottom(start = '2001q1'):
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''

    gdp_df = get_list_of_GDP_recession()
    
    #get gdp_df from next recession start date to next recession end date
    startrow = (gdp_df.loc[gdp_df['Quarter'] == get_recession_start(start)].index[0])
    endrow = (gdp_df.loc[gdp_df['Quarter'] == get_recession_end(start)].index[0])
    gdp_df = gdp_df.iloc[startrow:endrow+1]
    
    #return recession bottom
    min = gdp_df['GDP'].min()
    return gdp_df.loc[gdp_df.loc[gdp_df['GDP'] == min].index[0]]['Quarter']


# In[51]:


def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters from 1996q1 through 2016q3, and returns it as mean 
    values in a dataframe.
    '''    
    # import
    hd_df = pd.read_csv('City_Zhvi_AllHomes.csv')
    
    # clean and format data
    hd_df.replace({"State": states}, inplace = True)
    hd_df.set_index(['State', 'RegionName'],inplace = True)
    hd_df.sort_index(inplace = True)
    
    hd_df = hd_df.iloc[:,4:]
    
    hd_df.columns = pd.to_datetime(hd_df.columns)
    hd_df = hd_df.resample('Q', axis=1).mean()
    hd_df = hd_df.rename(columns=lambda col: '{}q{}'.format(col.year, col.quarter))
    
    return hd_df


# In[53]:


def run_ttest(start = '2001q1'):
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    can be rejected or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    
    #creates new data showing the decline or growth of housing prices between the recession start and the recession bottom.
    ut_df = get_list_of_university_towns()
    hd_df = convert_housing_data_to_quarters()

    q_before_recession_start = pd.to_datetime(get_recession_start(start)) - pd.offsets.DateOffset(months=3)
    q_before_recession_start = '{}q{}'.format(q_before_recession_start.year, q_before_recession_start.quarter)

    bottom = get_recession_bottom(start)

    
    #new df includes hd_df indexes and quarters of start and bottom, a price ratio column, 
    #and a boolean column of whether it is a university town
    
    df = hd_df[[q_before_recession_start, bottom]]

    df['Price Ratio'] = df[q_before_recession_start] / df[bottom]
    
        # merge university town data to add boolean column 'Is UT'
    ut_df['Is UT'] = True
    ut_df.set_index('State', inplace = True)

    ut_df.reset_index(inplace = True)
    ut_df.set_index(['State','RegionName'],inplace = True)

    df = df.merge(ut_df, how = 'left', left_index = True, right_index = True)
    df['Is UT'].fillna(False, inplace = True)
    

    #run a ttest comparing the university town values to the non-university towns values
    ut = df[df['Is UT'] == True]
    notut = df[df['Is UT'] == False]

    from scipy import stats
    ttest = stats.ttest_ind(ut['Price Ratio'].dropna(), notut['Price Ratio'].dropna())
    ttest

    
    #return a tuple stating whether the alternative hypothesis (that the two groups are the same) is true or not, 
    #the p-value of the confidence, and which subset maintains better price ratio in recession.

    if ut['Price Ratio'].mean() < notut['Price Ratio'].mean():
        better = 'university town'
    elif ut['Price Ratio'].mean() > notut['Price Ratio'].mean():
        better = 'not university town'
    else:
        better = 'neither'

    return (ttest[1] <= .05, ttest[1], better)


# In[54]:


run_ttest()


# In[ ]:




