import uuid
from fastapi import APIRouter, Body, Request
from fastapi.encoders import jsonable_encoder
from db.mongodb import get_database
from models.location import Location, LocationDto
from exceptiondef import GenericException
from pymongo import ReturnDocument
import datetime as dt


dbname = get_database()
location_collection = dbname['location']
category_collection = dbname['category']
review_collection = dbname['review']

router = APIRouter()


# Obtiene todas las localizaciones
@router.get('/locations')
def get_locations():
    locats = list(location_collection.find(limit=100))
    #for r in locationsx:
    #    print (r)
    return locats

# Obtiene una location dado un ID
@router.get('/locations/{id}')
async def get_location(id : str):
    locat = location_collection.find_one({"_id": id})
    if not locat:
        raise GenericException("Location Id not found")
    return locat

# Actualiza una Location dado su ID en su record
@router.put('/locations/')
async def update_location(location: Location):
    location = jsonable_encoder(location)
    location_updated = location_collection.find_one_and_update({'_id': location['_id']}, 
                                                               {'$set': {"name": location['name'],
                                                                         "latitude": location['latitude'],
                                                                         "longitude": location['longitude']}},
                                                                return_document=ReturnDocument.AFTER)
    if not location_updated:
            raise GenericException("Location Id not found")
    return (location_updated)

# Agrega una nueva Location
@router.post("/locations")
def create_location(request: Request, location: LocationDto = Body(...)):
    # Valida si existe el registro
    location = jsonable_encoder(location)
    if location_collection.find_one({"name": location['name']}):
        raise GenericException("Location already exists in the system.")
    newrloc = {'_id': str(uuid.uuid1()),
               'name': location['name'],
               'latitude': location['latitude'],
               'longitude': location['longitude']
              }    
    new_location = location_collection.insert_one(newrloc)
    created_location = location_collection.find_one({"_id": new_location.inserted_id})

    # Inserta denormalizadamente en la coleccion reviews las combinaciones localidad(nueva)-categorias
    #Obtiene todas las categorias
    allcate = list(category_collection.find())
    print (allcate)
    # Recorre cada category para insertar la combinacion en la coleccion reviews
    for r in allcate:
        #Determina si no existe la combiacion y la inserta
        rev = review_collection.find({"$and": [{'category_name': r['name']},
                                               {'location_name': location['name']}]})
        if len(list(rev))==0:
            # inserta el registro de la categoria con todas las localidades
            newrev = {'_id': str(uuid.uuid1()),
                      'location_name': location['name'],
                      'category_name': r['name'],
                      'register_date': dt.datetime.now(),
                      'update_date': dt.datetime(1900,1,1,0,0),
                      'comments': ""
                     }
            new_review = review_collection.insert_one(newrev)
    return created_location
 