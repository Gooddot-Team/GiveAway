from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_login import current_user
from giveawayapp import login
from giveawayapp import db


class User(UserMixin, db.Document):
    username = db.StringField(max_length=64)
    email = db.StringField(max_length=120)
    password_hash = db.StringField(max_length=128)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Lists(UserMixin, db.Document):
    listname = db.StringField(max_lenght=128)
    username = db.StringField(max_lenght=128, required=True)
    lists = db.StringField()

class Giveaway(UserMixin, db.Document):
    giveaway = db.StringField(max_lenght=128)
    username = db.StringField(max_lenght=128, required=True)
    lists = db.StringField()
    filename = db.StringField()
    quantity = db.IntField()

class Winners(UserMixin, db.Document):
    giveaway = db.StringField(max_lenght=128)
    listname = db.StringField(max_lenght=128)
    winners = db.ListField(max_lenght=128)
    username = db.StringField(max_lenght=128, required=True)
    lists = db.StringField()
    iden = db.StringField()


@login.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()


