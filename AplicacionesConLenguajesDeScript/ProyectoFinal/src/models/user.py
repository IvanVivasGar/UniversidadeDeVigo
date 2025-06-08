from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, username, password, email, favorites=None, is_admin=False):
        self._username = username
        self._password = password
        self._email = email
        self._favorites = favorites or {
            'characters': [],
            'houses': [],
            'events': []
        }
        self._is_admin = is_admin
        self._oid = None  # Se llenará cuando Sirope guarde el objeto

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def email(self):
        return self._email

    @property
    def favorites(self):
        return self._favorites

    @property
    def is_admin(self):
        return self._is_admin

    def add_favorite(self, category, item_oid):
        if category in self._favorites:
            if item_oid not in self._favorites[category]:
                self._favorites[category].append(item_oid)
                return True
        return False

    def remove_favorite(self, category, item_oid):
        if category in self._favorites and item_oid in self._favorites[category]:
            self._favorites[category].remove(item_oid)
            return True
        return False

    # Métodos requeridos para Flask-Login
    def get_id(self):
        return self._oid

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True