(() => {
  // src/content/injection-bridge.js
  async function injectScript(scriptPath) {
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = chrome.runtime.getURL(scriptPath);
      script.onload = () => {
        script.remove();
        resolve();
      };
      script.onerror = () => {
        script.remove();
        reject(new Error(`Failed to load script: ${scriptPath}`));
      };
      (document.head || document.documentElement).appendChild(script);
    });
  }
  function setupMessageBridge() {
    window.addEventListener("message", (event) => {
      if (event.source !== window || !event.data?.source?.startsWith("vsc-")) {
        return;
      }
      const { source, action, data } = event.data;
      if (source === "vsc-page") {
        if (action === "storage-update") {
          chrome.storage.sync.set(data);
        } else if (action === "runtime-message") {
          if (data.type !== "VSC_STATE_UPDATE") {
            chrome.runtime.sendMessage(data);
          }
        } else if (action === "get-storage") {
          chrome.storage.sync.get(null, (items) => {
            window.postMessage({
              source: "vsc-content",
              action: "storage-data",
              data: items
            }, "*");
          });
        }
      }
    });
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      window.dispatchEvent(
        new CustomEvent("VSC_MESSAGE", {
          detail: request
        })
      );
      if (request.action === "get-status") {
        const responseHandler = (event) => {
          if (event.data?.source === "vsc-page" && event.data?.action === "status-response") {
            window.removeEventListener("message", responseHandler);
            sendResponse(event.data.data);
          }
        };
        window.addEventListener("message", responseHandler);
        return true;
      }
    });
    chrome.storage.onChanged.addListener((changes, namespace) => {
      if (namespace === "sync") {
        const changedData = {};
        for (const [key, { newValue }] of Object.entries(changes)) {
          changedData[key] = newValue;
        }
        window.postMessage({
          source: "vsc-content",
          action: "storage-changed",
          data: changedData
        }, "*");
      }
    });
  }

  // src/entries/content-entry.js
  async function init() {
    try {
      const settings = await chrome.storage.sync.get(null);
      const settingsElement = document.createElement("script");
      settingsElement.id = "vsc-settings-data";
      settingsElement.type = "application/json";
      settingsElement.textContent = JSON.stringify(settings);
      (document.head || document.documentElement).appendChild(settingsElement);
      await injectScript("inject.js");
      setupMessageBridge();
      console.debug("[VSC] Content script initialized");
    } catch (error) {
      console.error("[VSC] Failed to initialize:", error);
    }
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
