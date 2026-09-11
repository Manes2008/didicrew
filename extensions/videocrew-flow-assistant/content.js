// VideoCrew Flow Assistant - Content Script for flow.google.com
// Copyright (c) 2026 Manes2008/didicrew

console.log("[VideoCrew Extension] Content Script da khoi chay tren Google Flow.");

// Tao thanh tien trinh noi tren giao dien Google Flow
function createFloatingStatus() {
  let el = document.getElementById("videocrew-floating-badge");
  if (!el) {
    el = document.createElement("div");
    el.id = "videocrew-floating-badge";
    el.style.position = "fixed";
    el.style.bottom = "24px";
    el.style.right = "24px";
    el.style.zIndex = "999999";
    el.style.padding = "12px 18px";
    el.style.borderRadius = "14px";
    el.style.background = "rgba(10, 10, 15, 0.95)";
    el.style.border = "1px solid #06b6d4";
    el.style.boxShadow = "0 10px 30px rgba(6, 182, 212, 0.3)";
    el.style.color = "#ffffff";
    el.style.fontFamily = "system-ui, -apple-system, sans-serif";
    el.style.fontSize = "12px";
    el.style.fontWeight = "600";
    el.style.display = "none";
    el.style.transition = "all 0.3s ease";
    document.body.appendChild(el);
  }
  return el;
}

function updateFloatingStatus(text, isError = false) {
  const badge = createFloatingStatus();
  badge.style.display = "block";
  badge.style.borderColor = isError ? "#ef4444" : "#06b6d4";
  badge.innerHTML = `
    <div style="display:flex;align-items:center;gap:10px;">
      <div style="width:8px;height:8px;border-radius:50%;background:${isError ? '#ef4444' : '#06b6d4'};"></div>
      <div>
        <div style="font-size:10px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px;">VideoCrew Assistant</div>
        <div style="color:#ffffff;">${text}</div>
      </div>
    </div>
  `;
}

// Ham delay giua cac buoc thao tac
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Dien prompt vao o tao video
async function injectVideoPrompt(promptText) {
  updateFloatingStatus(`Dang nap Veo Prompt: ${promptText.substring(0, 30)}...`);
  
  const selectors = [
    "textarea",
    "input[type='text']",
    "div[contenteditable='true']",
    "[placeholder*='Bạn muốn tạo gì']",
    "[placeholder*='What do you want to create']"
  ];

  let inputEl = null;
  for (const s of selectors) {
    inputEl = document.querySelector(s);
    if (inputEl) break;
  }

  if (!inputEl) {
    console.warn("[VideoCrew] Khong tim thay o nhap prompt");
    return false;
  }

  inputEl.focus();
  inputEl.click();
  await sleep(300);

  if (inputEl.tagName === "DIV" && inputEl.isContentEditable) {
    inputEl.innerText = promptText;
  } else {
    inputEl.value = promptText;
  }

  inputEl.dispatchEvent(new Event("input", { bubbles: true }));
  inputEl.dispatchEvent(new Event("change", { bubbles: true }));
  await sleep(500);

  // Nhan Enter
  inputEl.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", keyCode: 13, code: "Enter", which: 13, bubbles: true }));
  inputEl.dispatchEvent(new KeyboardEvent("keyup", { key: "Enter", keyCode: 13, code: "Enter", which: 13, bubbles: true }));

  await sleep(2500);
  return true;
}

// Dien thoai vao Voiceover Studio
async function injectVoiceover(text, voiceName) {
  updateFloatingStatus(`Dang nap Voiceover (${voiceName}): ${text.substring(0, 25)}...`);

  // 1. Tim nut mo Giong noi
  const buttons = Array.from(document.querySelectorAll("button, div, span"));
  const voiceBtn = buttons.find((b) => b.innerText && (b.innerText.includes("Giọng nói") || b.innerText.includes("Voiceover")));
  if (voiceBtn) {
    voiceBtn.click();
    await sleep(1000);
  }

  // 2. Chon giong doc neu co
  if (voiceName) {
    const allVoiceLabels = Array.from(document.querySelectorAll("*"));
    const vTarget = allVoiceLabels.find((el) => el.innerText && el.innerText.trim() === voiceName);
    if (vTarget) {
      vTarget.click();
      await sleep(500);
    }
  }

  // 3. Tim o dien thoai mau
  const textareas = document.querySelectorAll("textarea, div[contenteditable='true']");
  if (textareas.length > 0) {
    const area = textareas[textareas.length - 1];
    area.focus();
    area.click();
    if (area.tagName === "DIV" && area.isContentEditable) {
      area.innerText = text.substring(0, 120);
    } else {
      area.value = text.substring(0, 120);
    }
    area.dispatchEvent(new Event("input", { bubbles: true }));
    await sleep(500);

    // Click nut Them vao cau lenh
    const addButtons = Array.from(document.querySelectorAll("button"));
    const submitBtn = addButtons.find((b) => b.innerText && (b.innerText.includes("Thêm vào câu lệnh") || b.innerText.includes("Tạo")));
    if (submitBtn) {
      submitBtn.click();
      await sleep(1500);
    }
  }
}

// Chay tien trinh nạp hang loat
async function runBatchInjection(payload, autoVoice) {
  const items = payload.veo_blocks || payload.scenes || [];
  const defaultVoice = payload.suggested_voice || "Charon";
  const total = items.length;

  if (total === 0) {
    updateFloatingStatus("Khong co phan canh nao can nap.", true);
    return;
  }

  for (let i = 0; i < total; i++) {
    const item = items[i];
    const pText = item.visual_prompt || "";
    const voText = item.voiceover_clean || "";
    const vName = item.suggested_voice || defaultVoice;

    updateFloatingStatus(`Dang xu ly phan canh ${i + 1}/${total}...`);

    if (pText) {
      await injectVideoPrompt(pText);
      await sleep(1500);
    }

    if (autoVoice && voText) {
      const chunks = item.voiceover_chunks || [voText.substring(0, 120)];
      for (const c of chunks) {
        await injectVoiceover(c, vName);
        await sleep(1000);
      }
    }
  }

  updateFloatingStatus(`Hoan tat! Da nap thanh cong ${total} phan canh.`);
  setTimeout(() => {
    const badge = document.getElementById("videocrew-floating-badge");
    if (badge) badge.style.display = "none";
  }, 8000);
}

// Lang nghe tin nhan tu Background
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "START_INJECTION") {
    runBatchInjection(request.payload, request.autoVoice);
    sendResponse({ status: "STARTED" });
    return true;
  }
});

// Kiem tra hang doi luu tru khi load trang
chrome.storage.local.get(["flowQueue", "flowAutoVoice"], (res) => {
  if (res.flowQueue) {
    const queue = res.flowQueue;
    const autoV = res.flowAutoVoice;
    chrome.storage.local.remove(["flowQueue"]);
    setTimeout(() => {
      runBatchInjection(queue, autoV);
    }, 4000);
  }
});
