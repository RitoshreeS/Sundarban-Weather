#Import necessary libraries
from flask import json # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
import plotly.express as px # type: ignore
import plotly.graph_objects as go # type: ignore
from plotly.subplots import make_subplots # type: ignore
from dash import Dash, html, dcc, Input, Output, callback # type: ignore
from dash import Dash, html, dcc # type: ignore
from dash.dependencies import Input, Output # type: ignore
import requests # type: ignore
from datetime import datetime
import geopandas as gpd


df_weather = pd.read_csv('D:/wwf india/Website Dashboard/plotly-dash/Weather.csv')

# Create the Dash app
app = Dash(__name__)

# Define image source file path for the WWF India logo
image_link = 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/World_Wide_Fund_for_Nature_logo.svg/1200px-World_Wide_Fund_for_Nature_logo.svg.png'

# Create the app layout
app.layout = html.Div(style={'backgroundColor': 'black', 'border': 'ridge', 'padding': '10px'}, children=[
    # Button with WWF India logo
    html.Button(
        id='wwf-button',
        children=[
            html.Img(src=image_link, alt='WWF India Logo', style={'width': '100%', 'height': 'auto'}),
        ],
        style={'border': 'none', 'background': 'transparent', 'cursor': 'pointer', 'padding': '0px'}
    ),
    html.H1('Sundarbans Weather Dashboard', style={'textAlign': 'center', 'color': 'White', 'font-size': 36}),
    # Area for the graphs
    html.Div(dcc.Graph(id='plot1'), style={'border': 'ridge', 'padding': '10px', 'backgroundColor': 'black','height': '1000px'}),
    html.Div(style={'display': 'flex', 'justify-content': 'center'}, children=[
        html.Div(dcc.Graph(id='plot2'), style={'border': 'ridge', 'padding': '10px', 'backgroundColor': 'black', 'width': '50%'}),
        html.Div(dcc.Graph(id='plot3'), style={'border': 'ridge', 'padding': '10px', 'backgroundColor': 'black', 'width': '50%'})
    ]),
    html.Div(style={'display': 'flex', 'justify-content': 'center'}, children=[
        html.Div(dcc.Graph(id='plot4'), style={'border': 'ridge', 'padding': '10px', 'backgroundColor': 'black', 'width': '50%'}),
        html.Div(dcc.Graph(id='plot5'), style={'border': 'ridge', 'padding': '10px', 'backgroundColor': 'black', 'width': '50%'})
    ])
])

# Create callback decorator
@app.callback(
    [Output(component_id='plot1', component_property='figure'),
     Output(component_id='plot2', component_property='figure'),
     Output(component_id='plot3', component_property='figure'),
     Output(component_id='plot4', component_property='figure'),
     Output(component_id='plot5', component_property='figure')],
    [Input(component_id='wwf-button', component_property='n_clicks')]
)


def update_graphs(n_clicks):
   # Load the GeoJSON file using geopandas
    gdf = gpd.read_file("D:/wwf india/Website Dashboard/plotly-dash/Polygon/SB_Landscape_Boundary.shp.geojson")

    # Filter the GeoDataFrame to include only the desired values of "sdtname"
    filtered_gdf = gdf[gdf['sdtname'].isin(['Gosaba', 'Patharpratima', 'Kultali'])]

    # Sample data for demonstration
    block_data = {
        'BLOCK': ['Patharpratima', 'Kultali', 'Gosaba'],
        'LATITUDE': [21.79206941, 21.8820151, 22.16557075],
        'LONGITUDE': [88.3555912, 88.5265151, 88.80817531],
    }
    df_blocks = pd.DataFrame(block_data)

    # Define the OpenWeatherMap API endpoint
    API_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"

    # Define the API parameters for each block
    weather_data = []
    for idx, row in df_blocks.iterrows():
        lat, lon = row['LATITUDE'], row['LONGITUDE']
        block = row['BLOCK']

        API_PARAMS = {
            "lat": lat,
            "lon": lon,
            "units": "metric",
            "appid": "419c843a9bee437e8437ad22e1c4288e",  # Replace with your OpenWeatherMap API key
            "cnt": 10,  # Number of forecast entries (max is 40)
        }

        # Fetch real-time 10-day weather forecast data for each block
        response = requests.get(API_ENDPOINT, params=API_PARAMS)
        forecast_data = response.json()

        # Extract the weather forecast data for each block
        for forecast in forecast_data['list']:
            weather_data.append({
                'Block': block,
                'Date': datetime.fromtimestamp(forecast['dt']).strftime('%a %b %d %H:%M'),
                'Weather': forecast['weather'][0]['description'],
                'Temperature': forecast['main']['temp'],
                'Humidity': forecast['main']['humidity'],
                'Wind Speed': forecast['wind']['speed'],
                'Pressure': forecast['main']['pressure'],
            })

    # Create DataFrame for the weather forecast data
    df_forecast = pd.DataFrame(weather_data)
    
    # Filter the GeoDataFrame to include only the desired values of "sdtname"
    filtered_gdf = gdf[gdf['sdtname'].isin(['Gosaba', 'Patharpratima', 'Kultali'])]
    

    # Plot the GeoDataFrame using Plotly Express
    fig1 = px.choropleth_mapbox(filtered_gdf, 
                                geojson=filtered_gdf.geometry, 
                                locations=filtered_gdf.index, 
                                color='sdtname',
                                mapbox_style="open-street-map",
                                center={"lat": filtered_gdf.centroid.y.mean(), "lon": filtered_gdf.centroid.x.mean()},
                                zoom=8,
                                opacity=0.5,
                                hover_name='sdtname',
                
                            )
    fig1.update_geos(fitbounds="locations", visible=False)

    # Add weather data as hover text on the polygons
    for idx, row in filtered_gdf.iterrows():
        block_forecast = df_forecast[df_forecast['Block'] == row['sdtname']]
        hover_text = "<b>Date:</b> " + block_forecast['Date'] + "<br>" + \
                    "<b>Weather:</b> " + block_forecast['Weather'] + "<br>" + \
                    "<b>Temperature:</b> " + block_forecast['Temperature'].astype(str) + "°C<br>" + \
                    "<b>Humidity:</b> " + block_forecast['Humidity'].astype(str) + "%<br>" + \
                    "<b>Wind Speed:</b> " + block_forecast['Wind Speed'].astype(str) + " m/s<br>" + \
                    "<b>Pressure:</b> " + block_forecast['Pressure'].astype(str) + " hPa<br>"
        
        fig1.add_trace(go.Scattermapbox(
            lon=[row['geometry'].centroid.x],
            lat=[row['geometry'].centroid.y],
            mode='markers',
            marker=dict(size=0),
            hoverinfo='text',
            text=hover_text,
            hoverlabel=dict(bgcolor='white', font=dict(color='black')),
            showlegend=False
        ))
    fig1.update_layout(height=1000)


    # Create a Plotly figure for plot2
    fig_plot2 = make_subplots(rows=1, cols=1, subplot_titles=("Temperature Data"))

    # Define colors for each block
    colors = {'Gosaba': 'red', 'Kultali': 'blue', 'Patharpratima': 'green'}

    # Add traces for min and max temperature for each block
    for block, color in colors.items():
        block_df = df_weather[df_weather['BLOCK'] == block]
        fig_plot2.add_trace(go.Scatter(x=block_df['DATES'], y=block_df['Temperature-Advisory Data'],
                                    mode='lines', name=f'{block} - Advisory Data', line=dict(color=color)),
                            row=1, col=1)
        fig_plot2.add_trace(go.Scatter(x=block_df['DATES'], y=block_df['Temperature-Realtime Data'],
                                    mode='lines', name=f'{block} - Realtime Data', line=dict(color=color, dash='dash')),
                            row=1, col=1)

        # Update layout for plot2
        fig_plot2.update_layout(title="Temperature Data",
                                xaxis_title="Date",
                                yaxis_title="Temperature (°C)",
                                template='plotly_dark',
                                font=dict(
                                    family="Arial, sans-serif",
                                    size=14,  # Increase font size to 14
                                    color="white"
                                )
                                )

    # Add dropdown menu for block selection
    buttons = []
    for block in colors.keys():
        visible_traces = [i for i, trace in enumerate(fig_plot2.data) if block in trace.name]
        buttons.append(dict(label=block,
                            method='update',
                            args=[{'visible': [True if i in visible_traces else False for i in range(len(fig_plot2.data))]}]))

    fig_plot2.update_layout(updatemenus=[dict(buttons=buttons,
                                            direction="down",
                                            pad={"r": 10, "t": 10},
                                            showactive=True,
                                            x=0.1,
                                            xanchor="left",
                                            y=1.1,
                                            yanchor="top")])

        # Create a Plotly figure for plot3 (Humidity Variation)
    fig_plot3 = make_subplots(rows=1, cols=1, subplot_titles=("Humidity Data"))

    # Define colors for each block
    colors = {'Gosaba': 'red', 'Kultali': 'blue', 'Patharpratima': 'green'}

    # Add traces for min and max humidity for each block
    for block, color in colors.items():
        block_df = df_weather[df_weather['BLOCK'] == block]
        fig_plot3.add_trace(go.Scatter(x=block_df['DATES'], y=block_df['Humidity-Advisory Data'],
                                    mode='lines', name=f'{block} - Advisory Data', line=dict(color=color)),
                            row=1, col=1)
        fig_plot3.add_trace(go.Scatter(x=block_df['DATES'], y=block_df['Humidity- Realtime Data'],
                                    mode='lines', name=f'{block} - Realtime Data', line=dict(color=color, dash='dash')),
                            row=1, col=1)

    # Update layout for plot3
    fig_plot3.update_layout(title="Humidity Data",
                            xaxis_title="Date",
                            yaxis_title="Humidity (%)",
                            template='plotly_dark',
                            font=dict(
                                family="Arial, sans-serif",
                                size=14,  # Increase font size to 14
                                color="white"
                            ))

    # Add dropdown menu for block selection
    buttons = []
    for block in colors.keys():
        visible_traces = [i for i, trace in enumerate(fig_plot3.data) if block in trace.name]
        buttons.append(dict(label=block,
                            method='update',
                            args=[{'visible': [True if i in visible_traces else False for i in range(len(fig_plot3.data))]}]))

    fig_plot3.update_layout(updatemenus=[dict(buttons=buttons,
                                            direction="down",
                                            pad={"r": 10, "t": 10},
                                            showactive=True,
                                            x=0.1,
                                            xanchor="left",
                                            y=1.1,
                                            yanchor="top")])

    
    # Create line graph for plot4 (Rainfall Data)
    fig_plot4 = px.line(df_weather, x='DATES', y='PRECIPITATION(mm)', color='BLOCK',
                        title='Rainfall Data', labels={'DATES': 'Date', 'PRECIPITATION(mm)': 'Precipitation (mm)'})

    # Update layout for plot4 to set the background color to black
    fig_plot4.update_layout(
        plot_bgcolor='black',  # Set plot background color
        paper_bgcolor='black',  # Set paper background color (outside plot area)
        font=dict(color='white', size=15),  # Set font color to white for better visibility on dark background,
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.3)'),  # Fade x-axis grid color (white with 30% opacity)
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.3)')  # Fade y-axis grid color (white with 30% opacity)
    )

    # Define the wind direction order
    wind_direction_order = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

    # Create a Plotly figure for plot5 (Wind rose plot)
    blocks = ['Gosaba', 'Patharpratima', 'Kultali']
    filtered_df = df_weather[df_weather['BLOCK'].isin(blocks)].sort_values(by='STRENGTH')

    # Calculate the color scale based on wind speed with a difference of 3
    max_wind_speed = filtered_df['WIND SPEED(km/h)'].max()
    color_scale = ['#f8f8ff', '#cce6ff', '#99ccff', '#66b3ff', '#3399ff', '#0066cc']

    # Initialize a list to hold traces for each block
    traces = []
    # Create traces for each block with color-coded bars based on wind speed
    for block in blocks:
        block_df = filtered_df[filtered_df['BLOCK'] == block]
        # Sort theta values based on wind_direction_order
        sorted_theta = sorted(block_df['WIND DIRECTION'], key=lambda x: wind_direction_order.index(x))
        trace = go.Barpolar(
            r=block_df['WIND SPEED(km/h)'],
            theta=sorted_theta,  # Use sorted theta values
            name=block,
            customdata=block_df['DATES'],  # Use DATES column as custom data
            hovertemplate='<b>%{fullData.name}</b><br>' +
                        'Date: %{customdata}<br>' +  # Update customdata reference
                        'Wind Speed: %{r} km/h<br>' +
                        'Wind Direction: %{theta}<extra></extra>',
            marker_color=block_df['WIND SPEED(km/h)'],  # Color based on wind speed
            marker=dict(colorscale=color_scale, cmin=0, cmax=max_wind_speed, colorbar=dict(title='Wind Speed(km/h)')),
            hoverlabel=dict(font=dict(size=18))  # Increase font size of hover labels
        )
        traces.append(trace)

    # Create the wind rose figure using the traces
    fig_plot5 = go.Figure(traces)

    # Define the dropdown menu for blocks selection
    dropdown_menu = []
    for trace, block in zip(traces, blocks):
        dropdown_menu.append(dict(
            args=[{"visible": [True if trace == t else False for t in fig_plot5.data]}],
            label=block,
            method="update"
        ))

    # Update layout to include the dropdown menu and color bar
    fig_plot5.update_layout(
        updatemenus=[
            dict(
                
                buttons=dropdown_menu,
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.1,
                yanchor="top"
            ),
        ],
        polar=dict(
            radialaxis=dict(visible=True, tickvals=[], ticktext=[]),  # Remove default tick values and labels
            angularaxis=dict(showline=False, visible=True)  # Adjust angular axis
        ),
        autosize=False,
        width=900,  # Adjust width as needed
        height=600,  # Adjust height as needed
        font=dict(size=16),  # Increase font size
        template='plotly_dark',  # Use Plotly's dark theme
        title='WIND SPEED AND DIRECTION',  # Add the title
    )



    return fig1, fig_plot2, fig_plot3, fig_plot4, fig_plot5  # Replace None with other figures as needed



# Run the app and open it in a new tab
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)



