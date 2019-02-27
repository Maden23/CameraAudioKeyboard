from DTMFDetector import DTMFdetector
import numpy as np
from ptzcamera import Camera
import audioop
from time import time

class AudioAnalyzer():
   
    def __init__(self, config, debug=False):
        self.config = config
        self.debug = debug
        # Класс, реализующий взаимодействие с камерой
        self.camera = Camera(config['ip'], config['login'], config['password'], config['onvif_port'])        
        # Декодер DTMF-тона в значение на клавиатуре
        self.detector = DTMFdetector() 
        # Время, когда последний раз был получен звук
        self.last_sound_time = int(round(time() * 1000))

    ## Применяется для обработки потока байт в реальном времени
    def analyze(self, bytes_data):
        ## Отправка в декодер
        # Декомпрессия из формата u-LAW (PCMU)
        data = audioop.ulaw2lin(bytes_data, 2)
        samples = np.frombuffer(data, dtype = np.int16)
        for s in samples:
            self.detector.goertzel(s)
        # Результатом алгоритма декодирования является characters -- список 
        # пар значений (нажатая клавиша, время нажатия в секундах от запуска скрипта)
        if (self.detector.characters): 
            self.transformInput(self.detector.characters)
            self.last_sound_time = int(round(time() * 1000))

        # В случае, когда звука нет больше 100 мс, камера останавливается
        elapsed = int(round(time() * 1000)) - self.last_sound_time
        if elapsed > 100:
            self.camera.stop()
        self.detector.characters = []

    
    ## Преобразует список пар (клавиша, временной штамп) в словарь (команда:длительность)
    def transformInput(self, pressedKeysRecords):
        commands_durations = {}  # Словарь (команда:длительность)
        lastkey = ''
        lastkey_timestamp = 0
        for record in pressedKeysRecords: # (клавиша, временной штамп)
            # Если клавиша встретилась первый раз (ее нет в словаре),
            # то она добавляется с нулевой длительностью
            if commands_durations.get(record[0]) == None:
                commands_durations[record[0]] = 0
            # При повторении одного значения клавиши к длительности добавляется 
            # разность во времени, начальная длительность -- 1 мс
            if (record[0] == lastkey):
                commands_durations[record[0]] += record[1] - lastkey_timestamp
            else:
                commands_durations[record[0]] += 0.001
            lastkey = record[0]
            lastkey_timestamp = record[1]
            if self.debug:
                print("Command & duration: ", commands_durations)
        self.sendCommands(commands_durations)
        
    ## Отправляет полученные команды камере 
    def sendCommands(self, commands_durations):
        for command in commands_durations.keys():
            if command == self.config['keys']['up']:
                self.camera.move_up(commands_durations[command])
            elif command == self.config['keys']['left']:
                self.camera.move_left(commands_durations[command])
            elif command == self.config['keys']['right']:
                self.camera.move_right(commands_durations[command])
            elif command == self.config['keys']['down']:
                self.camera.move_down(commands_durations[command])
        
        