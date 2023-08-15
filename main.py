from  bson import json_util
from bson import ObjectId
import re

from flask import Flask, jsonify
from flask import request

from pymongo import MongoClient

import json

app = Flask(__name__)

# Connexion à la base de données MongoDB
client = MongoClient("mongodb+srv://daoudaboye:19961907@cluster0.tsjwazz.mongodb.net/Titanic")  # URL de connexion à la base de données
db = client["Titanic"]  # Remplacez 'nom_de_votre_base_de_donnees' par le nom de votre base de données
collection = db["bateau"]  # Remplacez 'nom_de_votre_collection' par le nom de votre collection


@app.route('/', methods=['GET'])
def accueil():
    return '''<p><h2 align="center" style="color: red;"><font color="blue">BIENVENUE SUR LA PAGE DE</font></h2>
              <p><h3 align="center">DAOUDA BOYE</h3></p>'''

# Route pour obtenir la liste complète des passagers
@app.route('/passengers', methods=['GET'])
def get_passenger_list():
    # Récupérer tous les documents (passagers) de la collection
    passenger_list = list(collection.find({}))


    # Renvoyer la liste complète des passagers en réponse JSON
    return '''La liste des passager est :'''+json.dumps(passenger_list, default=json_util.default)


# Route pour obtenir le nombre total de passagersss
@app.route('/nombre_passengers', methods=['GET'])
def nombre_passagers():
    # Comptage total des documents dans la collection
    count = collection.count_documents({})

    # Renvoyer le nombre total de passagers au format JSON
    return "Le nombre total de passager est :"+json.dumps(count, default=json_util.default)


# Route pour obtenir le nombre de passagers survivants et non survivants
@app.route('/passengers/stats/survival', methods=['GET'])
def get_survival_stats():
    # Calculer le nombre de passagers survivants
    survived_result = collection.count_documents({"Survived": 1})

    # Calculer le nombre de passagers non survivants
    not_survived_result = collection.count_documents({"Survived": 0})

    # Création de la réponse JSON
    response_data = {
        "Le nombre de passagers qui ont survecu est": survived_result,
        "Le nombre de passagers qui ne sont pas survecu": not_survived_result
    }

    # Conversion du dictionnaire en format JSON en utilisant json_util.default
    response_json = json.dumps(response_data, default=json_util.default)

    # Renvoyer la réponse JSON
    return response_json.replace(',', ',\n')


#Route pour obtenir l'age moyen des passagers
@app.route('/passengers/stats/age-moyen', methods=['GET'])
def get_average_age():
    # Calculer l'âge moyen des passagers
    result = collection.aggregate([
        {"$group": {"_id": None, "age-moyen": {"$avg": "$Age"}}}
    ])

    average_age = list(result)[0]["age-moyen"]

    return "L'age moyen des passager est de :" +json.dumps(average_age, default=json_util.default)


# Route pour ajouter un nouveau passagers
@app.route('/add', methods=['POST'])
def add_passenger():
    # Récupérer les données du corps de la requête POST
    data = request.get_json()

    # Insérer les données dans la collection
    result = collection.insert_one(data)

    # Vérifier si l'insertion a réussi
    if result.inserted_id:
        response_data = {
            "message": "Passager ajoute avec succes",
            "passenger_id": str(result.inserted_id)
        }
    else:
        response_data = {
            "message": "Erreur lors de l'ajout du passager"
        }

    # Conversion du dictionnaire en format JSON en utilisant json_util.default
    response_json = json.dumps(response_data, default=json_util.default)

    # Renvoyer la réponse JSON
    return response_json.replace(',','\n')


# Route pour mis à jour les informations d'un passager
@app.route('/passengers/<string:passenger_id>', methods=['PUT'])
def update_passenger(passenger_id):
    # Vérification de la validité de l'ID
    if not re.match(r'^[0-9a-fA-F]{24}$', passenger_id):
        return "ID de passager invalide", 400
    data = request.get_json()

    # Mettre à jour les informations du passager dans la base de données
    result = collection.update_one({"_id": ObjectId(passenger_id)}, {"$set": data})

    # Vérifier si la mise à jour a réussi
    if result.modified_count > 0:
        response_data = {
            "message": "Informations du passager mises a jour avec succes"
        }
    else:
        response_data = {
            "message": "Erreur lors de la mise a jour des informations du passager"
        }

    # Conversion du dictionnaire en format JSON en utilisant json_util.default
    response_json = json.dumps(response_data, default=json_util.default)

    # Renvoyer la réponse JSON
    return response_json, 200


# Route pour supprimer un passager
@app.route('/passengers/<string:passenger_id>', methods=['DELETE'])
def delete_passenger(passenger_id):
    result = collection.delete_one({"_id": ObjectId(passenger_id)})

    if result.deleted_count > 0:
        response_data = {
            "message": "Passager supprime avec succes"
        }
        response_code = 200
    else:
        response_data = {
            "message": "Passager non trouve ou erreur lors de la suppression"
        }
        response_code = 404

    response_json = json.dumps(response_data, default=json_util.default)
    return response_json, response_code





if __name__ == '__main__':
    app.debug = True
    app.run()
