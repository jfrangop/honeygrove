import base64

from pybroker import *

from honeygrove import config


class BrokerEndpoint:
    """
    The BrokerEndpoint is for the transmission of Broker messages.
    You can send and retrive messages here.
    """

    # Creates endpoint and sets flags
    flags = AUTO_ADVERTISE | AUTO_PUBLISH | AUTO_ROUTING
    listenEndpoint = endpoint("listenEndpoint", flags)

    # commands and settings are topics we subscribed to. (GLOBAL SCOPE for multihop)
    commandsQueue = message_queue("commands", listenEndpoint, GLOBAL_SCOPE)

    # peering objects. needet for unpeering
    peerings = [0, 0, None]


    @staticmethod
    def getCommandMessage():
        """
        Gets a message from the command message_queue
        :return: Broker Message
        """
        return BrokerEndpoint.commandsQueue.want_pop()

    @staticmethod
    def sendLogs(jsonString):
        """
        Sends a Broker message containing a JSON string.
        :param jsonString: Json string.
        """
        BrokerEndpoint.listenEndpoint.send("logs", message([data(jsonString)]))

    @staticmethod
    def startListening():
        """
        Start listening on ip
        """
        BrokerEndpoint.listenEndpoint.listen(config.BrokerComPort, config.BrokerComIP)

    @staticmethod
    def peerTo(ip, port):
        """
        Peering to given port/ip
        logic for unpeering included if peered
        :param ip: string
        :param port: int
        """
        if [ip, port] != BrokerEndpoint.peerings[0:2]:
            if BrokerEndpoint.peerings[0] != 0:
                BrokerEndpoint.unPeer(BrokerEndpoint.peerings[2])

            obj = BrokerEndpoint.listenEndpoint.peer(ip, port)
            BrokerEndpoint.peerings = [ip, port, obj]

    @staticmethod
    def unPeer(peeringObj=None):
        """
        unpeering to given port/ip
        :param peeringObj: peering objekt
        """
        if peeringObj is None:
            BrokerEndpoint.listenEndpoint.unpeer(BrokerEndpoint.peerings[2])
        else:
            BrokerEndpoint.listenEndpoint.unpeer(peeringObj)


    @staticmethod
    def sendMessageToTopic(topic, msg):
        """
        Sends a Broker Message to a given topic
        :param topic: string with topic
        :param msg: can be str, int, double
        """
        BrokerEndpoint.listenEndpoint.send(topic, message([data(msg)]))

    @staticmethod
    def sendFile(filepath):
        """
        Sends a file to the file topic
        :param filepath: path to the file
        """
        with open(filepath, "rb") as file:
            content = file.read()
            b64content = base64.b64encode(content)
            BrokerEndpoint.listenEndpoint.send("files", message([data(b64content.decode(encoding="utf-8"))]))

