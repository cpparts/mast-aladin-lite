from enum import StrEnum


class AIDA_aspects(StrEnum):
    CENTER = "center"
    FOV = "fov"
    ROTATION = "rotation"
    IMAGE_LABEL = "image_label"

    def get_viewport_sync_list():
        return [AIDA_aspects.CENTER, AIDA_aspects.FOV, AIDA_aspects.ROTATION]
