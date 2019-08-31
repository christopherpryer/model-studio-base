from importlib import import_module
from numpy import cos, sin, arcsin, sqrt
from math import radians
from flask import session
import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import pandas as pd
import os

from ... import db
from ...utils import APP_STATIC, url_for

module = __name__.split('.')[-1]
children = import_module('model_studio.dashboards.children.%s' % module)

def get_ctx():
    ctx = dash.callback_context
    triggered = None
    if ctx.triggered:
        triggered = ctx.triggered[0]['prop_id'].split('.')[0]

    return triggered

def init_callbacks(dash_app):
    @dash_app.callback(
        Output('%s-parent' % __name__.replace('.', '-'), 'children'),
        [Input('test', 'values')])
    def index(p):
        user_id = session.get('user_id')
        if user_id:
            df = pd.DataFrame()
            return children.get_children(df)
        else:
            return html.A(
                'Authentication required', href=url_for('auth.login'))
