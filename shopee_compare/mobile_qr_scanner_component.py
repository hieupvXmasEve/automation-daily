from __future__ import annotations

import streamlit as st

from .mobile_qr_scanner_assets import get_vendored_qr_library_url

HTML = """
<div class="qr-wrap">
  <div class="qr-status" data-kind="idle">Tap Start camera to begin scanning.</div>
  <div class="qr-camera-row">
    <select class="qr-camera-select" aria-label="Camera device">
      <option value="">Auto-select camera</option>
    </select>
    <button class="qr-btn qr-refresh" type="button">Refresh cameras</button>
  </div>
  <div class="qr-reader"></div>
  <div class="qr-actions">
    <button class="qr-btn qr-start" type="button">Start camera</button>
    <button class="qr-btn qr-resume" type="button">Scan next</button>
    <button class="qr-btn qr-stop" type="button">Stop camera</button>
  </div>
</div>
"""
CSS = """
.qr-wrap { width: 100%; max-width: 36rem; margin: 0 auto; border: 1px solid rgba(49,51,63,0.2); border-radius: 0.75rem; padding: 0.75rem; background: var(--st-secondary-background-color); }
.qr-status { font-size: 0.95rem; margin-bottom: 0.75rem; min-height: 2.5rem; }
.qr-status[data-kind="error"] { color: #b42318; }
.qr-status[data-kind="paused"] { color: #175cd3; }
.qr-status[data-kind="scanning"] { color: #027a48; }
.qr-camera-row { display: flex; gap: 0.5rem; margin-bottom: 0.75rem; flex-wrap: wrap; }
.qr-camera-select { flex: 1 1 16rem; min-width: 0; border: 1px solid rgba(49,51,63,0.2); border-radius: 0.75rem; padding: 0.7rem 0.85rem; background: #fff; color: #101828; }
.qr-reader { position: relative; width: 100%; min-height: 34rem; border-radius: 0.75rem; overflow: hidden; background: #000; }
.qr-reader video, .qr-reader canvas { width: 100% !important; height: 100% !important; object-fit: cover; }
.qr-actions { display: flex; gap: 0.5rem; margin-top: 0.75rem; flex-wrap: wrap; }
.qr-btn { border: 0; border-radius: 999px; padding: 0.75rem 1rem; font-weight: 600; cursor: pointer; }
.qr-start { background: #0f766e; color: #fff; }
.qr-resume { background: #175cd3; color: #fff; }
.qr-stop { background: #344054; color: #fff; }
.qr-refresh { background: #667085; color: #fff; }
.qr-btn[disabled] { opacity: 0.45; cursor: not-allowed; }
.qr-c { position: absolute; width: 2rem; height: 2rem; border-color: #34d399; border-style: solid; }
.qr-c-tl { top: 0; left: 0; border-width: 3px 0 0 3px; border-radius: 4px 0 0 0; }
.qr-c-tr { top: 0; right: 0; border-width: 3px 3px 0 0; border-radius: 0 4px 0 0; }
.qr-c-bl { bottom: 0; left: 0; border-width: 0 0 3px 3px; border-radius: 0 0 0 4px; }
.qr-c-br { bottom: 0; right: 0; border-width: 0 3px 3px 0; border-radius: 0 0 4px 0; }
"""
JS = """
let qrLibraryPromise = null;

function isLikelyMobile() {
  return /android|iphone|ipad|ipod/i.test((navigator.userAgent || "").toLowerCase());
}

function cameraAutoLabel() {
  return isLikelyMobile() ? "Auto-select rear camera" : "Auto-select default camera";
}

async function loadQrLibrary(url) {
  if (!url) {
    throw new Error("Vendored QR library URL is missing.");
  }
  if (!qrLibraryPromise) {
    qrLibraryPromise = import(url);
  }
  return qrLibraryPromise;
}

function formatError(error) {
  if (!error) {
    return "Unknown browser error.";
  }
  if (typeof error === "string") {
    return error;
  }
  if (error instanceof Error) {
    return error.message || error.name || "Unknown browser error.";
  }
  const message = [error.name, error.message, error.code].filter(Boolean).join(": ");
  if (message) {
    return message;
  }
  try {
    return JSON.stringify(error);
  } catch {
    return String(error);
  }
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
  state.refresh.disabled = !state.enabled || state.isScanning;
}

function setCameraOptions(state, cameras) {
  const previous = state.cameraSelect.value || state.selectedCameraId || "";
  state.cameras = Array.isArray(cameras) ? cameras : [];
  state.cameraSelect.innerHTML = "";
  const autoOption = document.createElement("option");
  autoOption.value = "";
  autoOption.textContent = cameraAutoLabel();
  state.cameraSelect.appendChild(autoOption);
  state.cameras.forEach((camera, index) => {
    const option = document.createElement("option");
    option.value = camera.id || "";
    option.textContent = (camera.label || "").trim() || `Camera ${index + 1}`;
    state.cameraSelect.appendChild(option);
  });
  const fallback = previous && state.cameras.some((camera) => camera.id === previous)
    ? previous
    : (!isLikelyMobile() && state.cameras[0] ? state.cameras[0].id : "");
  state.cameraSelect.value = fallback;
  state.selectedCameraId = state.cameraSelect.value;
}

async function refreshCameraOptions(state, silent = false) {
  if (!navigator.mediaDevices?.enumerateDevices) {
    setCameraOptions(state, []);
    if (!silent) {
      setStatus(state, { kind: "error", code: "camera-enumeration-unsupported", message: "This browser does not expose camera device selection." });
    }
    return;
  }
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const cameras = devices
      .filter((device) => device.kind === "videoinput")
      .map((device) => ({ id: device.deviceId, label: device.label }));
    setCameraOptions(state, cameras);
    if (!silent && cameras.length) {
      setStatus(state, { kind: "idle", code: "camera-list-ready", message: "Camera list refreshed. Choose a device or use auto-select." });
    }
  } catch (error) {
    setCameraOptions(state, []);
    if (!silent) {
      setStatus(state, { kind: "error", code: "camera-enumeration-failed", message: `Could not list cameras. ${formatError(error)}` });
    }
  }
}

function resolveCameraConfig(state) {
  const selectedId = state.cameraSelect.value;
  state.selectedCameraId = selectedId;
  if (selectedId) {
    return selectedId;
  }
  if (isLikelyMobile()) {
    return { facingMode: "environment" };
  }
  return state.cameras[0]?.id || { facingMode: "user" };
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
  removeCornerFrame(state);
  if (state._orientationHandler) {
    screen.orientation?.removeEventListener("change", state._orientationHandler);
    state._orientationHandler = null;
  }
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
    await refreshCameraOptions(state, true);
    // Lock portrait to prevent video rotation when phone tilts to landscape
    if (screen.orientation?.lock) {
      try { await screen.orientation.lock("portrait"); } catch {}
    }
    const module = await loadQrLibrary(state.component.data?.library_url);
    const Html5Qrcode = module.Html5Qrcode;
    const Html5QrcodeSupportedFormats = module.Html5QrcodeSupportedFormats;
    if (!state.scanner) {
      state.scanner = new Html5Qrcode(state.readerId, {
        formatsToSupport: [Html5QrcodeSupportedFormats.QR_CODE],
        experimentalFeatures: { useBarCodeDetectorIfSupported: true },
        verbose: false
      });
    }
    await state.scanner.start(
      resolveCameraConfig(state),
      {
        fps: 15,
        qrbox: (width, height) => {
          const edge = Math.floor(Math.min(width, height) * 0.85);
          return { width: edge, height: edge };
        }
      },
      (decodedText) => {
        const value = (decodedText || "").trim();
        if (!value) {
          return;
        }
        const now = Date.now();
        if (state.lastText === value && now - state.lastScanAt < 800) {
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
    await refreshCameraOptions(state, true);
    state.isScanning = true;
    state.isPaused = false;
    // Register orientation handler to keep video stable when phone tilts
    state._orientationHandler = () => applyVideoOrientationFix(state);
    screen.orientation?.addEventListener("change", state._orientationHandler);
    setTimeout(() => applyVideoOrientationFix(state), 500);
    injectCornerFrame(state);
    updateButtons(state);
    setStatus(state, { kind: "scanning", code: "scanning", message: "Camera is scanning. Point the QR into the frame." });
  } catch (error) {
    setStatus(state, {
      kind: "error",
      code: "camera-start-failed",
      message: `Could not start camera scanner. ${formatError(error)}`
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

function applyVideoOrientationFix(state) {
  // Counter-rotate video/canvas to neutralize browser's auto-rotation when phone tilts
  const angle = screen.orientation?.angle ?? 0;
  const counterAngle = angle === 0 ? 0 : (360 - angle) % 360;
  const transform = counterAngle ? `rotate(${counterAngle}deg)` : "";
  state.reader.querySelectorAll("video, canvas").forEach(el => {
    el.style.transform = transform;
    el.style.transformOrigin = "center center";
  });
}

function injectCornerFrame(state) {
  // Inject L-bracket corners aligned to the qrbox area after camera renders
  setTimeout(() => {
    removeCornerFrame(state);
    const w = state.reader.clientWidth;
    const h = state.reader.clientHeight;
    if (!w || !h) return;
    const edge = Math.floor(Math.min(w, h) * 0.85);
    const left = Math.floor((w - edge) / 2);
    const top = Math.floor((h - edge) / 2);
    const frame = document.createElement("div");
    frame.className = "qr-corner-frame";
    frame.style.cssText = `position:absolute;top:${top}px;left:${left}px;width:${edge}px;height:${edge}px;pointer-events:none;z-index:10;`;
    frame.innerHTML = '<span class="qr-c qr-c-tl"></span><span class="qr-c qr-c-tr"></span><span class="qr-c qr-c-bl"></span><span class="qr-c qr-c-br"></span>';
    state.reader.appendChild(frame);
  }, 400);
}

function removeCornerFrame(state) {
  const existing = state.reader.querySelector(".qr-corner-frame");
  if (existing) existing.remove();
}

export default function(component) {
  const root = component.parentElement;
  let state = root.__mobileQrState;
  if (!state) {
    state = {
      component, enabled: false, isScanning: false, isPaused: false, lastText: "", lastScanAt: 0,
      readerId: `mobile-qr-reader-${component.key}`,
      status: root.querySelector(".qr-status"),
      cameraSelect: root.querySelector(".qr-camera-select"),
      reader: root.querySelector(".qr-reader"),
      start: root.querySelector(".qr-start"),
      resume: root.querySelector(".qr-resume"),
      stop: root.querySelector(".qr-stop"),
      refresh: root.querySelector(".qr-refresh"),
      cameras: [],
      selectedCameraId: "",
      scanner: null,
      _orientationHandler: null
    };
    state.reader.id = state.readerId;
    state.cameraSelect.onchange = () => {
      state.selectedCameraId = state.cameraSelect.value;
    };
    state.refresh.onclick = () => refreshCameraOptions(state, false);
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
  setCameraOptions(state, state.cameras);
  updateButtons(state);
  if (!state.enabled) {
    setStatus(state, { kind: "disabled", code: "no-shops", message: "Import at least one shop to enable camera scan." });
  } else if (!state.isScanning && !state.isPaused) {
    setStatus(state, { kind: "idle", code: "ready", message: "Tap Start camera to begin scanning." });
  }
}
"""


def render_mobile_qr_scanner(*, enabled: bool, key: str):
    component = st.components.v2.component(
        "mobile_qr_scanner",
        html=HTML,
        css=CSS,
        js=JS,
        isolate_styles=False,
    )
    return component(
        key=key,
        height=820,
        data={"enabled": enabled, "library_url": get_vendored_qr_library_url()},
        default={"status": {"kind": "idle", "code": "ready", "message": "Tap Start camera to begin scanning."}},
        on_status_change=lambda: None,
        on_scan_change=lambda: None,
    )
