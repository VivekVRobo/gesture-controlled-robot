// Gesture Controlled Robot - serial motor receiver
// Validate these pins and motor directions on your hardware before floor testing.

const uint8_t LEFT_PWM = 5;
const uint8_t LEFT_IN1 = 7;
const uint8_t LEFT_IN2 = 8;
const uint8_t RIGHT_PWM = 6;
const uint8_t RIGHT_IN1 = 9;
const uint8_t RIGHT_IN2 = 10;

const uint8_t DRIVE_PWM = 150;
const uint8_t TURN_PWM = 130;
const unsigned long WATCHDOG_MS = 500;
unsigned long lastCommandMs = 0;

void motor(uint8_t pwm, uint8_t in1, uint8_t in2, int speedValue) {
  const bool forward = speedValue >= 0;
  digitalWrite(in1, forward ? HIGH : LOW);
  digitalWrite(in2, forward ? LOW : HIGH);
  analogWrite(pwm, constrain(abs(speedValue), 0, 255));
}

void drive(int left, int right) {
  motor(LEFT_PWM, LEFT_IN1, LEFT_IN2, left);
  motor(RIGHT_PWM, RIGHT_IN1, RIGHT_IN2, right);
}

void stopRobot() { drive(0, 0); }

bool applyCommand(char c) {
  switch (c) {
    case 'F': drive(DRIVE_PWM, DRIVE_PWM); break;
    case 'B': drive(-DRIVE_PWM, -DRIVE_PWM); break;
    case 'L': drive(-TURN_PWM, TURN_PWM); break;
    case 'R': drive(TURN_PWM, -TURN_PWM); break;
    case 'S': stopRobot(); break;
    default: return false;
  }
  return true;
}

void setup() {
  Serial.begin(115200);
  pinMode(LEFT_PWM, OUTPUT); pinMode(LEFT_IN1, OUTPUT); pinMode(LEFT_IN2, OUTPUT);
  pinMode(RIGHT_PWM, OUTPUT); pinMode(RIGHT_IN1, OUTPUT); pinMode(RIGHT_IN2, OUTPUT);
  stopRobot();
  lastCommandMs = millis();
}

void loop() {
  while (Serial.available()) {
    const char c = Serial.read();
    if (applyCommand(c)) lastCommandMs = millis();
  }

  if (millis() - lastCommandMs > WATCHDOG_MS) {
    stopRobot();
  }
}
