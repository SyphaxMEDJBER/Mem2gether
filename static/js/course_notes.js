function getCsrfToken() {
  const cookie = document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="));
  return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
}

async function addNote(timecode, content, roomId) {
  const response = await fetch("/api/notes/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
    credentials: "same-origin",
    body: JSON.stringify({
      room_id: roomId,
      timecode: Number(timecode),
      content: content,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error || "Failed to create note");
  }

  return response.json();
}

async function fetchNotes(roomId) {
  const response = await fetch(`/api/notes/?room_id=${encodeURIComponent(roomId)}`, {
    method: "GET",
    credentials: "same-origin",
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error || "Failed to fetch notes");
  }

  const data = await response.json();
  return data.notes || [];
}

window.CourseNotesAPI = {
  addNote,
  fetchNotes,
};
