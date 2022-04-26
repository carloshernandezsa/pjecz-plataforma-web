"""
Inventarios Custodias, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired, Optional


class InvCustodiaForm(FlaskForm):
    """Formulario InvCustodia"""

    usuario = StringField("Usuario")
    oficina = StringField("Oficina")
    fecha = DateField("Fecha", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class InvCustodiaSearchForm(FlaskForm):
    """Formulario buscar InvCustodia"""

    nombre_completo = StringField("Nombre Completo", validators=[Optional()])
    fecha_desde = DateField("Fecha desde", validators=[DataRequired()])
    fecha_hasta = DateField("Fecha hasta", validators=[DataRequired()])
    buscar = SubmitField("Buscar")


class InvCustodiaAcceptRejectForm(FlaskForm):
    """Formaulario para Aceptar o Rechazar"""

    usuario = StringField("Usuario")
    nombre_completo = StringField("Nombre Completo")
    curp = StringField("CURP")
    oficina = StringField("Oficina")
    puesto = StringField("Puesto")
    fecha = DateField("Fecha", validators=[DataRequired()])
    aceptar = SubmitField("Aceptar")
    rechazar = SubmitField("Rechazar")
