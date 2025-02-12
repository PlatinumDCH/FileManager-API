from backend.app.core.security.secure_token.strategies.base_strategy import ITokenStrategy
from datetime import timedelta

class EmailTokenStrategy(ITokenStrategy):

    def _get_default_expiry(self) ->timedelta:
        return timedelta(minutes=30)
    
    async def create_token(
            self, 
            data, 
            expire_delta = None
        ) -> str:
        return self._encode_token(
            data,
            'email_token',
            expire_delta
        )
    
    async def decode_token(self, token)->dict: 
        return self._decode_token(token, 'email_token')
    