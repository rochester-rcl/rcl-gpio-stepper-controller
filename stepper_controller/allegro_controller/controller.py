import RPi.GPIO as GPIO
from threading import Thread, Lock
from enum import Enum
import time
from default_stepper.defaults import default_allegro

class AllegroControls:
    MICROSTEP_FULL = 0
    MICROSTEP_HALF = 1
    MICROSTEP_QUARTER = 2
    MICROSTEP_EIGHTH = 3
    MICROSTEP_SIXTEENTH = 4
    DEFAULT_STEP_ANGLE = 1.8
    DEFAULT_RPM = 60
    _lock = Lock()
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
            step_angle (``float``) -- 
                The step angle of the motor. Default is 1.8 degrees
            rpm (``int``) -- 
                The desired speed of the motor in revolutions per minute. Default is 60.
        """
        if 'stepper' in kwargs:
            self.stepper = self.merge_stepper_configs(default_allegro(), kwargs['stepper'])
        else:
            self.stepper = default_allegro()

        if 'step_angle' in kwargs:
            self.step_angle = kwargs['step_angle']
        else:
            self.step_angle = self.DEFAULT_STEP_ANGLE

        if 'rpm' in kwargs:
            self._rpm = kwargs['rpm']
        else:
            self._rpm = self.DEFAULT_RPM

        self.steps_per_rev = int(360 / self.step_angle)
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
        self._thread = Thread(target=self._move, args=())

    def _set_microstep_resolution(self, pins, pin_modes):
        set_microstep = lambda pin, pin_mode: GPIO.output(pin, pin_mode)
        for pin, mode in zip(pins, pin_modes):
            print(pin, mode)
            set_microstep(pin[1], mode)

    @property
    def rps(self):
        """
        The speed of the motor in revolutions per second 
        """
        return int(self._rpm / 60)

    @property
    def rpm(self):
        """
        The speed of the motor in revolutions per minute
        """
        return int(self._rpm)

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
        GPIO.output(self.stepper['enable'], GPIO.HIGH)

    def set_speed(self, rpm):
        """
        :param rpm (``int``): The speed of the motor in revolutions per minute 
        """
        with self._lock:
            self._rpm = rpm

    def move(self):
        """
        Continuously moves the motor in the current direction (executes in a separate thread)
        """
        self._thread.start()

    def _move(self):
        sleep_duration = int(self.rps / self.steps_per_rev)
        while True:
            for i in range(0, self.steps_per_rev):
                with self._lock:
                    if self.motor_stopped is True:
                        self._motor_shutdown()
                        break
                    if self.paused:
                        self._pause()
                        break
                    self.step()
                    time.sleep(sleep_duration)

    def step(self):
        """
        Moves the motor one step in the current direction
        """
        GPIO.output(self.stepper['step'], GPIO.HIGH)
        GPIO.output(self.stepper['step'], GPIO.LOW)

    def _pause(self):
        GPIO.output(self.stepper['step'], GPIO.LOW)

    def pause(self):
        """
        Pauses the motor's movement
        """
        self.paused = not self.paused

    def _motor_shutdown(self):
        """
        Shuts down the motor and does any necessary GPIO cleanup
        """
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

    @staticmethod
    def merge_stepper_configs(config_1, config_2):
        cloned = config_1.copy()
        cloned.update(config_2)
        return cloned


if __name__ == '__main__':
    controls = AllegroControls()
    controls.microstep(AllegroControls.MICROSTEP_FULL)
    controls.motor_setup(True)
    for step in range(0, 100):
        time.sleep(0.004)
        controls.step()
    controls.disable()
    controls.close()
