import uuid
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum


class LicenseType(str, Enum):
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class LicenseStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"


class LicenseManager:
    """
    Manages software/agent licenses for the real estate platform.
    Handles issuance, validation, renewal, and revocation.
    """

    LICENSE_DURATIONS = {
        LicenseType.BASIC: 30,
        LicenseType.PROFESSIONAL: 365,
        LicenseType.ENTERPRISE: 730,
    }

    LICENSE_LIMITS = {
        LicenseType.BASIC: {"api_calls_per_day": 100, "users": 1, "properties": 50},
        LicenseType.PROFESSIONAL: {"api_calls_per_day": 5000, "users": 10, "properties": 500},
        LicenseType.ENTERPRISE: {"api_calls_per_day": -1, "users": -1, "properties": -1},
    }

    def __init__(self):
        self._licenses: dict[str, dict] = {}

    def issue(self, owner_email: str, license_type: LicenseType,
              organization: str = None) -> dict:
        """Issue a new license key."""
        key = f"RE-{license_type.value.upper()}-{str(uuid.uuid4()).upper()[:16]}"
        days = self.LICENSE_DURATIONS[license_type]
        now = datetime.utcnow()

        record = {
            "key": key,
            "owner_email": owner_email,
            "organization": organization,
            "license_type": license_type.value,
            "status": LicenseStatus.ACTIVE.value,
            "issued_at": now.isoformat(),
            "expires_at": (now + timedelta(days=days)).isoformat(),
            "limits": self.LICENSE_LIMITS[license_type],
            "api_calls_today": 0,
            "last_used": None,
        }
        self._licenses[key] = record
        return record

    def validate(self, key: str) -> dict:
        """Validate a license key and return its status."""
        record = self._licenses.get(key)
        if not record:
            return {"valid": False, "reason": "License key not found"}

        if record["status"] == LicenseStatus.REVOKED.value:
            return {"valid": False, "reason": "License has been revoked"}

        expires = datetime.fromisoformat(record["expires_at"])
        if datetime.utcnow() > expires:
            record["status"] = LicenseStatus.EXPIRED.value
            return {"valid": False, "reason": "License has expired"}

        limit = record["limits"].get("api_calls_per_day", -1)
        if limit != -1 and record["api_calls_today"] >= limit:
            return {"valid": False, "reason": "Daily API call limit reached"}

        record["api_calls_today"] += 1
        record["last_used"] = datetime.utcnow().isoformat()
        return {"valid": True, "license_type": record["license_type"],
                "expires_at": record["expires_at"], "limits": record["limits"]}

    def revoke(self, key: str, reason: str = "") -> dict:
        if key not in self._licenses:
            return {"success": False, "error": "Key not found"}
        self._licenses[key]["status"] = LicenseStatus.REVOKED.value
        self._licenses[key]["revoke_reason"] = reason
        return {"success": True, "key": key}

    def renew(self, key: str) -> dict:
        if key not in self._licenses:
            return {"success": False, "error": "Key not found"}
        record = self._licenses[key]
        lt = LicenseType(record["license_type"])
        days = self.LICENSE_DURATIONS[lt]
        record["expires_at"] = (datetime.utcnow() + timedelta(days=days)).isoformat()
        record["status"] = LicenseStatus.ACTIVE.value
        return {"success": True, "new_expiry": record["expires_at"]}

    def list_licenses(self, owner_email: str = None) -> list[dict]:
        licenses = list(self._licenses.values())
        if owner_email:
            licenses = [l for l in licenses if l["owner_email"] == owner_email]
        return licenses
