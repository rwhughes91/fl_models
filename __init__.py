import pandas as pd
import os
from datetime import datetime

from Florida.counties.platform_gen import countiesByPlatform

def column_creator(yearsback=0):
    year = datetime.now().year - yearsback
    countyownedlabels = [f"Cnty. Owned {x}" for x in range(year-7, year)]
    countyownedlabels.reverse()

    columns = {
        'names': ['Adv No.','County','Account No.','Amount','Tax_Year','TSR_Check','Lumentum Check','Amount Check',
                'Location_House_Number','Location_City','Location_State','Location_Zip_4','Location_Full_Street_Address',
                'Location_City_State_Zip','Longitude','Latitude','Current_Owner','County_Land_Use','County_Land_Use_Desc',
                'Standardized_Land_Use','Standardized_Land_Use_Desc','Assessment_Year','Total_Assessed_Value','Market_Value_Year',
                'Total_Market_Value','Tax_Amount','Annual/Current Tax', countyownedlabels[0], countyownedlabels[1], countyownedlabels[2],
                  countyownedlabels[3], countyownedlabels[4], countyownedlabels[5], countyownedlabels[6],'Cert_Holder_Type1','Cert_Holder_Type2',
                'Cert_Holder_Type3','Cert_Holder_Type4','Cert_Holder_Type5','Cert_Holder_Type6','Cert_Holder_Type7',
                'Adv County Cert','TSR County Cert','Prior Cnty-Owned (past 7 years)','Latest_Arms_Length_Sale_Date',
                'Latest_Arms_Length_Sale_Price','Loan1_Amount','Loan1_Type','environmentalsubjectsitefoundcount','environmentalsitefoundcount',
                'environmentalscore','FLD_CLASS','Prior Liens Outstanding','HX','Tax Deed History','Environment File TSR For Test','Environment File Lumentum',
                'Environment File Lumentum For Test','CDD Bond', 'Address', 'City', 'State', 'Zip', 'Full Address', 'Loan?', 'Lien < $150', 'Tax Deed History_2',
                'Bad Address',"Zillow Test", 'EPA', "CDD", 'Flood', 'Prior Cnty-Owned (past 7 years)', 'Multiple Liens for Sale', "Priors", "Prior Screen",
                "AV", "Equalization Ratio", "Equalized AV", "Zestimate", "Latest ALS Date", "Latest ALS Price", "Sale Year (if > $1k)", "Market Index", "Value to use",
                "Sales Data within 7 years", "Use Code", "Vacant, No Sales Data", "Hx", "Haircut", "Adj Value for Calc", "Foreclosure (All-in $)", "Solv Prem",
                "LTV", "Bad Data/Other", "Google Test", "Google Assessment", "Available", "Data Change", "Bid?", "Lien Ref", "Face", "Large Liens?", 'GovernmentLien','LisPendens'],

        'countiesByPlatform': countiesByPlatform,

        'tsr_cols': ['List_Item_Ref','Amount','Location_House_Number','Location_City','Location_State','Location_Zip_4','Location_Full_Street_Address',
            'Location_City_State_Zip','Longitude','Latitude','Current_Owner','Standardized_Land_Use','Standardized_Land_Use_Desc','Market_Value_Year',
            'Total_Market_Value','Tax_Amount','CERT_HOLDER_TYPE1','CERT_HOLDER_TYPE2','CERT_HOLDER_TYPE3','CERT_HOLDER_TYPE4','CERT_HOLDER_TYPE5',
            'CERT_HOLDER_TYPE6','CERT_HOLDER_TYPE7','Latest_Arms_Length_Sale_Date','Latest_Arms_Length_Sale_Price','Loan1_Amount','Loan1_Type',
            'environmentalsubjectsitefoundcount','environmentalsitefoundcount','environmentalscore','FLD_CLASS','TaxDeedHistory','List_Note_2'],

        'lumentum_cols': ['AdvNumber','FaceValue','Environmental','CDDName','BackTaxOpenCount','GovtLien','LisPendens','CertificateHolderType_1',
               'CertificateHolderType_2','CertificateHolderType_3','CertificateHolderType_4','CertificateHolderType_5',
               'CertificateHolderType_6','CertificateHolderType_7','ZoningUseCode','LandDescription']
            }

    return columns


if __name__ == "__main__":
    f = os.path.abspath(os.path.dirname(__file__))
