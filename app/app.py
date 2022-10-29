import os

import requests
from flask import Flask, json, Response
from flask import request
from flask import make_response
from flask_mongoengine import MongoEngine
from flask_expects_json import expects_json
from flask import jsonify

UPLOAD_FOLDER = 'static/files'
ONSALE_DATE = "onsaleDate"
ALLOWED_EXTENSIONS = {'txt'}

app = Flask(__name__, template_folder='template')
app.debug = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = '3l2gribj4YoX9ZEgF0nIWnV7pmpwHXEy0QE6i9njoOrpWDBVkf'

print('mongodb://' + os.environ.get("MONGO_USER") + '@' + os.environ.get("MONGO_HOST") + ':' + os.environ.get(
        "MONGO_PORT") + '/' + os.environ.get("MONGO_DB"))
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
    },
    "required": ["id", "imagen", "name", "onsaleDate"]
}

@app.route('/api/comic', methods=["POST"])
@expects_json(schemaComicRegister)
def comic_store():
    auth = request.headers.get('Authorization')
    print("auth")
    print(auth)
    if not auth:
        return make_response({"mensaje":'could not verify'}, 401, {'WWW.Authentication': 'Basic realm: "login required"'})
    user_url = os.environ.get("USER_URL")
    comic_url = os.environ.get("COMIC_URL")
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': auth,
    }
    print(user_url)
    response = requests.request("GET", user_url, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        id = response_json["id"]
        email = response_json["email"]
        print(email)
        userExist = User.objects(email=email).first()
        print(userExist)
        if userExist is not None:
            url = comic_url+"/"+str(request.json["id"])
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
            print(url)
            response = requests.request("GET", url, headers=headers)
            userExist.comics = Comics(
                comic_id=request.json["id"],
                name=request.json["name"],
                imagen=request.json["imagen"],
                onsaleDate=request.json["onsaleDate"]
            )
            userExist.save()
            response = {
                "mensaje": "Se resitro correctamente el comic",
            }
            return Response(response=json.dumps(response), status=201, mimetype='application/json')
        else:
            response = {
                "mensaje": "El usuario no existe, y no se puede agregar"
            }
    else:
            response = {
                "mensaje": "El usuario no existe, y no se puede agregar"
            }
    return Response(response=json.dumps(response), status=400, mimetype='application/json')


class Comics(db.EmbeddedDocument):
    comic_id = db.IntField()
    name = db.StringField()
    imagen = db.StringField()
    onsaleDate = db.StringField()

class User(db.Document):
    __tablename__ = 'users'
    name = db.StringField(required=True)
    age = db.IntField()
    email = db.StringField()
    password = db.StringField()
    comics = db.EmbeddedDocumentField(Comics)