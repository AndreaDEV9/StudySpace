from extensions import db


class UniversidadCarrera(db.Model):
    __tablename__ = "universidad_carrera"

    id_universidad_carrera = db.Column(
        db.Integer,
        primary_key=True
    )

    id_universidad = db.Column(
        db.Integer,
        db.ForeignKey("universidades.id_universidad"),
        nullable=False
    )

    id_carrera = db.Column(
        db.Integer,
        db.ForeignKey("carreras.id_carrera"),
        nullable=False
    )

    estado = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )