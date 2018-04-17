import pandas as pd
import os

path = r"C:\Users\rhughes\Documents\Florida\Florida\counties"
counties = pd.read_excel(path+"\CountyByPlatform.xlsx")


def countyslice(platform):
    return counties[counties['Platform'] == platform]['County'].values


countiesByPlatform = {
    'RealAuction': countyslice('RealAuction'),
    'GrantStreet': countyslice('GrantStreet'),
    'DT': countyslice('DT'),
    'WFBS': countyslice('WFBS')
}

