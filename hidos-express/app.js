var express = require('express');
var app = express();
var path = require('path');
var helmet = require('helmet');

app.use(helmet());

app.get('/', function (req, res) {
  res.sendFile(path.join(__dirname + '/index.html'));
});

app.use('/static', express.static(__dirname + '/public'));

app.listen(3000, function () {
  console.log('hidos-express app listening on port 3000!');
});