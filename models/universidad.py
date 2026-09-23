from extensions import db


class Universidad(db.Model):
    __tablename__ = "universidades"

    id_universidad = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    estado = db.Column(db.Boolean, nullable=False, default=True)

    usuarios = db.relationship(
        "Usuario",
        backref="universidad",
        lazy=True
    )

    carreras = db.relationship(
        "UniversidadCarrera",
        backref="universidad",
        lazy=True
    )