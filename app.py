#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns


# In[2]:


import os
import dash
import dash_core_components as dcc
import dash_html_components as html


# In[3]:


df = pd.read_csv('incs.csv')


# In[6]:


df.head()


# In[8]:


df_pivot = pd.pivot_table(df, values='Reference Number', index='Created',
                          aggfunc='count')


df_pivot.sort_values(by='Created', ascending=False)
df_pivot.head()

df_pivot.reset_index(inplace=True)





app_name = 'ITSM Dashboard'
 
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
 
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'ITSM Dashboard'


# In[19]:


trace = px.line(x=df_pivot['Created'], y=df_pivot['Reference Number'])
 
app.layout = html.Div(children=[html.H1("CData Extension + Dash", style={'textAlign': 'center'}),
dcc.Graph(
id='example-graph',
figure={
'data': [trace],
'layout':
go.Layout(title='SuiteCRM Accounts Data', barmode='stack')
})
], className="container")


# In[20]:


if __name__ == '__main__':
    app.run_server(debug=True)

