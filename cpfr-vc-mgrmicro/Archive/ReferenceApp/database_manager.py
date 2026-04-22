"""
Database manager for Streamlit in Snowflake - Simplified version

Handles all Snowflake database operations for the VC_CPFR_VENDOR_EMAIL table.
Uses get_active_session() exclusively for Streamlit in Snowflake.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages Snowflake database operations using user's active session"""
    
    def __init__(self):
        """Initialize database manager for Streamlit in Snowflake"""
        self.session = None
        self.table_name = "EDLDB.SC_SANDBOX.VC_CPFR_VENDOR_EMAIL"
        self.last_error = None
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize Snowpark session using get_active_session() only"""
        try:
            from snowflake.snowpark.context import get_active_session
            self.session = get_active_session()
            if not self.session:
                raise ConnectionError("No active Snowflake session found. This app must run in Streamlit in Snowflake.")
            
            # Verify session works
                test_result = self.session.sql("SELECT 1 as test").collect()
                if not test_result:
                    raise ConnectionError("Session test query failed")
            
            logger.info("Successfully initialized Snowpark session")
        except ImportError:
            raise ImportError("Snowflake Snowpark not available")
        except Exception as e:
            logger.error(f"Failed to initialize Snowpark session: {e}")
            raise ConnectionError(f"Unable to establish Snowflake connection: {e}")
    
    def get_session(self):
        """Get the active Snowpark session"""
        if not self.session:
            self._initialize_session()
        return self.session
    
    def _escape_sql_string(self, value: Any) -> str:
        """Escape string values for SQL safety."""
        if value is None:
            return 'NULL'
        escaped_value = str(value).replace("'", "''")
        return f"'{escaped_value}'"
    
    def _execute_dml(self, query: str, operation: str = "DML") -> bool:
        """
        Execute DML operation (UPDATE, DELETE, INSERT) with error handling
        
        Args:
            query: SQL query to execute
            operation: Operation name for logging
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session()
        try:
            logger.info(f"Executing {operation}: {query[:200]}...")  # Log first 200 chars
            result = session.sql(query).collect()
            logger.info(f"{operation} executed successfully (result: {result})")
            
            # Commit the transaction
            try:
                session.sql("COMMIT").collect()
                logger.info(f"Committed {operation}")
            except Exception as e:
                logger.warning(f"Could not commit {operation} (may be auto-commit): {e}")
            
            return True
        except Exception as e:
            error_msg = f"{operation} failed: {str(e)}"
            self.last_error = error_msg
            logger.error(error_msg)
            logger.error(f"Failed query: {query}")
            return False
    
    def search_vendors(self, search_type: str, search_value: str) -> pd.DataFrame:
        """Search vendors by different criteria"""
        session = self.get_session()
        
        if search_type == "Vendor Number":
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE "Vendor Number" = '{search_value}'
                ORDER BY "Vendor Number", "FILE"
            """
        else:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE "{search_type}" ILIKE '%{search_value}%'
                ORDER BY "Vendor Number", "FILE"
            """
        
        try:
            df = session.sql(query).to_pandas()
            logger.info(f"Found {len(df)} vendor records for {search_type}: {search_value}")
            return df
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def get_vendor(self, vendor_number: str, file_value: str) -> Optional[Dict[str, Any]]:
        """Get a specific vendor record"""
        session = self.get_session()
        
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE "Vendor Number" = '{vendor_number}' AND "FILE" = '{file_value}'
        """
        
        try:
            df = session.sql(query).to_pandas()
            if not df.empty:
                return df.iloc[0].to_dict()
            return None
        except Exception as e:
            logger.error(f"Failed to get vendor {vendor_number}: {e}")
            raise
    
    def get_vendor_combinations(self, vendor_number: str) -> List[Dict[str, Any]]:
        """Get all FILE combinations for a vendor number"""
        session = self.get_session()
        
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE "Vendor Number" = '{vendor_number}'
            ORDER BY "FILE"
        """
        
        try:
            df = session.sql(query).to_pandas()
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Failed to get vendor combinations for {vendor_number}: {e}")
            raise
    
    def update_vendor(self, vendor_number: str, file_value: str, updates: Dict[str, Any]) -> bool:
        """Update vendor record with only changed fields"""
        if not updates:
            return True
        
        # Check if this is a dual entry vendor (Tier2+6Months)
        if file_value in ['Tier2', '6Months']:
            return self._update_dual_entry_vendor(vendor_number, file_value, updates)
        
        return self._update_single_vendor(vendor_number, file_value, updates)
    
    def change_vendor_tier(self, vendor_number: str, original_file: str, new_file: str, updates: Dict[str, Any]) -> bool:
        """
        Change vendor tier (FILE value) using explicit-then-implicit pattern
        
        Architecture:
        1. Make explicit change first (UPDATE FILE field)
        2. Run implicit checks and fixes based on resulting state
        """
        logger.info(f"Changing vendor {vendor_number} from {original_file} to {new_file}")
        
        # Remove FILE from updates since we handle it separately
        field_updates = {k: v for k, v in updates.items() if k != 'FILE'}
        
        # Special case: Changing TO Tier2 requires creating dual entry with full data
        # This includes: Tier1/3Months → Tier2, AND standalone 6Months → Tier2
        if new_file == 'Tier2':
            # Check if both Tier2 and 6Months already exist (true dual entry)
            vendor_combinations = self.get_vendor_combinations(vendor_number)
            tier2_exists = any(v.get('FILE') == 'Tier2' for v in vendor_combinations)
            sixmonths_exists = any(v.get('FILE') == '6Months' for v in vendor_combinations)
            
            if tier2_exists and sixmonths_exists:
                # Both exist - this is a "within dual entry" change
                if original_file in ['Tier2', '6Months']:
                    return self._change_within_dual_entry(vendor_number, original_file, new_file, field_updates)
                else:
                    # This shouldn't happen, but handle it
                    logger.warning(f"Both Tier2 and 6Months exist, but original_file is {original_file}")
                    return self._change_within_dual_entry(vendor_number, original_file, new_file, field_updates)
            else:
                # One or neither exists - create dual entry
                return self._change_to_tier2_with_dual_entry(vendor_number, original_file, field_updates)
        
        # Special case: Changing WITHIN dual entry pair (Tier2 ↔ 6Months)
        # Only if both exist and we're swapping between them
        if (original_file in ['Tier2', '6Months'] and new_file in ['Tier2', '6Months'] and original_file != new_file):
            vendor_combinations = self.get_vendor_combinations(vendor_number)
            tier2_exists = any(v.get('FILE') == 'Tier2' for v in vendor_combinations)
            sixmonths_exists = any(v.get('FILE') == '6Months' for v in vendor_combinations)
            
            if tier2_exists and sixmonths_exists:
                # Both exist - use within dual entry logic
                return self._change_within_dual_entry(vendor_number, original_file, new_file, field_updates)
            else:
                # Only one exists - treat as regular tier change
                logger.info(f"Only one entry exists ({original_file}), treating as regular tier change")
                if not self._make_explicit_tier_change(vendor_number, original_file, new_file, field_updates):
                    return False
                # NOTE: We do NOT call _check_and_fix_missing_secondary here because
                # standalone entries are valid - dual entries should only be created
                # when explicitly changing TO Tier2
                return True
        
        # Regular tier change: Make explicit change first
        if not self._make_explicit_tier_change(vendor_number, original_file, new_file, field_updates):
            return False
        
        # Handle special case - if changing FROM Tier2/6Months, remove orphaned secondary
        if original_file in ['Tier2', '6Months'] and new_file not in ['Tier2', '6Months']:
            secondary_file = '6Months' if original_file == 'Tier2' else 'Tier2'
            self._delete_orphaned_secondary(vendor_number, secondary_file)
        
        # Run implicit checks and fixes
        # NOTE: We do NOT call _check_and_fix_missing_secondary here because:
        # - Standalone 6Months entries are valid (should not auto-create Tier2)
        # - Dual entries should only be created when explicitly changing TO Tier2
        # - This check should only run in dual-entry contexts
        self._check_and_fix_duplicates(vendor_number)
        self._check_and_fix_unsynced_dual(vendor_number)
        
        return True
    
    def _change_to_tier2_with_dual_entry(self, vendor_number: str, original_file: str, updates: Dict[str, Any]) -> bool:
        """
        Special handling for changing TO Tier2 - creates Tier2 and ensures 6Months exists
        
        Logic:
        1. Check current state: Does 6Months already exist?
        2. If 6Months exists: Update it with merged data, create Tier2, delete original
        3. If 6Months doesn't exist: Create both Tier2 and 6Months, delete original
        """
        logger.info(f"Changing to Tier2 - creating dual entry for vendor {vendor_number}")
        session = self.get_session()
        
        try:
            # Step 1: Check current state - does 6Months already exist?
            vendor_combinations = self.get_vendor_combinations(vendor_number)
            sixmonths_exists = any(v.get('FILE') == '6Months' for v in vendor_combinations)
            tier2_exists = any(v.get('FILE') == 'Tier2' for v in vendor_combinations)
            
            logger.info(f"State check: sixmonths_exists={sixmonths_exists}, tier2_exists={tier2_exists}, original_file={original_file}")
            
            # Get current vendor data (the entry we're changing FROM)
            current_vendor = self.get_vendor(vendor_number, original_file)
            if not current_vendor:
                logger.error(f"Vendor {vendor_number} with FILE {original_file} not found")
                return False
            
            # Apply updates to current data
            updated_vendor_data = current_vendor.copy()
            updated_vendor_data.update(updates)
            updated_vendor_data['Vendor Number'] = vendor_number
            
            # Use existing create_dual_entry_data logic to get properly formatted data
            import streamlit as st
            tier2_data, sixmonths_data = st.session_state.vendor_processor.create_dual_entry_data(updated_vendor_data)
            
            # Step 2: Handle based on state
            if sixmonths_exists:
                # 6Months already exists - update it, create Tier2, delete original
                logger.info("6Months entry already exists - updating it and creating Tier2")
                
                # Update existing 6Months entry with merged data
                if not self._update_single_vendor(vendor_number, '6Months', sixmonths_data):
                    logger.error(f"Failed to update existing 6Months entry for vendor {vendor_number}")
                    return False
                
                # Create Tier2 entry
                if not self._insert_single_vendor(tier2_data):
                    logger.error(f"Failed to create Tier2 entry for vendor {vendor_number}")
                    return False
                
                # Delete the original entry (only if it's not 6Months - if it is, we already updated it)
                if original_file != '6Months':
                    delete_query = f"""
                        DELETE FROM {self.table_name}
                        WHERE "Vendor Number" = '{vendor_number}' AND "FILE" = '{original_file}'
                    """
                    if not self._execute_dml(delete_query, "DELETE"):
                        logger.error(f"Failed to delete original {original_file} entry")
                        return False
                else:
                    logger.info("Original entry was 6Months, which we updated - no deletion needed")
                
            else:
                # 6Months doesn't exist - create both, delete original
                logger.info("6Months entry doesn't exist - creating both Tier2 and 6Months")
                
                # Insert both entries
                if not (self._insert_single_vendor(tier2_data) and self._insert_single_vendor(sixmonths_data)):
                    logger.error(f"Failed to create dual entries for vendor {vendor_number}")
                    return False
                
                # Delete the original entry
                delete_query = f"""
                    DELETE FROM {self.table_name}
                    WHERE "Vendor Number" = '{vendor_number}' AND "FILE" = '{original_file}'
                """
                if not self._execute_dml(delete_query, "DELETE"):
                    logger.error(f"Failed to delete original {original_file} entry")
                    return False
            
            # Final commit
            try:
                session.sql("COMMIT").collect()
                logger.info("Committed all changes for Tier2 dual entry creation")
            except Exception as e:
                logger.warning(f"Could not commit (may be auto-commit): {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to change to Tier2 dual entry: {e}", exc_info=True)
            return False
    
    def _change_within_dual_entry(self, vendor_number: str, original_file: str, new_file: str, updates: Dict[str, Any]) -> bool:
        """
        Handle changing within dual entry pair (Tier2 ↔ 6Months)
        
        CRITICAL: We must merge in memory and delete the source entry BEFORE updating,
        to avoid creating true duplicates (same Vendor Number + same FILE value).
        
        Architecture:
        1. Get both entries (Tier2 and 6Months)
        2. Merge data in memory (prefer Tier2 values, then 6Months, then apply updates)
        3. Delete the entry we're changing FROM (e.g., delete Tier2 if changing Tier2 → 6Months)
        4. Update the entry we're changing TO (e.g., update 6Months with merged data)
        5. This avoids creating duplicates that can't be safely distinguished
        """
        logger.info(f"Changing within dual entry: {vendor_number} from {original_file} to {new_file}")
        session = self.get_session()
        
        try:
            # Step 1: Get both entries
            vendor_combinations = self.get_vendor_combinations(vendor_number)
            tier2_entry = next((v for v in vendor_combinations if v.get('FILE') == 'Tier2'), None)
            sixmonths_entry = next((v for v in vendor_combinations if v.get('FILE') == '6Months'), None)
            
            # Both must exist for this to be a "within dual entry" change
            if not tier2_entry or not sixmonths_entry:
                logger.warning(f"Only one entry exists for dual entry change, falling back to regular tier change")
                return self._make_explicit_tier_change(vendor_number, original_file, new_file, updates)
            
            # Step 2: Merge data in memory
            # Prefer non-null values, or Tier2 if both exist
            merged_data = {}
            all_fields = set(tier2_entry.keys()) | set(sixmonths_entry.keys())
            
            for field in all_fields:
                if field == 'FILE':
                    continue
                tier2_value = tier2_entry.get(field)
                sixmonths_value = sixmonths_entry.get(field)
                
                # Prefer non-null value, or Tier2 if both exist
                if tier2_value is not None and str(tier2_value).strip() != '':
                    merged_data[field] = tier2_value
                elif sixmonths_value is not None and str(sixmonths_value).strip() != '':
                    merged_data[field] = sixmonths_value
                else:
                    merged_data[field] = tier2_value  # Default to Tier2 if both null
            
            # Apply user updates on top of merged data
            merged_data.update(updates)
            
            logger.info(f"Merged data prepared: {len(merged_data)} fields")
            
            # Step 3: Delete the entry we're changing FROM (before any updates)
            # This prevents creating true duplicates
            delete_query = f"""
                DELETE FROM {self.table_name}
                WHERE "Vendor Number" = '{vendor_number}' AND "FILE" = '{original_file}'
            """
            if not self._execute_dml(delete_query, "DELETE"):
                logger.error(f"Failed to delete {original_file} entry before changing to {new_file}")
                return False
            
            # Verify deletion
            verify_delete = f"""
                SELECT COUNT(*) as row_count
                FROM {self.table_name}
                WHERE "Vendor Number" = '{vendor_number}' AND "FILE" = '{original_file}'
            """
            verify_result = session.sql(verify_delete).collect()
            remaining_count = verify_result[0]['ROW_COUNT'] if verify_result else -1
            logger.info(f"After DELETE, {remaining_count} row(s) remain with FILE='{original_file}'")
            
            if remaining_count > 0:
                logger.error(f"DELETE did not remove all {original_file} entries! {remaining_count} still exist")
                return False
            
            # Commit the delete before update
            try:
                session.sql("COMMIT").collect()
                logger.info("Committed DELETE before UPDATE")
            except Exception as e:
                logger.warning(f"Could not commit DELETE (may be auto-commit): {e}")
            
            # Step 4: Update the entry we're changing TO with merged data
            if not self._update_single_vendor(vendor_number, new_file, merged_data):
                logger.error(f"Failed to update {new_file} entry with merged data")
                return False
            
            # Verify update
            verify_update = f"""
                SELECT COUNT(*) as row_count
                FROM {self.table_name}
                WHERE "Vendor Number" = '{vendor_number}' AND "FILE" = '{new_file}'
            """
            verify_result = session.sql(verify_update).collect()
            updated_count = verify_result[0]['ROW_COUNT'] if verify_result else 0
            logger.info(f"After UPDATE, {updated_count} row(s) exist with FILE='{new_file}'")
            
            if updated_count == 0:
                logger.error(f"UPDATE did not create/update {new_file} entry!")
                return False
            
            # Final commit
            try:
                session.sql("COMMIT").collect()
                logger.info("Committed all changes for within dual entry change")
            except Exception as e:
                logger.warning(f"Could not commit final changes (may be auto-commit): {e}")
            
            logger.info(f"Successfully changed {original_file} to {new_file} within dual entry")
            return True
            
        except Exception as e:
            logger.error(f"Failed to change within dual entry: {e}", exc_info=True)
            return False
    
    def _make_explicit_tier_change(self, vendor_number: str, original_file: str, new_file: str, updates: Dict[str, Any]) -> bool:
        """Make the explicit FILE change (Step 1 of explicit-then-implicit pattern)"""
        logger.info(f"Making explicit tier change: {vendor_number} from {original_file} to {new_file}")
        session = self.get_session()
        
        set_clauses = [f'"FILE" = \'{new_file}\'']
        
        for field, value in updates.items():
            if field == 'FILE':
                continue
                
            # Handle date fields
            if field in ['Soft Chargeback Effective Date', 'Hard Chargeback Effective Date']:
                if value and isinstance(value, str) and value.startswith('datetime.date'):
                    continue
                elif value and isinstance(value, str) and value != 'None':
                    try:
                        from datetime import datetime
                        parsed_date = datetime.strptime(value, '%Y-%m-%d').date()
                        value = parsed_date.strftime('%Y-%m-%d')
                    except:
                        logger.warning(f"Could not parse date field {field}: {value}")
                        continue
            
            # Handle NULL values
            if value is None or value == '' or str(value).strip() == '':
                escaped_value = 'NULL'
            else:
                escaped_value = self._escape_sql_string(value)
            
            set_clauses.append(f'"{field}" = {escaped_value}')
        
        query = f"""
            UPDATE {self.table_name}
            SET {', '.join(set_clauses)}
            WHERE "Vendor Number" = '{vendor_number}' AND "FILE" = '{original_file}'
        """
        
        logger.info(f"Executing UPDATE query: {query}")
        
        # Execute the UPDATE
        if not self._execute_dml(query, "UPDATE"):
            logger.error(f"Failed to execute UPDATE for vendor {vendor_number}")
            return False
        
        # Verify that the UPDATE actually affected a row
        verify_query = f"""
            SELECT COUNT(*) as row_count
            FROM {self.table_name}
            WHERE "Vendor Number" = '{vendor_number}' AND "FILE" = '{new_file}'
        """
        
        try:
            result = session.sql(verify_query).collect()
            row_count = result[0]['ROW_COUNT'] if result else 0
            logger.info(f"Verification query found {row_count} row(s) with FILE='{new_file}' after UPDATE")
            
            if row_count == 0:
                logger.error(f"UPDATE did not affect any rows! Vendor {vendor_number}, FILE {original_file} -> {new_file}")
                # Check if the original entry still exists
                check_original = f"""
                    SELECT COUNT(*) as row_count
                    FROM {self.table_name}
                    WHERE "Vendor Number" = '{vendor_number}' AND "FILE" = '{original_file}'
                """
                check_result = session.sql(check_original).collect()
                original_count = check_result[0]['ROW_COUNT'] if check_result else 0
                logger.error(f"Original entry still exists: {original_count} row(s) with FILE='{original_file}'")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Failed to verify UPDATE: {e}")
            # Don't fail on verification error, but log it
            return True  # Assume success if verification fails
    
    def _delete_orphaned_secondary(self, vendor_number: str, file_to_delete: str) -> bool:
        """Delete an orphaned secondary entry (e.g., 6Months when Tier2 was changed to Tier1)"""
        logger.info(f"Deleting orphaned secondary entry: {vendor_number} FILE={file_to_delete}")
        
        delete_query = f"""
            DELETE FROM {self.table_name}
            WHERE "Vendor Number" = '{vendor_number}' AND "FILE" = '{file_to_delete}'
        """
        return self._execute_dml(delete_query, "DELETE")
    
    def _check_and_fix_duplicates(self, vendor_number: str) -> bool:
        """
        Check for true duplicates (same FILE value) and deduplicate if found
        
        When duplicates are found:
        1. Merge all duplicate entries into one (prefer non-null values)
        2. Delete all entries with that FILE value
        3. Re-insert the merged entry
        
        Note: We don't update first then delete - we delete all and re-insert to avoid
        transaction issues and ensure clean state.
        """
        logger.info(f"Checking for duplicates for vendor {vendor_number}")
        session = self.get_session()
        
        try:
            # Refresh vendor combinations to get current state
            vendor_combinations = self.get_vendor_combinations(vendor_number)
            logger.info(f"Found {len(vendor_combinations)} entry/entries for vendor {vendor_number}")
            
            # Group by FILE value to find duplicates
            file_groups = {}
            for entry in vendor_combinations:
                file_value = entry.get('FILE')
                if file_value not in file_groups:
                    file_groups[file_value] = []
                file_groups[file_value].append(entry)
            
            logger.info(f"File groups: {[(k, len(v)) for k, v in file_groups.items()]}")
            
            # Check for duplicates (same FILE value)
            for file_value, entries in file_groups.items():
                if len(entries) > 1:
                    logger.warning(f"Found {len(entries)} duplicate entries with FILE={file_value} for vendor {vendor_number}")
                    
                    # Merge duplicates - prefer non-null values, or Tier2 if both exist
                    merged_entry = entries[0].copy()
                    for entry in entries[1:]:
                        for field, value in entry.items():
                            if field == 'FILE' or field == 'Vendor Number':
                                continue
                            # Prefer non-null value, or keep existing if both are non-null
                            if merged_entry.get(field) is None or str(merged_entry.get(field)).strip() == '':
                                if value is not None and str(value).strip() != '':
                                    merged_entry[field] = value
                    
                    # Ensure Vendor Number and FILE are set
                    merged_entry['Vendor Number'] = vendor_number
                    merged_entry['FILE'] = file_value
                    
                    logger.info(f"Merged entry prepared for FILE={file_value}")
                    
                    # Delete ALL entries with this FILE value first
                    delete_query = f"""
                        DELETE FROM {self.table_name}
                        WHERE "Vendor Number" = '{vendor_number}' AND "FILE" = '{file_value}'
                    """
                    if not self._execute_dml(delete_query, "DELETE"):
                        logger.error(f"Failed to delete duplicate entries for FILE={file_value}")
                        return False
                    
                    # Verify deletion
                    verify_delete = f"""
                        SELECT COUNT(*) as row_count
                        FROM {self.table_name}
                        WHERE "Vendor Number" = '{vendor_number}' AND "FILE" = '{file_value}'
                    """
                    verify_result = session.sql(verify_delete).collect()
                    remaining_count = verify_result[0]['ROW_COUNT'] if verify_result else -1
                    logger.info(f"After DELETE, {remaining_count} row(s) remain with FILE='{file_value}'")
                    
                    # Commit the delete before insert
                    try:
                        session.sql("COMMIT").collect()
                    except Exception:
                        pass
                    
                    # Re-insert the merged entry
                    if not self._insert_single_vendor(merged_entry):
                        logger.error(f"Failed to re-insert merged entry for FILE={file_value}")
                        return False
                    
                    # Verify insertion
                    verify_insert = f"""
                        SELECT COUNT(*) as row_count
                        FROM {self.table_name}
                        WHERE "Vendor Number" = '{vendor_number}' AND "FILE" = '{file_value}'
                    """
                    verify_result = session.sql(verify_insert).collect()
                    inserted_count = verify_result[0]['ROW_COUNT'] if verify_result else 0
                    logger.info(f"After INSERT, {inserted_count} row(s) exist with FILE='{file_value}'")
                    
                    if inserted_count == 0:
                        logger.error(f"INSERT did not create any rows! Vendor {vendor_number}, FILE {file_value}")
                        return False
                    
                    # Final commit
                    try:
                        session.sql("COMMIT").collect()
                    except Exception:
                        pass
                    
                    logger.info(f"Successfully deduplicated {len(entries)} entries with FILE={file_value}")
                    return True
            
            logger.info("No duplicates found")
            return True  # No duplicates found
            
        except Exception as e:
            logger.error(f"Error checking for duplicates: {e}")
            return False
    
    def _check_and_fix_missing_secondary(self, vendor_number: str) -> bool:
        """
        Check if Tier2 exists but 6Months doesn't and create missing entry.
        
        CRITICAL: This function ONLY creates 6Months when Tier2 exists.
        It does NOT create Tier2 when only 6Months exists, because standalone
        6Months entries are valid. Dual entries should only be created when
        explicitly changing TO Tier2.
        """
        logger.info(f"Checking for missing secondary entry for vendor {vendor_number}")
        
        try:
            vendor_combinations = self.get_vendor_combinations(vendor_number)
            tier2_entry = next((v for v in vendor_combinations if v.get('FILE') == 'Tier2'), None)
            sixmonths_entry = next((v for v in vendor_combinations if v.get('FILE') == '6Months'), None)
            
            # ONLY check if Tier2 exists but 6Months doesn't
            # Do NOT create Tier2 when only 6Months exists - standalone 6Months is valid
            if tier2_entry and not sixmonths_entry:
                logger.info(f"Tier2 exists but 6Months missing - creating 6Months entry with copied data")
                sixmonths_data = tier2_entry.copy()
                sixmonths_data['FILE'] = '6Months'
                return self._insert_single_vendor(sixmonths_data)
            
            # If 6Months exists but Tier2 doesn't, that's OK - standalone 6Months is valid
            # Do NOT auto-create Tier2 here
            
            return True  # Both exist, or only 6Months exists (both OK), or only Tier2 exists (we fixed it)
            
        except Exception as e:
            logger.error(f"Error checking for missing secondary: {e}")
            return False
    
    def _check_and_fix_unsynced_dual(self, vendor_number: str) -> bool:
        """Check if Tier2 and 6Months exist but are out of sync, and sync them"""
        logger.info(f"Checking for unsynced dual entries for vendor {vendor_number}")
        
        try:
            vendor_combinations = self.get_vendor_combinations(vendor_number)
            tier2_entry = next((v for v in vendor_combinations if v.get('FILE') == 'Tier2'), None)
            sixmonths_entry = next((v for v in vendor_combinations if v.get('FILE') == '6Months'), None)
            
            # Both must exist to be unsynced
            if not tier2_entry or not sixmonths_entry:
                return True  # Not a dual entry, nothing to sync
            
            # Check for mismatches (excluding FILE field)
            mismatches = []
            merged_data = {}
            all_fields = set(tier2_entry.keys()) | set(sixmonths_entry.keys())
            
            for field in all_fields:
                if field == 'FILE':
                    continue
                tier2_value = tier2_entry.get(field)
                sixmonths_value = sixmonths_entry.get(field)
                
                # Normalize for comparison
                tier2_str = str(tier2_value or '').strip()
                sixmonths_str = str(sixmonths_value or '').strip()
                
                if tier2_str != sixmonths_str:
                    mismatches.append(field)
                    # Prefer non-null value, or Tier2 if both exist
                    if tier2_value is not None and tier2_str != '':
                        merged_data[field] = tier2_value
                    elif sixmonths_value is not None and sixmonths_str != '':
                        merged_data[field] = sixmonths_value
                    else:
                        merged_data[field] = tier2_value
                else:
                    merged_data[field] = tier2_value
            
            # If mismatches found, sync both entries
            if mismatches:
                logger.info(f"Found {len(mismatches)} mismatched fields: {', '.join(mismatches)}")
                
                # For email fields, normalize and deduplicate
                email_fields = ['Vendor Contacts', 'CM_Email', 'CM Manager_Email', 'SP_Email', 'SP Manager_Email', 'OVERRIDE_EMAIL']
                for field in email_fields:
                    if field in merged_data and merged_data[field]:
                        try:
                            import streamlit as st
                            if hasattr(st, 'session_state') and hasattr(st.session_state, 'vendor_processor'):
                                result = st.session_state.vendor_processor.email_validator.validate_email_list(str(merged_data[field]))
                                merged_data[field] = result.normalized_value
                            else:
                                # Fallback: basic normalization
                                emails = str(merged_data[field]).split(';')
                                normalized_emails = [e.strip().lower() for e in emails if e.strip()]
                                merged_data[field] = ';'.join(sorted(set(normalized_emails)))
                        except Exception as e:
                            logger.warning(f"Could not normalize email field {field}: {e}")
                
                # Sync both entries
                sync_updates = {k: v for k, v in merged_data.items() if k not in ['Vendor Number', 'FILE']}
                return self._update_dual_entry_vendor(vendor_number, 'Tier2', sync_updates)
            
            return True  # No mismatches, already in sync
            
        except Exception as e:
            logger.error(f"Error checking for unsynced dual entries: {e}")
            return False
    
    def insert_vendor(self, vendor_data: Dict[str, Any]) -> bool:
        """Insert a new vendor record"""
        # Handle dual entry creation (Tier2 creates both Tier2 and 6Months)
        if vendor_data.get('FILE') == 'Tier2':
            return self._insert_dual_entry_vendor(vendor_data)
        
        return self._insert_single_vendor(vendor_data)
    
    def _insert_dual_entry_vendor(self, vendor_data: Dict[str, Any]) -> bool:
        """Insert both Tier2 and 6Months entries for a new dual entry vendor"""
        logger.info(f"Creating dual entry vendor {vendor_data.get('Vendor Number', 'Unknown')}")
        
        import streamlit as st
        tier2_data, sixmonths_data = st.session_state.vendor_processor.create_dual_entry_data(vendor_data)
        
        return (self._insert_single_vendor(tier2_data) and self._insert_single_vendor(sixmonths_data))
    
    def _insert_single_vendor(self, vendor_data: Dict[str, Any]) -> bool:
        """Insert a single vendor record"""
        session = self.get_session()
        
        # Build INSERT query with proper NULL handling
        columns = []
        values = []
        
        for col, value in vendor_data.items():
            columns.append(f'"{col}"')
            if value is None or value == '' or str(value).strip() == '':
                values.append('NULL')
            else:
                values.append(self._escape_sql_string(value))
        
        column_names = ', '.join(columns)
        value_list = ', '.join(values)
        
        query = f"""
            INSERT INTO {self.table_name} ({column_names})
            VALUES ({value_list})
        """
        
        return self._execute_dml(query, "INSERT")
    
    def _update_dual_entry_vendor(self, vendor_number: str, file_value: str, updates: Dict[str, Any]) -> bool:
        """Update both Tier2 and 6Months entries for a dual entry vendor"""
        logger.info(f"Updating dual entry vendor {vendor_number} - synchronizing both Tier2 and 6Months")
        
        session = self.get_session()
        
        # Check for both entries
        check_query = f"""
            SELECT "FILE" FROM {self.table_name}
            WHERE "Vendor Number" = '{vendor_number}' AND "FILE" IN ('Tier2', '6Months')
            ORDER BY "FILE"
        """
        
        try:
            existing_files = session.sql(check_query).collect()
            existing_file_values = [row[0] for row in existing_files] if existing_files else []
            
            if 'Tier2' not in existing_file_values or '6Months' not in existing_file_values:
                logger.warning(f"Dual entry vendor {vendor_number} missing one or both entries. Falling back to single entry update.")
                return self._update_single_vendor(vendor_number, file_value, updates)
            
            # Update both entries with the same data (except FILE field)
            return (self._update_single_vendor(vendor_number, 'Tier2', updates) and 
                    self._update_single_vendor(vendor_number, '6Months', updates))
                
        except Exception as e:
            logger.error(f"Failed to update dual entry vendor {vendor_number}: {e}")
            return False
    
    def _update_single_vendor(self, vendor_number: str, file_value: str, updates: Dict[str, Any]) -> bool:
        """Update a single vendor entry (used by both single and dual entry updates)"""
        if not updates:
            return True
        
        session = self.get_session()
        
        # Build dynamic UPDATE query
        set_clauses = []
        
        for field, value in updates.items():
            if field == 'FILE':
                continue
                
            # Handle date fields
            if field in ['Soft Chargeback Effective Date', 'Hard Chargeback Effective Date']:
                if value and isinstance(value, str) and value.startswith('datetime.date'):
                    continue
                elif value and isinstance(value, str) and value != 'None':
                    try:
                        from datetime import datetime
                        parsed_date = datetime.strptime(value, '%Y-%m-%d').date()
                        value = parsed_date.strftime('%Y-%m-%d')
                    except:
                        logger.warning(f"Could not parse date field {field}: {value}")
                        continue
            
            # Handle NULL values
            if value is None or value == '' or str(value).strip() == '':
                escaped_value = 'NULL'
            else:
                escaped_value = self._escape_sql_string(value)
            
            set_clauses.append(f'"{field}" = {escaped_value}')
        
        if not set_clauses:
            return True  # No changes to make
        
        query = f"""
            UPDATE {self.table_name}
            SET {', '.join(set_clauses)}
            WHERE "Vendor Number" = '{vendor_number}' AND "FILE" = '{file_value}'
        """
        
        return self._execute_dml(query, "UPDATE")
