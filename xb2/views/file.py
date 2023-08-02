from flask import Blueprint, request, current_app, send_file
from typing import cast
from xb2.models import File
from xb2.utils import save_file
from flask_jwt_extended import jwt_required, current_user
from xb2.extensions import db
import os

file_bp = Blueprint('file', __name__)


@file_bp.post("/files")
@jwt_required()
def create_file():
    # check post id 
    post_id = int(request.args.get("post"))
    if post_id is None:
        raise Exception("POST_NOT_FOUND")
    
    if current_user.own_post(post_id):
        pass
    else:
        raise Exception("USER_DOES_NOT_OWN_RESOURCE")
    
    file = request.files.get("file")
    if file is None:
        raise Exception("FILE_NOT_FOUND")

    file_row = save_file(file, current_app.config["UPLOAD_FOLDER"])

    file_row.userId = current_user.id
    file_row.postId = post_id

    db.session.add(file_row)
    db.session.commit()

    return {
        "msg": file_row.id
    }

@file_bp.get("/files/<int:fileId>/serve")
def get_file(fileId: int):
    file: File = File.query.get(fileId)
    if file is None:
        raise Exception('FILE_NOT_FOUND')
    
    size = request.args.get("size")

    match size:
        case None:
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file.filename)
        case "large":
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"],'resize', f"{file.filename}-large")
        case "medium":
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"],'resize', f"{file.filename}-medium")
        case "thumbnail":
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"],'resize', f"{file.filename}-thumbnail")
        case _:
            raise Exception('FILE_NOT_FOUND')
    
    if not os.path.exists(file_path):
        raise Exception('FILE_NOT_FOUND')

    return send_file(file_path, mimetype=file.mimetype)


@file_bp.get("/files/<int:fileId>/metadata")
def get_file_meta(fileId: int):
    file: File = File.query.get(fileId)
    if file is None:
        raise Exception('FILE_NOT_FOUND')
    
    return {
        "id": fileId,
        "size": file.size,
        "width": file.width,
        "height": file.height,
        "metadata": file.metadata_
    }