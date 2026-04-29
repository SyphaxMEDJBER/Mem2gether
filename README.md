# Mem2gether

Application web collaborative en temps réel construite avec Django et Channels.  
Le projet permet à plusieurs utilisateurs connectés de rejoindre une room, discuter, utiliser un tableau blanc, synchroniser une vidéo YouTube et ajouter des notes horodatées.

## Table des matieres

- [Mem2gether](#mem2gether)
  - [Table des matières](#table-des-matières)
  - [Aperçu](#aperçu)
  - [Fonctionnalités](#fonctionnalités)
  - [Stack technique](#stack-technique)
  - [Démarrage rapide](#démarrage-rapide)
    - [1. Cloner le dépôt](#1-cloner-le-dépôt)
    - [2. Créer un environnement virtuel](#2-créer-un-environnement-virtuel)
    - [3. Installer les dépendances](#3-installer-les-dépendances)
    - [4. Appliquer les migrations](#4-appliquer-les-migrations)
    - [5. Lancer le serveur](#5-lancer-le-serveur)
  - [Configuration](#configuration)
  - [API HTTP](#api-http)
    - [`GET /api/notes/?room_id=<id>`](#get-apinotesroom_idid)
    - [`POST /api/notes/`](#post-apinotes)
  - [WebSockets](#websockets)
  - [Structure du projet](#structure-du-projet)
  - [Sécurité et bonnes pratiques](#sécurité-et-bonnes-pratiques)

## Aperçu

Mem2gether est une plateforme de travail/groupe orientée synchronisation:

- un créateur ouvre une room et partage son code
- les participants rejoignent la session en direct
- les contenus et interactions sont diffusés en temps réel (chat, tableau blanc, vidéo, réactions)

## Fonctionnalités

- Authentification utilisateur (signup, signin, logout, profil, suppression de compte)
- Création et participation à des rooms privées via un identifiant court
- Chat temps réel par room
- Mode `YouTube`: synchronisation lecture/pause/seek et changement de vidéo depuis URL/ID
- Tableau blanc synchronisé entre le professeur et les étudiants
- Notes de cours associées à un timecode (API + interface room)
- Réactions emoji en temps réel
- API HTTP pour lire/ajouter des notes

## Stack technique

- Python 3.x
- Django 4.x
- Django Channels (WebSocket)
- SQLite (par défaut)
- HTML/CSS/JS (templates Django)

## Démarrage rapide

### 1. Cloner le dépôt

```bash
git clone https://github.com/SyphaxMEDJBER/Mem2gether.git
cd Mem2gether
```

### 2. Créer un environnement virtuel

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
pip install whitenoise daphne
```

### 4. Appliquer les migrations

```bash
python manage.py migrate
```

### 5. Lancer le serveur

Mode developpement:

```bash
python manage.py runserver
```

Mode ASGI (recommande pour tests WebSocket proches de la prod):

```bash
daphne -b 0.0.0.0 -p 8000 application.asgi:application
```

Acces local: `http://127.0.0.1:8000`

## Configuration

Le fichier principal est `application/settings.py`.

Points importants:

- `DEBUG = True` en local uniquement
- Base de donnees SQLite par defaut
- `CHANNEL_LAYERS` en memoire (`InMemoryChannelLayer`) pour le developpement
- Fichiers media servis depuis `media/`

Variables a adapter avant deployment:

- `SECRET_KEY`
- `ALLOWED_HOSTS`
- configuration SMTP (`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, etc.)

## API HTTP

### `GET /api/notes/?room_id=<id>`

Retourne la liste des notes de la room.

### `POST /api/notes/`

Ajoute une note.

Exemple payload JSON:

```json
{
  "room_id": "abcd1234",
  "content": "Definition importante",
  "timecode": 95
}
```

## WebSockets

Routes principales:

- `/ws/rooms/<room_id>/` : chat + events de room (participants, mode, fermeture)
- `/ws/youtube/<room_id>/` : synchronisation YouTube
- `/ws/reactions/<room_id>/` : reactions emoji

## Structure du projet

```text
application/        # Configuration Django (settings, urls, asgi, routing)
authentification/   # Inscription, connexion, profil
rooms/              # Métier principal: rooms, chat, tableau blanc, YouTube, notes, WS
templates/          # Templates HTML
static/             # Assets statiques (CSS, JS, images)
media/              # Uploads utilisateurs
manage.py
```

## Securite et bonnes pratiques

Avant une mise en production:

- ne jamais versionner de credentials (SMTP, secret key, etc.)
- passer les secrets via variables d'environnement
- remplacer `InMemoryChannelLayer` par Redis (`channels_redis`)
- configurer un stockage media adapte et une politique de retention
- activer les parametres de securite Django (HTTPS, CSRF/SESSION cookies, hosts stricts)

## Documentation detaillee

Une documentation plus complete est disponible dans
[`docs/PROJECT_DOCUMENTATION.md`](docs/PROJECT_DOCUMENTATION.md).

Elle decrit l'architecture, les roles, les modeles, les endpoints, les flux de
synchronisation YouTube/tableau blanc, les WebSockets et les commandes de test.
