from backend.app.repository.collections.crud_token import TokenCrud
from backend.app.repository.collections.crud_user import UserCrud
from backend.app.repository.collections.crund_file import FileOperation

class CRUDManager:
    def __init__(self):
        self.users = UserCrud()
        self.files = FileOperation()
        self.tokens = TokenCrud()

crud = CRUDManager()

