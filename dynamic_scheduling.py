import numpy as np
import pandas as pd
from io import StringIO
from urllib import request

def dynamic_schedule(mean, SCV, omega, n, i, k, u):
    """
    Computes the table of optimal interarrival times tau_{i}(k,u).
    """
    
    Delta = 0.01
    m = int(u / Delta)

    # retrieve files
    url_tau = f'Dyn-Sched-Data/master/omega-{round(omega,1)}/tau-SCV-{round(float(SCV),2)}-omega-{round(omega,1)}-n-20-m-{m}'
    url_xi = f'Dyn-Sched-Data/master/omega-{round(omega,1)}/xi-SCV-{round(float(SCV),2)}-omega-{round(omega,1)}-n-20-m-{m}'
    url_tau = 'https://raw.githubusercontent.com/Roshanmahes/' + url_tau.replace('.', '_') + '.csv'
    url_xi = 'https://raw.githubusercontent.com/Roshanmahes/' + url_xi.replace('.', '_') + '.csv'

    # create schedule
    file_tau = request.urlopen(url_tau).read().decode('utf-8')
    df = pd.read_csv(StringIO(file_tau), index_col='i').fillna('') * mean

    df = df.iloc[1-n:,:]
    df = df.where(np.tril(np.ones(df.shape)).astype(np.bool)).dropna(axis=1, how='all') #.fillna('')
    df.reset_index(level=0, inplace=True)
    df = df.astype(float).round(2).fillna('').astype(str)

    df.iloc[:,0] = [str(i) for i in range(1,n)] # range(1,n)
    df.loc[n,:] = [r'\(i\) \(/\) \(k\)'] + [str(i) for i in range(1,n)]
    df.index = list(range(1,n)) + ['i / k']

    # get cost
    file_xi = request.urlopen(url_xi).read().decode('utf-8')
    df_cost = pd.read_csv(StringIO(file_xi), index_col='i').fillna('')
    cost = df_cost.iloc[i-1-n,k-1]
    
    return df, cost


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
            'if': {'row_index': i, 'column_id': str(i+1)},
        } for i in range(n)
    ] + [
        {   # no border if i > k
            'if': {'row_index': i, 'column_id': str(i+j)},
            'border': '1px solid #ffffff',
        } for i in range(n) for j in range(2,n)
    ] + [
        {   # border if i == k
            'if': {'row_index': i, 'column_id': str(i+1)},
            'border': '1px solid #d5d5d5',
        } for i in range(n)
    ] + [
        {   # highlight row
            'if': {'row_index': i-1, 'column_id': str(l)},
            'background-color': '#e0f1f0',
        } for l in ['i'] + list(range(k))
    ] + [
        {   # highlight column
            'if': {'row_index': l, 'column_id': str(k)},
            'background-color': '#e0f1f0',
        } for l in range(i,n)
    ] + [
        {   # interarrival time tau_i(k,u)
            'if': {'row_index': i-1, 'column_id': str(k)},
            'background-color': '#8ed1ca',
            'border': '1px solid #028073',
        },
        {   # row index i
            'if': {'row_index': i-1, 'column_id': 'i'},
            'background-color': '#B7E1DD',
            'border': '1px solid #bbb',
        },
        {   # column index k
            'if': {'row_index': n-1, 'column_id': str(k)},
            'background-color': '#B7E1DD',
            'border': '1px solid #bbb',
        },
    ]

    return style_data_conditional
