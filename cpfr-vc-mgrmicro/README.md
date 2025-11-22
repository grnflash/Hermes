# CPFR Vendor Contact Manager Micro

A Streamlit-based interface for managing vendor contact information in the Snowflake EDLDB.SC_SANDBOX.VC_CPFR_VENDOR_EMAIL table.

**Note:** This is a variant of `cpfr-vc-sltmgr` intended for a different audience with altered scope, features, and permissions.

## Purpose

This tool provides a user-friendly interface for managing vendor contact information with:
- Restricted field editing (some fields hidden from editing)
- Altered FILE field editing behavior
- Different permissions and scope compared to the main manager

## Key Differences from cpfr-vc-sltmgr

- **Restricted Field Access**: Some fields are hidden from editing
- **Modified FILE Field Editing**: Different workflow for editing the FILE field
- **Different Audience**: Intended for users with different permission levels
- **Independent Development**: No shared components - completely separate codebase

## Technology Stack

- **Python 3.11+**
- **Streamlit** (Snowflake native environment)
- **Snowflake Connector** for database operations
- **Pandas** for data manipulation

## Getting Started

1. Deploy to Snowflake Streamlit Apps
2. Configure connection to EDLDB.SC_SANDBOX schema
3. Access through Snowflake's native Streamlit interface

## Project Structure

- `streamlit_app.py` - Main Streamlit application
- `database_manager.py` - Snowflake connection and queries
- `vendor_processor.py` - Business logic and validation

## Development Notes

This project is maintained independently from `cpfr-vc-sltmgr` to ensure:
- No shared components that could cause cross-contamination
- Independent development cycles
- Isolated bug fixes and feature development

