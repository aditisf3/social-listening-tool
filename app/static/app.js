"use strict";

const $ = (sel) => document.querySelector(sel);

let currentKeyword = "";

async function loadSources() {
  const list = $("#source-list");
  try {
    const res = await fetch("/api/sources");
    const sources = await res.json();
    list.innerHTML = "";
    for (const s of sources) {
      const wrap = document.createElement("div");
      wrap.className = "source-item";

      const cb = document.createElement("input");
      cb.type = "checkbox";
      cb.id = `src-${s.key}`;
      cb.value = s.key;
      cb.checked = s.key === "reddit"; // default selection per spec

      const label = document.createElement("label");
      label.htmlFor = cb.id;
      label.textContent = s.name;

      const badge = document.createElement("span");
      if (!s.requires_credentials) {
        badge.className = "badge ready";
        badge.textContent = "no key needed";
      } else if (s.configured) {
        badge.className = "badge ready";
        badge.textContent = "key set";
      } else {
        badge.className = "badge needs-key";
        badge.textContent = "needs key";
      }

      wrap.append(cb, label, badge);
      list.appendChild(wrap);
    }
  } catch (err) {
    list.textContent = "Failed to load sources.";
  }
}

function selectedSources() {
  return Array.from(
    document.querySelectorAll("#source-list input[type=checkbox]:checked")
  ).map((cb) => cb.value);
}

function setStatus(msg, isError = false) {
  const el = $("#status");
  el.textContent = msg;
  el.classList.toggle("error", isError);
}

async function runCollect(evt) {
  evt.preventDefault();
  const keyword = $("#keyword").value.trim();
  const limit = parseInt($("#limit").value, 10) || 25;
  const sources = selectedSources();

  if (!keyword) return setStatus("Enter a keyword.", true);
  if (sources.length === 0) return setStatus("Select at least one source.", true);

  currentKeyword = keyword;
  const btn = $("#search-btn");
  btn.disabled = true;
  setStatus(`Collecting "${keyword}" from ${sources.join(", ")}…`);

  try {
    const res = await fetch("/api/collect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ keyword, sources, limit }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Request failed");

    const parts = [];
    for (const [src, info] of Object.entries(data.sources)) {
      parts.push(info.error ? `${src}: error` : `${src}: ${info.fetched}`);
    }
    setStatus(
      `Fetched ${data.fetched_total}, stored ${data.new_stored} new. (${parts.join(", ")})`
    );

    const errors = Object.entries(data.sources)
      .filter(([, i]) => i.error)
      .map(([s, i]) => `${s}: ${i.error}`);
    if (errors.length) setStatus(`Some sources failed — ${errors.join(" | ")}`, true);

    await Promise.all([loadSummary(), loadResults()]);
  } catch (err) {
    setStatus(err.message, true);
  } finally {
    btn.disabled = false;
  }
}

async function loadSummary() {
  if (!currentKeyword) return;
  const res = await fetch(`/api/summary?keyword=${encodeURIComponent(currentKeyword)}`);
  const data = await res.json();
  $("#summary-panel").hidden = false;
  const bySource = Object.entries(data.by_source)
    .map(([k, v]) => `<div class="stat">${k}: <b>${v}</b></div>`)
    .join("") || "<div class='stat'>none</div>";
  const bySent = ["positive", "neutral", "negative"]
    .map((k) => `<div class="stat"><span class="sent ${k}">${k}</span> ${data.by_sentiment[k] || 0}</div>`)
    .join("");
  $("#summary").innerHTML = `
    <div class="summary-grid">
      <div class="block"><h3>Total</h3><div class="stat">${data.total}</div></div>
      <div class="block"><h3>By source</h3>${bySource}</div>
      <div class="block"><h3>By sentiment</h3>${bySent}</div>
    </div>`;
}

function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}

async function loadResults() {
  const sentiment = $("#filter-sentiment").value;
  const params = new URLSearchParams();
  if (currentKeyword) params.set("keyword", currentKeyword);
  if (sentiment) params.set("sentiment", sentiment);
  const res = await fetch(`/api/posts?${params.toString()}`);
  const posts = await res.json();
  const container = $("#results");
  if (!posts.length) {
    container.textContent = "No results.";
    return;
  }
  container.innerHTML = posts
    .map((p) => {
      const when = p.published_at || p.collected_at || "";
      const author = p.author ? `@${escapeHtml(p.author)}` : "unknown";
      const link = p.url
        ? `<a href="${escapeHtml(p.url)}" target="_blank" rel="noopener">open ↗</a>`
        : "";
      return `
        <div class="post">
          <div class="post-meta">
            <span class="src-tag">${escapeHtml(p.source)}</span>
            <span class="sent ${p.sentiment_label}">${p.sentiment_label} (${p.sentiment_score})</span>
            <span>${author}</span>
            <span>${escapeHtml(String(when))}</span>
            ${link}
          </div>
          <div class="post-content">${escapeHtml(p.content)}</div>
        </div>`;
    })
    .join("");
}

$("#search-form").addEventListener("submit", runCollect);
$("#refresh-btn").addEventListener("click", loadResults);
$("#filter-sentiment").addEventListener("change", loadResults);

loadSources();
