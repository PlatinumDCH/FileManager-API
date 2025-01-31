import bcrypt
from dataclasses import dataclass


class Hasher:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """check password"""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    @staticmethod
    def get_password_hesh(password):
        """generate passord cashe"""
        salt = bcrypt.gensalt()
        heshed_passerd = bcrypt.hashpw(password.encode("utf-8"), salt)
        return heshed_passerd.decode("utf-8")
