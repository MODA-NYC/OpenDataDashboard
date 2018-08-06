import calendar
import requests
import datetime
import json
from datetime import datetime, timedelta, time

import pandas as pd
from sodapy import Socrata
import numpy as np

from credentials import socrata_key, socrata_pswd, socrata_username

request=Socrata('nycopendata.socrata.com', socrata_key,
               username=socrata_username,
               password=socrata_pswd)

ai_uid='r8cp-r4rc'
raw_data=request.get(ai_uid, limit=50000)

raw_df = pd.DataFrame(raw_data)

ai=raw_df.copy()

# reformatting data

ai.downloads=pd.to_numeric(ai.downloads)
ai.visits=pd.to_numeric(ai.visits)
ai.creation_date=pd.to_datetime(ai.creation_date,unit='s')
ai.last_update_date_data=pd.to_datetime(ai.last_update_date_data,unit='s')

# official, public, published assets (plus specific owners so assets correspond to DOITT's assets) (oppa)
oppa =ai[(ai.public=='true')&\
         (ai.provenance=='official')&\
         ((ai.owner=='NYC OpenData') |
         (ai.owner=='Vaughan Coleman')|
         (ai.owner=='Jose Beiro')|
         (ai.owner=='Ro Vernon')|
         (ai.owner=='NYCDOEOPenData')|
         (ai.owner=='Annette'))&\
         (ai.publication_stage=='published')].copy()

oppa.dropna(how='all',axis=1,inplace=True)

# assign time by update frequency
status_conditions = [
    (oppa['update_frequency']=='Weekly'),
    (oppa['update_frequency']=='Weekdays'),
    (oppa['update_frequency']=='Triannually'),
    (oppa['update_frequency']=='Several times per day'),
    (oppa['update_frequency']=='Daily'),
    (oppa['update_frequency']=='Quarterly'),
    (oppa['update_frequency']=='Monthly'),
    (oppa['update_frequency']=='Every four years'),
    (oppa['update_frequency']=='Biweekly'),
    (oppa['update_frequency']=='Bimonthly'),
    (oppa['update_frequency']=='Biannually') | (oppa['update_frequency']=='2 to 4 times per year'),
    (oppa['update_frequency']=='Annually'),
    (oppa['update_frequency']=='Historical Data') | (oppa['update_frequency']=='As needed')
]
status_choices=[pd.Timedelta('7 days'),pd.Timedelta('5 days'),pd.Timedelta('168 days'),pd.Timedelta('25 hours'),pd.Timedelta('47.9 hours'),pd.Timedelta('92 days'),pd.Timedelta('31 days'),pd.Timedelta('1459 days'),pd.Timedelta('84 hours'),pd.Timedelta('16 days'),pd.Timedelta('183 days'),pd.Timedelta('365 days'),pd.Timedelta('50000 days')]
oppa['update_threshold']=np.select(status_conditions, status_choices, default=pd.Timedelta('50000 days'))

# calculate when asset should have been last updated
oppa['update_delta'] = datetime.now()-ai.last_update_date_data

# assign status to automated, dictionary and geocoded columns
oppa['update_status']=np.where((oppa['update_delta']>=oppa['update_threshold']),'No','Yes')
oppa['automation']=np.where((oppa['automation']=='Yes'),'Automated','Manual')

# create asset status check dataframe
asset_status_check = oppa[['agency','name','update_frequency','automation','last_update_date_data','update_status','has_data_dictionary','geocoded']]
asset_status_check=asset_status_check.rename(index=str,columns={'agency':'Agency','name':'Asset Name','update_frequency':'Update Frequency','automation':'Update Method','last_update_date_data':'Last Updated','update_status':'Updated on Time?','has_data_dictionary':'Has Data Dictionary?','geocoded':'Is Geocoded?'})
asset_status_check=asset_status_check.to_dict('records')

#counts agency assets by "Automated" or "Manual"
automation_type_count = oppa.groupby(['agency','automation'])[['name']].count()
automation_type_count = automation_type_count.reset_index()
automation_type_count = pd.pivot_table(automation_type_count, index = 'agency', values = 'name', columns = ['automation'])
automation_type_count = automation_type_count.fillna(0)
automation_type_count = automation_type_count.reset_index()

# agency automated assets in bad update status 
automated_bad_status =oppa[(oppa.automation=="Automated")&\
         (oppa.update_status=='No')].copy()
automated_bad_status=automated_bad_status.groupby(['agency'])[['automation']].count()
automated_bad_status=automated_bad_status.reset_index()
automated_bad_status.columns=['agency','auto_bad_status']

# agency manual assets in good update status 
manual_bad_status = oppa[(oppa.automation=="Manual")&\
         (oppa.update_status=='No')].copy()
manual_bad_status=manual_bad_status.groupby(['agency'])[['automation']].count()
manual_bad_status=manual_bad_status.reset_index()
manual_bad_status.columns=['agency','manu_bad_status']

# count total assets by agency 
total_asset_count=oppa.groupby(['agency'])[['name']].count()
total_asset_count=total_asset_count.reset_index()
total_asset_count.columns=['agency','total_assets']

#join em all into a table!
concat_dfs=automation_type_count.join(automated_bad_status.set_index('agency'),on='agency')
concat_dfs=concat_dfs.join(manual_bad_status.set_index('agency'),on='agency')
concat_dfs=concat_dfs.join(total_asset_count.set_index('agency'),on='agency')
concat_dfs=concat_dfs.fillna(0)
concat_dfs['auto_perc_bad_status']=(concat_dfs.auto_bad_status/concat_dfs.Automated)
concat_dfs['manu_perc_bad_status']=(concat_dfs.manu_bad_status/concat_dfs.Manual)
concat_dfs=concat_dfs.fillna(0)
manual_bad_status.columns=['agency','manu_bad_status']


agency_status_check=concat_dfs[['agency','total_assets','Automated','auto_bad_status','Manual','manu_bad_status']]
agency_status_check=agency_status_check.rename(index=str,columns={'agency':'Agency','total_assets': 'Total Assets','Automated':'Automated','auto_bad_status':'A: Not Updated','Manual':'Manual','manu_bad_status':'M: Not Updated'})
agency_status_check=agency_status_check.to_dict('records')
