import numpy as np
import pandas as pd
from openpyxl import load_workbook

def dynamic_schedule(mean, SCV, omega, n, u, prefix='tau'):
    """
    Computes the table of optimal interarrival times tau_{i}(k,u).
    """
    
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

def style_table(n, i, k):
    """
    Styles the table of the interarrival times.
    """

    style_data_conditional = [
        {   # remove animation when selected
            'if': {'state': 'selected'},
            'background-color': 'inherit !important',
            'border': 'inherit !important',
        },
        {   # row header
            'if': {'column_id': 'i'},
            'background-color': '#FAFAFA',
            'fontWeight': 'bold',
        },
        {   # column header
            'if': {'row_index': n-1},
            'background-color': '#FAFAFA',
            'fontWeight': 'bold',
        },
    ] + [
        {   # border if i == k
            'if': {'row_index': i, 'column_id': i+1},
        } for i in range(n)
    ] + [
        {   # no border if i > k
            'if': {'row_index': i, 'column_id': i+j},
            'border': '1px solid #ffffff',
        } for i in range(n) for j in range(2,n)
    ] + [
        {   # border if i == k
            'if': {'row_index': i, 'column_id': i+1},
            'border': '1px solid #d5d5d5',
        } for i in range(n)
    ] + [
        {   # highlight row
            'if': {'row_index': i-1, 'column_id': l},
            'background-color': '#e0f1f0',
        } for l in ['i'] + list(range(k))
    ] + [
        {   # highlight column
            'if': {'row_index': l, 'column_id': k},
            'background-color': '#e0f1f0',
        } for l in range(i,n)
    ] + [
        {   # interarrival time tau_i(k,u)
            'if': {'row_index': i-1, 'column_id': k},
            'background-color': '#8ed1ca',
            'border': '1px solid #028073',
        },
        {   # row index i
            'if': {'row_index': i-1, 'column_id': 'i'},
            'background-color': '#B7E1DD',
            'border': '1px solid #bbb',
        },
        {   # column index k
            'if': {'row_index': n-1, 'column_id': k},
            'background-color': '#B7E1DD',
            'border': '1px solid #bbb',
        },
    ]

    return style_data_conditional
