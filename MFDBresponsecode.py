from enum import Enum

class Response(Enum):
    invalidKeyword = 400
    invalidPassword = 401
    noKeyMatches = 402
    noTableMatches = 403
    invalidInstanceCode = 404