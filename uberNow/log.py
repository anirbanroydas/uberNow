"""
The pubsub module provides interface for the rabbitmq client.

It provides classes to create pika clients to connect to rabbitmq broker server, interact with
and publish/subscribe to rabbitmq via creating channels, methods to publish, subscribe/consume, 
stop consuming, start publishing, start connection, stop connection, create channel, close channel, 
acknowledge delivery by publisher, acknowledge receiving of messages by consumers, send basic ack, 
basic cancel requests and also add callbacks for various other events.
"""



import pika.adapters
import pika
import msgpack
import logging
import uuid

import utils

LOG_EXCHANGE = 'ubernow_log_exchange'

EXCHANGE = LOG_EXCHANGE
EXCHANGE_TYPE = 'topic'
PORT = 5672

LOGGER = logging.getLogger(__name__)




class RabbitLogClient(object):
    """
    This is a RabbitMQ Client using the TornadoConnection Adapter that will
    handle unexpected interactions with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.

    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.

    It alos uses delivery confirmations and illustrates one way to keep track of
    messages that have been sent and if they've been confirmed by RabbitMQ.

    """

    def __init__(self, credentials=None, params=None, exchange=EXCHANGE,
                 exchange_type=EXCHANGE_TYPE, exchange_durability=True, logid=None):
        """Create a new instance of the consumer class, passing in the AMQP
        URL used to connect to RabbitMQ.

        :param credentials: credentials to connect to rabbitmq broker server
        :type credentials: pika.credentials.PlainCredentials
        :param params: connection paramaters used to connect with rabbitmq broker server
        :type params: pika.connection.ConnectionParameters

        """


        self._connection = None
        self._connected = False
        self._connecting = False
        self._channel = None
        self._closing = False
        self._closed = False
        self._consumer_tag = None
        self._deliveries = []
        self._acked = 0
        self._nacked = 0
        self._message_number = 0
        self._credentials = credentials if credentials else pika.PlainCredentials('guest', 'guest')
        self._parameters = params if params else pika.ConnectionParameters(host='localhost',
                                                                           port=PORT,
                                                                           virtual_host='/',
                                                                           credentials=self._credentials)

        self._exchange = exchange
        self._exchange_type = exchange_type
        self._exchange_durability = exchange_durability
        self._status = 0
        self._id = logid if logid else str(uuid.uuid4())


    def connect(self):
        """This method connects to RabbitMQ via the Torando Connectoin Adapter, returning the 
        connection handle.

        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :return: Returns a pika connection object which is a tornado connection object to rabbitmq server
        :rtype: pika.adapters.TornadoConnection

        """


        if self._connecting:
            LOGGER.warning('[RabbitLogClient] Already connecting to RabbitMQ')
            return

        LOGGER.info('[RabbitLogClient] Connecting to RabbitMQ on localhost:5672, Object: %s ' % self)
        self._connecting = True



        return pika.adapters.TornadoConnection(parameters=self._parameters,
                                               on_open_callback=self.on_connection_opened,
                                               stop_ioloop_on_close=False)



    def on_connection_opened(self, connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :param connection: connection object created
        :type connection: pika.adapters.TornadoConnection

        """

        LOGGER.info('[RabbitLogClient] Rabbitmq connection opened : %s ' % connection)

        self._status = 1
        self._connected = True
        self._connection = connection

        self.add_on_connection_close_callback()
        self.open_channel()



    def add_on_connection_close_callback(self):
        """This method adds an on close callback that will be invoked by pika
        when RabbitMQ closes the connection to the publisher unexpectedly.

        """

        self._connection.add_on_close_callback(callback_method=self.on_connection_closed)




    def on_connection_closed(self, connection, reply_code, reply_text):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param  connection: The closed connection obj
        :type connection: pika.connection.Connection
        :param reply_code: The server provided reply_code if given
        :type reply_code: int 
        :param reply_text: The server provided reply_text if given
        :type reply_text: str 

        """

        LOGGER.warning(
            '[RabbitLogClient] Rabbitmq connection closed unexpectedly : %s ' % connection)

        self._channel = None
        self._connecting = False
        self._connected = False
        self._status = 0
        if self._closing:
            LOGGER.warning('[RabbitLogClient] connection already closing')
            return

        else:
            LOGGER.info("Connection closed, reopening in 5 seconds: reply_code : [%d] : reply_text : %s " % (
                reply_code, reply_text))

            self._connection.add_timeout(5, self.reconnect)



    def reconnect(self):
        """Will be invoked by the IOLoop timer if the connection is
        closed. See the on_connection_closed method.

        """

        LOGGER.info('[RabbitLogClient] Reconnecting to rabbitmq')

        if not self._closing:
            # Create a new connection
            self._connection = self.connect()



    def close_connection(self):
        """This method closes the connection to RabbitMQ."""

        if self._closing:
            LOGGER.warning('[RabbitLogClient] connection is already closing...')
            return

        self._closing = True

        self._connection.close()

        self._connecting = False
        self._connected = False

        if self._channel:
            self._channel = None
        if self._connection:
            self._connection = None
        if self._consumer_tag:
            self._consumer_tag = None


        self._parameters = None
        self._credentials = None
        self._status = 0
        self._closed = True
        self._id = None

        LOGGER.info('[RabbitLogClient] rabbitmq connection cosed')


    def open_channel(self):
        """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.

        """

        LOGGER.info('[RabbitLogClient] Creating a new channel for connection : %s ' %
                    self._connection)

        self._channel = self._connection.channel(on_open_callback=self.on_channel_open)



    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param channel: The channel object
        :type channel: pika.channel.Channel 

        """

        LOGGER.info('[RabbitLogClient] Channel opened : %s ' % channel)

        self._status = 2

        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange()



    def close_channel(self):
        """Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.

        """

        LOGGER.info('[RabbitLogClient] Closing the channel... ')

        self._status = 1

        self._channel.close()

        if self._channel:
            LOGGER.info('[RabbitLogClient] Channel closed : %s ' % self._channel)
            self._channel = None

        else:
            LOGGER.info('[RabbitLogClient] Channel closed')




    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.

        """

        self._channel.add_on_close_callback(self.on_channel_closed)



    def on_channel_closed(self, channel, reply_code, reply_text):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param channel: The closed channel
        :type channel: pika.channel.Channel
        :param reply_code: The numeric reason the channel was closed
        :type reply_code: int 
        :param reply_text: The text reason the channel was closed
        :type reply_text: str 

        """

        LOGGER.info("Channel %i was closed: reply_code : [%d] reply_text : %s " % (
            channel, reply_code, reply_text))

        self._status = 1

        self.close_connection()



    def setup_exchange(self):
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.

        """


        LOGGER.info('[RabbitLogClient] Declaring exchange : %s ' % self._exchange)
        self._channel.exchange_declare(exchange=self._exchange,
                                       exchange_type=self._exchange_type,
                                       durable=self._exchange_durability,
                                       auto_delete=False,
                                       nowait=False,
                                       callback=self.on_exchange_declareok)




    def on_exchange_declareok(self, frame):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.

        :param frame: Exchange.DeclareOk response frame
        :type frame: pika.Frame.Method

        """

        LOGGER.info('[RabbitLogClient] Exchange declared')

        self._status = 3


        self.setup_publishing()




    def setup_publishing(self):
        """
        In this method we will setup the channel for publishing by making it available
        for delivery confirmations and publisher confirmations.

        """

        self.enable_delivery_confirmations()



    def enable_delivery_confirmations(self):
        """Send the Confirm.Select RPC method to RabbitMQ to enable delivery
        confirmations on the channel. The only way to turn this off is to close
        the channel and create a new one.

        When the message is confirmed from RabbitMQ, the
        on_delivery_confirmation method will be invoked passing in a Basic.Ack
        or Basic.Nack method from RabbitMQ that will indicate which messages it
        is confirming or rejecting.

        """


        LOGGER.info(
            '[RabbitLogClient] Enabling delivery confirmation for publisher - Issuing Confirm.Select RPC command')

        self._channel.confirm_delivery(callback=self.on_delivery_confirmation)

        self._status = 6



    def on_delivery_confirmation(self, method_frame):
        """Invoked by pika when RabbitMQ responds to a Basic.Publish RPC
        command, passing in either a Basic.Ack or Basic.Nack frame with
        the delivery tag of the message that was published. The delivery tag
        is an integer counter indicating the message number that was sent
        on the channel via Basic.Publish. Here we're just doing house keeping
        to keep track of stats and remove message numbers that we expect
        a delivery confirmation of from the list used to keep track of messages
        that are pending confirmation.

        :param  method_frame: Basic.Ack or Basic.Nack frame
        :type method_frame: pika.frame.Method

        """

        LOGGER.info('[RabbitLogClient] Publisher Delivery Confirmation received from broker')

        confirmation_type = method_frame.method.NAME.split('.')[1].lower()

        LOGGER.info('[RabbitLogClient] Received %s for delivery tag: %i ' %
                    (confirmation_type, method_frame.method.delivery_tag))

        if confirmation_type == 'ack':
            self._acked += 1
        elif confirmation_type == 'nack':
            self._nacked += 1

        self._deliveries.remove(method_frame.method.delivery_tag)

        LOGGER.info('[RabbitLogClient] Published %i messages, %i have yet to be confirmed, %i were acked and %i were nacked ' % (
            self._message_number, len(self._deliveries), self._acked, self._nacked))



    def publish(self, msg, routing_key, exchange=None, delivery_mode=2):
        """If the class is not stopping, publish a message to RabbitMQ,
        appending a list of deliveries with the message number that was sent.
        This list will be used to check for delivery confirmations in the
        on_delivery_confirmations method.

        Once the message has been sent, schedule another message to be sent.
        The main reason I put scheduling in was just so you can get a good idea
        of how the process is flowing by slowing down and speeding up the
        delivery intervals by changing the PUBLISH_INTERVAL constant in the
        class.

        :param msg: Message to be published to Channel
        :tyep msg: string
        :param routing_key: Routing Key to direct message via the Exchange
        :type routing_key: string 

        """


        LOGGER.info('[RabbitLogClient] Publishing message')

        properties = pika.BasicProperties(content_type='application/msgpack',
                                          headers=msg,
                                          delivery_mode=delivery_mode,
                                          app_id=self._id
                                          )


        msg = msgpack.packb(msg, use_bin_type=True)

        self._channel.basic_publish(exchange=exchange if exchange else self._exchange,
                                    routing_key=routing_key,
                                    body=msg,
                                    properties=properties)

        self._message_number += 1

        self._deliveries.append(self._message_number)

        LOGGER.info('[RabbitLogClient] Message published')






    def start(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.

        """

        LOGGER.info('[RabbitLogClient] starting the rabbitmq connection')

        self._connection = self.connect()
        # self._connection.ioloop.start()



    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.

        """


        LOGGER.info('[RabbitLogClient] Stopping RabbitLogClient object... : %s ' % self)

        self.close_channel()
        self.close_connection()

        LOGGER.info('[RabbitLogClient] RabbitLogClient Stopped')


    @property
    def status(self):
        """Gives the status of the RabbitLogClient Connection.


        :return: Returns the current status of the connection
        :rtype: self._status

        """


        return self._status















class Log():

	NOTSET = 0
	DEBUG = 10
	INFO = 20
	WARNING = 30
	ERROR = 40
	CRITICAL = 50

	# Example Log Structure : 
	# { 'type': 'ERROR',
	#   'time': '12-07-2016 08:35:43 pm',
	#   'location': 'ubernow.apps.main.views.IndexHandler',
	#   'msg': 'Invalid Request Error',
	#   'description': 'The request type is invalid',
	# 	'other/request/call' : 'any arbitrary info to be added to description'
	#  }

	def __init__(self, app_name='default', loglevel=10, exchange=EXCHANGE, exchange_type=EXCHANGE_TYPE):
		self.loglevel = loglevel
		self.log_client = RabbitLogClient(exchange=exchange,
                                    exchange_type=exchange_type,
                                    exchange_durability=True,
                                    logid=None
                                    )
		self.log_client.start()
        self.app_name = app_name

	def setLevel(self, loglevel):
		self.loglevel = loglevel


	def getLevel(self):
		return self.loglevel


	def log_msg(self, loglevel, msg):
		if loglevel >= self.loglevel:
			msg['time'] = utils.localTime()
			self.log_client.publish(msgpack.packb(msg, use_bin_type=True),
                           routing_key=self.app_name + '.' + str(loglevel),
                           exchange='log_exchange',
                           delivery_mode=2
                           )

	def debug(self, msg):
		msg['type'] = 'DEBUG'
		self.log_msg(Log.DEBUG, msg)



	def info(self, msg):
		msg['type'] = 'INFO'
		self.log_msg(Log.INFO, msg)



	def warning(self, msg):
		msg['type'] = 'WARNING'
		self.log_msg(Log.WARNING, msg)


	def error(self, msg):
		msg['type'] = 'ERROR'
		self.log_msg(Log.ERROR, msg)


	def critical(self, msg):
		msg['type'] = 'CRITICAL'
		self.log_msg(Log.CRITICAL, msg)


	def log(self, msg):
		msg['type'] = 'NOTSET'
		self.log_msg(Log.NOTSET, msg)


