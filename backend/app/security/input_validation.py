"""Input validation and sanitization utilities.

Provides utilities for validating and sanitizing user inputs
to prevent injection attacks and ensure data integrity.
"""

from typing import Any, Optional, List, Dict
import re
from pydantic import BaseModel, validator, ValidationError


class InputSanitizer:
    """Input sanitization utilities.
    
    Provides methods to sanitize and validate user inputs
    to prevent security vulnerabilities.
    """
    
    # Patterns for common injection attacks
    SQL_INJECTION_PATTERN = re.compile(
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|SCRIPT)\b)",
        re.IGNORECASE,
    )
    
    XSS_PATTERN = re.compile(
        r"<script[^>]*>.*?</script>|<iframe[^>]*>.*?</iframe>|javascript:|onerror=|onload=",
        re.IGNORECASE | re.DOTALL,
    )
    
    COMMAND_INJECTION_PATTERN = re.compile(
        r"[;&|`$(){}[\]<>]",
    )
    
    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        """Sanitize string input.
        
        Args:
            value: Input string
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
            
        Raises:
            ValueError: If input contains dangerous patterns
        """
        if not isinstance(value, str):
            raise ValueError("Input must be a string")
        
        # Check for SQL injection
        if InputSanitizer.SQL_INJECTION_PATTERN.search(value):
            raise ValueError("Potentially dangerous SQL pattern detected")
        
        # Check for XSS
        if InputSanitizer.XSS_PATTERN.search(value):
            raise ValueError("Potentially dangerous script pattern detected")
        
        # Trim whitespace
        sanitized = value.strip()
        
        # Enforce max length
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal.
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Sanitized filename
        """
        # Remove path separators
        sanitized = filename.replace("/", "").replace("\\", "")
        
        # Remove dangerous characters
        sanitized = re.sub(r"[^a-zA-Z0-9._-]", "", sanitized)
        
        # Prevent hidden files
        if sanitized.startswith("."):
            sanitized = sanitized[1:]
        
        return sanitized
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        pattern = re.compile(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )
        return bool(pattern.match(email))
    
    @staticmethod
    def validate_url(url: str, allowed_schemes: Optional[List[str]] = None) -> bool:
        """Validate URL format and scheme.
        
        Args:
            url: URL to validate
            allowed_schemes: List of allowed URL schemes (default: http, https)
            
        Returns:
            True if valid, False otherwise
        """
        if allowed_schemes is None:
            allowed_schemes = ["http", "https"]
        
        pattern = re.compile(
            r"^(" + "|".join(allowed_schemes) + r")://"
            r"([a-zA-Z0-9.-]+|\[[0-9a-fA-F:]+\])"
            r"(?::[0-9]+)?"
            r"(?:/[^\s]*)?$"
        )
        return bool(pattern.match(url))


class SafeInput(BaseModel):
    """Pydantic model for safe input validation."""
    
    @validator("*", pre=True)
    def sanitize_inputs(cls, v: Any) -> Any:
        """Sanitize all string inputs."""
        if isinstance(v, str):
            return InputSanitizer.sanitize_string(v)
        return v


def validate_and_sanitize(
    data: Dict[str, Any],
    schema: Optional[BaseModel] = None,
) -> Dict[str, Any]:
    """Validate and sanitize input data.
    
    Args:
        data: Input data dictionary
        schema: Optional Pydantic schema for validation
        
    Returns:
        Sanitized data dictionary
        
    Raises:
        ValidationError: If validation fails
    """
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = InputSanitizer.sanitize_string(value)
        elif isinstance(value, dict):
            sanitized[key] = validate_and_sanitize(value)
        elif isinstance(value, list):
            sanitized[key] = [
                validate_and_sanitize(item) if isinstance(item, dict)
                else InputSanitizer.sanitize_string(item) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    if schema:
        try:
            return schema(**sanitized).dict()
        except ValidationError as e:
            raise ValueError(f"Validation failed: {e}")
    
    return sanitized

