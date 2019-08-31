"""Create a Dash app within a Flask app."""
from dash import Dash
import dash_html_components as html
from importlib import import_module

from .settings import *
from .layout import html_layout

module = __name__.split('.')[-1]
callbacks = import_module('model_studio.dashboards.callbacks.%s' % module)

from ..auth import login_required
from ..utils import url_for

def init_app(server):
    """Create a Dash app."""
    dash_app = Dash(server=server,
                    external_stylesheets=EXTERNAL_STYLESHEETS,
                    external_scripts=EXTERNAL_SCRIPTS,
                    routes_pathname_prefix='/%s/' % module)

    dash_app.index_string = html_layout
    dash_app.config['suppress_callback_exceptions'] = True

    dash_id = '%s-parent' % __name__.replace('.', '-')
    dash_app.layout = html.Div(
        children=[html.P('Test', hidden=True, id='test'), html.Div(
            html.Div(
                [], className='container-fluid', id=dash_id,
                style={'width': '100%'}
            ),
            className='content-wrapper')],
        id='dash-container'
    )

    callbacks.init_callbacks(dash_app)

    return dash_app.server
