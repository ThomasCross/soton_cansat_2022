from CFS.Mechanisms.servomechanism import ServoMechanism


class BoolMechanism(ServoMechanism):
    # This class is used to define boolean servo mechanisms

    def __init__(self, mechanism_name, mechanism_id, servo_pin, initial_pos, activate_pos):
        # Used to initialise BoolMechanism class
        # String    mechanism_name     Contains name of sensor
        # Int       mechanism_id       Contains id of sensor
        # Int       servo_pin          Pin of servo mechanism

        super().__init__(mechanism_name, mechanism_id, servo_pin)  # Initialise Parent Class

        self._logger.info("Starting Boolean Mechanism Object ({},{})".format(initial_pos, activate_pos))

        self.__init_pos = initial_pos  # Store initial and activation servo positions
        self.__acti_pos = activate_pos

        self._logger.info("Setting Boolean Mechanism to initial position")
        self.set_servo_pos(initial_pos)  # Set servo to initial position

    def activate(self):
        # Used to move the servo to an activation position
        self._logger.info("Setting Boolean Mechanism to activation position")
        self.set_servo_pos(self.__acti_pos)
