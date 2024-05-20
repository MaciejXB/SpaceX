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

dropdown_options = [{'label': 'All Sites', 'value': 'All Sites'}]

launch_sites_df = spacex_df.groupby(['Launch Site'], as_index=False).first()
for index, row in launch_sites_df.iterrows():
    dropdown_options.append({
        'label': row['Launch Site'],
        'value': row['Launch Site']
    })

# Create a dash application
app = dash.Dash(__name__)

# Create an app layouts
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboardssss',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Div([
                                    dcc.Dropdown(id='site-dropdown', 
                                                    options=dropdown_options,
                                                    value='All Sites',
                                                    style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'text-align' : 'center' })
                                ]),

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
                                    min=min_payload,
                                    max=max_payload,
                                    step=1000,
                                    value=[min_payload, max_payload]
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
def update_pie(launch_site):
    if launch_site == 'All Sites':
        pie_df = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        pie_chart = px.pie(pie_df, values='class', names='Launch Site', title="Total successful launches")
    else:
        pie_df = pd.DataFrame(columns=['Mission outcome', 'Count'])
        fails = spacex_df[spacex_df['Launch Site'] == launch_site][spacex_df['class'] == 0].shape[0]
        success = spacex_df[spacex_df['Launch Site'] == launch_site][spacex_df['class'] == 1].shape[0]
        fail_df = pd.DataFrame([{'Mission outcome': 'Fail', 'Count': fails}])
        success_df = pd.DataFrame([{'Mission outcome': 'Success', 'Count': success}])
        pie_df = pd.concat([pie_df, fail_df, success_df], ignore_index=True)
        pie_chart = px.pie(pie_df, values='Count', names='Mission outcome', title=f"Success vs. Failed at {launch_site}")
        pie_chart.update_layout(xaxis_title="Vehicle Type", yaxis_title="Adversadditure")

    return pie_chart

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), Input(component_id='payload-slider', component_property='value')]
)
def update_scatter(launch_site, payload_range):
    if launch_site == 'All Sites':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        scatter_chart = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='class', title='Payload Success Rate by Payload Mass')
        scatter_chart.update_layout(xaxis_title="Payload Mass (kg)", yaxis_title="Success / Failure")
    else:
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & (spacex_df['Payload Mass (kg)'] <= payload_range[1]) & (spacex_df['Launch Site'] == launch_site)]
        scatter_chart = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='class', title=f'Payload Success Rate by Payload Mass at {launch_site}')
        scatter_chart.update_layout(xaxis_title="Payload Mass (kg)",  yaxis_title="Success / Failure")
    
    return scatter_chart

# Run the app
if __name__ == '__main__':
    app.run_server()
