from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import FloatField
from wtforms.validators import InputRequired, NumberRange

import jsonschema

class VideoUploadForm(FlaskForm):
    class Meta:
        csrf = False

    # iPhone Video files: mov | Android Video files: 3gp, mp4
    file = FileField('file', validators=[
            FileRequired(), FileAllowed(['mov', '3gp', 'mp4'], '.mov, .3gp, .mp4 files only')]) 
    lat = FloatField('lat', validators = [InputRequired(), NumberRange(min=-90, max=90)])
    lon = FloatField('lon', validators = [InputRequired(), NumberRange(min=-180, max=180)])
