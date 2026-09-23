from extensions import db


class Sugerencia(db.Model):
    __tablename__ = "sugerencias"

    id_sugerencia = db.Column(
        db.Integer,
        primary_key=True
    )

    titulo = db.Column(
        db.String(200),
        nullable=False
    )

    descripcion = db.Column(
        db.Text,
        nullable=True
    )

    enlace = db.Column(
        db.String(500),
        nullable=True
    )

    id_curso = db.Column(
        db.Integer,
        db.ForeignKey("cursos.id_curso"),
        nullable=False
    )

    estado = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    curso = db.relationship(
        "Curso",
        backref="sugerencias"
    )