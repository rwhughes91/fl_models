import pandas as pd
from datetime import datetime
from .Errors import InputError

def lumentum_generator(lum_model, fl_model, merge_on_left, merge_on_right, platform="", yearsback=0):
    '''

    This function is made to use as a static method for the fl_wrangler class
    Purpose: this will take in a pandas dataframe from lumentum and output and output the model we use in FL for acquisitions
    Note: this will modify an existing model you pass in and return the same instance

    Caveats: the platform causes different operations, so choose carefully (see below)

    :param lum_model: pd.DataFrame
    :param fl_model: pd.DataFrame
    :param lum_cols: list of column names: length of 16
    :param merge_on_left: str
    :param merge_on_right: str
    :param platform: str
    :return fl_model: pd.DataFrame
    '''

    certholdertype = ['CertificateHolderType_1', 'CertificateHolderType_2',
                      'CertificateHolderType_3', 'CertificateHolderType_4', 'CertificateHolderType_5',
                      'CertificateHolderType_6', 'CertificateHolderType_7'
                      ]

    lum_cols = ['AdvNumber', 'NALFormat', 'AuctionFormat', 'FaceValue', 'Environmental', 'CDDName', 'BackTaxOpenCount',
                'GovtLien', 'LisPendens', certholdertype[0], certholdertype[1],
                certholdertype[2], certholdertype[3], certholdertype[4],
                certholdertype[5], certholdertype[6], 'ZoningUseCode', 'LandDescription'
                ]

    if type(lum_model) != pd.DataFrame:
        # validating arguments
        raise TypeError("lumentum model must be a dataframe")

    elif type(fl_model) != pd.DataFrame or len(fl_model.columns) != 61:
        # validating arguments
        raise TypeError("fl_model must be a dataframe with 61 columns")

    elif type(lum_cols) != list or len(lum_cols) != 18:
        # validating arguments
        raise TypeError("lum_cols must me a list to use for columns with a length of 16")

    elif (type(merge_on_left) != str and type(merge_on_right) != list)\
            or (type(merge_on_right) != str and type(merge_on_right) != list):
        # validating arguments
        raise TypeError("your merging columns must be a string")
    # checking that merging names are in the columns
    elif type(platform) != str:
        # validating arguments
        raise TypeError("counties platform must be a string")

    else:
        # if all the arguments pass
        for column in lum_cols:
            if column not in lum_model.columns:
                raise InputError('missing a column in the lum model', 'column ' + column + ' missing from model')

        # slice from the lum_cols from lum_model
        # merging the dataframe
        lum_sub = lum_model.loc[:, lum_cols]
        if type(merge_on_left) == list:
            lum_gen = fl_model[merge_on_left]
        elif type(merge_on_left) == str:
            lum_gen = fl_model[[merge_on_left]]
        prox_model = lum_gen.merge(lum_sub, how="left", left_on=merge_on_left, right_on=merge_on_right)

        fl_model['Lumentum Check'] = prox_model['FaceValue']
        fl_model['Environment File Lumentum'] = prox_model['Environmental']
        fl_model['CDD Bond'] = prox_model['CDDName']
        fl_model['GovernmentLien'] = prox_model['GovtLien']
        fl_model['LisPendens'] = prox_model['LisPendens']

        # to dynamically create columns for different platforms
        year = datetime.now().year - yearsback
        county_owned_columns = [f"Cnty. Owned {x}" for x in range(year - 7, year)]
        county_owned_columns.reverse()

        if platform.lower() == "realauction":
            fl_model['Prior Liens Outstanding'] = prox_model['BackTaxOpenCount']
        elif platform.lower() == "dt":
            # dynamically update columns (see above) -- this method is preferred so it works year over year
            for index, label in enumerate(county_owned_columns):
                fl_model[label] = prox_model[certholdertype[index]]

        elif platform.lower() == "wfbs":
            # dynamically update columns (see above) -- this method is preferred so it works year over year
            for index, label in enumerate(county_owned_columns):
                fl_model[label] = prox_model[certholdertype[index]]

            fl_model['County_Land_Use'] = prox_model['ZoningUseCode']
            fl_model['County_Land_Use_Desc'] = prox_model['LandDescription']

        return fl_model