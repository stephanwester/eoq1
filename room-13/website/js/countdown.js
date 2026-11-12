// Countdown to The Opening: Friday 13 November 2026, 15:00 Dutch time (UTC+1).
const OPENING = Date.UTC(2026, 10, 13, 14, 0, 0);
const AFTER = Date.UTC(2026, 10, 13, 23, 0, 0);
const out = document.getElementById("countdown");
const pad = n => String(n).padStart(2, "0");
function tick() {
  const now = Date.now();
  if (now >= AFTER) { out.textContent = "ROOM 13 IS CLOSED. FOR NOW."; return; }
  if (now >= OPENING) { out.textContent = "ROOM 13 IS OPEN."; return; }
  let s = Math.floor((OPENING - now) / 1000);
  const d = Math.floor(s / 86400); s %= 86400;
  const h = Math.floor(s / 3600); s %= 3600;
  const m = Math.floor(s / 60); s %= 60;
  out.textContent = `ROOM 13 OPENS IN ${d}D ${pad(h)}:${pad(m)}:${pad(s)}`;
}
tick();
setInterval(tick, 1000);
