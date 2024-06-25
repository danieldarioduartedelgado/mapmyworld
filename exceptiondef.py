
######
###### Archivo destinado para definir clases Exception en caso de requerir personalizar el manejo de excepciones
######

# Clase para el manejo generico de excepciones de la app
class GenericException(Exception):
    def __init__(self, message: str):
        self.message = message
