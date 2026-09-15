// VideoCrew Flow Assistant - Content Script
// Ho tro giao tiep 2 chieu giua Website VideoCrew va tab Google Flow
// Copyright (c) 2026 Manes2008/didicrew

const isVideoCrewSite = !window.location.hostname.includes("flow.google.com");
const isGoogleFlow = window.location.hostname.includes("flow.google.com");

console.log("[VideoCrew Assistant] Content script khoi dong tren:", window.location.hostname);

// ==========================================
// 1. XU LY TREN WEBSITE VIDEOCREW
// ==========================================
if (isVideoCrewSite) {
  // Bao cho website biet extension da duoc cai dat
  window.postMessage({ type: "VIDEOCREW_EXTENSION_INSTALLED", version: "1.0.0" }, "*");

  // Lang nghe yeu cau day kich ban tu website
  window.addEventListener("message", (event) => {
    if (event.data && event.data.type === "VIDEOCREW_PUSH_TO_FLOW") {
      const payload = event.data.payload;
      const targetUrl = event.data.targetUrl;
      const autoVoice = event.data.autoVoice !== false;

      chrome.storage.local.set({
        flowQueue: payload,
        flowTargetUrl: targetUrl,
        flowAutoVoice: autoVoice,
        flowTimestamp: Date.now()
      }, () => {
        console.log("[VideoCrew Extension] Da luu payload vao chrome.storage.local thanh cong.");
      });
    }
  });
}

// ==========================================
// 2. XU LY TREN GOOGLE FLOW (DIRECTOR DOCK)
// ==========================================
if (isGoogleFlow) {
  let activePayload = null;
  let isDockMinimized = false;

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  // Tao giao dien Floating Director Dock tren Google Flow
  function initDirectorDock() {
    let dock = document.getElementById("videocrew-director-dock");
    if (dock) return dock;

    dock = document.createElement("div");
    dock.id = "videocrew-director-dock";
    dock.style.position = "fixed";
    dock.style.bottom = "20px";
    dock.style.right = "20px";
    dock.style.width = "380px";
    dock.style.maxHeight = "85vh";
    dock.style.zIndex = "999999";
    dock.style.backgroundColor = "rgba(10, 10, 15, 0.96)";
    dock.style.backdropFilter = "blur(12px)";
    dock.style.border = "1px solid rgba(6, 182, 212, 0.4)";
    dock.style.borderRadius = "16px";
    dock.style.boxShadow = "0 12px 40px rgba(0, 0, 0, 0.6), 0 0 20px rgba(6, 182, 212, 0.2)";
    dock.style.color = "#f4f4f5";
    dock.style.fontFamily = "system-ui, -apple-system, sans-serif";
    dock.style.fontSize = "12px";
    dock.style.display = "flex";
    dock.style.flexDirection = "column";
    dock.style.overflow = "hidden";
    dock.style.transition = "all 0.3s cubic-bezier(0.16, 1, 0.3, 1)";

    document.body.appendChild(dock);
    renderDockContent(dock);
    return dock;
  }

  function renderDockContent(dock) {
    if (isDockMinimized) {
      dock.style.width = "auto";
      dock.style.height = "auto";
      dock.innerHTML = `
        <div id="vc-btn-expand" style="padding: 10px 16px; cursor: pointer; display: flex; align-items: center; gap: 8px; font-weight: bold; color: #06b6d4;">
          <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#06b6d4;"></span>
          VideoCrew Director (${(activePayload?.veo_blocks?.length || activePayload?.scenes?.length || 0)} Scenes)
        </div>
      `;
      document.getElementById("vc-btn-expand").onclick = () => {
        isDockMinimized = false;
        renderDockContent(dock);
      };
      return;
    }

    dock.style.width = "380px";
    dock.style.height = "auto";

    const totalScenes = activePayload?.veo_blocks?.length || activePayload?.scenes?.length || 0;
    const totalChars = activePayload?.characters?.length || 0;
    const voiceName = activePayload?.suggested_voice || "Alnilam / Charon";

    dock.innerHTML = `
      <div style="padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: space-between; background: rgba(6, 182, 212, 0.08);">
        <div>
          <div style="font-weight: 700; color: #ffffff; font-size: 13px; display: flex; align-items: center; gap: 6px;">
            VideoCrew Flow Director
            <span style="font-size: 9px; padding: 2px 6px; border-radius: 4px; background: rgba(6,182,212,0.2); color: #22d3ee; border: 1px solid rgba(6,182,212,0.3);">READY</span>
          </div>
          <div style="font-size: 10px; color: #a1a1aa; margin-top: 2px;">
            ${totalScenes} phan canh | ${totalChars} nhan vat | Giong: ${voiceName}
          </div>
        </div>
        <div style="display: flex; gap: 6px;">
          <button id="vc-btn-minimize" style="background: transparent; border: none; color: #a1a1aa; cursor: pointer; font-size: 14px; padding: 4px;">_</button>
          <button id="vc-btn-close" style="background: transparent; border: none; color: #a1a1aa; cursor: pointer; font-size: 14px; padding: 4px;">x</button>
        </div>
      </div>

      <div id="vc-status-banner" style="padding: 8px 16px; background: rgba(0,0,0,0.4); border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 11px; color: #38bdf8;">
        San sang dong bo voi du an Flow hien tai.
      </div>

      <div style="display: flex; border-bottom: 1px solid rgba(255,255,255,0.1); background: rgba(0,0,0,0.2);">
        <button id="vc-tab-scenes" style="flex: 1; padding: 8px; background: transparent; border: none; border-bottom: 2px solid #06b6d4; color: #ffffff; font-weight: 600; cursor: pointer;">Phan Canh (${totalScenes})</button>
        <button id="vc-tab-chars" style="flex: 1; padding: 8px; background: transparent; border: none; color: #a1a1aa; font-weight: 600; cursor: pointer;">Nhan Vat (${totalChars})</button>
      </div>

      <div id="vc-body-content" style="flex: 1; overflow-y: auto; max-height: 380px; padding: 12px; display: flex; flex-direction: column; gap: 8px;">
        <!-- Danh sach items render o day -->
      </div>

      <div style="padding: 12px 16px; border-top: 1px solid rgba(255,255,255,0.1); background: rgba(0,0,0,0.4); display: flex; flex-direction: column; gap: 8px;">
        <div style="display: flex; gap: 8px;">
          <button id="vc-btn-paste-clip" style="flex: 1; padding: 7px; border-radius: 8px; background: #27272a; border: 1px solid #3f3f46; color: #e4e4e7; font-size: 11px; font-weight: 600; cursor: pointer;">
            Doc Tu Clipboard
          </button>
          <button id="vc-btn-fill-all" style="flex: 1.5; padding: 7px; border-radius: 8px; background: linear-gradient(135deg, #0284c7, #2563eb); border: none; color: #ffffff; font-size: 11px; font-weight: 700; cursor: pointer; box-shadow: 0 4px 12px rgba(37,99,235,0.3);">
            Dien Tu Dong Tat Ca
          </button>
        </div>
      </div>
    `;

    document.getElementById("vc-btn-minimize").onclick = () => {
      isDockMinimized = true;
      renderDockContent(dock);
    };
    document.getElementById("vc-btn-close").onclick = () => {
      dock.style.display = "none";
    };
    document.getElementById("vc-btn-paste-clip").onclick = handlePasteFromClipboard;
    document.getElementById("vc-btn-fill-all").onclick = () => handleFillAll(activePayload);

    renderScenesList();

    document.getElementById("vc-tab-scenes").onclick = (e) => {
      e.target.style.borderBottom = "2px solid #06b6d4";
      e.target.style.color = "#ffffff";
      const charTab = document.getElementById("vc-tab-chars");
      charTab.style.borderBottom = "none";
      charTab.style.color = "#a1a1aa";
      renderScenesList();
    };

    document.getElementById("vc-tab-chars").onclick = (e) => {
      e.target.style.borderBottom = "2px solid #06b6d4";
      e.target.style.color = "#ffffff";
      const sceneTab = document.getElementById("vc-tab-scenes");
      sceneTab.style.borderBottom = "none";
      sceneTab.style.color = "#a1a1aa";
      renderCharsList();
    };
  }

  function setStatus(text, isError = false) {
    const el = document.getElementById("vc-status-banner");
    if (el) {
      el.innerText = text;
      el.style.color = isError ? "#f87171" : "#38bdf8";
    }
  }

  // Render danh sach phan canh
  function renderScenesList() {
    const container = document.getElementById("vc-body-content");
    if (!container) return;
    const items = activePayload?.veo_blocks || activePayload?.scenes || [];

    if (items.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 24px 12px; color: #71717a; font-size: 11px;">
          Chua co du lieu phan canh.<br>
          Bam <strong>"Doc Tu Clipboard"</strong> neu ban da sao chep tu website VideoCrew.
        </div>
      `;
      return;
    }

    container.innerHTML = items.map((item, idx) => {
      const pText = item.visual_prompt || "";
      const voText = item.voiceover_clean || "";
      const num = item.block_num || item.scene_num || idx + 1;
      return `
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 10px; display: flex; flex-direction: column; gap: 6px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: 700; color: #22d3ee; font-size: 11px;">Phan canh #${num}</span>
            <div style="display: flex; gap: 4px;">
              <button class="vc-copy-prompt" data-text="${encodeURIComponent(pText)}" style="padding: 2px 6px; font-size: 10px; background: #27272a; border: 1px solid #3f3f46; color: #a1a1aa; border-radius: 4px; cursor: pointer;">Copy</button>
              <button class="vc-fill-single" data-prompt="${encodeURIComponent(pText)}" data-vo="${encodeURIComponent(voText)}" style="padding: 2px 8px; font-size: 10px; background: rgba(6,182,212,0.2); border: 1px solid rgba(6,182,212,0.4); color: #67e8f9; border-radius: 4px; cursor: pointer; font-weight: 600;">Dien vao Flow</button>
            </div>
          </div>
          <div style="font-size: 11px; color: #d4d4d8; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
            ${pText || "Khong co visual prompt"}
          </div>
          ${voText ? `
            <div style="font-size: 10px; color: #fbbf24; background: rgba(0,0,0,0.3); padding: 4px 6px; border-radius: 6px; border-left: 2px solid #f59e0b;">
              <strong>Thoai:</strong> ${voText.substring(0, 70)}...
            </div>
          ` : ""}
        </div>
      `;
    }).join("");

    container.querySelectorAll(".vc-copy-prompt").forEach(btn => {
      btn.onclick = () => {
        const text = decodeURIComponent(btn.getAttribute("data-text"));
        navigator.clipboard.writeText(text);
        setStatus("Da copy prompt phan canh vao clipboard!");
      };
    });

    container.querySelectorAll(".vc-fill-single").forEach(btn => {
      btn.onclick = async () => {
        const prompt = decodeURIComponent(btn.getAttribute("data-prompt"));
        const vo = decodeURIComponent(btn.getAttribute("data-vo"));
        setStatus("Dang dien phan canh vao o tao video...");
        const ok = await injectTextIntoFlow(prompt);
        if (ok) {
          setStatus("Da dien thanh cong prompt vao Flow!");
        } else {
          setStatus("Khong tim thay o nhap prompt tren Flow!", true);
        }
      };
    });
  }

  // Render danh sach nhan vat
  function renderCharsList() {
    const container = document.getElementById("vc-body-content");
    if (!container) return;
    const chars = activePayload?.characters || [];

    if (chars.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 24px 12px; color: #71717a; font-size: 11px;">
          Chua co nhan vat nao duoc trich xuat tu kich ban.<br>
          Kich ban can co muc "Nhan vat: ..." hoac "Character Consistency".
        </div>
      `;
      return;
    }

    container.innerHTML = chars.map((c, idx) => {
      const prompt = c.flow_prompt || `${c.name}: ${c.description}`;
      return `
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 10px; display: flex; flex-direction: column; gap: 6px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: 700; color: #a78bfa; font-size: 11px;">${c.name}</span>
            <div style="display: flex; gap: 4px;">
              <button class="vc-copy-char" data-text="${encodeURIComponent(prompt)}" style="padding: 2px 6px; font-size: 10px; background: #27272a; border: 1px solid #3f3f46; color: #a1a1aa; border-radius: 4px; cursor: pointer;">Copy</button>
              <button class="vc-fill-char" data-text="${encodeURIComponent(prompt)}" style="padding: 2px 8px; font-size: 10px; background: rgba(167,139,250,0.2); border: 1px solid rgba(167,139,250,0.4); color: #c4b5fd; border-radius: 4px; cursor: pointer; font-weight: 600;">Dien Nhan Vat</button>
            </div>
          </div>
          <div style="font-size: 11px; color: #d4d4d8; line-height: 1.4;">
            ${c.description}
          </div>
        </div>
      `;
    }).join("");

    container.querySelectorAll(".vc-copy-char").forEach(btn => {
      btn.onclick = () => {
        const text = decodeURIComponent(btn.getAttribute("data-text"));
        navigator.clipboard.writeText(text);
        setStatus("Da copy mo ta nhan vat!");
      };
    });

    container.querySelectorAll(".vc-fill-char").forEach(btn => {
      btn.onclick = async () => {
        const text = decodeURIComponent(btn.getAttribute("data-text"));
        setStatus("Dang dien nhan vat vao o prompt...");
        const ok = await injectTextIntoFlow(text);
        if (ok) {
          setStatus("Da dien thong tin nhan vat vao Flow!");
        } else {
          setStatus("Khong tim thay o nhap prompt!", true);
        }
      };
    });
  }

  // Ham tim kiem o nhap va dien noi dung tren Google Flow
  async function injectTextIntoFlow(text) {
    const selectors = [
      "textarea",
      "div[contenteditable='true']",
      "input[type='text']:not([aria-hidden='true'])",
      "[placeholder*='tạo gì' i]",
      "[placeholder*='create' i]",
      "[placeholder*='prompt' i]",
      "[aria-label*='prompt' i]",
      "[aria-label*='câu lệnh' i]"
    ];

    let targetEl = null;
    for (const s of selectors) {
      const candidates = Array.from(document.querySelectorAll(s));
      for (const el of candidates) {
        if (el.offsetParent !== null && !el.closest("#videocrew-director-dock")) {
          targetEl = el;
          break;
        }
      }
      if (targetEl) break;
    }

    if (!targetEl) {
      console.warn("[VideoCrew] Khong tim thay o nhap tren Flow DOM");
      return false;
    }

    targetEl.focus();
    targetEl.click();
    await sleep(200);

    if (targetEl.tagName === "DIV" && targetEl.isContentEditable) {
      targetEl.innerText = text;
    } else {
      targetEl.value = text;
    }

    targetEl.dispatchEvent(new Event("input", { bubbles: true }));
    targetEl.dispatchEvent(new Event("change", { bubbles: true }));
    await sleep(300);

    // Kich hoat go Enter de Flow tiep nhan
    targetEl.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", keyCode: 13, code: "Enter", which: 13, bubbles: true }));
    targetEl.dispatchEvent(new KeyboardEvent("keyup", { key: "Enter", keyCode: 13, code: "Enter", which: 13, bubbles: true }));

    return true;
  }

  // Doc payload tu Clipboard
  async function handlePasteFromClipboard() {
    try {
      const text = await navigator.clipboard.readText();
      const parsed = JSON.parse(text);
      if (parsed && (parsed.veo_blocks || parsed.scenes)) {
        activePayload = parsed;
        chrome.storage.local.set({ flowQueue: parsed });
        setStatus(`Da nhan thanh cong ${(parsed.veo_blocks?.length || parsed.scenes?.length || 0)} phan canh tu Clipboard!`);
        renderDockContent(document.getElementById("videocrew-director-dock"));
      } else {
        setStatus("Clipboard khong chua dinh dang JSON VideoCrew hop le.", true);
      }
    } catch (e) {
      setStatus("Vui long cap quyen doc Clipboard tren trinh duyet.", true);
    }
  }

  // Dien tu dong toan bo phan canh
  async function handleFillAll(payload) {
    const items = payload?.veo_blocks || payload?.scenes || [];
    if (items.length === 0) {
      setStatus("Chua co phan canh de dien.", true);
      return;
    }

    setStatus(`Bat dau dien tu dong ${items.length} phan canh...`);
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      const pText = item.visual_prompt || "";
      if (pText) {
        setStatus(`Dang dien phan canh ${i + 1}/${items.length}...`);
        await injectTextIntoFlow(pText);
        await sleep(3000);
      }
    }
    setStatus(`Hoan tat dien ${items.length} phan canh vao Flow!`);
  }

  // Kiem tra du lieu luu trong chrome.storage.local khi load tab Flow
  chrome.storage.local.get(["flowQueue"], (res) => {
    if (res.flowQueue) {
      activePayload = res.flowQueue;
      console.log("[VideoCrew] Da nhan flowQueue tu storage:", activePayload);
    }
    initDirectorDock();
  });

  // Lang nghe tin nhan truc tiep tu background hoac popup
  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === "START_INJECTION" && msg.payload) {
      activePayload = msg.payload;
      initDirectorDock();
      handleFillAll(msg.payload);
      sendResponse({ status: "STARTED" });
      return true;
    }
  });
}
