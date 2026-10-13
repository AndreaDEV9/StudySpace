
from extensions import db


class CursoUsuario(db.Model):
    __tablename__ = "usuario_curso"

    id_usuario_curso = db.Column(
        db.Integer,
        primary_key=True
    )

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id_usuario", ondelete="CASCADE"),
        nullable=False
    )

    id_curso = db.Column(
        db.Integer,
        db.ForeignKey("cursos.id_curso", ondelete="CASCADE"),
        nullable=False
    )

    fecha_seleccion = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    estado = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    __table_args__ = (
        db.UniqueConstraint(
            "id_usuario",
            "id_curso",
            name="uq_usuario_curso"
        ),
    )

    usuario = db.relationship(
        "Usuario",
        backref=db.backref("cursos_seleccionados", lazy=True)
    )

    curso = db.relationship(
        "Curso",
        backref=db.backref("usuarios_seleccion", lazy=True)
    )
