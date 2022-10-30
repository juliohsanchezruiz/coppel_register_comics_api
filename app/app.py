import os

import requests
from flask import Flask, json, Response
from flask import request
from flask import make_response
from flask_mongoengine import MongoEngine
from flask_expects_json import expects_json
from datetime import datetime
from typing import Any, Hashable, Iterable, Optional

from mongoengine import EmbeddedDocumentField, ReferenceField

UPLOAD_FOLDER = 'static/files'
ONSALE_DATE = "onsaleDate"
ALLOWED_EXTENSIONS = {'txt'}

app = Flask(__name__, template_folder='template')
app.debug = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = '3l2gribj4YoX9ZEgF0nIWnV7pmpwHXEy0QE6i9njoOrpWDBVkf'

app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://' + os.environ.get("MONGO_USER") + '@' + os.environ.get("MONGO_HOST") + ':' + os.environ.get(
        "MONGO_PORT") + '/' + os.environ.get("MONGO_DB"),
    "username": os.environ.get("MONGO_USER"),
    "password": os.environ.get("MONGO_PASS"),
}

db = MongoEngine(app)

if __name__ == "__main__":
    app.run()

schemaComicRegister = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "imagen": {"type": "string"},
        "name": {"type": "string"},
        "onsaleDate": {"type": "string"},
        "personaje": {"type": "string"},
    },
    "required": ["id", "imagen", "name", "onsaleDate"]
}


@app.route('/api/addToLayaway', methods=["POST"])
@app.route('/api/addToLayaway/', methods=["POST"])
@expects_json(schemaComicRegister)
def comic_store():
    auth = request.headers.get('Authorization')
    if not auth:
        return make_response({"mensaje": 'could not verify'}, 401,
                             {'WWW.Authentication': 'Basic realm: "login required"'})
    user_url = os.environ.get("USER_URL")
    comic_url = os.environ.get("COMIC_URL")
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': auth,
    }
    response = requests.request("GET", user_url, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        id = response_json["id"]
        email = response_json["email"]
        userExist = User.objects(email=email).first()
        if userExist is not None:
            url = comic_url + "/" + str(request.json["id"])
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
            response_comic = requests.request("GET", url, headers=headers)
            print(response_comic.status_code)
            if response_comic.status_code == 200:
                # comics = userExist.comics
                # search_comics = buscar_dicc(comics, "comic_id", request.json["id"])
                print(userExist.to_json())
                print(userExist.id)
                # print(userExist._id)
                search_comics = Comics.objects(comic_id=request.json["id"], user=userExist.id).all()
                print(search_comics)
                if len(search_comics) == 0:
                    comic = Comics(
                        comic_id=request.json["id"],
                        name=request.json["name"],
                        imagen=request.json["imagen"],
                        onsaleDate=request.json["onsaleDate"],
                        user=userExist,
                        character=request.json.get("character", ""),
                        created_at=datetime.now())
                    comic.save()

                    response = {
                        "mensaje": "Se resitro correctamente el comic",
                    }
                    return Response(response=json.dumps(response), status=201, mimetype='application/json')
                else:
                    response = {
                        "mensaje": "El comic ya fue registrado anteriormente"
                    }
            else:
                response = {
                    "mensaje": "El comic no existe"
                }
        else:
            response = {
                "mensaje": "El usuario no existe, y no se puede agregar"
            }
    else:
        response = {
            "mensaje": "Usuario invalido"
        }
    return Response(response=json.dumps(response), status=400, mimetype='application/json')


def buscar_dicc(it: Iterable[dict], clave: Hashable, valor: Any) -> Optional[dict]:
    for dicc in it:
        if dicc[clave] == valor:
            return dicc
    return None


class User(db.Document):
    __tablename__ = 'users'
    name = db.StringField(required=True)
    age = db.IntField()
    email = db.StringField()
    password = db.StringField()
    meta = {
        'indexes': [
            'email',  # single-field index
        ]
    }


class Comics(db.Document):
    comic_id = db.IntField()
    name = db.StringField()
    imagen = db.StringField()
    onsaleDate = db.StringField()
    character = db.StringField()
    created_at = db.DateTimeField(default=datetime.utcnow)
    user = db.ReferenceField(User)
