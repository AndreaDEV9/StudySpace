from extensions import db


class Carrera(db.Model):
    __tablename__ = "carreras"

    id_carrera = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    estado = db.Column(db.Boolean, nullable=False, default=True)

    usuarios = db.relationship(
        "Usuario",
        backref="carrera",
        lazy=True
    )

    cursos = db.relationship(
        "Curso",
        backref="carrera",
        lazy=True
    )

    universidades = db.relationship(
        "UniversidadCarrera",
        backref="carrera",
        lazy=True
    )