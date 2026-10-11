// Google Analytics (#13); loaded only when GOOGLE_ANALYTICS_ID is set
window.dataLayer = window.dataLayer || [];
function gtag() { window.dataLayer.push(arguments); }
gtag('js', new Date());
gtag('config', document.currentScript.getAttribute('data-ga-id'));
