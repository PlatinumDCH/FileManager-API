from enum import Enum

class RoleSet(str, Enum):
    admin = 'ADMIN'
    user = 'USER'
    