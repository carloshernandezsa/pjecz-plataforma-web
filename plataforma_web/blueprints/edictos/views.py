"""
Edictos, vistas
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

from plataforma_web.blueprints.edictos.forms import EdictoEditForm, EdictoNewForm, EdictoSearchForm
from plataforma_web.blueprints.edictos.models import Edicto, EdictoException

from plataforma_web.blueprints.autoridades.models import Autoridad, AutoridadException
from plataforma_web.blueprints.distritos.models import Distrito

edictos = Blueprint("edictos", __name__, template_folder="templates")

SUBDIRECTORIO = "Edictos"
DIAS_LIMITE = 5


@edictos.route("/edictos/acuses/<id_hashed>")
def checkout(id_hashed):
    """Acuse"""
    edicto = Edicto.query.get_or_404(Edicto.decode_id(id_hashed))
    dia, mes, ano = dia_mes_ano(edicto.creado)
    return render_template("edictos/checkout.jinja2", edicto=edicto, dia=dia, mes=mes.upper(), ano=ano)


@edictos.before_request
@login_required
@permission_required(Permiso.VER_JUSTICIABLES)
def before_request():
    """Permiso por defecto"""


@edictos.route("/edictos")
def list_active():
    """Listado de Edictos activos"""
    # Si es administrador, ve los edictos de todas las autoridades
    if current_user.can_admin("edictos"):
        todas = Edicto.query.filter(Edicto.estatus == "A").order_by(Edicto.fecha.desc()).limit(100).all()
        return render_template("edictos/list_admin.jinja2", autoridad=None, edictos=todas, estatus="A")
    # No es administrador, consultar su autoridad
    autoridad = Autoridad.query.get_or_404(current_user.autoridad_id)
    # Si su autoridad es jurisdiccional, ve sus propios edictos
    if current_user.autoridad.es_jurisdiccional:
        sus_listas = Edicto.query.filter(Edicto.autoridad == autoridad).filter(Edicto.estatus == "A").order_by(Edicto.fecha.desc()).limit(100).all()
        return render_template("edictos/list.jinja2", autoridad=autoridad, edictos=sus_listas, estatus="A")
    # No es jurisdiccional, se redirige al listado de edictos
    return redirect(url_for("edictos.list_distritos"))


@edictos.route("/edictos/distritos")
def list_distritos():
    """Listado de Distritos"""
    distritos = Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    return render_template("edictos/list_distritos.jinja2", distritos=distritos, estatus="A")


@edictos.route("/edictos/distrito/<int:distrito_id>")
def list_autoridades(distrito_id):
    """Listado de Autoridades de un distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    autoridades = Autoridad.query.filter(Autoridad.distrito == distrito).filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.estatus == "A").order_by(Autoridad.descripcion).all()
    return render_template("edictos/list_autoridades.jinja2", distrito=distrito, autoridades=autoridades, estatus="A")


@edictos.route("/edictos/autoridad/<int:autoridad_id>")
def list_autoridad_edictos(autoridad_id):
    """Listado de Edictos activos de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    edictos_activos = Edicto.query.filter(Edicto.autoridad == autoridad).filter(Edicto.estatus == "A").order_by(Edicto.fecha.desc()).limit(100).all()
    return render_template("edictos/list.jinja2", autoridad=autoridad, edictos=edictos_activos, estatus="A")


@edictos.route("/edictos/inactivos/autoridad/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def list_autoridad_edictos_inactive(autoridad_id):
    """Listado de Edictos inactivos de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    edictos_inactivos = Edicto.query.filter(Edicto.autoridad == autoridad).filter(Edicto.estatus == "B").order_by(Edicto.creado.desc()).limit(100).all()
    return render_template("edictos/list.jinja2", autoridad=autoridad, edictos=edictos_inactivos, estatus="B")


@edictos.route("/edictos/refrescar/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
@permission_required(Permiso.CREAR_ADMINISTRATIVOS)
def refresh(autoridad_id):
    """Refrescar Edictos"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.get_task_in_progress("edictos.tasks.refrescar"):
        flash("Debe esperar porque hay una tarea en el fondo sin terminar.", "warning")
    else:
        tarea = current_user.launch_task(
            nombre="edictos.tasks.refrescar",
            descripcion=f"Refrescar edictos de {autoridad.clave}",
            usuario_id=current_user.id,
            autoridad_id=autoridad.id,
        )
        flash(f"{tarea.descripcion} está corriendo en el fondo.", "info")
    return redirect(url_for("edictos.list_autoridad_edictos", autoridad_id=autoridad.id))


@edictos.route("/edictos/<int:edicto_id>")
def detail(edicto_id):
    """Detalle de un Edicto"""
    edicto = Edicto.query.get_or_404(edicto_id)
    return render_template("edictos/detail.jinja2", edicto=edicto)


@edictos.route("/edictos/buscar", methods=["GET", "POST"])
def search():
    """Buscar Edictos"""
    form_search = EdictoSearchForm()
    if form_search.validate_on_submit():
        autoridad = Autoridad.query.get(form_search.autoridad.data)
        consulta = Edicto.query.filter(Edicto.autoridad == autoridad)
        if form_search.fecha_desde.data:
            consulta = consulta.filter(Edicto.fecha >= form_search.fecha_desde.data)
        if form_search.fecha_hasta.data:
            consulta = consulta.filter(Edicto.fecha <= form_search.fecha_hasta.data)
        consulta = consulta.order_by(Edicto.fecha.desc()).limit(100).all()
        return render_template("edictos/list.jinja2", autoridad=autoridad, edictos=consulta)
    distritos = Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    autoridades = Autoridad.query.filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all()
    return render_template("edictos/search.jinja2", form=form_search, distritos=distritos, autoridades=autoridades)


@edictos.route("/edictos/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_JUSTICIABLES)
def new():
    """Subir Edicto como juzgado"""
    hoy = date.today()

    # Validar autoridad
    autoridad = current_user.autoridad
    try:
        if autoridad is None or autoridad.estatus != "A":
            raise AutoridadException("El juzgado/autoridad no existe o no es activa.")
        if not autoridad.distrito.es_distrito_judicial:
            raise AutoridadException("El juzgado/autoridad no está en un distrito jurisdiccional.")
        if not autoridad.es_jurisdiccional:
            raise AutoridadException("El juzgado/autoridad no es jurisdiccional.")
        if autoridad.directorio_edictos is None or autoridad.directorio_edictos == "":
            raise AutoridadException("El juzgado/autoridad no tiene directorio para edictos.")
    except AutoridadException as error:
        return redirect(url_for("sistemas.bad_request", error=str(error)))

    # Si viene el formulario
    form = EdictoNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():

        # Tomar valores del formulario
        fecha = form.fecha.data
        descripcion = unidecode(form.descripcion.data.strip())
        expediente = form.expediente.data
        numero_publicacion = form.numero_publicacion.data
        archivo = request.files["archivo"]

        # Validar fecha y archivo
        archivo_nombre = secure_filename(archivo.filename.lower())
        try:
            if fecha > hoy:
                raise EdictoException("La fecha no debe ser del futuro.")
            if fecha < hoy - timedelta(days=DIAS_LIMITE):
                raise EdictoException(f"La fecha no debe ser más antigua a {DIAS_LIMITE} días.")
            if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
                raise EdictoException("No es un archivo PDF.")
        except EdictoException as error:
            flash(str(error), "error")
            form.fecha.data = hoy
            return render_template("edictos/new.jinja2", form=form)

        # Insertar registro
        edicto = Edicto(
            autoridad=autoridad,
            fecha=fecha,
            descripcion=descripcion,
            expediente=expediente,
            numero_publicacion=numero_publicacion,
        )
        edicto.save()

        # Elaborar nombre del archivo y ruta
        ano_str = fecha.strftime("%Y")
        mes_str = fecha.strftime("%m")
        fecha_str = fecha.strftime("%Y-%m-%d")
        expediente_str = expediente.replace("/", "-")
        archivo_str = f"{fecha_str}-{expediente_str}-{str(numero_publicacion)}-{edicto.encode_id()}.pdf"
        ruta_str = str(Path(SUBDIRECTORIO, autoridad.directorio_edictos, ano_str, mes_str, archivo_str))

        # Subir el archivo
        deposito = current_app.config["CLOUD_STORAGE_DEPOSITO"]
        storage_client = storage.Client()
        bucket = storage_client.bucket(deposito)
        blob = bucket.blob(ruta_str)
        blob.upload_from_string(archivo.stream.read(), content_type="application/pdf")
        url = blob.public_url

        # Actualizar el nombre del archivo y el url
        edicto.archivo = archivo_str
        edicto.url = url
        edicto.save()

        # Mostrar mensaje de éxito y detalle
        flash(f"Edicto {edicto.archivo} guardado.", "success")
        return redirect(url_for("edictos.detail", edicto_id=edicto.id))

    # Prellenado de los campos
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.fecha.data = hoy
    return render_template("edictos/new.jinja2", form=form)


@edictos.route("/edictos/nuevo/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_JUSTICIABLES)
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def new_for_autoridad(autoridad_id):
    """Subir Edicto para una autoridad dada"""
    hoy = date.today()

    # Validar autoridad
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    try:
        if autoridad is None or autoridad.estatus != "A":
            raise AutoridadException("El juzgado/autoridad no existe o no es activa.")
        if not autoridad.distrito.es_distrito_judicial:
            raise AutoridadException("El juzgado/autoridad no está en un distrito jurisdiccional.")
        if not autoridad.es_jurisdiccional:
            raise AutoridadException("El juzgado/autoridad no es jurisdiccional.")
        if autoridad.directorio_edictos is None or autoridad.directorio_edictos == "":
            raise AutoridadException("El juzgado/autoridad no tiene directorio para edictos.")
    except AutoridadException as error:
        return redirect(url_for("sistemas.bad_request", error=str(error)))

    # Si viene el formulario
    form = EdictoNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():

        # Tomar valores del formulario
        fecha = form.fecha.data
        descripcion = unidecode(form.descripcion.data.strip())
        expediente = form.expediente.data
        numero_publicacion = form.numero_publicacion.data
        archivo = request.files["archivo"]

        # Validar fecha y archivo
        archivo_nombre = secure_filename(archivo.filename.lower())
        try:
            if fecha > hoy:
                raise EdictoException("La fecha no debe ser del futuro.")
            if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
                raise EdictoException("No es un archivo PDF.")
        except EdictoException as error:
            flash(str(error), "error")
            form.fecha.data = hoy
            return render_template("edictos/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # Insertar registro
        edicto = Edicto(
            autoridad=autoridad,
            fecha=fecha,
            descripcion=descripcion,
            expediente=expediente,
            numero_publicacion=numero_publicacion,
        )
        edicto.save()

        # Elaborar nombre del archivo y ruta
        ano_str = fecha.strftime("%Y")
        mes_str = fecha.strftime("%m")
        fecha_str = fecha.strftime("%Y-%m-%d")
        expediente_str = expediente.replace("/", "-")
        archivo_str = f"{fecha_str}-{expediente_str}-{str(numero_publicacion)}-{edicto.encode_id()}.pdf"
        ruta_str = str(Path(SUBDIRECTORIO, autoridad.directorio_edictos, ano_str, mes_str, archivo_str))

        # Subir el archivo
        deposito = current_app.config["CLOUD_STORAGE_DEPOSITO"]
        storage_client = storage.Client()
        bucket = storage_client.bucket(deposito)
        blob = bucket.blob(ruta_str)
        blob.upload_from_string(archivo.stream.read(), content_type="application/pdf")
        url = blob.public_url

        # Actualizar el nombre del archivo y el url
        edicto.archivo = archivo_str
        edicto.url = url
        edicto.save()

        # Mostrar mensaje de éxito y detalle
        flash(f"Edicto {edicto.archivo} guardado.", "success")
        return redirect(url_for("edictos.detail", edicto_id=edicto.id))

    # Prellenado de los campos
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.fecha.data = hoy
    return render_template("edictos/new_for_autoridad.jinja2", form=form, autoridad=autoridad)


@edictos.route("/edictos/edicion/<int:edicto_id>", methods=["GET", "POST"])
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def edit(edicto_id):
    """Editar Edicto"""
    edicto = Edicto.query.get_or_404(edicto_id)
    form = EdictoEditForm()
    if form.validate_on_submit():
        edicto.fecha = form.fecha.data
        edicto.descripcion = form.descripcion.data
        edicto.save()
        flash(f"Edicto {edicto.archivo} guardado.", "success")
        return redirect(url_for("edictos.detail", edicto_id=edicto.id))
    form.fecha.data = edicto.fecha
    form.descripcion.data = edicto.descripcion
    return render_template("edictos/edit.jinja2", form=form, edicto=edicto)


@edictos.route("/edictos/eliminar/<int:edicto_id>")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def delete(edicto_id):
    """Eliminar Edicto"""
    edicto = Edicto.query.get_or_404(edicto_id)
    if edicto.estatus == "A":
        if current_user.can_admin("edictos") or (current_user.autoridad_id == edicto.autoridad_id):
            edicto.delete()
            flash(f"Edicto {edicto.archivo} eliminado.", "success")
        else:
            flash("No tiene permiso para eliminar.", "warning")
    return redirect(url_for("edictos.detail", edicto_id=edicto_id))


@edictos.route("/edictos/recuperar/<int:edicto_id>")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def recover(edicto_id):
    """Recuperar Edicto"""
    edicto = Edicto.query.get_or_404(edicto_id)
    if edicto.estatus == "B":
        if current_user.can_admin("edictos") or (current_user.autoridad_id == edicto.autoridad_id):
            edicto.recover()
            flash(f"Edicto {edicto.archivo} recuperado.", "success")
        else:
            flash("No tiene permiso para recuperar.", "warning")
    return redirect(url_for("edictos.detail", edicto_id=edicto_id))
