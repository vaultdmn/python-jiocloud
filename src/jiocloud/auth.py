"""Authentication module for JioCloud (Phone and Email OTP send and verify)."""

from typing import Any, Optional

from jiocloud._http import JioCloudHTTPClient


class AuthService:
    """Handles JioCloud authentication flows (Phone & Email OTP send/verify)."""

    def __init__(self, http: JioCloudHTTPClient) -> None:
        self.http = http
        self.base_url = "https://api.jioaicloud.com"

    def send_otp(
        self,
        mobile_number: Optional[str] = None,
        email_id: Optional[str] = None,
    ) -> None:
        """Send OTP to mobile number or email ID.

        Args:
            mobile_number: Mobile number with country code (e.g. "+910000000000").
            email_id: Email address (e.g. "user@example.com").
        """
        if email_id:
            url = f"{self.base_url}/account/login/otp/send"
            payload: dict[str, Any] = {"emailId": email_id}
        else:
            url = f"{self.base_url}/account/jioid/sendotp"
            payload = {"mobileNumber": mobile_number or ""}
        self.http.post(url, json=payload)

    def verify_otp(
        self,
        mobile_number: Optional[str] = None,
        email_id: Optional[str] = None,
        otp: str = "",
        is_stay_sign_in: bool = True,
    ) -> dict[str, Any]:
        """Verify OTP and authenticate user session via phone or email.

        Args:
            mobile_number: Mobile number with country code.
            email_id: Email address.
            otp: 6-digit OTP code received.
            is_stay_sign_in: Whether to maintain persistent login.

        Returns:
            Dictionary containing user accounts and session details.
        """
        if email_id:
            url = f"{self.base_url}/account/otp/login"
            payload = {
                "mobileNumber": "",
                "emailId": email_id,
                "otp": otp,
                "deviceType": "W",
                "deviceInfo": {
                    "model": "browser",
                    "deviceName": "Web Device",
                    "platformType": "Firefox",
                    "platformVersion": "155.0",
                    "type": "browser",
                    "isWebClient": True,
                },
                "isStaySignIn": is_stay_sign_in,
            }
        else:
            url = f"{self.base_url}/account/jioid/verifyotp"
            payload = {
                "mobileNumber": mobile_number or "",
                "otp": otp,
                "isStaySignIn": is_stay_sign_in,
                "isMnr": "Y",
            }
        response = self.http.post(url, json=payload)
        return dict(response) if isinstance(response, dict) else {}
