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



from flask import url_for, redirect, render_template
from flask_wtf import Form
from flask_wtf.file import FileField
from werkzeug import secure_filename

class UploadForm(Form):
    file = FileField(render_kw={'multiple': True})

@blueprint.route('/upload/', methods=['GET', 'POST'])
def upload():
    form = UploadForm()

    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        form.file.data.save('uploads/' + filename)
        return redirect(url_for('user.upload'))

    return render_template('users/upload.html', form=form)