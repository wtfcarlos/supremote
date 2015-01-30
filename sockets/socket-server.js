var redis = require("redis");
redisClient = redis.createClient();

redisClient.select(1, function() {

	redisClient.on("error", function (err) {
        console.log("Error " + err);
    });

	var express = require('express');
	var app = express();
	var server = require('http').Server(app);
	var io = require('socket.io')(server);

	server.listen(9000);

	var bodyParser = require('body-parser');
	app.use(bodyParser.json());

	// Example page for testing.
	app.get('/', function (req, res) {
	  res.sendfile(__dirname + '/index.html');
	});


	// Endpoint for emitting from the django server.
	app.post('/emit', function(req, res) {
	    // Get emission password from system variable
	    var emission_key = process.env.SUPREMOTE_SOCKET_KEY
	    var received_key = req.body.password;

	    res.setHeader('Content-Type', 'application/json');

	    if (received_key == emission_key) {

	    	var message = req.body.message;
	    	var event_type = req.body.event_type;
	    	var room = req.body.room;

	    	if (event_type == "update") {
	    		io.sockets.in(room)
	    		.emit('update', message);
	    	} else if (event_type == "action") {
	    		var action_name = req.body.action_name;
	    		io.sockets.in(room)
	    		.emit('#' + action_name, message);
	    	} else {
	    		res.end(
	    			JSON.stringify(
	    				{ "result": "error", "description": "Event type not supported." }
	    				)
	    			);
	    	}
	    	res.end(JSON.stringify({ "result": "ok", "socket_key": emission_key }));
	    } else {
			res.end(JSON.stringify({ "result": "error", "description": "Emission password not provided." }));
	    }
	    
	});


	io.on('connection', function (socket) {

		socket.on('disconnect', function(data) {
			console.log("DISCONNECTED!!!");
		});

		socket.on('reconnect', function(data) {
			console.log("RECONECCTED");
		});

	  
	 	socket.on('join', function (data) {
			// Get origin
			// Get room name
			var room_name = data;

			var allowAllOriginsKey = room_name + '.allow_all_origins';
			var domainKey = room_name + '.domains';
			var host = parseUri(socket.request.headers.referer).host;

			socket.join(room_name);

			redisClient.get(allowAllOriginsKey, function(error, reply) {
				if (reply === null && typeof reply === "object") {
					socket.emit('not-found', {'error': 'No such remote key: ' + room_name});
					socket.leave();
				} else {

					if (parseInt(reply) == 0) {
						// Check for permitted origin.
						redisClient.smembers(domainKey, function(error, domainList) {
							console.log(domainList);
							if(domainList !== null) {
								if(domainList.indexOf(host) <= -1) {
									socket.emit('unauthorized', 'This origin is not allowed: ' + host + '. Closing connection now.');
									socket.leave();
								}
							}

						});

					} else {
						socket.emit('info', 'This remote is setup to accept connections from any origin. This is alright for development purposes, but you should not be seeing this in a production environment.');
					}

				}
			});
		});
	});


	// parseUri 1.2.2
	// (c) Steven Levithan <stevenlevithan.com>
	// MIT License

	function parseUri (str) {
		var	o   = parseUri.options,
			m   = o.parser[o.strictMode ? "strict" : "loose"].exec(str),
			uri = {},
			i   = 14;

		while (i--) uri[o.key[i]] = m[i] || "";

		uri[o.q.name] = {};
		uri[o.key[12]].replace(o.q.parser, function ($0, $1, $2) {
			if ($1) uri[o.q.name][$1] = $2;
		});

		return uri;
	};

	parseUri.options = {
			strictMode: false,
			key: ["source","protocol","authority","userInfo","user","password","host","port","relative","path","directory","file","query","anchor"],
			q:   {
				name:   "queryKey",
				parser: /(?:^|&)([^&=]*)=?([^&]*)/g
			},
			parser: {
				strict: /^(?:([^:\/?#]+):)?(?:\/\/((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?))?((((?:[^?#\/]*\/)*)([^?#]*))(?:\?([^#]*))?(?:#(.*))?)/,
				loose:  /^(?:(?![^:@]+:[^:@\/]*@)([^:\/?#.]+):)?(?:\/\/)?((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?)(((\/(?:[^?#](?![^?#\/]*\.[^?#\/.]+(?:[?#]|$)))*\/?)?([^?#\/]*))(?:\?([^#]*))?(?:#(.*))?)/
			}
		};

});