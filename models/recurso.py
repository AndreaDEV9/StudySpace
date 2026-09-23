from extensions import db


class Recurso(db.Model):
    __tablename__ = "recursos"

    id_recurso = db.Column(
        db.Integer,
        primary_key=True
    )

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id_usuario"),
        nullable=False
    )

    tipo_recurso = db.Column(
        db.String(20),
        nullable=False
    )

    id_nota = db.Column(
        db.Integer,
        db.ForeignKey("notas.id_nota"),
        nullable=True
    )

    id_sugerencia = db.Column(
        db.Integer,
        db.ForeignKey("sugerencias.id_sugerencia"),
        nullable=True
    )

    tipo_guardado = db.Column(
        db.String(20),
        nullable=False,
        default="FAVORITO"
    )

    fecha_guardado = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    estado = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )