# Outside Imports
import dash
import glob
import plotly
import json
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
token = 'pk.eyJ1IjoiZHJld3J1c3QxIiwiYSI6ImNrOGxxMXQxbDBlaDIzbG56MjFnM2VxZGMifQ.FTGX44CylOAZSO_WHYsP1g'
px.set_mapbox_access_token(token)

# Imports from this application
from app import app





url = 'routes/routes.csv'
routes_df = pd.read_csv(url, encoding='latin-1')
routes_df = routes_df[['StateNum', 'Route', 'RouteName', 'Active', 'Latitude', 'Longitude', 'Stratum', 'BCR', 'RouteTypeID']]


class Bird:

  url = 'routes/routes.csv'
  routes_df = pd.read_csv(url, encoding='latin-1')
  routes_df = routes_df[['StateNum', 'Route', 'RouteName', 'Active', 'Latitude', 'Longitude', 'Stratum', 'BCR', 'RouteTypeID']]

  def __init__(self, bird_num, low_year, high_year):
    self.bird_num = bird_num
    self.low_year = low_year
    self.high_year = high_year

  def get_state_data(self):
    path = r"states"
    all_files = glob.glob(path + "/*.csv")
    li = []
    for filename in all_files:
      df = pd.read_csv(filename, index_col=None, header=0)
      state_num = df.at[0, "StateNum"]
      Adf = self.bird_function(df)
      Bdf = self.year_function(Adf)
      Cdf = self.route_count_function(Bdf)
      Ddf = self.route_clean_function(state_num)
      Edf = self.create_array(Cdf)
      Fdf = self.finish_df(Ddf, Cdf, Edf)
      li.append(Fdf)
    frame = pd.concat(li, axis=0, ignore_index=True)
    return frame

  def bird_function(self, state_df):
    beginning_df = state_df[(state_df["AOU"] == self.bird_num)] 
    return beginning_df

  def year_function(self, state_df):
    df = state_df[(state_df["Year"] >= self.low_year) & (state_df["Year"] <= self.high_year)]
    df = df.reset_index(drop=True)
    return df
  
  def route_count_function(self, state_df):
    df = state_df.groupby("Route").SpeciesTotal.sum().reset_index()
    df['AOU'] = str(self.bird_num)
    return df
    
  def route_clean_function(self, state_number):
    df = routes_df[(routes_df["StateNum"] == state_number)]
    df = df.sort_values(by="Route", ascending=True)
    df = df.reset_index(drop=True)
    return df

  def create_array(self, st_routes):
    route_array = []
    for ind in st_routes.index:
      route_array.append(st_routes["Route"][ind])
    return route_array

  def finish_df(self, st_routes, st_counts, array):
    booleans = []
    x = 0
    for ind in st_routes.index:
      if x == len(array):
        booleans.append(False)
      elif (st_routes['Route'][ind] == array[x]):
        booleans.append(True)
        x += 1
      else:
        booleans.append(False)
    is_route = pd.Series(booleans)
    df = st_routes[is_route]
    final_df = pd.merge(df, st_counts, on=["Route"], how="inner")
    return final_df

    # Will use this in the Route Class and Year Class sorts by year for graphing
  def sort_by_year(self, df):
    new_df = df.sort_values(by="Year", ascending=True)
    final_df = new_df.reset_index(drop=True)
    return final_df  
  
  @classmethod
  def map_graph(cls, df):
    df["text"] = ("Count: " + df["SpeciesTotal"].astype(str))
    fig = px.scatter_mapbox(data_frame=df, lat = "Latitude", lon = "Longitude", 
                          mapbox_style = "light", color = "SpeciesTotal", size = "SpeciesTotal", 
                          text = "RouteName", hover_name = "text", 
                          color_continuous_scale = px.colors.sequential.Rainbow, opacity = 0.3, 
                          size_max=25, zoom = 4.5, center= {"lat": 39.25, "lon": -84.8})
    fig.update_layout(clickmode='event+select')
    return fig

class Route(Bird):

  def __init__(self, bird_num, low_year, high_year, route):
    super().__init__(bird_num, low_year, high_year)
    self.route = route
  
  def get_route_data(self):
    path = r"states"
    all_files = glob.glob(path + "/*.csv")
    li = []
    for filename in all_files:
      df = pd.read_csv(filename, index_col=None, header=0)
      df = df[['StateNum', 'Route', 'RPID', 'Year', 'AOU', 'SpeciesTotal']]
      state_num = df.at[0, "StateNum"]
      cleaned_rts = self.route_clean_function(state_num)
      combined_strts = pd.merge(df, cleaned_rts) # automatically fits routeNum with frame
      Gdf = self.bird_function(combined_strts) # only get designated bird's count (I LIKE THIS can call from MAIN CLASS)
      Hdf = self.year_function(Gdf)
      Idf = self.set_route(Hdf) 
      Jdf = self.sort_by_year(Idf) # Make sure we're getting years sorted
      li.append(Jdf) # Don't really need the list but to keep it uniform
    combined_all = pd.concat(li, axis=0, ignore_index=True)
    return combined_all

  def set_route(self, state_df):
    route_setdf = state_df[(state_df["RouteName"] == self.route)] # only get state's route counts
    return route_setdf

  @classmethod
  def route_sum(cls, df):
    route_total = (df['SpeciesTotal'].sum())
    return route_total

  @classmethod
  def year_graph(cls, df):
    # df["SpeciesTotal"] = df["SpeciesTotal"].astype(float).astype(int)
    fig = px.bar(df, y='SpeciesTotal', x='Year', text='SpeciesTotal')
    fig.update_traces(texttemplate='%{text:.1s}', textposition='outside')
    fig.update_layout(uniformtext_minsize=10, uniformtext_mode='show')
    return fig



### CREATING NEW CLASS Years FOR LINE GRAPH

class Years(Bird):

  def __init__(self, bird_num, low_year, high_year):
    super().__init__(bird_num, low_year, high_year)

  # CLASS Years(Bird) main_year_func()
  # use combined_state then bird func from parent class to get only one species
  # sort by year and sum totals
  # return dataframe

  def main_year_func(self):
    combined_df = self.combine_sts()
    next_df = self.bird_function(combined_df)
    last_df = self.year_count_function(next_df)
    finished_df = self.sort_by_year(last_df)
    return finished_df

  # read in ea state pick columns then merge them

  def combine_sts(self):
    path = r"states"
    all_files = glob.glob(path + "/*.csv")
    li = []
    for filename in all_files:
      df = pd.read_csv(filename, index_col=None, header=0)
      next_df = df[['StateNum', 'Route', 'RPID', 'Year', 'AOU', 'SpeciesTotal']]
      li.append(next_df) 
    combined = pd.concat(li, axis=0, ignore_index=True)
    return combined

  def year_count_function(self, df):
    sum_df = df.groupby("Year").SpeciesTotal.sum().reset_index()
    return sum_df

  @classmethod
  def line_graph(cls, df):
    fig = go.Figure(data=go.Scatter(x=df['Year'], y=df['SpeciesTotal']))
    return fig



styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}



#### Container
layout = dbc.Container(
    [

#### Trying out html header instead of markdown
      html.Div(
        [
          dbc.Row(dbc.Col(
              [html.H2('Bird Census Route Counts:', className="text-info mb-4"),
              html.H5('Data From The Breeding Bird Survey')]
                  ,xs=12, sm=12, md=12, lg=8, xl=10), justify="center", className="mb-3")
                  ],
                ),


#### Explanation of site in markdown
#### A way to put a space in markdown:  &nbsp;
      html.Div(
        [
          dbc.Row(dbc.Col(
            dcc.Markdown(
                """

                The Breeding Bird Survey is an ongoing census of North American Birds.
                First use the range slider to choose the years you would like to look at.  Next, select
                a species of bird or view the current one. 
                
                Finally, zoom in on the route names and choose a route name. Spell it correctly 
                in the text field to see your selected yearly totals for that route.
                It should add up to the route total count for the years you're looking at.  Some
                years no birds are counted and of course some routes have bigger bird populations.
                """
                      ),xs=12, sm=12, md=12, lg=8, xl=10), justify="center")
                  ],
                ),



#### Year Range Selector
html.Div(
  [
    dbc.Row(dbc.Col(
    html.Div([
    html.H4('Years:', className="text-info mb-4"), 
    html.Div([
    dcc.RangeSlider(
      id="range_slider_year",
      marks={i: '{}'.format(i) for i in range(1968, 2019, 10)},
      min=1966,
      max=2018,
      value=[1966, 2018]
      ),
      ], style={'marginBottom': 20, 'marginTop': 20}),
      html.Div(id='output-container-range-slider')
    ], style={'marginBottom': 5, 'marginTop': 25}
    ), xs=12, sm=12, md=12, lg=8, xl=10), justify="center")
    ], style={'marginBottom': 5, 'marginTop': -30}
    ),
                



#### Bird Selection: Needs more birds
html.Div([dbc.Row(dbc.Col(
    html.Div([
    html.H5('Species:', className="text-info"),
    dcc.Dropdown(
      id="drop_down_bird",
      options=[
            {'label': "American Goldfinch 5290", 'value': 5290},
            {'label': "Carolina Chikadee 7360", 'value': 7360},
            {'label': "Cooper's Hawk 3330", 'value': 3330},
            {'label': "Eastern Bluebird 7660", 'value': 7660},
            {'label': "Kentucky Warbler 6770", 'value': 6770},
            {'label': "Northern Bobwhite 2890", 'value': 2890},
            {'label': "Prothonotary Warbler (Golden Swamp Warbler) 6370", 'value': 6370},  
            {'label': "Red Tailed Hawk 3370", 'value': 3370},
            {'label': "Red Shouldered Hawk 3390", 'value': 3390},
            {'label': "Ruby Throated Hummingbird 4280", 'value': 4280}
        ],
      value=5290,
      style={"margin-top": "25px", "margin-bottom": "30px"}
    ),
    html.Div(id='output-container-drop-down')
   ], style={'marginBottom': 35, 'marginTop': 25}
   ),xs=12, sm=12, md=12, lg=8, xl=10), justify="center")
                  ],
                ),

#### First Graph
      html.Div(
        [
          dbc.Row(dbc.Col(
   html.Div([
             dcc.Graph(id="map_route_counts"),
   ],),xs=12, sm=12, md=12, lg=8, xl=10), justify="center")
                  ],
                ),

#### Map Click Data of Route Clicked
html.Div(
      [
        dbc.Row(dbc.Col(
      
      html.Div([
            html.Pre(id='click-data', style=styles['pre']),
        ], 
        ),xs=12, sm=12, md=12, lg=8, xl=10), justify="center")
        ],
        ),



#### Route input
  html.Div([
  dbc.Row(dbc.Col(
  html.Div([
  html.Div([
    html.H4('Route:', className="text-info"),
    html.H5("Click a route above on the map to see info.", className="mt-3"),
    html.H5("Next type it in below."),
      dcc.Input(
        value="CUMBERLND GP",
        id="text_input_route", 
        type='text', 
        style={"margin-top": "15px", "margin-bottom": "25px"}
              ),
  html.Div(id='output-container-route-input')
        ], 
    style={'marginBottom': 35, 'marginTop': 25}
        ),
    html.Div(id='route-count-total')
            ], 
    style={'marginBottom': 5, 'marginTop': 25}
            ),xs=12, sm=12, md=12, lg=8, xl=10), justify="center")
                  ],
                ),

#### Reload Graphs Button
html.Div([
dbc.Row(dbc.Col(
html.Div([
  html.Div([
    html.H5('Re-load Graphs:', className="text-info")
          ], 
          style={'marginBottom': 25, 'marginTop': 10}),
          html.Div([
  # html.Button('Submit', id='button'),
  dbc.Button("Submit New Graphs", size="lg", id='submit_button', color='info', className="mr-1"),
          ],
          style={'marginBottom': 25, 'marginTop': 25}),
  html.Div(id='output-container-route-button')
        ], 
          style={'marginBottom': 30, 'marginTop': 25}),
            xs=12, sm=12, md=12, lg=8, xl=10), justify="center")
                  ],
                ),


#### Second Graph
      html.Div(
        [
          dbc.Row(dbc.Col(
           
    html.Div([
      dcc.Graph(id="yearly_graph_counts"),
            ],
                      ),xs=12, sm=12, md=12, lg=8, xl=10), justify="center")
                  ],
                ),


#### End of Container
    ]
)

#### Callbacks and updates of both graphs
@app.callback(
    [Output('map_route_counts', 'figure'),
    Output('yearly_graph_counts', 'figure')],
    [Input('range_slider_year', 'value'),
    Input('drop_down_bird', 'value'),
    Input('text_input_route', 'value')])
def update_figure(range_slider_year, drop_down_bird, text_input_route):
    bird_object = Bird(drop_down_bird, range_slider_year[0], range_slider_year[1])
    bird_instance = bird_object.get_state_data()
    bird_map_instance = Bird.map_graph(bird_instance)
    bird_map_instance.update_layout(transition_duration=500)

    route_object = Route(drop_down_bird, range_slider_year[0], range_slider_year[1], text_input_route) 
    route_instance = route_object.get_route_data()
    
    route_graph_instance = Route.year_graph(route_instance)
    route_graph_instance.update_layout(transition_duration=500)
    return bird_map_instance, route_graph_instance


#### Callbacks and updates of route counts
@app.callback(
    Output('route-count-total', 'children'),
    [Input('range_slider_year', 'value'),
    Input('drop_down_bird', 'value'),
    Input('text_input_route', 'value')])
def update_count(range_slider_year, drop_down_bird, text_input_route):
    route_object = Route(drop_down_bird, range_slider_year[0], range_slider_year[1], text_input_route) 
    route_instance = route_object.get_route_data()
    route_total = Route.route_sum(route_instance)
    return f'{route_total:.0f} species were counted.'

#### Callback and update of year selector
@app.callback(
    dash.dependencies.Output('output-container-range-slider', 'children'),
    [dash.dependencies.Input('range_slider_year', 'value')])
def update_slider(value):
    return ("You have selected the years " + str(value[0]) + " through " + str(value[1]) + ".")

#### Callback and update of selected bird
@app.callback(
    dash.dependencies.Output('output-container-drop-down', 'children'),
    [dash.dependencies.Input('drop_down_bird', 'value')])
def update_drop_down(value):
    return ("You have selected bird AOU # " + str(value) + ".")

#### Callback and update of Route that was entered
@app.callback(
    dash.dependencies.Output('output-container-route-input', 'children'),
    [dash.dependencies.Input('text_input_route', 'value')])
def update_route_input(value):
    return ("Route entered: " + str(value) + ".")

#### Callback and update of button 
@app.callback(
    dash.dependencies.Output('output-container-route-button', 'children'),
    [dash.dependencies.Input('submit_button', 'n_clicks')],
    [dash.dependencies.State('text_input_route', 'value'),
    dash.dependencies.State('drop_down_bird', 'value')])
def update_output(n_clicks, route_input, bird_input):
    return u'''
    You have selected bird AOU {}, the route {}, and the button was clicked {} times.
    '''.format(bird_input, route_input, n_clicks)

#### Callback and update of map click
@app.callback(
    Output('click-data', 'children'),
    [Input("map_route_counts", "clickData")])
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)













