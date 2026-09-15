// ── NEST BOX DOOR — SIMULATOR VERSION ───────────────────────────────
// This is the real controller logic with four swaps, so you can SEE it run:
//
//   real DS3231M clock   ->  Wokwi's DS1307   (same I2C address; one word changes)
//   real DRV8871 driver  ->  two LEDs         (they show exactly what IN1/IN2 do)
//   real linear actuator ->  a servo          (so you can watch the door move)
//   real deep sleep      ->  a fast clock     (one whole day every ~30 seconds)
//
// The sunrise maths, the schedule and the battery guard are the same code
// that goes on the real board. The pin numbers are the same GPIOs too:
//   GPIO3 = XIAO D1 = IN1      GPIO5 = XIAO D3 = IN2
//   GPIO4 = XIAO D2 = battery sense
//   GPIO6 = XIAO D4 = SDA      GPIO7 = XIAO D5 = SCL

#include <Wire.h>
#include <RTClib.h>
#include <Dusk2Dawn.h>
#include <ESP32Servo.h>

const float LAT = -37.8136;     // your latitude  (south = negative)
const float LON = 144.9631;     // your longitude (east  = positive)
const float TZ  = 10.0;         // STANDARD time offset. Never change for daylight saving.

const int OPEN_BEFORE_SUNRISE_MIN = 30;    // boxes open 30 min before sunrise
const int CLOSE_BEFORE_SUNSET_MIN = 150;   // boxes shut 2.5 h before sunset
const float VBAT_CUTOFF = 11.9;            // volts: below this, stop moving

const int PIN_IN1 = 3, PIN_IN2 = 5, PIN_VBAT = 4, PIN_SERVO = 10;

const int MIN_PER_TICK = 6;     // simulated minutes per loop
const int TICK_MS      = 120;   // real milliseconds per loop

RTC_DS1307 rtc;                 // real build: RTC_DS3231 rtc;
Dusk2Dawn here(LAT, LON, TZ);
Servo panel;

DateTime clk;
int lastState = -1;

// The knob stands in for the 220k / 33k divider on the real board.
float batteryVolts() {
  return 10.5 + (analogRead(PIN_VBAT) / 4095.0) * 3.5;   // 10.5 V .. 14.0 V
}

void driveMotor(bool opening) {
  digitalWrite(PIN_IN1, opening ? HIGH : LOW);
  digitalWrite(PIN_IN2, opening ? LOW  : HIGH);
  panel.write(opening ? 90 : 0);
  delay(700);                    // stands in for the actuator's 55 second stroke
  digitalWrite(PIN_IN1, LOW);    // both low = driver coasts, LEDs go out
  digitalWrite(PIN_IN2, LOW);
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_IN1, OUTPUT);
  pinMode(PIN_IN2, OUTPUT);
  digitalWrite(PIN_IN1, LOW);
  digitalWrite(PIN_IN2, LOW);
  panel.attach(PIN_SERVO, 500, 2400);
  panel.write(0);

  Wire.begin(6, 7);
  if (!rtc.begin()) { Serial.println("No clock found - check SDA and SCL."); while (1) delay(10); }
  clk = DateTime(2026, 9, 15, 0, 0, 0);

  Serial.println();
  Serial.println("NEST BOX DOOR - simulator");
  Serial.println("-------------------------------------------------------------");
  Serial.println("green LED  the driver is running the motor OPEN");
  Serial.println("red LED    the driver is running the motor SHUT");
  Serial.println("servo      where the door actually is");
  Serial.println("the knob   battery volts - turn it down past 11.9 V to see");
  Serial.println("           the guard park the boxes open and give up");
  Serial.println();
  Serial.println("One whole day passes every 30 seconds or so.");
  Serial.println("-------------------------------------------------------------");
  Serial.println();
}

void loop() {
  clk = clk + TimeSpan(0, 0, MIN_PER_TICK, 0);
  int minuteOfDay = clk.hour() * 60 + clk.minute();

  int sunrise = here.sunrise(clk.year(), clk.month(), clk.day(), false);
  int sunset  = here.sunset (clk.year(), clk.month(), clk.day(), false);
  int openAt  = sunrise - OPEN_BEFORE_SUNRISE_MIN;
  int closeAt = sunset  - CLOSE_BEFORE_SUNSET_MIN;

  float vbat = batteryVolts();
  int want = (minuteOfDay >= openAt && minuteOfDay < closeAt) ? 1 : 0;

  if (vbat < VBAT_CUTOFF) {
    if (lastState != 1) {
      Serial.printf("%02d:%02d  battery %.1f V - too flat. Parking the boxes OPEN and stopping.\n",
                    clk.hour(), clk.minute(), vbat);
      driveMotor(true);
      lastState = 1;
    }
  } else if (want != lastState) {
    Serial.printf("%02d:%02d  %s\n", clk.hour(), clk.minute(),
      want ? "OPENING  - hens can get in to lay" : "SHUTTING - before they pick a roost");
    Serial.printf("        sunrise %02d:%02d, sunset %02d:%02d, battery %.1f V\n",
      sunrise / 60, sunrise % 60, sunset / 60, sunset % 60, vbat);
    driveMotor(want == 1);
    lastState = want;
  }

  if (clk.minute() < MIN_PER_TICK && clk.hour() % 6 == 0) {
    Serial.printf("%02d:%02d  %s\n", clk.hour(), clk.minute(),
                  lastState == 1 ? "boxes open" : "boxes shut");
  }

  delay(TICK_MS);
}
