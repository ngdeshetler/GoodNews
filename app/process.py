           
def run_model_x(load_file,file_loc):
    import numpy as np
    import pandas as pd
    import os
    import scipy.linalg
    from statsmodels.formula.api import ols
    from patsy.contrasts import Sum
    from sklearn.decomposition import PCA
    from report_tools import formula
    import pickle
    from report_tools import *
    import datetime

    with open(os.path.join(file_loc,load_file)) as f:
        df, full_topic_names, pos_rels, main_metrics, main_metrics_readable, main_metrics_readable_bm = pickle.load(f)
	
    formula=formula(pos_rels=pos_rels)
    
    for m in main_metrics:
        df[m+'_log']=np.log10(df[m])
        df.loc[abs(df[m+'_log'])==np.inf,m+'_log']=0
        
    res_dic={}
    for metric in main_metrics:
        res_dic[metric] = ols(metric+'_log'+formula, data=df).fit()
    res_dic_tp={}
    for metric in main_metrics:
        res_dic_tp[metric] = ols(formula=(metric+"_log ~ " + ' + '.join(full_topic_names.keys()).lower()), data=df).fit()
    main_metrics_log=[metric+'_log' for metric in main_metrics]
    df_metrics=df[main_metrics_log]
	
    pca = PCA(n_components=1)
    df['engagement_ns']=pca.fit_transform(df_metrics)
	
    main_metrics.append('engagement')
    main_metrics_readable['engagement']='Engagement Score'
    main_metrics_readable_bm['Engagement Score']='engagement'
	
    res_dic['engagement'] = ols('engagement_ns'+formula, data=df).fit()
    res_dic_tp['engagement'] = ols(formula=("engagement_ns ~ " + ' + '.join(full_topic_names.keys()).lower()), data=df).fit()
    
    df['engagement']=scale(df['engagement_ns'])
    
    pickle_name='model'+'_' + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.pickle'
    
    with open(os.path.join(file_loc,pickle_name), 'w') as f:  # Python 3: open(..., 'wb')
        pickle.dump([df, full_topic_names, pos_rels, main_metrics, main_metrics_readable, main_metrics_readable_bm, res_dic, res_dic_tp], f) 

def run_features_x(load_file,file_loc,public_mode=False):
    from report_tools import *
    import pickle
    import pandas as pd
    import os
    import numpy as np
    from decimal import *
    import datetime
    
    dummy_names=["The Ethicist",
    "Education Innovation",
    "The Stone",
    "The Upshot",
    "Critic's Notebook",
    "Letter From America",
    "Sunday Review",
    "Modern Love",
    "Room for Debate",
    "N.Y.C. Events Guide",
    "Social Q's",
    "First Person",
    "T Magazine",
    "Campaign Stops",
    "On the Ground",
    "Taking Note",
    "Dot Earth",
    "First Draft",
    "The Ad Campaign",
    "On Washington",
    "News Analysis",
    "Bits",
    "State of the Art"]
    
    np.random.shuffle(dummy_names)
    
    with open(os.path.join(file_loc,load_file)) as f:
        df, full_topic_names, pos_rels, main_metrics, main_metrics_readable, main_metrics_readable_bm, res_dic, res_dic_tp = pickle.load(f)

    fe=feature_elements(df,pos_rels=pos_rels,topics=full_topic_names)
    
    table_data={}
    table_data_tp={}
    for m in main_metrics:
        print 'Creating Features'
        model=res_dic[m]
        indexes=filter_features_indexes(model)
        features=[]
        mean_ref=[]
        ii=0
        for i in (indexes):
    	    fet_dic=fe[model.params.index[i]]
    	    if public_mode:
    	        name=dummy_names[ii]
    	        ii+=1
    	        mean=round(Decimal(feature_calc(df,fet_dic,m)/grand_cal(df,m,cal='max')),3)
    	        med=round(Decimal(feature_calc(df,fet_dic,m,cal='med')/grand_cal(df,m,cal='max')),3)
    	        param=round(Decimal(get_param(i,model,log=(m!='engagement'))/max(model.params)),3)
    	    else:
    	        name=fet_dic['name']
    	        mean=round(Decimal(feature_calc(df,fet_dic,m)),3)
    	        med=round(Decimal(feature_calc(df,fet_dic,m,cal='med')),3)
    	        param=round(Decimal(get_param(i,model,log=(m!='engagement'))),3)
            features.append(dict(
                            name=name,
                            mean=mean,
                            med=med,
                            dif=round(Decimal(dif_grand_cal(df,fet_dic,m)),3),
                            param=param,
                            pval=round(Decimal(get_conf(i,model)),3),
                            per=performance(model.params[i]),
                            clas=class_code(dif_grand_cal(df,fet_dic,m))
            ))
            mean_ref.append(round(Decimal(feature_calc(df,fet_dic,m)),3))
        table_data[m]=[features[i] for i in np.argsort(mean_ref)[::-1]]
        
        model=res_dic_tp[m]
        indexes=filter_features_indexes(model)
        features=[]
        mean_ref=[]
        ii=0
        for i in (indexes):
    	    fet_dic=fe[model.params.index[i]]
    	    if public_mode:
    	        name=dummy_names[ii]
    	        ii+=1
    	        mean=round(Decimal(feature_calc(df,fet_dic,m)/grand_cal(df,m,cal='max')),3)
    	        med=round(Decimal(feature_calc(df,fet_dic,m,cal='med')/grand_cal(df,m,cal='max')),3)
    	        param=round(Decimal(get_param(i,model,log=(m!='engagement'))/max(model.params)),3)
    	    else:
    	        name=fet_dic['name']
    	        mean=round(Decimal(feature_calc(df,fet_dic,m)),3)
    	        med=round(Decimal(feature_calc(df,fet_dic,m,cal='med')),3)
    	        param=round(Decimal(get_param(i,model,log=(m!='engagement'))),3)
            features.append(dict(
                            name=name,
                            mean=mean,
                            med=med,
                            dif=round(Decimal(dif_grand_cal(df,fet_dic,m)),3),
                            param=param,
                            pval=round(Decimal(get_conf(i,model)),3),
                            per=performance(model.params[i]),
                            clas=class_code(dif_grand_cal(df,fet_dic,m))
            ))
            mean_ref.append(round(Decimal(feature_calc(df,fet_dic,m)),3))
        
        
        table_data_tp[m]=[features[i] for i in np.argsort(mean_ref)[::-1]]
    
    pickle_name='table'+'_' + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.pickle'
    with open(os.path.join(file_loc,pickle_name), 'w') as f:  # Python 3: open(..., 'wb')
        pickle.dump([df, main_metrics, main_metrics_readable,table_data, table_data_tp ], f) 
        
    os.remove(os.path.join(file_loc,load_file))

    
