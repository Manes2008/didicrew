// VideoCrew Flow Assistant - Background Service Worker
// Copyright (c) 2026 Manes2008/didicrew

chrome.runtime.onInstalled.addListener(() => {
  console.log("[VideoCrew Extension] Da cai dat thanh cong.");
});

// Lang nghe tin nhan truc tiep tu website VideoCrew
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
  if (request.type === "PING") {
    sendResponse({ status: "OK", version: "1.0.0", message: "VideoCrew Extension da san sang!" });
    return true;
  }

  if (request.type === "PUSH_TO_FLOW") {
    const payload = request.payload;
    const targetUrl = request.targetUrl || "https://flow.google.com";
    const autoVoice = request.autoVoice !== false;

    // Luu vao storage de content script doc duoc
    chrome.storage.local.set({
      flowQueue: payload,
      flowTargetUrl: targetUrl,
      flowAutoVoice: autoVoice,
      flowStatus: "QUEUED",
      flowIndex: 0
    }, () => {
      // Tim tab flow.google.com dang mo hoac tao tab moi
      chrome.tabs.query({ url: "*://flow.google.com/*" }, (tabs) => {
        if (tabs && tabs.length > 0) {
          const tab = tabs[0];
          chrome.tabs.update(tab.id, { active: true });
          if (targetUrl && !tab.url.includes(targetUrl.split("/project/")[1] || "none")) {
            chrome.tabs.update(tab.id, { url: targetUrl });
          }
          // Gui tin nhan bat dau sang content script
          setTimeout(() => {
            chrome.tabs.sendMessage(tab.id, { type: "START_INJECTION", payload, autoVoice });
          }, 3000);
        } else {
          chrome.tabs.create({ url: targetUrl }, (newTab) => {
            setTimeout(() => {
              chrome.tabs.sendMessage(newTab.id, { type: "START_INJECTION", payload, autoVoice });
            }, 5000);
          });
        }
      });
      sendResponse({ status: "SUCCESS", message: "Da chuyen tiep kich ban sang Google Flow tab!" });
    });
    return true;
  }
});

// Lang nghe tin nhan noi bo tu content script hoac popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "UPDATE_PROGRESS") {
    chrome.storage.local.set({
      flowProgress: request.progress,
      flowStatus: request.status
    });
    sendResponse({ status: "OK" });
    return true;
  }
});
