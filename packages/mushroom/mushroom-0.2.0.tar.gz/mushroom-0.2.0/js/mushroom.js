(function(undefined) {

var mushroom = window.mushroom;
if (mushroom === undefined) {
	mushroom = window.mushroom = {};
}

function createXHR() {
	try {
		return new window.XMLHttpRequest();
	} catch(e) {};
	try {
		return new window.ActiveXObject('Microsoft.XMLHTTP');
	} catch(e) {};
}

WEB_SOCKET_SUPPORT = 'WebSocket' in window;

function post(url, data, callback) {
	var xhr = createXHR();
	xhr.open('POST', url, true);
	xhr.onreadystatechange = function() {
		if (xhr.readyState === 4) {
			callback(xhr);
		}
	};
	/* In order to make so called 'simple requests' that work via CORS
	 * the Content-Type is very limited. We simply use text/plain which
	 * is better than using form-data content types.
	 * https://developer.mozilla.org/en/http_access_control#Simple_requests
	 */
	if (data != null) {
		xhr.setRequestHeader('Content-Type', 'text/plain')
		xhr.send(JSON.stringify(data));
	} else {
		xhr.send(null);
	}
}

mushroom.Client = function(options) {
	this.url = options.url;
	this.transports = options.transports ||
			(WEB_SOCKET_SUPPORT ? ['ws', 'poll'] : ['poll']);
	this.methods = options.methods || {};
	this.messageHandlers = {
		'0': this.handleHeartbeat,
		'1': this.handleNotification,
		'2': this.handleRequest,
		'3': this.handleResponse,
		'4': this.handleError,
		'-1': this.handleDisconnect
	};
	this.lastMessageId = -1;
	this.requests = {};

	// FIXME this requires jQuery
	/*
	$(window).bind('beforeunload', function() {
		// FIXME It seams that this call should be done asynchroneously
		//       which might not work for cross domain requests at all.
		//       We need to find a good solution here or use a shorter
		//       timeout value in order to detect disconnects earlier at
		//       the server side.
		this.disconnect();
	}.bind(this));
	*/
}

mushroom.Client.prototype.nextMessageId = function() {
	this.lastMessageId += 1;
	return this.lastMessageId;
};

mushroom.Client.prototype.connect = function(auth) {
	var request = {
		transports: this.transports,
		auth: auth || null
	}
	post(this.url, request, function(xhr) {
		// FIXME check status code
		jsonResponse = JSON.parse(xhr.responseText);
		transportClass = mushroom.transports[jsonResponse.transport];
		if (transportClass === undefined) {
			throw Error('Unsupported transport ' + this.transport);
		}
		this.transport = new transportClass(this, jsonResponse);
		this.transport.start();
	}.bind(this));
};

mushroom.Client.prototype.method = function(name, callback) {
	this.methods[name] = callback;
	return this;
};

mushroom.Client.prototype.call = function(method, params, responseCallback, errorCallback) {
	var message;
	if (responseCallback) {
		message = new mushroom.Request({
			messageId: this.nextMessageId(),
			method: method,
			params: params,
			responseCallback: function(message) {
				if (message.success) {
					responseCallback(message.data);
				} else {
					if (errorCallback) {
						errorCallback(message.data);
					} else {
						console.log('Unhandled RPC error', message);
						// FIXME call global error handler of client
					}
				}
			}
		});
		this.requests[message.messageId] = message;
	} else {
		message = new mushroom.Notification({
			messageId: this.nextMessageId(),
			method: method,
			params: pararms
		});
	}
	this.sendMessage(message);
};

mushroom.Client.prototype.sendMessage = function(message) {
	this.transport.sendMessage(message);
};

mushroom.Client.prototype.handleNotification = function(data) {
	var request = new mushroom.Request({
		client: this,
		messageId: data[1],
		method: data[2],
		params: data[3]
	});
	var method = this.methods[request.method];
	if (method !== undefined) {
		method.call(this, request);
	} else {
		// FIXME Add logging that does not cause errors on browsers without
		//       developer tools.
		console.log('No method for notification: ' + request.method);
	}
}

mushroom.Client.prototype.handleResponse = function(data) {
	var response = new mushroom.Response({
		client: this,
		messageId: data[1],
		requestMessageId: data[2],
		data: data[3]
	});
	var request = this.requests[response.requestMessageId];
	response.request = request
	request.responseCallback(response);
}

mushroom.PollTransport = function(client, options) {
	this.client = client;
	this.url = options.url;
	this.lastMessageId = null;
	this.running = false;
	this.stopping = false;
}

mushroom.PollTransport.prototype.start = function() {
	if (this.running) {
		throw Error('Already started');
	}
	this.poll();
};

mushroom.PollTransport.prototype.poll = function() {
	this.running = true;
	var request = [
		[0, this.lastMessageId]
	]
	post(this.url, request, function(xhr) {
		if (xhr.status !== 200) {
			throw Error('Polling failed');
		}
		data = JSON.parse(xhr.responseText);
		data.forEach(function(messageData) {
			var code = messageData[0];
			if (code > 0) {
				this.lastMessageId = messageData[1];
			}
			var handler = this.client.messageHandlers[code];
			handler.call(this.client, messageData);
		}.bind(this));
		if (this.stopping) {
			this.stopping = false;
			this.running = false;
		} else {
			this.poll();
		}
	}.bind(this));
};

mushroom.PollTransport.prototype.sendMessage = function(message) {
	var request = [
		message.toList()
	];
	post(this.url, request, function(xhr) {
		// FIXME remove message from out-queue
	});
}

mushroom.WebSocketTransport = function(client, options) {
	this.client = client;
	this.url = options.url;
};

mushroom.WebSocketTransport.prototype.start = function() {
	this.ws = new WebSocket(this.url);
	this.ws.onopen = function(event) {
		console.log('open', event);
	}.bind(this);
	this.ws.onclose = function(event) {
		console.log('close', event);
	}.bind(this);
	this.ws.onmessage = function(event) {
		frame = event.data;
		messageData = JSON.parse(frame);
		var code = messageData[0];
		if (code > 0) {
			this.lastMessageId = messageData[1];
		}
		var handler = this.client.messageHandlers[code];
		handler.call(this.client, messageData);
	}.bind(this);
};

mushroom.WebSocketTransport.prototype.sendMessage = function(message) {
	// FIXME queue messages and wait for acknowledgement
	var data = message.toList();
	var frame = JSON.stringify(data);
	this.ws.send(frame);
};

mushroom.transports = {
	'poll': mushroom.PollTransport,
	'ws': mushroom.WebSocketTransport
}

mushroom.Notification = function(options) {
	this.client = options.client;
	this.messageId = options.messageId;
	this.method = options.method;
	this.params = options.params;
};

mushroom.Notification.prototype.isRequest = false;

mushroom.Request = function(options) {
	this.client = options.client;
	this.messageId = options.messageId;
	this.method = options.method;
	this.params = options.params || null;
	this.responseCallback = options.responseCallback || null;
};

mushroom.Request.prototype.isRequest = true;

mushroom.Request.fromList = function() {
}

mushroom.Request.MESSAGE_CODE = 2;

mushroom.Request.prototype.toList = function() {
	return [mushroom.Request.MESSAGE_CODE, this.messageId,
			this.method, this.params];
}

mushroom.Request.prototype.sendResponse = function(data) {
	var response = new mushroom.Response({
		client: this.client,
		messageId: this.client.nextMessageId(),
		requestMessageId: this.messageId,
		data: data
	});
	this.client.sendMessage(response);
};

mushroom.Request.prototype.sendError = function(data) {
	var error = new mushroom.Error({
		client: this.client,
		messageId: this.client.nextMessageId(),
		requestMessageId: this.messageId,
		data: data
	});
	this.client.sendMessage(error);
}

mushroom.Response = function(options) {
	this.client = options.client;
	this.messageId = options.messageId;
	this.requestMessageId = options.messageId;
	this.request = options.request || null;
	this.data = options.data || null;
};

mushroom.Response.MESSAGE_CODE = 3;

mushroom.Response.prototype.success = true;

mushroom.Error = function(options) {
	this.client = options.client;
	this.messageId = options.messageId;
	this.requestMessageId = options.messageId;
	this.data = options.data || null;
};

mushroom.Error.MESSAGE_CODE = 4;

mushroom.Error.prototype.success = false;

mushroom.Error.prototype.toList = function() {
	return [mushroom.Error.MESSAGE_CODE, this.messageId,
			this.requestMessageId, this.data];
};

})();
