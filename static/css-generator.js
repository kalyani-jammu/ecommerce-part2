const $ = (s) => document.querySelector(s);
const controls = ["bg-color", "text-color", "font-size", "padding", "radius", "font-family", "shadow"];
function cssText() {
  return `.generated-element {\n  background-color: ${$("#bg-color").value};\n  color: ${$("#text-color").value};\n  font-size: ${$("#font-size").value}px;\n  padding: ${$("#padding").value}px;\n  border-radius: ${$("#radius").value}px;\n  font-family: ${$("#font-family").value};\n  box-shadow: ${$("#shadow").value};\n}`;
}
function update() {
  const css = cssText();
  $("#preview-button").style.cssText = css.replace(".generated-element", "").replace(/[{}]/g, "");
  $("#css-output").textContent = css;
  $("#font-size-value").textContent = $("#font-size").value + "px";
  $("#padding-value").textContent = $("#padding").value + "px";
  $("#radius-value").textContent = $("#radius").value + "px";
}
controls.forEach(id => $("#" + id).addEventListener("input", update));
$("#reset-style").addEventListener("click", () => {
  const defaults = { "bg-color": "#28735e", "text-color": "#ffffff", "font-size": 16, padding: 14, radius: 10, "font-family": "Arial, sans-serif", shadow: "none" };
  Object.entries(defaults).forEach(([id, value]) => $("#" + id).value = value); update();
});
$("#copy-css").addEventListener("click", async () => {
  try { await navigator.clipboard.writeText(cssText()); $("#css-message").textContent = "CSS copied."; }
  catch (_) { $("#css-message").textContent = "Clipboard access unavailable; select and copy the code."; }
});
async function loadSaved() {
  const list = $("#saved-styles");
  try {
    const styles = await (await fetch("/api/css/saved")).json(); list.replaceChildren();
    if (!styles.length) { list.textContent = "No saved styles yet."; return; }
    styles.forEach(style => {
      const item = document.createElement("div"); item.className = "saved-style";
      const title = document.createElement("strong"); title.textContent = style.name;
      const date = document.createElement("small"); date.textContent = new Date(style.created_at).toLocaleString();
      const code = document.createElement("pre"); code.textContent = style.css_code;
      item.append(title, date, code); list.append(item);
    });
  } catch (_) { list.textContent = "Could not load saved styles."; }
}
$("#save-css").addEventListener("click", async () => {
  const message = $("#css-message");
  try {
    const response = await fetch("/api/css/save", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: $("#style-name").value, css_code: cssText() }) });
    const result = await response.json(); if (!response.ok) throw new Error(result.error || "Could not save CSS.");
    message.textContent = "Style saved successfully."; await loadSaved();
  } catch (e) { message.textContent = e.message; }
});
update(); loadSaved();
