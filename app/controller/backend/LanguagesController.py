#!/usr/bin/env python2
# coding: utf-8
# file: LanguagesController.py

from flask import request, jsonify, render_template

from .import ADMIN_URL
from app import web, db
from app.CommonClass.ValidateClass import ValidateClass, login_required
from app.models import CobraLanguages


__author__ = "lightless"
__email__ = "root@lightless.me"


@web.route(ADMIN_URL + "/add_new_language", methods=['GET', 'POST'])
@login_required
def add_new_language():

    if request.method == "POST":

        vc = ValidateClass(request, "language", "extensions")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(tag="danger", msg=msg)

        l = CobraLanguages(vc.vars.language, vc.vars.extensions)
        try:
            db.session.add(l)
            db.session.commit()
            return jsonify(tag="success", msg="add success")
        except:
            return jsonify(tag="danger", msg="try again later?")
    else:
        return render_template("backend/language/add_new_language.html")


@web.route(ADMIN_URL + "/languages", methods=['GET'])
@login_required
def languages():

    languages = CobraLanguages.query.all()
    data = {
        'languages': languages,
    }
    return render_template("backend/language/languages.html", data=data)


@web.route(ADMIN_URL + "/del_language", methods=['POST'])
@login_required
def del_language():

    vc = ValidateClass(request, "id")
    ret, msg = vc.check_args()
    if not ret:
        return jsonify(tag="danger", msg=msg)

    l = CobraLanguages.query.filter_by(id=vc.vars.id).first()
    try:
        db.session.delete(l)
        db.session.commit()
        return jsonify(tag="success", msg="delete success.")
    except:
        return jsonify(tag="danger", msg="delete failed.")


@web.route(ADMIN_URL + "/edit_language/<int:language_id>", methods=['POST', 'GET'])
@login_required
def edit_language(language_id):

    if request.method == "POST":

        vc = ValidateClass(request, "language", "extensions")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(tag="danger", msg=msg)

        l = CobraLanguages.query.filter_by(id=language_id).first()
        try:
            l.language = vc.vars.language
            l.extensions = vc.vars.extensions
            db.session.add(l)
            db.session.commit()
            return jsonify(tag="success", msg="update success.")
        except:
            return jsonify(tag="danger", msg="try again later?")

    else:
        l = CobraLanguages.query.filter_by(id=language_id).first()
        data = {
            'language': l,
        }
        return render_template("backend/language/edit_language.html", data=data)

