from aiogram.fsm.state import State, StatesGroup


class ExerciseState(StatesGroup):
    answering = State()


class TestState(StatesGroup):
    in_progress = State()


class AIState(StatesGroup):
    waiting = State()
