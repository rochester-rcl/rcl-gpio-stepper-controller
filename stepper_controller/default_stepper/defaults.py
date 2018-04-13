from enum import Enum


class DefaultStepperPins(Enum):
    """
        Stores all default GPIO values
    """
    RIGHT_DIR = 23
    RIGHT_STEP = 24
    RIGHT_ENABLE = 12
    RIGHT_VDD = 14
    RIGHT_MICROSTEP_MS1 = 22
    RIGHT_MICROSTEP_MS2 = 5
    RIGHT_MICROSTEP_MS3 = 6

    LEFT_DIR = 20
    LEFT_STEP = 21
    LEFT_ENABLE = 16
    LEFT_VDD = 15
    LEFT_MICROSTEP_MS1 = 22
    LEFT_MICROSTEP_MS2 = 5
    LEFT_MICROSTEP_MS3 = 6

    @property
    def default_allegro(self):
        """
        A dict that stores all of the default values for an Allegro stepper driver carrier 
        """
        return {'dir': self.RIGHT_DIR, 'step': self.RIGHT_STEP, 'enable': self.RIGHT_ENABLE,
                'vdd': self.RIGHT_VDD, 'microstep': {'ms1': self.RIGHT_MICROSTEP_MS1, 'ms2': self.RIGHT_MICROSTEP_MS2,
                                                     'ms3': self.RIGHT_MICROSTEP_MS3}}