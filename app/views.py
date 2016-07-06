from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from app import app
from preproc import *
from report_tools import *
from process import *
import pickle
import sqlalchemy
import pandas as pd
from flask import send_from_directory
import os
from glob import glob
import shutil
import numpy as np
import datetime
from decimal import *

public_mode=True

UPLOAD_FOLDER_RAW = os.path.dirname(os.path.realpath(__file__))+'/raw/'
UPLOAD_FOLDER_EDIT = os.path.dirname(os.path.realpath(__file__))+'/edit/'
ALLOWED_EXTENSIONS = set(['csv','CSV'])


app.config['UPLOAD_RAW_DEST'] = UPLOAD_FOLDER_RAW
app.config['UPLOAD_EDIT_DEST'] = UPLOAD_FOLDER_EDIT
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER_RAW

# check file is ok
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
                           
def pickle_name(type):
    return type+'_' + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.pickle'

def most_recent(pick_files):
    mod_time=[os.path.getmtime(os.path.join(app.config['UPLOAD_EDIT_DEST'],file)) for file in pick_files]
    order=np.argsort(mod_time)[::-1]
    return pick_files[order[0]], [pick_files[x] for x in order]

def run_model(all_files):
    print 'Running Model'
    # Load in most recent uploads:
    data_files=[x for x in all_files if (x[-7:]=='.pickle' and x[:4]=='data')]
    if not data_files:
        return render_template("review_input.html")
    load_file, ordered_files=most_recent(data_files)
    print load_file
    
    run_model_x(load_file,app.config['UPLOAD_EDIT_DEST'])

def run_features(all_files):
    model_files=[x for x in all_files if (x[-7:]=='.pickle' and x[:5]=='model')]
    if not model_files:	
        run_model(all_files)
        all_files=os.listdir(app.config['UPLOAD_EDIT_DEST'])
        model_files=[x for x in all_files if (x[-7:]=='.pickle' and x[:5]=='model')]
    load_file, ordered_files=most_recent(model_files)
    print load_file
    
    run_features_x(load_file,app.config['UPLOAD_EDIT_DEST'],public_mode)

def load_files():
    all_files=os.listdir(app.config['UPLOAD_EDIT_DEST'])
    report_files=[x for x in all_files if (x[-7:]=='.pickle' and x[:5]=='table')]
    if not report_files:	
        run_features(all_files)
        all_files=os.listdir(app.config['UPLOAD_EDIT_DEST'])
        report_files=[x for x in all_files if (x[-7:]=='.pickle' and x[:5]=='table')]
        
    load_file, ordered_files=most_recent(report_files)
    print load_file
    global df
    global main_metrics
    global main_metrics_readable
    global table_data
    global table_data_tp
    with open(os.path.join(app.config['UPLOAD_EDIT_DEST'],load_file)) as f:
        df, main_metrics, main_metrics_readable, table_data, table_data_tp = pickle.load(f)
    
@app.route('/')   
@app.route('/welcome')    
def welcome():
    return render_template("welcome.html")


@app.route('/report')    
def report():
    load_files()
    
    metric='engagement'
    if public_mode:
        grand_mean=grand_cal(df,metric,cal='mean')/grand_cal(df,metric,cal='max')
    else:
        grand_mean=grand_cal(df,metric,cal='mean')
    
    return render_template("e_general.html", features=table_data[metric], metric=main_metrics_readable[metric], grand_mean=grand_mean)

##
@app.route('/e_general')
def e_general():
    if 'table_data' not in globals():
        load_files()
    
    metric='engagement'
    if public_mode:
        grand_mean=grand_cal(df,metric,cal='mean')/grand_cal(df,metric,cal='max')
    else:
        grand_mean=grand_cal(df,metric,cal='mean')
    return render_template("e_general.html", features=table_data[metric], metric=main_metrics_readable[metric], grand_mean=grand_mean)

@app.route('/e_topics')
def e_topics():
    if 'table_data' not in globals():
        load_files()
        
    metric='engagement'
    if public_mode:
        grand_mean=grand_cal(df,metric,cal='mean')/grand_cal(df,metric,cal='max')
    else:
        grand_mean=grand_cal(df,metric,cal='mean')
    return render_template("e_topics.html", features=table_data_tp[metric], metric=main_metrics_readable[metric], grand_mean=grand_mean)

##
@app.route('/vis_general')
def vis_general():
    if 'table_data' not in globals():
        load_files()
        
    metric='total_views'
    if public_mode:
        grand_mean=grand_cal(df,metric,cal='mean')/grand_cal(df,metric,cal='max')
    else:
        grand_mean=grand_cal(df,metric,cal='mean')
    return render_template("vis_general.html", features=table_data[metric], metric=main_metrics_readable[metric], grand_mean=grand_mean)

@app.route('/vis_topics')
def vis_topics():
    if 'table_data' not in globals():
        load_files()
        
    metric='total_views'
    if public_mode:
        grand_mean=grand_cal(df,metric,cal='mean')/grand_cal(df,metric,cal='max')
    else:
        grand_mean=grand_cal(df,metric,cal='mean')
    return render_template("vis_topics.html", features=table_data_tp[metric], metric=main_metrics_readable[metric], grand_mean=grand_mean)

##
@app.route('/vor_general')
def vor_general():
    if 'table_data' not in globals():
        load_files()
        
    metric='visitors'
    if public_mode:
        grand_mean=grand_cal(df,metric,cal='mean')/grand_cal(df,metric,cal='max')
    else:
        grand_mean=grand_cal(df,metric,cal='mean')
    return render_template("vor_general.html", features=table_data[metric], metric=main_metrics_readable[metric], grand_mean=grand_mean)

@app.route('/vor_topics')
def vor_topics():
    if 'table_data' not in globals():
        load_files()
        
    metric='visitors'
    if public_mode:
        grand_mean=grand_cal(df,metric,cal='mean')/grand_cal(df,metric,cal='max')
    else:
        grand_mean=grand_cal(df,metric,cal='mean')
    return render_template("vor_topics.html", features=table_data_tp[metric], metric=main_metrics_readable[metric], grand_mean=grand_mean)

##
@app.route('/r_general')
def r_general():
    if 'table_data' not in globals():
        load_files()
        
    metric='read_time_correct'
    if public_mode:
        grand_mean=grand_cal(df,metric,cal='mean')/grand_cal(df,metric,cal='max')
    else:
        grand_mean=grand_cal(df,metric,cal='mean')
    return render_template("r_general.html", features=table_data[metric], metric=main_metrics_readable[metric], grand_mean=grand_mean)

@app.route('/r_topics')
def r_topics():
    if 'table_data' not in globals():
        load_files()
        
    metric='read_time_correct'
    if public_mode:
        grand_mean=grand_cal(df,metric,cal='mean')/grand_cal(df,metric,cal='max')
    else:
        grand_mean=grand_cal(df,metric,cal='mean')
    return render_template("r_topics.html", features=table_data_tp[metric], metric=main_metrics_readable[metric], grand_mean=grand_mean)

##
@app.route('/s_general')
def s_general():
    if 'table_data' not in globals():
        load_files()
        
    metric='all_shares'
    if public_mode:
        grand_mean=grand_cal(df,metric,cal='mean')/grand_cal(df,metric,cal='max')
    else:
        grand_mean=grand_cal(df,metric,cal='mean')
    return render_template("s_general.html", features=table_data[metric], metric=main_metrics_readable[metric], grand_mean=grand_mean)

@app.route('/s_topics')
def s_topics():
    if 'table_data' not in globals():
        load_files()
        
    metric='all_shares'
    if public_mode:
        grand_mean=grand_cal(df,metric,cal='mean')/grand_cal(df,metric,cal='max')
    else:
        grand_mean=grand_cal(df,metric,cal='mean')
    return render_template("s_topics.html", features=table_data_tp[metric], metric=main_metrics_readable[metric], grand_mean=grand_mean)

##
@app.route('/c_general')
def c_general():
    if 'table_data' not in globals():
        load_files()
        
    metric='comments'
    if public_mode:
        grand_mean=grand_cal(df,metric,cal='mean')/grand_cal(df,metric,cal='max')
    else:
        grand_mean=grand_cal(df,metric,cal='mean')
    return render_template("c_general.html", features=table_data[metric], metric=main_metrics_readable[metric], grand_mean=grand_mean)

@app.route('/c_topics')
def c_topics():
    if 'table_data' not in globals():
        load_files()
        
    metric='comments'
    if public_mode:
        grand_mean=grand_cal(df,metric,cal='mean')/grand_cal(df,metric,cal='max')
    else:
        grand_mean=grand_cal(df,metric,cal='mean')
    return render_template("c_topics.html", features=table_data_tp[metric], metric=main_metrics_readable[metric], grand_mean=grand_mean)

@app.route('/engage_score')
def engage_score():
    return render_template('engage_score.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/input',methods=['GET','POST'])
def upload_file():
    return render_template('input.html')

@app.route('/uploads/<id>')
def show(id):
    return send_from_directory('/Users/Natalie/Documents/Insight/KPCC/KPCC_MfN/app/raw/', id)
    
@app.route('/output',methods=['POST'])
def pre_process():
    from pre_processer import *
    uploaded_files = request.files.getlist("file[]")
    
    for file in uploaded_files:
		if file and allowed_file(file.filename):
			filename=file.filename
			file.save(os.path.join(app.config['UPLOAD_RAW_DEST'],filename))
			print filename
		print 'filename: ' + filename
    pre_processer(app.config['UPLOAD_RAW_DEST'],app.config['UPLOAD_EDIT_DEST'])
   
    return render_template("output.html")

@app.route('/gif/<id>')
def show_loading(id):
    return send_from_directory('/static/images', "loading.gif")
    