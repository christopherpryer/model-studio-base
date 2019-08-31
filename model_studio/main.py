"""Routes for core Flask app."""
import os
from flask import Blueprint, render_template

from . import db

from .auth import login_required
from .utils import url_for

bp = Blueprint('main', __name__,
                    template_folder='templates',
                    static_folder='static')

@bp.route('/')
@login_required
def home():
    return render_template('home.html')
