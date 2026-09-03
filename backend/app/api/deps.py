import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.services.auth import decode_access_token

# tokenUrl is only used to populate the "Authorize" button in /docs; the
# actual login endpoint accepts a JSON body, not this form.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)


def get_current_user(token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials.", headers={"WWW-Authenticate": "Bearer"})
    if not token:
        raise credentials_error
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise credentials_error
    try:
        user_id = uuid.UUID(payload["sub"])
    except ValueError:
        raise credentials_error
    user = db.get(User, user_id)
    if user is None:
        raise credentials_error
    return user


def require_recruiter(user: User = Depends(get_current_user)) -> User:
    if user.role != "recruiter":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This action is restricted to recruiter accounts.")
    return user


def require_candidate(user: User = Depends(get_current_user)) -> User:
    if user.role != "candidate":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This action is restricted to candidate accounts.")
    return user
