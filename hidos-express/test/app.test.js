var test = require('node:test');
var assert = require('node:assert');

function start(env) {
  // load a fresh copy of the app with the given environment
  Object.assign(process.env, env || {});
  delete require.cache[require.resolve('../app')];
  var app = require('../app');
  return new Promise(function (resolve) {
    var server = app.listen(0, function () {
      resolve({ server: server, url: 'http://127.0.0.1:' + server.address().port });
    });
  });
}

test('landing page', async function () {
  var s = await start();
  try {
    var res = await fetch(s.url + '/');
    assert.strictEqual(res.status, 200);
    var html = await res.text();
    assert.match(html, /<title>HiDOS Cell Cloud<\/title>/);
    assert.match(html, /Cell C2/);
    assert.doesNotMatch(html, /Cell S</, 'Cell S was removed from the main menu (#57)');
    assert.match(html, /id="mobile-nav"/, 'responsive menu (#48)');
    assert.match(html, /href="\/login">Login/);
    assert.doesNotMatch(html, /googletagmanager/, 'analytics is off by default');
    assert.doesNotMatch(html, /\{\{/);
    // security headers from helmet
    assert.match(res.headers.get('content-security-policy'), /script-src 'self' https:\/\/cdnjs.cloudflare.com https:\/\/code.jquery.com/);
    assert.strictEqual(res.headers.get('x-content-type-options'), 'nosniff');
  } finally {
    s.server.close();
  }
});

test('static files', async function () {
  var s = await start();
  try {
    var img = await fetch(s.url + '/static/images/parallax1.jpg');
    assert.strictEqual(img.status, 200);
    assert.strictEqual(img.headers.get('content-type'), 'image/jpeg');
    var js = await fetch(s.url + '/static/js/landing.js');
    assert.strictEqual(js.status, 200);
    assert.strictEqual((await fetch(s.url + '/static/nope.png')).status, 404);
  } finally {
    s.server.close();
  }
});

test('configuration from the environment', async function () {
  var s = await start({ CELL_CLOUD_LOGIN_URL: 'https://cell.example.org/login?a=1&b=2', GOOGLE_ANALYTICS_ID: 'G-TEST123' });
  try {
    var res = await fetch(s.url + '/');
    var html = await res.text();
    assert.match(html, /href="https:\/\/cell.example.org\/login\?a=1&amp;b=2">Login/);
    assert.match(html, /googletagmanager.com\/gtag\/js\?id=G-TEST123/);
    assert.match(html, /data-ga-id="G-TEST123"/);
    assert.match(res.headers.get('content-security-policy'), /googletagmanager/);
  } finally {
    s.server.close();
    delete process.env.CELL_CLOUD_LOGIN_URL;
    delete process.env.GOOGLE_ANALYTICS_ID;
  }
});
