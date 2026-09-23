from flask import Blueprint, render_template, session, redirect


inicio_bp = Blueprint("inicio", __name__)


@inicio_bp.route("/")
def inicio():
    return render_template("inicio.html")


@inicio_bp.route("/logout")
def logout():
    session.clear()

    return redirect("/")