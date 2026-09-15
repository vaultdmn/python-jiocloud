"""Authentication module for JioCloud (OTP send and verify)."""

from typing import Any

from jiocloud._http import JioCloudHTTPClient


class AuthService:
    """Handles JioCloud authentication flows (Send OTP / Verify OTP)."""

    def __init__(self, http: JioCloudHTTPClient) -> None:
        self.http = http
        self.base_url = "https://api.jioaicloud.com"

    def send_otp(self, mobile_number: str) -> None:
        """Send OTP to mobile number.

        Args:
            mobile_number: Mobile number with country code (e.g. "+910000000000").
        """
        url = f"{self.base_url}/account/jioid/sendotp"
        payload = {"mobileNumber": mobile_number}
        self.http.post(url, json=payload)

    def verify_otp(
        self,
        mobile_number: str,
        otp: str,
        is_stay_sign_in: bool = True,
    ) -> dict[str, Any]:
        """Verify OTP and authenticate user session.

        Args:
            mobile_number: Mobile number with country code.
            otp: 6-digit OTP code received.
            is_stay_sign_in: Whether to maintain persistent login.

        Returns:
            Dictionary containing user accounts and session details.
        """
        url = f"{self.base_url}/account/jioid/verifyotp"
        payload = {
            "mobileNumber": mobile_number,
            "otp": otp,
            "isStaySignIn": is_stay_sign_in,
            "isMnr": "Y",
        }
        response = self.http.post(url, json=payload)
        return dict(response) if isinstance(response, dict) else {}
