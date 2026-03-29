"""
Vendor Processor for CPFR Vendor Contact Streamlit Manager

Handles business logic, validation, and data processing for vendor contact management.
Implements Tier2+6Months logic and email validation.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of validation operation"""
    is_valid: bool
    normalized_value: str
    errors: List[str]

@dataclass
class VendorSearchResult:
    """Result of vendor search operation"""
    vendors: List[Dict[str, Any]]
    has_dual_entries: bool
    tier2_entries: List[Dict[str, Any]]
    other_entries: List[Dict[str, Any]]

class EmailValidator:
    """Handles email validation and normalization"""
    
    # Email regex pattern - standard format
    EMAIL_PATTERN = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', re.IGNORECASE)
    
    @classmethod
    def validate_email_list(cls, email_string: str) -> ValidationResult:
        """
        Validate and normalize semicolon-delimited email list
        
        Args:
            email_string: Semicolon-delimited email string
            
        Returns:
            ValidationResult with normalized emails and any errors
        """
        if not email_string or not isinstance(email_string, str):
            return ValidationResult(True, '', [])
        
        emails = []
        errors = []
        
        # Split by semicolon and process each email
        for email in email_string.split(';'):
            email = email.strip()
            
            if not email:  # Skip empty entries
                continue
            
            # Normalize email case (domain lowercase, preserve local part)
            if '@' in email:
                local, domain = email.rsplit('@', 1)
                normalized_email = f"{local}@{domain.lower()}"
            else:
                normalized_email = email.lower()
            
            # Validate email format
            if cls.EMAIL_PATTERN.match(normalized_email):
                emails.append(normalized_email)
            else:
                errors.append(f"Invalid email format: {email}")
        
        # Remove duplicates and sort
        unique_emails = sorted(set(emails))
        normalized = ';'.join(unique_emails)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            normalized_value=normalized,
            errors=errors
        )

class VendorProcessor:
    """Main business logic processor for vendor operations"""
    
    def __init__(self):
        self.email_validator = EmailValidator()
    
    def process_search_results(self, df) -> VendorSearchResult:
        """
        Process search results and identify dual entries
        
        Args:
            df: DataFrame with search results
            
        Returns:
            VendorSearchResult with organized vendor data
        """
        if df.empty:
            return VendorSearchResult([], False, [], [])
        
        vendors = df.to_dict('records')
        
        # Group by Vendor Number to identify dual entries
        vendor_groups = {}
        for vendor in vendors:
            vendor_number = vendor['Vendor Number']
            if vendor_number not in vendor_groups:
                vendor_groups[vendor_number] = []
            vendor_groups[vendor_number].append(vendor)
        
        # Check for Tier2+6Months combinations
        has_dual_entries = False
        tier2_entries = []
        other_entries = []
        
        for vendor_number, vendor_list in vendor_groups.items():
            file_values = [v['FILE'] for v in vendor_list]
            
            # Check if this vendor has Tier2+6Months combination
            if 'Tier2' in file_values and '6Months' in file_values:
                has_dual_entries = True
                tier2_entries.extend([v for v in vendor_list if v['FILE'] in ['Tier2', '6Months']])
            else:
                other_entries.extend(vendor_list)
        
        return VendorSearchResult(
            vendors=vendors,
            has_dual_entries=has_dual_entries,
            tier2_entries=tier2_entries,
            other_entries=other_entries
        )
    
    def validate_vendor_data(self, vendor_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate vendor data for all fields
        
        Args:
            vendor_data: Dictionary with vendor field data
            
        Returns:
            ValidationResult with validation status and errors
        """
        errors = []
        normalized_data = {}
        
        for field, value in vendor_data.items():
            if not value:  # Skip empty values
                normalized_data[field] = value
                continue
            
            # Validate email fields
            if field in ['Vendor Contacts', 'CM_Email', 'CM Manager_Email', 'SP_Email', 'SP Manager_Email', 'OVERRIDE_EMAIL']:
                result = self.email_validator.validate_email_list(str(value))
                normalized_data[field] = result.normalized_value
                errors.extend(result.errors)
            
            # Validate other fields
            elif field in ['Vendor Number']:
                # Basic validation for vendor number
                if not isinstance(value, str) or len(value.strip()) < 3:
                    errors.append(f"Vendor Number must be at least 3 characters")
                normalized_data[field] = str(value).strip()
            
            else:
                # Basic string normalization
                normalized_data[field] = str(value).strip() if value else ''
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            normalized_value=str(normalized_data),
            errors=errors
        )
    
    def calculate_changes(self, original: Dict[str, Any], updated: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate which fields have changed
        
        Args:
            original: Original vendor data
            updated: Updated vendor data
            
        Returns:
            Dictionary with only changed fields
        """
        changes = {}
        
        for field, new_value in updated.items():
            original_value = original.get(field, '')
            
            # Normalize values for comparison
            if field in ['Vendor Contacts', 'CM_Email', 'CM Manager_Email', 'SP_Email', 'SP Manager_Email', 'OVERRIDE_EMAIL']:
                # Normalize email fields for comparison
                orig_result = self.email_validator.validate_email_list(str(original_value))
                new_result = self.email_validator.validate_email_list(str(new_value))
                if orig_result.normalized_value != new_result.normalized_value:
                    changes[field] = new_result.normalized_value
            else:
                # Simple string comparison for other fields
                if str(original_value).strip() != str(new_value).strip():
                    changes[field] = str(new_value).strip()
        
        return changes
    
    def create_dual_entry_data(self, vendor_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Create data for both Tier2 and 6Months entries
        
        Args:
            vendor_data: Base vendor data
            
        Returns:
            Tuple of (tier2_data, sixmonths_data)
        """
        # Create copies of the base data
        tier2_data = vendor_data.copy()
        sixmonths_data = vendor_data.copy()
        
        # Set FILE values
        tier2_data['FILE'] = 'Tier2'
        sixmonths_data['FILE'] = '6Months'
        
        return tier2_data, sixmonths_data
    
    def get_required_fields(self) -> List[str]:
        """
        Get list of required fields for new vendor entries
        
        Returns:
            List of required field names
        """
        return ['Vendor Number', 'Vendor Name', 'Vendor Contacts']
    
    def get_editable_fields(self) -> List[str]:
        """
        Get list of editable fields (excludes Vendor Number and FILE)
        
        Note: The following fields are hidden from editing:
        - PURCHASER
        - Shipment Method Code
        - CB Rollout Phase
        - Soft Chargeback Effective Date
        - Hard Chargeback Effective Date
        
        Returns:
            List of editable field names
        """
        return [
            'Vendor Name', 'Vendor Contacts',
            'Parent Vendor', 'CM_Email', 'CM Manager_Email',
            'SP_Email', 'SP Manager_Email', 'OVERRIDE_EMAIL'
        ]
