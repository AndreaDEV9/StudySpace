from extensions import db


class Ciclo(db.Model):
    __tablename__ = "ciclos"

    id_ciclo = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True, nullable=False)
    estado = db.Column(db.Boolean, nullable=False, default=True)

    usuarios = db.relationship(
        "Usuario",
        backref="ciclo",
        lazy=True
    )

    cursos = db.relationship(
        "Curso",
        backref="ciclo",
        lazy=True
    )