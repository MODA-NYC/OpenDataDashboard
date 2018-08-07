import pandas as pd
from ga_functions import return_ga_data


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

def load_sources():
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


def cast_ga_data(ga_data):
    # TODO: move this into load_ga_data in the DataFrame
    ga_data['ga:users'] = pd.to_numeric(ga_data['ga:users'])
    ga_data['ga:newUsers'] = pd.to_numeric(ga_data['ga:newUsers'])
    ga_data['ga:sessions'] = pd.to_numeric(ga_data['ga:sessions'])
    ga_data['ga:pageviews'] = pd.to_numeric(ga_data['ga:pageviews'])
    ga_data['ga:date'] = pd.to_datetime(ga_data['ga:date'],format='%Y%m%dT%')
    return ga_data


#create usp dataframe and reformat data types
def make_usp(ga_data, freq='d'):
    usp = ga_data.groupby(pd.Grouper(key='ga:date', freq=freq)).sum()
    usp = usp.reset_index()
    usp['bounce_rate'] = usp['ga:bounces'] / usp['ga:sessions']
    return usp

def make_sources (sources, start_date='20180714', end_date='20180724'):
    """Create sources dataframe and reformate data types."""
    sources_df = sources.copy()
    sources_df['ga:users'] = pd.to_numeric(sources_df['ga:users'])
    # warning this assumes a certian static date range might cause problems down the line
    sources_df = sources_df[sources_df['ga:date'] > start_date]
    sources_df = sources_df[sources_df['ga:date'] < end_date]
    return sources_df

