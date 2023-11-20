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

def get_snmp_data(host, port, community, org, oid):
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=0),
        UdpTransportTarget((host, port)),
        ContextData(),
        ObjectType(ObjectIdentity(org, oid))
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


def calculate_bytes_per_second():
    community_string = 'public'
    host = 'localhost'
    port = 161
    org = 'IF-MIB'
    
    current_time_x = time.strftime('%Y-%m-%d %H:%M:%S')
    if_in_octets_x = get_snmp_data(host, port, community_string, org, 'ifInOctets')
    if_out_octets_x = get_snmp_data(host, port, community_string, org, 'ifOutOctets')
    
    
    if if_in_octets_x is not None and if_out_octets_x is not None:
        if_in_octets_x = int(if_in_octets_x)
        if_out_octets_x = int(if_out_octets_x)
    
    time.sleep(1)
    current_time_y = time.strftime('%Y-%m-%d %H:%M:%S')
    if_in_octets_y = get_snmp_data(host, port, community_string, org, 'ifInOctets')
    if_out_octets_y = get_snmp_data(host, port, community_string, org, 'ifOutOctets')
    
    
    if if_in_octets_y is not None and if_out_octets_y is not None:
        if_in_octets_y = int(if_in_octets_y)
        if_out_octets_y = int(if_out_octets_y)

    if if_in_octets_x is not None and if_out_octets_x is not None and if_in_octets_y is not None and if_out_octets_y is not None:
        dif_in = if_in_octets_y - if_in_octets_x
        dif_out = if_out_octets_y - if_out_octets_x
        total_bytes =  dif_in + dif_out
        dif_time = current_time_y - current_time_x
        taxa = (total_bytes / dif_time)
        return taxa, time.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return 0, time.strftime('%Y-%m-%d %H:%M:%S')


def percent_packet_error():
    community_string = 'public'
    host = 'localhost'
    port = 161
    org = 'IF-MIB'
    
    if_in_error = get_snmp_data(host, port, community_string, org, 'ifInErrors')
    if_in_ucast_pkts = get_snmp_data(host, port, community_string, org, 'ifInUcastPkts')
    if_in_NU_cast_Pkts = get_snmp_data(host, port, community_string, org, 'ifInNUcastPkts')
    
    if if_in_error is not None and if_in_ucast_pkts is not None and if_in_NU_cast_Pkts is not None:
        if_in_error = int(if_in_error)
        if_in_ucast_pkts = int(if_in_ucast_pkts)
        if_in_NU_cast_Pkts = int(if_in_NU_cast_Pkts)
        add_in_NU = if_in_ucast_pkts + if_in_NU_cast_Pkts
        error_percentage = (if_in_error / add_in_NU)

        return error_percentage, time.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return 0, time.strftime('%Y-%m-%d %H:%M:%S')
    

def percent_datagram_error():
    community_string = 'public'
    host = 'localhost'
    port = 161
    org = 'IP-MIB'
    
    ip_in_hdr_error = get_snmp_data(host, port, community_string, org, 'ipInHdrErrors')
    ip_in_addr_error = get_snmp_data(host, port, community_string, org, 'ipInAddrErrors')
    ip_in_unknown_protos = get_snmp_data(host, port, community_string, org, 'ipInUnknownProtos')
    ip_in_receives = get_snmp_data(host, port, community_string, org, 'ipInReceives')
    
    if ip_in_hdr_error is not None and ip_in_addr_error is not None and ip_in_unknown_protos is not None and ip_in_receives is not None:
        ip_in_hdr_error = int(ip_in_hdr_error)
        ip_in_addr_error = int(ip_in_addr_error)
        ip_in_unknown_protos = int(ip_in_unknown_protos)
        ip_in_receives = int(ip_in_receives)
        add_in_hdr_addr_unknown = ip_in_hdr_error + ip_in_addr_error + ip_in_unknown_protos
        error_percent = (add_in_hdr_addr_unknown / ip_in_receives)

        return error_percent, time.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return 0, time.strftime('%Y-%m-%d %H:%M:%S')

def link_use():
    community_string = 'public'
    host = 'localhost'
    port = 161
    org = 'IF-MIB'
    
    if_speed = get_snmp_data(host, port, community_string, org, 'ifSpeed')
    taxa_bytes, time_ret = calculate_bytes_per_second()

    if if_speed is not None and taxa_bytes is not None:
        if_speed = int(if_speed)
        taxa_bytes = taxa_bytes * 8
        use = (taxa_bytes / if_speed)

        return use, time.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return 0, time.strftime('%Y-%m-%d %H:%M:%S')
    
def calculate_forwarding_per_second():
    community_string = 'public'
    host = 'localhost'
    port = 161
    org = 'IP-MIB'
    
    current_time_x = time.strftime('%Y-%m-%d %H:%M:%S')
    ip_forw_dat_x = get_snmp_data(host, port, community_string, org, 'ipForwDatagrams')
    
    if ip_forw_dat_x is not None:
        ip_forw_dat_x = int(ip_forw_dat_x)
    
    time.sleep(1)

    current_time_y = time.strftime('%Y-%m-%d %H:%M:%S')
    ip_forw_dat_y = get_snmp_data(host, port, community_string, org, 'ipForwDatagrams')
    
    if ip_forw_dat_y is not None:
        ip_forw_dat_y = int(ip_forw_dat_y)

    if ip_forw_dat_x is not None and ip_forw_dat_y is not None:
        dif_forw = ip_forw_dat_y - ip_forw_dat_x
        dif_time = current_time_y - current_time_x
        taxa = (dif_forw / dif_time)
        return taxa, time.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return 0, time.strftime('%Y-%m-%d %H:%M:%S')

X_bytes = deque(maxlen = 20) 
X_bytes.append(int(time.time())) 

Y_bytes = deque(maxlen = 20) 
Y_bytes.append(calculate_bytes_per_second())

X_error = deque(maxlen = 20) 
X_error.append(int(time.time())) 

Y_error = deque(maxlen = 20) 
Y_error.append(percent_packet_error())

X_datagram = deque(maxlen = 20) 
X_datagram.append(int(time.time())) 

Y_datagram = deque(maxlen = 20) 
Y_datagram.append(percent_datagram_error())

X_link = deque(maxlen = 20) 
X_link.append(int(time.time())) 

Y_link = deque(maxlen = 20) 
Y_link.append(link_use())

X_forw = deque(maxlen = 20) 
X_forw.append(int(time.time())) 

Y_forw = deque(maxlen = 20)
Y_forw.append(calculate_forwarding_per_second())

app = dash.Dash(__name__) 

app.layout = html.Div([

    html.Div([
        dcc.Graph(id='live-graph-bytes'),
        dcc.Graph(id='live-graph-error'),
        dcc.Graph(id='live-graph-datagram-error'),
        dcc.Graph(id='live-graph-link-use'),
        dcc.Graph(id='live-graph-forwarding'),
        dcc.Interval( 
			id = 'graph-update', 
			interval = 3*1000, 
			n_intervals = 0
		), 
    ])    
])

#Taxa de bytes/s
@app.callback(Output('live-graph-bytes', 'figure'), 
	[Input('graph-update', 'n_intervals')]) 
def update_graph_bytes(n):
    bytes_per_second, current_time = calculate_bytes_per_second()
    X_bytes.append(current_time)
    Y_bytes.append(bytes_per_second)
    
    trace_bytes = go.Scatter(x=list(X_bytes), y=list(Y_bytes), mode='lines+markers', name='Bytes por Segundo')
    data_bytes = [trace_bytes]

    layout_bytes = go.Layout(title='Taxa de Bytes por Segundo',
                             xaxis=dict(title='Tempo'),
                             yaxis=dict(title='Bytes/segundo'))

    return {'data': data_bytes, 'layout': layout_bytes}


#Percentual de pacotes recebidos com erro
@app.callback( 
	Output('live-graph-error', 'figure'), 
	[Input('graph-update', 'n_intervals') ] 
) 
def update_graph_scatter(n):
    error_percentage, current_time = percent_packet_error()
    X_error.append(current_time)
    Y_error.append(error_percentage)

    trace = go.Scatter(x=list(X_error), y=list(Y_error), mode='lines+markers', name='Porcentagem de Erro')
    data = [trace]

    layout = go.Layout(title='Porcentagem de Pacotes Recebidos com Erro',
                       xaxis=dict(title='Tempo'),
                       yaxis=dict(title='Porcentagem de Erro'))

    return {'data': data, 'layout': layout}


#Percentual de datagramas IP com recebidos com erro
@app.callback( 
	Output('live-graph-datagram-error', 'figure'), 
	[Input('graph-update', 'n_intervals') ] 
) 
def update_graph_datagram(n):
    error_percentage, current_time = percent_datagram_error()
    X_datagram.append(current_time)
    Y_datagram.append(error_percentage)

    trace = go.Scatter(x=list(X_datagram), y=list(Y_datagram), mode='lines+markers', name='Porcentagem de Erro')
    data = [trace]

    layout = go.Layout(title='Porcentagem de Datagramas IP Recebidos com Erro',
                       xaxis=dict(title='Tempo'),
                       yaxis=dict(title='Porcentagem de Erro'))

    return {'data': data, 'layout': layout}


#Utilização do link
@app.callback( 
	Output('live-graph-link-use', 'figure'), 
	[Input('graph-update', 'n_intervals')]
)
def update_graph_link_use(n):
    use, current_time = link_use()
    X_link.append(current_time)
    Y_link.append(use)

    trace = go.Scatter(x=list(X_link), y=list(Y_link), mode='lines+markers', name='Utilização do Link')
    data = [trace]

    layout = go.Layout(title='Utlização do link',
                       xaxis=dict(title='Tempo'),
                       yaxis=dict(title='Utilização'))

    return {'data': data, 'layout': layout}


#Taxa de forwarding/s
@app.callback(Output('live-graph-forwarding', 'figure'), 
	[Input('graph-update', 'n_intervals')]) 
def update_graph_bytes(n):
    forw_per_second, current_time = calculate_forwarding_per_second()
    X_forw.append(current_time)
    Y_forw.append(forw_per_second)
    
    trace = go.Scatter(x=list(X_forw), y=list(Y_forw), mode='lines+markers', name='Forwarding por Segundo')
    data = [trace]

    layout = go.Layout(title='Taxa de Forwarding por Segundo',
                             xaxis=dict(title='Tempo'),
                             yaxis=dict(title='Forwarding/segundo'))

    return {'data': data, 'layout': layout}



if __name__ == '__main__': 
	app.run_server(host='0.0.0.0', port=8080 ,debug=True)