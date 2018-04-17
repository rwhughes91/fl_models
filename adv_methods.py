from datetime import datetime
from .Errors import InputError
import pandas as pd
import math


def homesteadmodifier(array, wfbs=False):
    '''
    purpose of this function is to manipulate the homestead array into a form the fl_model accepts
    :param array: list from adv, tsr, or lum relating to homestead status of a lien
    :wfbs boolean: determines if platform is wfbs. if so, will run the function differently
    :return: updated list with the proper formatting we use in the model
    '''
    # Function to normalize homestead values from the adv_list
    # Will be used in the platform function Below

    # self data type check
    if type(array) != list:
        raise TypeError('input to the function must be of type: list')
    else:
        newarray = []
        for row in array:
            if row:
                if row is True:
                    newarray.append('Yes')
                elif type(row) == str:
                    word = row.lower()
                    if word.startswith('y') or word.startswith('hx') or word.startswith("t"):
                        newarray.append('Yes')
                    else:
                        newarray.append('No')
                elif type(row) == int or type(row) == float:
                    if row > 0:
                        newarray.append('Yes')
                    elif math.isnan(row):
                        newarray.append('Yes')
                    else:
                        newarray.append('No')
            elif row is False:
                newarray.append('No')
            elif row == 0:
                newarray.append('No')
            elif wfbs:
                newarray.append('No')
            else:
                newarray.append('Yes')
        return newarray


def grantstreetadv(county, adv_list, fl_model):
    '''
    takes in county name, adv_list location, and fl_model
    will build out the fl_model with the assumtion of a grantstreet platform
    :param county: string
    :param adv_list: pandas.DataFrame
    :param fl_model: pandas.DataFrame
    :return fl_model: pandas.DataFrame
    '''

    if type(county) != str:
        raise TypeError('County must be a string')
    elif type(adv_list) != pd.DataFrame:
        raise TypeError('adv_list must be a pandas dataframe')
    elif type(fl_model) != pd.DataFrame:
        raise TypeError('fl_model must be a pandas dataframe')

    # dynamically get the current year we want to work with
    year = datetime.now().year
    # dynamically create columns that update by year for the adv_list
    # for fl_model
    cnty = [f"Cnty. Owned ({x})" for x in range(year - 7, year)]
    cnty.reverse()
    # for pulling from adv_list
    county_owned_columns = [f"Cnty. Owned {x}" for x in range(year - 7, year)]
    county_owned_columns.reverse()

    # certain counties pull differently
    if county == "Charlotte" or "Indian River" or "Pinellas":
        # need to use Parcel No. instead of Account No.
        fl_model['Account No.'] = adv_list['Parcel No.']
    elif county == "Pasco":
        # need to use Fude instead of Account No.
        fl_model['Account No.'] = adv_list['Fuse']
    else:
        # can use Account No.
        fl_model['Account No.'] = adv_list['Account No.']

    fl_model['Adv No.'] = adv_list['Adv No.']
    fl_model['Amount'] = adv_list['Face Amount']
    fl_model['Tax_Year'] = adv_list['Tax Year']

    # if the use codes go higher than 100 they come in the 01000 format
    # dividing by 100 will fix this potential issue
    if max(adv_list['Use Code']) >= 100:
        fl_model['County_Land_Use'] = adv_list['Use Code'] / 100
    else:
        fl_model['County_Land_Use'] = adv_list['Use Code']

    fl_model['County_Land_Use_Desc'] = adv_list['Use Code Description']
    fl_model['Assessment_Year'] = adv_list['Assessed Year']
    fl_model['Total_Assessed_Value'] = adv_list['Assessed Value']

    # dynamically update columns (see above) -- this method is preferred so it works year over year
    for index, label in enumerate(county_owned_columns):
        fl_model[label] = adv_list[cnty[index]]

    fl_model['HX'] = homesteadmodifier(adv_list['Homestead'])
    fl_model['Prior Liens Outstanding'] = adv_list['Prior Certs Outstand.']  # need to lookup still

    return fl_model


def realauctionadv(adv_list, fl_model):
    '''
    takes in county name, adv_list location, and fl_model
    will build out the fl_model with the assumtion of a real_auction platform
    :param adv_list:
    :param fl_model:
    :return fl_model:
    '''

    if type(adv_list) != pd.DataFrame:
        raise TypeError('adv_list must be a pandas dataframe')
    elif type(fl_model) != pd.DataFrame:
        raise TypeError('fl_model must be a pandas dataframe')

    ctype = ['CERT_TYP1', 'CERT_TYP2', 'CERT_TYP3', 'CERT_TYP4', 'CERT_TYP5', 'CERT_TYP6', 'CERT_TYP7']
    ctypeBoolean = True

    fl_model['Account No.'] = adv_list['FOLIO']
    fl_model['Adv No.'] = adv_list['ADV_NUM']
    fl_model['Amount'] = adv_list['ADV_AMT']
    fl_model['Tax_Year'] = adv_list['TAX_YEAR']

    # if the use codes go higher than 100 they come in the 01000 format
    # dividing by 100 will fix this potential issue
    if max(adv_list['SLUC']) >= 100:
        fl_model['County_Land_Use'] = adv_list['SLUC'] / 100
    else:
        fl_model['County_Land_Use'] = adv_list['SLUC']

    fl_model['County_Land_Use_Desc'] = adv_list['SLUC_DESC']
    fl_model['Assessment_Year'] = datetime.now().year - 1
    fl_model['Total_Assessed_Value'] = adv_list['ASSESSED']

    # dynamically adding columns if they exist in the adv_list
    # the alt. is to use the supplemental dataframe to pull the columns

    for col in ctype[0:6]:
        if col in adv_list.columns:
            ctypeBoolean = True
        else:
            ctypeBoolean = False

    if ctypeBoolean:
        year = datetime.now().year
        county_owned_columns = [f"Cnty. Owned {x}" for x in range(year - 6, year)]
        county_owned_columns.reverse()

        for index, label in enumerate(county_owned_columns):
            fl_model[label] = adv_list[ctype[index]]

    else:
        raise InputError("Can't pull in Cert_typ(n)", "You need to import a supplemental dataframe to successfully pull \
           in all column data!")

    if ctype[6] in adv_list.columns:
        fl_model['Cnty. Owned 2010'] = adv_list[ctype[6]]

    fl_model['HX'] = homesteadmodifier(adv_list['HMSTEAD'])

    if 'prior_liens' in adv_list.columns:
        fl_model['Prior Liens Outstanding'] = adv_list['prior_liens']  # need to lookup still

    return fl_model


def dtadv(adv_list, fl_model):

    if type(adv_list) != pd.DataFrame:
        raise TypeError('adv_list must be a pandas dataframe')
    elif type(fl_model) != pd.DataFrame:
        raise TypeError('fl_model must be a pandas dataframe')

    fl_model['Account No.'] = adv_list['PropertyNo']
    fl_model['Adv No.'] = adv_list['SequenceID']
    fl_model['Amount'] = adv_list['UnPaidBalance']
    fl_model['Tax_Year'] = datetime.now().year - 1

    # if the use codes go higher than 100 they come in the 01000 format
    # dividing by 100 will fix this potential issue
    if max(adv_list['UseCode']) >= 100:
        fl_model['County_Land_Use'] = adv_list['UseCode']
    else:
        fl_model['County_Land_Use'] = adv_list['UseCode']

    fl_model['County_Land_Use_Desc'] = adv_list['UseCodeDescription']
    fl_model['Assessment_Year'] = datetime.now().year - 1
    fl_model['Total_Assessed_Value'] = adv_list['AssessedValue']
    fl_model['Prior Liens Outstanding'] = adv_list['PriorDelinqYrs']  # need to lookup still

    fl_model['HX'] = homesteadmodifier(adv_list['Homestead'])


def wfbsadv(adv_list, fl_model):

    if type(adv_list) != pd.DataFrame:
        raise TypeError('adv_list must be a pandas dataframe')
    elif type(fl_model) != pd.DataFrame:
        raise TypeError('fl_model must be a pandas dataframe')

    fl_model['Account No.'] = adv_list['Parcel Account Number']
    fl_model['Adv No.'] = adv_list['Advertising Seq No']
    fl_model['Amount'] = adv_list['Face Amount']
    fl_model['Tax_Year'] = adv_list['Tax Year']
    fl_model['Assessment_Year'] = datetime.now().year - 1
    fl_model['Total_Assessed_Value'] = adv_list['Assessed Value']
    fl_model['Prior Liens Outstanding'] = adv_list['Unpaid Certificates']  # need to lookup still
