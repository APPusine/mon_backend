import os
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)  # Autorise les requêtes depuis n'importe quelle origine (dont Adalo)

# Configuration des clés API depuis les variables d'environnement Render
openai.api_key = os.getenv("OPENAI_API_KEY")
# Pour Meshy, tu ajouteras plus tard : MESHY_API_KEY = os.getenv("MESHY_API_KEY")

# -------------------------------------------------------------------
# Endpoint de test : GET /api/generations
# Utilisé par Adalo pour tester la connexion et découvrir les champs
# -------------------------------------------------------------------
@app.route('/api/generations', methods=['GET'])
def get_generations():
    # Retourne une liste d'exemples pour qu'Adalo puisse mapper les champs
    return jsonify([
        {
            "id": 1,
            "modele3d_url": "https://via.placeholder.com/400x300?text=Exemple+1"
        },
        {
            "id": 2,
            "modele3d_url": "https://via.placeholder.com/400x300?text=Exemple+2"
        }
    ])

# -------------------------------------------------------------------
# Endpoint de santé pour UptimeRobot (optionnel)
# -------------------------------------------------------------------
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "timestamp": time.time()})

# -------------------------------------------------------------------
# Endpoint principal : POST /api/generate
# Reçoit photo_url et prompt, analyse avec GPT-4V, retourne une URL d'image
# -------------------------------------------------------------------
@app.route('/api/generate', methods=['POST'])
def generate():
    # 1. Récupérer les données envoyées par Adalo
    data = request.get_json()
    if not data:
        return jsonify({"error": "Données JSON attendues"}), 400

    photo_url = data.get('photo_url')
    prompt = data.get('prompt')

    if not photo_url or not prompt:
        return jsonify({"error": "Les champs 'photo_url' et 'prompt' sont requis"}), 400

    # 2. Appeler GPT-4V pour analyser l'image et le prompt
    try:
        # Préparer le message pour GPT-4V
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Voici une photo et une description : '{prompt}'. Analyse l'image pour comprendre l'objet à concevoir. Décris ses dimensions, sa fonction, les éléments de fixation, etc. Sois technique et précis. Réponds en JSON avec les clés : objet, fonction, dimensions, contraintes, matériau_suggéré."
                    },
                    {
                        "type": "image_url",
                        "image_url": photo_url
                    }
                ]
            }
        ]

        # Appel à l'API OpenAI (GPT-4V)
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",  # ou "gpt-4-turbo" selon disponibilité
            messages=messages,
            max_tokens=500
        )

        # Extraire le contenu de la réponse
        gpt_output = response.choices[0].message.content

        # Tenter de parser le JSON
        try:
            analysis = json.loads(gpt_output)
        except json.JSONDecodeError:
            # Si ce n'est pas du JSON valide, on garde le texte brut
            analysis = {"description": gpt_output}

    except Exception as e:
        # En cas d'erreur avec GPT, on logge et on continue avec une analyse par défaut
        print(f"Erreur GPT: {e}")
        analysis = {"description": f"Analyse par défaut pour : {prompt}"}

    # 3. Pour l'instant, on génère une URL d'image placeholder (simulation)
    # Plus tard, tu appelleras ici Meshy avec l'analyse pour obtenir une vraie 3D
    simulation_image_url = "https://via.placeholder.com/400x300?text=Modele+3D+genere"

    # 4. Retourner la réponse à Adalo
    return jsonify({
        "status": "success",
        "modele3d_url": simulation_image_url,
        "analysis": analysis,
        "message": "Génération terminée (simulation)"
    })

# -------------------------------------------------------------------
# Point d'entrée pour lancer le serveur
# -------------------------------------------------------------------
if __name__ == '__main__':
    # Render fournit automatiquement le port via l'environnement
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Endpoint de test existant
@app.route('/api/generations', methods=['GET'])
def get_generations():
    return jsonify([
        {"id": 1, "modele3d_url": "https://via.placeholder.com/400x300?text=Test1"},
        {"id": 2, "modele3d_url": "https://via.placeholder.com/400x300?text=Test2"}
    ])

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

# Nouvel endpoint d'analyse
@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    photo_url = data.get('photo_url')
    prompt = data.get('prompt')
    # Pour gérer un dialogue, on pourrait aussi recevoir un historique
    # mais pour l'instant on part du principe que c'est la première interaction

    if not photo_url or not prompt:
        return jsonify({"error": "photo_url et prompt requis"}), 400

    try:
        # Appel à GPT-4V
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Tu es un expert en conception mécanique. L'utilisateur a fourni cette photo et ce prompt : '{prompt}'. "
                                    "Analyse la photo et le prompt pour comprendre ce qu'il veut concevoir. "
                                    "Tu dois extraire toutes les informations techniques pertinentes : dimensions, forme, fonction, contraintes, matériau, etc. "
                                    "Si certaines informations sont manquantes ou ambiguës, liste les questions à poser à l'utilisateur pour clarifier. "
                                    "Réponds au format JSON avec les clés suivantes : "
                                    "- 'description': une description technique de l'objet (texte). "
                                    "- 'parametres': un objet JSON avec les paramètres extraits (ex: longueur, largeur, etc.). "
                                    "- 'questions': une liste de questions à poser (chaîne de caractères). "
                                    "Si aucune question n'est nécessaire, mets une liste vide. "
                                    "Sois précis et utilise des unités (mm, etc.) si possible."
                        },
                        {
                            "type": "image_url",
                            "image_url": photo_url
                        }
                    ]
                }
            ],
            max_tokens=800,
            response_format={ "type": "json_object" }  # Force la réponse en JSON (disponible pour certains modèles)
        )

        # Récupérer la réponse
        gpt_output = response.choices[0].message.content
        # Parser le JSON
        try:
            result = json.loads(gpt_output)
        except:
            # Si le parsing échoue, on retourne un message d'erreur
            return jsonify({"error": "Réponse GPT invalide", "raw": gpt_output}), 500

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

