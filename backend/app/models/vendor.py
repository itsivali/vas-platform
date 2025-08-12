from beanie import Document, Indexed
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class VendorStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"

class VendorType(str, Enum):
    TELECOM = "telecom"
    ENTERTAINMENT = "entertainment"
    UTILITY = "utility"
    FINANCIAL = "financial"
    RETAIL = "retail"

class APIConfiguration(BaseModel):
    base_url: str
    api_version: str = "v1"
    timeout: int = 30
    retry_attempts: int = 3
    rate_limit: int = 1000  # requests per hour
    authentication_type: str = "api_key"  # api_key, oauth, basic
    headers: Optional[Dict[str, str]] = {}

class WebhookConfiguration(BaseModel):
    url: Optional[HttpUrl] = None
    events: List[str] = []
    secret: Optional[str] = None
    retry_attempts: int = 3
    timeout: int = 10

class SettlementAccount(BaseModel):
    bank_name: str
    account_number: str
    account_name: str
    branch_code: Optional[str] = None
    swift_code: Optional[str] = None

class VendorMetadata(BaseModel):
    business_registration: Optional[Dict[str, Any]] = {}
    contact_persons: Optional[List[Dict[str, Any]]] = []
    sla_requirements: Optional[Dict[str, Any]] = {}
    technical_contacts: Optional[List[Dict[str, str]]] = []

class Vendor(Document):
    # Basic Information
    company_name: str = Field(..., max_length=255)
    business_number: Indexed(str, unique=True)
    vendor_type: VendorType
    description: Optional[str] = None
    
    # API Configuration
    api_key: Indexed(str, unique=True)
    api_secret_hash: str
    api_config: APIConfiguration
    webhook_config: Optional[WebhookConfiguration] = None
    
    # Business Configuration
    commission_rate: float = Field(..., ge=0, le=100, description="Commission percentage")
    settlement_account: SettlementAccount
    settlement_frequency: str = "daily"  
    
    # Status and Verification
    status: VendorStatus = VendorStatus.PENDING
    is_verified: bool = False
    verification_documents: Optional[List[str]] = []
    
    # Performance Metrics
    total_transactions: int = 0
    total_revenue: float = 0.0
    success_rate: float = 0.0
    average_response_time: float = 0.0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity_at: Optional[datetime] = None
    contract_start_date: Optional[datetime] = None
    contract_end_date: Optional[datetime] = None
    
    # Metadata
    metadata: VendorMetadata = Field(default_factory=VendorMetadata)
    
    class Settings:
        name = "vendors"
        indexes = [
            "company_name",
            "business_number",
            "api_key",
            "status",
            "vendor_type",
            "created_at",
            [("status", 1), ("vendor_type", 1)],
        ]