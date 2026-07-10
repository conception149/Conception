#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ============================================================
# app.py - Serveur Flask pour le recensement Titokeur(eus)
# Installation : pip install flask requests python-dotenv
# Lancement : python app.py
# ============================================================

import os
import requests
import logging
from flask import Flask, request, redirect, url_for, render_template_string, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime

# ============================================================
# CONFIGURATION - À MODIFIER
# ============================================================

# --- Telegram ---
BOT_TOKEN = '8774308699:AAGVozIXsYmJIIXn_ulMZiemsgCesg9wS_E'  # Votre token
CHAT_ID = '6979130071'  # Remplacez par votre ID Telegram

# --- Fichiers ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 Mo

# --- Serveur ---
DEBUG_MODE = True  # Passer à False en production
HOST = '0.0.0.0'
PORT = 5000

# ============================================================
# INITIALISATION
# ============================================================

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200 Mo max

# Créer le dossier d'upload s'il n'existe pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# FONCTIONS
# ============================================================

def allowed_file(filename):
    """Vérifier si l'extension du fichier est autorisée"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_telegram_message(text):
    """Envoyer un message texte vers Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, data=data, timeout=30)
        if response.status_code == 200:
            logger.info("✅ Message Telegram envoyé")
            return response.json()
        else:
            logger.error(f"❌ Erreur envoi message : {response.text}")
            return None
    except Exception as e:
        logger.error(f"❌ Exception envoi message : {e}")
        return None

def send_telegram_video(file_path, caption=''):
    """Envoyer une vidéo vers Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    
    try:
        with open(file_path, 'rb') as f:
            files = {'video': f}
            data = {
                'chat_id': CHAT_ID,
                'caption': caption,
                'supports_streaming': True
            }
            response = requests.post(url, data=data, files=files, timeout=120)
            if response.status_code == 200:
                logger.info(f"✅ Vidéo envoyée : {os.path.basename(file_path)}")
                return response.json()
            else:
                logger.error(f"❌ Erreur envoi vidéo : {response.text}")
                return None
    except Exception as e:
        logger.error(f"❌ Exception envoi vidéo : {e}")
        return None

def format_telegram_message(data):
    """Construire le message formaté pour Telegram"""
    prenom = data.get('prenom', 'Non renseigné')
    nom = data.get('nom', 'Non renseigné')
    email = data.get('email', 'Non renseigné')
    telephone = data.get('telephone', 'Non renseigné')
    age = data.get('age', 'Non renseigné')
    ville = data.get('ville', 'Non renseigné')
    specialite = data.get('specialite', 'Non renseigné')
    precision = data.get('precision', '')
    bio = data.get('bio', '')
    dispos = data.get('dispo', 'Aucune sélection')
    lien = data.get('lien', '')
    message = data.get('message', '')
    
    text = "📥 *NOUVELLE CANDIDATURE TITOKEUR(EUS)*\n\n"
    text += f"📅 *Date* : {datetime.now().strftime('%d/%m/%Y à %H:%M')}\n\n"
    
    text += "👤 *Identité*\n"
    text += f"Nom : {prenom} {nom}\n"
    text += f"Email : {email}\n"
    text += f"Téléphone : {telephone}\n"
    text += f"Âge : {age} ans\n"
    text += f"Ville : {ville}\n\n"
    
    text += "🎭 *Profil artistique*\n"
    text += f"Spécialité : {specialite}"
    if precision:
        text += f" ({precision})"
    text += "\n"
    if bio:
        text += f"Bio : {bio}\n\n"
    
    if dispos:
        text += f"🕒 *Disponibilités* : {dispos}\n\n"
    
    if lien:
        text += f"🔗 *Lien* : {lien}\n\n"
    
    if message:
        text += f"💬 *Message* : {message}\n\n"
    
    text += "📹 *Vidéos* : 2 vidéos envoyées (5 min max)"
    
    return text

# ============================================================
# ROUTES FLASK
# ============================================================

@app.route('/', methods=['GET'])
def index():
    """Page d'accueil - affiche le formulaire"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Erreur</title></head>
        <body style="font-family: sans-serif; text-align: center; padding: 2rem;">
            <h1>❌ Erreur</h1>
            <p>Le fichier <code>index.html</code> est introuvable.</p>
            <p>Assurez-vous qu'il est dans le même dossier que <code>app.py</code>.</p>
        </body>
        </html>
        """, 404

@app.route('/confirmation', methods=['GET'])
def confirmation():
    """Page de confirmation après soumission"""
    try:
        with open('confirmation.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        # Page de confirmation par défaut
        return """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Confirmation</title>
            <style>
                * { margin:0; padding:0; box-sizing:border-box; }
                body {
                    font-family: 'Segoe UI', sans-serif;
                    background: linear-gradient(145deg, #f0f6fb 0%, #dce8f2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 2rem;
                }
                .card {
                    max-width: 600px;
                    background: white;
                    border-radius: 40px;
                    padding: 3rem;
                    text-align: center;
                    box-shadow: 0 30px 50px rgba(0,0,0,0.1);
                }
                .icon { font-size: 4rem; margin-bottom: 1rem; }
                h1 { color: #1a4b6d; font-size: 2rem; margin-bottom: 0.5rem; }
                p { color: #2c4e6e; font-size: 1.1rem; line-height: 1.6; margin-bottom: 1.5rem; }
                .btn {
                    display: inline-block;
                    background: #1a4b6d;
                    color: white;
                    padding: 0.8rem 2.5rem;
                    border-radius: 60px;
                    text-decoration: none;
                    font-weight: 700;
                }
                .btn:hover { background: #0f3a55; }
                .details {
                    text-align: left;
                    background: #f5f9fe;
                    border-radius: 16px;
                    padding: 1.2rem;
                    margin: 1.5rem 0;
                    font-size: 0.9rem;
                    color: #1a3f59;
                }
            </style>
        </head>
        <body>
            <div class="card">
                <div class="icon">✅</div>
                <h1>Merci pour votre candidature !</h1>
                <p>Vos informations et vidéos ont été envoyées avec succès.</p>
                <div class="details">
                    <strong>📌 Prochaines étapes :</strong><br>
                    • Nous examinerons votre candidature sous 48h<br>
                    • Vous recevrez un retour sur votre email<br>
                    • Si votre profil est retenu, nous vous contacterons
                </div>
                <a href="/" class="btn">⬅ Retour à l'accueil</a>
            </div>
        </body>
        </html>
        """

@app.route('/send_to_telegram', methods=['POST'])
def handle_form():
    """Traiter le formulaire et envoyer à Telegram"""
    
    logger.info("📥 Réception d'une nouvelle candidature")
    
    try:
        # ============================================================
        # 1. RÉCUPÉRATION DES DONNÉES TEXTE
        # ============================================================
        
        prenom = request.form.get('prenom', 'Non renseigné')
        nom = request.form.get('nom', 'Non renseigné')
        email = request.form.get('email', 'Non renseigné')
        telephone = request.form.get('telephone', 'Non renseigné')
        age = request.form.get('age', 'Non renseigné')
        ville = request.form.get('ville', 'Non renseigné')
        specialite = request.form.get('specialite', 'Non renseigné')
        precision = request.form.get('precision', '')
        bio = request.form.get('bio', '')
        dispo_list = request.form.getlist('dispo[]')
        dispos = ', '.join(dispo_list) if dispo_list else 'Aucune sélection'
        lien = request.form.get('lien', '')
        message = request.form.get('message', '')
        
        # ============================================================
        # 2. CONSTRUIRE LE MESSAGE
        # ============================================================
        
        data = {
            'prenom': prenom,
            'nom': nom,
            'email': email,
            'telephone': telephone,
            'age': age,
            'ville': ville,
            'specialite': specialite,
            'precision': precision,
            'bio': bio,
            'dispo': dispos,
            'lien': lien,
            'message': message
        }
        
        text = format_telegram_message(data)
        
        # ============================================================
        # 3. ENVOYER LE MESSAGE TEXTE
        # ============================================================
        
        result = send_telegram_message(text)
        if not result:
            logger.warning("⚠️ Le message texte n'a pas pu être envoyé")
        
        # ============================================================
        # 4. RÉCUPÉRATION ET ENVOI DES VIDÉOS
        # ============================================================
        
        saved_files = []
        video_files = ['video1', 'video2']
        
        for i, video_key in enumerate(video_files, 1):
            video = request.files.get(video_key)
            if video and video.filename and allowed_file(video.filename):
                # Nom sécurisé
                filename = secure_filename(f"video{i}_{prenom}_{nom}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
                # Corriger l'extension si nécessaire
                ext = video.filename.rsplit('.', 1)[1].lower()
                if ext not in ['mp4', 'mov', 'avi', 'mkv', 'webm']:
                    ext = 'mp4'
                filename = filename.rsplit('.', 1)[0] + '.' + ext
                
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                try:
                    video.save(filepath)
                    file_size = os.path.getsize(filepath)
                    
                    if file_size > MAX_FILE_SIZE:
                        os.remove(filepath)
                        logger.warning(f"⚠️ Vidéo {i} trop lourde : {file_size/1024/1024:.1f} Mo")
                    else:
                        saved_files.append(filepath)
                        caption = f"🎬 Vidéo {i} - {prenom} {nom}"
                        send_telegram_video(filepath, caption)
                        logger.info(f"✅ Vidéo {i} envoyée")
                except Exception as e:
                    logger.error(f"❌ Erreur traitement vidéo {i} : {e}")
        
        # ============================================================
        # 5. NETTOYAGE (optionnel)
        # ============================================================
        # Décommentez pour supprimer les fichiers après envoi
        # for filepath in saved_files:
        #     try:
        #         os.remove(filepath)
        #         logger.info(f"🗑️ Fichier supprimé : {filepath}")
        #     except Exception as e:
        #         logger.error(f"❌ Erreur suppression : {e}")
        
        logger.info("✅ Candidature traitée avec succès")
        
        # ============================================================
        # 6. REDIRECTION VERS LA CONFIRMATION
        # ============================================================
        
        return redirect('/confirmation')
        
    except Exception as e:
        logger.error(f"❌ Erreur générale : {e}")
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Erreur</title></head>
        <body style="font-family: sans-serif; text-align: center; padding: 2rem;">
            <h1>❌ Une erreur est survenue</h1>
            <p>Veuillez réessayer ou contacter l'administrateur.</p>
            <p style="color: #c44536; font-size: 0.9rem;">Erreur : {str(e)}</p>
            <a href="/">⬅ Retour à l'accueil</a>
        </body>
        </html>
        """, 500

# ============================================================
# LANCEMENT DU SERVEUR
# ============================================================

if __name__ == '__main__':

    print("=" * 50)
    print("🚀 SERVEUR FLASK - TITOKEUR(EUS)")
    print("=" * 50)
    print(f"📁 Dossier upload : {UPLOAD_FOLDER}")
    print(f"🤖 Bot Token : {BOT_TOKEN[:15]}...")
    print(f"👤 Chat ID : {CHAT_ID}")
    print(f"📍 Accédez à : http://{HOST}:{PORT}")
    print(f"📍 Local : http://127.0.0.1:{PORT}")
    print("=" * 50)
    print("🔴 Appuyez sur Ctrl+C pour arrêter")
    print("=" * 50)
    port = int(os.environ.get('PORT', 5000))  # Render donne le PORT
    app.run(host='0.0.0.0', port=port, debug=False)