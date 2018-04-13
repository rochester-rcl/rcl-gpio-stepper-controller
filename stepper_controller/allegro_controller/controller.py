# import RPi.GPIO as GPIO
from threading import Thread
from enum import Enum
import time
from default_stepper.defaults import default_allegro


class AllegroControls:
    MICROSTEP_FULL = 0
    MICROSTEP_HALF = 1
    MICROSTEP_QUARTER = 2
    MICROSTEP_EIGHTH = 3
    MICROSTEP_SIXTEENTH = 4
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
            self.stepper = {**kwargs['stepper'], **default_allegro()}
        else:
            self.stepper = default_allegro()

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
        self._thread = Thread(target=self._forward, args=())

    def _set_microstep_resolution(self, pins, pin_modes):

        set_microstep = lambda pin, pin_mode: GPIO.output(pin, pin_mode)
        for pin, mode in zip(pins, pin_modes):
            print(pin, mode)
            set_microstep(pin[1], mode)

    def microstep(self, resolution):
        """
        :param resolution (``int``): The resolution of each step - options are 
        AllegoControls.MICROSTEP_FULL (0 - default)
        
        AllegroControls.MICROSTEP_HALF (1)
        
        AllegroControls.MICROSTEP_QUARTER (2)
        
        AllegroControls.MICROSTEP_EIGHTH (3)
        
        AllegroControls.MICROSTEP_SIXTEENTH (4)
        
        """
        # available resolutions - FULL, HALF, QUARTER, EIGHTH, SIXTEENTH

        if resolution is self.MICROSTEP_FULL:  # LOW LOW LOW
            pin_mode = [GPIO.LOW, GPIO.LOW, GPIO.LOW]
            self._set_microstep_resolution(self.right_stepper['microstep'].items(), pin_mode)
            self._set_microstep_resolution(self.left_stepper['microstep'].items(), pin_mode)
        if resolution is self.MICROSTEP_HALF:  # HIGH LOW LOW
            pin_mode = (GPIO.HIGH, GPIO.LOW, GPIO.LOW)
            self._set_microstep_resolution(self.right_stepper['microstep'].items(), pin_mode)
            self._set_microstep_resolution(self.left_stepper['microstep'].items(), pin_mode)
        if resolution is self.MICROSTEP_QUARTER:  # LOW HIGH LOW
            pin_mode = (GPIO.LOW, GPIO.HIGH, GPIO.LOW)
            self._set_microstep_resolution(self.right_stepper['microstep'].items(), pin_mode)
            self._set_microstep_resolution(self.left_stepper['microstep'].items(), pin_mode)
        if resolution is self.MICROSTEP_EIGHTH:  # HIGH HIGH LOW
            pin_mode = (GPIO.HIGH, GPIO.HIGH, GPIO.LOW)
            self.set_microstep_resolution(self.right_stepper['microstep'].items(), pin_mode)
            self.set_microstep_resolution(self.left_stepper['microstep'].items(), pin_mode)
        if resolution is self.MICROSTEP_SIXTEENTH:
            pin_mode = (GPIO.HIGH, GPIO.HIGH, GPIO.HIGH)
            self._set_microstep_resolution(self.right_stepper['microstep'].items(), pin_mode)
            self._set_microstep_resolution(self.left_stepper['microstep'].items(), pin_mode)

    def motor_setup(self, dir):
        """
        :param dir (``bool``): The direction the motor turns 
        True = clockwise 
        False = counter-clockwise 
        """
        state = GPIO.LOW if dir is False else GPIO.HIGH
        # move right stepper counter clockwise
        GPIO.output(self.stepper['dir'], state)
        GPIO.output(self.stepper['enable'], state)

    def motor_forward(self):
        """
        Moves the motor forward in a separate thread
        """
        self._thread.start()

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

    def disable(self):
        """
        Disables the motor by setting the controller's enable pin to HIGH 
        """
        GPIO.output(controls.stepper['enable'], GPIO.HIGH)
        self.motor_stopped = True

    def close(self):
        """
        Shuts down the motor and cleans up GPIO pins
        """
        self._motor_shutdown()
        GPIO.cleanup()


if __name__ == '__main__':
    controls = AllegroControls()
    controls.microstep(AllegroControls.MICROSTEP_FULL)
    controls.motor_setup()
    for step in range(0, 100):
        time.sleep(0.004)
        controls.motor_forward()
    controls.disable()
    controls.close()
