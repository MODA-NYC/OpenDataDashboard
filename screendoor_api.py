import json
import requests
from pandas.io.json import json_normalize
import datetime
from datetime import datetime, timedelta, time, date

import pandas as pd
import calendar
import numpy as np

from credentials import screendoor_key, screendoor_project_id

last_year = datetime.now().year - 1
this_month = datetime.now().month
last_12_months = datetime(last_year, this_month, 1)
last_12_months = last_12_months.strftime('%Y-%m-%d')

def call_screendoor_api():
	records = '10000'
	#read in the open data customer support requests using the screendoor api
	api_request = requests.get('https://screendoor.dobt.co/api/projects/'+screendoor_project_id+'/responses?per_page='+records+'&v=0&api_key='+screendoor_key)
	screendoor_raw_data = api_request.json()
	#create a dataframe
	screendoor_df = pd.DataFrame(screendoor_raw_data)
	return screendoor_df

def normalize_screendoor_data(screendoor_df):
	#extract the nested dictionary 'responses'
	normalize_responses = json_normalize(screendoor_df['responses'])
	#join both dataframs 
	concat_df = pd.concat([screendoor_df,normalize_responses], axis=1,join_axes=[screendoor_df.index])
	return concat_df

def format_screendoor_data(concat_df):
	#reformat data types
	concat_df.submitted_at = pd.to_datetime(concat_df.submitted_at,format='%Y-%m-%dT%H:%M:%S.%fZ')
	concat_df.updated_at = pd.to_datetime(concat_df.updated_at,format='%Y-%m-%dT%H:%M:%S.%fZ')
	concat_df['request_type'] = concat_df['fygvab39']
	
	#create new dataframe with only columns needed 
	screendoor_df = concat_df[['id','submitted_at','updated_at','request_type','status']].copy()

	#create new 'request_type_grouped' column
	status_conditions = [
	    (screendoor_df['request_type']=='Request a dataset'),
	    (screendoor_df['request_type']=='General inquiry'),
	    (screendoor_df['request_type']=='Ask a question about a dataset'),
	    (screendoor_df['request_type']=='Report an error in the data')
	]
	status_choices = ['Request a Dataset', 'General Inquiry', 'Data Question', 'Report Error']
	screendoor_df['request_type_grouped'] = np.select(status_conditions, status_choices, default='Other')

	#calculate amount of time between submission and last updated  
	screendoor_df['update_time'] = (screendoor_df.updated_at-screendoor_df.submitted_at) / np.timedelta64(1,'D')
	return screendoor_df

def group_requests_by_type_and_status(screendoor_df):
	#count requests by type and status (top groups)
	requests_by_status_grouped = screendoor_df[screendoor_df['submitted_at']>=last_12_months]
	requests_by_status_grouped = requests_by_status_grouped.groupby(['request_type_grouped','status'])[['id']].count().reset_index()
	return requests_by_status_grouped

def group_inquiries_by_month_and_type(screendoor_df):
	#count monthly submissions by type
	monthly_submissions = screendoor_df.groupby(['request_type_grouped', pd.Grouper(key='submitted_at', freq='M')])['id'].count().reset_index()
	monthly_submissions['submitted_at'] = monthly_submissions['submitted_at'].astype('datetime64[M]')
	monthly_submissions = monthly_submissions[monthly_submissions['submitted_at']>=last_12_months]
	return monthly_submissions

def calculate_average_resolution_time(screendoor_df):
	#calculate monthly update time by request type and week
	monthly_resolution_sum = screendoor_df.groupby(['request_type_grouped', pd.Grouper(key='submitted_at', freq='M')])['update_time'].sum().reset_index()
	monthly_resolution_sum['submitted_at'] = monthly_resolution_sum['submitted_at'].astype('datetime64[M]')
	monthly_resolution_sum = monthly_resolution_sum.rename(index=str,columns={'update_time':'monthly_update_time'})
	monthly_resolution_sum = monthly_resolution_sum[['monthly_update_time']]

	#calculate number of monthly submissions request type 
	monthly_resolution_count = screendoor_df.groupby(['request_type_grouped', pd.Grouper(key='submitted_at', freq='M')])['update_time'].count().reset_index()
	monthly_resolution_count['submitted_at'] = monthly_resolution_count['submitted_at'].astype('datetime64[M]')
	monthly_resolution_count = monthly_resolution_count.rename(index=str,columns={'update_time':'update_time_count'})

	#join monthly_resolution_sum and monthly_resolution_count to get average monthly resolution time per inquiry type
	monthly_resolution_time = pd.concat([monthly_resolution_sum,monthly_resolution_count], axis=1,join_axes=[monthly_resolution_count.index])
	monthly_resolution_time['average_resolution'] = (monthly_resolution_time['monthly_update_time'] / monthly_resolution_time['update_time_count']).round()
	monthly_resolution_time = monthly_resolution_time[monthly_resolution_time['submitted_at'] >= last_12_months]
	return monthly_resolution_time
