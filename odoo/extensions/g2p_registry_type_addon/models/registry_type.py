from enum import Enum
from odoo import models, fields


class G2PTargetModelMapping:

    MODEL_MAPPING = {
        "farmer": "g2p.register.farmer",
        "households": "g2p.register.households",
        "individual_stipend_program": "g2p.individual.stipend.program.registry",
    }

    @classmethod
    def get_target_model_name(cls, key):
        return cls.MODEL_MAPPING.get(key)


class G2PRegistryType(Enum):
    FARMER = "farmer"
    HOUSEHOLDS = "households"
    INDIVIDUAL_STIPEND_PROGRAM = "individual_stipend_program"

    @classmethod
    def selection(cls):
        return [(member.value, member.name.replace("_", " ").title()) for member in cls]
