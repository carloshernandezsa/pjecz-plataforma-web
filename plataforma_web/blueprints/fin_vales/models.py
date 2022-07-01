"""
Financieros Vales, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class FinVale(db.Model, UniversalMixin):
    """FinVale"""

    ESTADOS = OrderedDict(
        [
            ("PENDIENTE", "Pendiente"),  # Un usuario lo ha creado, no debe permir crear un nuevo vale si tiene uno anterior por revisar
            ("ELIMINADO POR USUARIO", "Eliminado por usuario"),  # El usuario se arrepintio y lo elimino
            ("SOLICITADO", "Solicitado"),  # El superior lo autorizo con su firma
            ("ELIMINADO POR SOLICITANTE", "Eliminado por solicitante"),  # El superior lo elimino
            ("CANCELADO POR SOLICITANTE", "Cancelado por solicitante"),  # El superior ha canecelado la firma
            ("AUTORIZADO", "Autorizado"),  # Finanzas lo autorizo
            ("ELIMINADO POR AUTORIZADOR", "Eliminado por autorizador"),  # Finanzas lo elimino
            ("CANCELADO POR AUTORIZADOR", "Cancelado por autorizador"),  # Finanzas ha cancelado la firma
            ("ENTREGADO", "Entregado"),  # El usuario lo recogió
            ("POR REVISAR", "Por revisar"),  # El usuario a subido los archivos adjuntos
            ("REVISADO", "Comprobado"),  # Finanzas lo marca como revisado si cumple con la evidencia
        ]
    )

    TIPOS = OrderedDict(
        [
            ("NO DEFINIDO", "No definido"),
            ("GASOLINA", "Gasolina"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "fin_vales"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="fin_vales")

    # Columnas que deben pre-llenarse
    solicito_nombre = db.Column(db.String(256), nullable=False)
    solicito_puesto = db.Column(db.String(256), nullable=False)
    solicito_email = db.Column(db.String(256), nullable=False)
    autorizo_nombre = db.Column(db.String(256), nullable=False)
    autorizo_puesto = db.Column(db.String(256), nullable=False)
    autorizo_email = db.Column(db.String(256), nullable=False)

    # Columnas que en el estado PENDIENTE se pueden modificar
    estado = db.Column(
        db.Enum(*ESTADOS, name="estados", native_enum=False),
        index=True,
        nullable=False,
        default="PENDIENTE",
        server_default="PENDIENTE",
    )
    tipo = db.Column(
        db.Enum(*TIPOS, name="tipos", native_enum=False),
        index=True,
        nullable=False,
        default="GASOLINA",
        server_default="GASOLINA",
    )
    justificacion = db.Column(db.Text(), nullable=False)
    monto = db.Column(db.Float, nullable=False)

    # Columnas que en el estado SOLICITADO tienen valores
    solicito_efirma_tiempo = db.Column(db.DateTime)
    solicito_efirma_folio = db.Column(db.Integer)
    solicito_efirma_selloDigital = db.Column(db.String(512))
    solicito_efirma_url = db.Column(db.String(256))
    solicito_efirma_qr_url = db.Column(db.String(256))
    solicito_efirma_mensaje = db.Column(db.String(512))

    # Columnas que en el estado AUTORIZADO tienen valores
    autorizo_efirma_tiempo = db.Column(db.DateTime)
    autorizo_efirma_folio = db.Column(db.Integer)
    autorizo_efirma_selloDigital = db.Column(db.String(512))
    autorizo_efirma_url = db.Column(db.String(256))
    autorizo_efirma_qr_url = db.Column(db.String(256))
    autorizo_efirma_mensaje = db.Column(db.String(512))

    # Columnas que en el estado COMPROBADO tienen valores
    vehiculo_descripcion = db.Column(db.String(256))
    tanque_inicial = db.Column(db.String(256))
    tanque_final = db.Column(db.String(256))
    kilometraje_inicial = db.Column(db.Integer)
    kilometraje_final = db.Column(db.Integer)

    # Hijos
    fin_vales_adjuntos = db.relationship("FinValeAdjunto", back_populates="fin_vale")

    def __repr__(self):
        """Representación"""
        return f"<FinVale {self.id}>"
