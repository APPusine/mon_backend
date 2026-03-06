from flask import Flask, request, jsonify
from flask_cors import CORS  # Important pour autoriser Adalo
import time
import random

app = Flask(__name__)
CORS(app)  # Permet les requêtes depuis n'importe quelle origine

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    photo_url = data.get('photo_url')
    prompt = data.get('prompt')
    
    # Simuler un traitement (analyse du prompt, génération 3D)
    time.sleep(5)
    
    # Ici vous appellerez plus tard GPT et CadQuery
    # Pour l'instant on renvoie une URL factice
    image_id = random.randint(1, 1000)
    result_url = f"https://via.placeholder.com/400x300?text=Bride+{image_id}"
    
    return jsonify({
        "status": "success",
        "modele3d_url": result_url,
        "message": "Génération terminée"
    })

@app.route('/api/generations', methods=['GET'])
def get_generations():
    # Pour tester la connexion (GET ALL)
    return jsonify([
        {"id": 1, "modele3d_url": "https://via.placeholder.com/400x300?text=Test1"},
        {"id": 2, "modele3d_url": "https://via.placeholder.com/400x300?text=Test2"}
    ])

@app.route('/api/generations/<id>', methods=['GET'])
def get_generation(id):
    return jsonify({
        "id": id,
        "status": "completed",
        "modele3d_url": f"https://via.placeholder.com/400x300?text=Bride+{id}"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Important pour Render