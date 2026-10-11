var fs = require('fs');
var path = require('path');
var express = require('express');
var helmet = require('helmet');

// Configuration (environment variables)
var PORT = process.env.PORT || 3000;
var LOGIN_URL = process.env.CELL_CLOUD_LOGIN_URL || '/login';
var GOOGLE_ANALYTICS_ID = process.env.GOOGLE_ANALYTICS_ID || '';

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
  });
}

// index.html is rendered once at startup
var analytics = '';
if (GOOGLE_ANALYTICS_ID) {
  var id = escapeHtml(GOOGLE_ANALYTICS_ID);
  analytics = '<script async src="https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GOOGLE_ANALYTICS_ID) + '"></script>\n' +
    '  <script src="static/js/ga.js" data-ga-id="' + id + '"></script>';
}
var index = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8')
  .replace(/\{\{LOGIN_URL\}\}/g, escapeHtml(LOGIN_URL))
  .replace('<!--GOOGLE_ANALYTICS-->', analytics);

var analyticsHosts = GOOGLE_ANALYTICS_ID ? ['https://*.googletagmanager.com', 'https://*.google-analytics.com', 'https://*.analytics.google.com'] : [];

var app = express();

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      // materialize and jQuery are loaded from CDNs
      scriptSrc: ["'self'", 'https://cdnjs.cloudflare.com', 'https://code.jquery.com'].concat(analyticsHosts),
      connectSrc: ["'self'"].concat(analyticsHosts),
      imgSrc: ["'self'", 'data:'].concat(analyticsHosts),
    },
  },
}));

app.get('/', function (req, res) {
  res.type('html').send(index);
});

app.use('/static', express.static(path.join(__dirname, 'public')));

module.exports = app;

if (require.main === module) {
  app.listen(PORT, function () {
    console.log('hidos-express app listening on port ' + PORT + '!');
  });
}
