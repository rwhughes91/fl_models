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
import re


class FloridaWrangler:
    # class variable to define the columns of every model instance
    yearsback = 0
    columns = column_creator(yearsback=yearsback)

    # Set Up
    def __init__(self, county, advfilelocation, tsrfilelocation, lumfilelocation, market_values_location,
                 use_codes_location, supplemental=''):

        """
            DOCSTRING
            advfilelocation, tsrfilelocation, lumfilelocation should be locations that point to dataframes
            these files are standard during the florida model process
            see last years for questions about these dataframes and how this model is based

        """

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
        self.zillow_values = pd.read_excel(market_values_location, sheet_name='All Homes', skiprows=[0])
        self.use_codes = pd.read_excel(use_codes_location)

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

        """
            DOCSTRING
            this function is used for the FloridaWrangler class
            it will take the instance's county name, and choose the platform from within the dict that is passed
        """

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
        """
        this function was made as a test to see what columns we should use between adv and tsr/lumentum for the merging
        :return: a dict specifying what columns we are safe to merge on
        """
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
        self._fl_model['Zillow Test'] = 'N/A'
        self._fl_model['Flood'] = 'N/A'
        self._fl_model['Equalization Ratio'] = 1

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

    def write(self, yearsback=0):
        name = "{} Florida Model.xlsx".format(self.county)
        writer = pd.ExcelWriter(name, engine='xlsxwriter')

        def market_values_gen(fl_model, yearsback=0):
            columns = ['Region Name', 'Region Type', 'Data Type']
            mapper = []
            year = datetime.now().year - yearsback
            county_data_row = fl_model.zillow_values[(fl_model.zillow_values['Region Name'] == fl_model.county) & (
                fl_model.zillow_values['Region Type'] == 'county')]
            for namee in county_data_row.columns:
                if type(namee) == datetime:
                    if namee.month == 6 and ((year - namee.year <= 7) and (year - namee.year > 0)):
                        mapper.append(namee)
                    if yearsback >= 0:
                        if namee.month == 3 and namee.year == year:
                            mapper.append(namee)
            columns = columns + mapper
            df = county_data_row.loc[:, columns].copy()
            return df

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

        # making the market_vales_tab for the excel
        market_values_df = market_values_gen(self, yearsback)
        market_values_df.to_excel(writer, sheet_name='Valuation Data', index=False, startrow=2)
        valuation_data_worksheet = writer.sheets['Valuation Data']
        valuation_data_worksheet.write_formula('D5', '=+$K$4/D4')
        valuation_data_worksheet.write_formula('E5', '=+$K$4/E4')
        valuation_data_worksheet.write_formula('F5', '=+$K$4/F4')
        valuation_data_worksheet.write_formula('G5', '=+$K$4/G4')
        valuation_data_worksheet.write_formula('H5', '=+$K$4/H4')
        valuation_data_worksheet.write_formula('I5', '=+$K$4/I4')
        valuation_data_worksheet.write_formula('J5', '=+$K$4/J4')
        valuation_data_worksheet.write_formula('K5', '=+$K$4/K4')

        valuation_data_worksheet.write_formula('D2', '=YEAR(D3)')
        valuation_data_worksheet.write_formula('E2', '=YEAR(E3)')
        valuation_data_worksheet.write_formula('F2', '=YEAR(F3)')
        valuation_data_worksheet.write_formula('G2', '=YEAR(G3)')
        valuation_data_worksheet.write_formula('H2', '=YEAR(H3)')
        valuation_data_worksheet.write_formula('I2', '=YEAR(I3)')
        valuation_data_worksheet.write_formula('J2', '=YEAR(J3)')
        valuation_data_worksheet.write_formula('K2', '=YEAR(K3)')

        # write the dataframe to the excel sheet
        self.fl_model.to_excel(writer, sheet_name='Data', index=False)
        self.use_codes.to_excel(writer, sheet_name='Use Codes & County Type', index=False)

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
        # address formulas
        formula_column_generator('BH', '=M{0}', color="#d9d9d9")
        formula_column_generator('BI', '=Proper(J{0})', color='#d9d9d9')
        formula_column_generator('BJ', '=PROPER(K{0})', color="#d9d9d9")
        formula_column_generator('BK', '=L{0}', color="#d9d9d9")
        formula_column_generator('BL', '=CONCATENATE(M{0}," ",N{0})', color="#d9d9d9")
        formula_column_generator('BP', '=IF(D{0}>10000,IF(OR(I{0}="",I{0}=0,BI{0}="",BI{0}=0,BK{0}=0),"Bad Address","Pass"),"FV<$10K")', color="#d9d9d9")

        # loan information
        formula_column_generator('BM', '=IF(AU{0}>0,"L","")', color="#d9d9d9")

        # lien information
        formula_column_generator('BN', '=IF(D{0}<150,"Lien<$150","Pass")', color="#d9d9d9")
        formula_column_generator('BO', '=IF(BC{0}="Yes","Yes","No")', color='#d9d9d9')

        # zillow tests and pulls

        # EPA, CDD, Flood
        formula_column_generator('BR', '=IF(D{0}>20000,IF(OR(BD{0}="Yes",BF{0}="Yes"),"Yes","No"),"No, < $20K Lien")', color="#d9d9d9")
        formula_column_generator('BS', '=IF(D{0}>20000,IF(IFERROR(IF(BG{0}="None","No","Yes"),"No")="Yes","Yes","No"),"No, Lien < $20K")', color="#d9d9d9")

        # priors and county tests
        formula_column_generator('BU', '=IF(E{0}="","N/A",IF(OR(E{0}<2014,AR{0}="Yes"),"Yes","No"))', color="#d9d9d9")
        formula_column_generator('BV', '=IFERROR(IF(COUNTIF(C:C,C{0})>1,"Yes","No"),"No")', color="#d9d9d9")
        formula_column_generator('BW', '=BA{0}', color="#d9d9d9")
        formula_column_generator('BX', '=IF(AND(OR(CI{0}="S",CI{0}="R",CI{0}="C"),CH{0}="Yes",BW{0}>2),"Yes",IF(AND(OR(CI{0}="S",CI{0}="R",CI{0}="C"),CH{0}="No",BW{0}>1),"Yes",IF(AND(CI{0}="V",CH{0}="Yes",BW{0}>0),"Yes","No")))', color="#d9d9d9")
        formula_column_generator('BY', '=VALUE(W{0})', color="#d9d9d9")

        # equilization tests
        formula_column_generator('CA', '=BY{0}/BZ{0}', color="#d9d9d9")

        # ALS columns
        formula_column_generator('CC', '=AS{0}', color="#d9d9d9")
        formula_column_generator('CD', '=VALUE(AT{0})', color="#d9d9d9")
        formula_column_generator('CE', '=IFERROR(IF(CD{0}>1000,YEAR(CC{0}),""),"")', color="#d9d9d9")

        # valuation data
        formula_column_generator('CF', "=HLOOKUP(CE{0},'Valuation Data'!$D$2:$K$5,4,FALSE)", color="#d9d9d9")
        formula_column_generator('CG', "=IF(CB{0}>0,MIN(IFERROR(MIN(CD{0}*CF{0},CA{0}),CA{0}),CB{0}),IFERROR(MIN(CD{0}*CF{0},CA{0}),CA{0}))", color="#d9d9d9")

        # use code tests
        formula_column_generator('CI', "=VLOOKUP(R{0},'Use Codes & County Type'!A:D,4,FALSE)", color="#d9d9d9")
        formula_column_generator('CH', '=IFERROR(IF(AND(OR(CI{0}="S",CI{0}="R",CI{0}="C",CI{0}="V"),CF{0}>0),"Yes","No"),"No")', color="#d9d9d9")
        formula_column_generator('CJ', '=IF(AND(CH{0}="No",CI{0}="V"),"Yes","No")', color="#d9d9d9")

        # homestead
        formula_column_generator('CK', '=IF(OR(BB{0}="Yes",BB{0}=""),"Yes","No")', color="#d9d9d9")

        # more valuation and cash flow tests
        formula_column_generator('CL', '=IF(AND(OR(CI{0}="S",CI{0}="R",CI{0}="C"),CH{0}="Yes",CK{0}="Yes"),75%,IF(AND(OR(CI{0}="S",CI{0}="R"),CH{0}="Yes",CK{0}="No"),40%,IF(AND(OR(CI{0}="S",CI{0}="R",CI{0}="C"),CH{0}="No",CK{0}="Yes"),67%,IF(AND(OR(CI{0}="S",CI{0}="R"),CH{0}="No",CK{0}="No"),35%,IF(AND(CI{0}="C",CH{0}="Yes"),35%,IF(AND(CI{0}="C",CH{0}="No"),30%,IF(AND(CH{0}="Yes",CI{0}="V"),10%,0%)))))))', color="#d9d9d9")
        formula_column_generator('CM', '=CG{0}*CL{0}', color="#d9d9d9")
        formula_column_generator('CN', '=D{0}+(BA{0}+3)*MAX(D{0},Z{0})', color="#d9d9d9")
        formula_column_generator('CO', '=CM{0}-CN{0}', color="#d9d9d9")
        formula_column_generator('CP', '=+CN{0}/CG{0}', color="#d9d9d9")

        # google testing
        formula_column_generator('CR', '=IF(AND(CV{0}="*Bid",D{0}>49999),"Google","No")', color="#d9d9d9")

        # bid results test
        formula_column_generator('CV', '=IF(BN{0}="Lien<$150","Lien<$150",IF(OR(BU{0}="Yes",BV{0}="Yes"),"County Held Lien",IF(CG{0}<30000,"FMV<$30K",IF(BR{0}="Yes","EPA",IF(BS{0}="Yes","CDD",IF(BT{0}="High","Flood",IF(BX{0}="Yes","Too Many Priors",IF(CJ{0}="Yes","Vacant, No Sales Data",IF(CO{0}<0,"Neg Solv Premium",IF(BP{0}="Bad Address","Bad Address",IF(CQ{0}="Bad","Bad Data",IF(CS{0}="Bad","Bad Google",IF(CT{0}="Redeemed","Redeemed",IF(CU{0}="Data Change","Data Change","*Bid"))))))))))))))', color="#d9d9d9")
        formula_column_generator('CW', '=VALUE(A{0})', color="#d9d9d9")
        formula_column_generator('CX', '=VALUE(D{0})', color="#d9d9d9")
        formula_column_generator('CY', '=IF(AND(CV{0}="*Bid",CX{0}>75000),"Check","Ok")', color="#d9d9d9")

        # output the excel to the current directory
        # pdb.set_trace()
        writer.save()

    def wrangle_and_write(self):
        self.wrangle()
        self.write()


if __name__ == "__main__":
    path = os.path.abspath(os.path.dirname(__file__))
    path_to_counties = os.path.join(path, "Completed", "{}".format(sys.argv[1]))
    files = os.listdir(path_to_counties)

    regex_matches = {
        'adv_match': [r"[.\w ]*adv?[\s_]?list[\w ]*.xlsx?"],
        'tsr_match': [r"[.\w ]*tsr[\s_]?(list)?[\w ]*.xlsx?"],
        'lum_match': [r"[.\w ]*lumentum[\s_]?[\w ]*.xlsx?"],
        'zillows_match': [r"[.\w ]*zillows?[\s_]?[\w ]*.xlsx?"]
    }

    for key, value in regex_matches.items():
        for file in files:
            search = re.search(value[0], file, re.I)
            if search:
                value.append(search.group())
                break
            else:
                continue
        if not len(value) > 1:
            raise NameError("Error on file: {}, value: {}, key: {}".format(file, value, key))

    advfilelocation = os.path.join(path_to_counties, regex_matches['adv_match'][1])
    tsrfilelocation = os.path.join(path_to_counties, regex_matches['tsr_match'][1])
    lumfilelocation = os.path.join(path_to_counties, regex_matches['lum_match'][1])
    zillow_location = os.path.join(path_to_counties, regex_matches['zillows_match'][1])
    use_code_location = os.path.join(path, "Examples", "Alachua", "Use code and county types.xlsx")

    f = FloridaWrangler(sys.argv[1], advfilelocation, tsrfilelocation, lumfilelocation, zillow_location,
                        use_code_location)




