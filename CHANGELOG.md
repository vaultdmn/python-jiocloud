# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v0.1.0.html).

## [Unreleased]

### Added
- Automated token refresh on 401/403 responses using refresh tokens.
- Streamed chunked upload support with progress reporting (`TransferService.upload`).
- Redaction of sensitive tokens and authorization secrets from exception messages (`SEC-01`).

## [0.1.0] - 2026-11-12

### Added
- Initial release of `python-jiocloud`, an unofficial Python client for JioCloud API.
- Support for OTP authentication flow (`send_otp`, `verify_otp`).
- File management operations (`list`, `get`, `rename`, `move`, `delete`).
- Folder management operations (`list`, `create`).
- Transfer capabilities (download and upload with progress callbacks).
- Exception hierarchy (`AuthError`, `NotFoundError`, `RateLimitError`, `APIError`).
- Full type annotations (`py.typed`) and test suite using `respx` and `pytest`.
