from time import sleep
from onvif import ONVIFCamera
exec(open("./fix_zeep.py").read())

class Camera(object):
    
    def __init__(self, ip, login, password, port = 80):
        # Подключение
        self.mycam = ONVIFCamera(ip, port, login, password)

        # Создание сервиса для управления движением
        self.ptz = self.mycam.create_ptz_service()
        
        # Получение профиля, в котором содержатся необходимые токены
        # (Понадобятся в запросах)
        media = self.mycam.create_media_service()
        self.media_profile = media.GetProfiles()[0]
        
        self._initContinuousMove()
        
    def _initContinuousMove(self):
        # Для получения пределов движения по осям X и Y необходимо запросить параметры конфигурации сервиса PTZ
        request = self.ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = self.media_profile.PTZConfiguration.token
        self.ptz_configuration_options = self.ptz.GetConfigurationOptions(request)

        self.XMAX = self.ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
        self.XMIN = self.ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
        self.YMAX = self.ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
        self.YMIN = self.ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min

        # Для управления камерой необходимо создать запрос типа ContinuousMove
        self.request = self.ptz.create_type('ContinuousMove')
        self.request.ProfileToken = self.media_profile.token
        # Так как в созданном запросе атрибут Velosity = None, 
        # замещаем его объектом с аналогичной структурой
        self.request.Velocity = self.ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position
        self.request.Velocity.Zoom.x = 0.0

        self.ptz.Stop({'ProfileToken': self.media_profile.token})
    

    def stop(self):
         self.ptz.Stop({'ProfileToken': self.request.ProfileToken})
            
    def _perform_move(self, timeout):
        self.ptz.Stop({'ProfileToken': self.request.ProfileToken})
        # Start continuous move
        self.ptz.ContinuousMove(self.request)
        # Wait a certain time
        # sleep(timeout)
        # Stop continuous move
        # self.ptz.Stop({'ProfileToken': self.request.ProfileToken})
        
    def move_up(self, timeout=0):
        print('Moving UP')
        self.request.Velocity.PanTilt.x = 0
        self.request.Velocity.PanTilt.y = self.YMAX
        self._perform_move(timeout)

    def move_down(self, timeout=0):
        print('Moving DOWN')
        self.request.Velocity.PanTilt.x = 0
        self.request.Velocity.PanTilt.y = self.YMIN
        self._perform_move(timeout) 
    
    def move_right(self, timeout=0):
        print('Moving RIGHT')
        self.request.Velocity.PanTilt.x = self.XMAX
        self.request.Velocity.PanTilt.y = 0
        self._perform_move(timeout) 
    
    def move_left(self, timeout=0):
        print ('Moving LEFT')
        self.request.Velocity.PanTilt.x = self.XMIN
        self.request.Velocity.PanTilt.y = 0
        self._perform_move(timeout)