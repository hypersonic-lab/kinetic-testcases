#!/opt/homebrew/bin/python3
'''
    Date:   09/26/2022
    Author: Martin E. Liza
    File:   dataCollecter.py
    Def:    Generates a csv file with aerodynamics coefficients..

    Author		    Date		Revision
    ----------------------------------------------------
    Martin E. Liza	09/26/2022	Initial version.
'''
import pandas as pd 
import os 

# User's Input
cases_path = '<abs_to_cases>'
files_in   = os.listdir(cases_path)  
files_in.sort() 
dict_out  = { }

for count, val in enumerate(files_in):
    # Load csv
    try:
        df = pd.read_csv(os.path.join(cases_path, val, 'history.csv'))
    except:
        print(val) 
    # Create empty lists on the first count
    if count == 0:
        dict_out['mach'] = [ ]
        dict_out['AoA']  = [ ]
        headers = list(df.columns.values) 

    # Append Mach and AoA
    dict_out['mach'].append(int(val[1]))
    dict_out['AoA'].append(int(val.split('_')[1].split('o')[1].split('A')[1]))

    try:
        for key in headers:
            if count == 0:
                dict_out[key.replace('"','').strip()] = [ ]
            dict_out[key.replace('"','').strip()].append(df.iloc[-1][key]) 
    except:
        print(val) 
    try:
        del df 
    except:
        print(val) 

df_out = pd.DataFrame(dict_out)
df_out.to_csv('data_out.csv', index=False)

