import pandas as pd
from .adv_methods import homesteadmodifier
from .Errors import InputError
import numpy as np


def tsr_generator(tsr_model, fl_model, merge_on_left, merge_on_right, platform=""):
    '''

    :param tsr_model: pd.Dataframe that comes in from tsr
    :param fl_model: pd.Dataframe -- used for the florida models
    :param merge_on_left: string -- column to merge on
    :param merge_on_right: string -- column to merge on
    :param platform: a string that determines some extra functionality
    :return fl_model: pd.Dataframe -- original with updates
    '''

    tsr_cols = ['Parcel_ID', 'List_Item_Ref', 'Amount', 'Location_House_Number', 'Location_City', 'Location_State', 'Location_Zip_4',
                'Location_Full_Street_Address',
                'Location_City_State_Zip', 'Longitude', 'Latitude', 'Current_Owner', 'Standardized_Land_Use',
                'Standardized_Land_Use_Desc', 'Market_Value_Year',
                'Total_Market_Value', 'Tax_Amount', 'CERT_HOLDER_TYPE1', 'CERT_HOLDER_TYPE2', 'CERT_HOLDER_TYPE3',
                'CERT_HOLDER_TYPE4', 'CERT_HOLDER_TYPE5',
                'CERT_HOLDER_TYPE6', 'CERT_HOLDER_TYPE7', 'Latest_Arms_Length_Sale_Date',
                'Latest_Arms_Length_Sale_Price', 'Loan1_Amount', 'Loan1_Type',
                'environmentalsubjectsitefoundcount', 'environmentalsitefoundcount', 'environmentalscore', 'FLD_CLASS',
                'TaxDeedHistory', 'List_Note_2'
                ]

    # validating attribute types in the function
    if type(tsr_model) != pd.DataFrame:
        raise TypeError('tsr_model must be a pd.DataFrame')
    elif type(fl_model) != pd.DataFrame:
        raise TypeError('fl_model must be a pd.DataFrame')
    # making sure the tsr_cols was not manipulated
    elif type(tsr_cols) != list or len(tsr_cols) != 34:
        raise TypeError('columns must be a list with a length of 33')
    elif (type(merge_on_left) != str and type(merge_on_left) != list)\
            or (type(merge_on_right) != str and type(merge_on_right) != list):
        raise TypeError('merging columns must be a string')
    # making sure the merging will work correctly
    elif type(platform) != str:
        raise TypeError('platform must be a string')
    else:
        # validating column names in the tsr_model
        for column in tsr_cols:
            if column not in tsr_model.columns:
                raise InputError('tsr model missing a column', 'missing ' + column + ' in tsr_model')

        # merging the dataframe
        tsr_sub = tsr_model.loc[:, tsr_cols]
        if type(merge_on_left) == str:
            tsr_gen = fl_model[[merge_on_left]]
        elif type(merge_on_left) == list:
            tsr_sub['Parcel_ID'] = tsr_model['Parcel_ID']
            tsr_gen = fl_model[merge_on_left]
        else:
            raise TypeError('Merging Columns must be a list of strings or a string - tsr')
        proxy_model = tsr_gen.merge(tsr_sub, how="left", left_on=merge_on_left, right_on=merge_on_right)

        # validate no row shifting
        row_length = proxy_model.shape[0]
        if not fl_model.shape[0] == row_length:
            if row_length > fl_model.shape[0]:
                duplicates = [str(index) for index, value in proxy_model['List_Item_Ref'].value_counts().iteritems() if
                              value > 1]
                message = ", ".join(duplicates)
                raise ValueError("duplicate adv numbers in tsr: {}".format(message))
            else:
                raise ValueError("looks like the left merging didn't work, your fl_model is less than proxy")

        # conditionally changing null values in the data frame to simulate an excel vlookup
        slice = pd.isnull(proxy_model['List_Item_Ref'])
        if slice.sum() > 0:
            proxy_model.loc[slice, :] = proxy_model.loc[slice, :].fillna('#N/A')
        proxy_model = proxy_model.fillna(0)

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
            fl_model['HX'] = homesteadmodifier(proxy_model['ID_11'], wfbs=True)

        return fl_model


