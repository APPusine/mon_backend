import os
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

# Clé API OpenAI depuis les variables d'environnement
openai.api_key = os.getenv("OPENAI_API_KEY")

# -------------------------------------------------------------------
# Endpoint de test : GET /api/generations
# Utilisé par Adalo pour tester la connexion et découvrir les champs
# On inclut photo_url et prompt (même vides) pour forcer leur création
# -------------------------------------------------------------------
@app.route('/api/generations', methods=['GET'])
def get_generations():
    return jsonify([
        {
            "id": 1,
            "modele3d_url": "https://via.placeholder.com/400x300?text=Exemple+1",
            "photo_url": "",
            "prompt": ""
        },
        {
            "id": 2,
            "modele3d_url": "https://via.placeholder.com/400x300?text=Exemple+2",
            "photo_url": "",
            "prompt": ""
        }
    ])

# -------------------------------------------------------------------
# Endpoint de santé pour UptimeRobot
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
    # Récupérer les données JSON
    data = request.get_json()
    if not data:
        return jsonify({"error": "Données JSON attendues"}), 400

    photo_url = data.get('photo_url')
    prompt = data.get('prompt')

    if not photo_url or not prompt:
        return jsonify({"error": "Les champs 'photo_url' et 'prompt' sont requis"}), 400

    # Appel à GPT-4V
    try:
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

        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=500
        )
        gpt_output = response.choices[0].message.content

        # Essayer de parser le JSON
        try:
            analysis = json.loads(gpt_output)
        except json.JSONDecodeError:
            analysis = {"description": gpt_output}

    except Exception as e:
        print(f"Erreur GPT: {e}")
        analysis = {"description": f"Analyse par défaut pour : {prompt}"}

    # Pour l'instant, on renvoie une image placeholder (simulation)
    simulation_image_url = "https://via.placeholder.com/400x300?text=Modele+3D+genere"

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
    # Render fournit le port via l'environnement
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
