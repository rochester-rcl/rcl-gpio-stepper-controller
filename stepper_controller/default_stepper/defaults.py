from enum import Enum


class DefaultAllegroPins(Enum):
    """
        Stores all default GPIO values
    """
    DIR = 23
    STEP = 24
    ENABLE = 12
    VDD = 14
    MICROSTEP_MS1 = 22
    MICROSTEP_MS2 = 5
    MICROSTEP_MS3 = 6


def default_allegro():
    """
    Returns a dict that stores all of the default values for an Allegro stepper driver carrier 
    :return:
        dict
    """
    return {'dir': DefaultAllegroPins.DIR, 'step': DefaultAllegroPins.STEP,
            'enable': DefaultAllegroPins.ENABLE,
            'vdd': DefaultAllegroPins.VDD,
            'microstep': {'ms1': DefaultAllegroPins.MICROSTEP_MS1, 'ms2': DefaultAllegroPins.MICROSTEP_MS2,
                          'ms3': DefaultAllegroPins.MICROSTEP_MS3}}
