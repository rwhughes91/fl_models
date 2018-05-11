
def supplemental_df_gen(supplemental_model, fl_model):
    col = "CER_TYPE"
    columns = [col + str(i) for i in range(1, 8)]
    subset = supplemental_model.loc[:, ['ADV_NUM'] + columns]

    proxy_model_supp = fl_model[['Adv No.']].copy()
    proxy_model_supp = proxy_model_supp.merge(subset, how="left", left_on='Adv No.', right_on="ADV_NUM")

    return proxy_model_supp


