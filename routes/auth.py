from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
    current_app,
)
import bcrypt
from sqlalchemy import text, or_, func

from extensions import db
from models import Usuario, Universidad, Carrera, Ciclo, Curso
from models.universidad_carrera import UniversidadCarrera
from models.curso_usuario import CursoUsuario


auth_bp = Blueprint("auth", __name__)


# =========================================================
# LOGIN
# =========================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        usuario = Usuario.query.filter_by(
            username=username,
            estado=True,
        ).first()

        if not usuario:
            flash("Usuario o contraseña incorrectos.", "danger")
            return render_template("login.html")

        password_guardada = usuario.password
        password_correcta = False

        if password_guardada and password_guardada.startswith(
            ("$2a$", "$2b$", "$2y$")
        ):
            try:
                password_correcta = bcrypt.checkpw(
                    password.encode("utf-8"),
                    password_guardada.encode("utf-8"),
                )
            except (ValueError, TypeError):
                password_correcta = False
        else:
            # Compatibilidad temporal con contraseñas antiguas.
            password_correcta = (
                password == password_guardada
                if password_guardada is not None
                else False
            )

            if password_correcta:
                usuario.password = bcrypt.hashpw(
                    password.encode("utf-8"),
                    bcrypt.gensalt(),
                ).decode("utf-8")
                db.session.commit()

        if not password_correcta:
            flash("Usuario o contraseña incorrectos.", "danger")
            return render_template("login.html")

        session.clear()
        session["usuario_id"] = usuario.id_usuario
        session["username"] = usuario.username

        if not all((
            usuario.id_universidad,
            usuario.id_carrera,
            usuario.id_ciclo,
        )):
            return redirect(
                url_for("auth.configuracion_academica")
            )

        return redirect(url_for("inicio.inicio"))

    return render_template("login.html")


# =========================================================
# REGISTRO
# =========================================================

@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        apellido = request.form.get("apellido", "").strip()
        username = request.form.get("username", "").strip()
        correo = request.form.get("correo", "").strip().lower()
        password = request.form.get("password", "")

        if not all((nombre, apellido, username, correo, password)):
            flash(
                "Completa todos los campos del registro.",
                "danger",
            )
            return render_template("registro.html")

        usuario_existente = Usuario.query.filter(
            or_(
                Usuario.username == username,
                Usuario.correo == correo,
            )
        ).first()

        if usuario_existente:
            flash(
                "El usuario o correo ya está registrado.",
                "danger",
            )
            return render_template("registro.html")

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            username=username,
            correo=correo,
            password=password_hash,
            tipo_plan="FREE",
            estado=True,
        )

        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Error al registrar usuario"
            )
            flash(
                "No se pudo completar el registro. Inténtalo nuevamente.",
                "danger",
            )
            return render_template("registro.html")

        flash(
            "Registro completado. Ahora inicia sesión.",
            "success",
        )
        return redirect(url_for("auth.login"))

    return render_template("registro.html")


# =========================================================
# PUNTO DE ENTRADA DE LA CONFIGURACIÓN ACADÉMICA
# =========================================================

@auth_bp.route("/configuracion-academica")
def configuracion_academica():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    usuario = db.session.get(Usuario, session["usuario_id"])

    if not usuario:
        session.clear()
        return redirect(url_for("auth.login"))

    if all((
        usuario.id_universidad,
        usuario.id_carrera,
        usuario.id_ciclo,
    )):
        return redirect(url_for("inicio.inicio"))

    return redirect(url_for("auth.configuracion_carrera"))


# =========================================================
# PASO 1: INSTITUCIÓN Y CARRERA
# =========================================================

@auth_bp.route(
    "/configuracion-academica/carrera",
    methods=["GET", "POST"],
)
def configuracion_carrera():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    universidades = (
        Universidad.query
        .filter_by(estado=True)
        .order_by(Universidad.nombre.asc())
        .all()
    )

    usuario = db.session.get(Usuario, session["usuario_id"])
    seleccion_actual = None

    if usuario and usuario.id_universidad and usuario.id_carrera:
        seleccion_actual = {
            "id_universidad": usuario.id_universidad,
            "id_carrera": usuario.id_carrera,
        }

    if request.method == "POST":
        try:
            id_universidad = int(
                request.form.get("id_universidad", "")
            )
            id_carrera = int(
                request.form.get("id_carrera", "")
            )
        except (TypeError, ValueError):
            flash(
                "Selecciona una institución y una carrera válidas.",
                "warning",
            )
            return redirect(
                url_for("auth.configuracion_carrera")
            )

        universidad = db.session.get(
            Universidad,
            id_universidad,
        )
        carrera = db.session.get(Carrera, id_carrera)

        if not universidad or not universidad.estado:
            flash(
                "La institución seleccionada no está disponible.",
                "danger",
            )
            return redirect(
                url_for("auth.configuracion_carrera")
            )

        if not carrera or not carrera.estado:
            flash(
                "La carrera seleccionada no está disponible.",
                "danger",
            )
            return redirect(
                url_for("auth.configuracion_carrera")
            )

        relacion = UniversidadCarrera.query.filter_by(
            id_universidad=id_universidad,
            id_carrera=id_carrera,
            estado=True,
        ).first()

        if not relacion:
            flash(
                "La carrera no está asociada a la institución seleccionada.",
                "warning",
            )
            return redirect(
                url_for("auth.configuracion_carrera")
            )

        session["config_academica"] = {
            "id_universidad": id_universidad,
            "id_carrera": id_carrera,
        }

        return redirect(url_for("auth.configuracion_ciclo"))

    return render_template(
        "configuracion_carrera.html",
        universidades=universidades,
        seleccion_actual=seleccion_actual,
    )


# =========================================================
# PASO 2: CICLO ACADÉMICO
# =========================================================

@auth_bp.route(
    "/configuracion-academica/ciclo",
    methods=["GET", "POST"],
)
def configuracion_ciclo():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    config = session.get("config_academica")

    if (
        not config
        or not config.get("id_universidad")
        or not config.get("id_carrera")
    ):
        return redirect(url_for("auth.configuracion_carrera"))

    universidad = db.session.get(
        Universidad,
        config["id_universidad"],
    )
    carrera = db.session.get(
        Carrera,
        config["id_carrera"],
    )

    relacion = UniversidadCarrera.query.filter_by(
        id_universidad=config["id_universidad"],
        id_carrera=config["id_carrera"],
        estado=True,
    ).first()

    if (
        not universidad
        or not carrera
        or not universidad.estado
        or not carrera.estado
        or not relacion
    ):
        session.pop("config_academica", None)
        flash(
            "Vuelve a seleccionar tu institución y carrera.",
            "warning",
        )
        return redirect(url_for("auth.configuracion_carrera"))

    limite_ciclo = (
        6
        if universidad.tipo_institucion == "INSTITUTO"
        else 10
    )

    ciclos = (
        Ciclo.query
        .filter(
            Ciclo.estado.is_(True),
            Ciclo.numero <= limite_ciclo,
        )
        .order_by(Ciclo.numero.asc())
        .all()
    )

    if request.method == "POST":
        try:
            id_ciclo = int(request.form.get("id_ciclo", ""))
        except (TypeError, ValueError):
            flash("Selecciona un ciclo válido.", "warning")
            return redirect(url_for("auth.configuracion_ciclo"))

        ciclo = db.session.get(Ciclo, id_ciclo)

        if (
            not ciclo
            or not ciclo.estado
            or ciclo.numero > limite_ciclo
        ):
            flash(
                "El ciclo no es válido para la institución seleccionada.",
                "warning",
            )
            return redirect(url_for("auth.configuracion_ciclo"))

        config["id_ciclo"] = id_ciclo
        session["config_academica"] = config

        return redirect(url_for("auth.configuracion_cursos"))

    return render_template(
        "configuracion_ciclo.html",
        universidad=universidad,
        carrera=carrera,
        ciclos=ciclos,
    )


# =========================================================
# PASO 3: SELECCIÓN Y CREACIÓN DE CURSOS
# =========================================================

@auth_bp.route(
    "/configuracion-academica/cursos",
    methods=["GET", "POST"],
)
def configuracion_cursos():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    usuario_id = session["usuario_id"]
    config = session.get("config_academica")

    if not config or not all(
        config.get(campo)
        for campo in (
            "id_universidad",
            "id_carrera",
            "id_ciclo",
        )
    ):
        return redirect(url_for("auth.configuracion_carrera"))

    universidad = db.session.get(
        Universidad,
        config["id_universidad"],
    )
    carrera = db.session.get(
        Carrera,
        config["id_carrera"],
    )
    ciclo = db.session.get(
        Ciclo,
        config["id_ciclo"],
    )

    if (
        not universidad
        or not carrera
        or not ciclo
        or not universidad.estado
        or not carrera.estado
        or not ciclo.estado
    ):
        session.pop("config_academica", None)
        flash(
            "La configuración académica ya no es válida. "
            "Selecciona nuevamente tu institución, carrera y ciclo.",
            "warning",
        )
        return redirect(url_for("auth.configuracion_carrera"))

    relacion = UniversidadCarrera.query.filter_by(
        id_universidad=universidad.id_universidad,
        id_carrera=carrera.id_carrera,
        estado=True,
    ).first()

    if not relacion:
        session.pop("config_academica", None)
        flash(
            "La carrera no está asociada a la institución seleccionada.",
            "warning",
        )
        return redirect(url_for("auth.configuracion_carrera"))

    def obtener_cursos_disponibles():
        """Obtiene cursos generales y los personalizados del usuario."""
        return (
            Curso.query
            .filter(
                Curso.id_carrera == carrera.id_carrera,
                Curso.id_ciclo == ciclo.id_ciclo,
                Curso.estado.is_(True),
                or_(
                    Curso.es_personalizado.is_(False),
                    Curso.id_usuario_creador == usuario_id,
                ),
            )
            .order_by(Curso.nombre.asc())
            .all()
        )

    if request.method == "POST":
        accion = request.form.get(
            "accion",
            "guardar_cursos",
        ).strip()

        # -------------------------------------------------
        # A. CREAR CURSO PERSONALIZADO
        # -------------------------------------------------

        if accion == "crear_curso":
            nombre = request.form.get(
                "nombre_curso",
                "",
            ).strip()

            descripcion = request.form.get(
                "descripcion_curso",
                "",
            ).strip()

            if not nombre:
                flash("Escribe el nombre del curso.", "warning")
                return redirect(
                    url_for("auth.configuracion_cursos")
                )

            if len(nombre) > 150:
                flash(
                    "El nombre del curso no puede superar los 150 caracteres.",
                    "warning",
                )
                return redirect(
                    url_for("auth.configuracion_cursos")
                )

            # Evitar cursos activos con el mismo nombre,
            # carrera y ciclo entre los cursos generales
            # y los personalizados del usuario actual.
            duplicado = (
                Curso.query
                .filter(
                    Curso.id_carrera == carrera.id_carrera,
                    Curso.id_ciclo == ciclo.id_ciclo,
                    Curso.estado.is_(True),
                    func.lower(func.trim(Curso.nombre))
                    == nombre.lower(),
                    or_(
                        Curso.es_personalizado.is_(False),
                        Curso.id_usuario_creador == usuario_id,
                    ),
                )
                .first()
            )

            if duplicado:
                flash(
                    "Ya existe un curso con ese nombre para tu carrera "
                    "y ciclo. Puedes seleccionarlo en la lista.",
                    "info",
                )
                return redirect(
                    url_for("auth.configuracion_cursos")
                )

            nuevo_curso = Curso(
                nombre=nombre,
                descripcion=descripcion or None,
                id_carrera=carrera.id_carrera,
                id_ciclo=ciclo.id_ciclo,
                estado=True,
                es_personalizado=True,
                id_usuario_creador=usuario_id,
            )

            try:
                db.session.add(nuevo_curso)
                db.session.commit()

                flash(
                    "Curso creado correctamente. "
                    "Ahora puedes seleccionarlo en la lista.",
                    "success",
                )

            except Exception:
                db.session.rollback()
                current_app.logger.exception(
                    "Error al crear un curso personalizado"
                )
                flash(
                    "No se pudo crear el curso. "
                    "Verifica los datos e inténtalo nuevamente.",
                    "danger",
                )

            return redirect(url_for("auth.configuracion_cursos"))

        # -------------------------------------------------
        # B. LEER Y VALIDAR LOS CURSOS SELECCIONADOS
        # -------------------------------------------------

        ids_formulario = (
            request.form.getlist("cursos_seleccionados")
            or request.form.getlist("id_curso")
        )

        try:
            ids_seleccionados = {
                int(valor)
                for valor in ids_formulario
            }
        except (TypeError, ValueError):
            flash(
                "La selección contiene cursos inválidos.",
                "warning",
            )
            return redirect(url_for("auth.configuracion_cursos"))

        cursos_disponibles = obtener_cursos_disponibles()

        ids_disponibles = {
            curso.id_curso
            for curso in cursos_disponibles
        }

        if not ids_seleccionados.issubset(ids_disponibles):
            flash(
                "Uno o más cursos no pertenecen a tu carrera y ciclo, "
                "o ya no están disponibles.",
                "warning",
            )
            return redirect(url_for("auth.configuracion_cursos"))

        if cursos_disponibles and not ids_seleccionados:
            flash(
                "Selecciona al menos un curso para continuar.",
                "warning",
            )
            return redirect(url_for("auth.configuracion_cursos"))

        # -------------------------------------------------
        # C. GUARDAR CONFIGURACIÓN Y SELECCIONES
        # -------------------------------------------------

        try:
            usuario = db.session.get(Usuario, usuario_id)

            if not usuario:
                db.session.rollback()
                session.clear()
                return redirect(url_for("auth.login"))

            usuario.id_universidad = universidad.id_universidad
            usuario.id_carrera = carrera.id_carrera
            usuario.id_ciclo = ciclo.id_ciclo

            selecciones_anteriores = (
                CursoUsuario.query
                .filter_by(
                    id_usuario=usuario_id,
                    estado=True,
                )
                .all()
            )

            for seleccion in selecciones_anteriores:
                seleccion.estado = False

            for id_curso in ids_seleccionados:
                seleccion = CursoUsuario.query.filter_by(
                    id_usuario=usuario_id,
                    id_curso=id_curso,
                ).first()

                if seleccion:
                    seleccion.estado = True
                else:
                    db.session.add(
                        CursoUsuario(
                            id_usuario=usuario_id,
                            id_curso=id_curso,
                            estado=True,
                        )
                    )

            db.session.commit()
            session.pop("config_academica", None)

            flash(
                "Tu espacio de estudio está configurado.",
                "success",
            )
            return redirect(url_for("inicio.inicio"))

        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Error al guardar la configuración académica"
            )
            flash(
                "No se pudo guardar la configuración. Inténtalo nuevamente.",
                "danger",
            )
            return redirect(url_for("auth.configuracion_cursos"))

    # -----------------------------------------------------
    # D. CARGAR LOS CURSOS PARA MOSTRARLOS EN LA PLANTILLA
    # -----------------------------------------------------

    cursos_disponibles = obtener_cursos_disponibles()

    ids_cursos_actuales = {
        curso.id_curso
        for curso in cursos_disponibles
    }

    selecciones_actuales = {
        seleccion.id_curso
        for seleccion in CursoUsuario.query.filter_by(
            id_usuario=usuario_id,
            estado=True,
        ).all()
        if seleccion.id_curso in ids_cursos_actuales
    }

    return render_template(
        "configuracion_cursos.html",
        universidad=universidad,
        carrera=carrera,
        ciclo=ciclo,
        cursos_disponibles=cursos_disponibles,
        cursos=cursos_disponibles,
        selecciones_actuales=selecciones_actuales,
    )


# =========================================================
# API: OBTENER CARRERAS POR INSTITUCIÓN
# =========================================================

@auth_bp.route(
    "/api/carreras/<int:id_universidad>",
    methods=["GET"],
)
def carreras_por_universidad(id_universidad):
    carreras = db.session.execute(
        text("""
            SELECT
                c.id_carrera,
                c.nombre
            FROM carreras AS c
            INNER JOIN universidad_carrera AS uc
                ON uc.id_carrera = c.id_carrera
            WHERE uc.id_universidad = :id_universidad
              AND uc.estado = 1
              AND c.estado = 1
            ORDER BY c.nombre
        """),
        {"id_universidad": id_universidad},
    ).mappings().all()

    return jsonify([
        {
            "id_carrera": carrera["id_carrera"],
            "nombre": carrera["nombre"],
        }
        for carrera in carreras
    ])


# =========================================================
# API: AGREGAR O REUTILIZAR UNIVERSIDAD O INSTITUTO
# =========================================================

@auth_bp.route("/api/universidades", methods=["POST"])
def agregar_universidad():
    if not session.get("usuario_id"):
        return jsonify({
            "ok": False,
            "mensaje": "Debes iniciar sesión.",
        }), 401

    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    tipo = (
        datos.get("tipo_institucion") or ""
    ).strip().upper()

    if not nombre or len(nombre) > 150:
        return jsonify({
            "ok": False,
            "mensaje": (
                "Ingresa un nombre válido de hasta 150 caracteres."
            ),
        }), 400

    if tipo not in ("UNIVERSIDAD", "INSTITUTO"):
        return jsonify({
            "ok": False,
            "mensaje": "Selecciona Universidad o Instituto.",
        }), 400

    try:
        existente = db.session.execute(
            text("""
                SELECT
                    id_universidad,
                    nombre,
                    tipo_institucion,
                    estado
                FROM universidades
                WHERE LOWER(TRIM(nombre)) = LOWER(TRIM(:nombre))
                LIMIT 1
            """),
            {"nombre": nombre},
        ).mappings().first()

        if existente:
            if not existente["estado"]:
                return jsonify({
                    "ok": False,
                    "mensaje": (
                        "La institución ya existe, pero está inactiva."
                    ),
                }), 409

            if existente["tipo_institucion"] != tipo:
                return jsonify({
                    "ok": False,
                    "mensaje": (
                        "Ya existe una institución con ese nombre "
                        "y tiene registrado otro tipo."
                    ),
                }), 409

            return jsonify({
                "ok": True,
                "id_universidad": existente["id_universidad"],
                "nombre": existente["nombre"],
                "tipo_institucion": existente["tipo_institucion"],
                "creada": False,
                "mensaje": "Se utilizará la institución existente.",
            }), 200

        resultado = db.session.execute(
            text("""
                INSERT INTO universidades (
                    nombre,
                    descripcion,
                    estado,
                    tipo_institucion
                )
                VALUES (
                    :nombre,
                    :descripcion,
                    1,
                    :tipo
                )
            """),
            {
                "nombre": nombre,
                "descripcion": "Registrada por un estudiante",
                "tipo": tipo,
            },
        )

        id_nuevo = resultado.lastrowid
        db.session.commit()

        return jsonify({
            "ok": True,
            "id_universidad": id_nuevo,
            "nombre": nombre,
            "tipo_institucion": tipo,
            "creada": True,
            "mensaje": "Institución registrada correctamente.",
        }), 201

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "Error al registrar una institución"
        )
        return jsonify({
            "ok": False,
            "mensaje": "No se pudo registrar la institución.",
        }), 500


# =========================================================
# API: AGREGAR O REUTILIZAR CARRERA PROFESIONAL
# =========================================================

@auth_bp.route("/api/carreras", methods=["POST"])
def agregar_carrera():
    if not session.get("usuario_id"):
        return jsonify({
            "ok": False,
            "mensaje": "Debes iniciar sesión.",
        }), 401

    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()

    try:
        id_universidad = int(datos.get("id_universidad"))
    except (TypeError, ValueError):
        return jsonify({
            "ok": False,
            "mensaje": "Selecciona una institución válida.",
        }), 400

    if not nombre or len(nombre) > 100:
        return jsonify({
            "ok": False,
            "mensaje": (
                "Ingresa una carrera válida de hasta 100 caracteres."
            ),
        }), 400

    try:
        institucion = db.session.execute(
            text("""
                SELECT id_universidad
                FROM universidades
                WHERE id_universidad = :id
                AND estado = 1
            """),
            {"id": id_universidad},
        ).first()

        if not institucion:
            return jsonify({
                "ok": False,
                "mensaje": "La institución no existe o está inactiva.",
            }), 404

        carrera = db.session.execute(
            text("""
                SELECT id_carrera, nombre, estado
                FROM carreras
                WHERE LOWER(TRIM(nombre)) = LOWER(TRIM(:nombre))
                LIMIT 1
            """),
            {"nombre": nombre},
        ).mappings().first()

        creada = False

        if carrera:
            if not carrera["estado"]:
                return jsonify({
                    "ok": False,
                    "mensaje": (
                        "La carrera ya existe, pero está inactiva."
                    ),
                }), 409

            id_carrera = carrera["id_carrera"]
            nombre_final = carrera["nombre"]
        else:
            resultado = db.session.execute(
                text("""
                    INSERT INTO carreras (nombre, estado)
                    VALUES (:nombre, 1)
                """),
                {"nombre": nombre},
            )

            id_carrera = resultado.lastrowid
            nombre_final = nombre
            creada = True

        relacion = db.session.execute(
            text("""
                SELECT
                    id_universidad_carrera,
                    estado
                FROM universidad_carrera
                WHERE id_universidad = :id_universidad
                AND id_carrera = :id_carrera
                LIMIT 1
            """),
            {
                "id_universidad": id_universidad,
                "id_carrera": id_carrera,
            },
        ).mappings().first()

        if not relacion:
            db.session.execute(
                text("""
                    INSERT INTO universidad_carrera (
                        id_universidad,
                        id_carrera,
                        estado
                    )
                    VALUES (
                        :id_universidad,
                        :id_carrera,
                        1
                    )
                """),
                {
                    "id_universidad": id_universidad,
                    "id_carrera": id_carrera,
                },
            )
        elif not relacion["estado"]:
            db.session.execute(
                text("""
                    UPDATE universidad_carrera
                    SET estado = 1
                    WHERE id_universidad_carrera = :id
                """),
                {"id": relacion["id_universidad_carrera"]},
            )

        db.session.commit()

        return jsonify({
            "ok": True,
            "id_carrera": id_carrera,
            "nombre": nombre_final,
            "creada": creada,
            "mensaje": (
                "Carrera registrada correctamente."
                if creada
                else "Se utilizará la carrera existente."
            ),
        }), 201 if creada else 200

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "Error al registrar una carrera"
        )
        return jsonify({
            "ok": False,
            "mensaje": "No se pudo registrar la carrera.",
        }), 500