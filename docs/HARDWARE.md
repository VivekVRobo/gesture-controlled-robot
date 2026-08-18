# Hardware Integration

## Reference hardware

- USB-connected Arduino Uno/Nano-compatible board
- Dual H-bridge motor driver
- Two geared DC motors
- Separate motor battery/supply
- USB webcam on the host computer

## Default firmware pins

| Function | Pin |
|---|---:|
| Left PWM | 5 |
| Left IN1 | 7 |
| Left IN2 | 8 |
| Right PWM | 6 |
| Right IN1 | 9 |
| Right IN2 | 10 |

## Bring-up

1. Power motors from a suitable motor supply, not the Arduino 5 V pin.
2. Share ground between Arduino and motor driver.
3. Lift wheels off the floor.
4. Send `S`, `F`, `B`, `L`, `R` manually from a serial terminal and verify direction.
5. Disconnect the host serial stream and confirm the robot stops within roughly 500 ms.
6. Only then enable the webcam controller.

If left/right or forward/reverse is inverted, correct wiring or pin/direction mapping rather than compensating with confusing gesture labels.
