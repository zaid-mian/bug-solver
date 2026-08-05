# -------------------
#  Constants File
# -------------------

from enum import StrEnum

MAX_RETRIES = 10


# ----------------------------------------------
#  Status StrEnum (SUCCESS, FAILED, IN_PROGESS)
# ----------------------------------------------
class Status(StrEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    IN_PROGRESS = "IN_PROGRESS"
