from datetime import datetime

from app.extensions import db, bcrypt


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    _password = db.Column(db.String(255))
    timecreated = db.Column(db.DateTime, default=datetime.utcnow())
    verified = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = bcrypt.generate_password_hash(password, rounds=8)

    def verify_pw(self, password):
        return bcrypt.check_password_hash(self.password, password)
