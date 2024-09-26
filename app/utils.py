import os
from PIL import Image
from werkzeug.utils import secure_filename
from app import db
from app.models import Page
import uuid

def create_filename(filename):
    filename = secure_filename(filename)
    return f"{uuid.uuid4()}_{filename}"

def save_image(file, upload_folder):
    filename = create_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    img = Image.open(file)
    img.thumbnail((1000, 1000))
    img.save(file_path, optimize=True, quality=85)
    return filename

def save_video(file, upload_folder):
    filename = create_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    return filename

def save_audio(file, upload_folder):
    filename = create_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    return filename

def create_page(title, pre_media_content, main_content, media):
    page = Page(id=str(uuid.uuid4()), title=title, pre_media_content=pre_media_content, main_content=main_content, media=media)
    db.session.add(page)
    db.session.commit()
    return page

def update_page(page_id, title, pre_media_content, main_content, media):
    page = Page.query.get(page_id)
    if page:
        page.title = title
        page.pre_media_content = pre_media_content
        page.main_content = main_content
        page.media = media
        db.session.commit()
    return page

def delete_page(page_id):
    page = Page.query.get(page_id)
    if page:
        db.session.delete(page)
        db.session.commit()
    return page
