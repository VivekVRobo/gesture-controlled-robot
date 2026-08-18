// Gesture-controlled differential-drive robot receiver.
// Adjust pins and motor polarity for your hardware.

const int L_PWM = 5, L_IN1 = 7, L_IN2 = 8;
const int R_PWM = 6, R_IN1 = 9, R_IN2 = 10;
const int SPEED = 150;
const unsigned long WATCHDOG_MS = 500;
unsigned long lastCommandAt = 0;

void motor(int pwm, int in1, int in2, int speed) {
  speed = constrain(speed, -255, 255);
  digitalWrite(in1, speed >= 0 ? HIGH : LOW);
  digitalWrite(in2, speed >= 0 ? LOW : HIGH);
  analogWrite(pwm, abs(speed));
}

void drive(int left, int right) {
  motor(L_PWM, L_IN1, L_IN2, left);
  motor(R_PWM, R_IN1, R_IN2, right);
}

void stopRobot() { drive(0, 0); }

void setup() {
  pinMode(L_PWM, OUTPUT); pinMode(L_IN1, OUTPUT); pinMode(L_IN2, OUTPUT);
  pinMode(R_PWM, OUTPUT); pinMode(R_IN1, OUTPUT); pinMode(R_IN2, OUTPUT);
  Serial.begin(115200);
  stopRobot();
  lastCommandAt = millis();
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') return;
    lastCommandAt = millis();
    switch (c) {
      case 'F': drive(SPEED, SPEED); break;
      case 'B': drive(-SPEED, -SPEED); break;
      case 'L': drive(-SPEED, SPEED); break;
      case 'R': drive(SPEED, -SPEED); break;
      default: stopRobot(); break;
    }
  }

  if (millis() - lastCommandAt > WATCHDOG_MS) {
    stopRobot();
  }
}
