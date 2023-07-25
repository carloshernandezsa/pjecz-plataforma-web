"""
Edictos, modelos
"""
from urllib.parse import quote

from lib.universal_mixin import UniversalMixin
from plataforma_web.extensions import db


class Edicto(db.Model, UniversalMixin):
    """Edicto"""

    # Nombre de la tabla
    __tablename__ = "edictos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="edictos")

    # Columnas
    fecha = db.Column(db.Date, index=True, nullable=False)
    descripcion = db.Column(db.String(256), nullable=False)
    expediente = db.Column(db.String(16), nullable=False, default="", server_default="")
    numero_publicacion = db.Column(db.String(16), nullable=False, default="", server_default="")
    archivo = db.Column(db.String(256), nullable=False, default="", server_default="")
    url = db.Column(db.String(512), nullable=False, default="", server_default="")

    @property
    def descargar_url(self):
        """URL para descargar el archivo desde Google Cloud Storage"""
        return f"/edictos/descargar?url={quote(self.url)}"

    def __repr__(self):
        """Representación"""
        return f"<Edicto {self.descripcion}>"
