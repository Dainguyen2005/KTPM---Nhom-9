from flask import Flask, request, session
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from tab_sessions import get_user, update_user
from config import SECRET_KEY
from database import init_db, get_db
from auth_routes import auth_bp, setup_oauth
from main_routes import main_bp
from booking_routes import booking_bp
from payment_routes import payment_bp
from api_routes import api_bp
from admin_routes import admin_bp
from chatbot_routes import chatbot_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY


def _get_tab_token():
    return request.args.get("tab_token") or request.form.get("tab_token") or request.headers.get("X-Tab-Token")


@app.before_request
def restore_tab_session():
    token = _get_tab_token()
    if token:
        user = get_user(token)
        if user:
            session["user_id"] = user["user_id"]
            session["user_name"] = user["user_name"]
            session["role"] = user["role"]
            if user.get("google_demo"):
                session["google_demo"] = True
        else:
            session.clear()

    # Always refresh the logged-in user's data from SQLite.
    # This makes Admin changes visible immediately in other tabs/windows.
    if session.get("user_id"):
        conn = get_db()
        db_user = conn.execute("SELECT id,name,role FROM users WHERE id=?", (session["user_id"],)).fetchone()
        conn.close()
        if db_user:
            session["user_name"] = db_user["name"]
            session["role"] = db_user["role"]
            update_user(token, db_user["name"], db_user["role"])
        else:
            session.clear()
            if token:
                from tab_sessions import clear_user
                clear_user(token)


@app.after_request
def keep_tab_token(response):
    token = _get_tab_token()
    if token and 300 <= response.status_code < 400:
        location = response.headers.get("Location")
        if location:
            parts = urlsplit(location)
            query = dict(parse_qsl(parts.query, keep_blank_values=True))
            query["tab_token"] = token
            response.headers["Location"] = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))
    return response

setup_oauth(app)
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(api_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(chatbot_bp)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
