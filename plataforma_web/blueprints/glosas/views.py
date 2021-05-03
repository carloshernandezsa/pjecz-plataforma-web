"""
Glosas, vistas
"""
from datetime import date, timedelta
from pathlib import Path
from unidecode import unidecode

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from google.cloud import storage
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
from lib.time_to_text import dia_mes_ano

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.glosas.forms import GlosaEditForm, GlosaNewForm, GlosaSearchForm
from plataforma_web.blueprints.glosas.models import Glosa

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.distritos.models import Distrito

glosas = Blueprint("glosas", __name__, template_folder="templates")

SUBDIRECTORIO = "Glosas"
DIAS_LIMITE = 5


def subir_archivo(autoridad_id: int, fecha: date, archivo: str, puede_reemplazar: bool = False):
    """Subir archivo de glosa"""
    # Configuración
    deposito = current_app.config["CLOUD_STORAGE_DEPOSITO"]
    # Validar autoridad
    autoridad = Autoridad.query.get(autoridad_id)
    if autoridad is None or autoridad.estatus != "A":
        raise ValueError("El juzgado/autoridad no existe o no es activa.")
    if not autoridad.distrito.es_distrito_judicial:
        raise ValueError("El juzgado/autoridad no está en un distrito jurisdiccional.")
    if not autoridad.es_jurisdiccional:
        raise ValueError("El juzgado/autoridad no es jurisdiccional.")
    if autoridad.directorio_glosas is None or autoridad.directorio_glosas == "":
        raise ValueError("El juzgado/autoridad no tiene directorio para glosas.")
    # Validar fecha
    hoy = date.today()
    if not isinstance(fecha, date):
        raise ValueError("La fecha no es del tipo correcto.")
    if fecha > hoy:
        raise ValueError("La fecha no debe ser del futuro.")
    if fecha < hoy - timedelta(days=DIAS_LIMITE):
        raise ValueError(f"La fecha no debe ser más antigua a {DIAS_LIMITE} días.")
    # Validar que el archivo sea PDF
    archivo_nombre = secure_filename(archivo.filename.lower())
    if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
        raise ValueError("No es un archivo PDF.")
    # Definir ruta /SUBDIRECTORIO/DISTRITO/AUTORIDAD/YYYY/MM/YYYY-MM-DD.pdf
    ano_str = fecha.strftime("%Y")
    mes_str = fecha.strftime("%m")
    fecha_str = fecha.strftime("%Y-%m-%d")
    archivo_str = fecha_str + "-glosa.pdf"
    ruta_str = str(Path(SUBDIRECTORIO, autoridad.directorio_glosas, ano_str, mes_str, archivo_str))
    # Subir archivo a Google Storage
    storage_client = storage.Client()
    bucket = storage_client.bucket(deposito)
    blob = bucket.blob(ruta_str)
    blob.upload_from_string(archivo.stream.read(), content_type="application/pdf")
    return (archivo_str, blob.public_url)


@glosas.route("/glosas/acuses/<id_hashed>")
def checkout(id_hashed):
    """Acuse"""
    glosa = Glosa.query.get_or_404(Glosa.decode_id(id_hashed))
    dia, mes, ano = dia_mes_ano(glosa.creado)
    return render_template("glosas/checkout.jinja2", glosa=glosa, dia=dia, mes=mes.upper(), ano=ano)


@glosas.before_request
@login_required
@permission_required(Permiso.VER_JUSTICIABLES)
def before_request():
    """Permiso por defecto"""


@glosas.route("/glosas")
def list_active():
    """Listado de Glosas activos"""
    # Si es administrador, ve las glosas de todas las autoridades
    if current_user.can_admin("glosas"):
        todas = Glosa.query.filter(Glosa.estatus == "A").order_by(Glosa.fecha.desc()).limit(100).all()
        return render_template("glosas/list_admin.jinja2", autoridad=None, glosas=todas, estatus="A")
    # No es administrador, consultar su autoridad
    autoridad = Autoridad.query.get_or_404(current_user.autoridad_id)
    # Si su autoridad es jurisdiccional, ve sus propias glosas
    if current_user.autoridad.es_jurisdiccional:
        sus_listas = Glosa.query.filter(Glosa.autoridad == autoridad).filter(Glosa.estatus == "A").order_by(Glosa.fecha.desc()).limit(100).all()
        return render_template("glosas/list.jinja2", autoridad=autoridad, glosas=sus_listas, estatus="A")
    # No es jurisdiccional, se redirige al listado de distritos
    return redirect(url_for("glosas.list_distritos"))


@glosas.route("/glosas/distritos")
def list_distritos():
    """Listado de Distritos"""
    distritos = Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    return render_template("glosas/list_distritos.jinja2", distritos=distritos, estatus="A")


@glosas.route("/glosas/distrito/<int:distrito_id>")
def list_autoridades(distrito_id):
    """Listado de Autoridades de un distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    autoridades = Autoridad.query.filter(Autoridad.distrito == distrito).filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all()
    return render_template("glosas/list_autoridades.jinja2", distrito=distrito, autoridades=autoridades, estatus="A")


@glosas.route("/glosas/autoridad/<int:autoridad_id>")
def list_autoridad_glosas(autoridad_id):
    """Listado de Glosas activas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    glosas_activas = Glosa.query.filter(Glosa.autoridad == autoridad).filter(Glosa.estatus == "A").order_by(Glosa.fecha.desc()).limit(100).all()
    return render_template("glosas/list.jinja2", autoridad=autoridad, glosas=glosas_activas, estatus="A")


@glosas.route("/glosas/inactivos/autoridad/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def list_autoridad_glosas_inactive(autoridad_id):
    """Listado de Glosas inactivas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    glosas_inactivas = Glosa.query.filter(Glosa.autoridad == autoridad).filter(Glosa.estatus == "B").order_by(Glosa.creado.desc()).limit(100).all()
    return render_template("glosas/list.jinja2", autoridad=autoridad, glosas=glosas_inactivas, estatus="B")


@glosas.route("/glosas/refrescar/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
@permission_required(Permiso.CREAR_ADMINISTRATIVOS)
def refresh(autoridad_id):
    """Refrescar Glosas"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.get_task_in_progress("glosas.tasks.refrescar"):
        flash("Debe esperar porque hay una tarea en el fondo sin terminar.", "warning")
    else:
        tarea = current_user.launch_task(
            nombre="glosas.tasks.refrescar",
            descripcion=f"Refrescar glosas de {autoridad.clave}",
            usuario_id=current_user.id,
            autoridad_id=autoridad.id,
        )
        flash(f"{tarea.descripcion} está corriendo en el fondo.", "info")
    return redirect(url_for("glosas.list_autoridad_glosas", autoridad_id=autoridad.id))


@glosas.route("/glosas/<int:lista_de_acuerdo_id>")
def detail(glosa_id):
    """Detalle de una Lista de Acuerdos"""
    glosa = Glosa.query.get_or_404(glosa_id)
    return render_template("glosas/detail.jinja2", glosa=glosa)


@glosas.route("/glosas/buscar", methods=["GET", "POST"])
def search():
    """Buscar Glosas"""
    form_search = GlosaSearchForm()
    if form_search.validate_on_submit():
        autoridad = Autoridad.query.get(form_search.autoridad.data)
        consulta = Glosa.query.filter(Glosa.autoridad == autoridad)
        if form_search.fecha_desde.data:
            consulta = consulta.filter(Glosa.fecha >= form_search.fecha_desde.data)
        if form_search.fecha_hasta.data:
            consulta = consulta.filter(Glosa.fecha <= form_search.fecha_hasta.data)
        # tipo_juicio
        # expediente
        # descripcion
        consulta = consulta.order_by(Glosa.creado.desc()).limit(100).all()
        return render_template("glosas/list.jinja2", glosas=consulta)
    distritos = Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    autoridades = Autoridad.query.filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all()
    return render_template("glosas/search.jinja2", form=form_search, distritos=distritos, autoridades=autoridades)
