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

connector = reactor.connectTCP(config['ip'], config['port'], rtsp_client.RTSPFactory(config, debug=True))
try:
    reactor.run()
except KeyboardInterrupt:
    connector.disconnect()
    reactor.stop()
