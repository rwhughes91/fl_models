import pandas as pd
from Florida import column_creator
from datetime import datetime
from Florida.Errors import InputError
from Florida.adv_methods import homesteadmodifier, grantstreetadv, realauctionadv, dtadv, wfbsadv
from Florida.lumentum_methods import lumentum_generator
from Florida.tsr_methods import tsr_generator
from Florida.Errors import MergingError
import sys
import os
import numpy as np
import pdb

class FloridaWrangler:
    # class variable to define the columns of every model instance
    yearsback = 1
    columns = column_creator(yearsback=yearsback)

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
        self._platform = self.platformchooser(FloridaWrangler.columns['countiesByPlatform'])

        self.adv_list = pd.read_excel(advfilelocation)
        # some data is only available in supplemental files, but not all of them
        self.supplemental = supplemental
        self.tsr = pd.read_excel(tsrfilelocation)
        self.lumentum = pd.read_excel(lumfilelocation)

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
        self._platform = self.platformchooser(FloridaWrangler.columns['countiesByPlatform'])

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

    def adv_gen(self, yearsback=0):
        platform = self._platform.lower()

        if platform == "grantstreet":
            self._fl_model = grantstreetadv(self._county, self.adv_list, self._fl_model, yearsback)

        elif platform == "realauction":
            # do something
            self._fl_model = realauctionadv(self.adv_list, self._fl_model, yearsback)

        elif platform == "dt":
            # do something
            self._fl_model = dtadv(self.adv_list, self._fl_model, yearsback)

        elif platform == "wfbs":
            # do something
            self._fl_model = wfbsadv(self.adv_list, self._fl_model, yearsback)

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
        if len(df_adv['parcel compare']) == df_adv['parcel compare'].sum() and df_adv['parcel compare'].sum() > 0:
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
            if len(df_parcel['adv compare']) == df_parcel['adv compare'].sum() and df_parcel['adv compare'].sum() > 0:
                tsr_result = {
                    "left_on": ["Account No.", "Adv No."],
                    "right_on": ['Parcel_ID', 'List_Item_Ref']
                }

            # if no merging calculation failed for tsr -- something wrong with tsr
            else:
                raise MergingError("Both parcel and adv dont seem to be merging correctly between tsr and the adv list")

        # first merging calculation fl to lumentum
        lum = self.lumentum.loc[:, ["NALFormat", "AuctionFormat", "AdvNumber"]].copy()

        df_adv_lum = df.merge(lum, how="inner", left_on="Adv No.", right_on="AdvNumber")

        df_adv_lum['parcel compare'] = df_adv_lum['Account No.'] == df_adv_lum['NALFormat']
        df_adv_lum['parcel compare2'] = df_adv_lum['Account No.'] == df_adv_lum['AuctionFormat']

        # validating the merge
        if (len(df_adv_lum['parcel compare']) == df_adv_lum['parcel compare'].sum()\
                or len(df_adv_lum['parcel compare2']) == df_adv_lum['parcel compare2'].sum())\
                and (df_adv_lum['parcel compare'].sum() > 0 or df_adv_lum['parcel compare2'].sum() > 0):
            lum_result = {
                "left_on": "Adv No.",
                "right_on": "AdvNumber"
            }
        # second merging calculation fl to lumentum
        else:
            df_parcel_lum = df.merge(lum, how="inner", left_on=["Account No.", "Adv No."],
                                     right_on=["NALFormat", "AdvNumber"])
            df_parcel_lum_alt = df.merge(lum, how="inner", left_on=["Account No.", "Adv No."],
                                         right_on=["AuctionFormat", "AdvNumber"])

            df_parcel_lum['adv compare'] = df_parcel_lum['Adv No.'] == df_parcel_lum['AdvNumber']
            df_parcel_lum_alt['adv compare'] = df_parcel_lum_alt['Adv No.'] == df_parcel_lum_alt['AdvNumber']

            # validating the merge
            if len(df_parcel_lum['adv compare']) == df_parcel_lum['adv compare'].sum()\
                    and df_parcel_lum['adv compare'].sum() > 0:
                lum_result = {
                    "left_on": ["Account No.", "Adv No."],
                    "right_on": ["NALFormat", "AdvNumber"]
                }
            # validating the merge
            elif len(df_parcel_lum_alt['adv compare']) == df_parcel_lum_alt['adv compare'].sum()\
                    and df_parcel_lum_alt['adv compare'].sum() > 0:
                lum_result = {
                    "left_on": ["Account No.", "Adv No."],
                    "right_on": ["AuctionFormat", "AdvNumber"]
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
        # making sure the columns are available for merging
        if "tsr" in self._merge.keys():
            left_on = self._merge['tsr']["left_on"]
            right_on = self._merge['tsr']["right_on"]
            self._fl_model = tsr_generator(self.tsr, self._fl_model, left_on, right_on, self._platform.lower())
        else:
            raise InputError("you need to generate the merging columns before using", "")

    def lumentum_gen(self, yearsback=0):
        # making sure the columns are available for merging
        if "lum" in self._merge.keys():
            left_on = self._merge['lum']["left_on"]
            right_on = self._merge['lum']["right_on"]
            self._fl_model = lumentum_generator(self.lumentum, self._fl_model, left_on, right_on, self._platform.lower(), yearsback)
        else:
            raise InputError("you need to generate the merging columns before using", "")

    def cleanup(self):
        self._fl_model['County'] = self.county

        # get rid of all zeros in 2 different columns: Location_House_Number and CDD Bond
        zero_values_address = f.fl_model['Location_House_Number'] == 0
        f._fl_model.loc[zero_values_address, 'Location_House_Number'] = np.nan

        zero_values_cdd = f.fl_model['CDD Bond'] == 0
        f._fl_model.loc[zero_values_cdd, 'CDD Bond'] = np.nan

    def wrangle(self):
        self.adv_gen(FloridaWrangler.yearsback)
        self.merging_calc()
        self.tsr_gen()
        self.lumentum_gen(FloridaWrangler.yearsback)
        self.cleanup()

    def write(self):
        name = "{} Florida Model.xlsx".format(self.county)
        writer = pd.ExcelWriter(name, engine='xlsxwriter')

        def formula_column_generator(column, formula, color=''):
            length = f.fl_model.shape[0]
            column = column + '{}'
            if not color:
                formatting = False
            else:
                formatting = True
            nonlocal worksheet
            nonlocal writer

            cell_format = writer.book.add_format()
            cell_format.set_bg_color(color)

            # want to iterate through range 1 to length +1
            for row in range(1, length+1):
                form = formula.format(row+1)
                col = column.format(row+1)
                worksheet.write_formula(col, form, cell_format)

        def na_error_generator_map(df, value_to_change):
            # iterate through row of data frame
            # for each column
            log = []
            for column, series in df.iteritems():
                for index, value in series.iteritems():
                    if value == value_to_change:
                        col = list(df.columns).index(column)
                        log.append((index, col))
            return log

        # write the dataframe to the excel sheet
        self.fl_model.to_excel(writer, sheet_name='Data', index=False)

        # loop through each row of the Amount check column --
        worksheet = writer.sheets['Data']
        formula_column_generator('H', "=D{0}+D{0}-F{0}-G{0}", color="#d9d9d9")

        # generate the n/a error outputs
        log = na_error_generator_map(f.fl_model, '#N/A')
        for coordinates in log:
            worksheet.write_formula(coordinates[0]+1, coordinates[1], "=NA()")

        # annual/current tax
        formula_column_generator('AA', "=IFERROR(Z{0}/D{0},"")", color="#d9d9d9")

        # county owned lien checks
        formula_column_generator('AP', '=IF(OR(COUNTIF(AB{0}:AH{0},"Yes")>0,COUNTIF(AB{0}:AH{0},"C")>0),"Yes","No")',
                                 color="#d9d9d9")
        formula_column_generator('AQ', '=IF(COUNTIF(AI{0}:AO{0},"C")>0,"Yes","No")',
                                 color="#d9d9d9")
        formula_column_generator('AR', '=IF(AP{0}="Yes","Yes","No")',
                                 color="#d9d9d9")
        # environmental file for tsr
        formula_column_generator('BD', '=IFERROR(IF(AW{0}>0,"Yes","No"),"No")', color="d9d9d9")
        # environmental file for lumentum
        formula_column_generator('BF', '=IFERROR(IF(BE{0}="Without Environmental Issues","No","Yes"),"No")',
                                 color="#d9d9d9")

        # output the excel to the current directory
        # pdb.set_trace()
        writer.save()

    def wrangle_and_write(self):
        self.wrangle()
        self.write()


if __name__ == "__main__":
    path = os.path.abspath(os.path.dirname(__file__))
    advfilelocation = path + r"\Examples\Alachua\Al test fl.xlsx"
    tsrfilelocation = path + r"\Examples\Alachua\al tsr.xlsx"
    lumfilelocation = path + r"\Examples\Alachua\Alachua Lumentum 2017.xlsx"

    f = FloridaWrangler(sys.argv[1], advfilelocation, tsrfilelocation, lumfilelocation)




