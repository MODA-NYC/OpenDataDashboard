from datetime import datetime as dt
from datetime import timedelta

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import dash_table_experiments as dte

import ga_api as ga_helpers
import socrata_api as socrata_helpers
import screendoor_api as screendoor_helpers

"""Import functions and variables from API files"""
#Google Analytics API
usp_data = ga_helpers.load_ga_data()
usp_data = ga_helpers.cast_ga_data(usp_data)
sources_data = ga_helpers.load_sources_data()
sources_data = ga_helpers.cast_sources_data(sources_data)
usp_daily = ga_helpers.make_usp(usp_data, freq='d')
usp_weekly = ga_helpers.make_usp(usp_data, freq='W')
usp_monthly = ga_helpers.make_usp(usp_data, freq='M')
sources_monthly = ga_helpers.make_sources(sources_data)
print('finished google analytics api')

#Socrata Analytics API
socrata_data = socrata_helpers.call_socrata_api()
socrata_data = socrata_helpers.create_main_dataframe(socrata_data)
socrata_data = socrata_helpers.assign_dataframe_statuses(socrata_data)
asset_status_check = socrata_helpers.create_asset_status_check(socrata_data)
agency_status_check = socrata_helpers.create_agency_status_check(socrata_data)
print('finished socrata analytics api')

#Screendoor Analytics API
screendoor_data = screendoor_helpers.call_screendoor_api()
screendoor_data = screendoor_helpers.normalize_screendoor_data(screendoor_data)
screendoor_data = screendoor_helpers.format_screendoor_data(screendoor_data)
requests_by_status_grouped = screendoor_helpers.group_requests_by_type_and_status(screendoor_data)
monthly_submissions = screendoor_helpers.group_inquiries_by_month_and_type(screendoor_data)
monthly_resolution_time = screendoor_helpers.calculate_average_resolution_time(screendoor_data)
print('finished screendoor analytics api')


"""Dashboard variables"""

#Dates for filtering and 'last updated'
today_string = dt.today().strftime('%B %d, %Y')
today = dt.today().strftime('%Y-%m-%d')
ga_date = usp_daily[(usp_daily['ga:date'] >= (dt.today()-timedelta(days=8))) & (usp_daily['ga:date'] <= (dt.today()-timedelta(days=1)))]

#Traces for Inquiry Type 
trace1_inquiry = go.Bar(
  x=monthly_submissions[monthly_submissions['request_type_grouped'] == 'Other']['submitted_at'],
  y=monthly_submissions[monthly_submissions['request_type_grouped'] == 'Other']['id'],
  marker={'color':'#d64132'},
  name='Other'
)
trace2_inquiry = go.Bar(
  x=monthly_submissions[monthly_submissions['request_type_grouped'] == 'Report Error']['submitted_at'],
  y=monthly_submissions[monthly_submissions['request_type_grouped'] == 'Report Error']['id'],
  marker={'color':'#57b4dd'},
  name='Report Error'
)
trace3_inquiry = go.Bar(
  x=monthly_submissions[monthly_submissions['request_type_grouped'] == 'Request a Dataset']['submitted_at'],
  y=monthly_submissions[monthly_submissions['request_type_grouped'] == 'Request a Dataset']['id'],
  marker={'color':'#6c648b'},
  name='Request a Dataset'
)
trace4_inquiry = go.Bar(
  x=monthly_submissions[monthly_submissions['request_type_grouped'] == 'General Inquiry']['submitted_at'],
  y=monthly_submissions[monthly_submissions['request_type_grouped'] == 'General Inquiry']['id'],
  marker={'color':'#f5bd40'},
  name='General Inquiry'
)
trace5_inquiry = go.Bar(
  x=monthly_submissions[monthly_submissions['request_type_grouped'] == 'Data Question']['submitted_at'],
  y=monthly_submissions[monthly_submissions['request_type_grouped'] == 'Data Question']['id'],
  marker={'color':'#248038'},
  name='Data Question'
)

#Traces for Average Monthly Inquiry Resolution Time
trace1_resolution = go.Scatter(
  x=monthly_resolution_time[monthly_resolution_time['request_type_grouped'] == 'Data Question']['submitted_at'],
  y=monthly_resolution_time[monthly_resolution_time['request_type_grouped'] == 'Data Question']['average_resolution'], 
  line={'color':'#248038', 'width': 4},
  mode='lines',
  name='Data Question'
)
trace2_resolution = go.Scatter(
  x=monthly_resolution_time[monthly_resolution_time['request_type_grouped'] == 'General Inquiry']['submitted_at'],
  y=monthly_resolution_time[monthly_resolution_time['request_type_grouped'] == 'General Inquiry']['average_resolution'],
  line={'color':'#f5bd40', 'width': 4},
  mode='lines',
  name='General Inquiry'
)
trace3_resolution = go.Scatter(
  x=monthly_resolution_time[monthly_resolution_time['request_type_grouped'] == 'Request a Dataset']['submitted_at'],
  y=monthly_resolution_time[monthly_resolution_time['request_type_grouped'] == 'Request a Dataset']['average_resolution'],
  line={'color':'#6c648b', 'width': 4},
  mode='lines',
  name='Request a Dataset'
)
trace4_resolution = go.Scatter(
  x=monthly_resolution_time[monthly_resolution_time['request_type_grouped'] == 'Report Error']['submitted_at'],
  y=monthly_resolution_time[monthly_resolution_time['request_type_grouped'] == 'Report Error']['average_resolution'],
  line={'color':'#57b4dd', 'width': 4},
  mode='lines',
  name='Report Error'
)
trace5_resolution = go.Scatter(
  x=monthly_resolution_time[monthly_resolution_time['request_type_grouped'] == 'Other']['submitted_at'],
  y=monthly_resolution_time[monthly_resolution_time['request_type_grouped'] == 'Other']['average_resolution'],
  line={'color':'#d64132', 'width': 4},
  mode='lines',
  name='Other'
)

#Traces for Screendoor
trace1_status = go.Bar(
    x=requests_by_status_grouped[requests_by_status_grouped['status'] == 'Closed']['request_type_grouped'],
    y=requests_by_status_grouped[requests_by_status_grouped['status'] == 'Closed']['id'],
    marker={'color':'#57B4DD'},
    name='Closed'
)
trace2_status = go.Bar(
    x=requests_by_status_grouped[requests_by_status_grouped['status'] == 'Pending']['request_type_grouped'],
    y=requests_by_status_grouped[requests_by_status_grouped['status'] == 'Pending']['id'],
    marker={'color':'#F5BD40'},
    name='Pending'
)
trace3_status = go.Bar(
    x=requests_by_status_grouped[requests_by_status_grouped['status'] == 'Open']['request_type_grouped'],
    y=requests_by_status_grouped[requests_by_status_grouped['status'] == 'Open']['id'],
    marker={'color':'#D64312'},
    name='Open'
)

#Traces for Google Analytics Acquisition
trace1_source = go.Bar(
  x=sources_monthly[sources_monthly['ga:channelGrouping']=='Email']['ga:date'],
  y=sources_monthly[sources_monthly['ga:channelGrouping']=='Email']['ga:users'],
  marker={'color':'#201f2f'},
  name='Email'
)
trace2_source = go.Bar(
  x=sources_monthly[sources_monthly['ga:channelGrouping']=='Social']['ga:date'],
  y=sources_monthly[sources_monthly['ga:channelGrouping']=='Social']['ga:users'],
  marker={'color':'#e25d99'},
  name='Social'
)
trace3_source = go.Bar(
  x=sources_monthly[sources_monthly['ga:channelGrouping']=='Direct']['ga:date'],
  y=sources_monthly[sources_monthly['ga:channelGrouping']=='Direct']['ga:users'],
  marker={'color':'#F5BD40'},
  name='Direct'
)
trace4_source = go.Bar(
  x=sources_monthly[sources_monthly['ga:channelGrouping']=='Referral']['ga:date'],
  y=sources_monthly[sources_monthly['ga:channelGrouping']=='Referral']['ga:users'],
  marker={'color':'#ed7b14'},
  name='Referral'
)
trace5_source = go.Bar(
  x=sources_monthly[sources_monthly['ga:channelGrouping']=='Organic Search']['ga:date'],
  y=sources_monthly[sources_monthly['ga:channelGrouping']=='Organic Search']['ga:users'],
  name='Organic Search',
  marker={'color':'#104177'},
)

"""Generate Socrata tables"""
def generate_table(dataframe, max_rows=1000):
  return html.Table(
    # Header
    [html.Tr([html.Th(col) for col in dataframe.columns])] +
    # Body
    [html.Tr([
      html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
    ]) for i in range(min(len(dataframe), max_rows))]
  )

"""Dash Layout"""
app = dash.Dash()
app.layout = html.Div([

  html.Div(
    className = 'row',
    children = [
      html.Div(
        className = 'ten columns',
        children = [
          html.H2(
            children='Open Data Dashboard'
          )
        ]
      ),   
      html.Div(
        className = 'two columns',
        children = [
          html.P(
            children='Updated as of ' + today_string
          )
        ]
      )
    ]
  ),


  html.Div(
    className = 'row',
    children = [
      dcc.Markdown('###### This dashboard is meant to help support the operations of the NYC Open Data Team and Open Data Coordinators. Visit [NYC Open Data](https://opendata.cityofnewyork.us/) and explore our code on [GitHub](https://github.com/MODA-NYC/OpenDataDashboard).')
    ]
  ),


  dcc.Tabs(id='tabs_', value='tab1', style={'valign':'middle'}, children=[

    dcc.Tab(label='User Engagement', value='tab1', selected_style={'padding': 10, 'textAlign':'center' ,'height':'45'}, style={'padding': 10, 'textAlign':'center','height':'45'}, children=[
      
      html.Div(
        className="row",
        children=[
          html.H1(
            ' '
          )
        ]
      ),
      html.Div(
        className="row",
        children=[
          html.H1(
            ' '
          )
        ]
      ),
      html.Div(
      	style={'marginLeft': 50, 'marginRight': 50},
	    className = 'row',
	    children = [
	      html.Div(
	        className = 'three columns',
	        children = [
	          html.H4(
	            children='Web Traffic Metrics',
	            style={'color': '#808080'}
	          )
	        ]
	      ),   
	      html.Div(
	      	style={'marginRight': 0,'display': 'inline-block', 'align':'right'},
	        className = 'three columns',
	        children = [
	          dcc.DatePickerRange(
	            id='ga-date-picker-range',
	            min_date_allowed=dt(2017, 9, 21),
	            max_date_allowed=today,
	            initial_visible_month=today,
	            end_date=today,
	            number_of_months_shown=2,
	          ),
	        ]
	      ),
	      html.Div(
	        className = 'six columns',
	        children = [
	          html.H4(
	            children='User Acquisition Channels (last 12 mos.)',
	            style={'color': '#808080'}
	          )
	        ]
	      )
	    ]
	  ),
      html.Div(
      	style={'marginLeft': 50, 'marginRight': 50},
        className='row',
        children=[
          html.Div(
            className='six columns',
            children=[
              html.Div(
                children=[
	              html.H1(' '),
                  dcc.Tabs(id='tabs', value='ga_users', style={'padding':'0'},children=[
                    dcc.Tab(label='Users', value='ga_users', selected_style={'padding':'0','width':'25%','height':'30','textAlign':'center', 'verticalAlign':'middle'}, style={'padding':'0','width':'25%','height':'30','textAlign':'center', 'verticalAlign':'middle'}, children=[
                      html.Div([
                        dcc.Graph(
                          id='ga_users',
                          config={
					        'displayModeBar': False
					      },
                          figure={
                            'data': [
                              {'x': ga_date['ga:date'], 'y': ga_date['ga:users'],'type': 'scatter', 'name': 'Users', 'line': {'color': '#294a6d', 'width':4}, 'mode':'lines'},
                              {'x': ga_date['ga:date'], 'y': ga_date['ga:newUsers'],'type': 'scatter', 'name': 'New Users', 'line': {'color': '#ed7b14', 'dash':'dash', 'width':4}, 'mode':'lines'}
                            ],
                            'layout': {
                              'margin': {'l': 60, 'b': 40, 't': 10, 'r': 60},
                              'yaxis': {'title': 'Users','autorange': False, 'range' : [0,(ga_date['ga:users'].max()*1.30)], 'color': '#808080'},
                              'xaxis': {'color': '#808080'}
                            }
                          }
                        )
                      ])
                    ]),
                    dcc.Tab(label='Sessions', value='ga_sessions', selected_style={'padding':'0','width':'25%','height':'30','textAlign':'center','verticalAlign':'middle'}, style={'padding':'0','width':'25%','height':'30','textAlign':'center','verticalAlign':'middle'}, children=[
                      html.Div([
                        dcc.Graph(
                          id='ga_sessions',
                          config={
					        'displayModeBar': False
					      },
                          figure={
                            'data': [
                              {'x': ga_date['ga:date'], 'y': ga_date['ga:sessions'],'type': 'scatter', 'name': 'Sessions', 'line': {'color': '#294a6d', 'width':4}, 'mode':'lines'}
                            ],
                            'layout': {
                              'margin': {'l': 60, 'b': 40, 't': 10, 'r': 60},
                              'yaxis': {'title': 'Sessions', 'autorange': False, 'range' : [0,(ga_date['ga:sessions'].max()*1.30)], 'color': '#808080'},
                              'xaxis': {'color': '#808080'}
                            }
                          }
                        )
                      ])
                    ]),
                    dcc.Tab(label='Pageviews', value='ga_pageviews', selected_style={'padding':'0','width':'25%','height':'30','textAlign':'center','verticalAlign':'middle'}, style={'padding':'0','width':'25%','height':'30','textAlign':'center','verticalAlign':'middle'}, children=[
                      html.Div([
                        dcc.Graph(
                          id='ga_pageviews',
                          config={
					        'displayModeBar': False
					      },
                          figure={
                            'data': [
                              {'x': ga_date['ga:date'], 'y': ga_date['ga:pageviews'],'type': 'scatter', 'name': 'Pageviews', 'line': {'color': '#294a6d', 'width':4}, 'mode':'lines'},
                            ],
                            'layout': {
                              'margin': {'l': 60, 'b': 40, 't': 10, 'r': 60},
                              'yaxis': {'title': 'Pageviews', 'autorange': False, 'range' : [0,(ga_date['ga:pageviews'].max()*1.30)], 'color': '#808080'},
                              'xaxis': {'color': '#808080'}
                            }
                          }
                        )
                      ])
                    ]),
                    dcc.Tab(label='Bounce Rate', value='ga_bounce_rate', selected_style={'padding':'0','width':'25%','height':'30','textAlign':'center','verticalAlign':'middle'}, style={'padding':'0','width':'25%','height':'30','textAlign':'center','verticalAlign':'middle'}, children=[
                      html.Div([
                        dcc.Graph(
                          id='ga_bounce_rate',
                          config={
					        'displayModeBar': False
					      },
                          figure={
                            'data': [
                              {'x': ga_date['ga:date'], 'y': ga_date['bounce_rate']*100,'type': 'scatter', 'name': 'Bounce Rate', 'line': {'color': '#294a6d', 'width':4}, 'mode':'lines'},
                            ],
                            'layout': {
                              'margin': {'l': 60, 'b': 40, 't': 10, 'r': 60},
                              'yaxis': {'title': 'Bounce Rate (percent)', 'autorange': False, 'range' : [0,(ga_date['bounce_rate'].max()*130)], 'color': '#808080'},
                              'xaxis': {'color': '#808080'}
                            }
                          }
                        )
                      ])
                    ]),                               
                  ]),
                ]
              )
            ]
          ),
          html.Div(
            className="six columns",
              children=[
                html.Div(
                  className='row',
                  children=[
                    html.H1(
            		  ' '
                    )
                  ]
                ),
                html.Div(
                  className='row',
                  children=[
                    html.Div(
                      children=dcc.Graph(
                        id='ga_sources',
                        figure=go.Figure(data=[trace5_source,trace4_source, trace3_source, trace2_source, trace1_source],
                        layout=go.Layout(barmode='stack', margin={'l': 60, 'b': 25, 't': 70, 'r': 60},yaxis={'title': 'Users Acquired', 'autorange': False, 'range' : [0,320000], 'color': '#808080'}, xaxis={'color': '#808080', 'tickcolor':'#000'})),
                        config={'displayModeBar': False}
                      )
                    )
                  ]
                )
              ]
            )
          ]
        ),
      html.Div(
        className="row",
        children=[
          html.H1(
            ' '
          )
        ]
      ),
      html.Div(
        className="row",
        children=[
          html.H1(
            ' '
          )
        ]
      ),
      html.Div(
      	style={'marginLeft': 50, 'marginRight': 50},
        className="row",
        children=[
          html.Div(
            className="four columns",
            children=[
              html.Div(
                children=[
                  html.H4(
                    children='Help Desk Inquiry Type & Volume by Month (last 12 mos.)',
                    style={'color': '#808080'}
                  ),
                  html.Div(
                    children=dcc.Graph(
                      id='inquiries_by_month',
                      figure=go.Figure(data=[trace1_inquiry, trace2_inquiry, trace3_inquiry, trace4_inquiry, trace5_inquiry],
                      layout=go.Layout(barmode='stack',margin={'l': 60, 'b': 40, 't': 20, 'r': 5},yaxis={'title': 'Inquiries', 'color': '#808080'},xaxis={'color': '#808080'})),
                      config={'displayModeBar': False}
                    )
                  ),
                ]
              )
            ]
          ),
          html.Div(
            className="four columns",
            children=[
              html.Div(
                children=[
                  html.H4(
                    children='Help Desk Average Inquiry Resolution Time (last 12 mos.)',
                    style={'color': '#808080'}
                  ),
                  dcc.Graph(
                    id='inquiry_resolution_time',
                    figure={
                      'data': [trace1_resolution, trace2_resolution, trace3_resolution, trace4_resolution, trace5_resolution],
                      'layout': {
                        'margin': {'l': 60, 'b': 40, 't': 20, 'r': 5},
                        'yaxis': {'title': 'Average Days', 'color': '#808080'},
                        'xaxis': {'color': '#808080'},
                        'mode' : 'lines',
                      }
                    }
                  ),
                ]
              )
            ]
          ),
          html.Div(
            className="four columns",
            children=[
              html.Div(
                children=[
                  html.H4(
                    children='Total Help Desk Inquiries by Type and Status (last 12 mos.)',
                    style={'color': '#808080'}
                  ),
                  dcc.Graph(
                    id='request_by_status_grouped',
                    config={'displayModeBar': False},
                    figure=go.Figure(
                      data=[trace1_status,trace2_status,trace3_status],
                      layout=go.Layout(barmode='stack',margin={'l': 60, 'b': 40, 't': 20, 'r': 5},yaxis={'title': 'Inquiries', 'color': '#808080'}, xaxis={'title': 'Inquiry Type', 'tickangle': 0, 'color': '#808080'})
                    )
                  ),
                ]
              )
            ]
          )
        ]
      )
    ]),
    dcc.Tab(label='Data Asset Management', selected_style={'padding': 10, 'textAlign':'center' ,'height':'45'}, style={'padding': 10, 'textAlign':'center','height':'45'}, children=[
      html.Div(
        children=[
          html.H4(
            children='Data Asset Management Status by Dataset', title='Data Asset Management Status by Dataset'
          ),
          dte.DataTable(
            rows=asset_status_check, # initialise the rows
            row_selectable=False,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            id='asset_status_check'
          ),
          html.H4(
            children='Agency Asset Summaries ', title='Agency Asset Summaries '
          ),
          dte.DataTable(
            rows=agency_status_check, # initialise the rows
            row_selectable=False,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            id='agency_status_check'
          ),
        ]
      )
    ]),
    dcc.Tab(label='Metric Definitions', selected_style={'padding': 10, 'textAlign':'center' ,'height':'45'}, style={'padding': 10, 'textAlign':'center','height':'45'}, children=[
      html.Div(
        className = 'row'
      ),
      html.Div(
      className='row',
      children = [
        html.Div(
          className='four columns',
          children = [
            html.Div([
              html.H3('Google Analytics Definitions'),
              html.P('Data from Google Analytics are measuring web traffic and site interactions from users on the NYC Open Data website. Various web traffic platforms exist (SimilarWeb, WebTrends) and have slight variations in how they define “users” or “visits”; the Open Data Team has decided to use Google Analytics as the provider of choice for our web analytics, using their definitions of “users” to track our user engagement metrics.'),
              html.H5('User:'),
              html.P('The total number of (new and returning) users utilizing the website for the specified time period.'), 
              html.P('Google assigns users unique identifiers based on their IP address and when they first accessed a website. A returning user who accesses the site through a different device will be counted as a separate user.'),
              html.H5('New Users:'),
              html.P('A person utilizing the website for the first time for the specified time period.'),
              html.H5('Sessions:'),
              html.P('A group of interactions (such as browsing, downloading resources, etc) one user takes in the website within a given time frame. A unique session expires after 30 minutes or at midnight.'),
              html.H5('Pageview:'),
              html.P('An instance of a page being loaded in a browser'),
              html.H5('Bounce Rate:'),
              html.P('The percentage of times a person leaves the website from the first page in which they landed'),
              html.H5('Website User Acquisition:'),
              html.P('User traffic sources grouped by channels associated with the user’s session. Definitions may change as channels evolve.'),
              dcc.Markdown('**Email:** visits from links clicked in emails'),
              dcc.Markdown('**Social:** visits from links clicked in social networks (ie - Twitter, Facebook, LinkedIn)'),
              dcc.Markdown('**Referral:** visits from links clicked in other websites, excluding social networks'),
              dcc.Markdown('**Organic:** visits from unpaid search results'),
              dcc.Markdown('**Direct:** visits in which users directly navigated to the URL or visits in which the source of visit is unknown'),
              dcc.Markdown('Channel definitions [source](https://megalytic.com/blog/understanding-google-analytics-channels)'),
            ])
          ]
        ),
        html.Div(
          className='four columns',
          children = [
            html.Div([
              html.H3('Open Data Help Desk Inquiry Definitions'),
              html.P('Open Data Help Desk Inquiries are public inquiries submitted through the Open Data website’s “Contact Us” page, viathe “How can we help you?” dropdown menu. '),
              html.H5('Inquiry Type:'),
              html.P('Inquiry Type groups are comprised of the following “How can we help you?” dropdown selections.'),
              dcc.Markdown('**Report Error:** Report an error in the data'),
              dcc.Markdown('**Data Question:** Ask a question about a dataset'),
              dcc.Markdown('**General Inquiry:** General inquiry'),
              dcc.Markdown('**Request a Dataset:** Request a dataset'),
              dcc.Markdown('**Other:** Taxi and Limousine Commission question, Question for Department of Buildings, Comment on Open Data for All Report, Tell us how you use open data, Suggest a partnership, Request a training, Provide an additional resource for this website, Taxi and Limousine Commission (TLC), Department of Transportation (DOT)'),
              html.H5('Inquiry Status:'),
              dcc.Markdown('**Open:** An inquiry that has not had any action taken yet'),
              dcc.Markdown('**Pending:** An inquiry that has had action taken'),
              dcc.Markdown('**Closed:** An inquiry that has been resolved'),
              html.H5('Open Data Help Desk Inquiries by Month:'),
              html.P('The number of helpdesk inquiries submitted by website users, aggregated by month and Inquiry Type'),
              html.H5('Average Monthly Inquiry Resolution Time:'),
              html.P('The average number of days from inquiry submission date to date when inquiry was last updated, for “closed” inquiries only. The number of days is counted within the month the inquiry was resolved.'),
            ])
          ]
        ),
        html.Div(
          className='four columns',
          children = [
            html.Div([
              html.H3('Data Asset Management Definitions'),
              html.P('The Data Asset Management tab’s visualizations are sourced from the Asset Inventory data accessed via Socrata’s API. Socrata is the vendor that powers the data catalog and user interface for interacting with the assets on NYC Open Data.'),
              html.H5('Agency:'),
              html.P('New York City agency name'),
              html.H5('Asset Name:'),
              html.P('Name of unique material on the Open Data Portal. Asset are data that exist on the Open Data Portal (ie - datasets , snapshots, or maps)'),
              html.H5('Update Frequency:'),
              html.P('The frequency in which an asset is meant to be updated--stated by the agency when asset is first added to the portal'),
              html.H5('Update Method:'),
              html.P('Specifies whether an asset is updated manually or automatically'),
              html.H5('Last Updated:'),
              html.P('Date and time when an individual asset was last updated on the portal'),
              html.H5('Updated on Time?:'),
              html.P('Specifies whether an asset was last updated on time (possible answers are “Yes” and “No”)'),
              html.H5('Has Data Dictionary?:'),
              html.P('Specifies whether an asset has a data dictionary on the portal (possible answers are “Yes” and “No”)'),
              html.H5('Is Geocoded?:'),
              html.P('Specifies whether an asset has been geocoded  (possible answers are “Yes”, “No” and “N/A”)'),
              html.P(''),
              html.H5('Total Assets:'),
              html.P('Total assets by agency on the portal'),
              html.H5('Automated:'),
              html.P('Total automated assets by agency on the portal'),
              html.H5('Automated Not Updated:'),
              html.P('Total automated assets that have not been updated on time on the portal, by agency'),
              html.H5('Manual:'),
              html.P('Total manual assets by agency on the portal'),
              html.H5('Manual Not Updated:'),
              html.P('Total manual assets that have not been updated on time on the portal, by agency'),
            ])
          ]
        )
      ])
    ]),
  ])
])     

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})


"""Web Traffic Metrics Filtering"""
#Filters Users tab
@app.callback(
  Output('ga_users', 'figure'),
  [Input('ga-date-picker-range', 'start_date'),
  Input('ga-date-picker-range', 'end_date')])
def update_user_scatter(start_date, end_date):
  if start_date is not None:
    if end_date is not None: 
      start_date = dt.strptime(start_date, '%Y-%m-%d')
      end_date = dt.strptime(end_date, '%Y-%m-%d')
      day_difference = end_date - start_date
      if (day_difference < timedelta(days=27)):
        usp_daily_windowed = usp_daily[(usp_daily['ga:date'] >= start_date) & (usp_daily['ga:date'] <= end_date)]        
      elif (day_difference < timedelta(days=90)):
        usp_daily_windowed = usp_weekly[(usp_weekly['ga:date'] >= start_date) & (usp_weekly['ga:date'] <= end_date)]       
      else:
        usp_daily_windowed = usp_monthly[(usp_monthly['ga:date'] >= start_date) & (usp_monthly['ga:date'] <= end_date)]        
      figure = {
        'data': [
          {'x': usp_daily_windowed['ga:date'], 'y': usp_daily_windowed['ga:users'],'type': 'scatter', 'name': 'Users', 'line': {'color': '#294a6d', 'width':4}, 'mode':'lines'},
          {'x': usp_daily_windowed['ga:date'], 'y': usp_daily_windowed['ga:newUsers'],'type': 'scatter', 'name': 'New Users', 'line': {'color': '#ed7b14', 'dash':'dash', 'width':4}, 'mode':'lines'}
        ],
        'layout': {
          'margin': {'l': 60, 'b': 40, 't': 10, 'r': 60},
          'yaxis': {'title': 'Users','autorange': False, 'range' : [0,(usp_daily_windowed['ga:users'].max()*1.30)], 'color': '#808080'},
          'xaxis': {'color': '#808080'}
        }
      }
  return figure
#Filters Sessions tab
@app.callback(
  Output('ga_sessions', 'figure'),
  [Input('ga-date-picker-range', 'start_date'),
  Input('ga-date-picker-range', 'end_date')])
def update_sessions_scatter(start_date, end_date):
  #figure={} #instantiate figure object
  if start_date is not None:
    if end_date is not None: 
      start_date = dt.strptime(start_date, '%Y-%m-%d')
      end_date = dt.strptime(end_date, '%Y-%m-%d')
      day_difference = end_date - start_date
      if (day_difference < timedelta(days=27)):
        usp_daily_windowed = usp_daily[(usp_daily['ga:date'] >= start_date) & (usp_daily['ga:date'] <= end_date)]        
      elif (day_difference < timedelta(days=90)):
        usp_daily_windowed = usp_weekly[(usp_weekly['ga:date'] >= start_date) & (usp_weekly['ga:date'] <= end_date)]       
      else:
        usp_daily_windowed = usp_monthly[(usp_monthly['ga:date'] >= start_date) & (usp_monthly['ga:date'] <= end_date)]  
      figure = {
        'data': [
          {'x': usp_daily_windowed['ga:date'], 'y': usp_daily_windowed['ga:sessions'],'type': 'scatter', 'name': 'Sessions', 'line': {'color': '#294a6d', 'width':4}, 'mode':'lines'},
        ],
        'layout': {
          'margin': {'l': 60, 'b': 40, 't': 10, 'r': 60},
          'yaxis': {'title': 'Sessions', 'autorange': False, 'range' : [0,(usp_daily_windowed['ga:sessions'].max()*1.30)], 'color': '#808080'},
          'xaxis': {'color': '#808080'}
        }
      }
  return figure
#Filters Pageviews tab
@app.callback(
  Output('ga_pageviews', 'figure'),
  [Input('ga-date-picker-range', 'start_date'),
  Input('ga-date-picker-range', 'end_date')])
def update_pageviews_scatter(start_date, end_date):
  #figure={} #instantiate figure object
  if start_date is not None:
    if end_date is not None: 
      start_date = dt.strptime(start_date, '%Y-%m-%d')
      end_date = dt.strptime(end_date, '%Y-%m-%d')
      day_difference = end_date - start_date
      if (day_difference < timedelta(days=27)):
        usp_daily_windowed = usp_daily[(usp_daily['ga:date'] >= start_date) & (usp_daily['ga:date'] <= end_date)]        
      elif (day_difference < timedelta(days=90)):
        usp_daily_windowed = usp_weekly[(usp_weekly['ga:date'] >= start_date) & (usp_weekly['ga:date'] <= end_date)]       
      else:
        usp_daily_windowed = usp_monthly[(usp_monthly['ga:date'] >= start_date) & (usp_monthly['ga:date'] <= end_date)]  
      figure = {
        'data': [
          {'x': usp_daily_windowed['ga:date'], 'y': usp_daily_windowed['ga:pageviews'],'type': 'scatter', 'name': 'Pageviews', 'line': {'color': '#294a6d', 'width':4}, 'mode':'lines'},
        ],
        'layout': {
          'margin': {'l': 60, 'b': 40, 't': 10, 'r': 60},
          'yaxis': {'title': 'Pageviews', 'autorange': False, 'range' : [0,(usp_daily_windowed['ga:pageviews'].max()*1.30)], 'color': '#808080'},
          'xaxis': {'color': '#808080'}
        }
      }
  return figure
#Filters Bounce Rate tab
@app.callback(
  Output('ga_bounce_rate', 'figure'),
  [Input('ga-date-picker-range', 'start_date'),
  Input('ga-date-picker-range', 'end_date')])
def update_bounce_scatter(start_date, end_date):
  #figure={} #instantiate figure object
  if start_date is not None:
    if end_date is not None: 
      start_date = dt.strptime(start_date, '%Y-%m-%d')
      end_date = dt.strptime(end_date, '%Y-%m-%d')
      day_difference = end_date - start_date
      if (day_difference < timedelta(days=27)):
        usp_daily_windowed = usp_daily[(usp_daily['ga:date'] >= start_date) & (usp_daily['ga:date'] <= end_date)]        
      elif (day_difference < timedelta(days=90)):
        usp_daily_windowed = usp_weekly[(usp_weekly['ga:date'] >= start_date) & (usp_weekly['ga:date'] <= end_date)]       
      else:
        usp_daily_windowed = usp_monthly[(usp_monthly['ga:date'] >= start_date) & (usp_monthly['ga:date'] <= end_date)]  
      figure = {
        'data': [
          {'x': usp_daily_windowed['ga:date'], 'y': usp_daily_windowed['bounce_rate']*100,'type': 'scatter', 'name': 'Bounce Rate', 'line': {'color': '#294a6d', 'width':4}, 'mode':'lines'},
        ],
        'layout': {
          'margin': {'l': 60, 'b': 40, 't': 10, 'r': 60},
          'yaxis': {'title': 'Bounce Rate (percent)', 'autorange': False, 'range' : [0,(usp_daily_windowed['bounce_rate'].max()*130)], 'color': '#808080'},
          'xaxis': {'color': '#808080'}
        }
      }
  return figure



if __name__ == '__main__':
     app.run_server(host='0.0.0.0', port=5000, debug=True)




