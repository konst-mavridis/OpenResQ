"""
Input validation service - validates request data against security and business rules.
"""
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error."""
    pass


class InputValidator:
    """Validates user inputs for all endpoints."""
    
    # Field length limits
    MAX_TITLE_LENGTH = 200
    MAX_DESCRIPTION_LENGTH = 5000
    MAX_MESSAGE_LENGTH = 1000
    MAX_DISPLAY_NAME_LENGTH = 100
    
    # Valid enums
    VALID_EVENT_TYPES = [
        "fire", "medical", "accident", "crime", "flood",
        "earthquake", "chemical", "hazmat", "other"
    ]
    VALID_SEVERITIES = ["low", "medium", "high", "critical"]
    VALID_ALERT_LEVELS = ["info", "warning", "critical"]
    VALID_ROLES = ["citizen", "responder", "admin"]
    VALID_REPORT_STATUSES = ["pending", "in_progress", "resolved", "closed"]
    VALID_ALERT_STATUSES = ["active", "resolved", "archived"]
    
    @staticmethod
    def validate_report(
        title: str,
        description: str,
        event_type: str,
        severity: str,
        latitude: float,
        longitude: float
    ) -> bool:
        """Validate report creation data."""
        
        # Check title
        if not title or not isinstance(title, str):
            raise ValidationError("Title is required and must be text")
        if len(title) > InputValidator.MAX_TITLE_LENGTH:
            raise ValidationError(f"Title cannot exceed {InputValidator.MAX_TITLE_LENGTH} characters")
        if len(title.strip()) == 0:
            raise ValidationError("Title cannot be empty")
        
        # Check description
        if description and len(description) > InputValidator.MAX_DESCRIPTION_LENGTH:
            raise ValidationError(f"Description cannot exceed {InputValidator.MAX_DESCRIPTION_LENGTH} characters")
        
        # Check event type
        if event_type not in InputValidator.VALID_EVENT_TYPES:
            raise ValidationError(f"Invalid event type. Must be one of: {InputValidator.VALID_EVENT_TYPES}")
        
        # Check severity
        if severity not in InputValidator.VALID_SEVERITIES:
            raise ValidationError(f"Invalid severity. Must be one of: {InputValidator.VALID_SEVERITIES}")
        
        # Check coordinates
        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            raise ValidationError("Latitude and longitude must be numbers")
        
        if latitude < -90 or latitude > 90:
            raise ValidationError("Latitude must be between -90 and 90")
        
        if longitude < -180 or longitude > 180:
            raise ValidationError("Longitude must be between -180 and 180")
        
        return True
    
    @staticmethod
    def validate_alert(
        title: str,
        message: str,
        level: str
    ) -> bool:
        """Validate alert creation data."""
        
        # Check title
        if not title or not isinstance(title, str):
            raise ValidationError("Title is required and must be text")
        if len(title) > InputValidator.MAX_TITLE_LENGTH:
            raise ValidationError(f"Title cannot exceed {InputValidator.MAX_TITLE_LENGTH} characters")
        
        # Check message
        if not message or not isinstance(message, str):
            raise ValidationError("Message is required and must be text")
        if len(message) > InputValidator.MAX_MESSAGE_LENGTH:
            raise ValidationError(f"Message cannot exceed {InputValidator.MAX_MESSAGE_LENGTH} characters")
        
        # Check level
        if level not in InputValidator.VALID_ALERT_LEVELS:
            raise ValidationError(f"Invalid alert level. Must be one of: {InputValidator.VALID_ALERT_LEVELS}")
        
        return True
    
    @staticmethod
    def validate_user_registration(
        email: str,
        password: str,
        display_name: str
    ) -> bool:
        """Validate user registration data."""
        
        # Check email
        if not email or "@" not in email:
            raise ValidationError("Valid email is required")
        
        if len(email) > 255:
            raise ValidationError("Email is too long")
        
        # Check password
        if not password:
            raise ValidationError("Password is required")
        
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")
        
        if len(password) > 128:
            raise ValidationError("Password is too long")
        
        # Check display name
        if not display_name or not isinstance(display_name, str):
            raise ValidationError("Display name is required")
        
        if len(display_name) > InputValidator.MAX_DISPLAY_NAME_LENGTH:
            raise ValidationError(f"Display name cannot exceed {InputValidator.MAX_DISPLAY_NAME_LENGTH} characters")
        
        if len(display_name.strip()) == 0:
            raise ValidationError("Display name cannot be empty")
        
        return True
    
    @staticmethod
    def validate_role(role: str) -> bool:
        """Validate user role."""
        if role not in InputValidator.VALID_ROLES:
            raise ValidationError(f"Invalid role. Must be one of: {InputValidator.VALID_ROLES}")
        return True
    
    @staticmethod
    def validate_area(
        latitude: float,
        longitude: float,
        radius_km: float
    ) -> bool:
        """Validate user area of interest."""
        
        # Check coordinates
        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            raise ValidationError("Latitude and longitude must be numbers")
        
        if latitude < -90 or latitude > 90:
            raise ValidationError("Latitude must be between -90 and 90")
        
        if longitude < -180 or longitude > 180:
            raise ValidationError("Longitude must be between -180 and 180")
        
        # Check radius
        if not isinstance(radius_km, (int, float)):
            raise ValidationError("Radius must be a number")
        
        if radius_km < 1 or radius_km > 100:
            raise ValidationError("Radius must be between 1 and 100 km")
        
        return True
    
    @staticmethod
    def validate_status(status: str, valid_statuses: list) -> bool:
        """Validate status against allowed values."""
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status. Must be one of: {valid_statuses}")
        return True
    
    @staticmethod
    def validate_note(note: str) -> bool:
        """Validate responder note."""
        if not note or not isinstance(note, str):
            raise ValidationError("Note is required and must be text")
        
        if len(note) > InputValidator.MAX_MESSAGE_LENGTH:
            raise ValidationError(f"Note cannot exceed {InputValidator.MAX_MESSAGE_LENGTH} characters")
        
        if len(note.strip()) == 0:
            raise ValidationError("Note cannot be empty")
        
        return True
