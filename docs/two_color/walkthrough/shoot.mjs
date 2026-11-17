// Screenshots of each walkthrough step from a local preview of the dashboard (Chromium over the DevTools protocol).
// node shoot.mjs <steps.json> <out dir> [port]
import fs from "fs";
const [steps, out, port = "9333"] = process.argv.slice(2);
const list = JSON.parse(fs.readFileSync(steps, "utf8")).filter((s) => !process.env.ONLY || process.env.ONLY.split(",").includes(s.id));
const t = (await (await fetch(`http://localhost:${port}/json`)).json()).find((x) => x.type === "page");
const ws = new WebSocket(t.webSocketDebuggerUrl); await new Promise((r) => (ws.onopen = r));
let id = 0; const pend = new Map();
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { pend.get(d.id)(d.result); pend.delete(d.id); } };
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async (e) => (await send("Runtime.evaluate", { expression: e, returnByValue: true, awaitPromise: true })).result.value;
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
await send("Emulation.setDeviceMetricsOverride", { width: 1500, height: 1000, deviceScaleFactor: 1, mobile: false });
const info = {};
for (const s of list) {
  await send("Page.navigate", { url: `http://localhost:4173/?noworker&r=${Date.now()}#${s.h}` });
  await wait(1500);
  for (let k = 0; k < 120; k++) {                      // until the data are in and nothing is still computing
    const busy = await ev(`!document.querySelector('.cell') || /Computing|Loading/.test(document.getElementById('app').innerText)`);
    if (!busy) break;
    await wait(500);
  }
  await wait(1500 + (s.wait || 0));                   // maps of Pulse results are computed one after another
  if (s.find) await ev(`(()=>{const e=[...document.querySelectorAll('h2.cell-title, .heat svg text.t')].find(x=>x.textContent.includes(${JSON.stringify(s.find)}));
    if(e){e.scrollIntoView({block:'start'}); scrollBy(0,-60);} })()`);
  else if (s.scroll) await ev(`(()=>{const e=document.querySelector('${s.scroll}'); if(e){e.scrollIntoView({block:'start'}); scrollBy(0,-70);} })()`);
  else await ev(`scrollTo(0,0)`);
  await wait(800);
  const r = await send("Page.captureScreenshot", { format: "jpeg", quality: 82 });
  fs.writeFileSync(`${out}/${s.id}.jpg`, Buffer.from(r.data, "base64"));
  info[s.id] = await ev(`({title:[...document.querySelectorAll('.cell-title')].map(e=>e.textContent),
    maps:[...document.querySelectorAll('.heat svg text.t')].map(e=>e.textContent),
    legend:[...document.querySelectorAll('.legend li')].map(e=>e.textContent.trim()),
    notes:[...document.querySelectorAll('.note')].map(e=>e.textContent).filter(Boolean),
    how:(document.querySelector('.how-text')||{}).innerText||''})`);
  console.log(s.id, "done");
}
fs.writeFileSync(`${out}/info.json`, JSON.stringify(info, null, 1));
ws.close();
