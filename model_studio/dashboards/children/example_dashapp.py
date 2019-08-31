import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import dash_table

import pandas as pd
import os

from ...utils import url_for

def get_df_head(df, id):
    return dash_table.DataTable(
            id=id,
            data=df.head().to_dict('records'),
            columns=[{'id': c, 'name': c} for c in df.columns],
            style_table={'overflowX': 'scroll'},
        )

def get_children(df):
    children = [html.A('Log Out', href=url_for('auth.logout'))]
    children += [get_df_head(df)]
    return children
