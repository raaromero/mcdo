// Every panel (.cell) gets two small controls at its top right: ⤢ makes it span the full width (again: back), and the grip
// ⠿ drags it: drop it on another panel to swap the two, or on the empty space of a column to move it to the end of that column.
// The corner handle ◢ at the bottom right stretches the panel's width and height (double-click it: back to the normal size).
// A panel stretched wider than its column takes the full row; maps keep equal µm per pixel along x and z, so they fit in the box.
// Charts and maps redraw themselves when their size changes (ResizeObserver in plot.ts and heat.ts).
let dragged: HTMLElement | null = null;

function decorate(cell: HTMLElement) {
  if (cell.dataset.panel) return;
  cell.dataset.panel = "1";
  const bar = document.createElement("div");
  bar.className = "panel-bar";
  const grip = document.createElement("button");
  grip.type = "button"; grip.className = "panel-btn grip"; grip.textContent = "⠿"; grip.title = "Drag to move this panel";
  const wide = document.createElement("button");
  wide.type = "button"; wide.className = "panel-btn"; wide.textContent = "⤢"; wide.title = "Full width / back";
  wide.onclick = () => { cell.classList.toggle("panel-wide"); wide.setAttribute("aria-pressed", String(cell.classList.contains("panel-wide"))); };
  bar.append(grip, wide);
  const corner = document.createElement("div");
  corner.className = "panel-size"; corner.title = "Drag to stretch; double-click for the normal size";
  corner.addEventListener("pointerdown", (e) => stretch(cell, e));
  corner.addEventListener("dblclick", () => unstretch(cell));
  cell.append(bar, corner);
  grip.addEventListener("mousedown", () => { cell.draggable = true; });
  cell.addEventListener("dragstart", (e) => { dragged = cell; cell.classList.add("panel-dragging"); e.dataTransfer?.setData("text/plain", ""); });
  cell.addEventListener("dragend", () => { cell.draggable = false; cell.classList.remove("panel-dragging"); dragged = null;
    document.querySelectorAll(".panel-over, .panel-zone").forEach((n) => n.classList.remove("panel-over", "panel-zone")); });
  cell.addEventListener("dragover", (e) => { if (dragged && dragged !== cell) { e.preventDefault(); cell.classList.add("panel-over"); } });
  cell.addEventListener("dragleave", () => cell.classList.remove("panel-over"));
  cell.addEventListener("drop", (e) => {
    e.preventDefault(); cell.classList.remove("panel-over");
    if (!dragged || dragged === cell) return;
    const a = dragged, b = cell, pa = a.parentElement!, pb = b.parentElement!, na = a.nextSibling, nb = b.nextSibling;
    if (na === b) { pb.insertBefore(b, a); return; }                     // neighbours: swap
    if (nb === a) { pa.insertBefore(a, b); return; }
    pb.insertBefore(a, nb); pa.insertBefore(b, na);                       // anywhere on the page: swap the two
  });
}

/** The part of the panel that sets its height: a chart box, a map, or the panel itself. */
function body(cell: HTMLElement): HTMLElement {
  return cell.querySelector<HTMLElement>(":scope > .lc-box") ?? cell;
}

function stretch(cell: HTMLElement, e: PointerEvent) {
  e.preventDefault();
  const handle = e.currentTarget as HTMLElement, b = body(cell), x0 = e.clientX, y0 = e.clientY;
  const w0 = cell.getBoundingClientRect().width, h0 = b.getBoundingClientRect().height;
  const col = w0, row = cell.parentElement!.getBoundingClientRect().width;  // its column width, and the full row
  const wasWide = cell.classList.contains("panel-wide");
  handle.setPointerCapture(e.pointerId);
  cell.classList.add("panel-stretching");
  const move = (m: PointerEvent) => {
    const w = Math.max(220, w0 + m.clientX - x0), h = Math.max(140, h0 + m.clientY - y0);
    const wide = wasWide || w > col + 24;                                 // wider than its column: take the full row
    cell.classList.toggle("panel-wide", wide);
    cell.style.width = wide && w >= row - 8 ? "" : `${Math.min(w, row)}px`;
    b.style.height = `${h}px`;
  };
  const up = () => { handle.removeEventListener("pointermove", move); cell.classList.remove("panel-stretching"); };
  handle.addEventListener("pointermove", move);
  handle.addEventListener("pointerup", up, { once: true });
  handle.addEventListener("pointercancel", up, { once: true });
}

function unstretch(cell: HTMLElement) {
  cell.style.width = ""; body(cell).style.height = "";
  cell.classList.remove("panel-wide");
}

function zone(col: HTMLElement) {
  if (col.dataset.zone) return;
  col.dataset.zone = "1";
  col.addEventListener("dragover", (e) => { if (dragged && e.target === col) { e.preventDefault(); col.classList.add("panel-zone"); } });
  col.addEventListener("dragleave", (e) => { if (e.target === col) col.classList.remove("panel-zone"); });
  col.addEventListener("drop", (e) => {
    if (e.target !== col || !dragged) return;
    e.preventDefault(); col.classList.remove("panel-zone");
    col.append(dragged);
  });
}

export function panels(root: HTMLElement) {
  const run = () => { root.querySelectorAll<HTMLElement>(".cell").forEach(decorate); root.querySelectorAll<HTMLElement>(".stack, .stack2").forEach(zone); };
  new MutationObserver(run).observe(root, { childList: true, subtree: true });
  run();
}
