# Imports from 3rd party libraries
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

# Imports from this application
from app import app

# 2 column layout. 1st column width = 4/12
# https://dash-bootstrap-components.opensource.faculty.ai/l/components/layout
column1 = dbc.Col(
    [
        dcc.Markdown(
            """
        
            ## Let's Take a Look at Bird Populations..


            ##### ..Using census data gathered by the North American Breeding Bird Survey such as census route counts by location and year. 
            

            Ultimately this app will be able to show if a species 
            is going up or down in population and help raise awareness about bird populations.
            We can use this app to predict when a population will be endangered,
            or hopefully see successful bird conservation stories or adaptations.

            This App is still a work in progress..

            """
        ),
        dcc.Link(dbc.Button("Bird Census Map", color='primary'), href='/route_map_counts')
    ],
    md=4,
)

# gapminder = px.data.gapminder()
# fig = px.scatter(gapminder.query("year==2007"), x="gdpPercap", y="lifeExp", size="pop", color="continent",
#            hover_name="country", log_x=True, size_max=60)



# column2 = dbc.Col(
#     [
#         dcc.Graph(figure=fig),
#     ]
# )

# layout = dbc.Row([column1, column2])

column2 = dbc.Col(
    # https://unsplash.com/photos/T6zSVMTUU0Q
    [
        html.Img(src='assets/photographer-jim-strasma-unsplash.jpg', className='img-fluid')
    ]
)


layout = dbc.Row([column1, column2])
