import pandas as pd
from Florida import columns
from datetime import datetime
from Florida.Errors import InputError


class FloridaWrangler:
    # Set Up
    def __init__(self, county, advfilelocation, tsrfilelocation, lumfilelocation, supplemental=''):
        self.county = county
        self.platform = self.platformchooser(columns['countiesByPlatform'])
        self.adv_list = pd.read_excel(advfilelocation)
        self.supplemental = supplemental
        self.tsr = pd.read_excel(tsrfilelocation)
        self.lumentum = pd.read_excel(lumfilelocation)
        self.fl_model = pd.DataFrame(columns=columns.names)

    def platformchooser(self, dict_like):
        for key, value in dict_like.items():
            if self.county in value:
                platform = key
                return platform
            else:
                raise ValueError('Platform assignment not properly working')

    '''Static Methods'''
    @staticmethod
    def homesteadmodifier(array):
        # Function to normalize homestead values from the adv_list
        # Will be used in the platform function Below
        newarray = []
        for row in array:
            if row:
                word = row.lower()
                if word.startswith('y') or word.startswith('hx'):
                    newarray.append('Yes')
                else:
                    newarray.append('No')
            else:
                newarray.append('No')
        return newarray

    @staticmethod
    def grantstreetadv(county, adv_list, fl_model):
        year = datetime.now().year
        cnty = [f"Cnty. Owned ({x})" for x in range(year - 7, year)]
        cnty.reverse()
        county_owned_columns = [f"Cnty. Owned {x}" for x in range(year-7, year)]
        county_owned_columns.reverse()

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
        if max(adv_list['Use Code']) >= 100:
            fl_model['County_Land_Use'] = adv_list['Use Code']/100
        else:
            fl_model['County_Land_Use'] = adv_list['Use Code']
        fl_model['County_Land_Use_Desc'] = adv_list['Use Code Description']
        fl_model['Assessment_Year'] = adv_list['Assessed Year']
        fl_model['Total_Assessed_Value'] = adv_list['Assessed Value']

        for index, label in enumerate(county_owned_columns):
            fl_model[label] = adv_list[cnty[index]]

        fl_model['HX'] = FloridaWrangler.homesteadmodifier(adv_list['Homestead'])
        fl_model['Prior Liens Outstanding'] = adv_list['Prior Certs Outstand.']  # need to lookup still

        return fl_model

    @staticmethod
    def realauctionadv(adv_list, fl_model):
        ctype = ['CERT_TYP1', 'CERT_TYP2', 'CERT_TYP3', 'CERT_TYP4', 'CERT_TYP5', 'CERT_TYP6', 'CERT_TYP7']
        ctypeBoolean = True

        fl_model['Account No.'] = adv_list['FOLIO']
        fl_model['Adv No.'] = adv_list['ADV_NUM']
        fl_model['Amount'] = adv_list['ADV_AMT']
        fl_model['Tax_Year'] = adv_list['TAX_YEAR']

        if max(adv_list['SLUC']) >= 100:
            fl_model['County_Land_Use'] = adv_list['SLUC']/100
        else:
            fl_model['County_Land_Use'] = adv_list['SLUC']

        fl_model['County_Land_Use_Desc'] = adv_list['SLUC_DESC']
        fl_model['Assessment_Year'] = datetime.now().year -1
        fl_model['Total_Assessed_Value'] = adv_list['ASSESSED']

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
            raise InputError("Can't pull in Cert_typn", "You need to import a supplemental dataframe to successfully pull \
            in all column data!")

        if ctype[6] in adv_list.columns:

            fl_model['Cnty. Owned 2010'] = adv_list[ctype[6]]

        fl_model['HX'] = FloridaWrangler.homesteadmodifier(adv_list['HMSTEAD'])

        if 'prior_liens' in adv_list.columns:
            fl_model['Prior Liens Outstanding'] = adv_list['prior_liens'] #need to lookup still

        return fl_model

    @staticmethod
    def dtadv(adv_list, fl_model):
        fl_model['Account No.'] = adv_list['PropertyNo']
        fl_model['Adv No.'] = adv_list['SequenceID']
        fl_model['Amount'] = adv_list['UnPaidBalance']
        fl_model['Tax_Year'] = datetime.now().year - 1

        if max(adv_list['UseCode']) >= 100:
            fl_model['County_Land_Use'] = adv_list['UseCode']
        else:
            fl_model['County_Land_Use'] = adv_list['UseCode']

        fl_model['County_Land_Use_Desc'] = adv_list['UseCodeDescription']
        fl_model['Assessment_Year'] = datetime.now().year - 1
        fl_model['Total_Assessed_Value'] = adv_list['AssessedValue']
        fl_model['Prior Liens Outstanding'] = adv_list['PriorDelinqYrs']  # need to lookup still

        fl_model['HX'] = FloridaWrangler.homesteadmodifier(adv_list['Homestead'])

    @staticmethod
    def wfbsadv(adv_list, fl_model):
        fl_model['Account No.'] = adv_list['Parcel Account Number']
        fl_model['Adv No.'] = adv_list['Advertising Seq No']
        fl_model['Amount'] = adv_list['Face Amount']
        fl_model['Tax_Year'] = adv_list['Tax Year']
        fl_model['Assessment_Year'] = datetime.now().year - 1
        fl_model['Total_Assessed_Value'] = adv_list['Assessed Value']
        fl_model['Prior Liens Outstanding'] = adv_list['Unpaid Certificates']  # need to lookup still




