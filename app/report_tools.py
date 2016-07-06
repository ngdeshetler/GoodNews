def feature_elements(df,pos_rels=None,topics=None):
    pos_features={
        'location':None,
        'author_type':None,
        'original_reporting':False,
        'has_single_photo':False,
        'has_video':False,
        'real_time_reporting_breaking_news':False,
        'interactive_embeds':False,
        'major_social_promotion':False,
        'narrative_storytelling':False,
        'has_graphic':False,
        'has_multiple_photos':False,
        'analytic_voice':False,
        'pin_sourced':False,
        'text_type':None,
        'audio_type':None,
        'day':None
    }
    if pos_rels !=None:
        for fet in pos_rels.values():
            pos_features[fet]='relevance'
    top_ref={}
    if topics !=None:
        for fet in topics.keys():
            top_ref[fet.lower()]=fet
            pos_features[fet.lower()]=True



    features={}
    for fet in pos_features.keys():
        if pos_features[fet] == None:
            for level in list(set(df[fet])):
                features['C('+fet+', Sum)[S.'+level+']']={
                    'var':fet,
                    'value':level,
                    'name':(fet+': '+level).replace('_',' ').title()
                }
        elif not pos_features[fet]:
            features[fet]={
                'var':fet,
                'value':1,
                'name':fet.replace('_',' ').title()
            }
        elif pos_features[fet]==True:
        	 features[fet]={
                'var':fet,
                'value':1,
                'name':topics[top_ref[fet]].rstrip('\r\n')
            }
        else:
            features[fet]={
                'var':fet,
                'value':1,
                'name':(pos_features[fet]+': '+fet).replace('_',' ').title()
            }
            
    return features
    
def formula(pos_rels=None):
	formula = (" ~ C(location, Sum) + C(author_type, Sum) + original_reporting " 
	+ "+ has_single_photo + has_video + real_time_reporting_breaking_news "
	+ "+ interactive_embeds + major_social_promotion + narrative_storytelling "
	+ "+ has_graphic + has_multiple_photos + analytic_voice + pin_sourced "
	+ "+ C(text_type, Sum) + C(audio_type, Sum) + C(day, Sum)") 
	if pos_rels == None:
		return formula
	else:
		return formula + " + " + " + ".join(pos_rels.values()).lower()

def feature_calc(df,fet_dic,metric,cal='mean'):
	if cal=='mean':
		return df[metric][df[fet_dic['var']]==fet_dic['value']].mean()
	elif cal=='med':
	    return df[metric][df[fet_dic['var']]==fet_dic['value']].median()

def grand_cal(df,metric,cal='mean'):
	if cal=='mean':
		return df[metric].mean()
	elif cal=='med':
		return df[metric].median()
	elif cal=='max':
		return max(df[metric])

def dif_grand_cal(df,fet_dic,metric,cal='mean'):
	if cal=='mean':
		return ((df[metric][df[fet_dic['var']]==fet_dic['value']].mean() - df[metric].mean())/df[metric].mean())*100
	elif cal=='med':
		return ((df[metric][df[fet_dic['var']]==fet_dic['value']].median() - df[metric].median())/df[metric].median())*100

def get_param(index,model,log=True):
	if log:
		mul=100
	else:
		mul=1
	return model.params[index]*mul

def get_conf(index,model):
	return 1-model.pvalues[index]

def performance(param):
	if param>0:
		return "Strong Performer"
	else:
		return "Under Performer"

def class_code(param):
	if param>0:
		return "pos"
	else:
		return "neg"

def filter_features_indexes(model,p_val=.1,sort=True):
    import numpy as np
    if sort:
        indexes=np.argsort(model.params)[::-1].values
    else:
        indexes=len(model.params)
    indexes=[index for index in indexes if model.pvalues[index]<p_val] 
    indexes=[index for index in indexes if model.params.index[index] not in ['Intercept','pub_date_mean','pub_date_count']]
    return indexes


def scale(engage):
	maxx=max(engage)
	minn=min(engage)
	return [((x-minn)/(maxx-minn))*10 for x in engage]
