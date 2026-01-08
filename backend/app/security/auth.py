"""Enhanced authentication and authorization.

Provides JWT-based authentication, OAuth2 support, and
role-based access control (RBAC).
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings


# Security scheme for FastAPI
security = HTTPBearer()


class AuthService:
    """Authentication and authorization service.
    
    Handles JWT token generation, validation, and user authentication.
    Supports role-based access control.
    """
    
    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
    ) -> None:
        """Initialize auth service.
        
        Args:
            secret_key: JWT secret key (from settings if not provided)
            algorithm: JWT algorithm
            access_token_expire_minutes: Token expiration time
        """
        self.secret_key = secret_key or getattr(settings, "jwt_secret_key", "")
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
    
    def create_access_token(
        self,
        subject: str,
        roles: Optional[List[str]] = None,
        extra_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create JWT access token.
        
        Args:
            subject: User identifier (username, email, etc.)
            roles: List of user roles
            extra_claims: Additional claims to include
            
        Returns:
            Encoded JWT token
        """
        expire = datetime.utcnow() + timedelta(
            minutes=self.access_token_expire_minutes
        )
        
        payload = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            "roles": roles or [],
        }
        
        if extra_claims:
            payload.update(extra_claims)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify token and return user info.
        
        Args:
            token: JWT token
            
        Returns:
            User information from token
        """
        payload = self.decode_token(token)
        return {
            "username": payload.get("sub"),
            "roles": payload.get("roles", []),
        }


class RBAC:
    """Role-based access control helper."""
    
    @staticmethod
    def require_role(required_role: str):
        """Dependency to require specific role.
        
        Args:
            required_role: Required role name
            
        Returns:
            FastAPI dependency function
        """
        async def role_checker(
            credentials: HTTPAuthorizationCredentials = Depends(security),
        ) -> Dict[str, Any]:
            auth_service = AuthService()
            payload = auth_service.decode_token(credentials.credentials)
            roles = payload.get("roles", [])
            
            if required_role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role '{required_role}' required",
                )
            
            return payload
        
        return role_checker
    
    @staticmethod
    def require_any_role(*required_roles: str):
        """Dependency to require any of the specified roles.
        
        Args:
            *required_roles: One or more required roles
            
        Returns:
            FastAPI dependency function
        """
        async def role_checker(
            credentials: HTTPAuthorizationCredentials = Depends(security),
        ) -> Dict[str, Any]:
            auth_service = AuthService()
            payload = auth_service.decode_token(credentials.credentials)
            roles = payload.get("roles", [])
            
            if not any(role in roles for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"One of roles {required_roles} required",
                )
            
            return payload
        
        return role_checker


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """FastAPI dependency to get current authenticated user.
    
    Args:
        credentials: HTTP bearer credentials
        
    Returns:
        User information dictionary
    """
    auth_service = AuthService()
    return auth_service.verify_token(credentials.credentials)

