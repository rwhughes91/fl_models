import pandas as pd
from Florida import columns
from datetime import datetime
from Florida.Errors import InputError
from Florida.adv_methods import homesteadmodifier, grantstreetadv, realauctionadv, dtadv, wfbsadv
from Florida.lumentum_methods import lumentum_generator
from Florida.tsr_methods import tsr_generator
from Florida.Errors import MergingError


class FloridaWrangler:
    # class variable to define the columns of every model instance
    columns = columns

    # Set Up
    def __init__(self, county, advfilelocation, tsrfilelocation, lumfilelocation, supplemental=''):

        '''
            DOCSTRING
            advfilelocation, tsrfilelocation, lumfilelocation should be locations that point to dataframes
            these files are standard during the florida model process
            see last years for questions about these dataframes and how this model is based

        '''

        # will tell you what county we are dealing with and how the model just be constructed from here
        self._county = county
        # will choose platform based on the county named you provide the instance
        self._platform = self.platformchooser(columns['countiesByPlatform'])
        self.adv_list = pd.read_excel(advfilelocation)
        # some data is only available in supplemental files, but not all of them
        self.supplemental = supplemental
        self.tsr = pd.read_excel(tsrfilelocation)
        self.lumentum = pd.read_excel(lumfilelocation)

        # this is the beginning construction of the model we will output
        self._fl_model = pd.DataFrame(columns=FloridaWrangler.columns.names)

    @property
    def county(self):
        return self._county

    @county.setter
    def county(self, value):
        print("changing the county name. Please note this will change the entire object")
        self._county = value
        self._platform = self.platformchooser(columns['countiesByPlatform'])

    @county.deleter
    def county(self):
        print("you cannot delete this property")

    @property
    def platform(self):
        return self._platform

    @platform.setter
    def platform(self, value):
        print("you cannot change the platform. this is auto done upon creation")

    @platform.deleter
    def platform(self):
        print("you cannot delete this property")

    @property
    def fl_model(self):
        return self._fl_model


    def platformchooser(self, dict_like):
        '''

            DOCSTRING
            this function is used for the FloridaWrangler class
            it will take the instance's county name, and choose the platform from within the dict that is passed

        '''

        # for (key, value) in dict, if the country name is in list of values, match platform
        # if not, raise an error
        for key, value in dict_like.items():
            if self._county in value:
                platform = key
                return platform
        raise ValueError('County does not seem to have a platform!')

    def adv_gen(self):
        platform = self._platform.lower()

        if platform == "grantstreet":
            self._fl_model = grantstreetadv(self._county, self.adv_list, self._fl_model)

        elif platform == "realauction":
            # do something
            self._fl_model = realauctionadv(self.adv_list, self._fl_model)

        elif platform == "dt":
            # do something
            self._fl_model = dtadv(self.adv_list, self._fl_model)

        elif platform == "wfbs":
            # do something
            self._fl_model = wfbsadv(self.adv_list, self._fl_model)

        else:
            raise InputError("something seems to be wrong with the platform", "it needs to be one the big 4")

    def merging_calc(self):
        '''
        this function was made as a test to see what columns we should use between adv and tsr/lumentum for the merging
        :return: a dict specifying what columns we are safe to merge on
        '''

        df = self._fl_model.loc[:, ['Account No.', 'Adv No.', 'Amount']].copy()
        tsr = self.tsr.loc[:, ["Parcel_ID", "List_Item_Ref", "Amount"]].copy()

        df_parcel = df.merge(tsr, how="inner", left_on=["Account No.", "Adv No."],
                             right_on=["Parcel ID", "List_Item_Ref"])
        df_adv = df.merge(tsr, how="inner", left_on="Adv No.", right_on="List_Item_Ref")

        df_parcel['adv compare'] = df_parcel['Adv No.'] == df_parcel['List_Item_Ref']
        df_parcel['amount compare'] = df_parcel['Amount_x'] == df_parcel['Amount_y']

        df_adv['parcel compare'] = df_adv['Account No.'] == df_adv['Parcel_ID']
        df_adv['amount compare'] = df_adv['Amount_x'] == df_adv['Amount_y']

        if len(df_adv['parcel compare']) == df_adv['parcel compare'].sum():
            result = {'left_on': "Adv No.",
                      "right_on": "List_Item_Ref"
                      }
            return result

        elif len(df_parcel['Account No.']) == df_parcel['adv compare'].sum():
            result = {"left_on": ["Account No.", "Adv No."],
                      "right_on": ['Parcel_ID', 'List_Item_Ref']
                      }
            return result
        else:
            raise MergingError("Both parcel and adv dont seem to be merging correctly between tsr and the adv list")

    def tsr_gen(self):
        # do something
        return

    def lumentum_gen(self):
        # do something
        return





