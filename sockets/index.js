var express = require('express');
var app = express();
var server = require('http').Server(app);
var io = require('socket.io')(server);

server.listen(9000);

var bodyParser = require('body-parser')
app.use( bodyParser.json() );       // to support JSON-encoded bodies

app.get('/', function (req, res) {
  res.sendfile(__dirname + '/index.html');
});

app.post('/emit', function(req, res) {
    console.log(req.body);
    io.sockets.in(req.body.room).emit('hard-reset', { "message": req.body.message });
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({ "result": "ok" }));
});


io.on('connection', function (socket) {

	socket.on('disconnect', function(data) {
		console.log("DISCONNECTED!!!");
	});

  
  socket.on('join', function (data) {
    
  	// Get origin
  	// Get room name
  	var room_name = data;

  	// Verify room can be accessed from origin.

  	var referer = socket.request.headers.referer;

  	console.log(referer);
  	console.log("JOINING ROOM " + data);
  	socket.join(room_name);

  });

});