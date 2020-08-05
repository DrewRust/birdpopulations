# Outside Imports
import dash
import glob
import plotly
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

# 2 column layout. 1st column width = 4/12
# https://dash-bootstrap-components.opensource.faculty.ai/l/components/layout


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
                          size_max=25, zoom = 5, center= {"lat": 39.25, "lon": -84.8}, width = 700, height = 500)
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
    fig = px.bar(df, y='SpeciesTotal', x='Year', text='SpeciesTotal', width=700, height=500)
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




#### YOU NEED YOUR OBJECTS TO TO BE CHANGABLE
# bird_obj = Bird(3390, 2009, 2018)
# bird_obj_inst = bird_obj.get_state_data()
# AOU_num = bird_obj_inst.at[0, "AOU"]
# print("This map is showing route counts for bird species id " + str(AOU_num))
# bird_obj_inst_grph = Bird.map_graph(bird_obj_inst)

# route_obj = Route(3390, 1966, 2018, "SHILOH") 
# route_obj_inst = route_obj.get_route_data()
# route_name = route_obj_inst.at[0, "RouteName"]
# print("This bar plot is showing all the available yearly counts for route " + str(route_name))
# route_obj_inst_grph = Route.year_graph(route_obj_inst)



column1 = dbc.Col(
    [
        dcc.Markdown(
            """
        
            ## Bird Census Route Counts

            The Breeding Bird Survey is an ongoing census of North American Birds.
            First use the range slider to choose the years you would like to look at.  Next, select
            a species of bird or view the current one. 
            
            Finally, zoom in on the route names and choose a route name. Spell it correctly 
            in the text field to see your selected yearly totals for that route.
            It should add up to the route total count for the years you're looking at.  Some
            years no birds are counted and of course some routes have bigger bird populations.
            """
        ),
    #### This is a working copy but I improved it down below even though the Div was ..
    #### ... acting weird for the range slider it works
    # html.Div([
    # html.Label('Years:')], 
    # style={'marginBottom': 15, 'marginTop': 25}),
    # dcc.RangeSlider(
    #   id="range_slider",
    #   marks={i: '{}'.format(i) for i in range(1968, 2019, 10)},
    #   min=1966,
    #   max=2018,
    #   value=[1966, 2018]
    #   ),


    html.Div([
    html.H5('Years:'), 
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
    ], style={'marginBottom': 25, 'marginTop': 25}),

#### NEED MORE BIRDS
    html.Div([
    html.H5('Species:'),
    dcc.Dropdown(
      id="drop_down_bird",
      options=[
            {'label': "American Goldfinch", 'value': 5290},
            {'label': "Carolina Chikadee", 'value': 7360},
            {'label': "Cooper's Hawk", 'value': 3330},
            {'label': "Eastern Bluebird", 'value': 7660},
            {'label': "Kentucky Warbler", 'value': 6770},
            {'label': "Northern Bobwhite", 'value': 2890},
            {'label': "Prothonotary Warbler (Golden Swamp Warbler)", 'value': 6370},  
            {'label': "Red Tailed Hawk", 'value': 3370},
            {'label': "Red Shouldered Hawk", 'value': 3390},
            {'label': "Ruby Throated Hummingbird", 'value': 4280}
        ],
      value=5290,
      style={"margin-top": "15px", "margin-bottom": "20px"}
    ),
    html.Div(id='output-container-drop-down')
   ], style={'marginBottom': 25, 'marginTop': 25}),

# html.Div([
html.Div([
  html.Div([
    html.H5('Route:')
    ]),
    dcc.Input(
     value="Type in Route Here",
     id="text_input_route", 
     type='text', 
    #  style={"margin-top": "15px", "margin-bottom": "25px", "margin-left": "20px"}
    style={"margin-top": "15px", "margin-bottom": "25px"}
     ),
   html.Div(id='output-container-route-input')
    ], style={'marginBottom': 25, 'marginTop': 25}),
    #   html.Div(id='output_container_route_sum')
    # ], style={'marginBottom': 25, 'marginTop': 25}),
    # html.H6('Route Total: ', className='mb-5'), 
    html.Div([
    html.Div(id='route-count-total')], 
    style={'marginBottom': 25, 'marginTop': 25}),

        dcc.Markdown(
            """
        
            ##### Work in Progress..

            I've only included a beginning number bird species at this stage of the app development.
            I would ultimately like to include all US States and Canadian Provinces.  
            The program should run for all state, province, and territory files 
            and ideally will be able to make predictions on future populations.
            """
        ),


    ],
    md=4,
)


###### IMPORTANT this is where you call the dataframe if you use it
# gapminder = px.data.gapminder()
# fig = px.scatter(gapminder.query("year==2007"), x="gdpPercap", y="lifeExp", size="pop", color="continent",
#            hover_name="country", log_x=True, size_max=60)


column2 = dbc.Col(
    [
        ###### IMPORTANT
        # dcc.Graph(figure=graph1),
        # dcc.Graph(figure=map_red_shldr),
        dcc.Graph(id="map_route_counts"),
        dcc.Graph(id="yearly_graph_counts"),
        # html.Div([
        # html.Label("Route total cout: ", id="route_total_sum")
        # ]),
        # dcc.Graph(id="graph-with-input-box"),
    ]
)

# The input variables and the parameters don't have to match it's just an indexed list
# but I find it easier
@app.callback(
    #### This works but added the other output and input
    # Output('map_route_counts', 'figure'),
    # [Input('range_slider_year', 'value'),
    # Input('drop_down_bird', 'value')])

    #### Trying to figure out why the yearly outputs aren't working
    #### route_total_sum doesn't work (I want to the route total sum to print out next to route and to update)
    
    # [Output('map_route_counts', 'figure'),
    # Output('yearly_graph_counts', 'figure'),
    # dash.dependencies.Output('route_total_sum', 'value')],
    # [Input('range_slider_year', 'value'),
    # Input('drop_down_bird', 'value'),
    # Input('text_input_route', 'value')])

    [Output('map_route_counts', 'figure'),
    Output('yearly_graph_counts', 'figure')],
    [Input('range_slider_year', 'value'),
    Input('drop_down_bird', 'value'),
    Input('text_input_route', 'value')])

    # [Output('map_route_counts', 'figure'),
    # Output('yearly_graph_counts', 'figure'),
    # Output('route_total_sum', 'value')],
    # [Input('range_slider_year', 'value'),
    # Input('drop_down_bird', 'value'),
    # Input('text_input_route', 'value')])

    # Output('yearly_graph_counts', 'figure'),
    # [Input('range_slider_year', 'value'),
    # Input('drop_down_bird', 'value'),
    # Input('text_input_route', 'value')])

def update_figure(range_slider_year, drop_down_bird, text_input_route):
    #### Trying to figure out if the years can work with the routes graph
    bird_object = Bird(drop_down_bird, range_slider_year[0], range_slider_year[1])
    bird_instance = bird_object.get_state_data()
    bird_map_instance = Bird.map_graph(bird_instance)
    bird_map_instance.update_layout(transition_duration=500)
    #### This would go with the code above if I only had the bird object (map_route_counts)
    # return bird_map_instance

    route_object = Route(drop_down_bird, range_slider_year[0], range_slider_year[1], text_input_route) 
    route_instance = route_object.get_route_data()
    
    #### Doesn't work get route total count
    # route_total = Route.route_sum(route_instance)
    # route_total.update_layout(transition_duration=500)
    # route_total_print = ("This is the route count sum: " + str(route_total))
    #### Doesn't work
    
    # route_total.update_layout(transition_duration=500)
    #### This is what I'm working on I want it to get the total route count for the years selected
    #### So it matches with the map graph
    route_graph_instance = Route.year_graph(route_instance)
    route_graph_instance.update_layout(transition_duration=500)
    return bird_map_instance, route_graph_instance
    # return bird_map_instance, route_graph_instance, route_total
    # return route_graph_instance


@app.callback(
    Output('route-count-total', 'children'),
    [Input('range_slider_year', 'value'),
    Input('drop_down_bird', 'value'),
    Input('text_input_route', 'value')],
)
def update_count(range_slider_year, drop_down_bird, text_input_route):
    route_object = Route(drop_down_bird, range_slider_year[0], range_slider_year[1], text_input_route) 
    route_instance = route_object.get_route_data()
    route_total = Route.route_sum(route_instance)
    return f'{route_total:.0f} species were counted'



#### could probably add all these together but it works just fine for now
@app.callback(
    dash.dependencies.Output('output-container-range-slider', 'children'),
    [dash.dependencies.Input('range_slider_year', 'value')])
def update_slider(value):
    return ("You have selected the years " + str(value[0]) + " through " + str(value[1]))

@app.callback(
    dash.dependencies.Output('output-container-drop-down', 'children'),
    [dash.dependencies.Input('drop_down_bird', 'value')])
def update_drop_down(value):
    return ("You have selected bird AOU # " + str(value))

@app.callback(
    dash.dependencies.Output('output-container-route-input', 'children'),
    [dash.dependencies.Input('text_input_route', 'value')])
def update_route_input(value):
    return ("Route entered: " + str(value))

#### Doesn't work
# @app.callback(
#     dash.dependencies.Output('output_container_route_sum', 'children'),
#     [dash.dependencies.Input('route_total_sum', 'value')])
# def update_route_sum(value):
#     return ("Route total: " + str(value))

#### THIS ONE WORKS 
# @app.callback(
#     Output('graph-with-drop-down', 'figure'),
#     [Input('drop_down', 'value')])
# def update_figure(drop_down_bird):
#     bird_object = Bird(drop_down_bird, 2009, 2018)
#     bird_instance = bird_object.get_state_data()
#     bird_map_instance = Bird.map_graph(bird_instance)
#     bird_map_instance.update_layout(transition_duration=500)
#     return bird_map_instance

#### THIS doesn't work but it has the route instance I needed
# @app.callback(
#     [Output('graph-with-drop-down', 'figure'),
#     Output('graph-with-input-box', 'figure')]
#     [Input('drop_down', 'value'),
#     Input('range_slider', 'value'),
#     Input('input_box', 'value')])
# def update_route(drop_down_bird, input_box_route):
#     route_object = Route(drop_down_bird, 1966, 2018, input_box_route) 
#     route_instance = route_object.get_route_data()
#     route_graph_instance = Route.year_graph(route_instance)
#     route_graph_instance.update_layout(transition_duration=500)
#     return route_graph_instance


layout = dbc.Row([column1, column2])

























