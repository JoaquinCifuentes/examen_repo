from __future__ import unicode_literals
from django.db import models
from datetime import datetime
from time import strftime
import bcrypt
import re


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
FIRST_NAME_REGEX = re.compile(r'^[a-zA-Z -]+$')
LAST_NAME_REGEX = re.compile(r'^[a-zA-Z -]+$')
class UsuariosManager(models.Manager):
    def basic_validator(self, postData):
        error={}
        error["first_name"] = self.validar_longitud("first_name", postData["first_name"], 5)
        error["last_name"] = self.validar_longitud("last_name", postData["last_name"], 5)
        error["password"] = self.validar_longitud("password", postData["password"], 4)

        if not FIRST_NAME_REGEX.match(postData["first_name"]):
            error["first_name"]="el nombre puede tener solo letras"  
        if not LAST_NAME_REGEX.match(postData["last_name"]):
            error["last_name"]="el nombre puede tener solo letras"  touch .gitignore
        if len(self.filter(email=postData["email"])) > 0:
            error["email"]="el email ya existe, por favor intenta logearte"
        if not EMAIL_REGEX.match(postData["email"]):
            error["email"]="el mail no tiene un formato valido"
        if postData["password"] != postData["confirm"]:
            error["confirm"]= "las contraseñas deben ser iguales"

        return error

    def login_validator(self, datos):
        error={}
        if len(self.filter(email=datos["correoIngreso"])) == 0:
            error["correoIngreso"]="el email no esta registrado, te invitamos a crear tu usuario"
            return error
        if len(datos["correoIngreso"])==0:
            error["correoIngreso"]="debes ingresar un email"
        
        user=Usuario.objects.get(email=datos['correoIngreso'])
        contrasenaARevisar=datos['contrasena']
        contrasena=user.password
        if bcrypt.checkpw(contrasenaARevisar.encode(), contrasena.encode()) == False:
            error["contrasena"]= "malo tu password"
        return error

    def validar_longitud(self, campo, cadena, largoMinimo):
        error ={}
        if len(cadena)< largoMinimo:
            return (f"{campo} no puede ser menor que {largoMinimo} caracteres.")
    

class TripManager(models.Manager):
    def trip_validator(self, datos):
        error={}
        error["destination"] = self.validar_longitud("destination", datos["destination"], 3)
        error["plan"] = self.validar_longitud("plan", datos["plan"], 3)
        if len(datos["start_date"])==0 or len(datos["start_date"])>10:
            error["start_date"]= "ingrese fecha valida"
        else:
            fecha_inicio = datetime.strptime(datos["start_date"], '%Y-%m-%d')
            fecha_hoy = datetime.strptime(strftime("%Y-%m-%d"), '%Y-%m-%d')
            if fecha_inicio < fecha_hoy:
                error["start_date"]= "el viaje debe comenzar despues de hoy"

        if len(datos["end_date"])==0 or len(datos["end_date"])>10:
            error["end_date"]= "ingrese fecha valida"
        else:
            fecha_termino = datetime.strptime(datos["end_date"], '%Y-%m-%d')
            fecha_inicio = datetime.strptime(datos["start_date"], '%Y-%m-%d')
            if fecha_termino < fecha_inicio:
                error["end_date"]= "aún no implementamos el viaje en el tiempo"

        return error
    
    def validar_longitud(self, campo, cadena, largoMinimo):
        error ={}
        if len(cadena)< largoMinimo:
            return (f"{campo} no puede ser menor que {largoMinimo} caracteres.")
        


class Usuario(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects=UsuariosManager()

class trip(models.Model):
    destination = models.CharField(max_length=50)
    start_date =  models.DateField()
    end_date =  models.DateField()
    plan = models.TextField()
    creado_por = models.ForeignKey(Usuario,  related_name="viaje_creado", on_delete=models.CASCADE, blank=True, null=True, default=None)
    paseo = models.ManyToManyField(Usuario, related_name="viaje_invitado" )
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects=TripManager()
