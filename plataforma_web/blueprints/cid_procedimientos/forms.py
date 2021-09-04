"""
CID Procedimientos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from lib.wtforms import JSONField


class CIDProcedimientoForm(FlaskForm):
    """Formulario CID Procedimiento"""

    # Step Encabezado
    titulo_procedimiento = StringField("Título", validators=[DataRequired(), Length(max=256)])
    codigo = StringField("Código", validators=[DataRequired(), Length(max=16)])
    revision = IntegerField("Revisión", validators=[DataRequired()])
    fecha = DateField("Fecha de elaboración", validators=[DataRequired()])
    # Step Objetivo
    objetivo = JSONField("Objetivo", validators=[Optional()])
    # Step Alcance
    alcance = JSONField("Alcance", validators=[Optional()])
    # Step Documentos
    documentos = JSONField("Documentos", validators=[Optional()])
    # Step Definiciones
    definiciones = JSONField("Definiciones", validators=[Optional()])
    # Step Responsabilidades
    responsabilidades = JSONField("Responsabilidades", validators=[Optional()])
    # Step Desarrollo
    desarrollo = JSONField("Desarrollo", validators=[Optional()])
    # Step Registros
    registros = JSONField("Registros", validators=[Optional()])
    # Step Control de Cambios
    elaboro_nombre = StringField("Nombre", validators=[Optional(), Length(max=256)])
    elaboro_puesto = StringField("Puesto", validators=[Optional(), Length(max=256)])
    elaboro_email = StringField("Correo", validators=[Optional(), Length(max=256)])
    reviso_nombre = StringField("Nombre", validators=[Optional(), Length(max=256)])
    reviso_puesto = StringField("Puesto", validators=[Optional(), Length(max=256)])
    reviso_email = StringField("Correo", validators=[Optional(), Length(max=256)])
    aprobo_nombre = StringField("Nombre", validators=[Optional(), Length(max=256)])
    aprobo_puesto = StringField("Puesto", validators=[Optional(), Length(max=256)])
    aprobo_email = StringField("Correo", validators=[Optional(), Length(max=256)])
    control_cambios = JSONField("Control de Cambios", validators=[Optional()])
    # Guardar
    guardar = SubmitField("Guardar")
