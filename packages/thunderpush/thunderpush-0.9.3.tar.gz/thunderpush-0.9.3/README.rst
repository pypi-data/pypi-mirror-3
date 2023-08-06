-----------
Thunderpush
-----------

Thunderpush is a Tornado and SockJS based push service. It provides
a Beaconpush (beaconpush.com) inspired HTTP API and client.

This project is in early stage of development and should not be
used in production environments.

Install
=======

::
	
	pip install thunderpush

Usage
=====

::
	
	Usage: runner.py [options] apikey apisecret

	Options:
		-h, --help            show this help message and exit
		-p PORT, --port=PORT  binds server to custom port
		-H HOST, --host=HOST  binds server to custom address
		-v, --verbose         verbose mode
		-d, --debug           debug mode (useful for development)

Using the HTTP API
==================

Example of interacting with Thunderpush API using cURL::

	curl \
		-X POST \
		-H "Content-Type: application/json" \
		-H "X-Thunder-Secret-Key: secretkey" \
		--data-ascii "\"Hello World!\"" \
		http://thunder.example.com/1.0.0/[API key]/channel/[channel]/

All requests to the HTTP API must provide *X-Thunder-Secret-Key* header that
should contain the private API key. 

Sending a message to a channel
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

	POST /1.0.0/[API key]/channels/[channel]/

Message should be sent as the body of the request. Only valid JSON body
will be accepted.

Getting number of users online
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

	GET /1.0.0/[API key]/users/

Checking presence of a user
^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

	GET /1.0.0/[API key]/users/[user id]/

Returns 200 or 404 code depending on if the user is online or not.

Sending a message to a user
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

	POST /1.0.0/[API key]/users/[user id]/

Message should be sent as the body of the request. Only valid JSON body
will be accepted.

Retrieving list of users in a channel
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

	GET /1.0.0/[API key]/channels/[channel]/

JavaScript client
=================

In order to use provided by Thunderpush client, you need to include following
lines on your webpage.

::

	<script src="http://cdn.sockjs.org/sockjs-0.3.min.js"></script>
	<script src="thunderpush.js"></script>

The only thing you have to do now is to make a connection to your Thunderpush
server in following way::

	<script type="text/javascript">
	Thunder.connect("thunder.example.com", "apikey", ["testchannel"], {log: true});
	Thunder.listen(function(message) { alert(message); });
	</script>

This code is all you need to do to start receive messages pushed to the client
from your Thunderpush server. As you can see, we instructed Thunder client
to display logs, which can be helpful for debugging your application.

For more examples of how to use Thunderpush, look into `examples <https://github.com/kjagiello/thunderpush/tree/master/examples>`_.

JavaScript client API
=====================

Connecting to the server
^^^^^^^^^^^^^^^^^^^^^^^^

::
	
	Thunder.connect(server, apiKey, channels, options)

Connects to the Thunderpush server and starts listening for incomming
messages. 

server
  Adress of your Thunderpush server.

apiKey
  Public api key.

channels
  Array of channels you want to subscribe to.

options
  Object with optional settings you may pass to Thunder:

  log
    Set it to true if you want to activate verbose mode. This will turn on
    SockJS logs as well.

  user
    Set it to override the client generated user id.

Listening for messages
^^^^^^^^^^^^^^^^^^^^^^

::
	
	Thunder.listen(handler)

Registers callback function that will receive incomming messages. You can
register as many handlers you want. Handler function should accept
one argument which is the message itself.
