# Documentation projet Mem2gether

## Objectif

Mem2gether est une application Django de session collaborative. Un professeur
cree une room, des etudiants la rejoignent, puis tout le monde partage un meme
espace avec chat, video YouTube synchronisee, tableau blanc et notes de cours.

## Architecture generale

```text
application/        Configuration Django, URLs globales, ASGI et WebSocket
authentification/   Comptes utilisateurs, roles professeur/etudiant, profil
rooms/              Coeur metier: rooms, participants, chat, YouTube, notes
templates/          Pages HTML Django
static/             CSS, JavaScript et assets statiques
media/              Fichiers uploades ou servis localement
docs/               Documentation projet
```

L'application utilise deux types de communication:

- HTTP classique pour les pages, formulaires, APIs AJAX et polling.
- WebSocket Channels pour les evenements temps reel quand le client les utilise.

## Roles

Les roles sont stockes dans `authentification.models.UserProfile`.

- `teacher`: peut creer une room et piloter la video/le tableau blanc.
- `student`: peut rejoindre une room, suivre la synchronisation et creer ses
  notes personnelles.

Le profil est cree automatiquement avec un signal `post_save` quand un
utilisateur Django est cree.

## Modele de donnees principal

### `Room`

Une room represente une session collaborative.

Champs importants:

- `room_id`: identifiant court partage aux participants.
- `creator`: professeur createur de la room.
- `youtube_video_id`: ID de la video YouTube active.
- `youtube_state`: etat de lecture, par exemple `playing` ou `paused`.
- `youtube_time`: position connue de la video en secondes.
- `youtube_updated_at`: date du dernier changement video.
- `whiteboard_data`: image PNG du tableau blanc encodee en data URL.
- `whiteboard_updated_at`: date du dernier changement du tableau blanc.

### `Participant`

Associe un utilisateur a une room. Sert a afficher la presence dans
l'interface.

### `Message`

Message de chat rattache a une room.

### `CourseNote`

Note personnelle d'un etudiant, rattachee a une room et a un timecode video.

## Flux de room

1. Le professeur clique sur creation de room.
2. `rooms.views.create_room` genere un `room_id` et cree une `Room`.
3. Les participants entrent ce code via `join_room`.
4. `room_view` ajoute l'utilisateur dans `Participant`.
5. La page `templates/rooms/room.html` charge les donnees de synchronisation
   avec des appels AJAX.

## Synchronisation YouTube

L'etat video est persiste dans la table `Room`.

Endpoints principaux:

- `GET /rooms/<room_id>/sync-state/`
  renvoie l'etat courant de la video.
- `POST /rooms/<room_id>/sync-state/`
  accepte les commandes du professeur uniquement.

Types d'evenements acceptes:

- `set_video`: change la video.
- `play`: lance la lecture.
- `pause`: met en pause.
- `seek`: change la position.
- `sync`: force un recalage complet.
- `heartbeat`: met a jour la position pendant la lecture.

Quand la video est en lecture, le serveur recalcule la position actuelle en
ajoutant le temps ecoule depuis `youtube_updated_at`. Cela evite de renvoyer un
temps trop ancien aux etudiants.

## Synchronisation du tableau blanc

Le tableau blanc est un canvas HTML dans `templates/rooms/room.html`.

Le principe est simple:

1. Le professeur dessine sur le canvas.
2. Le navigateur transforme le canvas en image PNG avec `toDataURL`.
3. L'image est envoyee au serveur avec `POST /rooms/<room_id>/whiteboard-state/`.
4. Le serveur stocke l'image dans `Room.whiteboard_data`.
5. Les etudiants appellent regulierement `GET /rooms/<room_id>/whiteboard-state/`.
6. Le navigateur des etudiants redessine l'image recue dans leur canvas.

Ce flux est donc une synchronisation par snapshot et polling HTTP, pas un
WebSocket dedie au tableau blanc.

## Chat et participants

Le chat peut passer par:

- `rooms.consumers.ChatConsumer` pour le WebSocket.
- `rooms.views.room_messages_state` pour le fallback AJAX.

Les participants sont serialises par `_serialize_participants`, puis diffuses
aux clients par `_broadcast_participants`.

Quand le createur quitte une room, `leave_room` supprime la room et diffuse un
evenement `room_closed` pour rediriger les clients.

## Notes de cours

API principale:

- `GET /api/notes/?room_id=<id>`: liste les notes de l'etudiant connecte.
- `POST /api/notes/`: cree une note personnelle.

Payload POST:

```json
{
  "room_id": "abcd1234",
  "content": "Definition importante",
  "timecode": 95
}
```

Les professeurs ne creent pas de notes via cette API. Les notes sont
personnelles: un etudiant ne voit que ses propres notes.

## WebSockets

Routes declarees dans `rooms/routing.py`:

- `/ws/rooms/<room_id>/`: chat, participants et fermeture de room.
- `/ws/youtube/<room_id>/`: synchronisation video.

Le point d'entree ASGI est `application/asgi.py`. Il combine:

- `get_asgi_application()` pour HTTP.
- `AuthMiddlewareStack` et `URLRouter` pour les WebSockets authentifies.

## Tests

Les tests sont dans `rooms/tests_*.py` et `authentification/tests.py`.

Commandes utiles:

```powershell
python manage.py test
```

ou pour cibler une app:

```powershell
python manage.py test rooms
python manage.py test authentification
```

## Points de vigilance avant production

- Deplacer `SECRET_KEY` et les identifiants SMTP dans des variables
  d'environnement.
- Remplacer `InMemoryChannelLayer` par Redis avec `channels_redis`.
- Configurer `ALLOWED_HOSTS`.
- Desactiver `DEBUG`.
- Servir les medias et statiques avec une configuration adaptee.
- Verifier la taille de `whiteboard_data`, car stocker des images base64 en base
  peut devenir lourd.
