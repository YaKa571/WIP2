//ChatGPT saved the day once again with this one
function activateVerticalResizeHandle() {
    const handle = document.querySelector('.vertical-resize-handle');
    const pieCharts = document.querySelector('.home-tab > .flex-wrapper:nth-of-type(3)');
    const barChart = document.querySelector('.home-tab > .flex-wrapper:nth-of-type(5)');
    const homeTab = document.querySelector('.home-tab');

    if (!handle || !pieCharts || !barChart || !homeTab) {
        return false;
    }

    const minFr = 5;
    const totalFr = 16; // 7fr + 9fr from CSS
    const handleHeight = handle.offsetHeight || 5;
    const rowCount = 5;
    const gridGap = parseFloat(getComputedStyle(homeTab).rowGap) || 0;
    const totalGapHeight = gridGap * (rowCount - 1);

    let isResizing = false;
    let startY, startPieHeight, startBarHeight;
    let initialPieFr, initialBarFr;

    handle.addEventListener('mousedown', function (e) {
        isResizing = true;
        document.body.style.userSelect = 'none';
        handle.classList.add('resizing');

        const usableHeight = pieCharts.parentNode.offsetHeight - handleHeight - totalGapHeight - 200;

        startY = e.clientY;
        startPieHeight = pieCharts.offsetHeight;
        startBarHeight = barChart.offsetHeight;

        initialPieFr = (startPieHeight / usableHeight) * totalFr;
        initialBarFr = (startBarHeight / usableHeight) * totalFr;

        e.preventDefault();
    });

    document.addEventListener('mousemove', function (e) {
        if (!isResizing) return;

        const usableHeight = pieCharts.parentNode.offsetHeight - handleHeight - totalGapHeight;

        const deltaY = e.clientY - startY;
        const deltaFr = (deltaY / usableHeight) * totalFr;

        let rawPieFr = initialPieFr + deltaFr;
        let rawBarFr = initialBarFr - deltaFr;

        let newPieFr, newBarFr;

        if (rawPieFr < minFr) {
            newPieFr = minFr;
            newBarFr = totalFr - minFr;
        } else if (rawBarFr < minFr) {
            newBarFr = minFr;
            newPieFr = totalFr - minFr;
        } else {
            newPieFr = rawPieFr;
            newBarFr = rawBarFr;
        }

        homeTab.style.gridTemplateRows = `auto auto ${newPieFr}fr 5px ${newBarFr}fr`;
    });

    document.addEventListener('mouseup', function () {
        if (isResizing) handle.classList.remove('resizing');
        isResizing = false;
        document.body.style.userSelect = '';
    });

    return true;
}

// Search several times (max 30)
let verticalTries = 0;
const verticalMaxTries = 30;
const verticalInterval = setInterval(function () {
    if (activateVerticalResizeHandle()) {
        clearInterval(verticalInterval);
    } else {
        verticalTries += 1;
        if (verticalTries >= verticalMaxTries) clearInterval(verticalInterval);
    }
}, 200);
