import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
from plotly import tools
import plotly.offline as py
import chart_studio
import chart_studio.plotly as cspy

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd



chart_studio.tools.set_credentials_file(username='riteshk28', api_key='belZgXNyrXnvBUCmyGbK')

#
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True)

app.layout = html.Div([ # this code section taken from Dash docs https://dash.plotly.com/dash-core-components/upload
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-div'),
    html.Div(id='output-datatable'),
    html.Div(html.Img(src='assets\pic.PNG'))
])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),
        html.P("Select Date Column"),
        dcc.Dropdown(id='xaxis-data',
                     options=[{'label':x, 'value':x} for x in df.columns]),
        html.P("Select Assignment Group Column"),
        dcc.Dropdown(id='yaxis-data',
                     options=[{'label':x, 'value':x} for x in df.columns]),
        html.P("Select INC Ref Column"),
        dcc.Dropdown(id='zaxis-data',
                     options=[{'label':x, 'value':x} for x in df.columns]),
        html.P("Select CI Column"),
        dcc.Dropdown(id='caxis-data',
                     options=[{'label':x, 'value':x} for x in df.columns]),
        
        html.Button(id="submit-button", children="Create Graph"),
        html.Hr(),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            page_size=15
        ),
        dcc.Store(id='stored-data', data=df.to_dict('records')),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback(Output('output-datatable', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@app.callback(Output('output-div', 'children'),
              Input('submit-button','n_clicks'),
              State('stored-data','data'),
              State('xaxis-data','value'),
              State('yaxis-data', 'value'),
              State('zaxis-data', 'value'),
              State('caxis-data', 'value')
              )


def make_graphs(n, data, x_data, y_data, z_data, c_data):
    if n is None:
        return dash.no_update
    else:
        
        fig = make_subplots(rows=1, cols=2)
        data = pd.DataFrame(data)
        
        #Defining data for bar plot
        df_pivot = pd.pivot_table(data, values=z_data, index=x_data,
                                  aggfunc='count')
        df_pivot.sort_values(by=x_data, ascending=False)
        df_pivot.head()
        df_pivot.reset_index(inplace=True)
        #line_fig = go.Scatter(x=df_pivot['Created'], y=df_pivot['Reference Number'], title='Alerts Trend')
        
        #lets define our data for assignment group count pie chart
        asn_grp = data[y_data].value_counts()
        asn_grp = pd.DataFrame(asn_grp)
        asn_grp['Group'] = asn_grp.index
        asn_grp.columns = ['Count', 'Group']
        #pie_fig = px.pie(values=asn_grp.Count, names=asn_grp.Group, title='Assignment Groups')
        
        ci = data[c_data].value_counts()
        ci = pd.DataFrame(ci)
        ci['CI'] = ci.index
        ci.columns = ['Counts', 'CI']
        ci.sort_values(by='Counts', ascending=False)
        ci = ci.head(5)
        
        fig_go = go.Figure()
        fig_go.add_trace(go.Indicator(value = len(data), title='Total INCs'))
        #fig_go.update_layout(height=300, width=300) # Added parameter)
        
        line_fig = px.line(x=df_pivot[x_data], y=df_pivot[z_data], title="Incident Trend")


        
        fig.add_trace(
            go.Bar(y=asn_grp.Count, x=asn_grp.Group, name="Assignment Groups"),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(y=ci.Counts, x=ci.CI, name="Top 5 CIs"),
            row=1, col=2
        )
        

        online_data = [line_fig]
        grid = cspy.plot(online_data, auto_open=True)
        #print(link)
        return grid
    #dcc.Graph(figure=line_fig), dcc.Graph(figure=fig), dcc.Graph(figure=fig_go)
    
    

if __name__ == '__main__':
    app.run_server(debug=True)  