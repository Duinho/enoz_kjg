(() => {
  // src/utils/constants.js
  window.VSC = window.VSC || {};
  window.VSC.Constants = {};
  if (!window.VSC.Constants.DEFAULT_SETTINGS) {
    const regStrip = /^[\r\t\f\v ]+|[\r\t\f\v ]+$/gm;
    const regEndsWithFlags = /\/(?!.*(.).*\1)[gimsuy]*$/;
    window.VSC.Constants.regStrip = regStrip;
    window.VSC.Constants.regEndsWithFlags = regEndsWithFlags;
    const DEFAULT_SETTINGS = {
      lastSpeed: 1,
      // default 1x
      enabled: true,
      // default enabled
      displayKeyCode: 86,
      // default: V
      rememberSpeed: false,
      // default: false
      forceLastSavedSpeed: false,
      //default: false
      audioBoolean: true,
      // default: true (enable audio controller support)
      startHidden: false,
      // default: false
      controllerOpacity: 0.3,
      // default: 0.3
      controllerButtonSize: 14,
      keyBindings: [
        { action: "slower", key: 83, value: 0.1, force: false, predefined: true },
        // S
        { action: "faster", key: 68, value: 0.1, force: false, predefined: true },
        // D
        { action: "rewind", key: 90, value: 10, force: false, predefined: true },
        // Z
        { action: "advance", key: 88, value: 10, force: false, predefined: true },
        // X
        { action: "reset", key: 82, value: 1, force: false, predefined: true },
        // R
        { action: "fast", key: 71, value: 1.8, force: false, predefined: true },
        // G
        { action: "display", key: 86, value: 0, force: false, predefined: true },
        // V
        { action: "mark", key: 77, value: 0, force: false, predefined: true },
        // M
        { action: "jump", key: 74, value: 0, force: false, predefined: true }
        // J
      ],
      blacklist: `www.instagram.com
x.com
imgur.com
teams.microsoft.com
meet.google.com`.replace(regStrip, ""),
      defaultLogLevel: 4,
      logLevel: 3
    };
    window.VSC.Constants.DEFAULT_SETTINGS = DEFAULT_SETTINGS;
    const formatSpeed = (speed) => speed.toFixed(2);
    window.VSC.Constants.formatSpeed = formatSpeed;
    const LOG_LEVELS = {
      NONE: 1,
      ERROR: 2,
      WARNING: 3,
      INFO: 4,
      DEBUG: 5,
      VERBOSE: 6
    };
    const MESSAGE_TYPES = {
      SET_SPEED: "VSC_SET_SPEED",
      ADJUST_SPEED: "VSC_ADJUST_SPEED",
      RESET_SPEED: "VSC_RESET_SPEED",
      TOGGLE_DISPLAY: "VSC_TOGGLE_DISPLAY"
    };
    const SPEED_LIMITS = {
      MIN: 0.07,
      // Video min rate per Chromium source
      MAX: 16
      // Maximum playback speed in Chrome per Chromium source
    };
    const CONTROLLER_SIZE_LIMITS = {
      // Video elements: minimum size before rejecting controller entirely
      VIDEO_MIN_WIDTH: 40,
      VIDEO_MIN_HEIGHT: 40,
      // Audio elements: minimum size before starting controller hidden
      AUDIO_MIN_WIDTH: 20,
      AUDIO_MIN_HEIGHT: 20
    };
    const CUSTOM_ACTIONS_NO_VALUES = ["pause", "muted", "mark", "jump", "display"];
    window.VSC.Constants.LOG_LEVELS = LOG_LEVELS;
    window.VSC.Constants.MESSAGE_TYPES = MESSAGE_TYPES;
    window.VSC.Constants.SPEED_LIMITS = SPEED_LIMITS;
    window.VSC.Constants.CONTROLLER_SIZE_LIMITS = CONTROLLER_SIZE_LIMITS;
    window.VSC.Constants.CUSTOM_ACTIONS_NO_VALUES = CUSTOM_ACTIONS_NO_VALUES;
  }

  // src/utils/logger.js
  window.VSC = window.VSC || {};
  if (!window.VSC.logger) {
    class Logger {
      constructor() {
        this.verbosity = 3;
        this.defaultLevel = 4;
        this.contextStack = [];
      }
      /**
       * Set logging verbosity level
       * @param {number} level - Log level from LOG_LEVELS constants
       */
      setVerbosity(level) {
        this.verbosity = level;
      }
      /**
       * Set default logging level
       * @param {number} level - Default level from LOG_LEVELS constants
       */
      setDefaultLevel(level) {
        this.defaultLevel = level;
      }
      /**
       * Generate video/controller context string from context stack
       * @returns {string} Context string like "[V1]" or ""
       * @private
       */
      generateContext() {
        if (this.contextStack.length > 0) {
          return `[${this.contextStack[this.contextStack.length - 1]}] `;
        }
        return "";
      }
      /**
       * Format video element identifier using controller ID
       * @param {HTMLMediaElement} video - Video element
       * @returns {string} Formatted ID like "V1" or "A1"
       * @private
       */
      formatVideoId(video) {
        if (!video) return "V?";
        const isAudio = video.tagName === "AUDIO";
        const prefix = isAudio ? "A" : "V";
        if (video.vsc?.controllerId) {
          return `${prefix}${video.vsc.controllerId}`;
        }
        return `${prefix}?`;
      }
      /**
       * Push context onto stack (for nested operations)
       * @param {string|HTMLMediaElement} context - Context string or video element
       */
      pushContext(context) {
        if (typeof context === "string") {
          this.contextStack.push(context);
        } else if (context && (context.tagName === "VIDEO" || context.tagName === "AUDIO")) {
          this.contextStack.push(this.formatVideoId(context));
        }
      }
      /**
       * Pop context from stack
       */
      popContext() {
        this.contextStack.pop();
      }
      /**
       * Execute function with context
       * @param {string|HTMLMediaElement} context - Context string or video element
       * @param {Function} fn - Function to execute
       * @returns {*} Function result
       */
      withContext(context, fn) {
        this.pushContext(context);
        try {
          return fn();
        } finally {
          this.popContext();
        }
      }
      /**
       * Log a message with specified level
       * @param {string} message - Message to log
       * @param {number} level - Log level (optional, uses default if not specified)
       */
      log(message, level) {
        const logLevel = typeof level === "undefined" ? this.defaultLevel : level;
        const LOG_LEVELS = window.VSC.Constants.LOG_LEVELS;
        if (this.verbosity >= logLevel) {
          const context = this.generateContext();
          const contextualMessage = `${context}${message}`;
          switch (logLevel) {
            case LOG_LEVELS.ERROR:
              console.log(`ERROR:${contextualMessage}`);
              break;
            case LOG_LEVELS.WARNING:
              console.log(`WARNING:${contextualMessage}`);
              break;
            case LOG_LEVELS.INFO:
              console.log(`INFO:${contextualMessage}`);
              break;
            case LOG_LEVELS.DEBUG:
              console.log(`DEBUG:${contextualMessage}`);
              break;
            case LOG_LEVELS.VERBOSE:
              console.log(`DEBUG (VERBOSE):${contextualMessage}`);
              console.trace();
              break;
            default:
              console.log(contextualMessage);
          }
        }
      }
      /**
       * Log error message
       * @param {string} message - Error message
       */
      error(message) {
        this.log(message, window.VSC.Constants.LOG_LEVELS.ERROR);
      }
      /**
       * Log warning message
       * @param {string} message - Warning message
       */
      warn(message) {
        this.log(message, window.VSC.Constants.LOG_LEVELS.WARNING);
      }
      /**
       * Log info message
       * @param {string} message - Info message
       */
      info(message) {
        this.log(message, window.VSC.Constants.LOG_LEVELS.INFO);
      }
      /**
       * Log debug message
       * @param {string} message - Debug message
       */
      debug(message) {
        this.log(message, window.VSC.Constants.LOG_LEVELS.DEBUG);
      }
      /**
       * Log verbose debug message with stack trace
       * @param {string} message - Verbose debug message
       */
      verbose(message) {
        this.log(message, window.VSC.Constants.LOG_LEVELS.VERBOSE);
      }
    }
    window.VSC.logger = new Logger();
  }

  // src/core/storage-manager.js
  window.VSC = window.VSC || {};
  if (!window.VSC.StorageManager) {
    class StorageManager {
      static errorCallback = null;
      /**
       * Register error callback for monitoring storage failures
       * @param {Function} callback - Callback function for errors
       */
      static onError(callback) {
        this.errorCallback = callback;
      }
      /**
       * Get settings from Chrome storage or pre-injected settings
       * @param {Object} defaults - Default values
       * @returns {Promise<Object>} Storage data
       */
      static async get(defaults = {}) {
        if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.sync) {
          return new Promise((resolve) => {
            chrome.storage.sync.get(defaults, (storage) => {
              window.VSC.logger.debug("Retrieved settings from chrome.storage");
              resolve(storage);
            });
          });
        } else {
          if (!window.VSC_settings) {
            const settingsElement = document.getElementById("vsc-settings-data");
            if (settingsElement && settingsElement.textContent) {
              try {
                window.VSC_settings = JSON.parse(settingsElement.textContent);
                window.VSC.logger.debug("Loaded settings from script element");
                settingsElement.remove();
              } catch (e) {
                window.VSC.logger.error("Failed to parse settings from script element:", e);
              }
            }
          }
          if (window.VSC_settings) {
            window.VSC.logger.debug("Using VSC_settings");
            return Promise.resolve({ ...defaults, ...window.VSC_settings });
          } else {
            window.VSC.logger.debug("No settings available, using defaults");
            return Promise.resolve(defaults);
          }
        }
      }
      /**
       * Set settings in Chrome storage
       * @param {Object} data - Data to store
       * @returns {Promise<void>}
       */
      static async set(data) {
        if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.sync) {
          return new Promise((resolve, reject) => {
            chrome.storage.sync.set(data, () => {
              if (chrome.runtime.lastError) {
                const error = new Error(`Storage failed: ${chrome.runtime.lastError.message}`);
                console.error("Chrome storage save failed:", chrome.runtime.lastError);
                if (this.errorCallback) {
                  this.errorCallback(error, data);
                }
                reject(error);
                return;
              }
              window.VSC.logger.debug("Settings saved to chrome.storage");
              resolve();
            });
          });
        } else {
          window.VSC.logger.debug("Sending storage update to content script");
          window.postMessage({
            source: "vsc-page",
            action: "storage-update",
            data
          }, "*");
          window.VSC_settings = { ...window.VSC_settings, ...data };
          return Promise.resolve();
        }
      }
      /**
       * Remove keys from Chrome storage
       * @param {Array<string>} keys - Keys to remove
       * @returns {Promise<void>}
       */
      static async remove(keys) {
        if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.sync) {
          return new Promise((resolve, reject) => {
            chrome.storage.sync.remove(keys, () => {
              if (chrome.runtime.lastError) {
                const error = new Error(`Storage remove failed: ${chrome.runtime.lastError.message}`);
                console.error("Chrome storage remove failed:", chrome.runtime.lastError);
                if (this.errorCallback) {
                  this.errorCallback(error, { removedKeys: keys });
                }
                reject(error);
                return;
              }
              window.VSC.logger.debug("Keys removed from storage");
              resolve();
            });
          });
        } else {
          if (window.VSC_settings) {
            keys.forEach((key) => delete window.VSC_settings[key]);
          }
          return Promise.resolve();
        }
      }
      /**
       * Clear all Chrome storage
       * @returns {Promise<void>}
       */
      static async clear() {
        if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.sync) {
          return new Promise((resolve, reject) => {
            chrome.storage.sync.clear(() => {
              if (chrome.runtime.lastError) {
                const error = new Error(`Storage clear failed: ${chrome.runtime.lastError.message}`);
                console.error("Chrome storage clear failed:", chrome.runtime.lastError);
                if (this.errorCallback) {
                  this.errorCallback(error, { operation: "clear" });
                }
                reject(error);
                return;
              }
              window.VSC.logger.debug("Storage cleared");
              resolve();
            });
          });
        } else {
          window.VSC_settings = {};
          return Promise.resolve();
        }
      }
      /**
       * Listen for storage changes
       * @param {Function} callback - Callback function for changes
       */
      static onChanged(callback) {
        if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.onChanged) {
          chrome.storage.onChanged.addListener((changes, areaName) => {
            if (areaName === "sync") {
              callback(changes);
            }
          });
        } else {
          window.addEventListener("message", (event) => {
            if (event.data?.source === "vsc-content" && event.data?.action === "storage-changed") {
              const changes = {};
              for (const [key, value] of Object.entries(event.data.data)) {
                changes[key] = { newValue: value, oldValue: window.VSC_settings?.[key] };
              }
              window.VSC_settings = { ...window.VSC_settings, ...event.data.data };
              callback(changes);
            }
          });
        }
      }
    }
    window.VSC.StorageManager = StorageManager;
  }

  // src/core/settings.js
  window.VSC = window.VSC || {};
  if (!window.VSC.VideoSpeedConfig) {
    class VideoSpeedConfig {
      constructor() {
        this.settings = { ...window.VSC.Constants.DEFAULT_SETTINGS };
        this.pendingSave = null;
        this.saveTimer = null;
        this.SAVE_DELAY = 1e3;
      }
      /**
       * Load settings from Chrome storage or pre-injected settings
       * @returns {Promise<Object>} Loaded settings
       */
      async load() {
        try {
          const storage = await window.VSC.StorageManager.get(window.VSC.Constants.DEFAULT_SETTINGS);
          this.settings.keyBindings = storage.keyBindings || window.VSC.Constants.DEFAULT_SETTINGS.keyBindings;
          if (!storage.keyBindings || storage.keyBindings.length === 0) {
            window.VSC.logger.info("First initialization - setting up default key bindings");
            this.settings.keyBindings = [...window.VSC.Constants.DEFAULT_SETTINGS.keyBindings];
            await this.save({ keyBindings: this.settings.keyBindings });
          }
          this.settings.lastSpeed = Number(storage.lastSpeed);
          this.settings.displayKeyCode = Number(storage.displayKeyCode);
          this.settings.rememberSpeed = Boolean(storage.rememberSpeed);
          this.settings.forceLastSavedSpeed = Boolean(storage.forceLastSavedSpeed);
          this.settings.audioBoolean = Boolean(storage.audioBoolean);
          this.settings.enabled = Boolean(storage.enabled);
          this.settings.startHidden = Boolean(storage.startHidden);
          this.settings.controllerOpacity = Number(storage.controllerOpacity);
          this.settings.controllerButtonSize = Number(storage.controllerButtonSize);
          this.settings.blacklist = String(storage.blacklist);
          this.settings.logLevel = Number(
            storage.logLevel || window.VSC.Constants.DEFAULT_SETTINGS.logLevel
          );
          this.ensureDisplayBinding(storage);
          window.VSC.logger.setVerbosity(this.settings.logLevel);
          window.VSC.logger.info("Settings loaded successfully");
          return this.settings;
        } catch (error) {
          window.VSC.logger.error(`Failed to load settings: ${error.message}`);
          return window.VSC.Constants.DEFAULT_SETTINGS;
        }
      }
      /**
       * Save settings to Chrome storage
       * @param {Object} newSettings - Settings to save
       * @returns {Promise<void>}
       */
      async save(newSettings = {}) {
        try {
          this.settings = { ...this.settings, ...newSettings };
          const keys = Object.keys(newSettings);
          if (keys.length === 1 && keys[0] === "lastSpeed") {
            this.pendingSave = newSettings.lastSpeed;
            if (this.saveTimer) {
              clearTimeout(this.saveTimer);
            }
            this.saveTimer = setTimeout(async () => {
              const speedToSave = this.pendingSave;
              this.pendingSave = null;
              this.saveTimer = null;
              await window.VSC.StorageManager.set({ ...this.settings, lastSpeed: speedToSave });
              window.VSC.logger.info("Debounced speed setting saved successfully");
            }, this.SAVE_DELAY);
            return;
          }
          await window.VSC.StorageManager.set(this.settings);
          if (newSettings.logLevel !== void 0) {
            window.VSC.logger.setVerbosity(this.settings.logLevel);
          }
          window.VSC.logger.info("Settings saved successfully");
        } catch (error) {
          window.VSC.logger.error(`Failed to save settings: ${error.message}`);
        }
      }
      /**
       * Get a specific key binding
       * @param {string} action - Action name
       * @param {string} property - Property to get (default: 'value')
       * @returns {*} Key binding property value
       */
      getKeyBinding(action, property = "value") {
        try {
          const binding = this.settings.keyBindings.find((item) => item.action === action);
          return binding ? binding[property] : false;
        } catch (e) {
          window.VSC.logger.error(`Failed to get key binding for ${action}: ${e.message}`);
          return false;
        }
      }
      /**
       * Set a key binding value with validation
       * @param {string} action - Action name
       * @param {*} value - Value to set
       */
      setKeyBinding(action, value) {
        try {
          const binding = this.settings.keyBindings.find((item) => item.action === action);
          if (!binding) {
            window.VSC.logger.warn(`No key binding found for action: ${action}`);
            return;
          }
          if (["reset", "fast", "slower", "faster"].includes(action)) {
            if (typeof value !== "number" || isNaN(value)) {
              window.VSC.logger.warn(`Invalid numeric value for ${action}: ${value}`);
              return;
            }
          }
          binding.value = value;
          window.VSC.logger.debug(`Updated key binding ${action} to ${value}`);
        } catch (e) {
          window.VSC.logger.error(`Failed to set key binding for ${action}: ${e.message}`);
        }
      }
      /**
       * Ensure display binding exists in key bindings
       * @param {Object} storage - Storage object  
       * @private
       */
      ensureDisplayBinding(storage) {
        if (this.settings.keyBindings.filter((x) => x.action === "display").length === 0) {
          this.settings.keyBindings.push({
            action: "display",
            key: Number(storage.displayKeyCode) || 86,
            value: 0,
            force: false,
            predefined: true
          });
        }
      }
    }
    window.VSC.videoSpeedConfig = new VideoSpeedConfig();
    window.VSC.VideoSpeedConfig = VideoSpeedConfig;
  }

  // src/ui/options/options.js
  window.VSC = window.VSC || {};
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
  var keyBindings = [];
  var BLACKLISTED_KEYCODES = [
    9,
    // Tab - needed for keyboard navigation
    16,
    // Shift (alone)
    17,
    // Ctrl/Control (alone)
    18,
    // Alt (alone)
    91,
    // Meta/Windows/Command Left
    92,
    // Meta/Windows Right
    93,
    // Context Menu/Right Command
    224
    // Meta/Command (Firefox)
  ];
  var keyCodeAliases = {
    0: "null",
    null: "null",
    undefined: "null",
    32: "Space",
    37: "Left",
    38: "Up",
    39: "Right",
    40: "Down",
    96: "Num 0",
    97: "Num 1",
    98: "Num 2",
    99: "Num 3",
    100: "Num 4",
    101: "Num 5",
    102: "Num 6",
    103: "Num 7",
    104: "Num 8",
    105: "Num 9",
    106: "Num *",
    107: "Num +",
    109: "Num -",
    110: "Num .",
    111: "Num /",
    112: "F1",
    113: "F2",
    114: "F3",
    115: "F4",
    116: "F5",
    117: "F6",
    118: "F7",
    119: "F8",
    120: "F9",
    121: "F10",
    122: "F11",
    123: "F12",
    124: "F13",
    125: "F14",
    126: "F15",
    127: "F16",
    128: "F17",
    129: "F18",
    130: "F19",
    131: "F20",
    132: "F21",
    133: "F22",
    134: "F23",
    135: "F24",
    186: ";",
    188: "<",
    189: "-",
    187: "+",
    190: ">",
    191: "/",
    192: "~",
    219: "[",
    220: "\\",
    221: "]",
    222: "'"
  };
  function recordKeyPress(e) {
    if (e.keyCode === 8) {
      e.target.value = "";
      e.preventDefault();
      e.stopPropagation();
      return;
    } else if (e.keyCode === 27) {
      e.target.value = "null";
      e.target.keyCode = null;
      e.preventDefault();
      e.stopPropagation();
      return;
    }
    if (BLACKLISTED_KEYCODES.includes(e.keyCode)) {
      e.preventDefault();
      e.stopPropagation();
      return;
    }
    e.target.value = keyCodeAliases[e.keyCode] || (e.keyCode >= 48 && e.keyCode <= 90 ? String.fromCharCode(e.keyCode) : `Key ${e.keyCode}`);
    e.target.keyCode = e.keyCode;
    e.preventDefault();
    e.stopPropagation();
  }
  function inputFilterNumbersOnly(e) {
    var char = String.fromCharCode(e.keyCode);
    if (!/[\d\.]$/.test(char) || !/^\d+(\.\d*)?$/.test(e.target.value + char)) {
      e.preventDefault();
      e.stopPropagation();
    }
  }
  function inputFocus(e) {
    e.target.value = "";
  }
  function inputBlur(e) {
    const keyCode = e.target.keyCode;
    e.target.value = keyCodeAliases[keyCode] || (keyCode >= 48 && keyCode <= 90 ? String.fromCharCode(keyCode) : `Key ${keyCode}`);
  }
  function updateCustomShortcutInputText(inputItem, keyCode) {
    inputItem.value = keyCodeAliases[keyCode] || (keyCode >= 48 && keyCode <= 90 ? String.fromCharCode(keyCode) : `Key ${keyCode}`);
    inputItem.keyCode = keyCode;
  }
  function add_shortcut() {
    var html = `<select class="customDo">
    <option value="slower">Decrease speed</option>
    <option value="faster">Increase speed</option>
    <option value="rewind">Rewind</option>
    <option value="advance">Advance</option>
    <option value="reset">Reset speed</option>
    <option value="fast">Preferred speed</option>
    <option value="muted">Mute</option>
    <option value="softer">Decrease volume</option>
    <option value="louder">Increase volume</option>
    <option value="pause">Pause</option>
    <option value="mark">Set marker</option>
    <option value="jump">Jump to marker</option>
    <option value="display">Show/hide controller</option>
    </select>
    <input class="customKey" type="text" placeholder="press a key"/>
    <input class="customValue" type="text" placeholder="value (0.10)"/>
    <button class="removeParent">X</button>`;
    var div = document.createElement("div");
    div.setAttribute("class", "row customs");
    div.innerHTML = html;
    var customs_element = document.getElementById("customs");
    customs_element.insertBefore(
      div,
      customs_element.children[customs_element.childElementCount - 1]
    );
    const experimentalButton = document.getElementById("experimental");
    if (experimentalButton && experimentalButton.disabled) {
      const customValue = div.querySelector(".customValue");
      const select = document.createElement("select");
      select.className = "customForce show";
      select.innerHTML = `
      <option value="false">Default behavior</option>
      <option value="true">Override site keys</option>
    `;
      customValue.parentNode.insertBefore(select, customValue.nextSibling);
    }
  }
  function createKeyBindings(item) {
    const action = item.querySelector(".customDo").value;
    const key = item.querySelector(".customKey").keyCode;
    const value = Number(item.querySelector(".customValue").value);
    const forceElement = item.querySelector(".customForce");
    const force = forceElement ? forceElement.value : "false";
    const predefined = !!item.id;
    keyBindings.push({
      action,
      key,
      value,
      force,
      predefined
    });
  }
  function validate() {
    var valid = true;
    var status = document.getElementById("status");
    var blacklist = document.getElementById("blacklist");
    if (window.validationTimeout) {
      clearTimeout(window.validationTimeout);
    }
    blacklist.value.split("\n").forEach((match) => {
      match = match.replace(window.VSC.Constants.regStrip, "");
      if (match.startsWith("/")) {
        try {
          var parts = match.split("/");
          if (parts.length < 3)
            throw "invalid regex";
          var flags = parts.pop();
          var regex = parts.slice(1).join("/");
          var regexp = new RegExp(regex, flags);
        } catch (err) {
          status.textContent = 'Error: Invalid blacklist regex: "' + match + '". Unable to save. Try wrapping it in foward slashes.';
          status.classList.add("show", "error");
          valid = false;
          window.validationTimeout = setTimeout(function() {
            status.textContent = "";
            status.classList.remove("show", "error");
          }, 5e3);
          return;
        }
      }
    });
    return valid;
  }
  async function save_options() {
    if (validate() === false) {
      return;
    }
    var status = document.getElementById("status");
    status.textContent = "Saving...";
    status.classList.remove("success", "error");
    status.classList.add("show");
    try {
      keyBindings = [];
      Array.from(document.querySelectorAll(".customs")).forEach(
        (item) => createKeyBindings(item)
      );
      keyBindings = keyBindings.map((binding) => ({
        ...binding,
        force: Boolean(binding.force === "true" || binding.force === true)
      }));
      var rememberSpeed = document.getElementById("rememberSpeed").checked;
      var forceLastSavedSpeed = document.getElementById("forceLastSavedSpeed").checked;
      var audioBoolean = document.getElementById("audioBoolean").checked;
      var startHidden = document.getElementById("startHidden").checked;
      var controllerOpacity = Number(document.getElementById("controllerOpacity").value);
      var controllerButtonSize = Number(document.getElementById("controllerButtonSize").value);
      var logLevel = parseInt(document.getElementById("logLevel").value);
      var blacklist = document.getElementById("blacklist").value;
      if (!window.VSC.videoSpeedConfig) {
        window.VSC.videoSpeedConfig = new window.VSC.VideoSpeedConfig();
      }
      const settingsToSave = {
        rememberSpeed,
        forceLastSavedSpeed,
        audioBoolean,
        startHidden,
        controllerOpacity,
        controllerButtonSize,
        logLevel,
        keyBindings,
        blacklist: blacklist.replace(window.VSC.Constants.regStrip, "")
      };
      await window.VSC.videoSpeedConfig.save(settingsToSave);
      status.textContent = "Options saved";
      status.classList.add("success");
      setTimeout(function() {
        status.textContent = "";
        status.classList.remove("show", "success");
      }, 2e3);
    } catch (error) {
      console.error("Failed to save options:", error);
      status.textContent = "Error saving options: " + error.message;
      status.classList.add("show", "error");
      setTimeout(function() {
        status.textContent = "";
        status.classList.remove("show", "error");
      }, 3e3);
    }
  }
  async function restore_options() {
    try {
      if (!window.VSC.videoSpeedConfig) {
        window.VSC.videoSpeedConfig = new window.VSC.VideoSpeedConfig();
      }
      await window.VSC.videoSpeedConfig.load();
      const storage = window.VSC.videoSpeedConfig.settings;
      document.getElementById("rememberSpeed").checked = storage.rememberSpeed;
      document.getElementById("forceLastSavedSpeed").checked = storage.forceLastSavedSpeed;
      document.getElementById("audioBoolean").checked = storage.audioBoolean;
      document.getElementById("startHidden").checked = storage.startHidden;
      document.getElementById("controllerOpacity").value = storage.controllerOpacity;
      document.getElementById("controllerButtonSize").value = storage.controllerButtonSize;
      document.getElementById("logLevel").value = storage.logLevel;
      document.getElementById("blacklist").value = storage.blacklist;
      const keyBindings2 = storage.keyBindings || window.VSC.Constants.DEFAULT_SETTINGS.keyBindings;
      for (let i in keyBindings2) {
        var item = keyBindings2[i];
        if (item.predefined) {
          if (item["action"] == "display" && typeof item["key"] === "undefined") {
            item["key"] = storage.displayKeyCode || window.VSC.Constants.DEFAULT_SETTINGS.displayKeyCode;
          }
          if (window.VSC.Constants.CUSTOM_ACTIONS_NO_VALUES.includes(item["action"])) {
            const valueInput2 = document.querySelector("#" + item["action"] + " .customValue");
            if (valueInput2) {
              valueInput2.style.display = "none";
            }
          }
          const keyInput = document.querySelector("#" + item["action"] + " .customKey");
          const valueInput = document.querySelector("#" + item["action"] + " .customValue");
          const forceInput = document.querySelector("#" + item["action"] + " .customForce");
          if (keyInput) {
            updateCustomShortcutInputText(keyInput, item["key"]);
          }
          if (valueInput) {
            valueInput.value = item["value"];
          }
          if (forceInput) {
            forceInput.value = String(item["force"]);
          }
        } else {
          add_shortcut();
          const dom = document.querySelector(".customs:last-of-type");
          dom.querySelector(".customDo").value = item["action"];
          if (window.VSC.Constants.CUSTOM_ACTIONS_NO_VALUES.includes(item["action"])) {
            const valueInput = dom.querySelector(".customValue");
            if (valueInput) {
              valueInput.style.display = "none";
            }
          }
          updateCustomShortcutInputText(
            dom.querySelector(".customKey"),
            item["key"]
          );
          dom.querySelector(".customValue").value = item["value"];
          if (item["force"] !== void 0 && !dom.querySelector(".customForce")) {
            const customValue = dom.querySelector(".customValue");
            const select = document.createElement("select");
            select.className = "customForce";
            select.innerHTML = `
            <option value="false">Default behavior</option>
            <option value="true">Override site keys</option>
          `;
            select.value = String(item["force"]);
            customValue.parentNode.insertBefore(select, customValue.nextSibling);
          } else {
            const forceSelect = dom.querySelector(".customForce");
            if (forceSelect) {
              forceSelect.value = String(item["force"]);
            }
          }
        }
      }
      const hasExperimentalFeatures = keyBindings2.some((kb) => kb.force !== void 0 && kb.force !== false);
      if (hasExperimentalFeatures) {
        show_experimental();
      }
    } catch (error) {
      console.error("Failed to restore options:", error);
      document.getElementById("status").textContent = "Error loading options: " + error.message;
      document.getElementById("status").classList.add("show", "error");
      setTimeout(function() {
        document.getElementById("status").textContent = "";
        document.getElementById("status").classList.remove("show", "error");
      }, 3e3);
    }
  }
  async function restore_defaults() {
    try {
      var status = document.getElementById("status");
      status.textContent = "Restoring defaults...";
      status.classList.remove("success", "error");
      status.classList.add("show");
      await window.VSC.StorageManager.clear();
      if (!window.VSC.videoSpeedConfig) {
        window.VSC.videoSpeedConfig = new window.VSC.VideoSpeedConfig();
      }
      await window.VSC.videoSpeedConfig.save(window.VSC.Constants.DEFAULT_SETTINGS);
      document.querySelectorAll(".removeParent").forEach((button) => button.click());
      await restore_options();
      status.textContent = "Default options restored";
      status.classList.add("success");
      setTimeout(function() {
        status.textContent = "";
        status.classList.remove("show", "success");
      }, 2e3);
    } catch (error) {
      console.error("Failed to restore defaults:", error);
      status.textContent = "Error restoring defaults: " + error.message;
      status.classList.add("show", "error");
      setTimeout(function() {
        status.textContent = "";
        status.classList.remove("show", "error");
      }, 3e3);
    }
  }
  function show_experimental() {
    const button = document.getElementById("experimental");
    const customRows = document.querySelectorAll(".row.customs");
    const advancedRows = document.querySelectorAll(".row.advanced-feature");
    advancedRows.forEach((row) => {
      row.classList.add("show");
    });
    const createForceSelect = () => {
      const select = document.createElement("select");
      select.className = "customForce show";
      select.innerHTML = `
      <option value="false">Allow event propagation</option>
      <option value="true">Disable event propagation</option>
    `;
      return select;
    };
    customRows.forEach((row) => {
      const existingSelect = row.querySelector(".customForce");
      if (!existingSelect) {
        const customValue = row.querySelector(".customValue");
        const newSelect = createForceSelect();
        const rowId = row.id;
        if (rowId && window.VSC.videoSpeedConfig && window.VSC.videoSpeedConfig.settings.keyBindings) {
          const savedBinding = window.VSC.videoSpeedConfig.settings.keyBindings.find((kb) => kb.action === rowId);
          if (savedBinding && savedBinding.force !== void 0) {
            newSelect.value = String(savedBinding.force);
          }
        } else if (!rowId) {
          const rowIndex = Array.from(row.parentElement.querySelectorAll(".row.customs:not([id])")).indexOf(row);
          const customBindings = window.VSC.videoSpeedConfig?.settings.keyBindings?.filter((kb) => !kb.predefined) || [];
          if (customBindings[rowIndex] && customBindings[rowIndex].force !== void 0) {
            newSelect.value = String(customBindings[rowIndex].force);
          }
        }
        if (customValue) {
          customValue.parentNode.insertBefore(newSelect, customValue.nextSibling);
        }
      } else {
        existingSelect.classList.add("show");
      }
    });
    button.textContent = "Advanced features enabled";
    button.disabled = true;
  }
  var debouncedSave = debounce(save_options, 300);
  document.addEventListener("DOMContentLoaded", async function() {
    window.VSC.StorageManager.onError((error, data) => {
      console.warn("Storage operation failed:", error.message, data);
    });
    await restore_options();
    document.querySelectorAll(".row.customs[id] .customDo").forEach((select) => {
      select.disabled = true;
    });
    document.getElementById("save").addEventListener("click", async (e) => {
      e.preventDefault();
      await save_options();
    });
    document.getElementById("add").addEventListener("click", add_shortcut);
    document.getElementById("restore").addEventListener("click", async (e) => {
      e.preventDefault();
      await restore_defaults();
    });
    document.getElementById("experimental").addEventListener("click", show_experimental);
    document.getElementById("about").addEventListener("click", function() {
      window.open("https://github.com/igrigorik/videospeed");
    });
    document.getElementById("feedback").addEventListener("click", function() {
      window.open("https://github.com/igrigorik/videospeed/issues");
    });
    function eventCaller(event, className, funcName) {
      if (!event.target.classList.contains(className)) {
        return;
      }
      funcName(event);
    }
    document.addEventListener("keypress", (event) => {
      eventCaller(event, "customValue", inputFilterNumbersOnly);
    });
    document.addEventListener("focus", (event) => {
      eventCaller(event, "customKey", inputFocus);
    });
    document.addEventListener("blur", (event) => {
      eventCaller(event, "customKey", inputBlur);
    });
    document.addEventListener("keydown", (event) => {
      eventCaller(event, "customKey", recordKeyPress);
    });
    document.addEventListener("click", (event) => {
      eventCaller(event, "removeParent", function() {
        event.target.parentNode.remove();
      });
    });
    document.addEventListener("change", (event) => {
      eventCaller(event, "customDo", function() {
        const valueInput = event.target.nextElementSibling.nextElementSibling;
        if (window.VSC.Constants.CUSTOM_ACTIONS_NO_VALUES.includes(event.target.value)) {
          valueInput.style.display = "none";
          valueInput.value = 0;
        } else {
          valueInput.style.display = "inline-block";
        }
      });
    });
  });
})();
