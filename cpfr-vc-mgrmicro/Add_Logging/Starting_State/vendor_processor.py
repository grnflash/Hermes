"""
Vendor Processor for CPFR Vendor Contact Streamlit Manager

Handles business logic, validation, and data processing for vendor contact management.
Single-row model: one row per (Vendor Number, FILE). Supports duplicate labeling for
multiple rows per vendor (FILE primacy: Tier1 > Tier2 > 6Months > None).
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# FILE primacy for duplicate labeling: first is primary, rest are subordinates
FILE_PRIMACY_ORDER = ['Tier1', 'Tier2', '6Months', 'None']

@dataclass
class ValidationResult:
    """Result of validation operation"""
    is_valid: bool
    normalized_value: str
    errors: List[str]

@dataclass
class VendorSearchResult:
    """Result of vendor search operation. vendors list includes is_primary and duplicate_label per row."""
    vendors: List[Dict[str, Any]]

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
    
    def _file_primacy_rank(self, file_value: str) -> int:
        """Return sort rank for FILE (lower = higher primacy). Tier1 > Tier2 > 6Months > None."""
        try:
            return FILE_PRIMACY_ORDER.index(file_value)
        except ValueError:
            return len(FILE_PRIMACY_ORDER)
    
    def _row_fingerprint(self, row: Dict[str, Any], exclude_keys: Optional[List[str]] = None) -> str:
        """Stable string for comparing rows (excluding FILE and Vendor Number for same-FILE compare)."""
        exclude = set(exclude_keys or []) | {'FILE', 'Vendor Number'}
        parts = []
        for k in sorted(row.keys()):
            if k in exclude:
                continue
            v = row.get(k)
            parts.append(f"{k}={repr(v)}")
        return "|".join(parts)
    
    def process_search_results(self, df) -> VendorSearchResult:
        """
        Process search results: sort by FILE primacy, label duplicates.

        FILE values are pre-normalized by DatabaseManager.search_vendors before this
        method receives them. For each vendor number, rows are ordered by FILE primacy
        (Tier1 > Tier2 > 6Months > None). First row is primary; additional rows get
        is_primary=False and duplicate_label:
        - Different FILE from primary: "(duplicate)"
        - Same FILE, other fields differ: "(duplicate - other)"
        - Same FILE, identical: "(duplicate 2)", "(duplicate 3)", ...

        Args:
            df: DataFrame with search results (FILE column already normalized)

        Returns:
            VendorSearchResult with vendors list (each row has is_primary, duplicate_label)
        """
        if df.empty:
            return VendorSearchResult([])

        vendors = df.to_dict('records')
        
        # Group by Vendor Number
        vendor_groups = {}
        for vendor in vendors:
            vendor_number = vendor['Vendor Number']
            if vendor_number not in vendor_groups:
                vendor_groups[vendor_number] = []
            vendor_groups[vendor_number].append(vendor)
        
        result_list = []
        for vendor_number, group in vendor_groups.items():
            # Sort by FILE primacy (Tier1 first, then Tier2, 6Months, None)
            group_sorted = sorted(
                group,
                key=lambda r: (self._file_primacy_rank(r.get('FILE', '')), self._row_fingerprint(r))
            )
            primary = group_sorted[0]
            primary['is_primary'] = True
            primary['duplicate_label'] = None
            result_list.append(primary)
            
            if len(group_sorted) == 1:
                continue
            
            primary_fingerprint = self._row_fingerprint(primary)
            primary_file = primary.get('FILE', '')
            identical_count = 0
            
            for sub in group_sorted[1:]:
                sub['is_primary'] = False
                sub_file = sub.get('FILE', '')
                sub_fingerprint = self._row_fingerprint(sub)
                
                if sub_file != primary_file:
                    sub['duplicate_label'] = '(duplicate)'
                elif sub_fingerprint != primary_fingerprint:
                    sub['duplicate_label'] = '(duplicate - other)'
                else:
                    identical_count += 1
                    sub['duplicate_label'] = f'(duplicate {identical_count + 1})'
                result_list.append(sub)
        
        return VendorSearchResult(
            vendors=result_list
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
