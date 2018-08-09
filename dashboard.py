import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from screendoor_api import *
import ga_api as ga_helpers
from socrata_api import *
from datetime import datetime as dt
import dash_table_experiments as dte



usp_data = ga_helpers.load_ga_data()
usp_data = ga_helpers.cast_ga_data(usp_data)
sources_data = ga_helpers.load_sources_data()
sources_data = ga_helpers.cast_sources_data(sources_data)
usp_daily = ga_helpers.make_usp(usp_data, freq='d')
usp_weekly = ga_helpers.make_usp(usp_data, freq='W')
usp_monthly = ga_helpers.make_usp(usp_data, freq='M')
sources_daily = ga_helpers.make_sources(sources_data, freq='d')
sources_weekly = ga_helpers.make_sources(sources_data, freq='W')
sources_monthly = ga_helpers.make_sources(sources_data, freq='M')


today_string = dt.today().strftime('%B %d, %Y')
today = dt.today().strftime('%Y-%m-%d')

ga_date = usp_daily[(usp_daily['ga:date'] >= (dt.today()-timedelta(days=8))) & (usp_daily['ga:date'] <= (dt.today()-timedelta(days=1)))]
ga_date_sources = sources_daily[(sources_daily['ga:date'] >= (dt.today()-timedelta(days=8))) & (sources_daily['ga:date'] <= (dt.today()-timedelta(days=1)))]

colors = {
    'background': '#FFF',
    'text': '#D3D3D3'
}

#Traces for Inquiry Type 


trace1_inquiry = go.Bar(
  x=monthly_submissions[monthly_submissions['request_type_grouped'] == 'Data Question']['submitted_at'],
  y=monthly_submissions[monthly_submissions['request_type_grouped'] == 'Data Question']['id'],
  name='Data Question'
)

trace2_inquiry = go.Bar(
  x=monthly_submissions[monthly_submissions['request_type_grouped'] == 'General Inquiry']['submitted_at'],
  y=monthly_submissions[monthly_submissions['request_type_grouped'] == 'General Inquiry']['id'],
  name='General Inquiry'
)

trace3_inquiry = go.Bar(
  x=monthly_submissions[monthly_submissions['request_type_grouped'] == 'Other']['submitted_at'],
  y=monthly_submissions[monthly_submissions['request_type_grouped'] == 'Other']['id'],
  name='Other'
)

trace4_inquiry = go.Bar(
  x=monthly_submissions[monthly_submissions['request_type_grouped'] == 'Report Error']['submitted_at'],
  y=monthly_submissions[monthly_submissions['request_type_grouped'] == 'Report Error']['id'],
  name='Report Error'
)

trace5_inquiry = go.Bar(
  x=monthly_submissions[monthly_submissions['request_type_grouped'] == 'Request a Dataset']['submitted_at'],
  y=monthly_submissions[monthly_submissions['request_type_grouped'] == 'Request a Dataset']['id'],
  name='Request a Dataset'
)


#Traces for Screendoor

trace1_status = go.Bar(
    x=requests_by_status_grouped[requests_by_status_grouped['status'] == 'Closed']['request_type_grouped'],
    y=requests_by_status_grouped[requests_by_status_grouped['status'] == 'Closed']['id'],
    name='Closed'
)
trace2_status = go.Bar(
    x=requests_by_status_grouped[requests_by_status_grouped['status'] == 'Pending']['request_type_grouped'],
    y=requests_by_status_grouped[requests_by_status_grouped['status'] == 'Pending']['id'],
    name='Pending'
)
trace3_status = go.Bar(
    x=requests_by_status_grouped[requests_by_status_grouped['status'] == 'Open']['request_type_grouped'],
    y=requests_by_status_grouped[requests_by_status_grouped['status'] == 'Open']['id'],
    name='Open'
)

#Traces for Google Analytics

trace1_source = go.Bar(
  x=ga_date_sources[ga_date_sources['ga:channelGrouping']=='Direct']['ga:date'],
  y=ga_date_sources[ga_date_sources['ga:channelGrouping']=='Direct']['ga:users'],
  name='Direct'
)

trace2_source = go.Bar(
  x=ga_date_sources[ga_date_sources['ga:channelGrouping']=='Organic Search']['ga:date'],
  y=ga_date_sources[ga_date_sources['ga:channelGrouping']=='Organic Search']['ga:users'],
  name='Organic Search'
)

trace3_source = go.Bar(
  x=ga_date_sources[ga_date_sources['ga:channelGrouping']=='Referral']['ga:date'],
  y=ga_date_sources[ga_date_sources['ga:channelGrouping']=='Referral']['ga:users'],
  name='Referral'
)

trace4_source = go.Bar(
  x=ga_date_sources[ga_date_sources['ga:channelGrouping']=='Social']['ga:date'],
  y=ga_date_sources[ga_date_sources['ga:channelGrouping']=='Social']['ga:users'],
  name='Social'
)

trace5_source = go.Bar(
  x=ga_date_sources[ga_date_sources['ga:channelGrouping']=='Email']['ga:date'],
  y=ga_date_sources[ga_date_sources['ga:channelGrouping']=='Email']['ga:users'],
  name='Email'
)

#Socrata table

def generate_table(dataframe, max_rows=1000):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

app = dash.Dash()
app.layout = html.Div([
  html.Div(
    className='row',
    children=[    
      html.H4(
        children='Open Data Dashboard'
      ),
      html.P(
        children='Updated as of ' + today_string
      ),
    ]
  ),
  dcc.Tabs(id='tabs', value='tab1', children=[
    dcc.Tab(label='User Engagement', value='tab1', selected_style={'height':'45'}, style={'height':'45'}, children=[
      html.Div(
        className='row',
        children=[
          html.Div(
            children=[
              dcc.DatePickerRange(
                id='ga-date-picker-range',
                min_date_allowed=dt(2017, 9, 21),
                max_date_allowed=today,
                initial_visible_month=today,
                end_date=today,
              ),
            ]
          )
        ]
      ),
      html.Div(
        className='row',
        children=[
          html.Div(
            className='six columns',
            children=[
              html.Div(
                children=[
                  html.H6(
                    children='Web Traffic Metrics', title='Data from Google Analytics'
                  ),
                  dcc.Tabs(id='tabs', value='ga_users', style={'padding':'0'}, content_style={'height':300},children=[
                    dcc.Tab(label='Users', value='ga_users', selected_style={'padding':'0','width':'25%','height':'30','textAlign':'center','verticalAlign':'middle'}, style={'padding':'0','width':'25%','height':'30','textAlign':'center','verticalAlign':'middle'}, children=[
                      html.Div([
                        dcc.Graph(
                          id='ga_users',
                          figure={
                            'data': [
                              {'x': ga_date['ga:date'], 'y': ga_date['ga:users'],'type': 'scatter', 'name': 'Users'},
                              {'x': ga_date['ga:date'], 'y': ga_date['ga:newUsers'],'type': 'scatter', 'name': 'New Users'}
                            ],
                            'layout': {
                              'height': 300,
                              'margin': {'l': 60, 'b': 40, 't': 10, 'r': 60},
                              'yaxis': {'title': 'Users','autorange': False, 'range' : [0,(ga_date['ga:users'].max()*1.30)]}
                            }
                          }
                        )
                      ])
                    ]),
                    dcc.Tab(label='Sessions', value='ga_sessions', selected_style={'padding':'0','width':'25%','height':'30','textAlign':'center','verticalAlign':'middle'}, style={'padding':'0','width':'25%','height':'30','textAlign':'center','verticalAlign':'middle'}, children=[
                      html.Div([
                        dcc.Graph(
                          id='ga_sessions',
                          figure={
                            'data': [
                              {'x': ga_date['ga:date'], 'y': ga_date['ga:sessions'],'type': 'scatter', 'name': 'Sessions'}
                            ],
                            'layout': {
                              'height': 300,
                              'margin': {'l': 60, 'b': 40, 't': 10, 'r': 60},
                              'yaxis': {'title': 'Sessions', 'autorange': False, 'range' : [0,(ga_date['ga:sessions'].max()*1.30)]}
                            }
                          }
                        )
                      ])
                    ]),
                    dcc.Tab(label='Pageviews', value='ga_pageviews', selected_style={'padding':'0','width':'25%','height':'30','textAlign':'center','verticalAlign':'middle'}, style={'padding':'0','width':'25%','height':'30','textAlign':'center','verticalAlign':'middle'}, children=[
                      html.Div([
                        dcc.Graph(
                          id='ga_pageviews',
                          figure={
                            'data': [
                              {'x': ga_date['ga:date'], 'y': ga_date['ga:pageviews'],'type': 'scatter', 'name': 'Pageviews'}
                            ],
                            'layout': {
                              'height': 300,
                              'margin': {'l': 60, 'b': 40, 't': 10, 'r': 60},
                              'yaxis': {'title': 'Pageviews', 'autorange': False, 'range' : [0,(ga_date['ga:pageviews'].max()*1.30)]}
                            }
                          }
                        )
                      ])
                    ]),
                    dcc.Tab(label='Bounce Rate', value='ga_bounce_rate', selected_style={'padding':'0','width':'25%','height':'30','textAlign':'center','verticalAlign':'middle'}, style={'padding':'0','width':'25%','height':'30','textAlign':'center','verticalAlign':'middle'}, children=[
                      html.Div([
                        dcc.Graph(
                          id='ga_bounce_rate',
                          figure={
                            'data': [
                              {'x': ga_date['ga:date'], 'y': ga_date['bounce_rate'],'type': 'scatter', 'name': 'Bounce Rate'}
                            ],
                            'layout': {
                              'height': 300,
                              'margin': {'l': 60, 'b': 40, 't': 10, 'r': 60},
                              'yaxis': {'title': 'Bounce Rate', 'autorange': False, 'range' : [0,(ga_date['bounce_rate'].max()*1.30)]}
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
                children=[
                  html.H6(
                    children='User Acquisition Channels', title='These are user acquisition methods'
                  ),
                  html.Div(
                    children=dcc.Graph(
                      id='ga_sources',
                      figure=go.Figure(data=[trace1_source,trace2_source, trace3_source, trace4_source, trace5_source],
                      layout=go.Layout(barmode='stack',height=300,margin={'l': 60, 'b': 40, 't': 20, 'r': 5},yaxis={'title': 'Users Acquired'}))
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
          html.Div(
            className="four columns",
            children=[
              html.Div(
                children=[
                  html.H6(
                    children='Help Desk Inquiry Type & Volume by Month (last 12 mos.)'
                  ),
                  html.Div(
                    children=dcc.Graph(
                      id='inquiries_by_month',
                      figure=go.Figure(data=[trace1_inquiry, trace2_inquiry, trace3_inquiry, trace4_inquiry, trace5_inquiry],
                      layout=go.Layout(barmode='stack',height=300,margin={'l': 60, 'b': 40, 't': 20, 'r': 5},yaxis={'title': 'Inquiries'}))
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
                  html.H6(
                    children='Help Desk Average Monthly Inquiry Resolution Time by Inquiry Type (last 12 mos.)'
                  ),
                  dcc.Graph(
                    id='inquiry_resolution_time',
                    figure={
                      'data': [
                        go.Scatter(
                          x=monthly_resolution_time[monthly_resolution_time['request_type_grouped'] == k]['submitted_at'],
                          y=monthly_resolution_time[monthly_resolution_time['request_type_grouped'] == k]['average_resolution'],
                          name=k
                        ) for k in monthly_resolution_time['request_type_grouped'].unique()
                      ],
                      'layout': {
                        'height': 300,
                        'margin': {'l': 60, 'b': 40, 't': 20, 'r': 5},
                        'yaxis': {'title': 'Average Days'}
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
                  html.H6(
                    children='Total Help Desk Inquiries by Type and Status (last 12 mos.)'
                  ),
                  dcc.Graph(
                    id='request_by_status_grouped',
                    figure=go.Figure(
                      data=[trace1_status,trace2_status,trace3_status],
                      layout=go.Layout(barmode='stack',height=300,margin={'l': 60, 'b': 40, 't': 20, 'r': 5},yaxis={'title': 'Inquiries'}, xaxis={'title': 'Inquiry Type', 'tickangle': 0})
                    )
                  ),
                ]
              )
            ]
          )
        ]
      )
    ]),
    dcc.Tab(label='Asset Management', selected_style={'height':'45'}, style={'height':'45'}, children=[
      html.Div(
        children=[
          html.H6(
            children='Asset Management Status by Dataset', title='Asset Management Status by Dataset'
          ),
          dte.DataTable(
            rows=asset_status_check, # initialise the rows
            row_selectable=False,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            #max_rows_in_viewport=5,
            #header_row_height=32,
            #row_height=22,
            id='asset_status_check'
          ),
          html.H6(
            children='Agency Asset Summaries ', title='Agency Asset Summaries '
          ),
          dte.DataTable(
            rows=agency_status_check, # initialise the rows
            row_selectable=False,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            #max_rows_in_viewport=5,
            #header_row_height=32,
            #row_height=22,
            id='agency_status_check'
          ),
        ]
      )
    ]),
    dcc.Tab(label='Definitions', selected_style={'height':'45'}, style={'height':'45'}, children=[
      
    ]),
  ])
])   
    

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

@app.callback(
    Output('ga_sessions', 'figure'),
    [Input('ga-date-picker-range', 'start_date'),
    Input('ga-date-picker-range', 'end_date')])
def update_sessions_scatter(start_date, end_date):
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
          {'x': usp_daily_windowed['ga:date'], 'y': usp_daily_windowed['ga:sessions'],'type': 'scatter'}
        ],
        'layout': {
          'height': 300,
          'margin': {'l': 60, 'b': 40, 't': 10, 'r': 60},
          'yaxis': {'title': 'Sessions', 'autorange': False, 'range' : [0,(usp_daily_windowed['ga:sessions'].max()*1.30)]}
        }
      }
  return figure

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
          {'x': usp_daily_windowed['ga:date'], 'y': usp_daily_windowed['ga:users'],'type': 'scatter', 'name': 'Users'},
          {'x': usp_daily_windowed['ga:date'], 'y': usp_daily_windowed['ga:newUsers'],'type': 'scatter', 'name': 'New Users'}
        ],
        'layout': {
          'height': 300,
          'margin': {'l': 60, 'b': 40, 't': 10, 'r': 60},
          'yaxis': {'title': 'Users','autorange': False, 'range' : [0,(usp_daily_windowed['ga:users'].max()*1.30)]}
        }
      }
  return figure

@app.callback(
    Output('ga_pageviews', 'figure'),
    [Input('ga-date-picker-range', 'start_date'),
    Input('ga-date-picker-range', 'end_date')])
def update_pageviews_scatter(start_date, end_date):
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
          {'x': usp_daily_windowed['ga:date'], 'y': usp_daily_windowed['ga:pageviews'],'type': 'scatter'}
        ],
        'layout': {
          'height': 300,
          'margin': {'l': 60, 'b': 40, 't': 10, 'r': 60},
          'yaxis': {'title': 'Pageviews', 'autorange': False, 'range' : [0,(usp_daily_windowed['ga:pageviews'].max()*1.30)]}
        }
      }
  return figure


@app.callback(
    Output('ga_bounce_rate', 'figure'),
    [Input('ga-date-picker-range', 'start_date'),
    Input('ga-date-picker-range', 'end_date')])
def update_bounce_scatter(start_date, end_date):
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
          {'x': usp_daily_windowed['ga:date'], 'y': usp_daily_windowed['bounce_rate'],'type': 'scatter'}
        ],
        'layout': {
          'height': 300,
          'margin': {'l': 60, 'b': 40, 't': 10, 'r': 60},
          'yaxis': {'title': 'Bounce Rate', 'autorange': False, 'range' : [0,(usp_daily_windowed['bounce_rate'].max()*1.30)]}
        }
      }
  return figure



if __name__ == '__main__':
    # load run obj into global scope

    #run server
    app.run_server(debug=True)





















