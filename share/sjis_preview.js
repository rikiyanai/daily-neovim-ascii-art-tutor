(function () {
  "use strict";

  function queryToken() {
    return new URLSearchParams(window.location.search).get("token");
  }

  function endpoint() {
    var token = queryToken();
    return token ? "/api/preview?token=" + encodeURIComponent(token) : "preview.json";
  }

  function setImage(img, url, width, height) {
    return new Promise(function (resolve, reject) {
      img.onload = resolve;
      img.onerror = function () { reject(new Error("native image failed to load")); };
      if (width) img.width = width;
      if (height) img.height = height;
      img.src = url;
      if (img.complete && img.naturalWidth) resolve();
    });
  }

  function setPanel(name, panel) {
    var root = document.querySelector('[data-panel="' + name + '"]');
    if (!root || !panel) return;
    root.querySelector(".raw").textContent = panel.text;
    return setImage(root.querySelector(".raster"), panel.png_data_url,
      panel.width_px, panel.height_px);
  }

  function render(payload) {
    var images = [setPanel("before", payload.before),
      setPanel("yours", payload.yours), setPanel("target", payload.target)];
    var diff = payload.difference || {};
    images.push(setImage(document.getElementById("difference-image"), diff.png_data_url));
    document.getElementById("difference-summary").textContent =
      "changed pixels: " + diff.changed_pixel_count +
      " · changed bbox: " + JSON.stringify(diff.changed_bbox) +
      " · visual equal: " + diff.visual_equal;

    var receipt = payload.receipt || {};
    var gate = payload.gate || {};
    var root = document.getElementById("receipt");
    var gateClass = gate.transcription_ready ? "pass" : "fail";
    root.innerHTML =
      "<div class=\"" + gateClass + "\"><strong>TRANSCRIPTION READY: " +
      gate.transcription_ready + "</strong></div>" +
      "<div>preview present: " + gate.preview_present +
      " · receipt fresh: " + gate.fresh_receipt +
      " · operator visual acceptance: " + gate.operator_visual_acceptance +
      "</div>" +
      "<div>font SHA-256: " + receipt.font_sha256 +
      "<br>source bytes SHA-256: " + receipt.source_byte_sha256 +
      "<br>target text SHA-256: " + receipt.target_text_sha256 +
      "</div>";
    document.getElementById("status").textContent =
      "Native raster loaded at " + payload.font.font_size_px +
      " px with " + payload.font.line_pitch_px + " px line pitch.";
    var joins = payload.join_evaluation;
    document.getElementById("join-summary").textContent = joins ?
      "Target registration: " + (joins.passed ? "matches" : "differs") +
        " · " + joins.measurements.length + " visible glyph positions compared." :
      "No target registration positions have been declared.";
    var scale = payload.font.lattice_px_per_unit;
    document.getElementById("join-measurements").textContent = joins ?
      joins.measurements.map(function (item) {
        return item.name + ": target x=" + item.expected_x_units * scale +
          " px, yours x=" + item.actual_x_units * scale +
          " px; vertical difference=" + item.delta_y_px + " px; " +
          (item.passed ? "matches" : "differs");
      }).join("\n") : "";
    var identity = {};
    ["source_byte_sha256", "source_text_sha256", "yours_text_sha256",
      "target_text_sha256", "font_sha256", "font_size_px", "line_pitch_px",
      "before_pixel_sha256", "yours_pixel_sha256", "target_pixel_sha256",
      "diff_pixel_sha256", "join_contract_sha256"].forEach(function (key) {
        identity[key] = receipt[key];
      });
    return Promise.all(images).then(function () { return fontLoaded; }).then(function () {
      if (!queryToken()) return;
      return fetch("/api/seen?token=" + encodeURIComponent(queryToken()), {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(identity)
      }).then(function (response) {
        if (!response.ok) throw new Error("Preview changed; display acknowledgement refused");
      });
    });
  }

  var fontLoaded = Promise.resolve();
  if (queryToken()) {
    var nativeFont = new FontFace("SaitamaarTutor", "url(/font.ttf?token=" +
      encodeURIComponent(queryToken()) + ")");
    fontLoaded = nativeFont.load().then(function (font) {
      document.fonts.add(font);
      document.body.classList.add("native-font-ready");
    });
  }

  function load() {
    return fetch(endpoint(), { cache: "no-store" })
      .then(function (response) {
        if (!response.ok) throw new Error("preview request failed: " + response.status);
        return response.json();
      })
      .then(render)
      .catch(function (error) {
        document.getElementById("status").textContent =
          "Preview unavailable: " + error.message;
      });
  }

  load();
  // The local adapter may receive editor updates through PreviewServer.update.
  // No polling is enabled for a file:// or un-tokened static preview.
  if (queryToken()) window.setInterval(load, 1000);
}());
