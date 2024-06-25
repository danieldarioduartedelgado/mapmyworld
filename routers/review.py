import uuid
from fastapi import APIRouter, Body, Request
from fastapi.encoders import jsonable_encoder
from pymongo import ReturnDocument
from models.reviews import Review, ReviewDto
from exceptiondef import GenericException
from db.mongodb import get_database
import datetime as dt

dbname = get_database()
review_collection = dbname['review']
location_collection = dbname['location']
category_collection = dbname['category']

router = APIRouter()

# Obtiene todas las revisiones
@router.get('/reviews')
def get_reviews():
    revs = list(review_collection.find(limit=100))
    #for r in revs:
    #    print (r)
    return revs

# Obtiene las 10 tuplas Category-Location que tienen mas de 30 dias en los que no sido revisadas
# priorizando las que nunca han sido revisadas, es decir su campo de "update_date" es null (1900/01/01)
@router.get('/catelocareviews')
def get_catelocareviews():
    # Se define la variable de 30 dias atras respecto de hoy
    limitdate = dt.datetime.now() - dt.timedelta(days=30)
    revs = list(review_collection.find({'register_date':{"$lte": limitdate}},limit=10).sort("update_date"))
    return revs
    #for r in revs:
    #    print (r)


# Obtiene una review dado un ID
@router.get('/reviews/{id}')
async def get_review(id : str):
    locat = review_collection.find_one({"_id": id})
    if not locat:
        raise GenericException("Review Id not found")
    return locat

# Agrega una nueva revision. Actualiza el comentario y la fecha de la revision
# en caso que no exista la crea
@router.post("/reviews")
def create_review(request: Request, review: ReviewDto = Body(...)):
    review = jsonable_encoder(review)
    # Valida que exista el codigo de la location dada
    loc = location_collection.find_one({"_id": review['id_location']})
    if not loc:
        raise GenericException("Location Id [" + str(review['id_location']) + "] was not found in the system. Please try with a valid Location.")
    loc = jsonable_encoder(loc)
    # Valida que exista el codigo de la category dada
    cat = category_collection.find_one({"_id": review['id_category']})
    if not cat:
        raise GenericException("Category Id [" + str(review['id_category']) + "] was not found in the system. Please try with a valid Category.")
    cat = jsonable_encoder(cat)
    # Valida la existencia de la revision, si existe la actualiza, en caso que no exista la crea
    rev = review_collection.find({"$and": [{'location_name': loc['name']},
                                           {'category_name': cat['name']}]})
    if rev:
        rev = list(rev)
        review_updated = review_collection.find_one_and_update({'_id': rev[0]['_id']}, 
                                                              {'$set': {"comments": review['comments'], 
                                                                        "update_date": dt.datetime.now()}},
                                                              return_document=ReturnDocument.AFTER)
        return review_updated
    # no existe, inserta el registro 
    newrev = {'_id': str(uuid.uuid1()),
              'id_location': loc['_id'],
              'location_name': loc['name'],
              'id_category': cat['_id'],
              'category_name': cat['name'],
              'register_date': dt.datetime.now(), # Registra la fec registro a la actual
              'update_date': dt.datetime.now(),   # Registra la fec creacion a la actual
              'comments': review['comments']}    
    new_review = review_collection.insert_one(newrev)
    created_review = review_collection.find_one({"_id": new_review.inserted_id})
    return created_review
    
