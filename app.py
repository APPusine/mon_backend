import os
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
