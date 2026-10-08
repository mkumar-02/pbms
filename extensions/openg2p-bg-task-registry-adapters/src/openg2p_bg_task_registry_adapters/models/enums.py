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
