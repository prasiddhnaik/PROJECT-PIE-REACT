"""
Shared authentication utilities for microservices.
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import os

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class AuthManager:
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

# Global auth manager instance
auth_manager = AuthManager()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependency to get current authenticated user."""
    token = credentials.credentials
    payload = auth_manager.verify_token(token)
    return payload

def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """Dependency to get current user if authenticated, None otherwise."""
    if not credentials:
        return None
    try:
        token = credentials.credentials
        payload = auth_manager.verify_token(token)
        return payload
    except HTTPException:
        return None

class UserContext:
    """User context for request tracking."""
    def __init__(self, user_id: Optional[str] = None, session_id: Optional[str] = None):
        self.user_id = user_id
        self.session_id = session_id
        self.request_id = None
        
    def set_request_id(self, request_id: str):
        self.request_id = request_id
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "request_id": self.request_id
        }

def create_user_context(user_data: Optional[Dict[str, Any]] = None) -> UserContext:
    """Create user context from auth data."""
    if not user_data:
        return UserContext()
    
    return UserContext(
        user_id=user_data.get("sub"),
        session_id=user_data.get("session_id")
    ) 