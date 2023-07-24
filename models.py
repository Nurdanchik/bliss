from peewee import *
import datetime
from flask_login import UserMixin


db = PostgresqlDatabase(
    'galaxy',
    host = 'localhost',
    port = '5432',
    user = 'lada_sedan',
    password = 'qwe123'
)

db.connect()

class BaseModel(Model):
    class Meta:
        database = db
        
        
class MyUser(UserMixin,BaseModel):
    username = CharField(max_length=255, null=False, unique=True)
    email = CharField(max_length=255, null=False, unique=True)
    age = IntegerField()
    full_name = CharField(max_length=255, null=True)
    password = CharField(max_length=255, null=False)
    profile_picture = CharField(max_length=255, null=True)
    
    
class Post(BaseModel):
    author = ForeignKeyField(MyUser, on_delete='CASCADE')
    title = CharField(max_length=255, null=False)
    content = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)
    # likes = IntegerField(default=0)        #that's whst i added 
    
db.create_tables([MyUser, Post])