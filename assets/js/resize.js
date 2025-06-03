// ChatGPT prompt: Write a modern, robust JavaScript script that places a draggable handle
// (e.g., a div with the class .resize-handle) between two horizontally aligned columns
// (.left-column and .right-column) and allows users to dynamically resize the width o
// both columns by dragging the handle.
function activateResizeHandle() {
    const handle = document.querySelector('.resize-handle');
    const left = document.querySelector('.left-column');
    const right = document.querySelector('.right-column');
    console.log("Handle:", handle, "Left:", left, "Right:", right);
    if (!handle || !left || !right) {
        return false;
    }

    let isResizing = false;

    handle.addEventListener('mousedown', function (e) {
        isResizing = true;
        document.body.style.userSelect = 'none';
        console.log('Drag Start');
    });

    document.addEventListener('mousemove', function (e) {
        if (!isResizing) return;
        const parentRect = left.parentNode.getBoundingClientRect();
        const handleWidth = handle.offsetWidth || 5; // px
        const minRight = 760; // px
        const minLeft = 250;  // px

        let newWidth = e.clientX - parentRect.left;
        let maxLeft = parentRect.width - minRight - handleWidth;
        newWidth = Math.max(minLeft, Math.min(newWidth, maxLeft));

        left.style.width = newWidth + 'px';
        console.log('Dragging...', newWidth);
    });

    document.addEventListener('mouseup', function () {
        if (isResizing) console.log('Drag End');
        isResizing = false;
        document.body.style.userSelect = '';
    });

    console.log("Resize handle aktiviert!");
    return true;
}

// Search several times (max 30)
let tries = 0;
const maxTries = 30;
const interval = setInterval(function () {
    if (activateResizeHandle()) {
        clearInterval(interval);
    } else {
        tries += 1;
        if (tries >= maxTries) clearInterval(interval);
    }
}, 200);
