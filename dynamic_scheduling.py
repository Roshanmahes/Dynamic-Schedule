import numpy as np
import pandas as pd
from openpyxl import load_workbook

def dynamic_schedule(mean, SCV, omega, n, u, prefix='tau'):
    
    Delta = 0.01
    m = int(u / Delta)

    file_name = f'-SCV-{round(SCV,2)}-omega-{round(omega,1)}-n-20-m-250'
    file_name = 'output/' + prefix + file_name.replace('.', '_') + '.xlsx'
    work_sheets = load_workbook(file_name).worksheets

    df_list = []

    for i in range(n):

        df_sheet = pd.DataFrame(work_sheets[i-n].values)
        df_row = df_sheet.iloc[m,:i+1] * mean
        df_list += [[f'{df_row[i]:.2f}' for i in range(len(df_row))]]

    df = pd.DataFrame(df_list, columns=range(1,n+1)).fillna('')
    df.index = range(1,n+1)

    return df

def style_table(n):

    style_data_conditional = [
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
    ] + [
        {
            'if': {'row_index': i, 'column_id': i+1},
            'border': '1px solid #d5d5d5',
        } for i in range(n)
    ] + [
        {
            'if': {'row_index': i, 'column_id': i+j},
            'border': '1px solid #ffffff',
        } for i in range(n) for j in range(2,n)
    ] + [
        {
            'if': {'row_index': i, 'column_id': i+j, 'state': 'selected'},
            'background-color': '#ffffff',
            'border': 'transparent',
        } for i in range(n) for j in range(2,n)
    ] + [
        {
            'if': {'row_index': i, 'column_id': i+1},
            'border': '1px solid #d5d5d5',
        } for i in range(n)
    ]

    return style_data_conditional