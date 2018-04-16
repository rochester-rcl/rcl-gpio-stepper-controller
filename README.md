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
This will install 2 modules: allegro_controller and default_stepper. The documentation can be found [here](https://rochester-rcl.github.io/rcl-gpio-stepper-controller/build/html/stepper_controller.html)

Basic usage
```python
from allegro_controller.controller import AllegroControls
import time

controls = AllegroControls()
controls.microstep(AllegroControls.MICROSTEP_FULL)
controls.motor_setup(True)
for step in range(0, 100):
   time.sleep(0.004)
   controls.step()
controls.disable()
controls.close()
```
