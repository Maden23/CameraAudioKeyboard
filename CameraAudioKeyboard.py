#import socket
#
#ip = "192.168.15.43"
#
#def sendrequest(sock, request):
#    sock.send(request.encode())
#    data = sock.recv(1024)
#    print("server -> client")
#    print(data.decode())
#    
#requests = [
#    "DESCRIBE rtsp://" + ip + " RTSP/1.0\r\nCSeq: 1\\r\nAccept: application/sdp\r\n\r\n",
##    "SETUP rtsp://" + ip + "/trackID=2 RTSP/1.0\r\nCSeq: 2\r\nTransport: RTP/AVP;unicast;client_port=4321-4322\r\n\r\n",
##    "PLAY rtsp://" + ip + "/trackID=2 RTSP/1.0\r\nCSeq: 3\r\nSession: 865805256\r\nRange: npt=now-\r\n\r\n",
##    "TEARDOWN rtsp://" + ip + "/trackID=2 RTSP/1.0\r\nCSeq: 3\r\nSession: 275102146\r\n\r\n"
#]
#
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((ip, 554))
#
#for req in requests:
#    print("client -> server")
#    print(req)
#    sendrequest(s, req)
#
#s.close()


from twisted.internet import reactor
import rtsp_client

config = {
        'ip' : '192.168.15.43',
        'port' : 554,
        'onvif_port' : 80,
        'request_tail' : '', # Добавочная часть для управления камерой по RTSP
        'udp_port' : 47634,
        'login' : 'admin',
        'password' : 'Supervisor',
        'keys' : {
            ## Назначения команд клавишам 
            'up' : '5',
            'left' : '7',
            'right' : '9',
            'down' : '0',
            }
        }

connector = reactor.connectTCP(config['ip'], config['port'], rtsp_client.RTSPFactory(config, debug=False))
try:
    reactor.run()
except KeyboardInterrupt:
    connector.disconnect()
    reactor.stop()
