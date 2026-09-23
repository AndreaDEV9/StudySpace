from extensions import db


class Tema(db.Model):
    __tablename__ = "temas"

    id_tema = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(150),
        nullable=False
    )

    descripcion = db.Column(
        db.Text,
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
        backref="temas"
    )