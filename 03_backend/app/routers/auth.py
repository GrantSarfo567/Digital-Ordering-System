from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.auth_service import send_otp, verify_otp

router = APIRouter()

class PhoneRequest(BaseModel):
    phone: str

class OTPVerifyRequest(BaseModel):
    phone: str
    token: str

@router.post("/send-otp")
def request_otp(body: PhoneRequest):
    try:
        send_otp(body.phone)
        return {"message": "OTP sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify-otp")
def verify_otp_route(body: OTPVerifyRequest):
    try:
        response = verify_otp(body.phone, body.token)
        return {
            "message": "Verification successful",
            "session": response
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))