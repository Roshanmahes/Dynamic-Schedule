# imports
import dash
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from markdown_helper import markdown_popup
import numpy as np
import pandas as pd
from adaptive_scheduling import Transient_IA
import plotly.graph_objs as go
import plotly.io as pio

pio.templates.default = 'plotly_white'


# initial table
n = 20
m = 0
Delta = 0.01

minima = [[None] * (n-1) for k in range(n)]

for i in range(n-1):
    for k in range(i+1):
        minima[i][k] = f'{round(12.78, 2):.2f}'

for i in range(n-1):
    minima[n-1][i] = i+1
        
# minima
df = pd.DataFrame(minima, index=list(range(1,n)) + ['i / k'], columns=range(1,n)).fillna('') # columns=range(1,n)
df.index.name = 'i'
df.reset_index(level=0, inplace=True)

# print(df)


# df = pd.DataFrame({r'Client (\(i\))': [''],
#                    r'Interarrival time (\(x_i\))': ['Computing appointment schedule...'],
#                    r'Arrival time (\(t_i\))': ['']})
df = df.to_dict('records')

# print(df)

# print(df[0].keys())

columns = [{'name': [r'Optimal Interarrival Times \(\tau_{i}(k)\)'], 'id': k} for k in df[0].keys()] #[{'name': [f'Appointment Schedule', k], 'id': k} for k in df[0].keys()]
#  'i' if k == 'i' else None

print(columns)

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
                            r'where $I_i$ and $W_i$ are the idle time and waiting time associated to client $i$, respectively. ' +
                            # r'The sequence of arrival epochs $t_1,\dots,t_n$ is called the schedule. ' +
                            r'We schedule the jobs one by one: at time $t_i$, i.e., at the moment client $i$ enters the system, ' +
                            r'the optimal arrival epoch $t_{i+1}$ of client $i + 1$ is scheduled. This applet ' +
                            r'produces the optimal arrival time $x_{i+1} := t_{i+1} - t_i$ given the current state $(k, u)$. ' +
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
                                dcc.Input(id='n', min=1, max=25, step=1, value=15, type='number'),
                                html.Td(r'\([1,25]\)'),
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
                                columns=columns,
                                data=df,
                                merge_duplicate_headers=True,
                                style_header={'textAlign': 'center', 'backgroundColor': '#f9f9f9', 'fontWeight': 'bold'},
                                style_cell={'textAlign': 'center'},
                                style_data_conditional=[
                                    {
                                        'if': {'state': 'selected'},
                                        'backgroundColor': '#e0f1f0',
                                        'border': '1px solid #028073',
                                    },
                                    {
                                        'if': {'column_id': 'i'},
                                        'background-color': '#FAFAFA',
                                        'fontWeight': 'bold',
                                    },
                                    {
                                        'if': {'column_id': 'i', 'state': 'selected'},
                                        'background-color': '#FAFAFA',
                                        'border': '1px solid #d5d5d5',
                                    },
                                    {
                                        'if': {'row_index': n-1},
                                        'background-color': '#FAFAFA',
                                        'fontWeight': 'bold',
                                    },
                                    {
                                        'if': {'row_index': n-1, 'state': 'selected'},
                                        'background-color': '#FAFAFA',
                                        'border': '1px solid #d5d5d5',
                                    },
                                ] + 
                                [
                                    {
                                        'if': {'row_index': i, 'column_id': i+1},
                                        'border': '1px solid #d5d5d5',
                                    } for i in range(n)
                                ] +
                                [
                                    {
                                        'if': {'row_index': i, 'column_id': i+j},
                                        'border': '1px solid #ffffff',
                                    } for i in range(n) for j in range(2,n)
                                ] +
                                [
                                    {
                                        'if': {'row_index': i, 'column_id': i+j, 'state': 'selected'},
                                        'background-color': '#ffffff',
                                        'border': 'transparent',
                                    } for i in range(n) for j in range(2,n)
                                ] +
                                [
                                    {
                                        'if': {'row_index': i, 'column_id': i+1},
                                        'border': '1px solid #d5d5d5',
                                    } for i in range(n)
                                ],
                            ),
                        ),
                        # html.Div([
                        #     dcc.Graph(
                        #         id='graph_df',
                        #         figure = no_fig,
                        #         config={'displayModeBar': False},
                        #     )], className='graphic'),
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

# schedule & graph
# @app.callback(
#     [Output('schedule_df', 'columns'), Output('schedule_df', 'data'), Output('graph_df', 'figure')],
#     [Input('submit-button', 'n_clicks')],
#     [State('mean', 'value'), State('SCV', 'value'), State('omega', 'value'),
#      State('n', 'value'), State('wis', 'value'), State('u', 'value')],
# )
# def updateTable(n_clicks, mean, SCV, omega, n, wis, u):

#     N = n + wis
#     tol = None if N < 15 else 1e-4
#     u = u / mean

#     if not u and not wis:
#         N = N - 1
#         x, y = Transient_IA(SCV, u, omega, N, [], wis, tol)
#         x = np.pad(x, (1,0))
#     else:
#         x, y = Transient_IA(SCV, u, omega, N, [], wis, tol)

#     x = x * mean

#     df = pd.DataFrame({r'Client (\(i\))': list(np.arange(1,len(x)+1)),
#         r'Interarrival time (\(x_i\))': [f'{np.round(i,4):.4f}' for i in x],
#         r'Arrival time (\(t_i\))': [f'{np.round(i,4):.4f}' for i in np.cumsum(x)]})

#     figure = go.Figure(data=[go.Scatter(x=df.iloc[:,0], y=df.iloc[:,1], marker={'color': '#028073'})],
#         layout=go.Layout(
#             title=go.layout.Title(text=r'$\text{Optimal interarrival times } (x_i)$', x=0.5, xanchor='center'), # Plotly 4
#             # title=r'$\text{Optimal interarrival times } (x_i)$', # Plotly 2
#             xaxis={'title': r'$\text{Client } (i)$', 'tick0': 1, 'dtick': 1, 'range': [0.7,len(x) + 0.3]},
#             yaxis={'title': r'$\text{Interarrival time } (x_i)$'},
#             paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'))
    
#     columns = [{'name': [f'Appointment Schedule (Cost: {y * mean:.4f})', k], 'id': k} for k in df.columns]

#     return columns, df.to_dict('records'), figure


app.layout = app_layout

if __name__ == '__main__':
  app.run_server()
