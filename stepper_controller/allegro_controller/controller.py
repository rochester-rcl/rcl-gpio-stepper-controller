import RPi.GPIO as GPIO
from threading import Thread
from enum import Enum
import time
from stepper_controller.default_stepper.defaults import DefaultStepperPins


class AllegroControls:
    """
    A class to control an Allegro stepper driver carrier like the `Pololu A4988 <https://www.pololu.com/product/1182>`_
    """

    def __init__(self, **kwargs):
        """
        :param kwargs: 
        :Keyword Arguments:
            stepper (``dict``) --
                Optionally pass in a dict to override the default GPIO pins found in `DefaultStepperPins.default_allegro 
                <stepper_controller.default_stepper.html#module-stepper_controller.default_stepper.defaults>`_
                You can replace any / all of the following keys:
                dir | step | enable | vdd | microstep - ms1 | ms2 | ms3 
        """
        if 'stepper' in kwargs:
            self.stepper = {**kwargs['stepper'], **DefaultStepperPins.default_allegro}
        else:
            self.stepper = DefaultStepperPins.default_allegro

        self.mode = GPIO.setmode(GPIO.BCM)
        self.motor_stopped = False
        self.paused = False

        # dir pin high is ccw

        for key, pin in self.stepper.items():
            if key is 'microstep':
                for microstep_pin, value in pin.items():
                    GPIO.setup(value, GPIO.OUT)
                    GPIO.output(value, GPIO.LOW)
            else:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)

        # stop motors w/ enable pins
        GPIO.output(self.stepper['enable'], GPIO.HIGH)

    def _set_microstep_resolution(self, pins, pin_modes):

        set_microstep = lambda pin, pin_mode: GPIO.output(pin, pin_mode)
        for pin, mode in zip(pins, pin_modes):
            print(pin, mode)
            set_microstep(pin[1], mode)

    def microstep(self, resolution):
        """
        :param resolution (``str``): The resolution of each step - options are FULL, HALF, QUARTER, EIGHTH, and SIXTEENTH 
        """
        # available resolutions - FULL, HALF, QUARTER, EIGHTH, SIXTEENTH

        if resolution is 'full':  # LOW LOW LOW
            pin_mode = [GPIO.LOW, GPIO.LOW, GPIO.LOW]
            self._set_microstep_resolution(self.right_stepper['microstep'].items(), pin_mode)
            self._set_microstep_resolution(self.left_stepper['microstep'].items(), pin_mode)
        if resolution is 'half':  # HIGH LOW LOW
            pin_mode = (GPIO.HIGH, GPIO.LOW, GPIO.LOW)
            self._set_microstep_resolution(self.right_stepper['microstep'].items(), pin_mode)
            self._set_microstep_resolution(self.left_stepper['microstep'].items(), pin_mode)
        if resolution is 'quarter':  # LOW HIGH LOW
            pin_mode = (GPIO.LOW, GPIO.HIGH, GPIO.LOW)
            self._set_microstep_resolution(self.right_stepper['microstep'].items(), pin_mode)
            self._set_microstep_resolution(self.left_stepper['microstep'].items(), pin_mode)
        if resolution is 'eighth':  # HIGH HIGH LOW
            pin_mode = (GPIO.HIGH, GPIO.HIGH, GPIO.LOW)
            self.set_microstep_resolution(self.right_stepper['microstep'].items(), pin_mode)
            self.set_microstep_resolution(self.left_stepper['microstep'].items(), pin_mode)
        if resolution is 'sixteenth':
            pin_mode = (GPIO.HIGH, GPIO.HIGH, GPIO.HIGH)
            self._set_microstep_resolution(self.right_stepper['microstep'].items(), pin_mode)
            self._set_microstep_resolution(self.left_stepper['microstep'].items(), pin_mode)

    def motor_setup(self):
        """
        Sets up the motor (sets the direction and enable pins to LOW)
        """
        # move right stepper counter clockwise
        GPIO.output(self.stepper['dir'], GPIO.LOW)
        GPIO.output(self.stepper['enable'], GPIO.LOW)

    def motor_forward(self):
        """
        Moves the motor forward in a separate thread  
        """
        Thread(target=self._forward, args=()).start()

    def _forward(self):
        GPIO.output(self.stepper['step'], GPIO.HIGH)
        GPIO.output(self.stepper['step'], GPIO.LOW)

        if self.motor_stopped:
            self.motor_shutdown()

        if self.paused:
            self.pause()

    def pause(self):
        """
        Pauses the motor's movement
        """
        GPIO.output(self.stepper['step'], GPIO.LOW)

    def _motor_shutdown(self):
        GPIO.output(self.stepper['enable'], GPIO.HIGH)
        for key, pin in self.stepper.items():
            if key is 'microstep':
                for microstep_pin, value in pin.items():
                    GPIO.output(value, GPIO.LOW)
            else:
                GPIO.output(pin, GPIO.LOW)

    def close(self):
        """
        Shuts down the motor and cleans up GPIO pins 
        """
        self._motor_shutdown()
        GPIO.cleanup()


if __name__ == '__main__':
    controls = AllegroControls()
    controls.microstep('sixteenth')
    controls.motor_setup()
    while True:
        for step in range(0, 100):
            time.sleep(0.004)
            controls.motor_forward()

    GPIO.output(controls.stepper['enable'], GPIO.HIGH)
    controls.motor_stopped = True
    controls.close()
