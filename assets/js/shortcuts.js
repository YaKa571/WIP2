// Wait until the initial HTML document has been completely loaded and parsed
// ChatGPT Prompt: Can you create keyboard shortcuts for the 2 buttons ... with JavaScript?
document.addEventListener("DOMContentLoaded", function () {
    // Timestamp of the last shortcut activation
    let lastTriggerTime = 0;
    // Minimum delay between activations (in milliseconds)
    const cooldown = 1000;

    // Listen for any key press on the whole document
    document.addEventListener("keydown", function (e) {
        const now = Date.now();

        // 1) Enforce cooldown: ignore if pressed too soon after the last activation
        // 2) Ignore if any modifier key is held (Ctrl, Meta/Cmd, Alt)
        // 3) Ignore if the focus is inside an <input> or <textarea>
        if (
            now - lastTriggerTime < cooldown ||
            e.ctrlKey ||
            e.metaKey ||
            e.altKey ||
            e.target.matches("input, textarea")
        ) {
            return;
        }

        let btn = null;

        // Map specific keys to button IDs:
        // - "s" toggles the settings menu button
        // - "t" toggles the dark mode button
        if (e.key === "s") {
            btn = document.getElementById("button-settings-menu");
        } else if (e.key === "t") {
            btn = document.getElementById("button-dark-mode-toggle");
        }

        // If the target button exists in the DOM, trigger its click handler
        if (btn) {
            btn.click();
            // Reset the cooldown timer
            lastTriggerTime = now;
        }
    });
});
