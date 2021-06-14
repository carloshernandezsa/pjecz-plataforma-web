"""
Autoridades, formularios
"""
from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Optional

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.materias.models import Materia


def distritos_opciones():
    """Distritos: opciones para select"""
    return Distrito.query.filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()


def materias_opciones():
    """Materias: opciones para select"""
    return Materia.query.filter(Materia.estatus == "A").order_by(Materia.nombre).all()


class AutoridadNewForm(FlaskForm):
    """Formulario nueva Autoridad"""

    distrito = QuerySelectField(query_factory=distritos_opciones, get_label="nombre")
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    clave = StringField("Clave (única)", validators=[DataRequired(), Length(max=16)])
    es_jurisdiccional = BooleanField("Es Jurisdiccional (habilita edictos, listas de acuerdos, sentencias, ubicaciones de expedientes)", validators=[Optional()])
    es_notaria = BooleanField("Es Notaría (habilita edictos)", validators=[Optional()])
    organo_jurisdiccional = SelectField("Órgano Jurisdiccional", choices=Autoridad.ORGANOS_JURISDICCIONALES, validators=[DataRequired()])
    materia = QuerySelectField("Materia (si es Juzgado de Primera Instancia)", query_factory=materias_opciones, get_label="nombre")
    # es_juzgado_primera_instancia = BooleanField("Es Juzgado de Primera Instancia (aparece en consultas por materia)", validators=[Optional()])
    # es_pleno_sala = BooleanField("Es Pleno o Sala (aparece en consultas al respecto)", validators=[Optional()])
    guardar = SubmitField("Guardar")


class AutoridadEditForm(FlaskForm):
    """Formulario modificar Autoridad"""

    distrito = QuerySelectField(query_factory=distritos_opciones, get_label="nombre")
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    clave = StringField("Clave (única)", validators=[DataRequired(), Length(max=16)])
    es_jurisdiccional = BooleanField("Es Jurisdiccional (habilita edictos, listas de acuerdos, sentencias, ubicaciones de expedientes)", validators=[Optional()])
    es_notaria = BooleanField("Es Notaría (habilita edictos)", validators=[Optional()])
    organo_jurisdiccional = SelectField("Órgano Jurisdiccional", choices=Autoridad.ORGANOS_JURISDICCIONALES, validators=[DataRequired()])
    materia = QuerySelectField("Materia (si es Juzgado de Primera Instancia)", query_factory=materias_opciones, get_label="nombre")
    # es_juzgado_primera_instancia = BooleanField("Es Juzgado de Primera Instancia (aparece en consultas por materia)", validators=[Optional()])
    # es_pleno_sala = BooleanField("Es Pleno o Sala (aparece en consultas al respecto)", validators=[Optional()])
    directorio_edictos = StringField("Directorio para edictos", validators=[Optional(), Length(max=256)])
    directorio_glosas = StringField("Directorio para glosas", validators=[Optional(), Length(max=256)])
    directorio_listas_de_acuerdos = StringField("Directorio para listas de acuerdos", validators=[Optional(), Length(max=256)])
    directorio_sentencias = StringField("Directorio para sentencias", validators=[Optional(), Length(max=256)])
    guardar = SubmitField("Guardar")


class AutoridadSearchForm(FlaskForm):
    """Formulario para buscar Autoridades"""

    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    buscar = SubmitField("Buscar")
