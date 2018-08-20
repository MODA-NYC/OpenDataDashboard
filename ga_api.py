import datetime
from datetime import datetime, timedelta, time, date

import pandas as pd

from ga_functions import return_ga_data


last_year = datetime.now().year-1
this_month = datetime.now().month
last_12_months = datetime(last_year, this_month, 1)
last_12_months = last_12_months.strftime('%Y-%m-%d')


#collect users, sessions, pageviews (usp) from google analytics api
def load_ga_data ():
  return pd.DataFrame(return_ga_data(
      start_date='2017-09-21',
      end_date='today',
      view_id='82639170',
      metrics=[
        {'expression': 'ga:users'},
        {'expression': 'ga:newUsers'},
        {'expression': 'ga:sessions'},
        {'expression': 'ga:pageviews'},
        {'expression': 'ga:bounces'}
      ],
      dimensions=[
        {'name': 'ga:date'},
      ],
      split_dates=False,  
    ))

# user sources from google analytics api

def load_sources_data():
  return pd.DataFrame(return_ga_data(
      start_date='2017-09-21',
      end_date='today',
      view_id='82639170',
      metrics=[
        {'expression': 'ga:users'},
      ],
      dimensions=[
        {'name': 'ga:channelGrouping'},
        {'name': 'ga:date'},
      ],
      split_dates=False,  
    ))


def cast_ga_data(usp_data):
    # TODO: move this into load_ga_data in the DataFrame
    usp_data['ga:users'] = pd.to_numeric(usp_data['ga:users'])
    usp_data['ga:newUsers'] = pd.to_numeric(usp_data['ga:newUsers'])
    usp_data['ga:sessions'] = pd.to_numeric(usp_data['ga:sessions'])
    usp_data['ga:pageviews'] = pd.to_numeric(usp_data['ga:pageviews'])
    usp_data['ga:bounces'] = pd.to_numeric(usp_data['ga:bounces'])
    usp_data['ga:date'] = pd.to_datetime(usp_data['ga:date'],format='%Y%m%d')
    return usp_data

def cast_sources_data(sources_data):
    # TODO: move this into load_ga_data in the DataFrame
    sources_data['ga:users'] = pd.to_numeric(sources_data['ga:users'])
    sources_data['ga:date'] = pd.to_datetime(sources_data['ga:date'],format='%Y%m%d')
    return sources_data


#create usp dataframe and reformat data types
def make_usp(usp_data, freq='d'):
    usp = usp_data.groupby(pd.Grouper(key='ga:date', freq=freq)).sum()
    usp = usp.reset_index()
    usp['bounce_rate'] = usp['ga:bounces'] / usp['ga:sessions']
    return usp

def make_sources (sources_data):
    """Create sources dataframe and reformate data types."""
    sources = sources_data.groupby(['ga:channelGrouping', pd.Grouper(key='ga:date', freq='M')]).sum().reset_index()
    sources['ga:date'] = sources['ga:date'].astype('datetime64[M]')
    return sources

