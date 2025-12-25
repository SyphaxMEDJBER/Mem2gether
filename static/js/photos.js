document.addEventListener("DOMContentLoaded", () => {
  const roomId = window.MEM2GETHER?.roomId;
  const uploadUrl = window.MEM2GETHER?.uploadUrl;

  const imgEl = document.getElementById("current-photo");
  const noPhotoEl = document.getElementById("no-photo");
  const queueEl = document.getElementById("queue-list");

  const btnPrev = document.getElementById("btn-prev");
  const btnNext = document.getElementById("btn-next");

  const form = document.getElementById("upload-form");
  const input = document.getElementById("image-input");
  const statusEl = document.getElementById("upload-status");

  function getCSRFToken() {
    return document.querySelector("input[name='csrfmiddlewaretoken']")?.value || "";
  }

  function renderState(state) {
    const queue = state.queue || [];
    const current = state.current || null;

    if (current && current.url) {
      imgEl.src = current.url;
      imgEl.style.display = "block";
      noPhotoEl.style.display = "none";
    } else {
      imgEl.style.display = "none";
      noPhotoEl.style.display = "block";
    }

    if (!queue.length) {
      queueEl.innerHTML = `<div class="queue-item"><p class="fw-semibold">Aucun média</p></div>`;
      return;
    }

    queueEl.innerHTML = queue.map(i => `
      <div class="queue-item" data-id="${i.id}" ${i.is_displayed ? "style='outline:2px solid #7c3aed'" : ""}>
        <img src="${i.url}">
        <div>
          <div class="fw-semibold">#${i.position}</div>
          <div class="text-muted small">par ${i.uploaded_by}</div>
        </div>
      </div>
    `).join("");

    document.querySelectorAll(".queue-item[data-id]").forEach(el => {
      el.onclick = () => {
        photosSocket.send(JSON.stringify({
          action: "set_current",
          image_id: Number(el.dataset.id)
        }));
      };
    });
  }

  /* ========= WEBSOCKET PHOTOS ========= */
  const photosSocket = new WebSocket(
    (location.protocol === "https:" ? "wss://" : "ws://") +
    location.host + "/ws/photos/" + roomId + "/"
  );

  photosSocket.onmessage = e => {
    const data = JSON.parse(e.data);
    if (data.type === "photos_state") renderState(data);
  };

  btnPrev.onclick = () => photosSocket.send(JSON.stringify({ action: "prev" }));
  btnNext.onclick = () => photosSocket.send(JSON.stringify({ action: "next" }));

  /* ========= UPLOAD (FIX CSRF + COOKIES) ========= */
  form.addEventListener("submit", async e => {
    e.preventDefault();

    if (!input.files.length) return;

    const fd = new FormData();
    fd.append("image", input.files[0]);

    statusEl.textContent = "Upload…";

    try {
      const res = await fetch(uploadUrl, {
        method: "POST",
        body: fd,
        credentials: "same-origin",   // 🔥 FIX CRITIQUE
        headers: {
          "X-CSRFToken": getCSRFToken()
        }
      });

      const json = await res.json();
      if (!json.ok) {
        statusEl.textContent = json.error || "Erreur upload";
        return;
      }

      input.value = "";
      statusEl.textContent = "Ajoutée ✅";
      setTimeout(() => statusEl.textContent = "", 1200);

    } catch {
      statusEl.textContent = "Erreur réseau";
    }
  });
});
