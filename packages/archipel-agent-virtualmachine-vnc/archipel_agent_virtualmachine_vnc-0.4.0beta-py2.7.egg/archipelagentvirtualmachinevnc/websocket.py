'''
Python WebSocket library with support for "wss://" encryption.
Copyright 2011 Joel Martin
Licensed under LGPL version 3 (see docs/LICENSE.LGPL-3)

Supports following protocol versions:
    - http://tools.ietf.org/html/draft-hixie-thewebsocketprotocol-75
    - http://tools.ietf.org/html/draft-hixie-thewebsocketprotocol-76
    - http://tools.ietf.org/html/draft-ietf-hybi-thewebsocketprotocol-07

You can make a cert/key with openssl using:
openssl req -new -x509 -days 365 -nodes -out self.pem -keyout self.pem
as taken from http://docs.python.org/dev/library/ssl.html#certificates

'''

import os, sys, time, errno, socket, struct, traceback, select
from cgi import parse_qsl
from threading import Thread
from base64 import b64encode, b64decode

# Imports that vary by python version
if sys.hexversion > 0x3000000:
    # python >= 3.0
    from io import StringIO
    from http.server import SimpleHTTPRequestHandler
    from urllib.parse import urlsplit
    b2s = lambda buf: buf.decode('latin_1')
    s2b = lambda s: s.encode('latin_1')
else:
    # python 2.X
    from cStringIO import StringIO
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from urlparse import urlsplit
    # No-ops
    b2s = lambda buf: buf
    s2b = lambda s: s

if sys.hexversion >= 0x2060000:
    # python >= 2.6
    from multiprocessing import Process
    from hashlib import md5, sha1
else:
    # python < 2.6
    Process = None
    from md5 import md5
    from sha import sha as sha1

# Degraded functionality if these imports are missing
for mod, sup in [('numpy', 'HyBi protocol'),
        ('ssl', 'TLS/SSL/wss'), ('resource', 'daemonizing')]:
    try:
        globals()[mod] = __import__(mod)
    except ImportError:
        globals()[mod] = None
        print("WARNING: no '%s' module, %s support disabled" % (
            mod, sup))


class WebSocketServer(Thread):
    """
    WebSockets server class.
    Must be sub-classed with new_client method definition.
    """

    buffer_size = 65536

    server_handshake_hixie = """HTTP/1.1 101 Web Socket Protocol Handshake\r
Upgrade: WebSocket\r
Connection: Upgrade\r
%sWebSocket-Origin: %s\r
%sWebSocket-Location: %s://%s%s\r
"""

    server_handshake_hybi = """HTTP/1.1 101 Switching Protocols\r
Upgrade: websocket\r
Connection: Upgrade\r
Sec-WebSocket-Accept: %s\r
"""

    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    policy_response = """<cross-domain-policy><allow-access-from domain="*" to-ports="*" /></cross-domain-policy>\n"""

    class EClose(Exception):
        pass

    def __init__(self, listen_host='', listen_port=None, source_is_ipv6=False,
            verbose=False, cert='', key='', ssl_only=None,
            daemon=False, record='', web=''):

        Thread.__init__(self)

        # settings
        self.verbose        = verbose
        self.listen_host    = listen_host
        self.listen_port    = listen_port
        self.ssl_only       = ssl_only
        self.daemon         = daemon
        self.handler_id     = 1

        # Make paths settings absolute
        self.cert = os.path.abspath(cert)
        self.key = self.web = self.record = ''
        if key:
            self.key = os.path.abspath(key)
        if web:
            self.web = os.path.abspath(web)
        if record:
            self.record = os.path.abspath(record)

        if self.web:
            os.chdir(self.web)

        # Sanity checks
        if not ssl and self.ssl_only:
            raise Exception("No 'ssl' module and SSL-only specified")
        if self.daemon and not resource:
            raise Exception("Module 'resource' required to daemonize")

        # Show configuration
        print("WebSocket server settings:")
        print("  - Listen on %s:%s" % (
                self.listen_host, self.listen_port))
        print("  - Flash security policy server")
        if self.web:
            print("  - Web server. Web root: %s" % self.web)
        if ssl:
            if os.path.exists(self.cert):
                print("  - SSL/TLS support")
                if self.ssl_only:
                    print("  - Deny non-SSL/TLS connections")
            else:
                print("  - No SSL/TLS support (no cert file)")
        else:
            print("  - No SSL/TLS support (no 'ssl' module)")
        if self.daemon:
            print("  - Backgrounding (daemon)")
        if self.record:
            print("  - Recording to '%s.*'" % self.record)

    #
    # WebSocketServer static methods
    #

    @staticmethod
    def socket(host, port=None, connect=False, prefer_ipv6=False):
        """ Resolve a host (and optional port) to an IPv4 or IPv6
        address. Create a socket. Bind to it if listen is set,
        otherwise connect to it. Return the socket.
        """
        flags = 0
        if host == '':
            host = None
        if connect and not port:
            raise Exception("Connect mode requires a port")
        if not connect:
            flags = flags | socket.AI_PASSIVE
        addrs = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM,
                socket.IPPROTO_TCP, flags)
        if not addrs:
            raise Exception("Could resolve host '%s'" % host)
        addrs.sort(key=lambda x: x[0])
        if prefer_ipv6:
            addrs.reverse()
        sock = socket.socket(addrs[0][0], addrs[0][1])
        if connect:
            sock.connect(addrs[0][4])
        else:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(addrs[0][4])
            sock.listen(100)
        return sock

    @staticmethod
    def encode_hybi(buf, opcode, base64=False):
        """ Encode a HyBi style WebSocket frame.
        Optional opcode:
            0x0 - continuation
            0x1 - text frame (base64 encode buf)
            0x2 - binary frame (use raw buf)
            0x8 - connection close
            0x9 - ping
            0xA - pong
        """
        if base64:
            buf = b64encode(buf)

        b1 = 0x80 | (opcode & 0x0f) # FIN + opcode
        payload_len = len(buf)
        if payload_len <= 125:
            header = struct.pack('>BB', b1, payload_len)
        elif payload_len > 125 and payload_len < 65536:
            header = struct.pack('>BBH', b1, 126, payload_len)
        elif payload_len >= 65536:
            header = struct.pack('>BBQ', b1, 127, payload_len)

        #print("Encoded: %s" % repr(header + buf))

        return header + buf, len(header), 0

    @staticmethod
    def decode_hybi(buf, base64=False):
        """ Decode HyBi style WebSocket packets.
        Returns:
            {'fin'          : 0_or_1,
             'opcode'       : number,
             'mask'         : 32_bit_number,
             'hlen'         : header_bytes_number,
             'length'       : payload_bytes_number,
             'payload'      : decoded_buffer,
             'left'         : bytes_left_number,
             'close_code'   : number,
             'close_reason' : string}
        """

        f = {'fin'          : 0,
             'opcode'       : 0,
             'mask'         : 0,
             'hlen'         : 2,
             'length'       : 0,
             'payload'      : None,
             'left'         : 0,
             'close_code'   : None,
             'close_reason' : None}

        blen = len(buf)
        f['left'] = blen

        if blen < f['hlen']:
            return f # Incomplete frame header

        b1, b2 = struct.unpack_from(">BB", buf)
        f['opcode'] = b1 & 0x0f
        f['fin'] = (b1 & 0x80) >> 7
        has_mask = (b2 & 0x80) >> 7

        f['length'] = b2 & 0x7f

        if f['length'] == 126:
            f['hlen'] = 4
            if blen < f['hlen']:
                return f # Incomplete frame header
            (f['length'],) = struct.unpack_from('>xxH', buf)
        elif f['length'] == 127:
            f['hlen'] = 10
            if blen < f['hlen']:
                return f # Incomplete frame header
            (f['length'],) = struct.unpack_from('>xxQ', buf)

        full_len = f['hlen'] + has_mask * 4 + f['length']

        if blen < full_len: # Incomplete frame
            return f # Incomplete frame header

        # Number of bytes that are part of the next frame(s)
        f['left'] = blen - full_len

        # Process 1 frame
        if has_mask:
            # unmask payload
            f['mask'] = buf[f['hlen']:f['hlen']+4]
            b = c = ''
            if f['length'] >= 4:
                mask = numpy.frombuffer(buf, dtype=numpy.dtype('<u4'),
                        offset=f['hlen'], count=1)
                data = numpy.frombuffer(buf, dtype=numpy.dtype('<u4'),
                        offset=f['hlen'] + 4, count=int(f['length'] / 4))
                #b = numpy.bitwise_xor(data, mask).data
                b = numpy.bitwise_xor(data, mask).tostring()

            if f['length'] % 4:
                print("Partial unmask")
                mask = numpy.frombuffer(buf, dtype=numpy.dtype('B'),
                        offset=f['hlen'], count=(f['length'] % 4))
                data = numpy.frombuffer(buf, dtype=numpy.dtype('B'),
                        offset=full_len - (f['length'] % 4),
                        count=(f['length'] % 4))
                c = numpy.bitwise_xor(data, mask).tostring()
            f['payload'] = b + c
        else:
            print("Unmasked frame: %s" % repr(buf))
            f['payload'] = buf[(f['hlen'] + has_mask * 4):full_len]

        if base64 and f['opcode'] in [1, 2]:
            try:
                f['payload'] = b64decode(f['payload'])
            except:
                print("Exception while b64decoding buffer: %s" %
                        repr(buf))
                raise

        if f['opcode'] == 0x08:
            if f['length'] >= 2:
                f['close_code'] = struct.unpack_from(">H", f['payload'])
            if f['length'] > 3:
                f['close_reason'] = f['payload'][2:]

        return f

    @staticmethod
    def encode_hixie(buf):
        return s2b("\x00" + b2s(b64encode(buf)) + "\xff"), 1, 1

    @staticmethod
    def decode_hixie(buf):
        end = buf.find(s2b('\xff'))
        return {'payload': b64decode(buf[1:end]),
                'hlen': 1,
                'length': end - 1,
                'left': len(buf) - (end + 1)}


    @staticmethod
    def gen_md5(keys):
        """ Generate hash value for WebSockets hixie-76. """
        key1 = keys['Sec-WebSocket-Key1']
        key2 = keys['Sec-WebSocket-Key2']
        key3 = keys['key3']
        spaces1 = key1.count(" ")
        spaces2 = key2.count(" ")
        num1 = int("".join([c for c in key1 if c.isdigit()])) / spaces1
        num2 = int("".join([c for c in key2 if c.isdigit()])) / spaces2

        return b2s(md5(struct.pack('>II8s',
            int(num1), int(num2), key3)).digest())

    #
    # WebSocketServer logging/output functions
    #

    def traffic(self, token="."):
        """ Show traffic flow in verbose mode. """
        if self.verbose and not self.daemon:
            sys.stdout.write(token)
            sys.stdout.flush()

    def msg(self, msg):
        """ Output message with handler_id prefix. """
        if not self.daemon:
            print("% 3d: %s" % (self.handler_id, msg))

    def vmsg(self, msg):
        """ Same as msg() but only if verbose. """
        if self.verbose:
            self.msg(msg)

    #
    # Main WebSocketServer methods
    #
    def send_frames(self, bufs=None):
        """ Encode and send WebSocket frames. Any frames already
        queued will be sent first. If buf is not set then only queued
        frames will be sent. Returns the number of pending frames that
        could not be fully sent. If returned pending frames is greater
        than 0, then the caller should call again when the socket is
        ready. """

        tdelta = int(time.time()*1000) - self.start_time

        if bufs:
            for buf in bufs:
                if self.version.startswith("hybi"):
                    if self.base64:
                        encbuf, lenhead, lentail = self.encode_hybi(
                                buf, opcode=1, base64=True)
                    else:
                        encbuf, lenhead, lentail = self.encode_hybi(
                                buf, opcode=2, base64=False)

                else:
                    encbuf, lenhead, lentail = self.encode_hixie(buf)

                if self.rec:
                    self.rec.write("%s,\n" %
                            repr("{%s{" % tdelta
                                + encbuf[lenhead:-lentail]))

                self.send_parts.append(encbuf)

        while self.send_parts:
            # Send pending frames
            buf = self.send_parts.pop(0)
            sent = self.client.send(buf)

            if sent == len(buf):
                self.traffic("<")
            else:
                self.traffic("<.")
                self.send_parts.insert(0, buf[sent:])
                break

        return len(self.send_parts)

    def recv_frames(self):
        """ Receive and decode WebSocket frames.

        Returns:
            (bufs_list, closed_string)
        """

        closed = False
        bufs = []
        tdelta = int(time.time()*1000) - self.start_time

        buf = self.client.recv(self.buffer_size)
        if len(buf) == 0:
            closed = "Client closed abruptly"
            return bufs, closed

        if self.recv_part:
            # Add partially received frames to current read buffer
            buf = self.recv_part + buf
            self.recv_part = None

        while buf:
            if self.version.startswith("hybi"):

                frame = self.decode_hybi(buf, base64=self.base64)
                #print("Received buf: %s, frame: %s" % (repr(buf), frame))

                if frame['payload'] == None:
                    # Incomplete/partial frame
                    self.traffic("}.")
                    if frame['left'] > 0:
                        self.recv_part = buf[-frame['left']:]
                    break
                else:
                    if frame['opcode'] == 0x8: # connection close
                        closed = "Client closed, reason: %s - %s" % (
                                frame['close_code'],
                                frame['close_reason'])
                        break

            else:
                if buf[0:2] == '\xff\x00':
                    closed = "Client sent orderly close frame"
                    break

                elif buf[0:2] == '\x00\xff':
                    buf = buf[2:]
                    continue # No-op

                elif buf.count(s2b('\xff')) == 0:
                    # Partial frame
                    self.traffic("}.")
                    self.recv_part = buf
                    break

                frame = self.decode_hixie(buf)

            self.traffic("}")

            if self.rec:
                start = frame['hlen']
                end = frame['hlen'] + frame['length']
                self.rec.write("%s,\n" %
                        repr("}%s}" % tdelta + buf[start:end]))


            bufs.append(frame['payload'])

            if frame['left']:
                buf = buf[-frame['left']:]
            else:
                buf = ''

        return bufs, closed

    def send_close(self, code=None, reason=''):
        """ Send a WebSocket orderly close frame. """

        if self.version.startswith("hybi"):
            msg = s2b('')
            if code != None:
                msg = struct.pack(">H%ds" % (len(reason)), code)

            buf, h, t = self.encode_hybi(msg, opcode=0x08, base64=False)
            self.client.send(buf)

        elif self.version == "hixie-76":
            buf = s2b('\xff\x00')
            self.client.send(buf)

        # No orderly close for 75

    def do_handshake(self, sock, address):
        """
        do_handshake does the following:
        - Peek at the first few bytes from the socket.
        - If the connection is Flash policy request then answer it,
          close the socket and return.
        - If the connection is an HTTPS/SSL/TLS connection then SSL
          wrap the socket.
        - Read from the (possibly wrapped) socket.
        - If we have received a HTTP GET request and the webserver
          functionality is enabled, answer it, close the socket and
          return.
        - Assume we have a WebSockets connection, parse the client
          handshake data.
        - Send a WebSockets handshake server response.
        - Return the socket for this WebSocket client.
        """

        stype = ""

        ready = select.select([sock], [], [], 3)[0]
        if not ready:
            raise self.EClose("ignoring socket not ready")
        # Peek, but do not read the data so that we have a opportunity
        # to SSL wrap the socket first
        handshake = sock.recv(1024, socket.MSG_PEEK)
        #self.msg("Handshake [%s]" % handshake)

        if handshake == "":
            raise self.EClose("ignoring empty handshake")

        elif handshake.startswith(s2b("<policy-file-request/>")):
            # Answer Flash policy request
            handshake = sock.recv(1024)
            sock.send(s2b(self.policy_response))
            raise self.EClose("Sending flash policy response")

        elif handshake[0] in ("\x16", "\x80"):
            # SSL wrap the connection
            if not ssl:
                raise self.EClose("SSL connection but no 'ssl' module")
            if not os.path.exists(self.cert):
                raise self.EClose("SSL connection but '%s' not found"
                                  % self.cert)
            retsock = None
            try:
                retsock = ssl.wrap_socket(
                        sock,
                        server_side=True,
                        certfile=self.cert,
                        keyfile=self.key)
            except ssl.SSLError:
                _, x, _ = sys.exc_info()
                if x.args[0] == ssl.SSL_ERROR_EOF:
                    raise self.EClose("")
                else:
                    raise

            scheme = "wss"
            stype = "SSL/TLS (wss://)"

        elif self.ssl_only:
            raise self.EClose("non-SSL connection received but disallowed")

        else:
            retsock = sock
            scheme = "ws"
            stype = "Plain non-SSL (ws://)"

        wsh = WSRequestHandler(retsock, address, not self.web)
        if wsh.last_code == 101:
            # Continue on to handle WebSocket upgrade
            pass
        elif wsh.last_code == 405:
            raise self.EClose("Normal web request received but disallowed")
        elif wsh.last_code < 200 or wsh.last_code >= 300:
            raise self.EClose(wsh.last_message)
        elif self.verbose:
            raise self.EClose(wsh.last_message)
        else:
            raise self.EClose("")

        h = self.headers = wsh.headers
        path = self.path = wsh.path

        prot = 'WebSocket-Protocol'
        protocols = h.get('Sec-'+prot, h.get(prot, '')).split(',')

        ver = h.get('Sec-WebSocket-Version')
        if ver:
            # HyBi/IETF version of the protocol

            if sys.hexversion < 0x2060000 or not numpy:
                raise self.EClose("Python >= 2.6 and numpy module is required for HyBi-07 or greater")

            # HyBi-08 - HyBi-12 report version 8
            # HyBi-13 reports version 13
            if ver in ['7', '8', '13']:
                self.version = "hybi-%02d" % int(ver)
            else:
                raise self.EClose('Unsupported protocol version %s' % ver)

            key = h['Sec-WebSocket-Key']

            # Choose binary if client supports it
            if 'binary' in protocols:
                self.base64 = False
            elif 'base64' in protocols:
                self.base64 = True
            else:
                raise self.EClose("Client must support 'binary' or 'base64' protocol")

            # Generate the hash value for the accept header
            accept = b64encode(sha1(s2b(key + self.GUID)).digest())

            response = self.server_handshake_hybi % accept
            if self.base64:
                response += "Sec-WebSocket-Protocol: base64\r\n"
            else:
                response += "Sec-WebSocket-Protocol: binary\r\n"
            response += "\r\n"

        else:
            # Hixie version of the protocol (75 or 76)

            if h.get('key3'):
                trailer = self.gen_md5(h)
                pre = "Sec-"
                self.version = "hixie-76"
            else:
                trailer = ""
                pre = ""
                self.version = "hixie-75"

            # We only support base64 in Hixie era
            self.base64 = True

            response = self.server_handshake_hixie % (pre,
                    h['Origin'], pre, scheme, h['Host'], path)

            if 'base64' in protocols:
                response += "%sWebSocket-Protocol: base64\r\n" % pre
            else:
                self.msg("Warning: client does not report 'base64' protocol support")
            response += "\r\n" + trailer

        self.msg("%s: %s WebSocket connection" % (address[0], stype))
        self.msg("%s: Version %s, base64: '%s'" % (address[0],
            self.version, self.base64))

        # Send server WebSockets handshake response
        #self.msg("sending response [%s]" % response)
        retsock.send(s2b(response))

        # Return the WebSockets socket which may be SSL wrapped
        return retsock


    #
    # Events that can/should be overridden in sub-classes
    #
    def started(self):
        """ Called after WebSockets startup """
        self.vmsg("WebSockets server started")

    def poll(self):
        """ Run periodically while waiting for connections. """
        #self.vmsg("Running poll()")
        pass

    def fallback_SIGCHLD(self, sig, stack):
        # Reap zombies when using os.fork() (python 2.4)
        self.vmsg("Got SIGCHLD, reaping zombies")
        try:
            result = os.waitpid(-1, os.WNOHANG)
            while result[0]:
                self.vmsg("Reaped child process %s" % result[0])
                result = os.waitpid(-1, os.WNOHANG)
        except (OSError):
            pass

    def do_SIGINT(self, sig, stack):
        self.msg("Got SIGINT, exiting")
        sys.exit(0)

    def top_new_client(self, startsock, address):
        """ Do something with a WebSockets client connection. """
        # Initialize per client settings
        self.send_parts = []
        self.recv_part  = None
        self.base64     = False
        self.rec        = None
        self.start_time = int(time.time()*1000)

        # handler process
        try:
            try:
                self.client = self.do_handshake(startsock, address)

                if self.record:
                    # Record raw frame data as JavaScript array
                    fname = "%s.%s" % (self.record,
                                        self.handler_id)
                    self.msg("opening record file: %s" % fname)
                    self.rec = open(fname, 'w+')
                    self.rec.write("var VNC_frame_data = [\n")

                self.new_client()
            except self.EClose:
                _, exc, _ = sys.exc_info()
                # Connection was not a WebSockets connection
                if exc.args[0]:
                    self.msg("%s: %s" % (address[0], exc.args[0]))
            except Exception:
                _, exc, _ = sys.exc_info()
                self.msg("handler exception: %s" % str(exc))
                if self.verbose:
                    self.msg(traceback.format_exc())
        finally:
            if self.rec:
                self.rec.write("'EOF']\n")
                self.rec.close()

            if self.client and self.client != startsock:
                self.client.close()

    def new_client(self):
        """ Do something with a WebSockets client connection. """
        raise("WebSocketServer.new_client() must be overloaded")

    def start_server(self):
        """
        Daemonize if requested. Listen for for connections. Run
        do_handshake() method for each connection. If the connection
        is a WebSockets client then call new_client() method (which must
        be overridden) for each new client connection.
        """
        lsock = self.socket(self.listen_host, self.listen_port)

        self.started()  # Some things need to happen after daemonizing

        while True:
            try:
                try:
                    self.client = None
                    startsock = None
                    pid = err = 0

                    try:
                        self.poll()

                        ready = select.select([lsock], [], [], 1)[0]
                        if lsock in ready:
                            startsock, address = lsock.accept()
                        else:
                            continue
                    except Exception:
                        _, exc, _ = sys.exc_info()
                        if hasattr(exc, 'errno'):
                            err = exc.errno
                        elif hasattr(exc, 'args'):
                            err = exc.args[0]
                        else:
                            err = exc[0]
                        if err == errno.EINTR:
                            self.vmsg("Ignoring interrupted syscall")
                            continue
                        else:
                            raise

                    if Process:
                        self.vmsg('%s: new handler Process' % address[0])
                        p = Process(target=self.top_new_client,
                                args=(startsock, address))
                        p.start()
                        # child will not return
                    else:
                        # python 2.4
                        self.vmsg('%s: forking handler' % address[0])
                        pid = os.fork()
                        if pid == 0:
                            # child handler process
                            self.top_new_client(startsock, address)
                            break  # child process exits

                    # parent process
                    self.handler_id += 1

                except KeyboardInterrupt:
                    _, exc, _ = sys.exc_info()
                    print("In KeyboardInterrupt")
                    pass
                except SystemExit:
                    _, exc, _ = sys.exc_info()
                    print("In SystemExit")
                    break
                except Exception:
                    _, exc, _ = sys.exc_info()
                    self.msg("handler exception: %s" % str(exc))
                    if self.verbose:
                        self.msg(traceback.format_exc())

            finally:
                if startsock:
                    startsock.close()

    ## THREAD COMPLIANCE
    def run(self):
        self.start_server()


# HTTP handler with WebSocket upgrade support
class WSRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, req, addr, only_upgrade=False):
        self.only_upgrade = only_upgrade # only allow upgrades
        SimpleHTTPRequestHandler.__init__(self, req, addr, object())

    def do_GET(self):
        if (self.headers.get('upgrade') and
                self.headers.get('upgrade').lower() == 'websocket'):

            if (self.headers.get('sec-websocket-key1') or
                    self.headers.get('websocket-key1')):
                # For Hixie-76 read out the key hash
                self.headers.__setitem__('key3', self.rfile.read(8))

            # Just indicate that an WebSocket upgrade is needed
            self.last_code = 101
            self.last_message = "101 Switching Protocols"
        elif self.only_upgrade:
            # Normal web request responses are disabled
            self.last_code = 405
            self.last_message = "405 Method Not Allowed"
        else:
            SimpleHTTPRequestHandler.do_GET(self)

    def send_response(self, code, message=None):
        # Save the status code
        self.last_code = code
        SimpleHTTPRequestHandler.send_response(self, code, message)

    def log_message(self, f, *args):
        # Save instead of printing
        self.last_message = f % args





# '''
# A WebSocket to TCP socket proxy with support for "wss://" encryption.
# Copyright 2010 Joel Martin
# Licensed under LGPL version 3 (see docs/LICENSE.LGPL-3)
#
# You can make a cert/key with openssl using:
# openssl req -new -x509 -days 365 -nodes -out self.pem -keyout self.pem
# as taken from http://docs.python.org/dev/library/ssl.html#certificates
#
# '''
#
# class WebSocketProxy(WebSocketServer):
#     """
#     Proxy traffic to and from a WebSockets client to a normal TCP
#     socket server target. All traffic to/from the client is base64
#     encoded/decoded to allow binary data to be sent/received to/from
#     the target.
#     """
#
#     buffer_size = 65536
#
#     traffic_legend = """
# Traffic Legend:
#     }  - Client receive
#     }. - Client receive partial
#     {  - Target receive
#
#     >  - Target send
#     >. - Target send partial
#     <  - Client send
#     <. - Client send partial
# """
#
#     def __init__(self, *args, **kwargs):
#         # Save off proxy specific options
#         self.target_host   = kwargs.pop('target_host')
#         self.target_port   = kwargs.pop('target_port')
#         self.wrap_cmd      = kwargs.pop('wrap_cmd')
#         self.wrap_mode     = kwargs.pop('wrap_mode')
#         # Last 3 timestamps command was run
#         self.wrap_times    = [0, 0, 0]
#
#         if self.wrap_cmd:
#             rebinder_path = ['./', os.path.dirname(sys.argv[0])]
#             self.rebinder = None
#
#             for rdir in rebinder_path:
#                 rpath = os.path.join(rdir, "rebind.so")
#                 if os.path.exists(rpath):
#                     self.rebinder = rpath
#                     break
#
#             if not self.rebinder:
#                 raise Exception("rebind.so not found, perhaps you need to run make")
#
#             self.target_host = "127.0.0.1"  # Loopback
#             # Find a free high port
#             sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             sock.bind(('', 0))
#             self.target_port = sock.getsockname()[1]
#             sock.close()
#
#             os.environ.update({
#                 "LD_PRELOAD": self.rebinder,
#                 "REBIND_OLD_PORT": str(kwargs['listen_port']),
#                 "REBIND_NEW_PORT": str(self.target_port)})
#
#         WebSocketServer.__init__(self, *args, **kwargs)
#
#     def run_wrap_cmd(self):
#         self.wrap_times.append(time.time())
#         self.wrap_times.pop(0)
#         self.cmd = subprocess.Popen(
#                 self.wrap_cmd, env=os.environ)
#         self.spawn_message = True
#
#     def started(self):
#         """
#         Called after Websockets server startup (i.e. after daemonize)
#         """
#         # Need to call wrapped command after daemonization so we can
#         # know when the wrapped command exits
#         if self.wrap_cmd:
#             self.run_wrap_cmd()
#
#     def poll(self):
#         # If we are wrapping a command, check it's status
#
#         if self.wrap_cmd and self.cmd:
#             ret = self.cmd.poll()
#             if ret != None:
#                 self.vmsg("Wrapped command exited (or daemon). Returned %s" % ret)
#                 self.cmd = None
#
#         if self.wrap_cmd and self.cmd == None:
#             # Response to wrapped command being gone
#             if self.wrap_mode == "ignore":
#                 pass
#             elif self.wrap_mode == "exit":
#                 sys.exit(ret)
#             elif self.wrap_mode == "respawn":
#                 now = time.time()
#                 avg = sum(self.wrap_times)/len(self.wrap_times)
#                 if (now - avg) < 10:
#                     # 3 times in the last 10 seconds
#                     if self.spawn_message:
#                         self.spawn_message = False
#                 else:
#                     self.run_wrap_cmd()
#
#     #
#     # Routines above this point are run in the master listener
#     # process.
#     #
#
#     #
#     # Routines below this point are connection handler routines and
#     # will be run in a separate forked process for each connection.
#     #
#
#     def new_client(self):
#         """
#         Called after a new WebSocket connection has been established.
#         """
#         # Connect to the target
#         tsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         tsock.connect((self.target_host, self.target_port))
#
#         # Start proxying
#         try:
#             self.do_proxy(tsock)
#         except:
#             if tsock:
#                 tsock.close()
#                 self.vmsg("%s:%s: Target closed" %(
#                     self.target_host, self.target_port))
#             raise
#
#     def do_proxy(self, target):
#         """
#         Proxy client WebSocket to normal target socket.
#         """
#         cqueue = []
#         c_pend = 0
#         tqueue = []
#         rlist = [self.client, target]
#         tstart = int(time.time()*1000)
#
#         while True:
#             wlist = []
#             tdelta = int(time.time()*1000) - tstart
#
#             if tqueue: wlist.append(target)
#             if cqueue or c_pend: wlist.append(self.client)
#             ins, outs, excepts = select.select(rlist, wlist, [], 1)
#             if excepts: raise Exception("Socket exception")
#
#             if target in outs:
#                 # Send queued client data to the target
#                 dat = tqueue.pop(0)
#                 sent = target.send(dat)
#                 if sent == len(dat):
#                     self.traffic(">")
#                 else:
#                     # requeue the remaining data
#                     tqueue.insert(0, dat[sent:])
#                     self.traffic(".>")
#
#             if target in ins:
#                 # Receive target data, encode it and queue for client
#                 buf = target.recv(self.buffer_size)
#                 if len(buf) == 0: raise self.EClose("Target closed")
#
#                 cqueue.append(buf)
#                 self.traffic("{")
#
#
#             if self.client in outs:
#                 # Send queued target data to the client
#                 c_pend = self.send_frames(cqueue)
#                 cqueue = []
#
#             if self.client in ins:
#                 # Receive client data, decode it, and queue for target
#                 bufs, closed = self.recv_frames()
#                 tqueue.extend(bufs)
#
#                 if closed:
#                     # TODO: What about blocking on client socket?
#                     self.send_close()
#                     raise self.EClose(closed)