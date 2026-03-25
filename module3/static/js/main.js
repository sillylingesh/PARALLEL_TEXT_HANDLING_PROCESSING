/* ═══════════════════════════════════════════════════════════
   main.js  —  Parallel Text Processor
   ═══════════════════════════════════════════════════════════ */

/* ── Tab navigation ────────────────────────────────────────── */
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(btn.dataset.tab).classList.add('active');
  });
});

/* ── Toast notifications ────────────────────────────────────── */
function toast(msg, type = 'info') {
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  document.getElementById('toast-container').appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

/* ── Polling state ─────────────────────────────────────────── */
let _pollTimer = null;

function startPolling() {
  if (_pollTimer) return;
  _pollTimer = setInterval(pollProgress, 600);
}

function stopPolling() {
  clearInterval(_pollTimer);
  _pollTimer = null;
}

async function pollProgress() {
  try {
    const data = await apiFetch('/api/progress');
    const pct = data.pct || 0;

    // Progress bar
    document.getElementById('progress-bar').style.width = pct + '%';
    document.getElementById('progress-text').textContent =
      `${data.done} / ${data.total} chunks  (${pct.toFixed(1)}%)`;

    // Log
    const logEl = document.getElementById('log-box');
    logEl.textContent = data.log.join('\n');
    logEl.scrollTop = logEl.scrollHeight;

    // Timer
    document.getElementById('timer-text').textContent = (data.duration || 0).toFixed(1) + 's';

    // Status badge
    updateStatus(data);

    if (!data.running) {
      stopPolling();
      if (data.done > 0) {
        toast(`✅ Processed ${data.done} chunks in ${data.duration}s — batch ${data.batch_id}`, 'success');
        refreshResults();
        refreshCharts();
        // Switch to results tab
        setTimeout(() => {
          document.querySelector('[data-tab="tab-results"]').click();
        }, 400);
      }
      if (data.error) toast('⚠ ' + data.error, 'error');
    }
  } catch (e) { /* silent */ }
}

function updateStatus(data) {
  const badge = document.getElementById('status-badge');
  const dot   = badge.querySelector('.status-dot');
  const label = badge.querySelector('.status-label');
  badge.className = 'status-badge';

  if (data.running) {
    badge.classList.add('running');
    label.textContent = 'Processing…';
  } else if (data.done > 0 && !data.error) {
    badge.classList.add('done');
    label.textContent = 'Complete ✓';
  } else if (data.error) {
    badge.classList.add('stopped');
    label.textContent = 'Error';
  } else {
    badge.classList.add('ready');
    label.textContent = 'Ready';
  }
}

/* ── API helper ────────────────────────────────────────────── */
async function apiFetch(url, opts = {}) {
  const res = await fetch(url, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: 'Network error' }));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json();
}

/* ═══════════════════════════════════════════════════════════
   INPUT TAB
   ═══════════════════════════════════════════════════════════ */

// Char count
const textArea = document.getElementById('text-input');
const charCount = document.getElementById('char-count');
textArea.addEventListener('input', () => {
  const n = textArea.value.trim().length;
  charCount.textContent = n.toLocaleString() + ' characters';
});

// Load file
document.getElementById('btn-load-file').addEventListener('click', () => {
  document.getElementById('file-input').click();
});
document.getElementById('file-input').addEventListener('change', async e => {
  const files = Array.from(e.target.files);
  if (!files.length) return;

  const listEl = document.getElementById('file-list');
  listEl.innerHTML = '';
  files.forEach(f => {
    const li = document.createElement('li');
    li.textContent = f.name;
    listEl.appendChild(li);
  });

  toast(`Extracting text from ${files.length} file(s)...`, 'info');
  
  const formData = new FormData();
  files.forEach(f => formData.append('files', f));

  try {
    const res = await fetch('/api/extract', {
      method: 'POST',
      body: formData
    });
    if (!res.ok) throw new Error('Extraction failed');
    const data = await res.json();
    
    textArea.value = data.text;
    textArea.dispatchEvent(new Event('input'));
    toast(`Successfully loaded ${files.length} file(s)`, 'success');
  } catch (err) {
    toast(`Error: ${err.message}`, 'error');
  }
  
  e.target.value = '';
});

// Clear text
document.getElementById('btn-clear-text').addEventListener('click', () => {
  textArea.value = '';
  document.getElementById('file-list').innerHTML = '';
  textArea.dispatchEvent(new Event('input'));
});

// Start processing
document.getElementById('btn-start').addEventListener('click', async () => {
  const text = textArea.value.trim();
  if (!text) { toast('Please enter or load some text first.', 'error'); return; }

  const method  = document.querySelector('input[name="method"]:checked').value;
  const workers = parseInt(document.querySelector('input[name="workers"]:checked').value);

  try {
    await apiFetch('/api/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, method, workers }),
    });
    document.getElementById('progress-bar').style.width = '0%';
    document.getElementById('progress-text').textContent = '0 / 0 chunks';
    document.getElementById('timer-text').textContent = '0.0s';
    startPolling();
    toast('Processing started…', 'info');
  } catch (e) {
    toast(e.message, 'error');
  }
});

// Stop
document.getElementById('btn-stop').addEventListener('click', async () => {
  await apiFetch('/api/stop', { method: 'POST' }).catch(() => {});
  stopPolling();
  const badge = document.getElementById('status-badge');
  badge.className = 'status-badge stopped';
  badge.querySelector('.status-label').textContent = 'Stopped';
  toast('Processing stopped.', 'error');
});

/* ═══════════════════════════════════════════════════════════
   RESULTS TAB
   ═══════════════════════════════════════════════════════════ */

async function refreshResults() {
  try {
    const data = await apiFetch('/api/results');
    renderStats(data.stats);
    renderTable('results-table', data.rows);
    document.getElementById('results-count').textContent =
      data.rows.length.toLocaleString() + ' records';
  } catch (e) {
    toast('Failed to load results: ' + e.message, 'error');
  }
}

function renderStats(stats) {
  if (!stats) {
    ['stat-total','stat-avg','stat-pos','stat-neg','stat-neu'].forEach(id => {
      document.getElementById(id).textContent = '—';
    });
    return;
  }
  document.getElementById('stat-total').textContent = stats.total.toLocaleString();
  document.getElementById('stat-avg').textContent   = (stats.avg_score >= 0 ? '+' : '') + stats.avg_score;
  document.getElementById('stat-pos').textContent   = stats.positive_words.toLocaleString();
  document.getElementById('stat-neg').textContent   = stats.negative_words.toLocaleString();
  document.getElementById('stat-neu').textContent   = stats.neutral_words.toLocaleString();
}

function renderTable(tableId, rows) {
  const tbody = document.querySelector(`#${tableId} tbody`);
  
  if (!rows.length) {
    tbody.innerHTML = `<tr><td colspan="9">
      <div class="empty-state">
        <div class="icon">🗂</div>
        <p>No records yet — process some text first.</p>
      </div></td></tr>`;
    return;
  }

  let html = '';
  rows.forEach(r => {
    const scoreClass = r.sentiment_score > 0 ? 'score-pos' :
                       r.sentiment_score < 0 ? 'score-neg' : 'score-neu';
    const preview = r.chunk_text.length > 70
      ? r.chunk_text.slice(0, 70) + '…'
      : r.chunk_text;
    const ts = r.timestamp ? r.timestamp.slice(0, 19) : '';

    html += `
      <tr>
        <td>${r.id}</td>
        <td class="chunk-preview" title="${escHtml(r.chunk_text)}">${escHtml(preview)}</td>
        <td class="${scoreClass}">${r.sentiment_score >= 0 ? '+' : ''}${r.sentiment_score}</td>
        <td><span class="badge-label badge-${r.sentiment_label}">${r.sentiment_label}</span></td>
        <td>${r.positive_count}</td>
        <td>${r.negative_count}</td>
        <td>${r.neutral_count}</td>
        <td>${r.word_count}</td>
        <td style="color:var(--muted);font-size:.7rem">${ts}</td>
      </tr>`;
  });
  tbody.innerHTML = html;
}

function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

document.getElementById('btn-refresh-results').addEventListener('click', refreshResults);

document.getElementById('btn-clear-db').addEventListener('click', async () => {
  if (!confirm('Delete ALL records from the database? This cannot be undone.')) return;
  await apiFetch('/api/clear', { method: 'POST' });
  toast('Database cleared.', 'info');
  refreshResults();
  refreshCharts();
});

/* ═══════════════════════════════════════════════════════════
   SEARCH TAB
   ═══════════════════════════════════════════════════════════ */

document.getElementById('btn-search').addEventListener('click', runSearch);
document.getElementById('search-keyword').addEventListener('keyup', e => {
  if (e.key === 'Enter') runSearch();
});

async function runSearch() {
  const kw    = document.getElementById('search-keyword').value.trim();
  const minSc = document.getElementById('search-min').value;
  const maxSc = document.getElementById('search-max').value;
  const label = document.getElementById('search-label').value;

  let url = `/api/results?limit=500&label=${encodeURIComponent(label)}`;
  if (kw)    url += `&keyword=${encodeURIComponent(kw)}`;
  if (minSc) url += `&min_score=${minSc}`;
  if (maxSc) url += `&max_score=${maxSc}`;

  try {
    const data = await apiFetch(url);
    renderTable('search-table', data.rows);
    document.getElementById('search-count').textContent =
      `${data.rows.length.toLocaleString()} result(s) found`;
  } catch (e) {
    toast('Search failed: ' + e.message, 'error');
  }
}

document.getElementById('btn-reset-search').addEventListener('click', () => {
  document.getElementById('search-keyword').value = '';
  document.getElementById('search-min').value     = '';
  document.getElementById('search-max').value     = '';
  document.getElementById('search-label').value   = 'All';
  document.querySelector('#search-table tbody').innerHTML = '';
  document.getElementById('search-count').textContent = '';
});

/* ═══════════════════════════════════════════════════════════
   VISUALIZE TAB — Chart.js
   ═══════════════════════════════════════════════════════════ */

let _charts = {};
const PAL = { 
  pos: '#10b981', // Emerald-500
  neg: '#ef4444', // Red-500
  neu: '#f59e0b', // Amber-500
  acc: '#4f46e5'  // Indigo-600
};

async function refreshCharts(existingData = null) {
  try {
    const data = existingData || await apiFetch('/api/results');
    const stats  = data.stats;
    const scores = data.scores;

    if (!stats) {
      document.getElementById('chart-empty').style.display = 'block';
      return;
    }
    document.getElementById('chart-empty').style.display = 'none';

    const chartDefaults = {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { labels: { color: '#374151', font: { family: 'Inter', size: 11 } } },
        tooltip: {
          backgroundColor: '#ffffff',
          borderColor: '#e5e7eb',
          borderWidth: 1,
          titleColor: '#111827',
          bodyColor: '#374151',
          padding: 10,
          cornerRadius: 6,
          displayColors: true
        }
      }
    };

    // ── Chart 1: Sentiment Chunk Count (Bar) ──────────────────
    buildChart('chart-bar', 'bar', {
      labels: ['Positive', 'Negative', 'Neutral'],
      datasets: [{
        label: 'Chunks',
        data: [stats.positive_chunks, stats.negative_chunks, stats.neutral_chunks],
        backgroundColor: [PAL.pos + '99', PAL.neg + '99', PAL.neu + '99'],
        borderColor:     [PAL.pos, PAL.neg, PAL.neu],
        borderWidth: 1.5,
        borderRadius: 6,
      }]
    }, {
      ...chartDefaults,
      plugins: { ...chartDefaults.plugins, legend: { display: false } },
      scales: {
        x: { ticks: { color: '#6b7280' }, grid: { color: '#f3f4f6' } },
        y: { ticks: { color: '#6b7280' }, grid: { color: '#f3f4f6' }, beginAtZero: true }
      }
    });

    // ── Chart 2: Word Distribution (Doughnut) ─────────────────
    buildChart('chart-doughnut', 'doughnut', {
      labels: ['Positive', 'Negative', 'Neutral'],
      datasets: [{
        data: [stats.positive_words, stats.negative_words, stats.neutral_words],
        backgroundColor: [PAL.pos + 'cc', PAL.neg + 'cc', PAL.neu + 'cc'],
        borderColor: '#131325',
        borderWidth: 3,
        hoverOffset: 8,
      }]
    }, {
      ...chartDefaults,
      cutout: '65%',
    });

    // ── Chart 3: Score Histogram ──────────────────────────────
    if (scores.length) {
      const min = Math.min(...scores), max = Math.max(...scores);
      const bins = buildHistogram(scores, min, max, 15);
      buildChart('chart-hist', 'bar', {
        labels: bins.labels,
        datasets: [{
          label: 'Frequency',
          data: bins.counts,
          backgroundColor: bins.colors,
          borderColor: '#131325',
          borderWidth: 1,
          borderRadius: 4,
        }]
      }, {
        ...chartDefaults,
        plugins: { ...chartDefaults.plugins, legend: { display: false } },
        scales: {
          x: { ticks: { color: '#6b7280', font:{size:10} }, grid: { color: '#f3f4f6' } },
          y: { ticks: { color: '#6b7280' }, grid: { color: '#f3f4f6' }, beginAtZero: true }
        }
      });
    }

    // ── Chart 4: Avg Score Gauge (Horizontal Bar) ─────────────
    const avg = stats.avg_score;
    buildChart('chart-gauge', 'bar', {
      labels: ['Score'],
      datasets: [
        {
          label: 'Average Sentiment Score',
          data: [Math.abs(avg)],
          backgroundColor: avg > 0 ? PAL.pos + 'cc' : avg < 0 ? PAL.neg + 'cc' : PAL.neu + 'cc',
          borderColor:     avg > 0 ? PAL.pos : avg < 0 ? PAL.neg : PAL.neu,
          borderWidth: 2,
          borderRadius: 6,
        }
      ]
    }, {
      ...chartDefaults,
      indexAxis: 'y',
      plugins: {
        ...chartDefaults.plugins,
        legend: { display: false },
        title: {
          display: true,
          text: `Average Score: ${avg >= 0 ? '+' : ''}${avg}`,
          color: avg > 0 ? PAL.pos : avg < 0 ? PAL.neg : PAL.neu,
          font: { family: 'Oxanium', size: 13, weight: '700' },
          padding: { bottom: 10 }
        }
      },
      scales: {
        x: { ticks: { color: '#6b7280' }, grid: { color: '#f3f4f6' }, beginAtZero: true },
        y: { ticks: { display: false }, grid: { display: false } }
      }
    });
  } catch (e) {
    toast('Chart error: ' + e.message, 'error');
  }
}

function buildChart(id, type, chartData, options) {
  if (_charts[id]) { _charts[id].destroy(); }
  const ctx = document.getElementById(id).getContext('2d');
  _charts[id] = new Chart(ctx, { type, data: chartData, options });
}

function buildHistogram(values, min, max, numBins) {
  const range = max - min || 1;
  const size  = range / numBins;
  const counts = new Array(numBins).fill(0);
  const labels  = [];

  for (let i = 0; i < numBins; i++) {
    const lo = +(min + i * size).toFixed(1);
    const hi = +(min + (i + 1) * size).toFixed(1);
    labels.push(lo === hi ? `${lo}` : `${lo}`);
  }
  values.forEach(v => {
    const idx = Math.min(Math.floor((v - min) / size), numBins - 1);
    counts[idx]++;
  });
  const colors = counts.map((_, i) => {
    const mid = min + (i + .5) * size;
    return mid > 0 ? PAL.pos + '99' : mid < 0 ? PAL.neg + '99' : PAL.neu + '99';
  });
  return { labels, counts, colors };
}

document.getElementById('btn-refresh-charts').addEventListener('click', refreshCharts);

/* ═══════════════════════════════════════════════════════════
   EXPORT TAB
   ═══════════════════════════════════════════════════════════ */

document.getElementById('btn-export').addEventListener('click', async () => {
  const filter = document.querySelector('input[name="exp-filter"]:checked').value;
  const labelMap = {
    'All Results': 'All', 'Positive Only': 'Positive',
    'Negative Only': 'Negative', 'Neutral Only': 'Neutral'
  };
  const label = labelMap[filter] || 'All';

  try {
    // Fetch preview first
    const data = await apiFetch(`/api/results?label=${label}`);
    if (!data.rows.length) { toast('No data for selected filter.', 'error'); return; }

    // Show preview
    const headers = ['id','chunk_text','sentiment_score','sentiment_label',
                     'positive_count','negative_count','neutral_count','word_count','timestamp'];
    let preview = headers.join(',') + '\n';
    data.rows.slice(0, 25).forEach(r => {
      preview += headers.map(h => {
        const v = r[h];
        return typeof v === 'string' && v.includes(',') ? `"${v.replace(/"/g,'""')}"` : v;
      }).join(',') + '\n';
    });
    if (data.rows.length > 25) preview += `… ${data.rows.length - 25} more rows …\n`;
    document.getElementById('export-preview').textContent = preview;

    // Trigger download
    const a = document.createElement('a');
    a.href = `/api/export?label=${label}`;
    a.download = '';
    document.body.appendChild(a);
    a.click();
    a.remove();

    document.getElementById('export-status').textContent =
      `✅  Exported ${data.rows.length.toLocaleString()} rows`;
    document.getElementById('export-status').style.color = 'var(--pos)';
    toast(`Exported ${data.rows.length} rows.`, 'success');
  } catch (e) {
    toast('Export failed: ' + e.message, 'error');
  }
});

/* ═══════════════════════════════════════════════════════════
   INIT
   ═══════════════════════════════════════════════════════════ */
async function initApp() {
  try {
    const data = await apiFetch('/api/results');
    renderStats(data.stats);
    renderTable('results-table', data.rows);
    document.getElementById('results-count').textContent =
      data.rows.length.toLocaleString() + ' records';
    
    await refreshCharts(data);
  } catch (e) {
    console.error('Init error:', e);
  }
}

initApp();

