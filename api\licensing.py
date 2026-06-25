from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from licensing.manager import LicenseManager, LicenseType

router = APIRouter(prefix="/api/v1/licenses", tags=["licensing"])
manager = LicenseManager()


class IssueLicenseRequest(BaseModel):
    owner_email: str
    license_type: LicenseType
    organization: str = None


@router.post("/issue")
def issue_license(req: IssueLicenseRequest):
    return manager.issue(req.owner_email, req.license_type, req.organization)


@router.get("/validate/{key}")
def validate_license(key: str):
    return manager.validate(key)


@router.post("/revoke/{key}")
def revoke_license(key: str, reason: str = ""):
    return manager.revoke(key, reason)


@router.post("/renew/{key}")
def renew_license(key: str):
    return manager.renew(key)


@router.get("/list")
def list_licenses(owner_email: str = None):
    return {"licenses": manager.list_licenses(owner_email)}
