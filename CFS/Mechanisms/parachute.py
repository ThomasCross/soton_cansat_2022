from CFS.Data import hardcoded
from CFS.Mechanisms.boolmechanism import BoolMechanism
from CFS.Mechanisms.mechanism import MechanismIDs


class ParachuteRelease(BoolMechanism):
    # This class is used to store and define the parachute release mechanism

    def __init__(self):
        # This is used to initialise the parachute release mechanism
        super().__init__(
            "ParachuteMech",
            MechanismIDs.PARACHUTE,
            hardcoded.CON_PIN_PARACHUTE_SERVO,
            hardcoded.CON_INIT_PARACHUTE_SERVO,
            hardcoded.CON_ACTI_PARACHUTE_SERVO
        )
