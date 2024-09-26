import os
from PIL import Image
from werkzeug.utils import secure_filename
from app import db
from app.models import Page
import uuid
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import base64

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

def create_qr_code_url_string(page, page_url):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(page_url)
    qr.make(fit=True)
    img = qr.make_image()
    font = ImageFont.truetype("Roboto-Bold.ttf", 30)
    draw = ImageDraw.Draw(img)

    qr_size = img.size[0]
    padding = 20
    max_text_width = qr_size - padding*2
    
    # Wrap text
    lines = []
    words = page.title.split()
    current_line = words[0]
    for word in words[1:]:
        if draw.textlength(current_line + " " + word, font=font) <= max_text_width:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    
    line_height = font.size + 5
    text_height = len(lines) * line_height
    
    new_img = Image.new('RGB', (qr_size, qr_size + 20 + text_height), color='white')
    draw = ImageDraw.Draw(new_img)
    
    new_img.paste(img, (0, 0))

    for i, line in enumerate(lines):
        text_width = draw.textlength(line, font=font)
        text_position = ((qr_size - text_width) / 2, qr_size - 15 + i * line_height)
        draw.text(text_position, line, fill='black', font=font)

    img = new_img
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f'data:image/png;base64,{img_str}'