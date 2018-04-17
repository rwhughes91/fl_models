import pandas as pd
from Florida import columns
from datetime import datetime
from Florida.Errors import InputError
from .adv_methods import homesteadmodifier, grantstreetadv, realauctionadv, dtadv, wfbsadv


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
        self.county = county
        # will choose platform based on the county named you provide the instance
        self.platform = self.platformchooser(columns['countiesByPlatform'])
        self.adv_list = pd.read_excel(advfilelocation)
        # some data is only available in supplemental files, but not all of them
        self.supplemental = supplemental
        self.tsr = pd.read_excel(tsrfilelocation)
        self.lumentum = pd.read_excel(lumfilelocation)

        # this is the beginning construction of the model we will output
        self.fl_model = pd.DataFrame(columns=FloridaWrangler.columns.names)

    def platformchooser(self, dict_like):
        '''

            DOCSTRING
            this function is used for the FloridaWrangler class
            it will take the instance's county name, and choose the platform from within the dict that is passed

        '''

        # for (key, value) in dict, if the country name is in list of values, match platform
        # if not, raise an error
        for key, value in dict_like.items():
            if self.county in value:
                platform = key
                return platform
        raise ValueError('County does not seem to have a platform!')

    '''
        Static Methods
        The methods below this point represent static methods for the class
        
    '''





