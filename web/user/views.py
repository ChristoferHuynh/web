# -*- coding: utf-8 -*-
"""User views."""
from flask import Flask
from flask import Blueprint, render_template
from flask_login import login_required
from flask import url_for, redirect, render_template
from flask_wtf import Form
from flask_wtf.file import FileField
from werkzeug import secure_filename
from flask import send_from_directory
import os
from flask import Flask, request, abort
from web.extensions import storage

blueprint = Blueprint('user', __name__, url_prefix='/users', static_folder='../static')

@blueprint.route('/members/')
@login_required
def members():
    """List members."""
    return render_template('users/members.html')


@blueprint.route("/upload/", methods=["GET"])
@login_required
def upload_get():
    print storage
#    import pdb
#    pdb.set_trace()
    return render_template('users/upload.html', storage=storage)


@blueprint.route("/upload/", methods=["POST"])
@login_required
def upload_post():
    file = request.files.get("file")
    my_upload = storage.upload(file)
    return render_template('users/upload.html', storage=storage)



@blueprint.route('/results/')
@login_required
def results():
    """Result page."""
    return render_template('users/results.html', storage=storage)

@blueprint.route("/view/<path:object_name>")
@login_required
def view_get(object_name):
    obj = storage.get(object_name)
    return render_template("users/view.html", obj=obj)
