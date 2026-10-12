import os
import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
from tab_sessions import set_user, clear_user

try:
    from authlib.integrations.flask_client import OAuth
except ImportError:
    OAuth = None

auth_bp = Blueprint("auth", __name__)

oauth = None


def setup_oauth(app):
    global oauth
    if not OAuth:
        return
    oauth = OAuth(app)
    if os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET"):
        oauth.register(
            name="google",
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            client_kwargs={"scope": "openid email profile"},
        )


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if not name or not email or not password or not confirm:
            error = "Vui lòng nhập đầy đủ thông tin."
        elif len(password) < 6:
            error = "Mật khẩu phải có ít nhất 6 ký tự."
        elif password != confirm:
            error = "Mật khẩu xác nhận không khớp."
        else:
            conn = get_db()
            try:
                conn.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)",
                             (name, email, generate_password_hash(password)))
                conn.commit()
                return redirect(url_for("auth.login", registered=1))
            except sqlite3.IntegrityError:
                error = "Email này đã được đăng ký."
            finally:
                conn.close()
    return render_template("register.html", error=error)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    registered = request.args.get("registered")
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        if not user or not check_password_hash(user["password"], password):
            error = "Email hoặc mật khẩu không đúng."
        else:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["role"] = user["role"]
            set_user(request.form.get("tab_token"), user["id"], user["name"], user["role"])
            return redirect(request.args.get("next") or url_for("main.index"))
    return render_template("login.html", error=error, registered=registered)


@auth_bp.route("/login/google")
def google_login():
    if oauth and os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET"):
        redirect_uri = url_for("auth.google_callback", _external=True)
        return oauth.google.authorize_redirect(redirect_uri)

    demo_email = "google.demo@example.com"
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email=?", (demo_email,)).fetchone()
    if not user:
        cur = conn.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)",
                           ("Google Demo User", demo_email, generate_password_hash("google-demo")))
        conn.commit()
        user_id = cur.lastrowid
    else:
        user_id = user["id"]
    conn.close()
    role = user["role"] if user else "user"
    session["user_id"] = user_id
    session["user_name"] = "Google Demo User"
    session["role"] = role
    session["google_demo"] = True
    set_user(request.args.get("tab_token") or request.form.get("tab_token"), user_id, "Google Demo User", role, True)
    return redirect(url_for("main.index"))


@auth_bp.route("/login/google/callback")
def google_callback():
    if not oauth:
        return redirect(url_for("auth.google_login"))
    token = oauth.google.authorize_access_token()
    userinfo = token.get("userinfo") or oauth.google.userinfo()
    email = (userinfo.get("email") or "").strip().lower()
    name = userinfo.get("name") or userinfo.get("given_name") or "Google User"
    if not email:
        return "Không lấy được email từ Google", 400
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not user:
        cur = conn.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)",
                           (name, email, generate_password_hash(os.urandom(16).hex())))
        conn.commit()
        user_id = cur.lastrowid
    else:
        user_id = user["id"]
    conn.close()
    role = user["role"] if user else "user"
    session["user_id"] = user_id
    session["user_name"] = name
    session["role"] = role
    session.pop("google_demo", None)
    set_user(request.args.get("tab_token") or request.form.get("tab_token"), user_id, name, role)
    return redirect(url_for("main.index"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    error = success = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        new_password = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")
        if not email or not new_password or not confirm:
            error = "Vui lòng nhập đầy đủ thông tin."
        elif len(new_password) < 6:
            error = "Mật khẩu mới phải có ít nhất 6 ký tự."
        elif new_password != confirm:
            error = "Mật khẩu xác nhận không khớp."
        else:
            conn = get_db()
            user = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
            if not user:
                error = "Không tìm thấy tài khoản với email này."
            else:
                conn.execute("UPDATE users SET password=? WHERE id=?",
                             (generate_password_hash(new_password), user["id"]))
                conn.commit()
                success = "Đổi mật khẩu thành công. Bạn có thể đăng nhập bằng mật khẩu mới."
            conn.close()
    return render_template("forgot_password.html", error=error, success=success)


@auth_bp.route("/logout")
def logout():
    clear_user(request.args.get("tab_token") or request.form.get("tab_token"))
    session.clear()
    return redirect(url_for("main.index"))
