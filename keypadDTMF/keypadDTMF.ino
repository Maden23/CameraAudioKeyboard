
#include "Tone.h"
#include "Keypad.h"

const byte rows = 4;
const byte cols = 4;

char keys[rows][cols] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'#','0','*','D'}
};


byte rowPins[rows] = {9,8,7,6};
byte colPins[cols] = {5,4,3,2};

Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, rows, cols);

// Частота тонов для клавиш (в порядке по рядам слева направо)
int DTMF[rows*cols][2]={
  {697,1209}, // 1
  {697,1336}, // 2
  {697,1477}, // 3
  {697,1633}, // A
  {770,1209}, // 4
  {770,1336}, // 5
  {770,1477}, // 6
  {770,1633}, // B
  {852,1209}, // 7
  {852,1336}, // 8
  {852,1477}, // 9
  {852,1633}, // C
  {941,1209}, // *
  {941,1336}, // 0
  {941,1477}, // #
  {941,1633}  // D
};

Tone freq1;
Tone freq2;
int freq1Pin = 12;
int freq2Pin = 13;

void getFrequencies(char key, int frequencies[])
{
  // Нахождение порядкового номера клавиши, если считать по рядам слева направо
  int num = -1;
  for (int i = 0; i < rows; i++)
  {
    for (int j = 0; j < cols; j++)
    {
      if (keys[i][j] == key)
      {
        num = i*4+j;
      }
    }
  } 

  // DTMF-частоты лежат по найденному индексу 
  if (num == -1)
  {
    frequencies[0] = 0;
    frequencies[1] = 0;   
    Serial.println("Unknown DTMF key"); 
  }
  else
  {
    frequencies[0] = DTMF[num][0];   
    frequencies[1] = DTMF[num][1];  
  }
}

void playDTMF(char key, long duration) {
  int freqs[2];
  getFrequencies(key, freqs);
  Serial.println("Playing f1 = " + String(freqs[0]) + " f2 =  " + String(freqs[1]));
  freq1.play(freqs[0], duration);
  freq2.play(freqs[1], duration);
}

void setup() {
  freq1.begin(freq1Pin);
  freq2.begin(freq2Pin);
  Serial.begin(9600);
//  playDTMF('5', 100000000000000000000000000000000);

}

char key;
char holdKey;
unsigned long t_hold;
void loop() {
  char list[4] = {'1', '2', '3', '4'};
  for (key : list)
  {
    playDTMF(key, 300);
    delay(500);
  }
//  key = keypad.getKey();
//
//  if (key != NO_KEY) 
//  {
//    holdKey = key;
//    Serial.println(key);
//  }
//  
//  if (keypad.getState() == HOLD)
//  {
//    if ((millis() - t_hold) > 100)
//    {
//      Serial.println(holdKey);
//      playDTMF(holdKey, (millis() - t_hold));
//      t_hold = millis();
//    }
//  }
//  else if (key != NO_KEY)
//  {
//      playDTMF(key, 100);
//  }
  
}
