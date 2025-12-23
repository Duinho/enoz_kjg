(() => {
  // src/background.js
  async function updateIcon(enabled) {
    try {
      const suffix = enabled ? "" : "_disabled";
      await chrome.action.setIcon({
        path: {
          "19": `assets/icons/icon19${suffix}.png`,
          "38": `assets/icons/icon38${suffix}.png`,
          "48": `assets/icons/icon48${suffix}.png`
        }
      });
      console.log(`Icon updated: ${enabled ? "enabled" : "disabled"}`);
    } catch (error) {
      console.error("Failed to update icon:", error);
    }
  }
  async function initializeIcon() {
    try {
      const storage = await chrome.storage.sync.get({ enabled: true });
      await updateIcon(storage.enabled);
    } catch (error) {
      console.error("Failed to initialize icon:", error);
      await updateIcon(true);
    }
  }
  chrome.storage.onChanged.addListener((changes, namespace) => {
    if (namespace === "sync" && changes.enabled) {
      updateIcon(changes.enabled.newValue !== false);
    }
  });
  chrome.runtime.onMessage.addListener((message, sender) => {
    if (message.type === "EXTENSION_TOGGLE") {
      updateIcon(message.enabled);
    }
  });
  chrome.runtime.onInstalled.addListener(async () => {
    console.log("Video Speed Controller installed/updated");
    await initializeIcon();
  });
  chrome.runtime.onStartup.addListener(async () => {
    console.log("Video Speed Controller started");
    await initializeIcon();
  });
  initializeIcon();
  console.log("Video Speed Controller background script loaded");
})();
