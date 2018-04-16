import pandas as pd
import os
from datetime import datetime

from .counties.setup import countiesByPlatform
year = datetime.now().year

countyownedlabels = [f"Cnty. Owned {x}" for x in range(year-7, year)]
countyownedlabels.reverse()

columns = {
    'names': ['Adv No.','County','Account No.','Amount','Tax_Year','TSR_Check','Lumentum Check','Amount Check',
            'Location_House_Number','Location_City','Location_State','Location_Zip_4','Location_Full_Street_Address',
            'Location_City_State_Zip','Longitude','Latitude','Current_Owner','County_Land_Use','County_Land_Use_Desc',
            'Standardized_Land_Use','Standardized_Land_Use_Desc','Assessment_Year','Total_Assessed_Value','Market_Value_Year',
            'Total_Market_Value','Tax_Amount','Annual/Current Tax',countyownedlabels[0],countyownedlabels[1],countyownedlabels[2],
              countyownedlabels[3],countyownedlabels[4],countyownedlabels[5], countyownedlabels[6],'Cert_Holder_Type1','Cert_Holder_Type2',
            'Cert_Holder_Type3','Cert_Holder_Type4','Cert_Holder_Type5','Cert_Holder_Type6','Cert_Holder_Type7',
            'Adv County Cert','TSR County Cert','Prior Cnty-Owned (past 7 years)','Latest_Arms_Length_Sale_Date',
            'Latest_Arms_Length_Sale_Price','Loan1_Amount','Loan1_Type','environmentalsubjectsitefoundcount','environmentalsitefoundcount',
            'environmentalscore','FLD_CLASS','Prior Liens Outstanding','HX','Tax Deed History','Environment File TSR For Test','Environment File Lumentum',
            'Environment File Lumentum For Test','CDD Bond','GovernmentLien','LisPendens'],

    'countiesByPlatform': countiesByPlatform
        }
