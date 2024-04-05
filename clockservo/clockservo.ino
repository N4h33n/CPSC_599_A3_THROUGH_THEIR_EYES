#include <Servo.h>
#define W_LED 3
#define Y_LED 5
#define R_LED 6
#define B_LED 9


Servo sunservo;
Servo moonservo;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  sunservo.attach(11);
  moonservo.attach(10);
  pinMode(W_LED, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  int val;

  if (Serial.available() > 0) {
    String inputString = Serial.readStringUntil('\n');
    // two positions, first for sun servo second for moon servo
    int delimPos = inputString.indexOf(',');
    if (delimPos != -1) {
      String sunstr = inputString.substring(0, delimPos);
      String moonstr = inputString.substring(delimPos + 1);

    float sunPos = sunstr.toFloat();
    float moonPos = moonstr.toFloat();
      if (sunPos >= 0 && sunPos <= 180 && moonPos >= 0 && moonPos <= 180) {
      Serial.println(sunPos);
      Serial.println(moonPos);
      sunservo.write(sunPos); 
      moonservo.write(moonPos); 
    }

      // Red LED for the first portion
        if (sunPos >= 0 && sunPos < 30) {
          analogWrite(R_LED, map(sunPos, 0, 30, 20, 255)); // Dim to Bright
          digitalWrite(Y_LED, LOW);
          digitalWrite(W_LED, LOW);
          digitalWrite(B_LED, LOW);
        }
        // Yellow LED for the second portion
        else if (sunPos >= 30 && sunPos < 60) {
          digitalWrite(R_LED, LOW);
          analogWrite(Y_LED, map(sunPos, 30, 60, 20, 255)); // Dim to Bright
          digitalWrite(W_LED, LOW);
          digitalWrite(B_LED, LOW);
        }
        // White LED at the center portion
        else if (sunPos >= 60 && sunPos < 90) {
          digitalWrite(R_LED, LOW);
          digitalWrite(Y_LED, LOW);
          analogWrite(W_LED, map(sunPos, 60, 90, 20, 255)); // Dim to Bright
          digitalWrite(B_LED, LOW);
        }
        // White LED at the center portion part 2
        else if (sunPos >= 90 && sunPos < 120) {
          digitalWrite(R_LED, LOW);
          digitalWrite(Y_LED, LOW);
          analogWrite(W_LED, map(sunPos, 90, 120, 255, 20)); // Bright to Dim
          digitalWrite(B_LED, LOW);
        }  
        // Yellow LED part 2
        else if (sunPos >= 120 && sunPos < 150) {
          digitalWrite(R_LED, LOW);
          analogWrite(Y_LED, map(sunPos, 120, 150, 255, 20)); // Bright to Dim
          digitalWrite(W_LED, LOW);
          digitalWrite(B_LED, LOW);
        }
        // Red LED for the last day portion
        else if (sunPos >= 150 && sunPos < 180) {
          analogWrite(R_LED, map(sunPos, 150, 180, 255, 20)); // Bright to Dim
          digitalWrite(Y_LED, LOW);
          digitalWrite(W_LED, LOW);
          digitalWrite(B_LED, LOW);
        }
        // Blue LED for night time
        else {
          digitalWrite(R_LED, LOW);
          digitalWrite(Y_LED, LOW);
          digitalWrite(W_LED, LOW);
          digitalWrite(B_LED, HIGH);
        }
    }
  }
  delay(10);
}
