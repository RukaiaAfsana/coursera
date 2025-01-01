# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
# Get unique launch sites
launch_sites = spacex_df['Launch Site'].unique()
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites],
                                    value='ALL',
                                    placeholder="Select a Launch Site here",
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=spacex_df['Payload Mass (kg)'].min(),
                                    max=spacex_df['Payload Mass (kg)'].max(),
                                    step=1000,
                                    marks={i: str(i) for i in range(int(spacex_df['Payload Mass (kg)'].min()), 
                                                                    int(spacex_df['Payload Mass (kg)'].max()), 1000)},
                                    value=[spacex_df['Payload Mass (kg)'].min(), spacex_df['Payload Mass (kg)'].max()]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Aggregating data for all sites
        success_counts = spacex_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        fig = px.pie(success_counts, names='class', values='count', title='Total Success vs Failure Launches')
    else:
        # Filtering for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        fig = px.pie(success_counts, names='class', values='count', title=f'Success vs Failure for site {selected_site}')
    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    min_payload, max_payload = payload_range
    
    # Filtering the DataFrame based on the selected payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= min_payload) & 
                            (spacex_df['Payload Mass (kg)'] <= max_payload)]
    
    if selected_site != 'ALL':
        # Filtering for the selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    # Create scatter plot
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='class',
                     title=f"Launch Success vs Payload Mass for {selected_site if selected_site != 'ALL' else 'All Sites'}",
                     labels={'class': 'Launch Success (1 = Success, 0 = Failure)', 
                             'Payload Mass (kg)': 'Payload Mass (kg)'},
                     color_discrete_map={1: 'green', 0: 'red'})
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug = True)
