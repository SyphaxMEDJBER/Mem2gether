"""API JSON pour les notes de cours.

Cette API est separee des vues HTML afin que le JavaScript de la room puisse
lire et creer des notes sans recharger la page.
"""

import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from authentification.models import UserProfile
from .models import CourseNote, Room


def _parse_payload(request):
    """Accepte un body JSON ou un formulaire POST classique."""
    # Le front peut envoyer du JSON.
    if request.content_type and "application/json" in request.content_type:
        try:
            return json.loads(request.body.decode("utf-8") or "{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    # Sinon on lit les champs d'un formulaire classique.
    return request.POST


def _is_teacher(user):
    """Retourne True si l'utilisateur a le role professeur."""
    # Le role est stocke dans le profil utilisateur.
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile.is_teacher


@login_required
@require_http_methods(["GET", "POST"])
def course_notes_api(request):
    """Liste ou cree les notes personnelles de l'utilisateur connecte."""
    if request.method == "POST":
        # Les notes sont reservees aux etudiants.
        if _is_teacher(request.user):
            return JsonResponse({"error": "teachers_cannot_create_notes"}, status=403)

        # On recupere et valide les donnees envoyees.
        payload = _parse_payload(request)
        if payload is None:
            return JsonResponse({"error": "invalid_json"}, status=400)

        room_id = str(payload.get("room_id", "")).strip()
        content = str(payload.get("content", "")).strip()
        raw_timecode = payload.get("timecode")

        if not room_id:
            return JsonResponse({"error": "missing_room_id"}, status=400)
        if not content:
            return JsonResponse({"error": "missing_content"}, status=400)

        # Le timecode doit etre un nombre positif.
        try:
            timecode = int(float(raw_timecode))
            if timecode < 0:
                raise ValueError
        except (TypeError, ValueError):
            return JsonResponse({"error": "invalid_timecode"}, status=400)

        try:
            room = Room.objects.get(room_id=room_id)
        except Room.DoesNotExist:
            return JsonResponse({"error": "room_not_found"}, status=404)

        # Creation de la note personnelle.
        note = CourseNote.objects.create(
            user=request.user,
            room=room,
            content=content,
            timecode=timecode,
        )

        return JsonResponse(
            {
                "id": note.id,
                "room_id": note.room.room_id,
                "user": note.user.username,
                "content": note.content,
                "timecode": note.timecode,
                "created_at": note.created_at.isoformat(),
            },
            status=201,
        )

    # En GET, on renvoie les notes de l'utilisateur connecte.
    room_id = request.GET.get("room_id", "").strip()
    if not room_id:
        return JsonResponse({"error": "missing_room_id"}, status=400)

    # Un professeur ne voit pas les notes personnelles des etudiants.
    notes = CourseNote.objects.none()
    if not _is_teacher(request.user):
        notes = (
            CourseNote.objects.filter(room__room_id=room_id, user=request.user)
            .select_related("user")
            .order_by("timecode", "created_at")
        )

    return JsonResponse(
        {
            "room_id": room_id,
            "notes": [
                {
                    "id": note.id,
                    "user": note.user.username,
                    "content": note.content,
                    "timecode": note.timecode,
                    "created_at": note.created_at.isoformat(),
                }
                for note in notes
            ],
        }
    )
