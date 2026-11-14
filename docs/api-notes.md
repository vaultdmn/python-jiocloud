# JioCloud API Notes

This document summarizes the reverse-engineered JioCloud Web API endpoints, headers, authentication flows, and request/response structures based on captured HTTP traffic (HAR).

## 1. Hosts & Domains

- **Authentication & Account API:** `https://api.jioaicloud.com`
- **File & Folder Metadata API:** `https://jaws-api.jioaicloud.com`
- **Upload API:** `https://jaws-upload.jioaicloud.com`
- **Download API:** `https://jaws-dl.jioaicloud.com`
- **Profile API:** `https://photosapi.jio.com`

---

## 2. Common Request Headers

Every request to JioCloud APIs must include standard client identification headers:

| Header Name | Value / Description |
| :--- | :--- |
| `X-Api-Key` | Static API key (`<API_KEY>`, configurable) |
| `X-App-Secret` | Base64 encoded app secret |
| `X-Client-Details` | `clientType:WEB; appVersion:89.0.12` |
| `X-Device-Type` | `W` (Web client) |
| `X-Device-Key` | Persistent UUID generated per client instance |
| `Authorization` / `Cookie` | Session tokens (`u` cookie containing auth data) |

---

## 3. Authentication Flow

### Send OTP
- **URL:** `POST https://api.jioaicloud.com/account/jioid/sendotp`
- **Request Body:**
  ```json
  {
    "mobileNumber": "+91<MOBILE_NUMBER>"
  }
  ```
- **Response:** Status `204 No Content` on success.

### Verify OTP
- **URL:** `POST https://api.jioaicloud.com/account/jioid/verifyotp`
- **Request Body:**
  ```json
  {
    "mobileNumber": "+91<MOBILE_NUMBER>",
    "otp": "<OTP_CODE>",
    "isStaySignIn": true,
    "isMnr": "Y"
  }
  ```
- **Response:**
  ```json
  {
    "requestId": "<UUID>",
    "userAccounts": [
      {
        "userId": "<USER_ID>",
        "productType": "Mobile",
        "phoneNumber": "+91<MOBILE_NUMBER>",
        "allocatedSpace": 64424509440,
        "isEmailValReq": "N"
      }
    ]
  }
  ```
  Sets session cookie `u` containing user session details.

---

## 4. File & Folder Operations (`jaws-api.jioaicloud.com`)

### List Files / Metadata
- **URL:** `GET /nms/metadata` or `GET /nms/metadata/defaultview/myfiles/v1`
- **Headers:** Requires `X-Device-Key`, `X-User-Id`, and auth cookie/token.

### Create Folder
- **URL:** `POST /nms/folders`
- **Request Body:** Folder metadata and parent path IDs.

### Rename, Move, Copy, Delete
- Handled via endpoints under `/nms/metadata/` using appropriate HTTP methods (`PUT`/`POST`).

---

## 5. Upload & Download

### Upload (`https://jaws-upload.jioaicloud.com`)
- **URL:** `POST /upload/files`
- **Mechanism:** Multipart/form-data or chunked binary uploads with headers (`X-CHUNK-SIZE`, `Content-MD5`).

### Download (`https://jaws-dl.jioaicloud.com`)
- **URL:** `GET /download/files/{id}`
- **Mechanism:** Direct binary streaming with support for `Range` headers.

---

## 6. Error Responses
Standard HTTP error codes:
- `400`: Bad Request
- `401`: Unauthorized / Expired Token
- `404`: Not Found
- `429`: Too Many Requests
- `5xx`: Server Error
