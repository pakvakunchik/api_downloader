import enum

class Status(str, enum.Enum):
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'
    IN_PROGRESS = 'IN_PROGRESS'