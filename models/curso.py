from extensions import db


class Curso(db.Model):
    __tablename__ = "cursos"

    id_curso = db.Column(
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

    id_carrera = db.Column(
        db.Integer,
        db.ForeignKey("carreras.id_carrera"),
        nullable=False
    )

    id_ciclo = db.Column(
        db.Integer,
        db.ForeignKey("ciclos.id_ciclo"),
        nullable=False
    )

    estado = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    es_personalizado = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    id_usuario_creador = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id_usuario"),
        nullable=True
    )

    creador = db.relationship(
        "Usuario",
        foreign_keys=[id_usuario_creador],
        backref="cursos_creados"
    )