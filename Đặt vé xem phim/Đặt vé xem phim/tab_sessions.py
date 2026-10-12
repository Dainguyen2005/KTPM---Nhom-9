import secrets
from threading import Lock

_lock = Lock()
_tab_users = {}

def new_token():
    return secrets.token_urlsafe(32)

def set_user(token, user_id, user_name, role, google_demo=False):
    if not token:
        return
    with _lock:
        _tab_users[token] = {
            'user_id': user_id,
            'user_name': user_name,
            'role': role,
            'google_demo': google_demo,
        }

def update_user(token, user_name=None, role=None):
    if not token:
        return
    with _lock:
        user = _tab_users.get(token)
        if not user:
            return
        if user_name is not None:
            user['user_name'] = user_name
        if role is not None:
            user['role'] = role

def get_user(token):
    if not token:
        return None
    with _lock:
        return _tab_users.get(token)

def clear_user(token):
    if token:
        with _lock:
            _tab_users.pop(token, None)
