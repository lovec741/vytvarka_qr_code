from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed

class LoginForm(FlaskForm):
    password = PasswordField('Heslo', validators=[DataRequired()])
    submit = SubmitField('Přihlásit se')

class PageForm(FlaskForm):
    md_placeholder = """Příklad:\n\n# Další Nadpis\n\n## Podnadpis článku\n\nNormální odstavec, kde bude **tato část vykreslená tučně**.\n\n* první odrážka\n* druhá odrážka\n\n1. číslovaná odrážka\n2. číslovaná odrážka"""
    title = StringField('Nadpis', validators=[DataRequired()])
    pre_media_content = TextAreaField('Úvodní text před médií (podporuje Markdown)', render_kw={"placeholder": md_placeholder})
    main_content = TextAreaField('Hlavní obsah (podporuje Markdown)', validators=[DataRequired()], render_kw={"placeholder": md_placeholder})
    image = FileField('Obrázek', validators=[FileAllowed(['jpg', 'png', 'gif', 'webp'])], render_kw={"accept": ".jpg,.png,.gif,.webp"})
    video = FileField('Video', validators=[FileAllowed(['mp4', 'webm'])], render_kw={"accept": ".mp4,.webm"})
    audio = FileField('Zvuk', validators=[FileAllowed(['mp3', 'wav'])], render_kw={"accept": ".mp3,.wav"})
    submit = SubmitField('Uložit')