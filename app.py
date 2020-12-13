# imports
import dash
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from markdown_helper import markdown_popup
import numpy as np
import pandas as pd
from dynamic_scheduling import dynamic_schedule, style_table

# initial table
df = pd.DataFrame().to_dict('records')


# main app
app = dash.Dash(__name__, external_scripts=['https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML'])
# app = dash.Dash(__name__, external_scripts=['https://cdn.jsdelivr.net/npm/mathjax@2.7.8/MathJax.js?config=TeX-MML-AM_CHTML'])
app.title = 'Dynamic Schedule'
server = app.server

def app_layout():
    
    app_layout = html.Div(id='main',children=[
        dcc.Interval(id='interval-updating-graphs', interval=1000, n_intervals=0),
        html.Div(id='top-bar'),
        html.Div(
            className='container',
            children=[
                html.Div(
                    id='left-side-column',
                    className='eight columns',
                    children=[
                        html.H4('Dynamic Schedule'),
                        html.P(
                            ['This webapp solves the minimization problem' +
                            r'$$\min_{t_1,\dots,t_n}\omega \sum_{i=1}^{n}\mathbb{E}I_i + (1 - \omega)\sum_{i=1}^{n}\mathbb{E}W_i,$$' +
                            r'where \(I_i\) and \(W_i\) are the idle time and waiting time associated to client \(i\), respectively. ' +
                            r'We schedule the jobs one by one: at time \(t_i\), i.e., at the moment client \(i\) enters the system, ' +
                            r'the optimal arrival epoch \(t_{i+1}\) of client \(i + 1\) is scheduled. This applet ' +
                            r'gives the optimal interarrival time \(\tau_{i}(k,u) := t_{i+1} - t_i\) given the current state \((k, u)\). ' +
                            'Click ', html.A('here', id='learn-more-button', n_clicks=0), ' to learn more.']
                        ),
                        html.P('Please fill in the parameters below.'),
                        html.Table(
                            id='my_table',
                            children=
                            # Header
                            [html.Tr([html.Th('Parameter'), html.Th('Value'), html.Th('Range'), html.Th('Explanation')])] +
                            # Body
                            [html.Tr([html.Td(r'\(\mathbb{E}B \)'),
                                html.Div(dcc.Input(id='mean', min=0.01, value=1, type='number')),
                                html.Td(r'\([0,\infty)\)'),
                                html.Td('mean')])] +
                            [html.Tr([html.Td(r'\(\mathbb{S}(B)\)'),
                                html.Div(dcc.Input(id='SCV', min=0.2, max=2, value=0.5, type='number')),
                                html.Td(r'\([0.2,2]\)'),
                                html.Td('SCV')])] +
                            [html.Tr([html.Td(r'\(\omega\)'),
                                dcc.Input(id='omega', min=0.1, max=0.9, value=0.5, type='number'),
                                html.Td(r'\((0,1)\)'),
                                html.Td('importance idle : waiting time')])] +
                            [html.Tr([html.Td(r'\(n\)'),
                                dcc.Input(id='n', min=1, max=19, step=1, value=15, type='number'),
                                html.Td(r'\([1,19]\)'),
                                html.Td('#clients to be scheduled')])] +
                            [html.Tr([html.Td(r'\(k\)'),
                                dcc.Input(id='k', min=0, max=8, step=1, value=0, type='number'),
                                html.Td(r'\([0,8]\)'),
                                html.Td('#clients in system')])] + 
                            [html.Tr([html.Td(r'\(u\)'),
                                dcc.Input(id='u', min=0, max=50, step=0.01, value=0, type='number'),
                                html.Td(r'\([0,50]\)'),
                                html.Td('service time client in service (so far)')])], style={'width': '100%'}
                        ),
                        html.Button(id='submit-button', n_clicks=0, children='Compute Appointment Schedule'),
                    ]
                ),
                html.Div(
                    id='right-side-column',
                    className='dynamic schedule',
                    children=[
                        html.Div(
                            dt.DataTable(
                                id='schedule_df',
                                data=df,
                                merge_duplicate_headers=True,
                                style_header={'textAlign': 'center', 'backgroundColor': '#f9f9f9', 'fontWeight': 'bold'},
                                style_cell={'textAlign': 'center'},
                            ),
                        ),
                    ],
                ),
            ],
        ),
        markdown_popup(),
        ])

    return app_layout

# learn more popup
@app.callback(
    Output('markdown', 'style'),
    [Input('learn-more-button', 'n_clicks'), Input('markdown_close', 'n_clicks')],
)
def update_click_output(button_click, close_click):

    ctx = dash.callback_context
    prop_id = ""
    if ctx.triggered:
        prop_id = ctx.triggered[0]['prop_id'].split(".")[0]

    if prop_id == 'learn-more-button':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# schedule
@app.callback(
    [Output('schedule_df', 'columns'), Output('schedule_df', 'style_data_conditional'), Output('schedule_df', 'data')],
    [Input('submit-button', 'n_clicks')],
    [State('mean', 'value'), State('SCV', 'value'), State('omega', 'value'),
     State('n', 'value'), State('u', 'value')], # State('k', 'value'), 
)
def updateTable(n_clicks, mean, SCV, omega, n, u):

    df = dynamic_schedule(mean, SCV, omega, n, u)
    
    df = pd.DataFrame(df, columns=range(1,n)).fillna('') # columns=range(1,n)
    df.loc[n,:] = range(1,n)
    df.index = list(range(1,n)) + ['i / k']


    df.index.name = 'i'
    df.reset_index(level=0, inplace=True)


    style_data = style_table(n)
    columns = [{'name': [r'Optimal interarrival times \(\tau_{i}(k,u)\)'], 'id': k} for k in df.keys()]

    return columns, style_data, df.to_dict('records')


app.layout = app_layout

if __name__ == '__main__':
  app.run_server()
