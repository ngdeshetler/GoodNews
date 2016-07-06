## Preprocessing functions:

def find_start(filename,lookup):
    with open(filename) as myFile:
        for num, line in enumerate(myFile, 1):
            if lookup in line:
                return num

def find_name(filename,lookup):
    with open(filename) as myFile:
        for num, line in enumerate(myFile, 1):
            if lookup in line:
                return line.split(lookup)[1]
                
def remove_symbols():
	return ['/','(',')',"'",'"']
	

def clean_headline(s):
	import string
	printable = set(string.printable)
	return ''.join(filter(lambda x: x in printable, s))
    
def get_cols(dff_dic):
	holder=[]
	for dff in dff_dic.values():
		for name in dff.columns.tolist():
			holder.append(name)
	return set(holder)

def merge_topics_df(dff_dic,indexs,cols):
	import pandas as pd
	df_all_topics=pd.DataFrame(index=indexs, columns=cols)
	for dff in dff_dic.values():
		df_all_topics=df_all_topics.combine_first(dff)
	df_all_topics=df_all_topics.fillna(0)
	df_all_topics.set_index(pd.Index(range(len(df_all_topics))), inplace = True)
	return df_all_topics


def remove_rep_rows(dff,metric='views'):
	import pandas as pd
	from collections import Counter
	reps=[k for k,v in Counter(dff['headline_clean'].values).items() if v>1]
	for rep in reps:
		where_reps=dff[dff['headline_clean']==rep].index.tolist()
		max_value = max(dff.loc[where_reps,[metric]].values)
		found_max=False
		for where in where_reps:
			if (dff.loc[where,[metric]].values==max_value and not found_max):
				where_reps.remove(where)
				found_max=True
		dff.drop(where_reps,inplace=True)
	return dff

## Get day of the week but as a string and number
def day_of_week(date_str):
	import datetime
	return datetime.datetime.strptime(date_str, '%m/%d/%Y').strftime('%A')

def day_of_week_num(date_str):
	import datetime
	return datetime.datetime.strptime(date_str, '%m/%d/%Y').isoweekday()
    
## Converts yes/no into 1/0
def binariz_yn(val):
    if str(val).lower()=='yes':
        return 1
    elif str(val).lower()=='no':
        return 0
    return val

## Weights view time by word count
def correct(row):
    return (row['avg_view_time']*60) / row['word_count']
    
    
## Replaces nans from data points not assigned a lable with NotOtherwiseSpecified
def fix_nan(i):
	import numpy as np
	if (type(i) is float and np.isnan(i)):
		return 'NOS'
	return i

## Only applies fix_nan to columns with NaNs
def fix_nans(dff,fun=fix_nan):
	import numpy as np
	for col in dff.columns:
		temp_set = list(set(dff[col]))
		if sum([1 for i in temp_set if (type(i) is float and np.isnan(i))])>=1:
			dff[col]=dff[col].apply(fix_nan)
	return dff
    
def break_and_make(dff,col_name,rem_symb):
	pos_rels={}
	for index, row in dff.iterrows():
		for rel_part in row[col_name].split(' and '):
			if rel_part not in pos_rels.keys():
				pos_rels[rel_part]=rel_part.replace(' ','_').translate(None, ''.join(rem_symb)).replace('__','_').lower()
				dff[pos_rels[rel_part]]=0
			dff.loc[index,[pos_rels[rel_part]]]=1
	return dff, pos_rels

def same_day_metrics(dff,metric):
	a=dff.groupby('pub_date')[metric].agg(['mean', 'count'])
	a=a.rename(columns={'mean': 'pub_date_mean', 'count': 'pub_date_count'})
	return dff.join(a, on='pub_date',rsuffix='_pub_date_'+metric)

def default_metrics():
	metrics=['total_views','read_time_correct','all_shares','visitors','comments']
	readable={'total_views':'Total Views','read_time_correct':'Average Read Time',
    	                   'all_shares':'Social Media Shares','visitors':'Total Visitors','comments':'Comments'}
	readable_bm = dict (zip(readable.values(),readable.keys()))
	return metrics, readable, readable_bm


def log_tran_metrics(dff,metrics):
	for m in metrics:
		dff[m+'_log']=np.log10(dff[m])
		dff.loc[abs(dff[m+'_log'])==np.inf,m+'_log']=0
	return dff

def scale(engage):
	maxx=max(engage)
	minn=min(engage)
	return [((x-minn)/(maxx-minn))*10 for x in engage]