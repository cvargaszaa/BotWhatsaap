from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
import json

app = Flask (__name__)

#configuracion de la BD SQLITE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db =SQLAlchemy(app)

#Modelo de la tabla log
class log(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    fecha_y_hora = db.Column(db.DateTime, default=datetime.utcnow)
    texto = db.Column(db.TEXT)   

#Crear tabla si no existe
with app.app_context():
    db.create_all ()
        
#Funcion para ordenar los registros por fecha y hora
def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora,reverse=True)

@app.route('/')
def index():
#Obtener todos los registros de la BD.
    registros = log.query.all()
    registros_ordenados = ordenar_por_fecha_y_hora (registros)
    return render_template('index.html' ,registros=registros_ordenados)

mensajes_log = []

#Funcion para agregar mensajes y Guardar en la BD.
def agregar_mensajes_log(texto):
    mensajes_log.append(texto)
#Guardar el mensaje en la BD.
    nuevo_registro = log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()
    
#Token de verificacion para la configuracion
TOKEN_BOTGMI = "BOTGMI"

@app.route('/webhook', methods=['GET','POST'])
def webhook():
    if request.method == 'GET':
        challenge = verificar_token(request)
        return challenge
    elif request.method == 'POST':
        reponse = recibir_mensajes(request)
        return reponse

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')

    if challenge and token == TOKEN_BOTGMI:
        return challenge
    else:
        return jsonify({'error':'Token Invalido'}),401

def recibir_mensajes(req):
    req = request.get_json()
    agregar_mensajes_log(json.dumps(req))
    try:
        req = request.get_json()
        entry =req['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensaje = value['messages']
        
        if objeto_mensaje:
            messages = objeto_mensaje[0]

            if "type" in messages:
                tipo = messages["type"]

                if tipo == "interactive":
                    return 0

                if "text" in messages:
                    text = messages["text"]["body"]
                    numero = messages["from"]

                    agregar_mensajes_log(json.dumps(text))
                    agregar_mensajes_log(json.dumps(numero))
        
        return jsonify({'message':'EVENT_RECEIVED'})
    except Exception as e:
        return jsonify({'message':'EVENT_RECEIVED'})




if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)
