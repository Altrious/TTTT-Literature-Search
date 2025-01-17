from config import *
from helper import sql
from context import db, app
from flask_login import LoginManager, UserMixin, login_user
from log import logger


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class LoginUser(UserMixin):
    def __init__(self, user):
        self.username = user[1]
        self.password = user[2]
        self.email = user[4]
        self.id = user[0]
        self.is_associated = True if get_associated_portal(user[0])[
            0] else False

    def verify_password(self, password):
        return password == self.password

    def get_id(self):
        return self.id

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @staticmethod
    def get(username):
        loginuser = get_user_by_username(username)
        if loginuser[0]:
            return LoginUser(loginuser[1][0])
        else:
            return None


@login_manager.user_loader
def load_user(username):
    return LoginUser.get(username)


def login(id, password):
    success = True
    msg = "success"
    user = load_user(id)
    code = 200

    if user:
        if user.password == password:
            login_user(user)
        else:
            logger.info("Expect:{}, Got:{}".format(user.password, password))
            msg = 'Wrong password'
            success = False
            code = 0
    else:
        msg = 'User not found'
        success = False
        code = 800

    return msg, success, user, code


def update_password(username, password, repassword):
    with sql.Db_connection() as [db, cursor]:
        user = sql.select(cursor, '*', 'user',
                          "where user_name = '%s'" % username)
        success = False
        msg = "success"

        if user[0]:
            if repassword == password:
                sql.update(cursor, ['password'], '`user`', [
                    password], "where user_name = '%s'" % username, True)
                success = True
            else:
                msg = 'The two passwords are inconsistent'
        else:
            msg = 'User not found'
        db.commit()

    return msg, success


def get_user_by_username(username):
    with sql.Db_connection() as [db, cursor]:
        user = sql.select(cursor, '*', 'user',
                          "where user_name = '%s'" % username)
        db.commit()
    return user


def get_associated_portal(id):
    with sql.Db_connection() as [db, cursor]:
        portal = sql.select(cursor, '*', 'portal', 'where user_id = %d' % id)
        db.commit()
    return portal


def insert_new_user(username, password, repassword, email):
    with sql.Db_connection() as [db, cursor]:
        user = sql.select(cursor, '*', 'user',
                          "where user_name = '%s'" % username)

        success = False
        msg = "success"

        if user[0]:
            msg = 'User already exists'
        else:
            if repassword == password:
                sql.insert(cursor, 'user', [
                           'user_name', 'password', 'mail'], [username, password, email])
                success = True
            else:
                msg = 'The two passwords are inconsistent'

        db.commit()

    return msg, success
