# Run the circuit before you build it

[Wokwi](https://wokwi.com) is a free circuit simulator that runs in a browser. It
shows real pictures of the boards with coloured wires between the pins, you can
drag things around and pull wires yourself, and it runs the actual firmware.

You do not need an account to run it. You need one only if you want to save it.

## Getting it going — five steps

1. Go to **https://wokwi.com/projects/new/esp32-c3**
2. Click the **diagram.json** tab. Select everything that's there and delete it.
   Paste in the whole of `diagram.json` from this folder.
3. Click the **sketch.ino** tab. Same again — select all, delete, paste in
   `sketch.ino` from this folder.
4. Click **Library Manager**, then the **+** button, and add these three:
   `RTClib`, `Dusk2Dawn`, `ESP32Servo`.
5. Press the green **▶** play button. First build takes a minute or so.

## What you're looking at

| On screen | On the real board |
|---|---|
| The black ESP32-C3 stick | Your XIAO ESP32-C3 |
| The small blue board with the coin cell | The DS3231M clock |
| **Green LED** lit | The driver is running the motor **open** |
| **Red LED** lit | The driver is running the motor **shut** |
| The servo horn | Where the nest box door actually is |
| The knob | Battery voltage — the 220k / 33k divider |
| The two 10 kΩ resistors | The same two pull-downs, doing the same job |

The GPIO numbers are identical to the real build, so you can hold this next to
[the wiring diagram](https://h-ashrafi.github.io/nestbox-door/) and they match
pin for pin:

```
GPIO3 = XIAO D1 = driver IN1      GPIO6 = XIAO D4 = clock SDA
GPIO5 = XIAO D3 = driver IN2      GPIO7 = XIAO D5 = clock SCL
GPIO4 = XIAO D2 = battery sense
```

## Things to try

- **Just watch it.** One day passes every 30 seconds or so. The green LED flashes
  at dawn, the red one flashes mid-afternoon, and the servo swings between them.
  The serial window prints what it's doing and why, in plain English.
- **Turn the knob down.** Below 11.9 V the battery guard fires: it parks the
  boxes open and stops moving. That's the behaviour that stops a flat battery
  leaving your hens locked out.
- **Change `LAT` to `-12.46`** (Darwin) **and watch the window barely move** all
  year. Then try `-42.88` (Hobart) and watch it swing hard between seasons. That
  is the whole reason the controller works off sunrise rather than a clock time.
- **Pull a wire out** and see what breaks. Free, and it costs you nothing.

## What it can't tell you

The simulator proves the *logic*. It cannot catch a swapped VIN and VOUT on the
buck, a cold solder joint, or a pull-down on a strapping pin stopping the board
booting. Those are the failures that actually bite, and they're all physical —
which is what section 06 of the bench sheet, "build it in stages", is for.

There is no DRV8871 or linear actuator in Wokwi's parts library. That matters
less than it sounds: the driver is just *two pins going high and low*, and two
LEDs show that perfectly.
