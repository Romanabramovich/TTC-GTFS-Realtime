function refreshMap() {
    const iframe = document.getElementById('map-frame');
    if (iframe) {
        setTimeout(() => {
            iframe.src = iframe.src;       // Refresh iframe
        }, 500);
    }
}

setInterval(refreshMap, 5000);
