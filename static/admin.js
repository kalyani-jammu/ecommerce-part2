const $ = (selector) => document.querySelector(selector);
const number = (value) => new Intl.NumberFormat().format(value || 0);
async function api(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed.");
  return data;
}
async function loadOverview() {
  const d = await api("/api/analytics/overview");
  $("#real-users").textContent = number(d.real_users);
  $("#active-users").textContent = number(d.active_users_5m);
  $("#country-count").textContent = number(d.countries);
  $("#real-visits").textContent = number(d.real_visits);
}
async function loadCountries() {
  const rows = await api(`/api/analytics/countries?source=${$("#country-source").value}`);
  const body = $("#country-rows"); body.replaceChildren();
  if (!rows.length) { body.innerHTML = '<tr><td colspan="3" class="muted">No visitor records yet.</td></tr>'; return; }
  rows.forEach(row => {
    const tr = document.createElement("tr");
    const country = document.createElement("td"); country.textContent = `${row.country_code ? row.country_code + " · " : ""}${row.country}`;
    const users = document.createElement("td"); users.textContent = number(row.users);
    const share = document.createElement("td");
    const wrap = document.createElement("div"); wrap.className = "share-cell";
    const bar = document.createElement("span"); bar.className = "share-bar"; bar.style.width = `${row.percentage}%`;
    const label = document.createElement("small"); label.textContent = `${row.percentage}%`;
    wrap.append(bar, label); share.append(wrap); tr.append(country, users, share); body.append(tr);
  });
}
async function loadTraffic() {
  const rows = await api(`/api/analytics/traffic?source=${$("#traffic-source").value}`);
  const chart = $("#traffic-chart"); chart.replaceChildren();
  if (!rows.length) { chart.textContent = "No traffic data yet."; chart.classList.add("empty-chart"); return; }
  chart.classList.remove("empty-chart");
  const max = Math.max(1, ...rows.map(r => r.visits));
  rows.forEach(row => {
    const item = document.createElement("div"); item.className = "bar-item";
    const value = document.createElement("b"); value.textContent = row.visits;
    const bar = document.createElement("div"); bar.className = "bar-track";
    const fill = document.createElement("span"); fill.style.height = `${Math.max(4, row.visits / max * 100)}%`; bar.append(fill);
    const date = document.createElement("small"); date.textContent = row.date.slice(5);
    item.append(value, bar, date); chart.append(item);
  });
}
async function refresh() { try { await Promise.all([loadOverview(), loadCountries(), loadTraffic()]); } catch (e) { console.error(e); } }
if ($("#country-source")) {
  $("#country-source").addEventListener("change", loadCountries);
  $("#traffic-source").addEventListener("change", loadTraffic);
  $("#run-simulator").addEventListener("click", async () => {
    const button = $("#run-simulator"), message = $("#sim-message");
    const countries = Array.from($("#sim-countries").selectedOptions).map(o => o.value);
    button.disabled = true; button.textContent = "Generating…"; message.textContent = "";
    try {
      const result = await api("/api/simulator/run", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ count: Number($("#sim-count").value), countries }) });
      message.textContent = result.message; message.className = "form-message success";
      await refresh(); $("#country-source").value = "simulated"; await loadCountries();
    } catch (e) { message.textContent = e.message; message.className = "form-message error-text"; }
    finally { button.disabled = false; button.textContent = "Run simulation"; }
  });
  refresh();
}
