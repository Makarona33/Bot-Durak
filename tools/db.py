from peewee import Model, CharField, IntegerField, PrimaryKeyField, DateTimeField, SQL
from peewee_async import Manager, MySQLDatabase

from config import DATABASE_NAME, DATABASE_PASSWORD, DATABASE_HOST

database = MySQLDatabase(database=DATABASE_NAME, user='root', password=DATABASE_PASSWORD, host=DATABASE_HOST,
                         charset='utf8mb4')

manager = Manager(database)


class Users(Model):
    user_id = PrimaryKeyField()
    nick = CharField()
    money = IntegerField(default=200)
    wins = IntegerField(default=0)
    loses = IntegerField(default=0)
    bonus_time = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])

    class Meta:
        database = database
        db_table = 'users'
