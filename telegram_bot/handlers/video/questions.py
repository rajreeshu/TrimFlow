from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict, Any, Optional, Callable


class QuestionType(Enum):
    """Enumeration of possible question types."""
    ORIENTATION = auto()
    VIDEO_LENGTH = auto()
    START_TIME = auto()
    END_TIME = auto()

@dataclass
class QuestionConfig:
    """Configuration for each question in the flow."""
    type: QuestionType
    message: str
    options: List[Dict[str, Any]]
    validator: Optional[Callable[[str], bool]] = None
    converter: Optional[Callable[[str], Any]] = None


def create_default_questions() -> List[QuestionConfig]:
    question_dicts = [
        {
            "type": QuestionType.ORIENTATION,
            "message": "Select the Orientation of the Video:",
            "options": [
                {"label": "Landscape", "value": "landscape"},
                {"label": "Portrait", "value": "portrait"}
            ],
            "validator": None,
            "converter": str
        },
        {
            "type": QuestionType.VIDEO_LENGTH,
            "message": "Select Video Length:",
            "options": [
                {"label": "30 seconds", "value": 30},
                {"label": "1 minute", "value": 60},
                {"label": "5 minutes", "value": 300},
                {"label": "Custom", "value": "custom"}
            ],
            "validator": lambda x: str(x).isdigit() and int(x) > 0,
            "converter": int
        },
        {
            "type": QuestionType.START_TIME,
            "message": "Select Start Time:",
            "options": [
                {"label": "10 seconds", "value": 10},
                {"label": "30 seconds", "value": 30},
                {"label": "Custom", "value": "custom"}
            ],
            "validator": lambda x: str(x).isdigit() and int(x) >= 0,
            "converter": int
        },
        {
            "type": QuestionType.END_TIME,
            "message": "Select End Time:",
            "options": [
                {"label": "10 seconds", "value": 10},
                {"label": "1 minute", "value": 60},
                {"label": "Custom", "value": "custom"}
            ],
            "validator": lambda x: str(x).isdigit() and int(x) > 0,
            "converter": int
        }
    ]
    return [QuestionConfig(**qd) for qd in question_dicts]
