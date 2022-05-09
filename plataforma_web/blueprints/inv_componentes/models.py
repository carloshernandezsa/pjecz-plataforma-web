"""
Inventarios Componentes, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class InvComponente(db.Model, UniversalMixin):
    """InvComponente"""

    GENERACIONES = OrderedDict(
        [
            ("NO DEFINIDO", "No definido"),
            ("6", "seis"),
            ("7", "siete"),
            ("8", "ocho"),
            ("9", "nueve"),
            ("10", "diez"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "inv_componentes"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    inv_categoria_id = db.Column(db.Integer, db.ForeignKey("inv_categorias.id"), index=True, nullable=False)
    inv_categoria = db.relationship("InvCategoria", back_populates="inv_componentes")
    inv_equipo_id = db.Column(db.Integer, db.ForeignKey("inv_equipos.id"), index=True, nullable=False)
    inv_equipo = db.relationship("InvEquipo", back_populates="inv_componentes")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    cantidad = db.Column(db.Integer(), nullable=False)
    generacion = db.Column(
        db.Enum(*GENERACIONES, name="generacion", native_enum=False),
        index=True,
        nullable=False,
        default="NO DEFINIDO",
        server_default="NO DEFINIDO",
    )
    version = db.Column(db.String(256))

    def __repr__(self):
        """Representación"""
        return f"<InvComponente {self.id}>"
