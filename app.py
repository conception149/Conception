#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ============================================================
# app.py - Serveur Flask avec envoi Telegram
# Installation : pip install flask requests python-dotenv
# Lancement : python app.py
# ============================================================

import os
import json
import uuid
import threading
import re
import requests
import logging
from flask import Flask, request, redirect, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
from dotenv import load_dotenv

# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

# --- Telegram ---
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

if not BOT_TOKEN or not CHAT_ID:
    raise RuntimeError(
        "BOT_TOKEN et CHAT_ID doivent être définis dans .env"
    )

# --- Fichiers ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 Mo

# --- Serveur ---
DEBUG_MODE = False
HOST = '0.0.0.0'
PORT = 5000

# ============================================================
# INITIALISATION
# ============================================================

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 20 * MAX_FILE_SIZE + (10 * 1024 * 1024)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Journal des consentements ---
CONSENT_LOG_FILE = 'consentements.log'
_consent_lock = threading.Lock()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# FONCTIONS
# ============================================================

def escape_markdown(text):
    """Échappe les caractères spéciaux Markdown pour Telegram"""
    if not text:
        return ''
    # Caractères à échapper pour Telegram Markdown
    chars_to_escape = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in chars_to_escape:
        text = text.replace(char, '\\' + char)
    return text

def clean_text(text):
    """Nettoie le texte pour éviter les problèmes d'encodage"""
    if not text:
        return 'Non renseigné'
    # Remplacer les caractères problématiques
    text = text.replace('\n', ' ').replace('\r', '')
    # Supprimer les caractères non imprimables
    text = ''.join(char for char in text if ord(char) >= 32 or char == ' ')
    return text.strip()

def allowed_file(filename):
    """Vérifier si l'extension du fichier est autorisée"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_client_ip():
    """Récupérer l'IP réelle du client"""
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or 'inconnu'

def enregistrer_consentement(age_confirme, usage_confirme, volume_confirme):
    """Enregistre une preuve de consentement horodatée"""
    consent_id = str(uuid.uuid4())
    record = {
        'consent_id': consent_id,
        'horodatage_utc': datetime.now(timezone.utc).isoformat(),
        'ip': get_client_ip(),
        'user_agent': request.headers.get('User-Agent', 'inconnu'),
        'age_confirme_18_plus': bool(age_confirme),
        'usage_ia_confirme': bool(usage_confirme),
        'volume_200_300_confirme': bool(volume_confirme),
    }

    with _consent_lock:
        with open(CONSENT_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

    logger.info(f"✅ Consentement enregistré : {consent_id}")
    return consent_id

def send_video_to_telegram(file_path, caption):
    """Envoie une vidéo vers Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    
    try:
        with open(file_path, 'rb') as f:
            files = {'video': f}
            data = {
                'chat_id': CHAT_ID,
                'caption': caption[:1024],  # Limite Telegram
                'parse_mode': 'Markdown'
            }
            response = requests.post(url, data=data, files=files, timeout=60)
            
        if response.status_code == 200:
            logger.info(f"✅ Vidéo envoyée à Telegram")
            return True
        else:
            logger.error(f"❌ Erreur envoi vidéo : {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Exception envoi vidéo : {e}")
        return False

def send_message_to_telegram(text):
    """Envoie un message texte vers Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # Nettoyer le texte
    clean_text_content = clean_text(text)
    
    data = {
        'chat_id': CHAT_ID,
        'text': clean_text_content,
        'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(url, data=data, timeout=30)
        if response.status_code == 200:
            logger.info("✅ Message Telegram envoyé")
            return True
        else:
            logger.error(f"❌ Erreur envoi message : {response.text}")
            # Réessayer sans Markdown si erreur
            if 'parse' in response.text:
                logger.info("🔄 Réessai sans Markdown...")
                data['parse_mode'] = None
                response2 = requests.post(url, data=data, timeout=30)
                if response2.status_code == 200:
                    logger.info("✅ Message envoyé sans Markdown")
                    return True
            return False
    except Exception as e:
        logger.error(f"❌ Exception envoi message : {e}")
        return False

def format_telegram_message(data):
    """Construire le message formaté pour Telegram"""
    # Nettoyer toutes les entrées
    prenom = clean_text(data.get('prenom', 'Non renseigné'))
    nom = clean_text(data.get('nom', 'Non renseigné'))
    email = clean_text(data.get('email', 'Non renseigné'))
    telephone = clean_text(data.get('telephone', 'Non renseigné'))
    age = clean_text(data.get('age', 'Non renseigné'))
    ville = clean_text(data.get('ville', 'Non renseigné'))
    specialite = clean_text(data.get('specialite', 'Non renseigné'))
    precision = clean_text(data.get('precision', ''))
    bio = clean_text(data.get('bio', ''))
    message = clean_text(data.get('message', ''))
    consent_id = clean_text(data.get('consent_id', 'Non renseigné'))
    video_count = data.get('video_count', 0)
    videos_uploaded_via = clean_text(data.get('videos_uploaded_via', 'telegram'))

    # Construction du message (format simple, sans Markdown complexe)
    text = "📥 NOUVELLE CANDIDATURE TITOKEUR(EUS)\n\n"
    text += f"📅 Date : {datetime.now().strftime('%d/%m/%Y à %H:%M')}\n\n"

    text += "👤 Identité\n"
    text += f"  Nom : {prenom} {nom}\n"
    text += f"  Email : {email}\n"
    text += f"  Téléphone : {telephone}\n"
    text += f"  Âge : {age} ans\n"
    text += f"  Ville : {ville}\n\n"

    text += "🎭 Profil artistique\n"
    text += f"  Spécialité : {specialite}"
    if precision:
        text += f" ({precision})"
    text += "\n"
    if bio:
        text += f"  Bio : {bio}\n\n"

    if message:
        text += f"💬 Message : {message}\n\n"

    text += f"📹 Vidéos : {video_count} vidéo(s)\n"
    text += f"📤 Envoi via : {videos_uploaded_via}\n\n"
    
    text += f"🔏 Consent ID : {consent_id}"

    return text

# ============================================================
# ROUTES FLASK
# ============================================================

@app.route('/')
def index():
    """Page d'accueil - affiche le formulaire"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Erreur</title></head>
        <body style="font-family: sans-serif; text-align: center; padding: 2rem;">
            <h1>❌ Erreur</h1>
            <p>Le fichier <code>index.html</code> est introuvable.</p>
        </body>
        </html>
        """, 404

@app.route('/consentement')
def page_consentement():
    """Page de consentement"""
    try:
        with open('consentement.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Fichier consentement.html introuvable.", 404

@app.route('/confirmation')
def confirmation():
    """Page de confirmation après soumission"""
    try:
        with open('confirmation.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Confirmation</title>
            <style>
                *{margin:0;padding:0;box-sizing:border-box;}
                body{font-family:'Segoe UI',sans-serif;background:linear-gradient(145deg,#f0f6fb,#dce8f2);
                     min-height:100vh;display:flex;align-items:center;justify-content:center;padding:2rem;}
                .card{max-width:600px;background:white;border-radius:40px;padding:3rem;text-align:center;box-shadow:0 30px 50px rgba(0,0,0,0.1);}
                .icon{font-size:4rem;margin-bottom:1rem;}
                h1{color:#1a4b6d;font-size:2rem;margin-bottom:0.5rem;}
                p{color:#2c4e6e;font-size:1.1rem;line-height:1.6;margin-bottom:1.5rem;}
                .btn{display:inline-block;background:#1a4b6d;color:white;padding:0.8rem 2.5rem;
                     border-radius:60px;text-decoration:none;font-weight:700;}
                .btn:hover{background:#0f3a55;}
                .details{text-align:left;background:#f5f9fe;border-radius:16px;padding:1.2rem;
                         margin:1.5rem 0;font-size:0.9rem;color:#1a3f59;}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="icon">✅</div>
                <h1>Merci pour votre candidature !</h1>
                <p>Vos informations ont été envoyées avec succès.</p>
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

@app.route('/enregistrer_consentement', methods=['POST'])
def route_enregistrer_consentement():
    """Enregistre le consentement et retourne consent_id"""
    try:
        data = request.get_json(force=True, silent=True) or {}

        age_confirme = data.get('age_confirme', False)
        usage_confirme = data.get('usage_confirme', False)
        volume_confirme = data.get('volume_confirme', False)

        if not (age_confirme and usage_confirme and volume_confirme):
            return jsonify({
                'success': False,
                'error': "Les trois confirmations sont requises."
            }), 400

        consent_id = enregistrer_consentement(age_confirme, usage_confirme, volume_confirme)
        return jsonify({'success': True, 'consent_id': consent_id})

    except Exception as e:
        logger.error(f"❌ Erreur enregistrement consentement : {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/send_to_drive', methods=['POST'])
def send_to_telegram():
    """Traite le formulaire et envoie à Telegram"""
    
    logger.info("📥 Réception d'une nouvelle candidature")
    
    try:
        # ============================================================
        # 1. RÉCUPÉRATION DES DONNÉES
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
        message = request.form.get('message', '')
        consent_id = request.form.get('consent_id', '')
        
        # Nouveaux champs pour le mode Google Forms
        video_count = request.form.get('video_count', 0)
        videos_uploaded_via = request.form.get('videos_uploaded_via', 'telegram')

        # Vérification du consentement
        if not consent_id:
            logger.warning("⚠️ Envoi refusé : aucun consent_id fourni")
            return "❌ Consentement requis. Merci de passer d'abord par la page de consentement.", 400

        # ============================================================
        # 2. RÉCUPÉRATION DES VIDÉOS (si envoyées directement)
        # ============================================================
        
        video_count_uploaded = 0
        video_files = []
        
        # Vérifier s'il y a des vidéos dans la requête
        video_keys = sorted(
            [k for k in request.files.keys() if k.startswith('video')],
            key=lambda k: int(''.join(filter(str.isdigit, k)) or 0)
        )
        
        for video_key in video_keys:
            video = request.files.get(video_key)
            if not video or not video.filename:
                continue
                
            if not allowed_file(video.filename):
                logger.warning(f"⚠️ Extension non autorisée : {video.filename}")
                continue
            
            # Sauvegarder temporairement
            filename = secure_filename(video.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            video.save(filepath)
            
            # Vérifier la taille
            file_size = os.path.getsize(filepath)
            if file_size > MAX_FILE_SIZE:
                os.remove(filepath)
                logger.warning(f"⚠️ Vidéo trop lourde : {file_size/1024/1024:.1f} Mo")
                continue
            
            video_files.append((filepath, filename))
            video_count_uploaded += 1

        # ============================================================
        # 3. ENVOI À TELEGRAM
        # ============================================================
        
        # Construire le message
        final_video_count = int(video_count) if video_count and int(video_count) > 0 else video_count_uploaded
        
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
            'message': message,
            'consent_id': consent_id,
            'video_count': final_video_count,
            'videos_uploaded_via': videos_uploaded_via if videos_uploaded_via else 'telegram'
        }
        
        # Envoyer le message texte
        text = format_telegram_message(data)
        
        # Log du message avant envoi
        logger.info(f"📤 Envoi du message : {text[:200]}...")
        
        success = send_message_to_telegram(text)
        
        if not success:
            logger.warning("⚠️ Échec de l'envoi du message, mais on continue")
        
        # Envoyer les vidéos (si présentes)
        for filepath, filename in video_files:
            caption = f"Vidéo de {prenom} {nom}\nID: {consent_id[:8]}..."
            send_video_to_telegram(filepath, caption)
            
            # Nettoyer le fichier temporaire
            try:
                os.remove(filepath)
            except Exception as e:
                logger.warning(f"⚠️ Impossible de supprimer {filepath}: {e}")
        
        # ============================================================
        # 4. LOG LOCAL
        # ============================================================
        
        log_text = f"""
{"="*60}
📥 NOUVELLE CANDIDATURE TITOKEUR(EUS)
📅 Date : {datetime.now().strftime('%d/%m/%Y à %H:%M')}

👤 Identité
  • Nom : {prenom} {nom}
  • Email : {email}
  • Téléphone : {telephone}
  • Âge : {age} ans
  • Ville : {ville}

📹 Vidéos : {final_video_count} vidéo(s) ({videos_uploaded_via})
🔏 Consent ID : {consent_id}
{"="*60}
"""
        with open('candidatures.log', 'a', encoding='utf-8') as f:
            f.write(log_text + "\n")
        
        logger.info(f"✅ Candidature traitée : {final_video_count} vidéos, ID: {consent_id[:8]}...")
        
        return redirect('/confirmation')

    except Exception as e:
        logger.error(f"❌ Erreur générale : {e}")
        import traceback
        traceback.print_exc()
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
# ROUTES API (pour les statistiques)
# ============================================================

@app.route('/api/stats')
def api_stats():
    """Retourne des statistiques sur les candidatures"""
    try:
        if os.path.exists('candidatures.log'):
            with open('candidatures.log', 'r', encoding='utf-8') as f:
                content = f.read()
                count = content.count('NOUVELLE CANDIDATURE')
        else:
            count = 0
            
        return jsonify({
            'status': 'ok',
            'total_candidatures': count,
            'server_time': datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/videos')
def api_videos():
    """Liste des vidéos (placeholder)"""
    return jsonify({
        'status': 'info',
        'message': 'Les vidéos sont envoyées via Telegram'
    })

# ============================================================
# LANCEMENT DU SERVEUR
# ============================================================

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 SERVEUR FLASK - TITOKEUR(EUS)")
    print("=" * 50)
    print(f"📁 Dossier upload : {UPLOAD_FOLDER}")
    print(f"🤖 Bot Token : {BOT_TOKEN[:10]}...")
    print(f"👤 Chat ID : {CHAT_ID}")
    print(f"📍 Local : http://127.0.0.1:{PORT}")
    print("=" * 50)
    print("📋 Routes disponibles :")
    print("  GET  /                   - Formulaire d'envoi")
    print("  GET  /consentement       - Page de consentement")
    print("  GET  /confirmation       - Page de confirmation")
    print("  POST /enregistrer_consentement - Enregistrer le consentement")
    print("  POST /send_to_drive      - Envoyer les vidéos vers Telegram")
    print("  GET  /api/stats          - Statistiques")
    print("=" * 50)
    print("🔴 Appuyez sur Ctrl+C pour arrêter")
    print("=" * 50)
    
    port = int(os.environ.get('PORT', PORT))
    app.run(host=HOST, port=port, debug=DEBUG_MODE)