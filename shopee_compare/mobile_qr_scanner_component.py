from __future__ import annotations

import streamlit as st

from .mobile_qr_scanner_assets import get_vendored_qr_library_url

HTML = """
<div class="qr-wrap">
  <div class="qr-status" data-kind="idle">Tap Start camera to begin scanning.</div>
  <div class="qr-reader"></div>
  <div class="qr-actions">
    <button class="qr-btn qr-start" type="button">Start camera</button>
    <button class="qr-btn qr-resume" type="button">Scan next</button>
    <button class="qr-btn qr-stop" type="button">Stop camera</button>
  </div>
</div>
"""
CSS = """
.qr-wrap { border: 1px solid rgba(49,51,63,0.2); border-radius: 0.75rem; padding: 0.75rem; background: var(--st-secondary-background-color); }
.qr-status { font-size: 0.95rem; margin-bottom: 0.75rem; min-height: 2.5rem; }
.qr-status[data-kind="error"] { color: #b42318; }
.qr-status[data-kind="paused"] { color: #175cd3; }
.qr-status[data-kind="scanning"] { color: #027a48; }
.qr-reader { width: 100%; min-height: 280px; border-radius: 0.75rem; overflow: hidden; background: #000; }
.qr-actions { display: flex; gap: 0.5rem; margin-top: 0.75rem; flex-wrap: wrap; }
.qr-btn { border: 0; border-radius: 999px; padding: 0.75rem 1rem; font-weight: 600; cursor: pointer; }
.qr-start { background: #0f766e; color: #fff; }
.qr-resume { background: #175cd3; color: #fff; }
.qr-stop { background: #344054; color: #fff; }
.qr-btn[disabled] { opacity: 0.45; cursor: not-allowed; }
"""
JS = """
let qrLibraryPromise = null;

async function loadQrLibrary(url) {
  if (!url) {
    throw new Error("Vendored QR library URL is missing.");
  }
  if (!qrLibraryPromise) {
    qrLibraryPromise = import(url);
  }
  return qrLibraryPromise;
}

function setStatus(state, payload) {
  state.component.setStateValue("status", payload);
  state.status.textContent = payload.message || "";
  state.status.dataset.kind = payload.kind || "idle";
}

function updateButtons(state) {
  state.start.disabled = !state.enabled || state.isScanning || state.isPaused;
  state.resume.disabled = !state.enabled || !state.isPaused;
  state.stop.disabled = !state.enabled || (!state.isScanning && !state.isPaused);
}

async function stopScanner(state, clearReader = true) {
  if (state.scanner && (state.isScanning || state.isPaused)) {
    try {
      await state.scanner.stop();
    } catch (error) {
    }
  }
  state.isScanning = false;
  state.isPaused = false;
  if (clearReader) {
    state.reader.innerHTML = "";
  }
  updateButtons(state);
}

async function startScanner(state) {
  if (!state.enabled) {
    setStatus(state, { kind: "disabled", code: "no-shops", message: "Import at least one shop to enable camera scan." });
  } else if (!window.isSecureContext) {
    setStatus(state, { kind: "error", code: "insecure-context", message: "Camera requires HTTPS or localhost. Open this page from a secure URL." });
    return;
  }
  if (!state.enabled) {
    return;
  }
  try {
    const module = await loadQrLibrary(state.component.data?.library_url);
    const Html5Qrcode = module.Html5Qrcode;
    const Html5QrcodeSupportedFormats = module.Html5QrcodeSupportedFormats;
    if (!state.scanner) {
      state.scanner = new Html5Qrcode(state.readerId, {
        formatsToSupport: [Html5QrcodeSupportedFormats.QR_CODE],
        verbose: false
      });
    }
    await state.scanner.start(
      { facingMode: "environment" },
      {
        fps: 10,
        qrbox: (width, height) => {
          const edge = Math.floor(Math.min(width, height) * 0.7);
          return { width: edge, height: edge };
        }
      },
      (decodedText) => {
        const value = (decodedText || "").trim();
        if (!value) {
          return;
        }
        const now = Date.now();
        if (state.lastText === value && now - state.lastScanAt < 1500) {
          return;
        }
        state.lastText = value;
        state.lastScanAt = now;
        state.scanner.pause(false);
        state.isScanning = false;
        state.isPaused = true;
        updateButtons(state);
        setStatus(state, { kind: "paused", code: "scan-success", message: `Scanned: ${value}. Tap Scan next to continue.` });
        state.component.setTriggerValue("scan", {
          text: value,
          source: "camera",
          scanned_at: new Date().toISOString()
        });
      },
      () => {}
    );
    state.isScanning = true;
    state.isPaused = false;
    updateButtons(state);
    setStatus(state, { kind: "scanning", code: "scanning", message: "Camera is scanning. Point the QR into the frame." });
  } catch (error) {
    setStatus(state, {
      kind: "error",
      code: "camera-start-failed",
      message: `Could not start camera scanner. ${error?.message || "Check permission and browser support."}`
    });
  }
}

function resumeScanner(state) {
  if (!state.scanner || !state.isPaused) {
    return;
  }
  state.scanner.resume();
  state.isPaused = false;
  state.isScanning = true;
  updateButtons(state);
  setStatus(state, { kind: "scanning", code: "scanning", message: "Camera is scanning. Point the QR into the frame." });
}

export default function(component) {
  const root = component.parentElement;
  let state = root.__mobileQrState;
  if (!state) {
    root.innerHTML = HTML_CONTENT;
    state = {
      component, enabled: false, isScanning: false, isPaused: false, lastText: "", lastScanAt: 0,
      readerId: `mobile-qr-reader-${component.key}`,
      status: root.querySelector(".qr-status"),
      reader: root.querySelector(".qr-reader"),
      start: root.querySelector(".qr-start"),
      resume: root.querySelector(".qr-resume"),
      stop: root.querySelector(".qr-stop"),
      scanner: null
    };
    state.reader.id = state.readerId;
    state.start.onclick = () => startScanner(state);
    state.resume.onclick = () => resumeScanner(state);
    state.stop.onclick = async () => {
      await stopScanner(state);
      setStatus(state, { kind: "idle", code: "stopped", message: "Camera stopped." });
    };
    root.__mobileQrState = state;
  }
  state.component = component;
  state.enabled = Boolean(component.data?.enabled);
  updateButtons(state);
  if (!state.enabled) {
    setStatus(state, { kind: "disabled", code: "no-shops", message: "Import at least one shop to enable camera scan." });
  } else if (!state.isScanning && !state.isPaused) {
    setStatus(state, { kind: "idle", code: "ready", message: "Tap Start camera to begin scanning." });
  }
}
"""
JS = f"const HTML_CONTENT = {HTML!r};\\n" + JS


def render_mobile_qr_scanner(*, enabled: bool, key: str):
    component = st.components.v2.component(
        "mobile_qr_scanner",
        html=HTML,
        css=CSS,
        js=JS,
    )
    return component(
        key=key,
        height=420,
        data={"enabled": enabled, "library_url": get_vendored_qr_library_url()},
        default={"status": {"kind": "idle", "code": "ready", "message": "Tap Start camera to begin scanning."}},
        on_status_change=lambda: None,
        on_scan_change=lambda: None,
    )
