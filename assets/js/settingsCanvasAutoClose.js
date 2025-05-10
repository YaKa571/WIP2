// ChatGPT prompt: Can you create an auto-close offcanvas panels JavaScript when the cursor leaves them?
// + Bug fix: prevent closing when changing their placement (and mouse leaves the offcanvas)
(function () {
    // Duration (ms) to ignore mouseleave after a placement change
    const IGNORE_DURATION = 300;
    // CSS selector for any offcanvas panel
    const OFFCANVAS_SELECTOR = '.offcanvas';
    // CSS selector for the internal close button
    const CLOSE_BUTTON_SELECTOR = '.btn-close';

    /**
     * Creates a MutationObserver that watches for class attribute changes
     * on the given offcanvas element and updates the lastPlacementChange timestamp.
     *
     * @param {HTMLElement} offcanvasElement - The offcanvas DOM node to observe
     * @param {{ timestamp: number }} lastPlacementChangeRef - Object holding the last change time
     * @returns {MutationObserver} The configured observer instance
     */
    function setupMutationObserver(offcanvasElement, lastPlacementChangeRef) {
        return new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                // If the 'class' attribute changed, record the current time
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    lastPlacementChangeRef.timestamp = Date.now();
                }
            });
        });
    }

    /**
     * Handles the mouseleave event on an offcanvas element.
     * Closes the offcanvas by clicking the close button, unless we are
     * within the IGNORE_DURATION after a placement change.
     *
     * @param {HTMLElement} closeButton - The close button to click
     * @param {{ timestamp: number }} lastPlacementChange - Object holding the last change time
     */
    function handleMouseLeave(closeButton, lastPlacementChange) {
        // Skip closing if placement was just changed recently
        if (Date.now() - lastPlacementChange.timestamp < IGNORE_DURATION) {
            return;
        }
        // Trigger the native close action
        closeButton.click();
    }

    /**
     * Attaches the auto-close behavior to a single offcanvas element.
     * Ensures we only attach once per element.
     *
     * @param {HTMLElement} offcanvasElement - The offcanvas node to enhance
     */
    function attachAutoCloseHandler(offcanvasElement) {
        // Avoid double-attaching
        if (offcanvasElement._autoClosed) return;
        offcanvasElement._autoClosed = true;

        // Reference object to hold the timestamp of the last placement change
        const lastPlacementChange = {timestamp: 0};
        // Find the internal close button
        const closeButton = offcanvasElement.querySelector(CLOSE_BUTTON_SELECTOR);
        if (!closeButton) return;

        // Observe class mutations to detect placement changes
        const observer = setupMutationObserver(offcanvasElement, lastPlacementChange);
        observer.observe(offcanvasElement, {attributes: true});

        // Attach the mouseleave handler to close when the cursor exits
        offcanvasElement.addEventListener('mouseleave', () =>
            handleMouseLeave(closeButton, lastPlacementChange)
        );
    }

    /**
     * Scans the document for any offcanvas elements and attaches
     * the auto-close handler to each.
     */
    function scanForOffcanvasElements() {
        document.querySelectorAll(OFFCANVAS_SELECTOR).forEach(attachAutoCloseHandler);
    }

    // Run an initial scan as soon as the DOM is fully loaded
    document.addEventListener('DOMContentLoaded', scanForOffcanvasElements);

    // Also watch the entire document for newly inserted offcanvas nodes
    new MutationObserver(scanForOffcanvasElements).observe(document.body, {
        childList: true,
        subtree: true
    });
})();
