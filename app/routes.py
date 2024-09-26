import functools
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.forms import LoginForm, PageForm
from app.models import Page
from app.utils import create_page, update_page, delete_page, save_image, save_video, save_audio
from app import db
from config import Config
import markdown2
import qrcode
from io import BytesIO
import base64
from flask_wtf.file import FileStorage
import os

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    pages = Page.query.all()
    return render_template('pages_overview.jinja', pages=pages)

@bp.route('/dashboard')
def dashboard():
    if session.get('logged_in') == True:
        pages = Page.query.all()
        return render_template('admin_dashboard.jinja', pages=pages)
    else:
        flash('Prosím, přihlašte se.', 'warning')
        return redirect(url_for('main.login'))



@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.password.data == Config.ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password', 'error')
    return render_template('login.jinja', form=form)

@bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('main.index'))

def login_required(func):
    @functools.wraps(func)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('main.login'))
        return func(*args, **kwargs)
    return decorated_function

@login_required
@bp.route('/create', methods=['GET', 'POST'])
def create():
    form = PageForm()
    if form.validate_on_submit():
        media = {}
        for media_type in ['image', 'video', 'audio']:
            form_data = getattr(form, media_type).data
            if form_data:
                filename = globals()[f'save_{media_type}'](form_data, Config.UPLOAD_FOLDER)
                media[media_type] = [filename]

        create_page(form.title.data, form.pre_media_content.data, form.main_content.data, media)
        return redirect(url_for('main.dashboard'))
    
    return render_template('create_edit_page.jinja', form=form, is_edit=False)

@login_required
@bp.route('/edit/<string:page_id>', methods=['GET', 'POST'])
def edit(page_id):
    page = Page.query.get_or_404(page_id)
    form = PageForm(obj=page)
                
    if form.validate_on_submit():
        media = dict(page.media) or {}
        for media_type in ['image', 'video', 'audio']:
            form_data = getattr(form, media_type).data
            if form_data and not isinstance(form_data, str):
                filename = globals()[f'save_{media_type}'](form_data, Config.UPLOAD_FOLDER)
                if media_type in media and media[media_type]:
                    old_file = media[media_type].pop(0)
                    if os.path.exists(os.path.join(Config.UPLOAD_FOLDER, old_file)):
                        os.remove(os.path.join(Config.UPLOAD_FOLDER, old_file))
                media[media_type] = [filename]

        update_page(page_id, form.title.data, form.pre_media_content.data, form.main_content.data, media)
        return redirect(url_for('main.dashboard'))
    
    for media_type in ['image', 'video', 'audio']:
        if page.media.get(media_type) and len(page.media.get(media_type)) > 0:
            form_field = getattr(form, media_type)
            form_field.data = page.media[media_type][0]

    return render_template('create_edit_page.jinja', form=form, is_edit=True)

@login_required
@bp.route('/delete/<string:page_id>')
def delete(page_id):
    delete_page(page_id)
    return redirect(url_for('main.index'))

@login_required
@bp.route('/qr/<string:page_id>')
def generate_qr(page_id):
    page_url = url_for('main.view', page_id=page_id, _external=True)
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(page_url)
    qr.make(fit=True)
    img = qr.make_image()
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f'data:image/png;base64,{img_str}'

@bp.route('/view/<string:page_id>')
def view(page_id):
    page = Page.query.get_or_404(page_id)
    pre_media_content_html = markdown2.markdown(page.pre_media_content)
    main_content_html = markdown2.markdown(page.main_content)
    return render_template('view_page.jinja', page=page, pre_media_content_html=pre_media_content_html, main_content_html=main_content_html)

@login_required
@bp.route('/preview', methods=['POST'])
def preview():
    content = request.form.get('content', '')
    html_content = markdown2.markdown(content)
    return jsonify({'html': html_content})