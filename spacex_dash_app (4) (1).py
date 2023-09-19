# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
            
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
        ],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True,
    ),
    
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={str(payload): str(payload) for payload in range(int(min_payload), int(max_payload)+1, 1000)},
        value=[min_payload, max_payload]
    ),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])
# Define the callback function
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, selected_payload_range):
    # Check if ALL sites were selected or just a specific launch site
    if selected_site == 'ALL':
        filtered_df = spacex_df # No filtering needed for 'ALL' sites
    else:
        # Filter the spacex_df for the selected launch site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
    
    # Filter the filtered_df based on the selected payload range
    filtered_df = filtered_df[
        (filtered_df['Payload Mass (kg)'] >= selected_payload_range[0]) &
        (filtered_df['Payload Mass (kg)'] <= selected_payload_range[1])
    ]
    
    # Create the scatter plot
    fig = px.scatter(
        data_frame=filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Payload vs Class with Booster Version Category'
    )
    
    return fig

# Callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Calculate success rates for all launch sites
        success_rates = spacex_df.groupby('Launch Site')['class'].mean()

        fig = go.Figure(data=[go.Pie(labels=success_rates.index, values=success_rates.values)])
        # fig.update_layout(title='Success Rate for All Launch Sites')

        return fig
    else:
        selected_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_count = selected_df[selected_df['class'] == 1]['class'].count()
        failed_count = selected_df[selected_df['class'] == 0]['class'].count()
        labels = ['Success', 'Failed']
        values = [success_count, failed_count]

        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        return fig

# Callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

# Run the app
if __name__ == '__main__':
    app.run_server()
