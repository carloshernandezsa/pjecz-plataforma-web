"""
Flask App
"""
from flask import Flask
from redis import Redis
import rq
from plataforma_web.extensions import csrf, db, login_manager, moment


from plataforma_web.blueprints.abogados.views import abogados
from plataforma_web.blueprints.audiencias.views import audiencias
from plataforma_web.blueprints.autoridades.views import autoridades
from plataforma_web.blueprints.autoridades_funcionarios.views import autoridades_funcionarios
from plataforma_web.blueprints.bitacoras.views import bitacoras
from plataforma_web.blueprints.centros_trabajos.views import centros_trabajos
from plataforma_web.blueprints.cid_procedimientos.views import cid_procedimientos
from plataforma_web.blueprints.cid_formatos.views import cid_formatos
from plataforma_web.blueprints.cid_registros.views import cid_registros
from plataforma_web.blueprints.distritos.views import distritos
from plataforma_web.blueprints.domicilios.views import domicilios
from plataforma_web.blueprints.edictos.views import edictos
from plataforma_web.blueprints.entradas_salidas.views import entradas_salidas
from plataforma_web.blueprints.epocas.views import epocas
from plataforma_web.blueprints.fin_vales.views import fin_vales
from plataforma_web.blueprints.fin_vales_adjuntos.views import fin_vales_adjuntos
from plataforma_web.blueprints.funcionarios.views import funcionarios
from plataforma_web.blueprints.funcionarios_oficinas.views import funcionarios_oficinas
from plataforma_web.blueprints.glosas.views import glosas
from plataforma_web.blueprints.identidades_generos.views import identidades_generos
from plataforma_web.blueprints.listas_de_acuerdos.views import listas_de_acuerdos
from plataforma_web.blueprints.listas_de_acuerdos_acuerdos.views import listas_de_acuerdos_acuerdos
from plataforma_web.blueprints.materias.views import materias
from plataforma_web.blueprints.materias_tipos_juicios.views import materias_tipos_juicios
from plataforma_web.blueprints.materias_tipos_juzgados.views import materias_tipos_juzgados
from plataforma_web.blueprints.modulos.views import modulos
from plataforma_web.blueprints.not_escrituras.view import not_escrituras
from plataforma_web.blueprints.oficinas.views import oficinas
from plataforma_web.blueprints.peritos.views import peritos
from plataforma_web.blueprints.peritos_tipos.views import peritos_tipos
from plataforma_web.blueprints.permisos.views import permisos
from plataforma_web.blueprints.redams.views import redams
from plataforma_web.blueprints.repsvm_agresores.views import repsvm_agresores
from plataforma_web.blueprints.repsvm_delitos_especificos.views import repsvm_delitos_especificos
from plataforma_web.blueprints.repsvm_delitos_genericos.views import repsvm_delitos_genericos
from plataforma_web.blueprints.repsvm_tipos_sentencias.views import repsvm_tipos_sentencias
from plataforma_web.blueprints.roles.views import roles
from plataforma_web.blueprints.sentencias.views import sentencias
from plataforma_web.blueprints.sistemas.views import sistemas
from plataforma_web.blueprints.soportes_categorias.views import soportes_categorias
from plataforma_web.blueprints.soportes_tickets.views import soportes_tickets
from plataforma_web.blueprints.soportes_adjuntos.views import soportes_adjuntos
from plataforma_web.blueprints.tareas.views import tareas
from plataforma_web.blueprints.tesis_jurisprudencias.views import tesis_jurisprudencias
from plataforma_web.blueprints.tesis_jurisprudencias_funcionarios.views import tesis_jurisprudencias_funcionarios
from plataforma_web.blueprints.tesis_jurisprudencias_sentencias.views import tesis_jurisprudencias_sentencias
from plataforma_web.blueprints.ubicaciones_expedientes.views import ubicaciones_expedientes
from plataforma_web.blueprints.usuarios.views import usuarios
from plataforma_web.blueprints.usuarios_roles.views import usuarios_roles
from plataforma_web.blueprints.inv_equipos.views import inv_equipos
from plataforma_web.blueprints.inv_marcas.views import inv_marcas
from plataforma_web.blueprints.inv_modelos.views import inv_modelos
from plataforma_web.blueprints.inv_redes.views import inv_redes
from plataforma_web.blueprints.inv_componentes.views import inv_componentes
from plataforma_web.blueprints.inv_categorias.views import inv_categorias
from plataforma_web.blueprints.inv_custodias.views import inv_custodias
from plataforma_web.blueprints.inv_equipos_fotos.views import inv_equipos_fotos

from plataforma_web.blueprints.usuarios.models import Usuario


def create_app():
    """Crear app"""
    # Definir app
    app = Flask(__name__, instance_relative_config=True)
    # Cargar la configuración para producción en config/settings.py
    app.config.from_object("config.settings")
    # Cargar la configuración para desarrollo en instance/settings.py
    app.config.from_pyfile("settings.py", silent=True)
    # Redis
    app.redis = Redis.from_url(app.config["REDIS_URL"])
    app.task_queue = rq.Queue(app.config["TASK_QUEUE"], connection=app.redis, default_timeout=1920)
    # Cargar los blueprints
    app.register_blueprint(abogados)
    app.register_blueprint(audiencias)
    app.register_blueprint(autoridades)
    app.register_blueprint(autoridades_funcionarios)
    app.register_blueprint(bitacoras)
    app.register_blueprint(centros_trabajos)
    app.register_blueprint(cid_procedimientos)
    app.register_blueprint(cid_formatos)
    app.register_blueprint(cid_registros)
    app.register_blueprint(distritos)
    app.register_blueprint(domicilios)
    app.register_blueprint(edictos)
    app.register_blueprint(entradas_salidas)
    app.register_blueprint(epocas)
    app.register_blueprint(fin_vales)
    app.register_blueprint(fin_vales_adjuntos)
    app.register_blueprint(funcionarios)
    app.register_blueprint(funcionarios_oficinas)
    app.register_blueprint(glosas)
    app.register_blueprint(identidades_generos)
    app.register_blueprint(listas_de_acuerdos)
    app.register_blueprint(listas_de_acuerdos_acuerdos)
    app.register_blueprint(materias)
    app.register_blueprint(materias_tipos_juicios)
    app.register_blueprint(materias_tipos_juzgados)
    app.register_blueprint(modulos)
    app.register_blueprint(not_escrituras)
    app.register_blueprint(oficinas)
    app.register_blueprint(peritos)
    app.register_blueprint(peritos_tipos)
    app.register_blueprint(permisos)
    app.register_blueprint(redams)
    app.register_blueprint(repsvm_agresores)
    app.register_blueprint(repsvm_delitos_especificos)
    app.register_blueprint(repsvm_delitos_genericos)
    app.register_blueprint(repsvm_tipos_sentencias)
    app.register_blueprint(roles)
    app.register_blueprint(sentencias)
    app.register_blueprint(sistemas)
    app.register_blueprint(soportes_categorias)
    app.register_blueprint(soportes_tickets)
    app.register_blueprint(soportes_adjuntos)
    app.register_blueprint(tareas)
    app.register_blueprint(tesis_jurisprudencias)
    app.register_blueprint(tesis_jurisprudencias_funcionarios)
    app.register_blueprint(tesis_jurisprudencias_sentencias)
    app.register_blueprint(usuarios)
    app.register_blueprint(usuarios_roles)
    app.register_blueprint(ubicaciones_expedientes)
    app.register_blueprint(inv_equipos)
    app.register_blueprint(inv_marcas)
    app.register_blueprint(inv_modelos)
    app.register_blueprint(inv_redes)
    app.register_blueprint(inv_componentes)
    app.register_blueprint(inv_categorias)
    app.register_blueprint(inv_custodias)
    app.register_blueprint(inv_equipos_fotos)
    # Cargar las extensiones
    extensions(app)
    authentication(Usuario)
    # Entregar app
    return app


def extensions(app):
    """Incorporar las extensiones"""
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)


def authentication(user_model):
    """Inicializar Flask-Login"""
    login_manager.login_view = "usuarios.login"

    @login_manager.user_loader
    def load_user(uid):
        return user_model.query.get(uid)
