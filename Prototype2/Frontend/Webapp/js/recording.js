export function createRecorder(controller) {
  const {
    btnStart,
    btnStop,
    btnRetake,
    btnSubmit,
    recStatus,
    recProgress,
    timeLimitEl,
    audioPreview
  } = controller;

  let mediaRecorder = null;
  let chunks = [];
  let audioBlob = null;
  let audioUrl = null;
  let recordTimer = null;
  let recordStartMs = 0;

  function setStatus(text, badgeClass) {
    recStatus.textContent = text;
    recStatus.className = `badge ${badgeClass}`;
  }

  function setProgress(percent) {
    recProgress.style.width = `${percent}%`;
  }

  function resetPreview() {
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    audioBlob = null;
    audioUrl = null;
    audioPreview.removeAttribute("src");
    audioPreview.load();
    btnRetake.disabled = true;
    btnSubmit.disabled = true;
  }

  async function startRecording() {
    resetPreview();
    chunks = [];

    const limitSec = Math.max(3, Math.min(30, Number(timeLimitEl.value) || 8));
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) chunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
      stream.getTracks().forEach((track) => track.stop());
      audioBlob = new Blob(chunks, { type: "audio/webm" });
      audioUrl = URL.createObjectURL(audioBlob);
      audioPreview.src = audioUrl;

      btnRetake.disabled = false;
      btnSubmit.disabled = false;

      setStatus("Recorded", "text-bg-success");
      setProgress(100);
    };

    mediaRecorder.start();
    recordStartMs = Date.now();
    setStatus("Recording", "text-bg-danger");
    setProgress(0);

    btnStart.disabled = true;
    btnStop.disabled = false;

    recordTimer = setInterval(() => {
      const elapsed = (Date.now() - recordStartMs) / 1000;
      const pct = Math.min(100, (elapsed / limitSec) * 100);
      setProgress(pct);
      if (elapsed >= limitSec) stopRecording();
    }, 100);
  }

  function stopRecording() {
    if (!mediaRecorder) return;
    if (recordTimer) clearInterval(recordTimer);
    recordTimer = null;

    if (mediaRecorder.state !== "inactive") mediaRecorder.stop();

    btnStart.disabled = false;
    btnStop.disabled = true;
    setStatus("Processing", "text-bg-warning");
  }

  btnStart.addEventListener("click", async () => {
    try {
      await startRecording();
    } catch (error) {
      setStatus("Mic blocked", "text-bg-danger");
      alert("Microphone permission is required to record.");
    }
  });

  btnStop.addEventListener("click", stopRecording);

  btnRetake.addEventListener("click", () => {
    resetPreview();
    setStatus("Idle", "text-bg-secondary");
    setProgress(0);
  });

  setStatus("Idle", "text-bg-secondary");
  setProgress(0);

  return {
    getAudio: () => ({ blob: audioBlob, url: audioUrl })
  };
}
