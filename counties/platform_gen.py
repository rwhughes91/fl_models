import pandas as pd
import os

path = os.path.abspath(os.path.dirname(__file__))
counties = pd.read_excel(path+"\CountyByPlatform.xlsx")


def countyslice(platform):
    return counties[counties['Platform'] == platform]['County'].values


countiesByPlatform = {
    'RealAuction': countyslice('RealAuction'),
    'GrantStreet': countyslice('GrantStreet'),
    'DT': countyslice('DT'),
    'WFBS': countyslice('WFBS')
}

