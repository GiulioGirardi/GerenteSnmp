import dash 
from dash.dependencies import Output, Input
from dash import dcc
from dash import html
import plotly 
import plotly.graph_objs as go 
from collections import deque 
import time
from pysnmp.hlapi import *
import asyncore

# SNMP parameters
community_string = 'public'
host = 'localhost'
port = 161

def get_snmp_data(host, port, community):
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=0),
        UdpTransportTarget((host, port)),
        ContextData(),
        ObjectType(ObjectIdentity('IP-MIB', 'icmpInEchos', 0))
    )

    error_indication, error_status, error_index, var_binds = next(iterator)

    if error_indication:
        print(error_indication)
        return None
    elif error_status:
        print('%s at %s' % (
            error_status.prettyPrint(),
            error_index and var_binds[int(error_index) - 1][0] or '?'
        ))
        return None
    else:
        for var_bind in var_binds:
            return int(var_bind[1])

X = deque(maxlen = 20) 
X.append(int(time.time())) 

Y = deque(maxlen = 20) 
Y.append(get_snmp_data(host, port, community_string)) 

app = dash.Dash(__name__) 

app.layout = html.Div( 
	[ 
		dcc.Graph(id = 'live-graph', animate = True), 
		dcc.Interval( 
			id = 'graph-update', 
			interval = 3*1000, 
			n_intervals = 0
		), 
	] 
) 

@app.callback( 
	Output('live-graph', 'figure'), 
	[ Input('graph-update', 'n_intervals') ] 
) 
def update_graph_scatter(n): 
	X.append(int(time.time())) 
	Y.append(get_snmp_data(host, port, community_string)) 

	data = plotly.graph_objs.Scatter( 
			x=list(X), 
			y=list(Y), 
			name='Scatter', 
			mode= 'lines+markers'
	) 

	return {'data': [data], 
			'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),yaxis = dict(range = [min(Y),max(Y)]),)} 

if __name__ == '__main__': 
	app.run_server(host='0.0.0.0', port=8080 ,debug=True)