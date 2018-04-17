import pandas as pd



def lumentum_generator(lum_model, fl_model, lum_cols, merge_on_left, merge_on_right, platform=""):

    lum_sub = lum_model.loc[:, lum_cols]
    lum_gen = fl_model[[merge_on_left]]
    prox_model = lum_gen.merge(lum_sub, how="left", left_on=merge_on_left, right_on=merge_on_right)

    fl_model['Lumentum Check'] = prox_model['FaceValue']
    fl_model['Environment File Lumentum'] = prox_model['Environmental']
    fl_model['CDD Bond'] = prox_model['CDDName']
    fl_model['GovernmentLien'] = prox_model['GovtLien']
    fl_model['LisPendens'] = prox_model['LisPendens']

    if platform.lower() == "real auction":
        fl_model['Prior Liens Outstanding'] = prox_model['BackTaxOpenCount']
    elif platform.lower() == "dt":

        # need to dynamically create these columns

        fl_model['Cnty. Owned 2016'] = prox_model['CertificateHolderType_1']
        fl_model['Cnty. Owned 2015'] = prox_model['CertificateHolderType_2']
        fl_model['Cnty. Owned 2014'] = prox_model['CertificateHolderType_3']
        fl_model['Cnty. Owned 2013'] = prox_model['CertificateHolderType_4']
        fl_model['Cnty. Owned 2012'] = prox_model['CertificateHolderType_5']
        fl_model['Cnty. Owned 2011'] = prox_model['CertificateHolderType_6']
        fl_model['Cnty. Owned 2010'] = prox_model['CertificateHolderType_7']
    elif platform.lower() == "wfbs":
        fl_model['Cnty. Owned 2016'] = prox_model['CertificateHolderType_1']
        fl_model['Cnty. Owned 2015'] = prox_model['CertificateHolderType_2']
        fl_model['Cnty. Owned 2014'] = prox_model['CertificateHolderType_3']
        fl_model['Cnty. Owned 2013'] = prox_model['CertificateHolderType_4']
        fl_model['Cnty. Owned 2012'] = prox_model['CertificateHolderType_5']
        fl_model['Cnty. Owned 2011'] = prox_model['CertificateHolderType_6']
        fl_model['Cnty. Owned 2010'] = prox_model['CertificateHolderType_7']
        fl_model['County_Land_Use'] = prox_model['ZoningUseCode']
        fl_model['County_Land_Use_Desc'] = prox_model['LandDescription']