import pandas as pd
from .adv_methods import homesteadmodifier


def tsr_generator(tsr_model, fl_model, tsr_cols, merge_on_left, merge_on_right, platform=""):

    if type(tsr_model) != pd.DataFrame:
        raise TypeError('tsr_model must be a pd.DataFrame')
    elif type(fl_model) != pd.DataFrame:
        raise TypeError('fl_model must be a pd.DataFrame')
    elif type(tsr_cols) != list:
        raise TypeError('columns must be a list')
    elif type(merge_on_left) != str or type(merge_on_right) != str:
        raise TypeError('merging columns must be a string')
    else:
        tsr_sub = tsr_model.loc[:, tsr_cols]
        tsr_gen = fl_model[[merge_on_left]]
        proxy_model = tsr_gen.merge(tsr_sub, how="left", left_on=merge_on_left, right_on=merge_on_right)

        fl_model['TSR_Check'] = proxy_model['Amount']
        fl_model['Location_House_Number'] = proxy_model['Location_House_Number']
        fl_model['Location_City'] = proxy_model['Location_City']
        fl_model['Location_State'] = proxy_model['Location_State']
        fl_model['Location_Zip_4'] = proxy_model['Location_Zip_4']
        fl_model['Location_Full_Street_Address'] = proxy_model['Location_Full_Street_Address']
        fl_model['Location_City_State_Zip'] = proxy_model['Location_City_State_Zip']
        fl_model['Longitude'] = proxy_model['Longitude']
        fl_model['Latitude'] = proxy_model['Latitude']
        fl_model['Current_Owner'] = proxy_model['Current_Owner']
        fl_model['Standardized_Land_Use'] = proxy_model['Standardized_Land_Use']
        fl_model['Standardized_Land_Use_Desc'] = proxy_model['Standardized_Land_Use_Desc']
        fl_model['Market_Value_Year'] = proxy_model['Market_Value_Year']
        fl_model['Total_Market_Value'] = proxy_model['Total_Market_Value']
        fl_model['Tax_Amount'] = proxy_model['Tax_Amount']
        fl_model['Cert_Holder_Type1'] = proxy_model['CERT_HOLDER_TYPE1']
        fl_model['Cert_Holder_Type2'] = proxy_model['CERT_HOLDER_TYPE2']
        fl_model['Cert_Holder_Type3'] = proxy_model['CERT_HOLDER_TYPE3']
        fl_model['Cert_Holder_Type4'] = proxy_model['CERT_HOLDER_TYPE4']
        fl_model['Cert_Holder_Type5'] = proxy_model['CERT_HOLDER_TYPE5']
        fl_model['Cert_Holder_Type6'] = proxy_model['CERT_HOLDER_TYPE6']
        fl_model['Cert_Holder_Type7'] = proxy_model['CERT_HOLDER_TYPE7']
        fl_model['Latest_Arms_Length_Sale_Date'] = proxy_model['Latest_Arms_Length_Sale_Date']
        fl_model['Latest_Arms_Length_Sale_Price'] = proxy_model['Latest_Arms_Length_Sale_Price']
        fl_model['Loan1_Amount'] = proxy_model['Loan1_Amount']
        fl_model['Loan1_Type'] = proxy_model['Loan1_Type']
        fl_model['environmentalsubjectsitefoundcount'] = proxy_model['environmentalsubjectsitefoundcount']
        fl_model['environmentalsitefoundcount'] = proxy_model['environmentalsitefoundcount']
        fl_model['environmentalscore'] = proxy_model['environmentalscore']
        fl_model['FLD_CLASS'] = proxy_model['FLD_CLASS']
        fl_model['Tax Deed History'] = proxy_model['TaxDeedHistory']

        if platform.lower() == "wfbs":
            fl_model['HX'] = homesteadmodifier(proxy_model['List_Note_2'])

        return fl_model


