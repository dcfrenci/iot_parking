#include <Servo.h>

// SERVO
Servo Servo1;
Servo Servo2;
const int servoPin1 = 9;
const int servoPin2 = 10;
const int openAngle = 90;
const int closeAngle = 180;

// LED
const int ledPin1 = 2;
const int ledPin2 = 4;

// SENSOR
const int trigPin = 12;
const int echoPin = 13;
float duration, distance;
bool precedingState = false;
int stabilityCounter = 0;
unsigned long lastSensorTime = 0; 

// TIMER HANDLER
unsigned long timerGate1 = 0;
unsigned long timerGate2 = 0;
bool openedGate1 = false;
bool openedGate2 = false;


void setup() {

  // SERVO setup
  Servo1.attach(servoPin1);
  Servo2.attach(servoPin2);

  // LED setup
  pinMode(ledPin1, OUTPUT);
  pinMode(ledPin2, OUTPUT);

  // SENSOR setup
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // SERIAL setup
  Serial.begin(9600);

  Servo1.write(closeAngle);
  Servo2.write(closeAngle);
  digitalWrite(ledPin1, LOW);
  digitalWrite(ledPin2, LOW);
}

void loop() {

  if (millis() - lastSensorTime >= 60) {
    lastSensorTime = millis();

    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    duration = pulseIn(echoPin, HIGH, 30000);
    
    if (duration == 0) {
      distance = 999;
    } else {
      distance = duration * 0.034 / 2;
    }

    bool actualState = (distance > 0 && distance < 10);

    if (actualState == precedingState) {
      stabilityCounter = 0;
    } else {
      stabilityCounter++;
      
      if (stabilityCounter >= 5) {
        precedingState = actualState;
        stabilityCounter = 0;
        
        if (precedingState) {
          Serial.println("DS:1");
        } else {
          Serial.println("DS:0");
        }
      }
    }
  }

  // SERIAL
  while(Serial.available() > 0){
    String input = Serial.readStringUntil('\n');
    input.trim();
    input.toLowerCase();
    
    if(input == "o1"){
      Servo1.write(openAngle);
      digitalWrite(ledPin1, HIGH);
      
      openedGate1 = true;
      timerGate1 = millis();
    }
    
    if(input == "o2"){
      Servo2.write(openAngle);
      digitalWrite(ledPin2, HIGH);

      openedGate2 = true;
      timerGate2 = millis();
    }
  }

  // CLOSING GATE AFTER 5000ms
  if (openedGate1 && (millis() - timerGate1 >= 5000)) {
    Servo1.write(closeAngle);
    digitalWrite(ledPin1, LOW);
    openedGate1 = false;
  }

  if (openedGate2 && (millis() - timerGate2 >= 5000)) {
    Servo2.write(closeAngle);
    digitalWrite(ledPin2, LOW);
    openedGate2 = false;
  }

}