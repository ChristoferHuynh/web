# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user, current_user

from web.extensions import login_manager
from web.public.forms import LoginForm
from web.user.forms import RegisterForm
from web.user.models import User
from web.utils import flash_errors

blueprint = Blueprint('public', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route('/', methods=['GET'])
def home_get():
    """Home page."""
    if current_user.is_authenticated:
        redirect_url = request.args.get('next') or url_for('user.members')
        return redirect(redirect_url)
    else:
        login_form = LoginForm(request.form)
        register_form = RegisterForm(request.form)

        # Handle logging in
        return render_template('public/home.html', login_form=login_form, register_form=register_form)



@blueprint.route('/', methods=['POST'])
def home_post():
    """Home page."""
    login_form = LoginForm(request.form)
    register_form = RegisterForm(request.form)
    # Handle logging in
    if request.method == 'POST':
        if login_form.validate_on_submit():
            login_user(login_form.user)
            flash('You are logged in.', 'success')
            redirect_url = request.args.get('next') or url_for('user.members')
            return redirect(redirect_url)
        elif register_form.validate_on_submit():
            User.create(
                username=register_form.username.data,
                email=register_form.email.data,
                password=register_form.password.data,
                active=True
            )
            flash('Thank you for registering. You can now log in.', 'success')
            return redirect(url_for('public.home_get'))
        else:
            flash_errors(login_form)
    return render_template('public/home.html', login_form=login_form, register_form=register_form)


@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home_get'))


@blueprint.route('/register/', methods=['POST'])
def register_post():
    """Register new user."""
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        User.create(username=form.username.data, email=form.email.data, password=form.password.data, active=True)
        flash('Thank you for registering. You can now log in.', 'success')
        return redirect(url_for('public.home_get'))
    else:
        flash_errors(register_form)
        return redirect(url_for('public.register_get'))

@blueprint.route('/register/', methods=['GET'])
def register_get():
    """Register new user."""
    form = RegisterForm(request.form)
    return render_template('public/register.html', form=form)



@blueprint.route('/about/')
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template('public/about.html', form=form)
