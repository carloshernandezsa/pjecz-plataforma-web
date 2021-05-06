"""
Edictos, modelos
"""
from pathlib import Path
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin

SUBDIRECTORIO = "Edictos"


class Edicto(db.Model, UniversalMixin):
    """Edicto"""

    # Nombre de la tabla
    __tablename__ = "edictos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column("autoridad", db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)

    # Columnas
    fecha = db.Column(db.Date, index=True, nullable=False)
    descripcion = db.Column(db.String(256), nullable=False)
    expediente = db.Column(db.String(16), index=True, nullable=False)
    numero_publicacion = db.Column(db.Integer(), nullable=False)
    archivo = db.Column(db.String(256))
    url = db.Column(db.String(512))

    def __repr__(self):
        """Representación"""
        return f"<Edicto {self.archivo}>"

    @property
    def ruta(self):
        """Ruta para guardar el archivo"""


class EdictoException(Exception):
    """Error por datos ilegales"""
