from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor
from rtp_audio_client import RTPAudioClient
from rtcp_client import RTCPClient


# Класс для установки соединения по протоколу RTSP
class RTSPClient(Protocol):
    
    def __init__(self, factory, config, debug=False):
        self.factory = factory
        self.config = config
        self.debug = debug
    
    ###### Twisted functions #######
    
    ## Отправка первого запроса после подключения
    def connectionMade(self):
        self.session = 1
        req = """OPTIONS rtsp://""" + self.config['ip'] + ':' + str(self.config['port']) + self.config['request_tail'] + """ RTSP/1.0\r
CSeq: 1\r
\r\n"""
        self.transport.write(req.encode())
        if self.debug:
            print("client -> server\n" + req)
        else:
            print("Connected to camera")
    
    ## Закрытие соединений
    def connectionLost(self, reason):
        if self.debug:
            print ("RTSP connection closed")
        try:
            self.rtcpport.stopListening()
            if self.debug:
                print("RTCP connection closed")
            self.rtpport.stopListening()
            if self.debug:
                print("RTP connection closed")
            else:
                print("Connection closed")
            reactor.stop()
        except:
            pass
    
    # Cоответствие типов запросов номерам CSeq
    requestSeqNums = {'1' : 'OPTIONS',
                   '2' : 'DESCRIBE',
                   '3' : 'SETUP',
                   '4' : 'PLAY'
                   }
    
    
    ## Обработка входяших данных (парсинг RSTP-ответа)
    def dataReceived(self, data):
        if self.debug:
            print("server -> client\n" + data.decode())
        response = data.decode().split('\r\n')
        code = response[0] # код ответа сервера
        cseq = response[1].split(': ')[1] # номер запроса, на который пришел ответ
        if code != 'RTSP/1.0 200 OK':
            print(self.requestSeqNums[cseq] + "request faild:" + code)
        else:
            #Обработка ответа и отправка следующего запроса
            if cseq == '1':
                self.sendDescribe()
            elif cseq == '2':
                self.parseDescribe(response)
                self.sendSetup()
            elif cseq == '3':
                self.parseSetup(response)
                #Установка соединения по RTP
                self.rtpport = reactor.listenUDP(self.config['udp_port'], RTPAudioClient(self.config, self.debug))
                #Установка соединения по RTCP
                self.rtcpport = reactor.listenUDP(self.config['udp_port']+1, RTCPClient(self.debug))
                self.sendPlay()
            

    #############################
    
    def sendDescribe(self):
        req = """DESCRIBE rtsp://""" + self.config['ip'] + ':' + str(self.config['port']) + self.config['request_tail'] + """ RTSP/1.0\r
CSeq:2\r
Accept: application/sdp\r
\r\n"""
        if self.debug:
            print("client -> server\n" + req)
        self.transport.write(req.encode())
        
    def parseDescribe(self, response):
        for line in range(len(response)):
            if response[line].startswith('m=audio') and response[line+1].startswith('a=control'):
                control = response[line+1].split(':', 1)[1].strip() #control: адрес_аудиопотока
                if control.startswith('rtsp://'):
                    self.audio_track = control
                elif control.startswith(self.config['ip']):
                    self.audio_track = 'rstp://' + control
                else:
                    self.audio_track = 'rtsp://'+self.config['ip']+':'+str(self.config['port'])+self.config['request_tail']+'/'+control
                
    def sendSetup(self):
        req = """SETUP """ + self.audio_track + """ RTSP/1.0\r
CSeq: 3\r
Transport: RTP/AVP;unicast;client_port=""" + str(self.config['udp_port']) + "-" + str(self.config['udp_port']+1) + """\r
\r\n"""
        if self.debug:
            print("client -> server\n" + req)
        self.transport.write(req.encode())
        
    def parseSetup(self, response):
        for line in response:
            if line.startswith('Session'):
                self.session = line.split(':')[1].strip()
            
    def sendPlay(self):
        req = """PLAY rtsp://""" + self.config['ip'] + ':' + str(self.config['port']) + self.config['request_tail'] + """ RTSP/1.0\r
CSeq: 4\r
Session: """ + self.session + """\r
Range: npt=0.000-\r
\r\n"""
        if self.debug:
            print("client -> server\n" + req)
        self.transport.write(req.encode())
        
class RTSPFactory(ClientFactory):
        
    def __init__(self, config, debug = False):
        self.prot = RTSPClient(self, config, debug)
    
    def buildProtocol(self, addr):
        return self.prot
    