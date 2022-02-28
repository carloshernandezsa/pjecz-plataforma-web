"""
INV MODELOS, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.datastructures import CombinedMultiDict

from lib import datatables
from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.inv_modelos.models import INVModelo
from plataforma_web.blueprints.inv_modelos.forms import INVModeloForm

# from plataforma_web.blueprints.inv_marcas.models import INVMarca
from plataforma_web.blueprints.inv_equipos.models import INVEquipo


MODULO = "INV MODELOS"

inv_modelos = Blueprint("inv_modelos", __name__, template_folder="templates")


@inv_modelos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@inv_modelos.route("/inv_modelos")
def list_active():
    """Listado de Modelos activos"""
    # activos = INVModelo.query.filter(INVModelo.estatus == "A").all()
    return render_template(
        "inv_modelos/list.jinja2",
        modelos=INVModelo.query.filter_by(estatus="A").all(),
        titulo="Modelos",
        estatus="A",
    )


@inv_modelos.route("/inv_modelos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Modelos inactivos"""
    # inactivos = INVModelo.query.filter(INVModelo.estatus == "B").all()
    return render_template(
        "inv_modelos/list.jinja2",
        modelos=INVModelo.query.filter_by(estatus="B").all(),
        titulo="Modelos inactivos",
        estatus="B",
    )


@inv_modelos.route("/inv_modelos/<int:modelo_id>")
def detail(modelo_id):
    """Detalle de un Modelos"""
    modelo = INVModelo.query.get_or_404(modelo_id)
    return render_template("inv_modelos/detail.jinja2", modelo=modelo)


@inv_modelos.route("/inv_modelos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Modelos"""
    form = INVModeloForm()
    validacion = False
    if form.validate_on_submit():
        try:
            _validar_form(form)
            validacion = True
        except Exception as err:
            flash(f"Creación de la descripcion incorrecta. {str(err)}", "warning")
            validacion = False
        if validacion:
            modelo = INVModelo(
                marca=form.nombre.data,
                descripcion=safe_string(form.descripcion.data),
            )
            modelo.save()
            flash(f"Modelos {modelo.descripcion} guardado.", "success")
            return redirect(url_for("inv_modelos.detail", modelo_id=modelo.id))
    return render_template("inv_modelos/new.jinja2", form=form)


@inv_modelos.route("/inv_modelos/edicion/<int:modelo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(modelo_id):
    """Editar Modelo"""
    modelo = INVModelo.query.get_or_404(modelo_id)
    form = INVModeloForm()
    validacion = False
    if form.validate_on_submit():
        try:
            _validar_form(form, True)
            validacion = True
        except Exception as err:
            flash(f"Actualización incorrecta. {str(err)}", "warning")
            validacion = False

        if validacion:
            modelo.marca = form.nombre.data
            modelo.descripcion = form.descripcion.data
            modelo.save()
            flash(f"Modelo {modelo.descripcion} guardado.", "success")
            return redirect(url_for("inv_modelos.detail", modelo_id=modelo.id))
    form.nombre.data = modelo.marca
    form.descripcion.data = modelo.descripcion
    return render_template("inv_modelos/edit.jinja2", form=form, modelo=modelo)


def _validar_form(form, same=False):
    if not same:
        # nombre_existente = INVModelo.query.filter(INVModelo.marca == form.nombre.data).first()
        # if nombre_existente:
        #     raise Exception("El nombre ya se encuentra en uso.")
        descripcion_existente = INVModelo.query.filter(INVModelo.descripcion == form.descripcion.data).first()
        if descripcion_existente:
            raise Exception("La descripcion ya esta en uso. ")


@inv_modelos.route("/inv_modelos/eliminar/<int:modelo_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(modelo_id):
    """Eliminar Modelo"""
    modelo = INVModelo.query.get_or_404(modelo_id)
    if modelo.estatus == "A":
        modelo.delete()
        flash(f"Modelo {modelo.descripcion} eliminado.", "success")
    return redirect(url_for("inv_modelos.detail", modelo_id=modelo.id))


@inv_modelos.route("/inv_modelos/recuperar/<int:modelo_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(modelo_id):
    """Recuperar Modelo"""
    modelo = INVModelo.query.get_or_404(modelo_id)
    if modelo.estatus == "B":
        modelo.recover()
        flash(f"Modelo {modelo.descripcion} recuperado.", "success")
    return redirect(url_for("inv_modelos.detail", modelo_id=modelo.id))
