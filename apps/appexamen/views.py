from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from .models import *
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from time import strftime
import bcrypt

def index(request):
    if "first_name" in request.session:
        del request.session["first_name"]
    if 'id' in request.session:
        del request.session['id']
    return render(request, "index.html")

def registro(request):
    if request.method == "GET":
        return redirect("/")
    elif request.method =="POST": 
        error = Usuario.objects.basic_validator(request.POST)
      
        if len(error) > 3 or error["first_name"] != None or error["last_name"] != None or error["password"] != None:
           
            for key, value in error.items():
                messages.error(request, value, key)
            user= Usuario(
                first_name = request.POST["first_name"],
                last_name =  request.POST["last_name"],
                email =  request.POST["email"],
            )
            context = {
                "user": user
            }
           
            return render(request, 'index.html', context)
        else:
            
            contrasena= bcrypt.hashpw(request.POST["password"].encode(), bcrypt.gensalt()).decode()
            user = Usuario.objects.create(
                first_name = request.POST["first_name"],
                last_name =  request.POST["last_name"],
                email =  request.POST["email"],
                password =  contrasena
            )
            request.session['first_name']=request.POST["first_name"]
            request.session['id']=user.id
            context={
                "user":user
            }   
        return redirect("/dashboard")

def login(request):
    if request.method == "GET":
        return redirect("/")
     
    elif request.method =="POST":        
        error = Usuario.objects.login_validator(request.POST)
        if len(error) > 0:
            for key, value in error.items():
                messages.error(request, value, key)
               
            return redirect('/')
        else:
           
            user=Usuario.objects.get(email=request.POST['correoIngreso'])
            contrasenaARevisar=request.POST['contrasena']
            contrasena=user.password
            if bcrypt.checkpw(contrasenaARevisar.encode(), contrasena.encode()):
                request.session['first_name'] = user.first_name
                request.session['id']=user.id
                return redirect ('/dashboard')
            
            return redirect("/") 
def dashboard(request):
    if "id" in request.session:
        context ={
            "usuarios":Usuario.objects.all(),
            "misViajes":trip.objects.filter(creado_por__id=request.session["id"]).order_by("-updated_at"),
            "viajes": trip.objects.all().exclude(creado_por__id=request.session["id"]).exclude(paseo__id=request.session["id"]).order_by("-updated_at"),
            "otrosViajes":trip.objects.filter(paseo__id=request.session["id"])
        }       
        return render(request,'dashboard.html', context)
    return redirect("/")
   
def crearViaje(request):
    if "id" in request.session: 
        if request.method == "GET":
            return render(request, "crearViaje.html")
     
        elif request.method =="POST": 
            error = trip.objects.trip_validator(request.POST)
      
            if len(error) > 2 or error["destination"] != None or error["plan"] != None :
            
                for key, value in error.items():
                    messages.error(request, value, key)
                viaje= trip(
                    destination = request.POST["destination"],
                    plan =  request.POST["plan"],

                )
                context = {
                    "viaje": viaje
                }

                return render(request, 'crearViaje.html', context)

            else:
                user = Usuario.objects.get(id=request.session["id"])
                trip.objects.create(
                    destination = request.POST["destination"],
                    start_date = request.POST["start_date"],
                    end_date = request.POST["end_date"],
                    plan = request.POST["plan"],
                    creado_por = user,

                )


                return redirect("/dashboard")
    return redirect("/")
    ############################
def editar(request, idViaje):
    esteViaje=trip.objects.get(id=idViaje)
    if request.session["id"] == esteViaje.creado_por.id:
        inicio = esteViaje.start_date.strftime('%Y-%m-%d')
        fin = esteViaje.end_date.strftime('%Y-%m-%d')
        
        
        context = {
            "esteViaje": trip.objects.get(id=idViaje),
            "start_date":inicio,
            "end_date":fin,
        }
        
        if request.method == "GET":

            return render(request, "edit.html", context)
     
        elif request.method =="POST": 
            error = trip.objects.trip_validator(request.POST)
      
            if len(error) > 2 or error["destination"] != None or error["plan"] != None :
            
                for key, value in error.items():
                    messages.error(request, value, key)
                viaje= trip(
                    destination = request.POST["destination"],
                    plan =  request.POST["plan"],
                   
                )
                context = {
                    "viaje": viaje,
                    "esteViaje": trip.objects.get(id=idViaje),
                    "start_date":inicio,
                    "end_date":fin,
                }
               
                return render(request, 'edit.html', context)
    
            else:
                esteViaje.destination=request.POST["destination"]
                esteViaje.start_date=request.POST["start_date"]
                esteViaje.end_date=request.POST["end_date"]
                esteViaje.plan = request.POST["plan"]
                esteViaje.save()
                return redirect("/dashboard") 

    return redirect("/")

     ##########################
def detalle(request, idViaje):
    if "id" in request.session:
        esteViaje=trip.objects.get(id=idViaje)
        user = Usuario.objects.get(id=request.session["id"])
        pasajeros = Usuario.objects.filter(viaje_invitado__id=idViaje)

        context ={
            "esteViaje":esteViaje,
            "user":user,
            "pasajeros":pasajeros
        }       
        return render(request,'detalle.html', context)
    return redirect("/") 

def join(request, idViaje):
    if "id" in request.session:
        esteViaje=trip.objects.get(id=idViaje)
        user = Usuario.objects.get(id=request.session["id"])
        esteViaje.paseo.add(user)
        user.viaje_invitado.add(esteViaje)

    return redirect("/dashboard")
def abortar(request,idViaje):
    if "id" in request.session:
        esteViaje=trip.objects.get(id=idViaje)
        user = Usuario.objects.get(id=request.session["id"])
        esteViaje.paseo.remove(user)
        user.viaje_invitado.remove(esteViaje)

    return redirect("/dashboard")

def eliminar(request,idViaje):
    esteViaje=trip.objects.get(id=idViaje)
    if request.session["id"] == esteViaje.creado_por.id:
        user = Usuario.objects.get(id=request.session["id"])
        esteViaje.delete()
        
        return redirect("/dashboard")
    return redirect("/") 

def salir(request):
    if "first_name" in request.session:
        del request.session["first_name"]
    if 'id' in request.session:
        del request.session['id']
    return redirect("/") 
# Create your views here.
