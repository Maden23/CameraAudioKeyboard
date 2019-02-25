from twisted.internet.protocol import DatagramProtocol
from audio_analyzer import AudioAnalyzer
from struct import unpack


class RTPAudioClient(DatagramProtocol):
    
    def __init__(self, config, debug=False):
        ### Класс, отправляющий аудио в DTMF-декодер и команды камере
        self.analyzer = AudioAnalyzer(config, debug)

    def startProtocol(self):
        print("Started receiving audio data")
                
    ### Обработка полученных по RTP данных 
    def datagramReceived(self, datagram, address):
        self.Datagram = datagram
        self.parse()
        # Передача полученных аудио-данных анализатору
        self.analyzer.analyze(self.Payload)
                
    ### Парсинг RTP-пакета. Взято с https://habr.com/ru/post/117735/
    def parse(self):        
        Ver_P_X_CC, M_PT, self.SequenceNumber, self.Timestamp, self.SyncSourceIdentifier = unpack('!BBHII', self.Datagram[:12])
        self.Version =      (Ver_P_X_CC & 0b11000000) >> 6
        self.Padding =      (Ver_P_X_CC & 0b00100000) >> 5
        self.Extension =    (Ver_P_X_CC & 0b00010000) >> 4
        self.CSRCCount =     Ver_P_X_CC & 0b00001111
        self.Marker =       (M_PT & 0b10000000) >> 7
        self.PayloadType =   M_PT & 0b01111111
        i = 0
        for i in range(0, self.CSRCCount, 4):
            self.CSRS.append(unpack('!I', self.Datagram[12+i:16+i]))
        if self.Extension:
            i = self.CSRCCount * 4
            (self.ExtensionHeaderID, self.ExtensionHeaderLength) = unpack('!HH', self.Datagram[12+i:16+i])
            self.ExtensionHeader = self.Datagram[16+i:16+i+self.ExtensionHeaderLength]
            i += 4 + self.ExtensionHeaderLength
        self.Payload = self.Datagram[12+i:]