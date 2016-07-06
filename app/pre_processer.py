def pre_processer(loc_in,loc_out):
 ## Import main dataframe
    from preproc import *
    import pickle
    import pandas as pd
    import os
    from glob import glob
    import shutil
    import numpy as np
    import datetime
    
    print os.path.join(loc_in,"fullData.csv")
    int_df = pd.read_csv(os.path.join(loc_in,"fullData.csv").decode('utf-8'))

	## Get topic names from csv file names
    dirlist = os.listdir(loc_in)
    topics=[x[:-4] for x in dirlist if (x[-4:]=='.csv' and x!='fullData.csv')]

	## Remove extranious symbols from column names
    int_df.columns = int_df.columns.str.replace(' ','_').str.translate(None, ''.join(remove_symbols())).str.lower()
    int_df["headline_clean"]=int_df.headline.apply(clean_headline)
   
	## Load in all of the topic specific cvs files (which contain extra metrics not included in fullData.csv)
    topic_df_dic={}
    full_topic_names={}
    for topic in topics:
        print os.path.join(loc_in,topic + ".csv")
        df_temp=pd.read_csv(os.path.join(loc_in,topic + ".csv").decode('utf-8'), index_col=False, skiprows=find_start(os.path.join(loc_in,topic + ".csv"),'Articles')-1)
        full_topic_names[topic]=find_name(os.path.join(loc_in,topic + ".csv"),'Content: Tagged topic as ')
        df_temp[topic]=[1 for x in range(len(df_temp))]
        df_temp.columns = df_temp.columns.str.replace(' ','_').str.translate(None, ''.join(remove_symbols())).str.lower()
        df_temp["headline_clean"]=df_temp.articles.apply(clean_headline)
        df_temp.set_index(df_temp["headline_clean"], inplace = True)
        topic_df_dic[topic] = df_temp
	
    ## Merge all topic dataframes into one
    df_all_topics=merge_topics_df(topic_df_dic,int_df["headline_clean"],get_cols(topic_df_dic))

	## Remove repeats in both dataframe
    int_df=remove_rep_rows(int_df)
    df_all_topics=remove_rep_rows(df_all_topics,metric='total_views')

	## Merge two dataframes
    df=pd.merge(int_df, df_all_topics, on='headline_clean')

    ## Clean data and create extra parameters
    df["day"]=df.pub_date.apply(day_of_week)
    df["day_num"]=df.pub_date.apply(day_of_week_num)
    df=df.applymap(binariz_yn)
    df['read_time_correct'] = df.apply(correct, axis=1)
    df=fix_nans(df,fun=fix_nan)
    df, pos_rels=break_and_make(df,'relevance',remove_symbols())
    df=same_day_metrics(df,'total_views')

    ## 
    main_metrics, main_metrics_readable, main_metrics_readable_bm = default_metrics()
    for m in main_metrics:
        df[m+'_log']=np.log10(df[m])
        df.loc[abs(df[m+'_log'])==np.inf,m+'_log']=0
    
    all_files=os.listdir(loc_out)
    for f in all_files:
        if f != '.DS_Store':
    	    shutil.move(os.path.join(loc_out,f),os.path.join(loc_out,'old'))
    
    pickle_name='data'+'_' + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.pickle'
    
    with open(os.path.join(loc_out,pickle_name), 'w') as f:  # Python 3: open(..., 'wb')
        pickle.dump([df, full_topic_names, pos_rels, main_metrics, main_metrics_readable, main_metrics_readable_bm], f) 
    
    os.remove(os.path.join(loc_in,"fullData.csv"))
    for topic in topics:
        os.remove(os.path.join(loc_in,topic + ".csv"))
    