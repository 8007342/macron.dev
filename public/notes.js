// Renders the notebook from /notes/manifest.jsonl: one JSON object per line,
// appended by each contributor (see README "The notebook"). Malformed or
// duplicate lines are skipped, so a union merge never breaks the page. Note
// bodies are shown as plain text, never as HTML.
(async () => {
  const list = document.getElementById('notes-list');
  if (!list) return;
  let text;
  try {
    const response = await fetch('/notes/manifest.jsonl', { cache: 'no-cache' });
    if (!response.ok) throw new Error(String(response.status));
    text = await response.text();
  } catch {
    list.textContent = 'The notebook could not be loaded right now.';
    return;
  }
  const NAME = /^(\d{4}-\d{2}-\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$/;
  const notes = new Map();
  for (const line of text.split('\n')) {
    let entry;
    try { entry = JSON.parse(line); } catch { continue; }
    if (!entry || typeof entry.title !== 'string' || typeof entry.file !== 'string') continue;
    const match = NAME.exec(entry.file);
    if (!match || notes.has(entry.file)) continue;
    notes.set(entry.file, { ...entry, date: match[1] });
  }
  list.textContent = '';
  if (notes.size === 0) { list.textContent = 'No notes yet.'; return; }
  for (const note of [...notes.values()].sort((a, b) => b.file.localeCompare(a.file))) {
    const item = document.createElement('details');
    item.className = 'note';
    const summary = document.createElement('summary');
    const title = document.createElement('span');
    title.textContent = note.title;
    const meta = document.createElement('span');
    meta.className = 'note-meta';
    meta.textContent = typeof note.host === 'string' ? `${note.date} · ${note.host}` : note.date;
    summary.append(title, meta);
    const body = document.createElement('div');
    body.className = 'note-body';
    item.append(summary, body);
    item.addEventListener('toggle', async () => {
      if (!item.open || body.dataset.loaded) return;
      body.dataset.loaded = '1';
      try {
        const response = await fetch(`/notes/${note.file}`);
        if (!response.ok) throw new Error(String(response.status));
        body.textContent = await response.text();
      } catch {
        body.textContent = 'This note could not be loaded.';
        delete body.dataset.loaded;
      }
    });
    list.append(item);
  }
})();
