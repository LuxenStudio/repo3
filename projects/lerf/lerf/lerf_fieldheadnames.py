from enum import Enum
# from luxenstudio.field_components.field_heads import FieldHeadNames

class LERFFieldHeadNames(Enum):
    """Possible field outputs"""
    HASHGRID = "hashgrid"
    CLIP = "clip"
    DINO = "dino"