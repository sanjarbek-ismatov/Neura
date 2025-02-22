import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from neura.db import get_db

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        user = db.execute("SELECT *  FROM user where username = ?", (username, )).fetchone()


        if user is None:
            # If user does not exist, create a new one
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
                flash("Account created. You can now log in.", "success")
                return redirect(url_for("home"))
        else:
            # If user exists, check the password
            if not check_password_hash(user["password"], password):
                error = "Incorrect password."
            else:
                session.clear()
                session["user_id"] = user["id"]
                flash("Logged in successfully!", "success")
                return redirect(url_for("home"))

        flash(error)

    return render_template('auth/register.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.register'))

        return view(**kwargs)

    return wrapped_view