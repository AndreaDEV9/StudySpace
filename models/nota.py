from extensions import db


class Nota(db.Model):
    __tablename__ = "notas"

    id_nota = db.Column(
        db.Integer,
        primary_key=True
    )

    titulo = db.Column(
        db.String(150),
        nullable=False
    )

    descripcion = db.Column(
        db.Text,
        nullable=True
    )

    archivo = db.Column(
        db.String(255),
        nullable=True
    )

    tipo_archivo = db.Column(
        db.String(50),
        nullable=True
    )

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id_usuario"),
        nullable=False
    )

    id_curso = db.Column(
        db.Integer,
        db.ForeignKey("cursos.id_curso"),
        nullable=False
    )

    id_tema = db.Column(
        db.Integer,
        db.ForeignKey("temas.id_tema"),
        nullable=True
    )

    estado = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    fecha_registro = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    usuario = db.relationship(
        "Usuario",
        backref="notas"
    )

    curso = db.relationship(
        "Curso",
        backref="notas"
    )

    tema = db.relationship(
        "Tema",
        backref="notas"
    )