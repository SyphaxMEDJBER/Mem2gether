# Mem2gether

Application web collaborative en temps reel construite avec Django et Channels.  
Le projet permet a plusieurs utilisateurs connectes de rejoindre une room, discuter, partager des images, synchroniser une video YouTube et ajouter des notes horodatees.

## Table des matieres

- [Mem2gether](#mem2gether)
  - [Table des matieres](#table-des-matieres)
  - [Apercu](#apercu)
  - [Fonctionnalites](#fonctionnalites)
  - [Stack technique](#stack-technique)
  - [Demarrage rapide](#demarrage-rapide)
    - [1. Cloner le depot](#1-cloner-le-depot)
    - [2. Creer un environnement virtuel](#2-creer-un-environnement-virtuel)
    - [3. Installer les dependances](#3-installer-les-dependances)
    - [4. Appliquer les migrations](#4-appliquer-les-migrations)
    - [5. Lancer le serveur](#5-lancer-le-serveur)
  - [Configuration](#configuration)
  - [API HTTP](#api-http)
    - [`GET /api/notes/?room_id=<id>`](#get-apinotesroom_idid)
    - [`POST /api/notes/`](#post-apinotes)
  - [WebSockets](#websockets)
  - [Structure du projet](#structure-du-projet)
  - [Securite et bonnes pratiques](#securite-et-bonnes-pratiques)

## Apercu

Mem2gether est une plateforme de travail/groupe orientee synchronisation:

- un createur ouvre une room et partage son code
- les participants rejoignent la session en direct
- les contenus et interactions sont diffuses en temps reel (chat, photos, video, reactions)

## Fonctionnalites

- Authentification utilisateur (signup, signin, logout, profil, suppression de compte)
- Creation et participation a des rooms privees via un identifiant court
- Chat temps reel par room
- Mode `Photos`: upload d'images, file d'attente et image courante synchronisee
- Mode `YouTube`: synchronisation lecture/pause/seek et changement de video depuis URL/ID
- Notes de cours associees a un timecode (API + interface room)
- Reactions emoji en temps reel
- API HTTP pour lire/ajouter des notes

## Stack technique

- Python 3.x
- Django 4.x
- Django Channels (WebSocket)
- SQLite (par defaut)
- HTML/CSS/JS (templates Django)

## Demarrage rapide

### 1. Cloner le depot

```bash
git clone https://github.com/SyphaxMEDJBER/Mem2gether.git
cd Mem2gether
```

### 2. Creer un environnement virtuel

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

### 3. Installer les dependances

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
- `/ws/photos/<room_id>/` : synchronisation photos
- `/ws/youtube/<room_id>/` : synchronisation YouTube
- `/ws/reactions/<room_id>/` : reactions emoji

## Structure du projet

```text
application/        # Configuration Django (settings, urls, asgi, routing)
authentification/   # Inscription, connexion, profil
rooms/              # Metier principal: rooms, chat, photos, YouTube, notes, WS
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
