"""
INV FOTOS, formularios
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class INVFotoNewForm(FlaskForm):
    """Formulario para subir archivos"""

    equipo = StringField("Descripción del archivo")  # read only
    descripcion = StringField("Descripción del archivo", validators=[DataRequired(), Length(max=512)])
    archivo = FileField("Archivo", validators=[FileRequired()])
    guardar = SubmitField("Subir Archivo")
