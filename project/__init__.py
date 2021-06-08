from fastapi import FastAPI
from .database import database as connection
from .database import User
from .database import Movie
from .database import UserReview
from .schemas import UserBaseModel
from fastapi import HTTPException
from .schemas import UserResponseModel
from .schemas import ReviewRequestPutModel
from .schemas import ReviewRequestModel
from .schemas import ReviewResponseModel
from typing import List
from .schemas import MovieResponseModel

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

@app.post('/users',response_model=UserResponseModel)
#@app.post('/users')
async def create_user(user:UserBaseModel):

	if User.select().where(User.username== user.username).exists():
		return HTTPException(409,'El username   ya se encuentra en uso')

	hash_password= User.create_password(user.password)

	user= User.create(
		username= user.username,
		password= hash_password
		)
	return user 
	#{
	#	'id': user.id,
	#	'username': user.username
	#}
	#UserResponseModel(id=user.id,username=user.username){
	
@app.post('/reviews',response_model=ReviewResponseModel)
async def create_review(user_review:ReviewRequestModel):

	if User.select().where(User.id== user_review.user_id).first() is None:
		raise HTTPException(status_code=404,detail='User not found')

	if Movie.select().where(Movie.id== user_review.movie_id).first() is None:
		raise HTTPException(status_code=404,detail='Movie not found')

	user_review= UserReview.create(
		user_id= user_review.user_id,
		movie_id= user_review.movie_id,
		review= user_review.review,
		score= user_review.score
		)

	return user_review 

@app.get('/reviews',response_model=List[ReviewResponseModel])
async def get_reviews(page:int=1, limit:int=10):


	reviews= UserReview.select().paginate(page,limit) # SELECT * FROM user_reviews;
	return [user_review for user_review in reviews]

@app.get('/reviews/{review_id}',response_model=ReviewResponseModel)
async def get_review(review_id:int):


	user_review= UserReview.select().where(UserReview.id==review_id).first()
	if user_review is None:
		raise HTTPException (status_code=404, detail='Review not found')
	return user_review

@app.put('/reviews/{review_id}',response_model=ReviewResponseModel)
async def update_review(review_id:int,review_request:ReviewRequestPutModel):

	user_review= UserReview.select().where(UserReview.id==review_id).first()
	if user_review is None:
		raise HTTPException (status_code=404, detail='Review not found')
	
	user_review.review= review_request.review
	user_review.score= review_request.score

	user_review.save()

	return user_review

@app.delete('/reviews/{review_id}',response_model=ReviewResponseModel)
async def delete_review(review_id:int):

	user_review= UserReview.select().where(UserReview.id==review_id).first()
	if user_review is None:
		raise HTTPException (status_code=404, detail='Review not found')
	
	user_review.delete_instance()

	return user_review
