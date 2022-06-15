from CFS.Data import hardcoded
from CFS.Mechanisms.boolmechanism import BoolMechanism
from CFS.Mechanisms.mechanism import MechanismIDs


class PayloadRelease(BoolMechanism):
    # This class is used to store and define the payload release mechanism

    def __init__(self):
        # This is used to initialise the parachute release mechanism
        super().__init__(
            "PayloadMech",
            MechanismIDs.PAYLOAD,
            hardcoded.PAY_PIN_PAYLOAD_SERVO,
            hardcoded.PAY_INIT_PAYLOAD_SERVO,
            hardcoded.PAY_ACTI_PAYLOAD_SERVO
        )
