"""
Rep Reportes, tareas en el fondo
"""
from datetime import datetime
import logging

from lib.tasks import set_task_progress, set_task_error
from plataforma_web.app import create_app

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.rep_reportes.models import RepReporte
from plataforma_web.blueprints.rep_resultados.models import RepResultado


bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("reportes.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()


def elaborar(reporte_id: int):
    """Elaborar reporte"""
    bitacora.info("Inicia")

    # Validar reporte
    reporte = RepReporte.query.get(reporte_id)
    if reporte is None:
        mensaje = set_task_error("El reporte no exite.")
        bitacora.error(mensaje)
        return mensaje
    if reporte.estatus != "A":
        mensaje = set_task_error("El reporte no es activo.")
        bitacora.error(mensaje)
        return mensaje
    if reporte.progreso != "PENDIENTE":
        mensaje = set_task_error("El progreso no es PENDIENTE.")
        bitacora.error(mensaje)
        return mensaje
    if reporte.programado > datetime.now():
        mensaje = set_task_error("El reporte está programado para el futuro.")
        bitacora.error(mensaje)
        return mensaje

    # Elaborar reporte de totales por cada módulo
    cantidad = 0
    modulos = Modulo.query.filter(Modulo.estatus == "A").order_by(Modulo.nombre).all()
    for modulo in modulos:
        cantidad = Bitacora.query.filter(Bitacora.modulo == modulo.nombre).filter(Bitacora.creado >= reporte.desde).filter(Bitacora.creado <= reporte.hasta).count()
        RepResultado(
            reporte=reporte,
            modulo=modulo,
            descripcion="Total de operaciones",
            tipo="TOTAL",
            cantidad=cantidad,
        ).save()
        cantidad += 1

    # Cambiar progreso a TERMINADO
    reporte.progreso = "TERMINADO"
    reporte.save()

    # Terminar tarea
    mensaje = f"Termina con {cantidad} resultados."
    set_task_progress(100)
    bitacora.info(mensaje)
    return mensaje
