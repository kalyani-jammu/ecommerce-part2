// A random browser identifier is used for unique-visitor counting; no name/email is collected.
(function () {
  try {
    let visitorId = localStorage.getItem("shopease_visitor_id");
    if (!visitorId) {
      visitorId = "v_" + (crypto.randomUUID ? crypto.randomUUID().replaceAll("-", "") : Math.random().toString(36).slice(2) + Date.now());
      localStorage.setItem("shopease_visitor_id", visitorId);
    }
    fetch("/api/track", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ visitor_id: visitorId, page_url: location.pathname })
    }).catch(() => {});
  } catch (_) { /* Analytics must never prevent the storefront from loading. */ }
})();
