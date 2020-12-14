import dash_html_components as html
import dash_core_components as dcc
from textwrap import dedent

def markdown_popup():
    return html.Div(
        id='markdown',
        className='modal',
        style={'display': 'none'},
        children=(
            html.Div(
                className='markdown-container',
                children=[
                    html.Div(
                        className='close-container',
                        children=html.Button(
                            'Close',
                            id='markdown_close',
                            n_clicks=0,
                            className='closeButton',
                        ),
                    ),
                    html.Div(
                        className='markdown-text',
                        children=[
                            dcc.Markdown(r'##### What am I looking at?'),
                            html.P(r'This app finds an optimal dynamic schedule for \(n\) clients, in the sense that it minimizes the objective function ' +
                                   r'$$\sum_{i=1}^{n}\omega\mathbb{E}I_i + (1-\omega)\mathbb{E}W_i.$$' +
                                   r'In here, \(I_i\) is the idle time prior to the arrival of client \(i\) and \(W_i\) is the waiting time of ' +
                                   r'client \(i\). The factor \(\omega\) reflects the relative importance of both components. The jobs are scheduled one by ' +
                                   r'one: at the moment that client \(i\) enters the system, the (inter)arrival epoch \(\tau_{i}(k,u)\) of client \(i+1\) is ' +
                                   r'scheduled. The schedule makes use of the relevant information available at this time point, i.e., the total number ' +
                                   r'of clients \(k\) in the system and the time \(u\) that the currently served client is yet in service. By modeling our ' +
                                   r'environment as a Markov Decision Process (MDP), the Bellman equation yields an expression for the optimal (expected) cost: ' +
                                   r'$$C_i^{\star}(k,u) := \inf_{t\geq 0}C_{i}(t,k,u) = ' +
                                   r'\inf_{t\geq 0}\sum_{\ell=1}^{k+1}\int_{0}^{\infty}(r_{k\ell,uv,i}(t) + C_{i+1}^{\star}(\ell,v))p_{k\ell,uv,i}(t)\,\mathrm{d}v.$$' +
                                   r'The \(t \geq 0\) that minimizes this expression is then the optimal interarrival time \(\tau_{i}(k,u)\).'),
                            html.P(r'The minimization is done by performing a so-called phase-type fit. The scheduler inserts the mean and squared ' +
                                   r'coefficient of variation (that is, the ratio of the variance to the mean) of the service time \(B\) of the clients. ' +
                                   r'For ease, the webapp assumes that all service times \(B_i\) are independent and stem from the same distribution \(B\). ' +
                                   r'Given these parameters of the true distribution, we determine the optimal schedule for a phase-type distribution ' +
                                   r'with the same parameters. It has been shown that the error introduced by this fit can be considered as negligible.'),
                            dcc.Markdown(r"""
                                    ##### More about this app
                                    
                                    The purpose of this app is to determine optimal dynamic schedules during any service process with a single server
                                    given the characteristics of the clients, and the state of the system, i.e., the relevant information, at any 
                                    arrival point. As the state space of the system is enormous, the dynamic schedules are not generated in real time, 
                                    but are approximated beforehand. To read more about it, please send an email to Roshan Mahes 
                                    ([roshan-1@live.com](mailto:roshan-1@live.com)), Michel Mandjes ([m.r.h.mandjes@uva.nl](mailto:M.R.H.Mandjes@uva.nl)) 
                                    or Marko Boon ([m.a.a.boon@tue.nl](mailto:m.a.a.boon@tue.nl)).
                                    """
                            )
                        ],
                    ),
                ],
            )
        ),
    )
