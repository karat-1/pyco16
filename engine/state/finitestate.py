import logging



class FiniteState:
    """
    A State Object which can encapsulate behaviour and is part of a StateMachine
    """

    def __init__(self, entity_obj = None, state_machine = None):
        """
        :param entity_obj: an Entity type object
        :param state_machine: The FiniteStateMachine Object corresponding to the project that was passed in
        """
        self.e = entity_obj
        self.state_machine = state_machine
        self.exiting_state = None
        self.start_time = 0
        self.animation_finished = False
        self.name = "Default"
        self.action_possible = False
        self.transitional_data = None
        self.is_locked = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def set_entity_obj(self, entity_obj):
        self.e = entity_obj

    def set_state_machine(self, state_machine):
        self.state_machine = state_machine

    def enter_state(self) -> None:
        """
        This function gets called when the StateMachine enters the current state for the first time
        :return: Nothing
        """
        self.exiting_state = False

    def exit_state(self) -> None:
        """
        This function gets called when the StateMachine exits the current state
        :return: Nothing
        """
        self.exiting_state = True

    def logic_update(self, dt) -> None:
        """
        This function gets called every frame. For encapsulation purposes, this function only should contain
        logical updates and state transitions
        :return: Nothing
        """
        if not self.e or not self.state_machine:
            self.logger.warning("entity or state machine not set. Cant update state")

    def physics_update(self, dt) -> None:
        """
        This function gets called every frame. For encapsulation purposes, this function only should contain
        physical updates
        :return: Nothing
        """
        if not self.e or not self.state_machine:
            self.logger.warning("entity or state machine not set. Cant update state")

    def late_physics_update(self, dt) -> None:
        """
        This function can be called during an entities late update. E.g. after its position has been updated
        :return: Nothing
        """
        if not self.e or not self.state_machine:
            self.logger.warning("entity or state machine not set. Cant update state")

    def late_logic_update(self, dt) -> None:
        """
        This function can be called during an entities late update. E.g. after its position has been updated
        :return: Nothing
        """
        if not self.e or not self.state_machine:
            self.logger.warning("entity or state machine not set. Cant update state")

    def print_state(self) -> None:
        self.logger.info(self.name)

    def render_state(self, surf, offset) -> None:
        pass
