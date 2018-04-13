## A Simple GPIO Stepper Controller Module
Currently works with [Allegro A4988 Carriers](https://www.pololu.com/product/1182).

#### Dependencies
Python 3

RPi.GPIO


#### Usage
First, install RPi.GPIO

`pip3 install RPi.GPIO`

Install the module
```
git clone https://github.com/rochester-rcl/rcl-gpio-stepper-controller.git
cd rcl-gpio-stepper-controller/stepper_controller
python3 setup.py sdist && pip3 install -e .
```

Basic usage
```python
from stepper_controller.allegro_controller.controls import AllegroControls
import time

controls = AllegroControls()
controls.microstep(AllegroControls.MICROSTEP_SIXTEENTH)
controls.motor_setup()
# take 100 steps at 1/16 microstep resolution and shut down
for step in range(0, 100):
    time.sleep(0.004)
    controls.motor_forward()
controls.disable()
controls.close()
```
