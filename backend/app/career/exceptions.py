from typing import Any
from app.event.career_domain import CareerErrorCode


class CareerSessionNotFoundException(Exception):
    def __init__(self, career_id: str) -> None:
        message = f"Career session with ID '{career_id}' was not found."
        super().__init__(message)
        self.code = CareerErrorCode.INVALID_CAREER_RECORD
        self.message = message
        self.career_id = career_id


class InvalidCareerStateException(Exception):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = CareerErrorCode.PROCESSING_ERROR
        self.message = message
        self.details = details or {}


class DecisionRequiredException(Exception):
    def __init__(self, career_id: str, decision_id: str, details: dict[str, Any] | None = None) -> None:
        message = f"Career session '{career_id}' has a pending decision '{decision_id}' that must be resolved before advancing."
        super().__init__(message)
        self.code = CareerErrorCode.PROCESSING_ERROR
        self.message = message
        self.career_id = career_id
        self.decision_id = decision_id
        self.details = details or {}


class InvalidDecisionOptionException(Exception):
    def __init__(self, decision_id: str, option_id: str) -> None:
        message = f"Option '{option_id}' is invalid for decision '{decision_id}'."
        super().__init__(message)
        self.code = CareerErrorCode.PROCESSING_ERROR
        self.message = message
        self.decision_id = decision_id
        self.option_id = option_id


class CareerCompletedException(Exception):
    def __init__(self, career_id: str) -> None:
        message = f"Career session '{career_id}' is completed and cannot be advanced further."
        super().__init__(message)
        self.code = CareerErrorCode.PROCESSING_ERROR
        self.message = message
        self.career_id = career_id


class CareerSimulationException(Exception):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = CareerErrorCode.PROCESSING_ERROR
        self.message = message
        self.details = details or {}
