from fastapi import FastAPI
from database import database as connection
from database import User
from database import Movie
from database import UserReview
from schemas import UserBaseModel
from fastapi import HTTPException
app= FastAPI(title='Proyecto para reseñar peliculas',
			description='En este proyecto resenaremos peliculas',
			version='1')

@app.on_event('startup')
def startup():
	#print('el servidor va a comenzar')
	if connection.is_closed():
		connection.connect()
		print('conectadno')

	connection.create_tables([User,Movie,UserReview])

@app.on_event('shutdown')
def shutdown():
	#print('el servidor se encuentra finalizado')
	if not connection.is_closed():
		connection.close()
		print('cerrado')


@app.get('/')
async def index():
	return 'Hola mundo desde un servidor en FASTAPI'

@app.get('/about')
async def about():
	return 'About'

@app.post('/users')
async def create_user(user:UserBaseModel):

	if User.select().where(User.username== user.username).exists():
		return HTTPException(409,'El username ya se encuentra en uso')

	hash_password= User.create_password(user.password)
	user= User.create(
		username= user.username,
		password= hash_password
		)
	return {
		'id': user.id,
		'username': user.username
	}