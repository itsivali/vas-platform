from beanie import Document, Indexed, Link
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import re

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"

class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    SUPPORT = "support"
    FINANCE = "finance"

class UserMetadata(BaseModel):
    device_info: Optional[Dict[str, Any]] = {}
    preferences: Optional[Dict[str, Any]] = {}
    kyc_status: Optional[str] = "pending"
    kyc_documents: Optional[List[str]] = []
    last_login_ip: Optional[str] = None
    failed_login_attempts: int = 0
    account_locked_until: Optional[datetime] = None

class User(Document):
    # Basic Information
    phone_number: Indexed(str, unique=True) = Field(..., description="User's phone number")
    email: Optional[Indexed(EmailStr, unique=True)] = None
    full_name: Optional[str] = Field(None, max_length=255)
    id_number: Optional[str] = Field(None, max_length=50)
    
    # Financial
    wallet_balance: float = Field(default=0.0, ge=0, description="Current wallet balance")
    loyalty_points: int = Field(default=0, ge=0)
    credit_limit: float = Field(default=0.0, ge=0)
    
    # Account Status
    status: UserStatus = UserStatus.ACTIVE
    role: UserRole = UserRole.CUSTOMER
    is_verified: bool = False
    email_verified: bool = False
    phone_verified: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    
    # Metadata
    metadata: UserMetadata = Field(default_factory=UserMetadata)
    
    # Security
    password_hash: Optional[str] = None
    mfa_secret: Optional[str] = None
    recovery_codes: Optional[List[str]] = []
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        #  phone number validation
        pattern = r'^\+254[71][0-9]{8}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid phone number format')
        return v
    
    @validator('id_number')
    def validate_id_number(cls, v):
        if v and not re.match(r'^[0-9]{8}$', v):
            raise ValueError('Invalid ID number format')
        return v
    
    class Settings:
        name = "users"
        indexes = [
            "phone_number",
            "email", 
            "status",
            "role",
            "created_at",
            "last_login_at",
            [("phone_number", 1), ("status", 1)],
        ]