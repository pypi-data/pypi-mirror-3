import logging

from sockjs.tornado import SockJSConnection
from thunderpush.messenger import Messenger
from thunderpush.sortingstation import SortingStation

try:
    import json
except ImportError:
    import simplejson as json 

logger = logging.getLogger()

class ThunderSocketHandler(SockJSConnection):
    def on_open(self, info):
        logger.debug("New connection opened.")

        # no messenger object yet, client needs issue CONNECT command first
        self.messenger = None

    def on_message(self, msg):
        logger.debug("Got message: %s" % msg)

        self.process_message(msg)

    def on_close(self):
        if self.connected:
            self.messenger.unregister_user(self)
            self.messenger = None

        logger.debug("User %s has disconnected." % self.userid)

    def process_message(self, msg):
        """
        We assume that every client message comes in following format:
        COMMAND argument1[:argument2[:argumentX]]
        """

        tokens = msg.split(" ")

        messages = {
            'CONNECT': self.handle_connect,
            'SUBSCRIBE': self.handle_subscribe
        }

        try:
            messages[tokens[0]](tokens[1])
        except (KeyError, IndexError):
            logger.warning("Received invalid message: %s." % msg)

    def handle_connect(self, args):
        if self.connected:
            logger.warning("User already connected.")
            return

        try:
            self.userid, self.apikey = args.split(":")
        except ValueError:
            logger.warning("Invalid message syntax.")
            return

        # get singleton instance of SortingStation
        ss = SortingStation.instance()

        # get and store the messenger object for given apikey
        self.messenger = ss.get_messenger_by_apikey(self.apikey)

        if self.messenger:
            self.messenger.register_user(self)
        else:
            logger.warning("Invalid API key.")

            # inform client that the key was not good
            self.send("WRONGKEY")
            self.close()

    def handle_subscribe(self, args):
        if not self.connected:
            logger.warning("User not connected.")
            return

        channels = args.split(":")

        if len(channels):
            for channel in channels:
                self.messenger.subsribe_user_to_channel(self, channel)

    @property
    def connected(self):
        return bool(self.messenger)
    