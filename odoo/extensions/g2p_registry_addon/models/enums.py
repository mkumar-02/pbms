import enum


class StipendProgramEnum(str, enum.Enum):
    """Matches NSR ``StipendProgramEnum`` / ``g2p_attribute_values`` stipend programs."""

    STIPEND_CLEANING = "STIPEND_CLEANING"
    STIPEND_MAINTENANCE = "STIPEND_MAINTENANCE"
    STIPEND_FOOD_GARDENS = "STIPEND_FOOD_GARDENS"
    STIPEND_SOCIAL_SERVICES = "STIPEND_SOCIAL_SERVICES"


class WorkTypeEnum(str, enum.Enum):
    """Matches NSR ``WorkTypeEnum`` / ``g2p_attribute_values`` work types."""

    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"


STIPEND_PROGRAM_SELECTION = [
    (StipendProgramEnum.STIPEND_CLEANING.value, "Cleaning"),
    (StipendProgramEnum.STIPEND_MAINTENANCE.value, "Maintenance"),
    (StipendProgramEnum.STIPEND_FOOD_GARDENS.value, "Food Gardens"),
    (StipendProgramEnum.STIPEND_SOCIAL_SERVICES.value, "Social Services"),
]

WORK_TYPE_SELECTION = [
    (WorkTypeEnum.FULL_TIME.value, "Full Time"),
    (WorkTypeEnum.PART_TIME.value, "Part Time"),
]
