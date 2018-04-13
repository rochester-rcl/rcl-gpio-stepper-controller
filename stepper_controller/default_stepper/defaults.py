from enum import Enum


class DefaultAllegroPins(Enum):
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


def default_allegro():
    """
    Returns a dict that stores all of the default values for an Allegro stepper driver carrier 
    :returns: dict 
    
    """
    return {'dir': DefaultAllegroPins.RIGHT_DIR, 'step': DefaultAllegroPins.RIGHT_STEP,
            'enable': DefaultAllegroPins.RIGHT_ENABLE,
            'vdd': DefaultAllegroPins.RIGHT_VDD,
            'microstep': {'ms1': DefaultAllegroPins.RIGHT_MICROSTEP_MS1, 'ms2': DefaultAllegroPins.RIGHT_MICROSTEP_MS2,
                          'ms3': DefaultAllegroPins.RIGHT_MICROSTEP_MS3}}
