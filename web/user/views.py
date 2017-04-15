# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template
from flask_login import login_required

blueprint = Blueprint('user', __name__, url_prefix='/users', static_folder='../static')


@blueprint.route('/members/')
@login_required
def members():
    """List members."""
    return render_template('users/members.html')

@blueprint.route('/input/')
@login_required
def input():
    """Input page."""
    return render_template('users/input.html')

@blueprint.route('/results/')
@login_required
def results():
    """Input page."""
    return render_template('users/results.html')
