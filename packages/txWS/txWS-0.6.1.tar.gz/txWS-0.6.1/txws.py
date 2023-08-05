# Copyright (c) 2011 Oregon State University

"""
Blind reimplementation of WebSockets as a standalone wrapper for Twisted
protocols.
"""

from base64 import b64encode, b64decode
from hashlib import md5, sha1
from string import digits
from struct import pack, unpack

from twisted.internet.interfaces import ISSLTransport
from twisted.protocols.policies import ProtocolWrapper, WrappingFactory
from twisted.python import log
from twisted.web.http import datetimeToString

# Flavors of WS supported here.
# HYBI00 - Hixie-76, HyBi-00. Challenge/response after headers, very minimal
#          framing. Tricky to start up, but very smooth sailing afterwards.
# HYBI07 - HyBi-07. Modern "standard" handshake. Bizarre masked frames, lots
#          of binary data packing.

HYBI00, HYBI07 = range(2)

# States of the state machine. Because there are no reliable byte counts for
# any of this, we don't use StatefulProtocol; instead, we use custom state
# enumerations. Yay!

REQUEST, NEGOTIATING, CHALLENGE, FRAMES = range(4)

# Control frame specifiers. Some versions of WS have control signals sent
# in-band. Adorable, right?

NORMAL, CLOSE, PING, PONG = range(4)

opcode_types = {
    0x0: NORMAL,
    0x1: NORMAL,
    0x2: NORMAL,
    0x8: CLOSE,
    0x9: PING,
    0xa: PONG,
}

encoders = {
    "base64": b64encode,
}

decoders = {
    "base64": b64decode,
}

# Fake HTTP stuff, and a couple convenience methods for examining fake HTTP
# headers.

def http_headers(s):
    """
    Create a dictionary of data from raw HTTP headers.
    """

    d = {}

    for line in s.split("\r\n"):
        try:
            key, value = [i.strip() for i in line.split(":", 1)]
            d[key] = value
        except ValueError:
            pass

    return d

def is_websocket(headers):
    """
    Determine whether a given set of headers is asking for WebSockets.
    """

    return ("Upgrade" in headers.get("Connection", "")
            and headers.get("Upgrade").lower() == "websocket")

def is_hybi00(headers):
    """
    Determine whether a given set of headers is HyBi-00-compliant.

    Hixie-76 and HyBi-00 use a pair of keys in the headers to handshake with
    servers.
    """

    return "Sec-WebSocket-Key1" in headers and "Sec-WebSocket-Key2" in headers

# Authentication for WS.

def complete_hybi00(headers, challenge):
    """
    Generate the response for a HyBi-00 challenge.
    """

    key1 = headers["Sec-WebSocket-Key1"]
    key2 = headers["Sec-WebSocket-Key2"]

    first = int("".join(i for i in key1 if i in digits)) / key1.count(" ")
    second = int("".join(i for i in key2 if i in digits)) / key2.count(" ")

    nonce = pack(">II8s", first, second, challenge)

    return md5(nonce).digest()

def make_accept(key):
    """
    Create an "accept" response for a given key.

    This dance is expected to somehow magically make WebSockets secure.
    """

    guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    return sha1("%s%s" % (key, guid)).digest().encode("base64").strip()

# Frame helpers.
# Separated out to make unit testing a lot easier.
# Frames are bonghits in newer WS versions, so helpers are appreciated.

def make_hybi00_frame(buf):
    """
    Make a HyBi-00 frame from some data.

    This function does exactly zero checks to make sure that the data is safe
    and valid text without any 0xff bytes.
    """

    return "\x00%s\xff" % buf

def parse_hybi00_frames(buf):
    """
    Parse HyBi-00 frames, returning unwrapped frames and any unmatched data.

    This function does not care about garbage data on the wire between frames,
    and will actively ignore it.
    """

    start = buf.find("\x00")
    frames = []

    while start != -1:
        end = buf.find("\xff")
        if end == -1:
            # Incomplete frame, try again later.
            return frames, buf
        else:
            frame, buf = buf[start + 1:end], buf[end + 1:]
            # Found a frame, put it in the list.
            frames.append((NORMAL, frame))
        start = buf.find("\x00")

    # We appear to have hit an exact frame boundary. This is actually pretty
    # likely with a lot of implementations.
    return frames, buf

def mask(buf, key):
    """
    Mask or unmask a buffer of bytes with a masking key.

    The key must be exactly four bytes long.
    """

    # This is super-secure, I promise~
    key = [ord(i) for i in key]
    buf = list(buf)
    for i, char in enumerate(buf):
        buf[i] = chr(ord(char) ^ key[i % 4])
    return "".join(buf)

def make_hybi07_frame(buf):
    """
    Make a HyBi-07 frame.

    This function always creates unmasked frames, and attempts to use the
    smallest possible lengths.
    """

    if len(buf) > 0xffff:
        length = "\x7f%s" % pack(">Q", len(buf))
    elif len(buf) > 0x7d:
        length = "\x7e%s" % pack(">H", len(buf))
    else:
        length = chr(len(buf))

    # Always make a normal packet.
    frame = "\x81%s%s" % (length, buf)
    return frame

def parse_hybi07_frames(buf):
    """
    Parse HyBi-07 frames in a highly compliant manner.

    This function requires *complete* frames and does highly bogus things if
    fed incomplete frames.
    """

    frames = []

    while buf:
        # Grab the header. This single byte holds some flags nobody cares
        # about, and an opcode which nobody cares about.
        header, buf = ord(buf[0]), buf[1:]
        if header & 0x70:
            # At least one of the reserved flags is set. Pork chop sandwiches!
            raise Exception("Reserved flag in HyBi-07 frame (%d)" % header)
            frames.append(("", CLOSE))
            return frames, buf

        # Get the opcode, and translate it to a local enum which we actually
        # care about.
        opcode = header & 0xf
        try:
            opcode = opcode_types[opcode]
        except KeyError:
            raise Exception("Unknown opcode %d in HyBi-07 frame!" % opcode)

        # Get the payload length and determine whether we need to look for an
        # extra length.
        length, buf = ord(buf[0]), buf[1:]
        masked = length & 0x80
        length &= 0x7f

        # Extra length fields.
        if length == 0x7e:
            length, buf = buf[:4], buf[4:]
            length = unpack(">H", length)[0]
        elif length == 0x7f:
            # Protocol bug: The top bit of this long long *must* be cleared;
            # that is, it is expected to be interpreted as signed. That's
            # fucking stupid, if you don't mind me saying so, and so we're
            # interpreting it as unsigned anyway. If you wanna send exabytes
            # of data down the wire, then go ahead!
            length, buf = buf[:8], buf[8:]
            length = unpack(">Q", length)[0]

        if masked:
            key, buf = buf[:4], buf[4:]

        data, buf = buf[:length], buf[length:]

        if masked:
            data = mask(data, key)

        if opcode == CLOSE:
            # Gotta unpack the opcode and return usable data here.
            data = unpack(">H", data[:2])[0], data[2:]

        frames.append((opcode, data))

    return frames, buf

class WebSocketProtocol(ProtocolWrapper):
    """
    Protocol which wraps another protocol to provide a WebSockets transport
    layer.
    """

    buf = ""
    codec = None
    location = "/"
    host = "example.com"
    origin = "http://example.com"
    state = REQUEST
    flavor = None

    def __init__(self, *args, **kwargs):
        ProtocolWrapper.__init__(self, *args, **kwargs)
        self.pending_frames = []

    def isSecure(self):
        """
        Borrowed technique for determining whether this connection is over
        SSL/TLS.
        """

        return ISSLTransport(self.transport, None) is not None

    def sendCommonPreamble(self):
        """
        Send the preamble common to all WebSockets connections.

        This might go away in the future if WebSockets continue to diverge.
        """

        self.transport.writeSequence([
            "HTTP/1.1 101 FYI I am not a webserver\r\n",
            "Server: TwistedWebSocketWrapper/1.0\r\n",
            "Date: %s\r\n" % datetimeToString(),
            "Upgrade: WebSocket\r\n",
            "Connection: Upgrade\r\n",
        ])

    def sendHyBi00Preamble(self):
        """
        Send a HyBi-00 preamble.
        """

        protocol = "wss" if self.isSecure() else "ws"

        self.sendCommonPreamble()

        self.transport.writeSequence([
            "Sec-WebSocket-Origin: %s\r\n" % self.origin,
            "Sec-WebSocket-Location: %s://%s%s\r\n" % (protocol, self.host,
                                                       self.location),
            "WebSocket-Protocol: %s\r\n" % self.codec,
            "Sec-WebSocket-Protocol: %s\r\n" % self.codec,
            "\r\n",
        ])

    def sendHyBi07Preamble(self):
        """
        Send a HyBi-07 preamble.
        """

        self.sendCommonPreamble()
        challenge = self.headers["Sec-WebSocket-Key"]
        response = make_accept(challenge)

        self.transport.write("Sec-WebSocket-Accept: %s\r\n\r\n" % response)

    def parseFrames(self):
        """
        Find frames in incoming data and pass them to the underlying protocol.
        """

        if self.flavor == HYBI00:
            parser = parse_hybi00_frames
        elif self.flavor == HYBI07:
            parser = parse_hybi07_frames
        else:
            raise Exception("Unknown flavor %r!" % self.flavor)

        frames, self.buf = parser(self.buf)

        for frame in frames:
            opcode, data = frame
            if opcode == NORMAL:
                # Business as usual. Decode the frame, if we have a decoder.
                if self.codec:
                    data = decoders[self.codec](data)
                # Pass the frame to the underlying protocol.
                ProtocolWrapper.dataReceived(self, data)
            elif opcode == CLOSE:
                # The other side wants us to close. I wonder why?
                reason, text = data
                log.msg("Closing connection: %r (%d)" % (text, reason))

                # Send the smallest possible closing message.
                # XXX totally protocol-7 specific
                self.transport.write("\x88\x00")

    def sendFrames(self):
        """
        Send all pending frames.
        """

        if self.state != FRAMES:
            return

        if self.flavor == HYBI00:
            maker = make_hybi00_frame
        elif self.flavor == HYBI07:
            maker = make_hybi07_frame
        else:
            raise Exception("Unknown flavor %r!" % self.flavor)

        for frame in self.pending_frames:
            # Encode the frame before sending it.
            if self.codec:
                frame = encoders[self.codec](frame)
            packet = maker(frame)
            self.transport.write(packet)
        self.pending_frames = []

    def validateHeaders(self):
        """
        Check received headers for sanity and correctness, and stash any data
        from them which will be required later.
        """

        # Obvious but necessary.
        if not is_websocket(self.headers):
            log.msg("Not handling non-WS request")
            return False

        # Stash host and origin for those browsers that care about it.
        if "Host" in self.headers:
            self.host = self.headers["Host"]
        if "Origin" in self.headers:
            self.origin = self.headers["Origin"]

        # Check whether a codec is needed. WS calls this a "protocol" for
        # reasons I cannot fathom.
        protocol = None
        if "WebSocket-Protocol" in self.headers:
            protocol = self.headers["WebSocket-Protocol"]
        elif "Sec-WebSocket-Protocol" in self.headers:
            protocol = self.headers["Sec-WebSocket-Protocol"]

        if protocol:
            if protocol not in encoders or protocol not in decoders:
                log.msg("Couldn't handle WS protocol %s!" % protocol)
                return False
            self.codec = protocol

        # Start the next phase of the handshake for HyBi-00.
        if is_hybi00(self.headers):
            log.msg("Starting HyBi-00/Hixie-76 handshake")
            self.flavor = HYBI00
            self.state = CHALLENGE

        # Start the next phase of the handshake for HyBi-07+.
        if "Sec-WebSocket-Version" in self.headers:
            version = self.headers["Sec-WebSocket-Version"]
            if version == "7":
                log.msg("Starting HyBi-07 conversation")
                self.sendHyBi07Preamble()
                self.flavor = HYBI07
                self.state = FRAMES
            else:
                log.msg("Can't support protocol version %s!" % version)
                return False

        return True

    def dataReceived(self, data):
        self.buf += data

        oldstate = None

        while oldstate != self.state:
            oldstate = self.state

            # Handle initial requests. These look very much like HTTP
            # requests, but aren't. We need to capture the request path for
            # those browsers which want us to echo it back to them (Chrome,
            # mainly.)
            # These lines look like:
            # GET /some/path/to/a/websocket/resource HTTP/1.1
            if self.state == REQUEST:
                if "\r\n" in self.buf:
                    request, chaff, self.buf = self.buf.partition("\r\n")
                    try:
                        verb, self.location, version = request.split(" ")
                    except ValueError:
                        self.loseConnection()
                    else:
                        self.state = NEGOTIATING

            elif self.state == NEGOTIATING:
                # Check to see if we've got a complete set of headers yet.
                if "\r\n\r\n" in self.buf:
                    head, chaff, self.buf = self.buf.partition("\r\n\r\n")
                    self.headers = http_headers(head)
                    # Validate headers. This will cause a state change.
                    if not self.validateHeaders():
                        self.loseConnection()

            elif self.state == CHALLENGE:
                # Handle the challenge. This is completely exclusive to
                # HyBi-00/Hixie-76.
                if len(self.buf) >= 8:
                    challenge, self.buf = self.buf[:8], self.buf[8:]
                    response = complete_hybi00(self.headers, challenge)
                    self.sendHyBi00Preamble()
                    self.transport.write(response)
                    log.msg("Completed HyBi-00/Hixie-76 handshake")
                    # Start sending frames, and kick any pending frames.
                    self.state = FRAMES
                    self.sendFrames()

            elif self.state == FRAMES:
                self.parseFrames()

    def write(self, data):
        """
        Write to the transport.

        This method will only be called by the underlying protocol.
        """

        self.pending_frames.append(data)
        self.sendFrames()

class WebSocketFactory(WrappingFactory):
    """
    Factory which wraps another factory to provide WebSockets transports for
    all of its protocols.
    """

    protocol = WebSocketProtocol
