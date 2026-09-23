from extensions import db

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id_usuario = db.Column(db.Integer, primary_key=True)

    id_universidad = db.Column(
        db.Integer,
        db.ForeignKey("universidades.id_universidad"),
        nullable=True
    )

    username = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    foto_perfil = db.Column(db.String(255), nullable=True)

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
    tipo_plan = db.Column(
        db.String(20),
        nullable=False,
        default="FREE"
    )
    fecha_registro = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )
    estado = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )