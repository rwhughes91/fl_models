import pandas as pd
from Florida import columns
from datetime import datetime
from Florida.Errors import InputError
from Florida.adv_methods import homesteadmodifier, grantstreetadv, realauctionadv, dtadv, wfbsadv
from Florida.lumentum_methods import lumentum_generator
from Florida.tsr_methods import tsr_generator
from Florida.Errors import MergingError
import sys
from halo import Halo


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
        if type(county) != str:
            raise InputError("county must be a string", "must be one of the 60 counties")
        else:
            self._county = county
        # will choose platform based on the county named you provide the instance
        self._platform = self.platformchooser(columns['countiesByPlatform'])

        spinner = Halo(text="Reading in the files", spinner="dots")
        spinner.start()

        self.adv_list = pd.read_excel(advfilelocation)
        # some data is only available in supplemental files, but not all of them
        self.supplemental = supplemental
        self.tsr = pd.read_excel(tsrfilelocation)
        self.lumentum = pd.read_excel(lumfilelocation)

        spinner.succeed("Files were read in successfully")

        # this is the beginning construction of the model we will output
        self._fl_model = pd.DataFrame(columns=FloridaWrangler.columns['names'])
        self._merge = {}

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
        # reading in the frames
        df = self._fl_model.loc[:, ['Account No.', 'Adv No.']].copy()
        tsr = self.tsr.loc[:, ["Parcel_ID", "List_Item_Ref"]].copy()

        # fist merging calculation fl to tsr
        df_adv = df.merge(tsr, how="inner", left_on="Adv No.", right_on="List_Item_Ref")
        df_adv['parcel compare'] = df_adv['Account No.'] == df_adv['Parcel_ID']

        # validating the merge
        if len(df_adv['parcel compare']) == df_adv['parcel compare'].sum():
            tsr_result = {
                'left_on': "Adv No.",
                "right_on": "List_Item_Ref"
            }

        # second merging for fl to tsr (only runs if first fails)
        else:
            df_parcel = df.merge(tsr, how="inner", left_on=["Account No.", "Adv No."],
                                 right_on=["Parcel ID", "List_Item_Ref"])

            df_parcel['adv compare'] = df_parcel['Adv No.'] == df_parcel['List_Item_Ref']

            # validating the merge
            if len(df_parcel['adv compare']) == df_parcel['adv compare'].sum():
                tsr_result = {
                    "left_on": ["Account No.", "Adv No."],
                    "right_on": ['Parcel_ID', 'List_Item_Ref']
                }

            # if no merging calculation failed for tsr -- something wrong with tsr
            else:
                raise MergingError("Both parcel and adv dont seem to be merging correctly between tsr and the adv list")

        # first merging calculation fl to lumentum
        lum = self.lumentum.loc[:, ["NALFormat", "TaxCollectorFormat", "AdvNumber"]].copy()

        df_adv_lum = df.merge(lum, how="inner", left_on="Adv No.", right_on="AdvNumber")

        df_adv_lum['parcel compare'] = df_adv_lum['Account No.'] == df_adv_lum['NALFormat']
        df_adv_lum['parcel compare2'] = df_adv_lum['Account No.'] == df_adv_lum['TaxCollectorFormat']

        # validating the merge
        if len(df_adv_lum['parcel compare']) == df_adv_lum['parcel compare'].sum() or len(df_adv_lum['parcel compare2']) == df_adv_lum['parcel compare2'].sum():
            lum_result = {
                "left_on": "Adv No.",
                "right_on": "AdvNumber"
            }
        # second merging calculation fl to lumentum
        else:
            df_parcel_lum = df.merge(lum, how="inner", left_on=["Account No.", "Adv No."],
                                     right_on=["NALFormat", "AdvNumber"])
            df_parcel_lum_alt = df.merge(lum, how="inner", left_on=["Account No.", "Adv No."],
                                         right_on=["TaxCollectorFormat", "AdvNumber"])

            df_parcel_lum['adv compare'] = df_parcel_lum['Adv No.'] == df_parcel_lum['AdvNumber']
            df_parcel_lum_alt['adv compare'] = df_parcel_lum_alt['Adv No.'] == df_parcel_lum_alt['AdvNumber']

            # validating the merge
            if len(df_parcel_lum['adv compare']) == df_parcel_lum['adv compare'].sum():
                lum_result = {
                    "left_on": ["Account No.", "Adv No."],
                    "right_on": ["NALFormat", "AdvNumber"]
                }
            # validating the merge
            elif len(df_parcel_lum_alt['adv compare']) == df_parcel_lum_alt['adv compare'].sum():
                lum_result = {
                    "left_on": ["Account No.", "Adv No."],
                    "right_on": ["TaxCollectorFormat", "AdvNumber"]
                }
            else:
                raise MergingError("Both parcel and adv dont seem to be merging\
                 correctly between lumentum and the adv list")
        result = {
            "tsr": tsr_result,
            "lum": lum_result
        }
        self._merge = result
        return result

    def tsr_gen(self):
        # do something
        return

    def lumentum_gen(self):
        # do something
        return

if __name__ == "__main__":
    advfilelocation = r"C:\Users\rhughes\Documents\Al test fl.xlsx"
    tsrfilelocation = r"C:\Users\rhughes\Documents\al tsr.xlsx"
    lumfilelocation = r"C:\Users\rhughes\Documents\Alachua Lumentum 2017.xlsx"

    f = FloridaWrangler(sys.argv[1], advfilelocation, tsrfilelocation, lumfilelocation)




