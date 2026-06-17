from jose import jwt

SECRET_KEY = "mude-isso"

ALGORITHM = "HS256"

def create_token(email):

    return jwt.encode(
        {"sub": email},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
