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
                
                #Guardar Log en la BD
                agregar_mensajes_log(json.dumps(tipo))
                agregar_mensajes_log(json.dumps(messages))

                if tipo == "interactive":
                    tipo_interactivo = messages["interactive"]["type"]
                    
                    if tipo_interactivo == "button_reply":
                        text = messages["interactive"]["button_reply"]["id"]
                        numero = messages["from"]

                        enviar_mensajes_whatsapp(text,numero)
                    
                    elif tipo_interactivo == "list_reply":
                        text = messages["interactive"]["list_reply"]["id"]
                        numero = messages["from"]

                        enviar_mensajes_whatsapp(text,numero)
                        
                if "text" in messages:
                    text = messages["text"]["body"]
                    numero = messages["from"]

                    enviar_mensajes_whatsapp(text,numero)
                    
                    #Guardar Log en la BD
                    agregar_mensajes_log(json.dumps(text))
                    agregar_mensajes_log(json.dumps(numero))
                    
        return jsonify({'message':'EVENT_RECEIVED'})
    except Exception as e:
        return jsonify({'message':'EVENT_RECEIVED'})

def enviar_mensajes_whatsapp(texto,number):
    texto = texto.lower()
    
    if "hola" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive":{
                "type":"button",
                "body": {
                    "text": "✨¡Bienvenido!✨\n \n Mi nombre es *P.A.NDora*, la asistente virtual del Negocio Internacional de Empresas Polar🌎\n \n¿En que puedo ayudarte?👩🏻‍💼\n"
                },
                "footer": {
                    "text": "Por Favor indicame si eres:"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply":{
                                "id":"btnsi",
                                "title":"Cliente"
                            }
                        },{
                            "type": "reply",
                            "reply":{
                                "id":"concom",
                                "title":"Consumidor"
                            }
                        }
                    ]
                }
            }
        }          
    elif "concom" in texto:
        data ={
            "messaging_product": "whatsapp",
            "to": number,
            "type": "interactive",
            "interactive":{
                "type" : "list",
                "body": {
                    "text": "Selecciona Alguna Opción"
                },
                "footer": {
                    "text": "Selecciona una de las opciones para poder ayudarte"
                },
                "action":{
                    "button":"Ver Opciones",
                    "sections":[
                        {
                            "title":"Compra y Venta",
                            "rows":[
                                {
                                    "id":"btncompra",
                                    "title" : "Comprar",
                                    "description": "Compra los mejores articulos de tecnologia"
                                },
                                {
                                    "id":"btnvender",
                                    "title" : "Vender",
                                    "description": "Vende lo que ya no estes usando"
                                }
                            ]
                        },{
                            "title":"Distribución y Entrega",
                            "rows":[
                                {
                                    "id":"btndireccion",
                                    "title" : "Local",
                                    "description": "Puedes visitar nuestro local."
                                },
                                {
                                    "id":"btnentrega",
                                    "title" : "Entrega",
                                    "description": "La entrega se realiza todos los dias."
                                }
                            ]
                        }
                    ]
                }
            }
        }    
    elif "btnq" in texto:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                    "link": "https://empresaspolar.com/pdf/POLAR_4web.pdf",
                    "caption": "Empresas Polar ¿Quienes somos?"
                }
            }
    elif "btnpro" in texto:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                    "link": "https://empresaspolar.com/files/Lista_APC_activos.pdf",
                    "caption": "Lista de Productos Activos - Disponibles"
                }
            }
    elif "btnven" in texto:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                    "link": "https://www.ign.es/espmap/mapas_mundo_bach/pdf/Mundo_Mapa_04.pdf",
                    "caption": "Donde estamos presente - Puntos de venta Autorizados"
                }
        }
    else:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive":{
                "type":"button",
                "body": {
                    "text": "✨¡Bienvenido!✨\n \n Mi nombre es *P.A.NDora*, la asistente virtual del Negocio Internacional de Empresas Polar🌎\n \n¿En que puedo ayudarte?👩🏻‍💼\n"
                },
                "footer": {
                    "text": "*Por Favor indicame si eres:*"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply":{
                                "id":"cli",
                                "title":"Cliente - Distribuidor"
                            }
                        },{
                            "type": "reply",
                            "reply":{
                                "id":"concom",
                                "title":"Consumidor - Comprador"
                            }
                        }
                    ]
                }
            }
        }
        
    #Convertir el diccionaria a formato JSON
    data=json.dumps(data)
    
    headers = {
        "Content-Type" : "application/json",
        "Authorization" : "Bearer EAAQ5ZBipbEvkBOyjeluwOFwu8RxOPiplAnEckHmYXAy7M4whz3M9QVrgL6CjArHtmu7yDx2FwWdb8NvYA641qwvYRmDpRJE7ZBZAiv31bKDau38TUq95oql6m7lqZBym00GVmTDovr08W21p5PM88NJQQmEhqO3VDRWU1GVNClijm4ZAf1oLj6DiTXZAUPQNZCQhSId3jjZBqUihKVOOcYcaHZCHJhkEZD"
    }
    connection = http.client.HTTPSConnection("graph.facebook.com")
    
    try:
        connection.request("POST","/v19.0/329054006960772/messages", data, headers)
        response = connection.getresponse()
        print(response.status, response.reason)
    except Exception as e:
        agregar_mensajes_log(json.dumps(e))
    finally:
        connection.close()


if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)
