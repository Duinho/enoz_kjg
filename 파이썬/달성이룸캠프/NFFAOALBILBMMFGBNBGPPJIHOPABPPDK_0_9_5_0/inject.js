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

  // src/utils/debug-helper.js
  window.VSC = window.VSC || {};
  var DebugHelper = class {
    constructor() {
      this.isActive = false;
    }
    /**
     * Enable debug mode with enhanced logging
     */
    enable() {
      this.isActive = true;
      console.log("\u{1F41B} VSC Debug Mode Enabled");
      if (window.VSC.logger && window.VSC.Constants.LOG_LEVELS) {
        window.VSC.logger.setVerbosity(window.VSC.Constants.LOG_LEVELS.DEBUG);
      }
      window.vscDebug = {
        checkMedia: () => this.checkMediaElements(),
        checkControllers: () => this.checkControllers(),
        testPopup: () => this.testPopupCommunication(),
        testBridge: () => this.testPopupMessageBridge(),
        forceShow: () => this.forceShowControllers(),
        forceShowAudio: () => this.forceShowAudioControllers(),
        getVisibility: (element) => this.getElementVisibility(element)
      };
      console.log(
        "\u{1F527} Debug functions available: vscDebug.checkMedia(), vscDebug.checkControllers(), vscDebug.testPopup(), vscDebug.testBridge(), vscDebug.forceShow(), vscDebug.forceShowAudio()"
      );
    }
    /**
     * Check all media elements and their detection status
     */
    checkMediaElements() {
      console.group("\u{1F3B5} Media Elements Analysis");
      const videos = document.querySelectorAll("video");
      const audios = document.querySelectorAll("audio");
      console.log(`Found ${videos.length} video elements, ${audios.length} audio elements`);
      [...videos, ...audios].forEach((media, index) => {
        console.group(`${media.tagName} #${index + 1}`);
        console.log("Element:", media);
        console.log("Connected to DOM:", media.isConnected);
        console.log("Has VSC controller:", !!media.vsc);
        console.log("Current source:", media.currentSrc || media.src || "No source");
        console.log("Ready state:", media.readyState);
        console.log("Paused:", media.paused);
        console.log("Duration:", media.duration);
        const style = window.getComputedStyle(media);
        console.log("Computed styles:", {
          display: style.display,
          visibility: style.visibility,
          opacity: style.opacity,
          width: style.width,
          height: style.height
        });
        const rect = media.getBoundingClientRect();
        console.log("Bounding rect:", {
          width: rect.width,
          height: rect.height,
          top: rect.top,
          left: rect.left,
          visible: rect.width > 0 && rect.height > 0
        });
        if (window.VSC.MediaElementObserver && window.VSC_controller?.mediaObserver) {
          const observer = window.VSC_controller.mediaObserver;
          console.log("VSC would detect:", observer.isValidMediaElement(media));
          console.log("VSC would start hidden:", observer.shouldStartHidden(media));
        }
        console.groupEnd();
      });
      this.checkShadowDOMMedia();
      console.groupEnd();
    }
    /**
     * Check shadow DOM for hidden media elements
     */
    checkShadowDOMMedia() {
      console.group("\u{1F47B} Shadow DOM Media Check");
      let shadowMediaCount = 0;
      const checkElement = (element) => {
        if (element.shadowRoot) {
          const shadowMedia = element.shadowRoot.querySelectorAll("video, audio");
          if (shadowMedia.length > 0) {
            console.log(`Found ${shadowMedia.length} media elements in shadow DOM of:`, element);
            shadowMediaCount += shadowMedia.length;
            shadowMedia.forEach((media, index) => {
              console.log(`  Shadow media #${index + 1}:`, media);
            });
          }
          element.shadowRoot.querySelectorAll("*").forEach(checkElement);
        }
      };
      document.querySelectorAll("*").forEach(checkElement);
      console.log(`Total shadow DOM media elements: ${shadowMediaCount}`);
      console.groupEnd();
    }
    /**
     * Check all controllers and their visibility status
     */
    checkControllers() {
      console.group("\u{1F3AE} Controllers Analysis");
      const controllers = document.querySelectorAll("vsc-controller");
      console.log(`Found ${controllers.length} VSC controllers`);
      controllers.forEach((controller, index) => {
        console.group(`Controller #${index + 1}`);
        console.log("Element:", controller);
        console.log("Classes:", controller.className);
        const style = window.getComputedStyle(controller);
        console.log("Computed styles:", {
          display: style.display,
          visibility: style.visibility,
          opacity: style.opacity,
          position: style.position,
          top: style.top,
          left: style.left,
          zIndex: style.zIndex
        });
        const isHidden = controller.classList.contains("vsc-hidden");
        const isManual = controller.classList.contains("vsc-manual");
        const hasNoSource = controller.classList.contains("vsc-nosource");
        console.log("VSC State:", {
          hidden: isHidden,
          manual: isManual,
          noSource: hasNoSource,
          effectivelyVisible: !isHidden && style.display !== "none"
        });
        let associatedVideo = null;
        document.querySelectorAll("video, audio").forEach((media) => {
          if (media.vsc && media.vsc.div === controller) {
            associatedVideo = media;
          }
        });
        if (associatedVideo) {
          console.log("Associated media:", associatedVideo);
          console.log("Media visibility would be:", this.getElementVisibility(associatedVideo));
        } else {
          console.log("\u26A0\uFE0F No associated media found");
        }
        console.groupEnd();
      });
      console.groupEnd();
    }
    /**
     * Test popup communication
     */
    testPopupCommunication() {
      console.group("\u{1F4E1} Popup Communication Test");
      if (typeof chrome !== "undefined" && chrome.runtime) {
        console.log("\u2705 Chrome runtime available");
      } else {
        console.log("\u2139\uFE0F Chrome runtime not available (expected in page context)");
      }
      console.log("Testing direct VSC message handling...");
      const videos = document.querySelectorAll("video, audio");
      console.log(`Found ${videos.length} media elements to control`);
      videos.forEach((video, index) => {
        console.log(`Media #${index + 1}:`, {
          element: video,
          hasController: !!video.vsc,
          currentSpeed: video.playbackRate,
          canControl: !video.classList.contains("vsc-cancelled")
        });
      });
      if (window.VSC_controller && window.VSC_controller.actionHandler) {
        console.log("\u2705 Action handler available, testing speed controls...");
        const testSpeed = 1.5;
        console.log(`Testing speed change to ${testSpeed}x`);
        videos.forEach((video, index) => {
          if (video.vsc) {
            console.log(`Applying speed ${testSpeed} to media #${index + 1} via action handler`);
            window.VSC_controller.actionHandler.adjustSpeed(video, testSpeed);
          } else {
            console.log(`Applying speed ${testSpeed} to media #${index + 1} directly`);
            video.playbackRate = testSpeed;
          }
        });
        setTimeout(() => {
          console.log("Resetting speed to 1.0x");
          videos.forEach((video) => {
            if (video.vsc) {
              window.VSC_controller.actionHandler.adjustSpeed(video, 1);
            } else {
              video.playbackRate = 1;
            }
          });
        }, 2e3);
      } else {
        console.log("\u274C Action handler not available");
      }
      console.groupEnd();
    }
    /**
     * Test the complete popup message bridge by simulating the message flow
     */
    testPopupMessageBridge() {
      console.group("\u{1F4E1} Testing Complete Popup Message Bridge");
      const testMessages = [
        { type: "VSC_SET_SPEED", payload: { speed: 1.25 } },
        { type: "VSC_ADJUST_SPEED", payload: { delta: 0.25 } },
        { type: "VSC_RESET_SPEED" }
      ];
      console.log("Testing message bridge by simulating popup messages...");
      testMessages.forEach((message, index) => {
        setTimeout(() => {
          console.log(`\u{1F527} Debug: Simulating popup message ${index + 1}:`, message);
          window.dispatchEvent(
            new CustomEvent("VSC_MESSAGE", {
              detail: message
            })
          );
        }, index * 1500);
      });
      console.log("Messages will be sent with 1.5 second intervals...");
      console.groupEnd();
    }
    /**
     * Force show all controllers for debugging
     */
    forceShowControllers() {
      console.log("\u{1F527} Force showing all controllers");
      const controllers = document.querySelectorAll("vsc-controller");
      controllers.forEach((controller, index) => {
        controller.classList.remove("vsc-hidden", "vsc-nosource");
        controller.classList.add("vsc-manual", "vsc-show");
        controller.style.display = "block !important";
        controller.style.visibility = "visible !important";
        controller.style.opacity = "1 !important";
        console.log(`Controller #${index + 1} forced visible`);
      });
      return controllers.length;
    }
    /**
     * Force show audio controllers specifically
     */
    forceShowAudioControllers() {
      console.log("\u{1F50A} Force showing audio controllers");
      const audioElements = document.querySelectorAll("audio");
      let controllersShown = 0;
      audioElements.forEach((audio, index) => {
        if (audio.vsc && audio.vsc.div) {
          const controller = audio.vsc.div;
          controller.classList.remove("vsc-hidden", "vsc-nosource");
          controller.classList.add("vsc-manual", "vsc-show");
          controller.style.display = "block !important";
          controller.style.visibility = "visible !important";
          controller.style.opacity = "1 !important";
          console.log(`Audio controller #${index + 1} forced visible`);
          controllersShown++;
        } else {
          console.log(`Audio #${index + 1} has no controller attached`);
        }
      });
      return controllersShown;
    }
    /**
     * Get detailed visibility information for an element
     */
    getElementVisibility(element) {
      const style = window.getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return {
        connected: element.isConnected,
        display: style.display,
        visibility: style.visibility,
        opacity: style.opacity,
        width: rect.width,
        height: rect.height,
        isVisible: element.isConnected && style.display !== "none" && style.visibility !== "hidden" && style.opacity !== "0" && rect.width > 0 && rect.height > 0
      };
    }
    /**
     * Monitor controller visibility changes
     */
    monitorControllerChanges() {
      console.log("\u{1F440} Starting controller visibility monitoring");
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.type === "attributes" && (mutation.attributeName === "class" || mutation.attributeName === "style")) {
            const target = mutation.target;
            if (target.tagName === "VSC-CONTROLLER") {
              console.log("\u{1F504} Controller visibility changed:", {
                element: target,
                classes: target.className,
                hidden: target.classList.contains("vsc-hidden"),
                manual: target.classList.contains("vsc-manual")
              });
            }
          }
        });
      });
      observer.observe(document.body, {
        attributes: true,
        subtree: true,
        attributeFilter: ["class", "style"]
      });
      return observer;
    }
  };
  window.VSC.DebugHelper = DebugHelper;
  window.vscDebugHelper = new DebugHelper();

  // src/utils/dom-utils.js
  window.VSC = window.VSC || {};
  window.VSC.DomUtils = {};
  window.VSC.DomUtils.escapeStringRegExp = function(str) {
    const matchOperatorsRe = /[|\\{}()[\]^$+*?.]/g;
    return str.replace(matchOperatorsRe, "\\$&");
  };
  window.VSC.DomUtils.isBlacklisted = function(blacklist) {
    let blacklisted = false;
    blacklist.split("\n").forEach((match) => {
      match = match.replace(window.VSC.Constants.regStrip, "");
      if (match.length === 0) {
        return;
      }
      let regexp;
      if (match.startsWith("/")) {
        try {
          const parts = match.split("/");
          if (parts.length < 3) {
            return;
          }
          const hasFlags = window.VSC.Constants.regEndsWithFlags.test(match);
          const flags = hasFlags ? parts.pop() : "";
          const regex = parts.slice(1, hasFlags ? void 0 : -1).join("/");
          if (!regex) {
            return;
          }
          regexp = new RegExp(regex, flags);
        } catch (err) {
          return;
        }
      } else {
        const escapedMatch = window.VSC.DomUtils.escapeStringRegExp(match);
        const looksLikeDomain = match.includes(".") && !match.includes("/");
        if (looksLikeDomain) {
          regexp = new RegExp(`(^|\\.|//)${escapedMatch}(\\/|:|$)`);
        } else {
          regexp = new RegExp(escapedMatch);
        }
      }
      if (regexp.test(location.href)) {
        blacklisted = true;
      }
    });
    return blacklisted;
  };
  window.VSC.DomUtils.inIframe = function() {
    try {
      return window.self !== window.top;
    } catch (e) {
      return true;
    }
  };
  window.VSC.DomUtils.getShadow = function(parent, maxDepth = 10) {
    const result = [];
    const visited = /* @__PURE__ */ new WeakSet();
    function getChild(element, depth = 0) {
      if (depth > maxDepth || visited.has(element)) {
        return;
      }
      visited.add(element);
      if (element.firstElementChild) {
        let child = element.firstElementChild;
        do {
          result.push(child);
          getChild(child, depth + 1);
          if (child.shadowRoot && depth < maxDepth - 2) {
            result.push(...window.VSC.DomUtils.getShadow(child.shadowRoot, maxDepth - depth));
          }
          child = child.nextElementSibling;
        } while (child);
      }
    }
    getChild(parent);
    return result.flat(Infinity);
  };
  window.VSC.DomUtils.findVideoParent = function(element) {
    let parentElement = element.parentElement;
    while (parentElement.parentNode && parentElement.parentNode.offsetHeight === parentElement.offsetHeight && parentElement.parentNode.offsetWidth === parentElement.offsetWidth) {
      parentElement = parentElement.parentNode;
    }
    return parentElement;
  };
  window.VSC.DomUtils.initializeWhenReady = function(document2, callback) {
    window.VSC.logger.debug("Begin initializeWhenReady");
    const handleWindowLoad = () => {
      callback(window.document);
    };
    window.addEventListener("load", handleWindowLoad, { once: true });
    if (document2) {
      if (document2.readyState === "complete") {
        callback(document2);
      } else {
        const handleReadyStateChange = () => {
          if (document2.readyState === "complete") {
            document2.removeEventListener("readystatechange", handleReadyStateChange);
            callback(document2);
          }
        };
        document2.addEventListener("readystatechange", handleReadyStateChange);
      }
    }
    window.VSC.logger.debug("End initializeWhenReady");
  };
  window.VSC.DomUtils.findMediaElements = function(node, audioEnabled = false) {
    if (!node) {
      return [];
    }
    const mediaElements = [];
    const selector = audioEnabled ? "video,audio" : "video";
    if (node && node.matches && node.matches(selector)) {
      mediaElements.push(node);
    }
    if (node.querySelectorAll) {
      mediaElements.push(...Array.from(node.querySelectorAll(selector)));
    }
    if (node.shadowRoot) {
      mediaElements.push(...window.VSC.DomUtils.findShadowMedia(node.shadowRoot, selector));
    }
    return mediaElements;
  };
  window.VSC.DomUtils.findShadowMedia = function(root, selector) {
    const results = [];
    if (root.shadowRoot) {
      results.push(...window.VSC.DomUtils.findShadowMedia(root.shadowRoot, selector));
    }
    if (root.querySelectorAll) {
      results.push(...Array.from(root.querySelectorAll(selector)));
    }
    if (root.querySelectorAll) {
      const allElements = Array.from(root.querySelectorAll("*"));
      allElements.forEach((element) => {
        if (element.shadowRoot) {
          results.push(...window.VSC.DomUtils.findShadowMedia(element.shadowRoot, selector));
        }
      });
    }
    return results;
  };

  // src/utils/event-manager.js
  window.VSC = window.VSC || {};
  var EventManager = class _EventManager {
    constructor(config, actionHandler) {
      this.config = config;
      this.actionHandler = actionHandler;
      this.listeners = /* @__PURE__ */ new Map();
      this.coolDown = false;
      this.timer = null;
      this.lastKeyEventSignature = null;
    }
    /**
     * Set up all event listeners
     * @param {Document} document - Document to attach events to
     */
    setupEventListeners(document2) {
      this.setupKeyboardShortcuts(document2);
      this.setupRateChangeListener(document2);
    }
    /**
     * Set up keyboard shortcuts
     * @param {Document} document - Document to attach events to
     */
    setupKeyboardShortcuts(document2) {
      const docs = [document2];
      try {
        if (window.VSC.inIframe()) {
          docs.push(window.top.document);
        }
      } catch (e) {
      }
      docs.forEach((doc) => {
        const keydownHandler = (event) => this.handleKeydown(event);
        doc.addEventListener("keydown", keydownHandler, true);
        if (!this.listeners.has(doc)) {
          this.listeners.set(doc, []);
        }
        this.listeners.get(doc).push({
          type: "keydown",
          handler: keydownHandler,
          useCapture: true
        });
      });
    }
    /**
     * Handle keydown events
     * @param {KeyboardEvent} event - Keyboard event
     * @private
     */
    handleKeydown(event) {
      const keyCode = event.keyCode;
      window.VSC.logger.verbose(`Processing keydown event: key=${event.key}, keyCode=${keyCode}`);
      const eventSignature = `${keyCode}_${event.timeStamp}_${event.type}`;
      if (this.lastKeyEventSignature === eventSignature) {
        return;
      }
      this.lastKeyEventSignature = eventSignature;
      if (this.hasActiveModifier(event)) {
        window.VSC.logger.debug(`Keydown event ignored due to active modifier: ${keyCode}`);
        return;
      }
      if (this.isTypingContext(event.target)) {
        return false;
      }
      const mediaElements = window.VSC.stateManager ? window.VSC.stateManager.getControlledElements() : [];
      if (!mediaElements.length) {
        return false;
      }
      const keyBinding = this.config.settings.keyBindings.find((item) => item.key === keyCode);
      if (keyBinding) {
        this.actionHandler.runAction(keyBinding.action, keyBinding.value, event);
        if (keyBinding.force === true || keyBinding.force === "true") {
          event.preventDefault();
          event.stopPropagation();
        }
      } else {
        window.VSC.logger.verbose(`No key binding found for keyCode: ${keyCode}`);
      }
      return false;
    }
    /**
     * Check if any modifier keys are active
     * @param {KeyboardEvent} event - Keyboard event
     * @returns {boolean} True if modifiers are active
     * @private
     */
    hasActiveModifier(event) {
      return !event.getModifierState || event.getModifierState("Alt") || event.getModifierState("Control") || event.getModifierState("Fn") || event.getModifierState("Meta") || event.getModifierState("Hyper") || event.getModifierState("OS");
    }
    /**
     * Check if user is typing in an input context
     * @param {Element} target - Event target
     * @returns {boolean} True if typing context
     * @private
     */
    isTypingContext(target) {
      return target.nodeName === "INPUT" || target.nodeName === "TEXTAREA" || target.isContentEditable;
    }
    /**
     * Set up rate change event listener
     * @param {Document} document - Document to attach events to
     */
    setupRateChangeListener(document2) {
      const rateChangeHandler = (event) => this.handleRateChange(event);
      document2.addEventListener("ratechange", rateChangeHandler, true);
      if (!this.listeners.has(document2)) {
        this.listeners.set(document2, []);
      }
      this.listeners.get(document2).push({
        type: "ratechange",
        handler: rateChangeHandler,
        useCapture: true
      });
    }
    /**
     * Handle rate change events
     * @param {Event} event - Rate change event
     * @private
     */
    handleRateChange(event) {
      if (this.coolDown) {
        window.VSC.logger.debug("Rate change event blocked by cooldown");
        const video2 = event.composedPath ? event.composedPath()[0] : event.target;
        if (video2.vsc && this.config.settings.lastSpeed !== void 0) {
          const authoritativeSpeed = this.config.settings.lastSpeed;
          if (Math.abs(video2.playbackRate - authoritativeSpeed) > 0.01) {
            window.VSC.logger.info(`Restoring speed during cooldown from external ${video2.playbackRate} to authoritative ${authoritativeSpeed}`);
            video2.playbackRate = authoritativeSpeed;
          }
        }
        event.stopImmediatePropagation();
        return;
      }
      const video = event.composedPath ? event.composedPath()[0] : event.target;
      if (!video.vsc) {
        window.VSC.logger.debug("Skipping ratechange - no VSC controller attached");
        return;
      }
      if (event.detail && event.detail.origin === "videoSpeed") {
        window.VSC.logger.debug("Ignoring extension-originated rate change");
        return;
      }
      if (this.config.settings.forceLastSavedSpeed) {
        if (event.detail && event.detail.origin === "videoSpeed") {
          video.playbackRate = Number(event.detail.speed);
        } else {
          const authoritativeSpeed = this.config.settings.lastSpeed || 1;
          window.VSC.logger.info(`Force mode: restoring external ${video.playbackRate} to authoritative ${authoritativeSpeed}`);
          video.playbackRate = authoritativeSpeed;
        }
        event.stopImmediatePropagation();
        return;
      }
      if (video.readyState < 1) {
        window.VSC.logger.debug("Ignoring external ratechange during video initialization (readyState < 1)");
        event.stopImmediatePropagation();
        return;
      }
      const rawExternalRate = typeof video.playbackRate === "number" ? video.playbackRate : NaN;
      const min = window.VSC.Constants.SPEED_LIMITS.MIN;
      if (!isNaN(rawExternalRate) && rawExternalRate <= min) {
        window.VSC.logger.debug(
          `Ignoring external ratechange below MIN: raw=${rawExternalRate}, MIN=${min}`
        );
        event.stopImmediatePropagation();
        return;
      }
      if (this.actionHandler) {
        this.actionHandler.adjustSpeed(video, video.playbackRate, {
          source: "external"
        });
      }
      event.stopImmediatePropagation();
    }
    /**
     * Start cooldown period to prevent event spam
     */
    refreshCoolDown() {
      window.VSC.logger.debug("Begin refreshCoolDown");
      if (this.coolDown) {
        clearTimeout(this.coolDown);
      }
      this.coolDown = setTimeout(() => {
        this.coolDown = false;
      }, _EventManager.COOLDOWN_MS);
      window.VSC.logger.debug("End refreshCoolDown");
    }
    /**
     * Show controller temporarily during speed changes or other automatic actions
     * @param {Element} controller - Controller element
     */
    showController(controller) {
      if (this.config.settings.startHidden && !controller.classList.contains("vsc-manual")) {
        window.VSC.logger.info(
          `Controller respecting startHidden setting - no temporary display (startHidden: ${this.config.settings.startHidden}, manual: ${controller.classList.contains("vsc-manual")})`
        );
        return;
      }
      window.VSC.logger.info(
        `Showing controller temporarily (startHidden: ${this.config.settings.startHidden}, manual: ${controller.classList.contains("vsc-manual")})`
      );
      controller.classList.add("vsc-show");
      if (this.timer) {
        clearTimeout(this.timer);
      }
      this.timer = setTimeout(() => {
        controller.classList.remove("vsc-show");
        this.timer = null;
        window.VSC.logger.debug("Hiding controller");
      }, 2e3);
    }
    /**
     * Clean up all event listeners
     */
    cleanup() {
      this.listeners.forEach((eventList, doc) => {
        eventList.forEach(({ type, handler, useCapture }) => {
          try {
            doc.removeEventListener(type, handler, useCapture);
          } catch (e) {
            window.VSC.logger.warn(`Failed to remove event listener: ${e.message}`);
          }
        });
      });
      this.listeners.clear();
      if (this.coolDown) {
        clearTimeout(this.coolDown);
        this.coolDown = false;
      }
      if (this.timer) {
        clearTimeout(this.timer);
        this.timer = null;
      }
    }
  };
  EventManager.COOLDOWN_MS = 200;
  window.VSC.EventManager = EventManager;

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

  // src/core/state-manager.js
  window.VSC = window.VSC || {};
  var VSCStateManager = class {
    constructor() {
      this.controllers = /* @__PURE__ */ new Map();
      window.VSC.logger?.debug("VSCStateManager initialized");
    }
    /**
     * Register a new controller
     * @param {VideoController} controller - Controller instance to register
     */
    registerController(controller) {
      if (!controller || !controller.controllerId) {
        window.VSC.logger?.warn("Invalid controller registration attempt");
        return;
      }
      const controllerInfo = {
        controller,
        element: controller.video,
        tagName: controller.video?.tagName,
        videoSrc: controller.video?.src || controller.video?.currentSrc,
        created: Date.now()
      };
      this.controllers.set(controller.controllerId, controllerInfo);
      window.VSC.logger?.debug(`Controller registered: ${controller.controllerId}`);
    }
    /**
     * Unregister a controller
     * @param {string} controllerId - ID of controller to unregister
     */
    unregisterController(controllerId) {
      if (this.controllers.has(controllerId)) {
        this.controllers.delete(controllerId);
        window.VSC.logger?.debug(`Controller unregistered: ${controllerId}`);
      }
    }
    /**
     * Get all registered media elements
     * @returns {Array<HTMLMediaElement>} Array of media elements
     */
    getAllMediaElements() {
      const elements = [];
      for (const [id, info] of this.controllers) {
        const video = info.controller?.video || info.element;
        if (video && video.isConnected) {
          elements.push(video);
        } else {
          this.controllers.delete(id);
        }
      }
      return elements;
    }
    /**
     * Get a media element by controller ID
     * @param {string} controllerId - Controller ID
     * @returns {HTMLMediaElement|null} Media element or null
     */
    getMediaByControllerId(controllerId) {
      const info = this.controllers.get(controllerId);
      return info?.controller?.video || info?.element || null;
    }
    /**
     * Get the first available media element
     * @returns {HTMLMediaElement|null} First media element or null
     */
    getFirstMedia() {
      const elements = this.getAllMediaElements();
      return elements[0] || null;
    }
    /**
     * Check if any controllers are registered
     * @returns {boolean} True if controllers exist
     */
    hasControllers() {
      return this.controllers.size > 0;
    }
    /**
     * Compatibility method - same as unregisterController
     * @param {string} controllerId - ID of controller to remove
     */
    removeController(controllerId) {
      this.unregisterController(controllerId);
    }
    /**
     * Compatibility method - same as getAllMediaElements
     * @returns {Array<HTMLMediaElement>} Array of media elements
     */
    getControlledElements() {
      return this.getAllMediaElements();
    }
  };
  window.VSC.StateManager = VSCStateManager;
  window.VSC.stateManager = new VSCStateManager();
  window.VSC.logger?.info("State Manager module loaded");

  // src/observers/media-observer.js
  window.VSC = window.VSC || {};
  var MediaElementObserver = class {
    constructor(config, siteHandler) {
      this.config = config;
      this.siteHandler = siteHandler;
    }
    /**
     * Scan document for existing media elements
     * @param {Document} document - Document to scan
     * @returns {Array<HTMLMediaElement>} Found media elements
     */
    scanForMedia(document2) {
      const mediaElements = [];
      const audioEnabled = this.config.settings.audioBoolean;
      const mediaTagSelector = audioEnabled ? "video,audio" : "video";
      const regularMedia = Array.from(document2.querySelectorAll(mediaTagSelector));
      mediaElements.push(...regularMedia);
      function findShadowMedia(root, selector) {
        const results = [];
        results.push(...root.querySelectorAll(selector));
        root.querySelectorAll("*").forEach((element) => {
          if (element.shadowRoot) {
            results.push(...findShadowMedia(element.shadowRoot, selector));
          }
        });
        return results;
      }
      const shadowMedia = findShadowMedia(document2, mediaTagSelector);
      mediaElements.push(...shadowMedia);
      const siteSpecificMedia = this.siteHandler.detectSpecialVideos(document2);
      mediaElements.push(...siteSpecificMedia);
      const filteredMedia = mediaElements.filter((media) => {
        return !this.siteHandler.shouldIgnoreVideo(media);
      });
      window.VSC.logger.info(
        `Found ${filteredMedia.length} media elements (${mediaElements.length} total, ${mediaElements.length - filteredMedia.length} filtered out)`
      );
      return filteredMedia;
    }
    /**
     * Lightweight scan that avoids expensive shadow DOM traversal
     * Used during initial load to avoid blocking page performance
     * @param {Document} document - Document to scan
     * @returns {Array<HTMLMediaElement>} Found media elements
     */
    scanForMediaLight(document2) {
      const mediaElements = [];
      const audioEnabled = this.config.settings.audioBoolean;
      const mediaTagSelector = audioEnabled ? "video,audio" : "video";
      try {
        const regularMedia = Array.from(document2.querySelectorAll(mediaTagSelector));
        mediaElements.push(...regularMedia);
        const siteSpecificMedia = this.siteHandler.detectSpecialVideos(document2);
        mediaElements.push(...siteSpecificMedia);
        const filteredMedia = mediaElements.filter((media) => {
          return !this.siteHandler.shouldIgnoreVideo(media);
        });
        window.VSC.logger.info(
          `Light scan found ${filteredMedia.length} media elements (${mediaElements.length} total, ${mediaElements.length - filteredMedia.length} filtered out)`
        );
        return filteredMedia;
      } catch (error) {
        window.VSC.logger.error(`Light media scan failed: ${error.message}`);
        return [];
      }
    }
    /**
     * Scan iframes for media elements
     * @param {Document} document - Document to scan
     * @returns {Array<HTMLMediaElement>} Found media elements in iframes
     */
    scanIframes(document2) {
      const mediaElements = [];
      const frameTags = document2.getElementsByTagName("iframe");
      Array.prototype.forEach.call(frameTags, (frame) => {
        try {
          const childDocument = frame.contentDocument;
          if (childDocument) {
            const iframeMedia = this.scanForMedia(childDocument);
            mediaElements.push(...iframeMedia);
            window.VSC.logger.debug(`Found ${iframeMedia.length} media elements in iframe`);
          }
        } catch (e) {
          window.VSC.logger.debug(`Cannot access iframe content (cross-origin): ${e.message}`);
        }
      });
      return mediaElements;
    }
    /**
     * Get media elements using site-specific container selectors
     * @param {Document} document - Document to scan
     * @returns {Array<HTMLMediaElement>} Found media elements
     */
    scanSiteSpecificContainers(document2) {
      const mediaElements = [];
      const containerSelectors = this.siteHandler.getVideoContainerSelectors();
      const audioEnabled = this.config.settings.audioBoolean;
      containerSelectors.forEach((selector) => {
        try {
          const containers = document2.querySelectorAll(selector);
          containers.forEach((container) => {
            const containerMedia = window.VSC.DomUtils.findMediaElements(container, audioEnabled);
            mediaElements.push(...containerMedia);
          });
        } catch (e) {
          window.VSC.logger.warn(`Invalid selector "${selector}": ${e.message}`);
        }
      });
      return mediaElements;
    }
    /**
     * Comprehensive scan for all media elements
     * @param {Document} document - Document to scan
     * @returns {Array<HTMLMediaElement>} All found media elements
     */
    scanAll(document2) {
      const allMedia = [];
      const regularMedia = this.scanForMedia(document2);
      allMedia.push(...regularMedia);
      const containerMedia = this.scanSiteSpecificContainers(document2);
      allMedia.push(...containerMedia);
      const iframeMedia = this.scanIframes(document2);
      allMedia.push(...iframeMedia);
      const uniqueMedia = [...new Set(allMedia)];
      window.VSC.logger.info(`Total unique media elements found: ${uniqueMedia.length}`);
      return uniqueMedia;
    }
    /**
     * Check if media element is valid for controller attachment
     * @param {HTMLMediaElement} media - Media element to check
     * @returns {boolean} True if valid
     */
    isValidMediaElement(media) {
      if (!media.isConnected) {
        window.VSC.logger.debug("Video not in DOM");
        return false;
      }
      if (media.tagName === "AUDIO" && !this.config.settings.audioBoolean) {
        window.VSC.logger.debug("Audio element rejected - audioBoolean disabled");
        return false;
      }
      if (this.siteHandler.shouldIgnoreVideo(media)) {
        window.VSC.logger.debug("Video ignored by site handler");
        return false;
      }
      return true;
    }
    /**
     * Check if media element should start with hidden controller
     * @param {HTMLMediaElement} media - Media element to check
     * @returns {boolean} True if controller should start hidden
     */
    shouldStartHidden(media) {
      if (media.tagName === "AUDIO") {
        if (!this.config.settings.audioBoolean) {
          window.VSC.logger.debug("Audio controller hidden - audio support disabled");
          return true;
        }
        if (media.disabled || media.style.pointerEvents === "none") {
          window.VSC.logger.debug("Audio controller hidden - element disabled or no pointer events");
          return true;
        }
        window.VSC.logger.debug(
          "Audio controller will start visible (audio elements can be invisible but functional)"
        );
        return false;
      }
      const style = window.getComputedStyle(media);
      if (style.display === "none" || style.visibility === "hidden" || style.opacity === "0") {
        window.VSC.logger.debug("Video not visible, controller will start hidden");
        return true;
      }
      return false;
    }
    /**
     * Find the best parent element for controller positioning
     * @param {HTMLMediaElement} media - Media element
     * @returns {HTMLElement} Parent element for positioning
     */
    findControllerParent(media) {
      const positioning = this.siteHandler.getControllerPosition(media.parentElement, media);
      return positioning.targetParent || media.parentElement;
    }
  };
  window.VSC.MediaElementObserver = MediaElementObserver;

  // src/observers/mutation-observer.js
  window.VSC = window.VSC || {};
  var VideoMutationObserver = class {
    constructor(config, onVideoFound, onVideoRemoved, mediaObserver) {
      this.config = config;
      this.onVideoFound = onVideoFound;
      this.onVideoRemoved = onVideoRemoved;
      this.mediaObserver = mediaObserver;
      this.observer = null;
      this.shadowObservers = /* @__PURE__ */ new Set();
    }
    /**
     * Start observing DOM mutations
     * @param {Document} document - Document to observe
     */
    start(document2) {
      this.observer = new MutationObserver((mutations) => {
        requestIdleCallback(
          () => {
            this.processMutations(mutations);
          },
          { timeout: 2e3 }
        );
      });
      const observerOptions = {
        attributeFilter: ["aria-hidden", "data-focus-method", "style", "class"],
        childList: true,
        subtree: true
      };
      this.observer.observe(document2, observerOptions);
      window.VSC.logger.debug("Video mutation observer started");
    }
    /**
     * Process mutation events
     * @param {Array<MutationRecord>} mutations - Mutation records
     * @private
     */
    processMutations(mutations) {
      mutations.forEach((mutation) => {
        switch (mutation.type) {
          case "childList":
            this.processChildListMutation(mutation);
            break;
          case "attributes":
            this.processAttributeMutation(mutation);
            break;
        }
      });
    }
    /**
     * Process child list mutations (added/removed nodes)
     * @param {MutationRecord} mutation - Mutation record
     * @private
     */
    processChildListMutation(mutation) {
      mutation.addedNodes.forEach((node) => {
        if (!node || node.nodeType !== Node.ELEMENT_NODE) {
          return;
        }
        if (node === document.documentElement) {
          window.VSC.logger.debug("Document was replaced, reinitializing");
          this.onDocumentReplaced();
          return;
        }
        this.checkForVideoAndShadowRoot(node, node.parentNode || mutation.target, true);
      });
      mutation.removedNodes.forEach((node) => {
        if (!node || node.nodeType !== Node.ELEMENT_NODE) {
          return;
        }
        this.checkForVideoAndShadowRoot(node, node.parentNode || mutation.target, false);
      });
    }
    /**
     * Process attribute mutations
     * @param {MutationRecord} mutation - Mutation record
     * @private
     */
    processAttributeMutation(mutation) {
      if (mutation.attributeName === "style" || mutation.attributeName === "class") {
        this.handleVisibilityChanges(mutation.target);
      }
      if (mutation.target.attributes["aria-hidden"] && mutation.target.attributes["aria-hidden"].value === "false" || mutation.target.nodeName === "APPLE-TV-PLUS-PLAYER") {
        const flattenedNodes = window.VSC.DomUtils.getShadow(document.body);
        const videoNodes = flattenedNodes.filter((x) => x.tagName === "VIDEO");
        for (const node of videoNodes) {
          if (node.vsc && mutation.target.nodeName === "APPLE-TV-PLUS-PLAYER") {
            continue;
          }
          if (node.vsc) {
            node.vsc.remove();
          }
          this.checkForVideoAndShadowRoot(node, node.parentNode || mutation.target, true);
        }
      }
    }
    /**
     * Handle visibility changes on elements that might contain videos
     * @param {Element} element - Element that had style/class changes
     * @private
     */
    handleVisibilityChanges(element) {
      if (element.tagName === "VIDEO" || element.tagName === "AUDIO" && this.config.settings.audioBoolean) {
        this.recheckVideoElement(element);
        return;
      }
      const audioEnabled = this.config.settings.audioBoolean;
      const mediaTagSelector = audioEnabled ? "video,audio" : "video";
      const videos = element.querySelectorAll ? element.querySelectorAll(mediaTagSelector) : [];
      videos.forEach((video) => {
        this.recheckVideoElement(video);
      });
    }
    /**
     * Re-check if a video element should have a controller attached
     * @param {HTMLMediaElement} video - Video element to recheck
     * @private
     */
    recheckVideoElement(video) {
      if (!this.mediaObserver) {
        return;
      }
      if (video.vsc) {
        if (!this.mediaObserver.isValidMediaElement(video)) {
          window.VSC.logger.debug("Video became invalid, removing controller");
          video.vsc.remove();
          video.vsc = null;
        } else {
          video.vsc.updateVisibility();
        }
      } else {
        if (this.mediaObserver.isValidMediaElement(video)) {
          window.VSC.logger.debug("Video became valid, attaching controller");
          this.onVideoFound(video, video.parentElement || video.parentNode);
        }
      }
    }
    /**
     * Check if node is or contains video elements
     * @param {Node} node - Node to check
     * @param {Node} parent - Parent node
     * @param {boolean} added - True if node was added, false if removed
     * @private
     */
    checkForVideoAndShadowRoot(node, parent, added) {
      if (!added && document.body?.contains(node)) {
        return;
      }
      if (node.nodeName === "VIDEO" || node.nodeName === "AUDIO" && this.config.settings.audioBoolean) {
        if (added) {
          this.onVideoFound(node, parent);
        } else {
          if (node.vsc) {
            this.onVideoRemoved(node);
          }
        }
      } else {
        this.processNodeChildren(node, parent, added);
      }
    }
    /**
     * Process children of a node recursively
     * @param {Node} node - Node to process
     * @param {Node} parent - Parent node
     * @param {boolean} added - True if node was added
     * @private
     */
    processNodeChildren(node, parent, added) {
      let children = [];
      if (node.shadowRoot) {
        this.observeShadowRoot(node.shadowRoot);
        children = Array.from(node.shadowRoot.children);
      }
      if (node.children) {
        children = [...children, ...Array.from(node.children)];
      }
      for (const child of children) {
        this.checkForVideoAndShadowRoot(child, child.parentNode || parent, added);
      }
    }
    /**
     * Set up observer for shadow root
     * @param {ShadowRoot} shadowRoot - Shadow root to observe
     * @private
     */
    observeShadowRoot(shadowRoot) {
      if (this.shadowObservers.has(shadowRoot)) {
        return;
      }
      const shadowObserver = new MutationObserver((mutations) => {
        requestIdleCallback(
          () => {
            this.processMutations(mutations);
          },
          { timeout: 500 }
        );
      });
      const observerOptions = {
        attributeFilter: ["aria-hidden", "data-focus-method"],
        childList: true,
        subtree: true
      };
      shadowObserver.observe(shadowRoot, observerOptions);
      this.shadowObservers.add(shadowRoot);
      window.VSC.logger.debug("Shadow root observer added");
    }
    /**
     * Handle document replacement
     * @private
     */
    onDocumentReplaced() {
      window.VSC.logger.warn("Document replacement detected - full reinitialization needed");
    }
    /**
     * Stop observing and clean up
     */
    stop() {
      if (this.observer) {
        this.observer.disconnect();
        this.observer = null;
      }
      this.shadowObservers.forEach((_shadowRoot) => {
      });
      this.shadowObservers.clear();
      window.VSC.logger.debug("Video mutation observer stopped");
    }
  };
  window.VSC.VideoMutationObserver = VideoMutationObserver;

  // src/core/action-handler.js
  window.VSC = window.VSC || {};
  var ActionHandler = class {
    constructor(config, eventManager) {
      this.config = config;
      this.eventManager = eventManager;
    }
    /**
     * Execute an action on media elements
     * @param {string} action - Action to perform
     * @param {*} value - Action value
     * @param {Event} e - Event object (optional)
     */
    runAction(action, value, e) {
      const mediaTags = window.VSC.stateManager ? window.VSC.stateManager.getControlledElements() : [];
      let targetController = null;
      if (e) {
        targetController = e.target.getRootNode().host;
      }
      mediaTags.forEach((v) => {
        const controller = v.vsc?.div;
        if (!controller) {
          return;
        }
        if (e && targetController && !(targetController === controller)) {
          return;
        }
        this.eventManager.showController(controller);
        if (!v.classList.contains("vsc-cancelled")) {
          this.executeAction(action, value, v, e);
        }
      });
    }
    /**
     * Execute specific action on a video element
     * @param {string} action - Action to perform
     * @param {*} value - Action value
     * @param {HTMLMediaElement} video - Video element
     * @param {Event} e - Event object (optional)
     * @private
     */
    executeAction(action, value, video, e) {
      switch (action) {
        case "rewind":
          window.VSC.logger.debug("Rewind");
          this.seek(video, -value);
          break;
        case "advance":
          window.VSC.logger.debug("Fast forward");
          this.seek(video, value);
          break;
        case "faster": {
          window.VSC.logger.debug("Increase speed");
          this.adjustSpeed(video, value, { relative: true });
          break;
        }
        case "slower": {
          window.VSC.logger.debug("Decrease speed");
          this.adjustSpeed(video, -value, { relative: true });
          break;
        }
        case "reset":
          window.VSC.logger.debug("Reset speed");
          this.resetSpeed(video, value);
          break;
        case "display": {
          window.VSC.logger.debug("Display action triggered");
          const controller = video.vsc.div;
          if (!controller) {
            window.VSC.logger.error("No controller found for video");
            return;
          }
          controller.classList.add("vsc-manual");
          controller.classList.toggle("vsc-hidden");
          if (controller.blinkTimeOut !== void 0) {
            clearTimeout(controller.blinkTimeOut);
            controller.blinkTimeOut = void 0;
          }
          if (this.eventManager && this.eventManager.timer) {
            clearTimeout(this.eventManager.timer);
            this.eventManager.timer = null;
          }
          if (controller.classList.contains("vsc-hidden")) {
            controller.classList.remove("vsc-show");
            window.VSC.logger.debug("Removed vsc-show class for immediate manual hide");
          }
          break;
        }
        case "blink":
          window.VSC.logger.debug("Showing controller momentarily");
          this.blinkController(video.vsc.div, value);
          break;
        case "drag":
          window.VSC.DragHandler.handleDrag(video, e);
          break;
        case "fast":
          this.resetSpeed(video, value);
          break;
        case "pause":
          this.pause(video);
          break;
        case "muted":
          this.muted(video);
          break;
        case "louder":
          this.volumeUp(video, value);
          break;
        case "softer":
          this.volumeDown(video, value);
          break;
        case "mark":
          this.setMark(video);
          break;
        case "jump":
          this.jumpToMark(video);
          break;
        case "SET_SPEED":
          window.VSC.logger.info("Setting speed to:", value);
          this.adjustSpeed(video, value, { source: "internal" });
          break;
        case "ADJUST_SPEED":
          window.VSC.logger.info("Adjusting speed by:", value);
          this.adjustSpeed(video, value, { relative: true, source: "internal" });
          break;
        case "RESET_SPEED": {
          window.VSC.logger.info("Resetting speed");
          const preferredSpeed = this.config.getKeyBinding("fast") || 1;
          this.adjustSpeed(video, preferredSpeed, { source: "internal" });
          break;
        }
        default:
          window.VSC.logger.warn(`Unknown action: ${action}`);
      }
    }
    /**
     * Seek video by specified seconds
     * @param {HTMLMediaElement} video - Video element
     * @param {number} seekSeconds - Seconds to seek
     */
    seek(video, seekSeconds) {
      window.VSC.siteHandlerManager.handleSeek(video, seekSeconds);
    }
    /**
     * Toggle pause/play
     * @param {HTMLMediaElement} video - Video element
     */
    pause(video) {
      if (video.paused) {
        window.VSC.logger.debug("Resuming video");
        video.play();
      } else {
        window.VSC.logger.debug("Pausing video");
        video.pause();
      }
    }
    /**
     * Reset speed with memory toggle functionality
     * @param {HTMLMediaElement} video - Video element
     * @param {number} target - Target speed (usually 1.0)
     */
    resetSpeed(video, target) {
      if (video.vsc?.div && this.eventManager) {
        this.eventManager.showController(video.vsc.div);
      }
      if (!video.vsc) {
        window.VSC.logger.warn("resetSpeed called on video without controller");
        return;
      }
      const currentSpeed = video.playbackRate;
      if (currentSpeed === target) {
        if (video.vsc.speedBeforeReset !== null) {
          window.VSC.logger.info(`Restoring remembered speed: ${video.vsc.speedBeforeReset}`);
          const rememberedSpeed = video.vsc.speedBeforeReset;
          video.vsc.speedBeforeReset = null;
          this.adjustSpeed(video, rememberedSpeed);
        } else {
          window.VSC.logger.info(`Already at reset speed ${target}, no change`);
        }
      } else {
        window.VSC.logger.info(`Remembering speed ${currentSpeed} and resetting to ${target}`);
        video.vsc.speedBeforeReset = currentSpeed;
        this.adjustSpeed(video, target);
      }
    }
    /**
     * Toggle mute
     * @param {HTMLMediaElement} video - Video element
     */
    muted(video) {
      video.muted = video.muted !== true;
    }
    /**
     * Increase volume
     * @param {HTMLMediaElement} video - Video element
     * @param {number} value - Amount to increase
     */
    volumeUp(video, value) {
      video.volume = Math.min(1, (video.volume + value).toFixed(2));
    }
    /**
     * Decrease volume
     * @param {HTMLMediaElement} video - Video element
     * @param {number} value - Amount to decrease
     */
    volumeDown(video, value) {
      video.volume = Math.max(0, (video.volume - value).toFixed(2));
    }
    /**
     * Set time marker
     * @param {HTMLMediaElement} video - Video element
     */
    setMark(video) {
      window.VSC.logger.debug("Adding marker");
      video.vsc.mark = video.currentTime;
    }
    /**
     * Jump to time marker
     * @param {HTMLMediaElement} video - Video element
     */
    jumpToMark(video) {
      window.VSC.logger.debug("Recalling marker");
      if (video.vsc.mark && typeof video.vsc.mark === "number") {
        video.currentTime = video.vsc.mark;
      }
    }
    /**
     * Show controller briefly
     * @param {HTMLElement} controller - Controller element
     * @param {number} duration - Duration in ms (default 1000)
     */
    blinkController(controller, duration) {
      const isAudioController = this.isAudioController(controller);
      if (controller.blinkTimeOut !== void 0) {
        clearTimeout(controller.blinkTimeOut);
        controller.blinkTimeOut = void 0;
      }
      controller.classList.add("vsc-show");
      window.VSC.logger.debug("Showing controller temporarily with vsc-show class");
      if (!isAudioController) {
        controller.blinkTimeOut = setTimeout(
          () => {
            controller.classList.remove("vsc-show");
            controller.blinkTimeOut = void 0;
            window.VSC.logger.debug("Removing vsc-show class after timeout");
          },
          duration ? duration : 2500
        );
      } else {
        window.VSC.logger.debug("Audio controller blink - keeping vsc-show class");
      }
    }
    /**
     * Check if controller is associated with an audio element
     * @param {HTMLElement} controller - Controller element
     * @returns {boolean} True if associated with audio element
     * @private
     */
    isAudioController(controller) {
      const mediaElements = window.VSC.stateManager ? window.VSC.stateManager.getControlledElements() : [];
      for (const media of mediaElements) {
        if (media.vsc && media.vsc.div === controller) {
          return media.tagName === "AUDIO";
        }
      }
      return false;
    }
    /**
     * Adjust video playback speed (absolute or relative)
     * Simplified to use proven working logic from setSpeed method
     *
     * @param {HTMLMediaElement} video - Target video element
     * @param {number} value - Speed value (absolute) or delta (relative)
     * @param {Object} options - Configuration options
     * @param {boolean} options.relative - If true, value is a delta; if false, absolute speed
     * @param {string} options.source - 'internal' (user action) or 'external' (site/other)
     */
    adjustSpeed(video, value, options = {}) {
      return window.VSC.logger.withContext(video, () => {
        const { relative = false, source = "internal" } = options;
        window.VSC.logger.debug(`adjustSpeed called: value=${value}, relative=${relative}, source=${source}`);
        const stack = new Error().stack;
        const stackLines = stack.split("\n").slice(1, 8);
        window.VSC.logger.debug(`adjustSpeed call stack: ${stackLines.join(" -> ")}`);
        if (!video || !video.vsc) {
          window.VSC.logger.warn("adjustSpeed called on video without controller");
          return;
        }
        if (typeof value !== "number" || isNaN(value)) {
          window.VSC.logger.warn("adjustSpeed called with invalid value:", value);
          return;
        }
        return this._adjustSpeedInternal(video, value, options);
      });
    }
    /**
     * Internal adjustSpeed implementation (context already set)
     * @private
     */
    _adjustSpeedInternal(video, value, options) {
      const { relative = false, source = "internal" } = options;
      if (video.vsc?.div && this.eventManager) {
        this.eventManager.showController(video.vsc.div);
      }
      let targetSpeed;
      if (relative) {
        const currentSpeed = video.playbackRate < 0.1 ? 0 : video.playbackRate;
        targetSpeed = currentSpeed + value;
        window.VSC.logger.debug(`Relative speed calculation: currentSpeed=${currentSpeed} + ${value} = ${targetSpeed}`);
      } else {
        targetSpeed = value;
        window.VSC.logger.debug(`Absolute speed set: ${targetSpeed}`);
      }
      targetSpeed = Math.min(
        Math.max(targetSpeed, window.VSC.Constants.SPEED_LIMITS.MIN),
        window.VSC.Constants.SPEED_LIMITS.MAX
      );
      targetSpeed = Number(targetSpeed.toFixed(2));
      if (source === "external" && this.config.settings.forceLastSavedSpeed) {
        targetSpeed = this.config.settings.lastSpeed || 1;
        window.VSC.logger.debug(`Force mode: blocking external change, restoring to ${targetSpeed}`);
      }
      this.setSpeed(video, targetSpeed, source);
    }
    /**
     * Get user's preferred speed (always global lastSpeed)
     * Public method for tests - matches VideoController.getTargetSpeed() logic
     * @param {HTMLMediaElement} video - Video element (for API compatibility) 
     * @returns {number} Current preferred speed (always lastSpeed regardless of rememberSpeed setting)
     */
    getPreferredSpeed(video) {
      return this.config.settings.lastSpeed || 1;
    }
    /**
     * Set video playback speed with complete state management
     * Unified implementation with all functionality - no fragmented logic
     * @param {HTMLMediaElement} video - Video element
     * @param {number} speed - Target speed
     * @param {string} source - Change source: 'internal' (user/extension) or 'external' (site)
     */
    setSpeed(video, speed, source = "internal") {
      const speedValue = speed.toFixed(2);
      const numericSpeed = Number(speedValue);
      video.playbackRate = numericSpeed;
      video.dispatchEvent(
        new CustomEvent("ratechange", {
          bubbles: true,
          composed: true,
          detail: {
            origin: "videoSpeed",
            speed: speedValue,
            source
          }
        })
      );
      const speedIndicator = video.vsc?.speedIndicator;
      if (!speedIndicator) {
        window.VSC.logger.warn(
          "Cannot update speed indicator: video controller UI not fully initialized"
        );
        return;
      }
      speedIndicator.textContent = numericSpeed.toFixed(2);
      window.VSC.logger.debug(`Updating config.settings.lastSpeed from ${this.config.settings.lastSpeed} to ${numericSpeed}`);
      this.config.settings.lastSpeed = numericSpeed;
      if (this.config.settings.rememberSpeed) {
        window.VSC.logger.debug(`Saving lastSpeed ${numericSpeed} to Chrome storage`);
        this.config.save({
          lastSpeed: this.config.settings.lastSpeed
        });
      } else {
        window.VSC.logger.debug("NOT saving to storage - rememberSpeed is false");
      }
      if (video.vsc?.div) {
        this.blinkController(video.vsc.div);
      }
      if (this.eventManager) {
        this.eventManager.refreshCoolDown();
      }
    }
  };
  window.VSC.ActionHandler = ActionHandler;

  // src/core/video-controller.js
  window.VSC = window.VSC || {};
  var VideoController = class {
    constructor(target, parent, config, actionHandler, shouldStartHidden = false) {
      if (target.vsc) {
        return target.vsc;
      }
      this.video = target;
      this.parent = target.parentElement || parent;
      this.config = config;
      this.actionHandler = actionHandler;
      this.controlsManager = new window.VSC.ControlsManager(actionHandler, config);
      this.shouldStartHidden = shouldStartHidden;
      this.controllerId = this.generateControllerId(target);
      this.speedBeforeReset = null;
      target.vsc = this;
      if (window.VSC.stateManager) {
        window.VSC.stateManager.registerController(this);
      } else {
        window.VSC.logger.error("StateManager not available during VideoController initialization");
      }
      this.initializeSpeed();
      this.div = this.initializeControls();
      this.setupEventHandlers();
      this.setupMutationObserver();
      window.VSC.logger.info("VideoController initialized for video element");
    }
    /**
     * Initialize video speed based on settings
     * @private
     */
    initializeSpeed() {
      const targetSpeed = this.getTargetSpeed();
      window.VSC.logger.debug(`Setting initial playbackRate to: ${targetSpeed}`);
      if (this.actionHandler && targetSpeed !== this.video.playbackRate) {
        window.VSC.logger.debug("Setting initial speed via adjustSpeed");
        this.actionHandler.adjustSpeed(this.video, targetSpeed, { source: "internal" });
      }
    }
    /**
     * Get target speed based on rememberSpeed setting and update reset binding
     * @param {HTMLMediaElement} media - Optional media element (defaults to this.video)
     * @returns {number} Target speed
     * @private
     */
    getTargetSpeed(media = this.video) {
      const targetSpeed = this.config.settings.lastSpeed || 1;
      if (this.config.settings.rememberSpeed) {
        window.VSC.logger.debug(`Remember mode: using lastSpeed ${targetSpeed} (changes will be saved)`);
      } else {
        window.VSC.logger.debug(`Non-persistent mode: using lastSpeed ${targetSpeed} (changes won't be saved)`);
      }
      return targetSpeed;
    }
    /**
     * Initialize video controller UI
     * @returns {HTMLElement} Controller wrapper element
     * @private
     */
    initializeControls() {
      window.VSC.logger.debug("initializeControls Begin");
      const document2 = this.video.ownerDocument;
      const speed = window.VSC.Constants.formatSpeed(this.video.playbackRate);
      const position = window.VSC.ShadowDOMManager.calculatePosition(this.video);
      window.VSC.logger.debug(`Speed variable set to: ${speed}`);
      const wrapper = document2.createElement("vsc-controller");
      const cssClasses = ["vsc-controller"];
      if (!this.video.currentSrc && !this.video.src && this.video.readyState < 2) {
        cssClasses.push("vsc-nosource");
      }
      if (this.config.settings.startHidden || this.shouldStartHidden) {
        cssClasses.push("vsc-hidden");
        window.VSC.logger.debug("Starting controller hidden");
      }
      wrapper.className = cssClasses.join(" ");
      const styleText = `
      position: absolute !important;
      z-index: 9999999 !important;
      top: ${position.top};
      left: ${position.left};
    `;
      wrapper.style.cssText = styleText;
      const shadow = window.VSC.ShadowDOMManager.createShadowDOM(wrapper, {
        top: "0px",
        // Position relative to shadow root since wrapper is already positioned
        left: "0px",
        // Position relative to shadow root since wrapper is already positioned
        speed,
        opacity: this.config.settings.controllerOpacity,
        buttonSize: this.config.settings.controllerButtonSize
      });
      this.controlsManager.setupControlEvents(shadow, this.video);
      this.speedIndicator = window.VSC.ShadowDOMManager.getSpeedIndicator(shadow);
      this.insertIntoDOM(document2, wrapper);
      window.VSC.logger.debug("initializeControls End");
      return wrapper;
    }
    /**
     * Insert controller into DOM with site-specific positioning
     * @param {Document} document - Document object
     * @param {HTMLElement} wrapper - Wrapper element to insert
     * @private
     */
    insertIntoDOM(document2, wrapper) {
      const fragment = document2.createDocumentFragment();
      fragment.appendChild(wrapper);
      const positioning = window.VSC.siteHandlerManager.getControllerPosition(
        this.parent,
        this.video
      );
      switch (positioning.insertionMethod) {
        case "beforeParent":
          positioning.insertionPoint.parentElement.insertBefore(fragment, positioning.insertionPoint);
          break;
        case "afterParent":
          positioning.insertionPoint.parentElement.insertBefore(
            fragment,
            positioning.insertionPoint.nextSibling
          );
          break;
        case "firstChild":
        default:
          positioning.insertionPoint.insertBefore(fragment, positioning.insertionPoint.firstChild);
          break;
      }
      window.VSC.logger.debug(`Controller inserted using ${positioning.insertionMethod} method`);
    }
    /**
     * Set up event handlers for media events
     * @private
     */
    setupEventHandlers() {
      const mediaEventAction = (event) => {
        const targetSpeed = this.getTargetSpeed(event.target);
        window.VSC.logger.info(`Media event ${event.type}: restoring speed to ${targetSpeed}`);
        this.actionHandler.adjustSpeed(event.target, targetSpeed, { source: "internal" });
      };
      this.handlePlay = mediaEventAction.bind(this);
      this.handleSeek = mediaEventAction.bind(this);
      this.video.addEventListener("play", this.handlePlay);
      this.video.addEventListener("seeked", this.handleSeek);
      window.VSC.logger.debug(
        "Added essential media event handlers: play, seeked"
      );
    }
    /**
     * Set up mutation observer for src attribute changes
     * @private
     */
    setupMutationObserver() {
      this.targetObserver = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.type === "attributes" && (mutation.attributeName === "src" || mutation.attributeName === "currentSrc")) {
            window.VSC.logger.debug("Mutation of A/V element detected");
            const controller = this.div;
            if (!mutation.target.src && !mutation.target.currentSrc) {
              controller.classList.add("vsc-nosource");
            } else {
              controller.classList.remove("vsc-nosource");
            }
          }
        });
      });
      this.targetObserver.observe(this.video, {
        attributeFilter: ["src", "currentSrc"]
      });
    }
    /**
     * Remove controller and clean up
     */
    remove() {
      window.VSC.logger.debug("Removing VideoController");
      if (this.div && this.div.parentNode) {
        this.div.remove();
      }
      if (this.handlePlay) {
        this.video.removeEventListener("play", this.handlePlay);
      }
      if (this.handleSeek) {
        this.video.removeEventListener("seeked", this.handleSeek);
      }
      if (this.targetObserver) {
        this.targetObserver.disconnect();
      }
      if (window.VSC.stateManager) {
        window.VSC.stateManager.removeController(this.controllerId);
      }
      delete this.video.vsc;
      window.VSC.logger.debug("VideoController removed successfully");
    }
    /**
     * Generate unique controller ID for badge tracking
     * @param {HTMLElement} target - Video/audio element
     * @returns {string} Unique controller ID
     * @private
     */
    generateControllerId(target) {
      const timestamp = Date.now();
      const src = target.currentSrc || target.src || "no-src";
      const tagName = target.tagName.toLowerCase();
      const srcHash = src.split("").reduce((hash, char) => {
        hash = (hash << 5) - hash + char.charCodeAt(0);
        return hash & hash;
      }, 0);
      const random = Math.floor(Math.random() * 1e3);
      return `${tagName}-${Math.abs(srcHash)}-${timestamp}-${random}`;
    }
    /**
     * Check if the video element is currently visible
     * @returns {boolean} True if video is visible
     */
    isVideoVisible() {
      if (!this.video.isConnected) {
        return false;
      }
      const style = window.getComputedStyle(this.video);
      if (style.display === "none" || style.visibility === "hidden" || style.opacity === "0") {
        return false;
      }
      const rect = this.video.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) {
        return false;
      }
      return true;
    }
    /**
     * Update controller visibility based on video visibility
     * Called when video visibility changes
     */
    updateVisibility() {
      const isVisible = this.isVideoVisible();
      const isCurrentlyHidden = this.div.classList.contains("vsc-hidden");
      if (this.video.tagName === "AUDIO") {
        if (!this.config.settings.audioBoolean && !isCurrentlyHidden) {
          this.div.classList.add("vsc-hidden");
          window.VSC.logger.debug("Hiding audio controller - audio support disabled");
        } else if (this.config.settings.audioBoolean && isCurrentlyHidden && !this.div.classList.contains("vsc-manual")) {
          this.div.classList.remove("vsc-hidden");
          window.VSC.logger.debug("Showing audio controller - audio support enabled");
        }
        return;
      }
      if (isVisible && isCurrentlyHidden && !this.div.classList.contains("vsc-manual") && !this.config.settings.startHidden) {
        this.div.classList.remove("vsc-hidden");
        window.VSC.logger.debug("Showing controller - video became visible");
      } else if (!isVisible && !isCurrentlyHidden) {
        this.div.classList.add("vsc-hidden");
        window.VSC.logger.debug("Hiding controller - video became invisible");
      }
    }
  };
  window.VSC.VideoController = VideoController;

  // src/ui/controls.js
  window.VSC = window.VSC || {};
  var ControlsManager = class {
    constructor(actionHandler, config) {
      this.actionHandler = actionHandler;
      this.config = config;
    }
    /**
     * Set up control button event listeners
     * @param {ShadowRoot} shadow - Shadow root containing controls
     * @param {HTMLVideoElement} video - Associated video element
     */
    setupControlEvents(shadow, video) {
      this.setupDragHandler(shadow);
      this.setupButtonHandlers(shadow);
      this.setupWheelHandler(shadow, video);
      this.setupClickPrevention(shadow);
    }
    /**
     * Set up drag handler for speed indicator
     * @param {ShadowRoot} shadow - Shadow root
     * @private
     */
    setupDragHandler(shadow) {
      const draggable = shadow.querySelector(".draggable");
      draggable.addEventListener(
        "mousedown",
        (e) => {
          this.actionHandler.runAction(e.target.dataset["action"], false, e);
          e.stopPropagation();
          e.preventDefault();
        },
        true
      );
    }
    /**
     * Set up button click handlers
     * @param {ShadowRoot} shadow - Shadow root
     * @private
     */
    setupButtonHandlers(shadow) {
      shadow.querySelectorAll("button").forEach((button) => {
        button.addEventListener(
          "click",
          (e) => {
            this.actionHandler.runAction(
              e.target.dataset["action"],
              this.config.getKeyBinding(e.target.dataset["action"]),
              e
            );
            e.stopPropagation();
          },
          true
        );
        button.addEventListener(
          "touchstart",
          (e) => {
            e.stopPropagation();
          },
          true
        );
      });
    }
    /**
     * Set up mouse wheel handler for speed control with touchpad filtering
     * 
     * Cross-browser wheel event behavior:
     * - Chrome/Safari/Edge: ALL devices use DOM_DELTA_PIXEL (mouse wheels ~100px, touchpads ~1-15px)
     * - Firefox: Mouse wheels use DOM_DELTA_LINE, touchpads use DOM_DELTA_PIXEL
     * 
     * Detection strategy: Use magnitude threshold in DOM_DELTA_PIXEL mode to distinguish
     * mouse wheels (±100px typical) from touchpads (±1-15px typical). Threshold of 50px
     * provides safety margin based on empirical browser testing.
     * 
     * @param {ShadowRoot} shadow - Shadow root
     * @param {HTMLVideoElement} video - Video element
     * @private
     */
    setupWheelHandler(shadow, video) {
      const controller = shadow.querySelector("#controller");
      controller.addEventListener(
        "wheel",
        (event) => {
          if (event.deltaMode === event.DOM_DELTA_PIXEL) {
            const TOUCHPAD_THRESHOLD = 50;
            if (Math.abs(event.deltaY) < TOUCHPAD_THRESHOLD) {
              window.VSC.logger.debug(`Touchpad scroll detected (deltaY: ${event.deltaY}) - ignoring`);
              return;
            }
          }
          event.preventDefault();
          const delta = Math.sign(event.deltaY);
          const step = 0.1;
          const speedDelta = delta < 0 ? step : -step;
          this.actionHandler.adjustSpeed(video, speedDelta, { relative: true });
          window.VSC.logger.debug(`Wheel control: adjusting speed by ${speedDelta} (deltaMode: ${event.deltaMode}, deltaY: ${event.deltaY})`);
        },
        { passive: false }
      );
    }
    /**
     * Set up click prevention for controller container
     * @param {ShadowRoot} shadow - Shadow root
     * @private
     */
    setupClickPrevention(shadow) {
      const controller = shadow.querySelector("#controller");
      controller.addEventListener("click", (e) => e.stopPropagation(), false);
      controller.addEventListener("mousedown", (e) => e.stopPropagation(), false);
    }
  };
  window.VSC.ControlsManager = ControlsManager;

  // src/ui/drag-handler.js
  window.VSC = window.VSC || {};
  var DragHandler = class {
    /**
     * Handle dragging of video controller
     * @param {HTMLVideoElement} video - Video element
     * @param {MouseEvent} e - Mouse event
     */
    static handleDrag(video, e) {
      const controller = video.vsc.div;
      const shadowController = controller.shadowRoot.querySelector("#controller");
      const parentElement = window.VSC.DomUtils.findVideoParent(controller);
      video.classList.add("vcs-dragging");
      shadowController.classList.add("dragging");
      const initialMouseXY = [e.clientX, e.clientY];
      const initialControllerXY = [
        parseInt(shadowController.style.left) || 0,
        parseInt(shadowController.style.top) || 0
      ];
      const startDragging = (e2) => {
        const style = shadowController.style;
        const dx = e2.clientX - initialMouseXY[0];
        const dy = e2.clientY - initialMouseXY[1];
        style.left = `${initialControllerXY[0] + dx}px`;
        style.top = `${initialControllerXY[1] + dy}px`;
      };
      const stopDragging = () => {
        parentElement.removeEventListener("mousemove", startDragging);
        parentElement.removeEventListener("mouseup", stopDragging);
        parentElement.removeEventListener("mouseleave", stopDragging);
        shadowController.classList.remove("dragging");
        video.classList.remove("vcs-dragging");
        window.VSC.logger.debug("Drag operation completed");
      };
      parentElement.addEventListener("mouseup", stopDragging);
      parentElement.addEventListener("mouseleave", stopDragging);
      parentElement.addEventListener("mousemove", startDragging);
      window.VSC.logger.debug("Drag operation started");
    }
  };
  window.VSC.DragHandler = DragHandler;

  // src/ui/shadow-dom.js
  window.VSC = window.VSC || {};
  var ShadowDOMManager = class {
    /**
     * Create shadow DOM for video controller
     * @param {HTMLElement} wrapper - Wrapper element
     * @param {Object} options - Configuration options
     * @returns {ShadowRoot} Created shadow root
     */
    static createShadowDOM(wrapper, options = {}) {
      const { top = "0px", left = "0px", speed = "1.00", opacity = 0.3, buttonSize = 14 } = options;
      const shadow = wrapper.attachShadow({ mode: "open" });
      const style = document.createElement("style");
      style.textContent = `
      * {
        line-height: 1.8em;
        font-family: sans-serif;
        font-size: 13px;
      }
      
      :host(:hover) #controls {
        display: inline-block;
      }
      
      /* Hide shadow DOM content for different hiding scenarios */
      :host(.vsc-hidden) #controller,
      :host(.vsc-nosource) #controller {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
      }
      
      /* Override hiding for manual controllers (unless explicitly hidden) */
      :host(.vsc-manual:not(.vsc-hidden)) #controller {
        display: block !important;
        visibility: visible !important;
        opacity: ${opacity} !important;
      }
      
      /* Show shadow DOM content when host has vsc-show class (highest priority) */
      :host(.vsc-show) #controller {
        display: block !important;
        visibility: visible !important;
        opacity: ${opacity} !important;
      }
      
      #controller {
        position: absolute;
        top: 0;
        left: 0;
        background: black;
        color: white;
        border-radius: 6px;
        padding: 4px;
        margin: 10px 10px 10px 15px;
        cursor: default;
        z-index: 9999999;
        white-space: nowrap;
      }
      
      #controller:hover {
        opacity: 0.7;
      }
      
      #controller:hover>.draggable {
        margin-right: 0.8em;
      }
      
      #controls {
        display: none;
        vertical-align: middle;
      }
      
      #controller.dragging {
        cursor: -webkit-grabbing;
        opacity: 0.7;
      }
      
      #controller.dragging #controls {
        display: inline-block;
      }
      
      .draggable {
        cursor: -webkit-grab;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 2.8em;
        height: 1.4em;
        text-align: center;
        vertical-align: middle;
        box-sizing: border-box;
      }
      
      .draggable:active {
        cursor: -webkit-grabbing;
      }
      
      button {
        opacity: 1;
        cursor: pointer;
        color: black;
        background: white;
        font-weight: normal;
        border-radius: 5px;
        padding: 1px 5px 3px 5px;
        font-size: inherit;
        line-height: inherit;
        border: 0px solid white;
        font-family: "Lucida Console", Monaco, monospace;
        margin: 0px 2px 2px 2px;
        transition: background 0.2s, color 0.2s;
      }
      
      button:focus {
        outline: 0;
      }
      
      button:hover {
        opacity: 1;
        background: #2196f3;
        color: #ffffff;
      }
      
      button:active {
        background: #2196f3;
        color: #ffffff;
        font-weight: bold;
      }
      
      button.rw {
        opacity: 0.65;
      }
      
      button.hideButton {
        opacity: 0.65;
        margin-left: 8px;
        margin-right: 2px;
      }
    `;
      shadow.appendChild(style);
      const controller = document.createElement("div");
      controller.id = "controller";
      controller.style.cssText = `top:${top}; left:${left}; opacity:${opacity};`;
      const draggable = document.createElement("span");
      draggable.setAttribute("data-action", "drag");
      draggable.className = "draggable";
      draggable.style.cssText = `font-size: ${buttonSize}px;`;
      draggable.textContent = speed;
      controller.appendChild(draggable);
      const controls = document.createElement("span");
      controls.id = "controls";
      controls.style.cssText = `font-size: ${buttonSize}px; line-height: ${buttonSize}px;`;
      const buttons = [
        { action: "rewind", text: "\xAB", class: "rw" },
        { action: "slower", text: "\u2212", class: "" },
        { action: "faster", text: "+", class: "" },
        { action: "advance", text: "\xBB", class: "rw" },
        { action: "display", text: "\xD7", class: "hideButton" }
      ];
      buttons.forEach((btnConfig) => {
        const button = document.createElement("button");
        button.setAttribute("data-action", btnConfig.action);
        if (btnConfig.class) {
          button.className = btnConfig.class;
        }
        button.textContent = btnConfig.text;
        controls.appendChild(button);
      });
      controller.appendChild(controls);
      shadow.appendChild(controller);
      window.VSC.logger.debug("Shadow DOM created for video controller");
      return shadow;
    }
    /**
     * Get controller element from shadow DOM
     * @param {ShadowRoot} shadow - Shadow root
     * @returns {HTMLElement} Controller element
     */
    static getController(shadow) {
      return shadow.querySelector("#controller");
    }
    /**
     * Get controls container from shadow DOM
     * @param {ShadowRoot} shadow - Shadow root
     * @returns {HTMLElement} Controls element
     */
    static getControls(shadow) {
      return shadow.querySelector("#controls");
    }
    /**
     * Get draggable speed indicator from shadow DOM
     * @param {ShadowRoot} shadow - Shadow root
     * @returns {HTMLElement} Speed indicator element
     */
    static getSpeedIndicator(shadow) {
      return shadow.querySelector(".draggable");
    }
    /**
     * Get all buttons from shadow DOM
     * @param {ShadowRoot} shadow - Shadow root
     * @returns {NodeList} Button elements
     */
    static getButtons(shadow) {
      return shadow.querySelectorAll("button");
    }
    /**
     * Update speed display in shadow DOM
     * @param {ShadowRoot} shadow - Shadow root
     * @param {number} speed - New speed value
     */
    static updateSpeedDisplay(shadow, speed) {
      const speedIndicator = this.getSpeedIndicator(shadow);
      if (speedIndicator) {
        speedIndicator.textContent = window.VSC.Constants.formatSpeed(speed);
      }
    }
    /**
     * Calculate position for controller based on video element
     * @param {HTMLVideoElement} video - Video element
     * @returns {Object} Position object with top and left properties
     */
    static calculatePosition(video) {
      const rect = video.getBoundingClientRect();
      const offsetRect = video.offsetParent?.getBoundingClientRect();
      const top = `${Math.max(rect.top - (offsetRect?.top || 0), 0)}px`;
      const left = `${Math.max(rect.left - (offsetRect?.left || 0), 0)}px`;
      return { top, left };
    }
  };
  window.VSC.ShadowDOMManager = ShadowDOMManager;

  // src/ui/vsc-controller-element.js
  window.VSC = window.VSC || {};
  var VSCControllerElement = class _VSCControllerElement extends HTMLElement {
    constructor() {
      super();
    }
    connectedCallback() {
      window.VSC.logger?.debug("VSC custom element connected to DOM");
    }
    disconnectedCallback() {
      window.VSC.logger?.debug("VSC custom element disconnected from DOM");
    }
    static register() {
      if (!customElements.get("vsc-controller")) {
        customElements.define("vsc-controller", _VSCControllerElement);
        window.VSC.logger?.info("VSC custom element registered");
      }
    }
  };
  window.VSC.VSCControllerElement = VSCControllerElement;
  VSCControllerElement.register();

  // src/site-handlers/base-handler.js
  window.VSC = window.VSC || {};
  var BaseSiteHandler = class {
    constructor() {
      this.hostname = location.hostname;
    }
    /**
     * Check if this handler applies to the current site
     * @returns {boolean} True if handler applies
     */
    static matches() {
      return false;
    }
    /**
     * Get the site-specific positioning for the controller
     * @param {HTMLElement} parent - Parent element
     * @param {HTMLElement} video - Video element
     * @returns {Object} Positioning information
     */
    getControllerPosition(parent, _video) {
      return {
        insertionPoint: parent,
        insertionMethod: "firstChild",
        // 'firstChild', 'beforeParent', 'afterParent'
        targetParent: parent
      };
    }
    /**
     * Handle site-specific seeking functionality
     * @param {HTMLMediaElement} video - Video element
     * @param {number} seekSeconds - Seconds to seek
     * @returns {boolean} True if handled, false for default behavior
     */
    handleSeek(video, seekSeconds) {
      if (video.currentTime !== void 0 && video.duration) {
        const newTime = Math.max(0, Math.min(video.duration, video.currentTime + seekSeconds));
        video.currentTime = newTime;
      } else {
        video.currentTime += seekSeconds;
      }
      return true;
    }
    /**
     * Handle site-specific initialization
     * @param {Document} document - Document object
     */
    initialize(_document) {
      window.VSC.logger.debug(`Initializing ${this.constructor.name} for ${this.hostname}`);
    }
    /**
     * Handle site-specific cleanup
     */
    cleanup() {
      window.VSC.logger.debug(`Cleaning up ${this.constructor.name}`);
    }
    /**
     * Check if video element should be ignored
     * @param {HTMLMediaElement} video - Video element
     * @returns {boolean} True if video should be ignored
     */
    shouldIgnoreVideo(_video) {
      return false;
    }
    /**
     * Get site-specific CSS selectors for video containers
     * @returns {Array<string>} CSS selectors
     */
    getVideoContainerSelectors() {
      return [];
    }
    /**
     * Handle special video detection logic
     * @param {Document} document - Document object
     * @returns {Array<HTMLMediaElement>} Additional videos found
     */
    detectSpecialVideos(_document) {
      return [];
    }
  };
  window.VSC.BaseSiteHandler = BaseSiteHandler;

  // src/site-handlers/netflix-handler.js
  window.VSC = window.VSC || {};
  var NetflixHandler = class extends window.VSC.BaseSiteHandler {
    /**
     * Check if this handler applies to Netflix
     * @returns {boolean} True if on Netflix
     */
    static matches() {
      return location.hostname === "www.netflix.com";
    }
    /**
     * Get Netflix-specific controller positioning
     * @param {HTMLElement} parent - Parent element
     * @param {HTMLElement} video - Video element
     * @returns {Object} Positioning information
     */
    getControllerPosition(parent, _video) {
      return {
        insertionPoint: parent.parentElement,
        insertionMethod: "beforeParent",
        targetParent: parent.parentElement
      };
    }
    /**
     * Handle Netflix-specific seeking using their API
     * @param {HTMLMediaElement} video - Video element
     * @param {number} seekSeconds - Seconds to seek
     * @returns {boolean} True if handled
     */
    handleSeek(video, seekSeconds) {
      try {
        window.postMessage(
          {
            action: "videospeed-seek",
            seekMs: seekSeconds * 1e3
          },
          "https://www.netflix.com"
        );
        window.VSC.logger.debug(`Netflix seek: ${seekSeconds} seconds`);
        return true;
      } catch (error) {
        window.VSC.logger.error(`Netflix seek failed: ${error.message}`);
        video.currentTime += seekSeconds;
        return true;
      }
    }
    /**
     * Initialize Netflix-specific functionality
     * @param {Document} document - Document object
     */
    initialize(document2) {
      super.initialize(document2);
      window.VSC.logger.debug(
        "Netflix handler initialized - script injection handled by content script"
      );
    }
    /**
     * Check if video should be ignored on Netflix
     * @param {HTMLMediaElement} video - Video element
     * @returns {boolean} True if video should be ignored
     */
    shouldIgnoreVideo(video) {
      return video.classList.contains("preview-video") || video.parentElement?.classList.contains("billboard-row");
    }
    /**
     * Get Netflix-specific video container selectors
     * @returns {Array<string>} CSS selectors
     */
    getVideoContainerSelectors() {
      return [".watch-video", ".nfp-container", "#netflix-player"];
    }
  };
  window.VSC.NetflixHandler = NetflixHandler;

  // src/site-handlers/youtube-handler.js
  window.VSC = window.VSC || {};
  var YouTubeHandler = class extends window.VSC.BaseSiteHandler {
    /**
     * Check if this handler applies to YouTube
     * @returns {boolean} True if on YouTube
     */
    static matches() {
      return location.hostname === "www.youtube.com";
    }
    /**
     * Get YouTube-specific controller positioning
     * @param {HTMLElement} parent - Parent element
     * @param {HTMLElement} video - Video element
     * @returns {Object} Positioning information
     */
    getControllerPosition(parent, _video) {
      const targetParent = parent.parentElement;
      return {
        insertionPoint: targetParent,
        insertionMethod: "firstChild",
        targetParent
      };
    }
    /**
     * Initialize YouTube-specific functionality
     * @param {Document} document - Document object
     */
    initialize(document2) {
      super.initialize(document2);
      this.setupYouTubeCSS();
    }
    /**
     * Set up YouTube-specific CSS classes and positioning
     * @private
     */
    setupYouTubeCSS() {
      window.VSC.logger.debug("YouTube CSS setup completed");
    }
    /**
     * Check if video should be ignored on YouTube
     * @param {HTMLMediaElement} video - Video element
     * @returns {boolean} True if video should be ignored
     */
    shouldIgnoreVideo(video) {
      return video.classList.contains("video-thumbnail") || video.parentElement?.classList.contains("ytp-ad-player-overlay");
    }
    /**
     * Get YouTube-specific video container selectors
     * @returns {Array<string>} CSS selectors
     */
    getVideoContainerSelectors() {
      return [".html5-video-player", "#movie_player", ".ytp-player-content"];
    }
    /**
     * Handle special video detection for YouTube
     * @param {Document} document - Document object
     * @returns {Array<HTMLMediaElement>} Additional videos found
     */
    detectSpecialVideos(document2) {
      const videos = [];
      try {
        const iframes = document2.querySelectorAll('iframe[src*="youtube.com"]');
        iframes.forEach((iframe) => {
          try {
            const iframeDoc = iframe.contentDocument;
            if (iframeDoc) {
              const iframeVideos = iframeDoc.querySelectorAll("video");
              videos.push(...Array.from(iframeVideos));
            }
          } catch (e) {
          }
        });
      } catch (e) {
        window.VSC.logger.debug(`Could not access YouTube iframe videos: ${e.message}`);
      }
      return videos;
    }
    /**
     * Handle YouTube-specific player state changes
     * @param {HTMLMediaElement} video - Video element
     */
    onPlayerStateChange(_video) {
      window.VSC.logger.debug("YouTube player state changed");
    }
  };
  window.VSC.YouTubeHandler = YouTubeHandler;

  // src/site-handlers/facebook-handler.js
  window.VSC = window.VSC || {};
  var FacebookHandler = class extends window.VSC.BaseSiteHandler {
    /**
     * Check if this handler applies to Facebook
     * @returns {boolean} True if on Facebook
     */
    static matches() {
      return location.hostname === "www.facebook.com";
    }
    /**
     * Get Facebook-specific controller positioning
     * @param {HTMLElement} parent - Parent element
     * @param {HTMLElement} video - Video element
     * @returns {Object} Positioning information
     */
    getControllerPosition(parent, _video) {
      let targetParent = parent;
      try {
        targetParent = parent.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement;
      } catch (e) {
        window.VSC.logger.warn("Facebook DOM structure changed, using fallback positioning");
        targetParent = parent.parentElement;
      }
      return {
        insertionPoint: targetParent,
        insertionMethod: "firstChild",
        targetParent
      };
    }
    /**
     * Initialize Facebook-specific functionality
     * @param {Document} document - Document object
     */
    initialize(document2) {
      super.initialize(document2);
      this.setupFacebookObserver(document2);
    }
    /**
     * Set up observer for Facebook's dynamic content loading
     * @param {Document} document - Document object
     * @private
     */
    setupFacebookObserver(document2) {
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.type === "childList" && mutation.addedNodes.length > 0) {
            mutation.addedNodes.forEach((node) => {
              if (node.nodeType === Node.ELEMENT_NODE) {
                const videos = node.querySelectorAll && node.querySelectorAll("video");
                if (videos && videos.length > 0) {
                  window.VSC.logger.debug(`Facebook: Found ${videos.length} new videos`);
                  this.onNewVideosDetected(Array.from(videos));
                }
              }
            });
          }
        });
      });
      observer.observe(document2.body, {
        childList: true,
        subtree: true
      });
      this.facebookObserver = observer;
      window.VSC.logger.debug("Facebook dynamic content observer set up");
    }
    /**
     * Handle new videos detected in Facebook's dynamic content
     * @param {Array<HTMLMediaElement>} videos - New video elements
     * @private
     */
    onNewVideosDetected(videos) {
      window.VSC.logger.debug(`Facebook: ${videos.length} new videos detected`);
    }
    /**
     * Check if video should be ignored on Facebook
     * @param {HTMLMediaElement} video - Video element
     * @returns {boolean} True if video should be ignored
     */
    shouldIgnoreVideo(video) {
      return video.closest("[data-story-id]") !== null || video.closest(".story-bucket-container") !== null || video.getAttribute("data-video-width") === "0";
    }
    /**
     * Get Facebook-specific video container selectors
     * @returns {Array<string>} CSS selectors
     */
    getVideoContainerSelectors() {
      return ["[data-video-id]", ".video-container", ".fbStoryVideoContainer", '[role="main"] video'];
    }
    /**
     * Cleanup Facebook-specific resources
     */
    cleanup() {
      super.cleanup();
      if (this.facebookObserver) {
        this.facebookObserver.disconnect();
        this.facebookObserver = null;
      }
    }
  };
  window.VSC.FacebookHandler = FacebookHandler;

  // src/site-handlers/amazon-handler.js
  window.VSC = window.VSC || {};
  var AmazonHandler = class extends window.VSC.BaseSiteHandler {
    /**
     * Check if this handler applies to Amazon
     * @returns {boolean} True if on Amazon
     */
    static matches() {
      return location.hostname === "www.amazon.com" || location.hostname === "www.primevideo.com" || location.hostname.includes("amazon.") || location.hostname.includes("primevideo.");
    }
    /**
     * Get Amazon-specific controller positioning
     * @param {HTMLElement} parent - Parent element
     * @param {HTMLElement} video - Video element
     * @returns {Object} Positioning information
     */
    getControllerPosition(parent, video) {
      if (!video.classList.contains("vjs-tech")) {
        return {
          insertionPoint: parent.parentElement,
          insertionMethod: "beforeParent",
          targetParent: parent.parentElement
        };
      }
      return super.getControllerPosition(parent, video);
    }
    /**
     * Check if video should be ignored on Amazon
     * @param {HTMLMediaElement} video - Video element
     * @returns {boolean} True if video should be ignored
     */
    shouldIgnoreVideo(video) {
      if (video.readyState < 2) {
        return false;
      }
      const rect = video.getBoundingClientRect();
      return rect.width < 200 || rect.height < 100;
    }
    /**
     * Get Amazon-specific video container selectors
     * @returns {Array<string>} CSS selectors
     */
    getVideoContainerSelectors() {
      return [".dv-player-container", ".webPlayerContainer", '[data-testid="video-player"]'];
    }
  };
  window.VSC.AmazonHandler = AmazonHandler;

  // src/site-handlers/apple-handler.js
  window.VSC = window.VSC || {};
  var AppleHandler = class extends window.VSC.BaseSiteHandler {
    /**
     * Check if this handler applies to Apple TV+
     * @returns {boolean} True if on Apple TV+
     */
    static matches() {
      return location.hostname === "tv.apple.com";
    }
    /**
     * Get Apple TV+-specific controller positioning
     * @param {HTMLElement} parent - Parent element
     * @param {HTMLElement} video - Video element
     * @returns {Object} Positioning information
     */
    getControllerPosition(parent, _video) {
      return {
        insertionPoint: parent.parentNode,
        insertionMethod: "firstChild",
        targetParent: parent.parentNode
      };
    }
    /**
     * Get Apple TV+-specific video container selectors
     * @returns {Array<string>} CSS selectors
     */
    getVideoContainerSelectors() {
      return ["apple-tv-plus-player", '[data-testid="player"]', ".video-container"];
    }
    /**
     * Handle special video detection for Apple TV+
     * @param {Document} document - Document object
     * @returns {Array<HTMLMediaElement>} Additional videos found
     */
    detectSpecialVideos(document2) {
      const applePlayer = document2.querySelector("apple-tv-plus-player");
      if (applePlayer && applePlayer.shadowRoot) {
        const videos = applePlayer.shadowRoot.querySelectorAll("video");
        return Array.from(videos);
      }
      return [];
    }
  };
  window.VSC.AppleHandler = AppleHandler;

  // src/site-handlers/index.js
  window.VSC = window.VSC || {};
  var SiteHandlerManager = class {
    constructor() {
      this.currentHandler = null;
      this.availableHandlers = [
        window.VSC.NetflixHandler,
        window.VSC.YouTubeHandler,
        window.VSC.FacebookHandler,
        window.VSC.AmazonHandler,
        window.VSC.AppleHandler
      ];
    }
    /**
     * Get the appropriate handler for the current site
     * @returns {BaseSiteHandler} Site handler instance
     */
    getCurrentHandler() {
      if (!this.currentHandler) {
        this.currentHandler = this.detectHandler();
      }
      return this.currentHandler;
    }
    /**
     * Detect which handler to use for the current site
     * @returns {BaseSiteHandler} Site handler instance
     * @private
     */
    detectHandler() {
      for (const HandlerClass of this.availableHandlers) {
        if (HandlerClass.matches()) {
          window.VSC.logger.info(`Using ${HandlerClass.name} for ${location.hostname}`);
          return new HandlerClass();
        }
      }
      window.VSC.logger.debug(`Using BaseSiteHandler for ${location.hostname}`);
      return new window.VSC.BaseSiteHandler();
    }
    /**
     * Initialize the current site handler
     * @param {Document} document - Document object
     */
    initialize(document2) {
      const handler = this.getCurrentHandler();
      handler.initialize(document2);
    }
    /**
     * Get controller positioning for current site
     * @param {HTMLElement} parent - Parent element
     * @param {HTMLElement} video - Video element
     * @returns {Object} Positioning information
     */
    getControllerPosition(parent, video) {
      const handler = this.getCurrentHandler();
      return handler.getControllerPosition(parent, video);
    }
    /**
     * Handle seeking for current site
     * @param {HTMLMediaElement} video - Video element
     * @param {number} seekSeconds - Seconds to seek
     * @returns {boolean} True if handled
     */
    handleSeek(video, seekSeconds) {
      const handler = this.getCurrentHandler();
      return handler.handleSeek(video, seekSeconds);
    }
    /**
     * Check if a video should be ignored
     * @param {HTMLMediaElement} video - Video element
     * @returns {boolean} True if video should be ignored
     */
    shouldIgnoreVideo(video) {
      const handler = this.getCurrentHandler();
      return handler.shouldIgnoreVideo(video);
    }
    /**
     * Get video container selectors for current site
     * @returns {Array<string>} CSS selectors
     */
    getVideoContainerSelectors() {
      const handler = this.getCurrentHandler();
      return handler.getVideoContainerSelectors();
    }
    /**
     * Detect special videos for current site
     * @param {Document} document - Document object
     * @returns {Array<HTMLMediaElement>} Additional videos found
     */
    detectSpecialVideos(document2) {
      const handler = this.getCurrentHandler();
      return handler.detectSpecialVideos(document2);
    }
    /**
     * Cleanup current handler
     */
    cleanup() {
      if (this.currentHandler) {
        this.currentHandler.cleanup();
        this.currentHandler = null;
      }
    }
    /**
     * Force refresh of current handler (useful for SPA navigation)
     */
    refresh() {
      this.cleanup();
      this.currentHandler = null;
    }
  };
  window.VSC.siteHandlerManager = new SiteHandlerManager();

  // src/site-handlers/scripts/netflix.js
  window.addEventListener("message", function(event) {
    if (event.origin != "https://www.netflix.com" || event.data.action != "videospeed-seek" || !event.data.seekMs) {
      return;
    }
    ;
    const videoPlayer = window.netflix.appContext.state.playerApp.getAPI().videoPlayer;
    const playerSessionId = videoPlayer.getAllPlayerSessionIds()[0];
    const currentTime = videoPlayer.getCurrentTimeBySessionId(playerSessionId);
    videoPlayer.getVideoPlayerBySessionId(playerSessionId).seek(currentTime + event.data.seekMs);
  }, false);

  // src/content/inject.js
  var VideoSpeedExtension = class {
    constructor() {
      this.config = null;
      this.actionHandler = null;
      this.eventManager = null;
      this.mutationObserver = null;
      this.mediaObserver = null;
      this.initialized = false;
    }
    /**
     * Initialize the extension
     */
    async initialize() {
      try {
        this.VideoController = window.VSC.VideoController;
        this.ActionHandler = window.VSC.ActionHandler;
        this.EventManager = window.VSC.EventManager;
        this.logger = window.VSC.logger;
        this.isBlacklisted = window.VSC.DomUtils.isBlacklisted;
        this.initializeWhenReady = window.VSC.DomUtils.initializeWhenReady;
        this.siteHandlerManager = window.VSC.siteHandlerManager;
        this.VideoMutationObserver = window.VSC.VideoMutationObserver;
        this.MediaElementObserver = window.VSC.MediaElementObserver;
        this.MESSAGE_TYPES = window.VSC.Constants.MESSAGE_TYPES;
        this.logger.info("Video Speed Controller starting...");
        this.config = window.VSC.videoSpeedConfig;
        await this.config.load();
        if (!this.config.settings.enabled) {
          this.logger.info("Extension is disabled");
          return;
        }
        if (this.isBlacklisted(this.config.settings.blacklist)) {
          this.logger.info("Site is blacklisted");
          return;
        }
        this.siteHandlerManager.initialize(document);
        this.eventManager = new this.EventManager(this.config, null);
        this.actionHandler = new this.ActionHandler(this.config, this.eventManager);
        this.eventManager.actionHandler = this.actionHandler;
        this.setupObservers();
        this.initializeWhenReady(document, (doc) => {
          this.initializeDocument(doc);
        });
        this.logger.info("Video Speed Controller initialized successfully");
        this.initialized = true;
      } catch (error) {
        console.error(`\u274C Failed to initialize Video Speed Controller: ${error.message}`);
        console.error("\u{1F4CB} Full error details:", error);
        console.error("\u{1F50D} Error stack:", error.stack);
      }
    }
    /**
    * Initialize for a specific document
    * @param {Document} document - Document to initialize
    */
    initializeDocument(document2) {
      try {
        if (window.VSC.initialized) {
          return;
        }
        window.VSC.initialized = true;
        this.applyDomainStyles(document2);
        this.eventManager.setupEventListeners(document2);
        if (document2 !== window.document) {
          this.setupDocumentCSS(document2);
        }
        this.deferExpensiveOperations(document2);
        this.logger.debug("Document initialization completed");
      } catch (error) {
        this.logger.error(`Failed to initialize document: ${error.message}`);
      }
    }
    /**
     * Defer expensive operations to avoid blocking page load
     * @param {Document} document - Document to defer operations for
     */
    deferExpensiveOperations(document2) {
      const callback = () => {
        try {
          if (this.mutationObserver) {
            this.mutationObserver.start(document2);
            this.logger.debug("Mutation observer started for document");
          }
          this.deferredMediaScan(document2);
        } catch (error) {
          this.logger.error(`Failed to complete deferred operations: ${error.message}`);
        }
      };
      if (window.requestIdleCallback) {
        requestIdleCallback(callback, { timeout: 2e3 });
      } else {
        setTimeout(callback, 100);
      }
    }
    /**
     * Perform media scanning in a non-blocking way
     * @param {Document} document - Document to scan
     */
    deferredMediaScan(document2) {
      const performChunkedScan = () => {
        try {
          const lightMedia = this.mediaObserver.scanForMediaLight(document2);
          lightMedia.forEach((media) => {
            this.onVideoFound(media, media.parentElement || media.parentNode);
          });
          this.logger.info(
            `Attached controllers to ${lightMedia.length} media elements (light scan)`
          );
          if (lightMedia.length === 0) {
            this.scheduleComprehensiveScan(document2);
          }
        } catch (error) {
          this.logger.error(`Failed to scan media elements: ${error.message}`);
        }
      };
      if (window.requestIdleCallback) {
        requestIdleCallback(performChunkedScan, { timeout: 3e3 });
      } else {
        setTimeout(performChunkedScan, 200);
      }
    }
    /**
     * Schedule a comprehensive scan if the light scan didn't find anything
     * @param {Document} document - Document to scan comprehensively
     */
    scheduleComprehensiveScan(document2) {
      setTimeout(() => {
        try {
          const comprehensiveMedia = this.mediaObserver.scanAll(document2);
          comprehensiveMedia.forEach((media) => {
            if (!media.vsc) {
              this.onVideoFound(media, media.parentElement || media.parentNode);
            }
          });
          this.logger.info(
            `Comprehensive scan found ${comprehensiveMedia.length} additional media elements`
          );
        } catch (error) {
          this.logger.error(`Failed comprehensive media scan: ${error.message}`);
        }
      }, 1e3);
    }
    /**
    * Apply domain-specific styles using CSS custom properties
    * Sets CSS custom property on :root to enable CSS-based domain targeting
    * @param {Document} document - Document to apply styles to
    */
    applyDomainStyles(document2) {
      try {
        const hostname = window.location.hostname;
        if (document2.documentElement) {
          document2.documentElement.style.setProperty("--vsc-domain", `"${hostname}"`);
        }
      } catch (error) {
        this.logger.error(`Failed to apply domain styles: ${error.message}`);
      }
    }
    /**
     * Set up observers for DOM changes and video detection
     */
    setupObservers() {
      this.mediaObserver = new this.MediaElementObserver(this.config, this.siteHandlerManager);
      this.mutationObserver = new this.VideoMutationObserver(
        this.config,
        (video, parent) => this.onVideoFound(video, parent),
        (video) => this.onVideoRemoved(video),
        this.mediaObserver
      );
    }
    /**
     * Handle newly found video element
     * @param {HTMLMediaElement} video - Video element
     * @param {HTMLElement} parent - Parent element
     */
    onVideoFound(video, parent) {
      try {
        if (this.mediaObserver && !this.mediaObserver.isValidMediaElement(video)) {
          this.logger.debug("Video element is not valid for controller attachment");
          return;
        }
        if (video.vsc) {
          this.logger.debug("Video already has controller attached");
          return;
        }
        const shouldStartHidden = this.mediaObserver ? this.mediaObserver.shouldStartHidden(video) : false;
        this.logger.debug(
          "Attaching controller to new video element",
          shouldStartHidden ? "(starting hidden)" : ""
        );
        video.vsc = new this.VideoController(
          video,
          parent,
          this.config,
          this.actionHandler,
          shouldStartHidden
        );
      } catch (error) {
        console.error("\u{1F4A5} Failed to attach controller to video:", error);
        this.logger.error(`Failed to attach controller to video: ${error.message}`);
      }
    }
    /**
     * Handle removed video element
     * @param {HTMLMediaElement} video - Video element
     */
    onVideoRemoved(video) {
      try {
        if (video.vsc) {
          this.logger.debug("Removing controller from video element");
          video.vsc.remove();
        }
      } catch (error) {
        this.logger.error(`Failed to remove video controller: ${error.message}`);
      }
    }
    /**
     * Set up CSS for iframe documents
     * @param {Document} document - Document to set up CSS for
     */
    setupDocumentCSS(document2) {
      const link = document2.createElement("link");
      link.href = typeof chrome !== "undefined" && chrome.runtime ? chrome.runtime.getURL("src/styles/inject.css") : "/src/styles/inject.css";
      link.type = "text/css";
      link.rel = "stylesheet";
      document2.head.appendChild(link);
      this.logger.debug("CSS injected into iframe document");
    }
  };
  (function() {
    const extension = new VideoSpeedExtension();
    window.addEventListener("VSC_MESSAGE", (event) => {
      const message = event.detail;
      if (typeof message === "object" && message.type && message.type.startsWith("VSC_")) {
        const videos = window.VSC.stateManager ? window.VSC.stateManager.getAllMediaElements() : [];
        switch (message.type) {
          case window.VSC.Constants.MESSAGE_TYPES.SET_SPEED:
            if (message.payload && typeof message.payload.speed === "number") {
              const targetSpeed = message.payload.speed;
              videos.forEach((video) => {
                if (video.vsc) {
                  extension.actionHandler.adjustSpeed(video, targetSpeed);
                } else {
                  video.playbackRate = targetSpeed;
                }
              });
              window.VSC.logger?.debug(`Set speed to ${targetSpeed} on ${videos.length} media elements`);
            }
            break;
          case window.VSC.Constants.MESSAGE_TYPES.ADJUST_SPEED:
            if (message.payload && typeof message.payload.delta === "number") {
              const delta = message.payload.delta;
              videos.forEach((video) => {
                if (video.vsc) {
                  extension.actionHandler.adjustSpeed(video, delta, { relative: true });
                } else {
                  const newSpeed = Math.min(Math.max(video.playbackRate + delta, 0.07), 16);
                  video.playbackRate = newSpeed;
                }
              });
              window.VSC.logger?.debug(`Adjusted speed by ${delta} on ${videos.length} media elements`);
            }
            break;
          case window.VSC.Constants.MESSAGE_TYPES.RESET_SPEED:
            videos.forEach((video) => {
              if (video.vsc) {
                extension.actionHandler.resetSpeed(video, 1);
              } else {
                video.playbackRate = 1;
              }
            });
            window.VSC.logger?.debug(`Reset speed on ${videos.length} media elements`);
            break;
          case window.VSC.Constants.MESSAGE_TYPES.TOGGLE_DISPLAY:
            if (extension.actionHandler) {
              extension.actionHandler.runAction("display", null, null);
            }
            break;
        }
      }
    });
    if (window.VSC_controller && window.VSC_controller.initialized) {
      window.VSC.logger?.info("VSC already initialized, skipping re-injection");
      return;
    }
    extension.initialize().catch((error) => {
      console.error(`Extension initialization failed: ${error.message}`);
      window.VSC.logger.error(`Extension initialization failed: ${error.message}`);
    });
    window.VSC_controller = extension;
  })();
})();
