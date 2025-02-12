import asyncio
from backend.app.core.security.secure_token.manager import token_manager
from backend.app.core.security.secure_token.types import TokenType

async def main():
    data = {"user_id": 123}
    token = await token_manager.create_token(TokenType.RESET_PASSWORD, data)
    decoded = await token_manager.decode_token(TokenType.RESET_PASSWORD, token)
    
    print("Generated Token:", token)
    print("Decoded Data:", decoded)


asyncio.run(main())