# CameraAudioKeyboard
Серверная часть на Python3 и прошивка на Arduino для управления ip-камерой, используя аудио-вход. Подробное описание в Гугл-доке
## Зависимости Python
1. Фреймворк [Twisted](https://twistedmatrix.com/trac/) для работы с сетью (TCP и UDP). `pip3 install Twisted`
2. ONVIF-клиент для Python 3 [python-onvif-zeep](https://github.com/FalkTannhaeuser/python-onvif-zeep) `pip3 install --upgrade onvif_zeep`
3. [NumPy](http://www.numpy.org/) `pip3 install numpy`

## Зависимости Arduino
1. [Keypad](http://playground.arduino.cc/Code/Keypad) для считывания нажатых клавиш.
2. [Tone](https://github.com/bhagman/Tone) для генерации сигналов на двух пинах платы

## Запуск
В файле **CameraAudioKeyboard.py** изменить параметры подключения к камере `config`.
Открыть терминал/командную строку в директории с этими файлами и запустить:
```
python3 CameraAudioKeyboard.py
```
