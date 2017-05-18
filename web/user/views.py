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
import tarfile, sys
from flask import Flask, request, abort
from web.extensions import storage
from web.evaluate import evaluate, Parsers
import shutil
blueprint = Blueprint('user', __name__, url_prefix='/users', static_folder='../static')

@blueprint.route('/members/')
@login_required
def members():
    """List members."""
    return render_template('users/members.html')


@blueprint.route("/upload/", methods=["GET"])
@login_required
def upload_get():
#    import pdb
#    pdb.set_trace()
    return render_template('users/upload.html', storage=storage)

#Upload and untar the tar.gz
#If using a cloud service, be sure to change the tar.file.open(URL TO TAR.GZ FILE)
@blueprint.route("/upload/", methods=["POST"])
@login_required
def upload_post():
    file = request.files.get("file")
    parser_type = request.form.get('parsers')
    parser =  getattr(Parsers, parser_type)

    my_upload = storage.upload(file)
    name = my_upload.name
    upload_folder = os.getcwd() + '/uploads/'
    upload_file = os.path.join(upload_folder, name)
    log_folder = os.path.abspath('../web/logs/')

    if parser_type == 'RJParser':
        tar = tarfile.open(upload_file)
        tar.extractall(log_folder)
        tar.close()
        os.remove(upload_file)
    else:
        os.rename(upload_file, log_folder + '/' + name)
#   my_upload = storage.upload(OUTPUT FILE) 
    evaluation = evaluate.evaluate(parser)
    output_file = os.getcwd() + '/uploads/' + name + '.out'
    evaluate.write_to(output_file, evaluation)
    remove_files(log_folder)
    return render_template('users/upload.html', storage=storage)

def remove_files(folder_path):
   for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

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
