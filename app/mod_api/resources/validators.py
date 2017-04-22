from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import FloatField
from wtforms.validators import InputRequired, NumberRange

class VideoUploadForm(FlaskForm):
    class Meta:
        csrf = False
    file = FileField('file', validators=[
            FileRequired(), FileAllowed(['mov'], '.mov files only')])
    # lat = FloatField('lat', validators=[InputRequired()])
    # lon = FloatField('lon', validators=[InputRequired()])
    lat = FloatField('lat', validators = [InputRequired(), NumberRange(min=-90, max=90)])
    lon = FloatField('lon', validators = [InputRequired(), NumberRange(min=-180, max=180)])

