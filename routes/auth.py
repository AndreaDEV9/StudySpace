from flask import Blueprint, render_template, request, redirect, url_for, session
import bcrypt

from extensions import db
from models import Usuario, Universidad, Carrera, Ciclo


auth_bp = Blueprint("auth", __name__)


# =========================
# LOGIN
# =========================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        usuario = Usuario.query.filter_by(
            username=username,
            estado=True
        ).first()

        if usuario:

            password_correcta = bcrypt.checkpw(
                password.encode("utf-8"),
                usuario.password.encode("utf-8")
            )

            if password_correcta:

                session["usuario_id"] = usuario.id_usuario
                session["username"] = usuario.username

                return redirect(url_for("inicio.inicio"))

        return "Usuario o contraseña incorrectos."

    return render_template("login.html")


# =========================
# REGISTRO
# =========================

@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():

    universidades = Universidad.query.filter_by(
        estado=True
    ).all()

    carreras = Carrera.query.filter_by(
        estado=True
    ).all()

    ciclos = Ciclo.query.filter_by(
        estado=True
    ).all()

    if request.method == "POST":

        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        username = request.form["username"]
        correo = request.form["correo"]
        password = request.form["password"]

        id_universidad = request.form["id_universidad"]
        id_carrera = request.form["id_carrera"]
        id_ciclo = request.form["id_ciclo"]

        # =========================
        # VALIDAR DUPLICADOS
        # =========================

        usuario_existente = Usuario.query.filter(
            (Usuario.username == username) |
            (Usuario.correo == correo)
        ).first()

        if usuario_existente:
            return "El usuario o correo ya está registrado."

        # =========================
        # ENCRIPTAR CONTRASEÑA
        # =========================

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # =========================
        # CREAR USUARIO
        # =========================

        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            username=username,
            correo=correo,
            password=password_hash,
            id_universidad=id_universidad,
            id_carrera=id_carrera,
            id_ciclo=id_ciclo,
            tipo_plan="FREE",
            estado=True
        )

        # =========================
        # GUARDAR EN BD
        # =========================

        db.session.add(nuevo_usuario)
        db.session.commit()

        # =========================
        # IR AL LOGIN
        # =========================

        return redirect(url_for("auth.login"))

    return render_template(
        "registro.html",
        universidades=universidades,
        carreras=carreras,
        ciclos=ciclos
    )