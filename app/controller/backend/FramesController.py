#!/usr/bin/env python2
# coding: utf-8
# file: FramesController.py

from flask import render_template
from flask import request
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app import web
from app.models import CobraWebFrame
from app.models import CobraWebFrameRules
from app.CommonClass.ValidateClass import login_required
from . import ADMIN_URL

__author__ = "lightless"
__email__ = "root@lightless.me"


@web.route(ADMIN_URL + "/frame_rules", methods=["GET"])
@login_required
def show_frame_rules():
    """
    显示所有Web框架规则
    :return:
    """
    result = db.session.query(
        CobraWebFrame.frame_name, CobraWebFrame.description, CobraWebFrameRules.path_rule,
        CobraWebFrameRules.content_rule, CobraWebFrameRules.status, CobraWebFrameRules.id
    ).filter(CobraWebFrameRules.frame_id == CobraWebFrame.id).all()
    # print(result)
    return render_template("backend/frames/frame_rules.html", data=dict(frames=result))


@web.route(ADMIN_URL + "/frames", methods=["GET"])
@login_required
def show_frames():
    """
    显示所有Web框架
    :return:
    """
    result = db.session.query(CobraWebFrame.id, CobraWebFrame.frame_name, CobraWebFrame.description).all()
    return render_template("backend/frames/frames.html", data=dict(frames=result))


@web.route(ADMIN_URL + "/add_frame_rule", methods=["GET", "POST"])
@login_required
def add_frame_rule():
    """
    增加Web框架规则
    :return: Json
    """
    if request.method == "POST":
        # print(request.form)
        status = request.form.get("status", 0)
        web_frame = request.form.get("web_frame", None)
        path_rule = request.form.get("path_rule", None)
        content_rule = request.form.get("content_rule", "")

        # 检查参数合法性
        if web_frame is None or web_frame == "" or not web_frame.isdigit():
            return jsonify(tag="danger", message="Web frame can't be blank.")
        if path_rule is None or path_rule == "":
            return jsonify(tag="danger", message="Path rule can't be blank.")
        web_frame_rule = CobraWebFrame.query.filter(CobraWebFrame.id == web_frame).all()
        if not len(web_frame_rule):
            return jsonify(tag="danger", message="No selected web frame.")

        # 插入数据
        web_frame_rule = CobraWebFrameRules(
            frame_id=web_frame, path_rule=path_rule, content_rule=content_rule, status=status
        )
        try:
            db.session.add(web_frame_rule)
            db.session.commit()
            return jsonify(tag="success", message="Add success.")
        except SQLAlchemyError as e:
            return jsonify(tag="warning", message=e.message)
    else:
        web_frames = db.session.query(
            CobraWebFrame.id, CobraWebFrame.frame_name, CobraWebFrame.description
        ).all()
        # print(web_frames)
        return render_template("backend/frames/add_new_frame_rule.html", data=dict(frames=web_frames))


@web.route(ADMIN_URL + "/add_frame", methods=["GET", "POST"])
@login_required
def add_frame():
    """
    增加Web框架
    :return: Json
    """
    if request.method == "POST":
        frame_name = request.form.get("frame_name", None)
        description = request.form.get("description", None)

        if frame_name is None or frame_name == "":
            return jsonify(tag="danger", message="Frame name can't be blank.")
        if description is None or description == "":
            return jsonify(tag="danger", message="Frame description can't be blank.")

        web_frame = CobraWebFrame(frame_name=frame_name, description=description)
        try:
            db.session.add(web_frame)
            db.session.commit()
            return jsonify(tag="success", message="Add Successful.")
        except SQLAlchemyError as e:
            return jsonify(tag="danger", message=e.message)

    else:
        return render_template("backend/frames/add_new_frame.html")


@web.route(ADMIN_URL + "/update_web_frame_status", methods=['POST'])
@login_required
def update_web_frame_status():
    """
    更新Web框架规则的状态
    :return: Json
    """
    web_frame_rule_id = request.form.get("id", "")
    if web_frame_rule_id == "":
        return jsonify(code=1004, message="id can't be blank")

    r = CobraWebFrameRules.query.filter(CobraWebFrameRules.id == web_frame_rule_id).first()
    r.status = not r.status
    try:
        db.session.add(r)
        db.session.commit()
        return jsonify(code=1001, message="Update successful")
    except SQLAlchemyError as e:
        return jsonify(code=1004, message=e.message)


@web.route(ADMIN_URL + "/delete_web_frame", methods=['POST'])
@login_required
def delete_web_frame():
    """
    删除Web框架规则
    :return: Json
    """
    web_frame_rule_id = request.form.get("id", "")
    if web_frame_rule_id == "":
        return jsonify(code=1004, message="id can't be empty")

    r = CobraWebFrameRules.query.filter(CobraWebFrameRules.id == web_frame_rule_id).first()
    try:
        db.session.delete(r)
        db.session.commit()
        return jsonify(code=1001, message="Delete successful")
    except SQLAlchemyError as e:
        return jsonify(code=1004, message=e.message)


@web.route(ADMIN_URL + "/edit_frame_rule/<int:fid>", methods=["GET"])
@web.route(ADMIN_URL + "/edit_frame_rule", methods=["POST"])
@login_required
def edit_frame_rule(fid=None):
    """
    修改Web框架规则
    :param fid: web框架规则的ID
    :return: Json
    """
    if request.method == "POST":
        # print(request.form)
        status = request.form.get("status", 0)
        web_frame = request.form.get("web_frame", None)
        path_rule = request.form.get("path_rule", None)
        content_rule = request.form.get("content_rule", "")
        fid = request.form.get("fid", "")

        # 检查参数合法性
        if fid == "":
            return jsonify(tag="danger", message="fid can't be blank.")
        if web_frame is None or web_frame == "" or not web_frame.isdigit():
            return jsonify(tag="danger", message="Web frame can't be blank.")
        if path_rule is None or path_rule == "":
            return jsonify(tag="danger", message="Path rule can't be blank.")
        web_frame_rule = CobraWebFrame.query.filter(CobraWebFrame.id == web_frame).all()
        if not len(web_frame_rule):
            return jsonify(tag="danger", message="No selected web frame.")

        # 插入数据
        web_frame_rule = CobraWebFrameRules.query.filter(CobraWebFrameRules.id == fid).first()
        web_frame_rule.status = status
        web_frame_rule.frame_id = web_frame
        web_frame_rule.path_rule = path_rule
        web_frame_rule.content_rule = content_rule
        try:
            db.session.add(web_frame_rule)
            db.session.commit()
            return jsonify(tag="success", message="Save successful.")
        except SQLAlchemyError as e:
            return jsonify(tag="warning", message=e.message)
    else:
        web_frame_rule = db.session.query(
            CobraWebFrame.id, CobraWebFrame.frame_name, CobraWebFrameRules.frame_id,
            CobraWebFrameRules.path_rule, CobraWebFrameRules.content_rule, CobraWebFrameRules.status,
        ).filter(CobraWebFrameRules.id == fid).first()
        frames = db.session.query(CobraWebFrame.id, CobraWebFrame.frame_name, CobraWebFrame.description).all()
        return render_template("backend/frames/edit_frame_rules.html",
                               data=dict(frame_rule=web_frame_rule, frames=frames, fid=fid))


@web.route(ADMIN_URL + "/delete_frame", methods=['POST'])
@login_required
def delete_frame():
    """
    删除WEB框架
    :return: Json
    """
    web_frame_id = request.form.get("id", "")
    if web_frame_id == "":
        return jsonify(code=1004, message="id can't be empty")

    r = CobraWebFrame.query.filter(CobraWebFrame.id == web_frame_id).first()
    try:
        db.session.delete(r)
        db.session.commit()
        return jsonify(code=1001, message="Delete successful")
    except SQLAlchemyError as e:
        return jsonify(code=1004, message=e.message)


@web.route(ADMIN_URL + "/edit_frame/<int:fid>", methods=["GET"])
@web.route(ADMIN_URL + "/edit_frame", methods=["POST"])
@login_required
def edit_frame(fid=""):
    """
    修改Web框架规则
    :param fid: web框架规则的ID
    :return: Json
    """
    if request.method == "POST":
        fid = request.form.get("fid", "")
        frame_name = request.form.get("frame_name", "")
        description = request.form.get("description", "")

        if fid == "":
            return jsonify(tag="danger", message="id can't be blank")
        if frame_name == "":
            return jsonify(tag="danger", message="frame name can't be blank.")
        if description == "":
            return jsonify(tag="danger", message="description can't be blank")

        frame = CobraWebFrame.query.filter(CobraWebFrame.id == fid).first()
        frame.frame_name = frame_name
        frame.description = description
        try:
            db.session.add(frame)
            db.session.commit()
            return jsonify(tag="success", message="Save successful")
        except SQLAlchemyError as e:
            return jsonify(tag="danger", message=e.message)
    else:
        result = db.session.query(
            CobraWebFrame.id, CobraWebFrame.frame_name, CobraWebFrame.description
        ).filter(CobraWebFrame.id == fid).first()
        return render_template("backend/frames/edit_frame.html", data=dict(frame=result, fid=fid))
