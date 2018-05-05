import pandas as pd
from datetime import datetime


def market_values_gen(fl_model, yearsback=0):
    mapper = []
    year = datetime.now().year - yearsback
    county_data_row = fl_model.zillow_values[(fl_model.zillow_values['Region Name'] == fl_model.county) & (fl_model.zillow_values['Region Type'] == 'county')]
    for name in county_data_row.columns:
        if type(name) == datetime:
            if name.month == 6 and ((year - name.year <= 7) and (year - name.year > 0)):
                mapper.append(name)
            if yearsback >= 0:
                if name.month == 3 and name.year == year:
                    mapper.append(name)
    return mapper
