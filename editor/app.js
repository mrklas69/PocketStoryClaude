// PocketStory World Editor — app.js

// ── Schema: columns per tab ─────────────────────────────────────────────────
const ENTITY_COLS = [
  { key: "id",          label: "ID",          type: "text" },
  { key: "name",        label: "Název",        type: "text" },
  { key: "type",        label: "Typ",          type: "select",
    options: ["ENVI", "CHAR", "UNIQUE", "SUMS"] },
  { key: "description", label: "Popis",        type: "textarea" },
  { key: "hp",          label: "HP",           type: "number", optional: true },
  { key: "hp_max",      label: "HP max",       type: "number", optional: true },
  { key: "capacity",    label: "Kapacita",     type: "number", optional: true },
  { key: "rank",        label: "Rank",         type: "number", optional: true },
  { key: "control",     label: "Control",      type: "text",   optional: true },
];

const REL_COMMON = [
  { key: "id",    label: "ID",   type: "number" },
  { key: "ent1",  label: "Ent1", type: "text" },
  { key: "ent2",  label: "Ent2", type: "text" },
];

const REL_SCHEMAS = {
  LOCATION: [...REL_COMMON,
    { key: "number", label: "Počet", type: "number" },
    { key: "hp",     label: "HP",    type: "number", optional: true },
  ],
  SKILL: [...REL_COMMON,
    { key: "number", label: "Úroveň", type: "number" },
  ],
  TYPE_OF: [...REL_COMMON],
  BEHAVIOR: [...REL_COMMON,
    { key: "number", label: "Intenzita", type: "number" },
  ],
  EDGE: [...REL_COMMON,
    { key: "number",  label: "Vzdálenost", type: "number" },
    { key: "way",     label: "Způsob",     type: "text",     optional: true },
    { key: "one_way", label: "Jednosměrná",type: "checkbox", optional: true },
    { key: "deny",    label: "Deny (TYPE_OF)", type: "text", optional: true },
  ],
  PRODUCE: [...REL_COMMON,
    { key: "number",  label: "Výnos",  type: "number" },
    { key: "lambda",  label: "Lambda (0=deterministický)", type: "number" },
  ],
  TRIGGER: [...REL_COMMON,
    { key: "number",  label: "HP práh (-1=resurrekt, 0=ambient)", type: "number" },
    { key: "lambda",  label: "Lambda",  type: "number", optional: true },
  ],
  CONSUME: [...REL_COMMON,
    { key: "number",  label: "Množství", type: "number" },
  ],
};

// ── State ────────────────────────────────────────────────────────────────────
let world = null;        // raw world JSON object
let worldName = null;
let currentTab = "entities";
let sortCol = null;
let sortAsc = true;
let searchTerm = "";
let dirty = false;

// ── DOM refs ────────────────────────────────────────────────────────────────
const worldSelect    = document.getElementById("world-select");
const btnSave        = document.getElementById("btn-save");
const btnExport      = document.getElementById("btn-export");
const dirtyIndicator = document.getElementById("dirty-indicator");
const tabs           = document.getElementById("tabs");
const toolbar        = document.getElementById("toolbar");
const tableContainer = document.getElementById("table-container");
const emptyState     = document.getElementById("empty-state");
const mainTable      = document.getElementById("main-table");
const tableHead      = document.getElementById("table-head");
const tableBody      = document.getElementById("table-body");
const searchInput    = document.getElementById("search");
const btnAdd         = document.getElementById("btn-add");
const worldMeta      = document.getElementById("world-meta");
const metaName       = document.getElementById("meta-name");
const metaDesc       = document.getElementById("meta-desc");
const modalOverlay   = document.getElementById("modal-overlay");
const modalTitle     = document.getElementById("modal-title");
const modalFields    = document.getElementById("modal-fields");
const modalCancel    = document.getElementById("modal-cancel");
const modalDuplicate = document.getElementById("modal-duplicate");
const modalDelete    = document.getElementById("modal-delete");
const modalSave      = document.getElementById("modal-save");

// ── Init ─────────────────────────────────────────────────────────────────────
(async () => {
  const worlds = await api("/worlds");
  worlds.forEach(name => {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    worldSelect.appendChild(opt);
  });
})();

// ── Events ───────────────────────────────────────────────────────────────────
worldSelect.addEventListener("change", () => loadWorld(worldSelect.value));
btnSave.addEventListener("click", saveWorld);
btnExport.addEventListener("click", exportJSON);
searchInput.addEventListener("input", () => { searchTerm = searchInput.value.toLowerCase(); renderTable(); });
btnAdd.addEventListener("click", () => openModal(null));
modalCancel.addEventListener("click", closeModal);
modalOverlay.addEventListener("click", e => { if (e.target === modalOverlay) closeModal(); });
modalSave.addEventListener("click", saveModal);
modalDelete.addEventListener("click", deleteRecord);
modalDuplicate.addEventListener("click", duplicateRecord);

document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    tab.classList.add("active");
    currentTab = tab.dataset.tab;
    sortCol = null; sortAsc = true;
    searchInput.value = ""; searchTerm = "";
    renderTable();
  });
});

metaName.addEventListener("input", () => { world.name = metaName.value; markDirty(); });
metaDesc.addEventListener("input", () => { world.description = metaDesc.value; markDirty(); });

document.addEventListener("keydown", e => {
  if (e.key === "Escape") closeModal();
});

window.addEventListener("beforeunload", e => {
  if (dirty) { e.preventDefault(); e.returnValue = ""; }
});

// ── API ───────────────────────────────────────────────────────────────────────
async function api(url, method = "GET", body = null) {
  const opts = { method, headers: { "Content-Type": "application/json" } };
  if (body !== null) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  if (!res.ok) throw new Error(`${method} ${url} → ${res.status}`);
  if (res.status === 204) return null;
  return res.json();
}

// ── Load world ────────────────────────────────────────────────────────────────
async function loadWorld(name) {
  if (!name) return;
  if (dirty && !confirm("Máš neuložené změny. Chceš je zahodit?")) {
    worldSelect.value = worldName;
    return;
  }
  try {
    world = await api(`/worlds/${name}`);
    worldName = name;
    dirty = false;
    updateDirty();
    btnSave.disabled = false;
    btnExport.disabled = false;
    tabs.classList.remove("hidden");
    toolbar.classList.remove("hidden");
    worldMeta.classList.remove("hidden");
    metaName.value = world.name || "";
    metaDesc.value = world.description || "";
    currentTab = "entities";
    document.querySelectorAll(".tab").forEach(t =>
      t.classList.toggle("active", t.dataset.tab === "entities"));
    sortCol = null; sortAsc = true;
    renderTable();
    toast(`Načten svět: ${name}`);
  } catch (e) {
    toast(`Chyba: ${e.message}`, true);
  }
}

// ── Save world ────────────────────────────────────────────────────────────────
async function saveWorld() {
  try {
    await api(`/worlds/${worldName}`, "PUT", world);
    dirty = false;
    updateDirty();
    toast("Uloženo ✓");
  } catch (e) {
    toast(`Chyba při ukládání: ${e.message}`, true);
  }
}

function exportJSON() {
  const blob = new Blob([JSON.stringify(world, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `${worldName}.json`;
  a.click();
}

function markDirty() {
  dirty = true;
  updateDirty();
}

function updateDirty() {
  dirtyIndicator.classList.toggle("hidden", !dirty);
  btnSave.classList.toggle("btn-primary", dirty);
}

// ── Table rendering ───────────────────────────────────────────────────────────
function getRows() {
  if (currentTab === "entities") return world.entities;
  return world.relations.filter(r => r.type === currentTab);
}

function getSchema() {
  if (currentTab === "entities") return ENTITY_COLS;
  return REL_SCHEMAS[currentTab] || REL_COMMON;
}

// Columns to show in the table (subset of schema — skip textarea/long fields in table)
function getTableCols(schema) {
  return schema.filter(c => c.key !== "description" || currentTab === "entities"
    ? c.key !== "description"
    : false);
}

function renderTable() {
  if (!world) return;
  const schema = getSchema();
  const cols = schema.filter(c => c.key !== "description");

  // Header
  tableHead.innerHTML = "";
  cols.forEach(col => {
    const th = document.createElement("th");
    const isSorted = sortCol === col.key;
    th.innerHTML = `${col.label} <span class="sort-icon">${isSorted ? (sortAsc ? "▲" : "▼") : "⇅"}</span>`;
    if (isSorted) th.classList.add("sorted");
    th.addEventListener("click", () => {
      if (sortCol === col.key) sortAsc = !sortAsc;
      else { sortCol = col.key; sortAsc = true; }
      renderTable();
    });
    tableHead.appendChild(th);
  });
  // Actions column header
  const thAct = document.createElement("th");
  thAct.textContent = "";
  tableHead.appendChild(thAct);

  // Rows
  let rows = getRows();
  if (!rows || rows.length === 0) {
    mainTable.classList.add("hidden");
    emptyState.querySelector("p").textContent = "Žádné záznamy v této záložce.";
    emptyState.style.display = "flex";
    return;
  }

  // Filter
  if (searchTerm) {
    rows = rows.filter(r =>
      cols.some(c => String(r[c.key] ?? "").toLowerCase().includes(searchTerm))
    );
  }

  // Sort
  if (sortCol) {
    rows = [...rows].sort((a, b) => {
      const av = a[sortCol] ?? "";
      const bv = b[sortCol] ?? "";
      const cmp = typeof av === "number" && typeof bv === "number"
        ? av - bv
        : String(av).localeCompare(String(bv));
      return sortAsc ? cmp : -cmp;
    });
  }

  emptyState.style.display = "none";
  mainTable.classList.remove("hidden");
  tableBody.innerHTML = "";

  rows.forEach(row => {
    const tr = document.createElement("tr");
    cols.forEach(col => {
      const td = document.createElement("td");
      const val = row[col.key];
      if (col.key === "type" && currentTab === "entities") {
        td.innerHTML = `<span class="pill pill-${val}">${val}</span>`;
      } else if (col.type === "checkbox") {
        td.innerHTML = val
          ? `<span class="td-bool-true">✓</span>`
          : `<span class="td-bool-false">—</span>`;
      } else if (col.key === "id") {
        td.textContent = val ?? "";
        td.classList.add("td-id");
      } else if (typeof val === "number") {
        td.textContent = val;
        td.classList.add("td-num");
      } else {
        td.textContent = val ?? "";
      }
      tr.appendChild(td);
    });

    // Edit button cell
    const tdBtn = document.createElement("td");
    const editBtn = document.createElement("button");
    editBtn.textContent = "✏";
    editBtn.className = "btn";
    editBtn.style.cssText = "padding:2px 8px;font-size:0.75rem;";
    editBtn.addEventListener("click", e => { e.stopPropagation(); openModal(row); });
    tdBtn.appendChild(editBtn);
    tr.appendChild(tdBtn);

    tr.addEventListener("click", () => openModal(row));
    tableBody.appendChild(tr);
  });
}

// ── Modal ────────────────────────────────────────────────────────────────────
let editingRow = null;    // reference to the actual row object in world
let editingIsNew = false;

function openModal(row) {
  const schema = getSchema();
  const isNew = row === null;
  editingIsNew = isNew;

  if (isNew) {
    // Create a new blank row pre-filled from schema defaults
    if (currentTab === "entities") {
      editingRow = { id: "", name: "", type: "UNIQUE", description: "" };
    } else {
      const maxId = world.relations.reduce((m, r) => Math.max(m, r.id ?? 0), 0);
      editingRow = { id: maxId + 1, type: currentTab, ent1: "", ent2: "" };
      schema.forEach(c => { if (!(c.key in editingRow)) editingRow[c.key] = c.type === "number" ? 0 : ""; });
    }
    modalTitle.textContent = currentTab === "entities" ? "Nová entita" : `Nová relace: ${currentTab}`;
    modalDelete.style.display = "none";
    modalDuplicate.style.display = "none";
  } else {
    editingRow = row;
    modalTitle.textContent = currentTab === "entities"
      ? `Entita: ${row.id}`
      : `Relace #${row.id} — ${row.type}`;
    modalDelete.style.display = "";
    modalDuplicate.style.display = "";
  }

  // Build form fields
  modalFields.innerHTML = "";
  schema.forEach(col => {
    const label = document.createElement("label");
    label.textContent = col.label;
    label.htmlFor = `mf-${col.key}`;
    modalFields.appendChild(label);

    let input;
    if (col.type === "textarea") {
      input = document.createElement("textarea");
      input.rows = 3;
      input.value = editingRow[col.key] ?? "";
    } else if (col.type === "select") {
      input = document.createElement("select");
      col.options.forEach(opt => {
        const o = document.createElement("option");
        o.value = opt; o.textContent = opt;
        if (opt === (editingRow[col.key] ?? col.options[0])) o.selected = true;
        input.appendChild(o);
      });
    } else if (col.type === "checkbox") {
      const wrapper = document.createElement("div");
      wrapper.style.paddingTop = "8px";
      input = document.createElement("input");
      input.type = "checkbox";
      input.checked = !!editingRow[col.key];
      wrapper.appendChild(input);
      input.id = `mf-${col.key}`;
      modalFields.appendChild(wrapper);
      return;
    } else {
      input = document.createElement("input");
      input.type = col.type === "number" ? "number" : "text";
      const v = editingRow[col.key];
      input.value = v !== undefined && v !== null ? v : "";
    }
    input.id = `mf-${col.key}`;
    modalFields.appendChild(input);
  });

  modalOverlay.classList.remove("hidden");
  // Focus first input
  const first = modalFields.querySelector("input, select, textarea");
  if (first) setTimeout(() => first.focus(), 50);
}

function closeModal() {
  modalOverlay.classList.add("hidden");
  editingRow = null;
}

function readModalValues() {
  const schema = getSchema();
  const result = {};
  schema.forEach(col => {
    const el = document.getElementById(`mf-${col.key}`);
    if (!el) return;
    if (col.type === "checkbox") {
      result[col.key] = el.checked;
    } else if (col.type === "number") {
      const v = el.value.trim();
      result[col.key] = v === "" ? undefined : Number(v);
    } else {
      const v = el.value.trim();
      result[col.key] = v === "" ? undefined : v;
    }
  });
  return result;
}

function saveModal() {
  const values = readModalValues();

  if (editingIsNew) {
    // Append to world
    if (currentTab === "entities") {
      world.entities.push(cleanEntity(values));
    } else {
      world.relations.push(cleanRelation(values));
    }
  } else {
    // Patch existing row in-place (mutate the object that's in world.entities/relations)
    Object.keys(editingRow).forEach(k => delete editingRow[k]);
    const cleaned = currentTab === "entities" ? cleanEntity(values) : cleanRelation(values);
    Object.assign(editingRow, cleaned);
  }

  markDirty();
  closeModal();
  renderTable();
}

function deleteRecord() {
  if (!confirm("Opravdu smazat tento záznam?")) return;
  if (currentTab === "entities") {
    world.entities = world.entities.filter(e => e !== editingRow);
  } else {
    world.relations = world.relations.filter(r => r !== editingRow);
  }
  markDirty();
  closeModal();
  renderTable();
}

function duplicateRecord() {
  const values = readModalValues();
  closeModal();

  let newRow;
  if (currentTab === "entities") {
    newRow = cleanEntity({ ...values, id: values.id + "_copy" });
    world.entities.push(newRow);
  } else {
    const maxId = world.relations.reduce((m, r) => Math.max(m, r.id ?? 0), 0);
    newRow = cleanRelation({ ...values, id: maxId + 1 });
    world.relations.push(newRow);
  }
  markDirty();
  renderTable();
  // Open the new row immediately
  openModal(newRow);
}

// Remove undefined/empty optional fields before storing
function cleanEntity(v) {
  const out = {};
  ENTITY_COLS.forEach(col => {
    if (v[col.key] !== undefined && v[col.key] !== "" && v[col.key] !== null)
      out[col.key] = v[col.key];
  });
  return out;
}

function cleanRelation(v) {
  const schema = REL_SCHEMAS[currentTab] || REL_COMMON;
  const out = { type: currentTab };
  schema.forEach(col => {
    const val = v[col.key];
    if (val !== undefined && val !== "" && val !== null) {
      // Skip default booleans
      if (col.type === "checkbox" && val === false) return;
      out[col.key] = val;
    }
  });
  return out;
}

// ── Toast ─────────────────────────────────────────────────────────────────────
function toast(msg, isError = false) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.className = "toast" + (isError ? " error" : "");
  clearTimeout(el._timer);
  el._timer = setTimeout(() => el.classList.add("hidden"), 2500);
}
