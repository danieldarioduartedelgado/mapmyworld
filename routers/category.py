import uuid
from fastapi import APIRouter, Body, Request
from fastapi.encoders import jsonable_encoder
from pymongo import ReturnDocument
from models.category import Category, CategoryDto
from exceptiondef import GenericException
from db.mongodb import get_database
from routers.location import get_locations
import datetime as dt

dbname = get_database()
category_collection = dbname['category']
review_collection = dbname['review']

router = APIRouter()


# Obtiene todas las categorias
@router.get('/categories')
def get_categories():
    cats = list(category_collection.find(limit=100))
    #for r in cats:
    #    print (r)
    return cats

# Obtiene una category dado un ID
@router.get('/categories/{id}')
async def get_category(id : str):
    locat = category_collection.find_one({"_id": id})
    if not locat:
        raise GenericException("Category Id not found")
    return locat

# Actualiza una category dado su ID en su record
@router.put('/categories/')
async def update_category(category: Category):
    category = jsonable_encoder(category)
    category_updated = category_collection.find_one_and_update({'_id': category['_id']}, 
                                                               {'$set': {"name": category['name']}},
                                                                return_document=ReturnDocument.AFTER)
    if not category_updated:
            raise GenericException("Category Id not found")
    return (category_updated)


# Agrega una nueva categoria
@router.post("/categories")
def create_category(request: Request, category: CategoryDto = Body(...)):
    # Valida si existe el registro
    category = jsonable_encoder(category)
    if category_collection.find_one({"name": category['name']}):
        raise GenericException("Category [" + str(category['name']) + "] already exists in the system.")
    newrcat = {'_id': str(uuid.uuid1()),
              'name': category['name']}    
    new_category = category_collection.insert_one(newrcat)
    created_category = category_collection.find_one({"_id": new_category.inserted_id})
    # Inserta denormalizadamente en la coleccion reviews las combinaciones categoria(nueva)-localidades
    #Obtiene todas las localidades
    alllocat = get_locations()
    # Recorre cada location para insertar la combinacion en la coleccion reviews
    for r in alllocat:
        #Determina si no existe la combiacion y la inserta
        rev = review_collection.find({"$and": [{'location_name': r['name']},
                                               {'category_name': category['name']}]})
        if len(list(rev))==0:
            # inserta el registro de la categoria con todas las localidades
            newrev = {'_id': str(uuid.uuid1()),
                     'location_name': r['name'],
                     'category_name': category['name'],
                     'register_date': dt.datetime.now(),
                     'update_date': dt.datetime(1900,1,1,0,0),
                     'comments': ""
                    }
            new_review = review_collection.insert_one(newrev)
    return created_category