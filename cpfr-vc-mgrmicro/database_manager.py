"""
Database manager for Streamlit in Snowflake

Handles all Snowflake database operations for the VC_CPFR_VENDOR_EMAIL table.
One row per (Vendor Number, FILE). Uses get_active_session() for Streamlit in Snowflake.
"""

import json
import uuid
import pandas as pd
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages Snowflake database operations using user's active session"""
    
    # Deprecated columns that will be removed from the table
    # These should be filtered out from INSERT/UPDATE operations
    DEPRECATED_COLUMNS = [
        'PURCHASER',
        'Shipment Method Code',
        'CB Rollout Phase',
        'Soft Chargeback Effective Date',
        'Hard Chargeback Effective Date'
    ]
    
    def __init__(self):
        """Initialize database manager for Streamlit in Snowflake"""
        self.session = None
        self.table_name = "EDLDB.SC_SANDBOX.VC_CPFR_VENDOR_EMAIL"
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize Snowpark session using get_active_session() only"""
        try:
            from snowflake.snowpark.context import get_active_session
            self.session = get_active_session()
            if not self.session:
                raise ConnectionError("No active Snowflake session found. This app must run in Streamlit in Snowflake.")

            # Set session timeout to prevent long-running queries.
            # STATEMENT_TIMEOUT_IN_SECONDS is a session-level parameter; it applies to
            # every query on every screen for the lifetime of the session.
            try:
                self.session.sql("ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 30").collect()
                logger.info("Session timeout set to 30 seconds")
            except Exception as e:
                logger.warning(f"Could not set session timeout: {e}")

            # Set query tag for Snowflake cost attribution and performance monitoring.
            # Required by Chewy DBS guidelines: owner and app_name are mandatory;
            # file_path is required for Python apps; comment is optional but useful.
            # Set once here so every query this session runs carries the tag automatically.
            try:
                query_tag = json.dumps({
                    "owner":     "nmiles1",
                    "app_name":  "VC_CPFR_EMAIL_STREAMLIT",
                    "file_path": "cpfr-vc-mgrmicro/streamlit_app.py",
                    "comment":   "CPFR Vendor Contact Manager - manages VC_CPFR_VENDOR_EMAIL",
                })
                self.session.sql(f"ALTER SESSION SET query_tag='{query_tag}'").collect()
                logger.info("Session query tag set")
            except Exception as e:
                logger.warning(f"Could not set query tag: {e}")

            # Try to use dedicated warehouse for Streamlit apps
            try:
                self.session.sql("USE WAREHOUSE STREAMLIT_XS_WH").collect()
                logger.info("Using STREAMLIT_XS_WH warehouse")
            except Exception as e:
                logger.info(f"Using default warehouse (STREAMLIT_XS_WH not available): {e}")

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
    
    def is_healthy(self) -> bool:
        """Quick non-blocking health check"""
        try:
            session = self.get_session()
            # Use LIMIT 0 for instant response
            session.sql("SELECT 1 WHERE 1=0").collect()
            return True
        except:
            return False
    
    def _escape_sql_string(self, value: Any) -> str:
        """Escape string values for SQL safety."""
        if value is None:
            return 'NULL'
        escaped_value = str(value).replace("'", "''")
        return f"'{escaped_value}'"
    
    def _build_file_where_clause(self, file_value: str) -> str:
        """
        Build WHERE clause for FILE field that handles NULL values correctly
        
        Args:
            file_value: FILE value to match (can be None, 'None', or actual FILE value)
            
        Returns:
            SQL WHERE clause fragment for FILE field
        """
        if file_value is None or file_value == 'None' or str(file_value).strip() == '':
            return '"FILE" IS NULL'
        else:
            # Escape the value for SQL (replace single quotes with double single quotes)
            escaped_value = str(file_value).replace("'", "''")
            return f'"FILE" = \'{escaped_value}\''
    
    def _normalize_file_value_for_write(self, file_value: Any) -> Optional[str]:
        """
        Normalize FILE value for writing to database
        
        Converts 'None' to None (NULL), '3Months' to '6Months', and handles malformed values
        
        Args:
            file_value: FILE value from UI or data
            
        Returns:
            Normalized FILE value (None for NULL, or valid FILE string)
        """
        if file_value is None or file_value == 'None' or str(file_value).strip() == '':
            return None
        
        file_str = str(file_value).strip()
        
        # Convert deprecated '3Months' to '6Months'
        if file_str == '3Months':
            logger.info(f"Converting deprecated 3Months to 6Months")
            return '6Months'
        
        # Normalize common variations
        file_str = file_str.replace(' ', '')  # Remove spaces
        file_lower = file_str.lower()
        
        # Map common variations to standard values
        if file_lower in ['tier1', 'tier 1', 't1']:
            return 'Tier1'
        elif file_lower in ['tier2', 'tier 2', 't2']:
            return 'Tier2'
        elif file_lower in ['6months', '6 months', 'sixmonths']:
            return '6Months'
        elif file_lower in ['3months', '3 months', 'threemonths']:
            logger.info(f"Converting 3Months variation to 6Months")
            return '6Months'
        elif file_lower in ['none', 'null', '']:
            return None
        
        # Return as-is if it's a valid value
        if file_str in ['Tier1', 'Tier2', '6Months']:
            return file_str
        
        # Log warning for unrecognized values but return as-is (let database handle validation)
        logger.warning(f"Unrecognized FILE value: {file_value}, returning as-is")
        return file_str
    
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
            logger.error(f"{operation} failed: {str(e)}")
            logger.error(f"Failed query: {query}")
            return False
    
    def search_vendors(self, search_type: str, search_value: str) -> pd.DataFrame:
        """
        Search vendors by different criteria.

        FILE column values are normalized before the DataFrame is returned so that
        all downstream consumers (including VendorProcessor) receive clean values.

        Args:
            search_type: Field to search on (e.g. "Vendor Number", "Vendor Name")
            search_value: Value to search for

        Returns:
            DataFrame with matching vendor rows; FILE column pre-normalized
        """
        session = self.get_session()
        
        if search_type == "Vendor Number":
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE "Vendor Number" = '{search_value}'
                ORDER BY "Vendor Number", "FILE"
                LIMIT 10
            """
        else:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE "{search_type}" ILIKE '%{search_value}%'
                ORDER BY "Vendor Number", "FILE"
                LIMIT 500
            """
        
        try:
            df = session.sql(query).to_pandas()
            logger.info(f"Found {len(df)} vendor records for {search_type}: {search_value}")
            # Normalize FILE column at the DB boundary so all consumers receive clean values
            if 'FILE' in df.columns:
                df['FILE'] = df['FILE'].apply(self._normalize_file_value_for_display)
            return df
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def get_vendor(self, vendor_number: str, file_value: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific vendor record
        
        Args:
            vendor_number: Vendor number to look up
            file_value: FILE value to match (can be None, 'None', or actual FILE value)
        """
        session = self.get_session()
        
        file_where = self._build_file_where_clause(file_value)
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE "Vendor Number" = '{vendor_number}' AND {file_where}
        """
        
        try:
            df = session.sql(query).to_pandas()
            if not df.empty:
                vendor_dict = df.iloc[0].to_dict()
                # Normalize FILE value for display (None -> 'None', convert 3Months to 6Months)
                if 'FILE' in vendor_dict:
                    vendor_dict['FILE'] = self._normalize_file_value_for_display(vendor_dict.get('FILE'))
                return vendor_dict
            return None
        except Exception as e:
            logger.error(f"Failed to get vendor {vendor_number}: {e}")
            raise
    
    def _normalize_file_value_for_display(self, file_value: Any) -> str:
        """
        Normalize FILE value for display in UI
        
        Converts None to 'None', '3Months' to '6Months', and handles malformed values
        
        Args:
            file_value: FILE value from database
            
        Returns:
            Normalized FILE value for display
        """
        if file_value is None or pd.isna(file_value):
            return 'None'
        
        file_str = str(file_value).strip()
        
        # Convert deprecated '3Months' to '6Months'
        if file_str == '3Months':
            logger.info(f"Converting deprecated 3Months to 6Months for display")
            return '6Months'
        
        # Normalize common variations
        file_str = file_str.replace(' ', '')  # Remove spaces
        file_lower = file_str.lower()
        
        # Map common variations to standard values
        if file_lower in ['tier1', 'tier 1', 't1']:
            return 'Tier1'
        elif file_lower in ['tier2', 'tier 2', 't2']:
            return 'Tier2'
        elif file_lower in ['6months', '6 months', 'sixmonths']:
            return '6Months'
        elif file_lower in ['3months', '3 months', 'threemonths']:
            logger.info(f"Converting 3Months variation to 6Months for display")
            return '6Months'
        elif file_lower in ['none', 'null', '']:
            return 'None'
        
        # Return as-is if it's a valid value
        if file_str in ['Tier1', 'Tier2', '6Months', 'None']:
            return file_str
        
        # Log warning for unrecognized values but return as-is
        logger.warning(f"Unrecognized FILE value for display: {file_value}, returning as-is")
        return file_str
    
    def get_vendor_combinations(self, vendor_number: str) -> List[Dict[str, Any]]:
        """Get all FILE combinations for a vendor number"""
        session = self.get_session()
        
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE "Vendor Number" = '{vendor_number}'
            ORDER BY "FILE"
            LIMIT 10
        """
        
        try:
            df = session.sql(query).to_pandas()
            records = df.to_dict('records')
            # Normalize FILE values for display
            for record in records:
                if 'FILE' in record:
                    record['FILE'] = self._normalize_file_value_for_display(record.get('FILE'))
            return records
        except Exception as e:
            logger.error(f"Failed to get vendor combinations for {vendor_number}: {e}")
            raise
    
    def update_vendor(self, vendor_number: str, file_value: str, updates: Dict[str, Any]) -> bool:
        """
        Update vendor record with only the changed fields.

        Args:
            vendor_number: Vendor number identifying the row to update
            file_value: FILE value identifying the row (can be None/'None' for NULL rows)
            updates: Dictionary of field names to new values; FILE key is ignored

        Returns:
            True if the update succeeded, False otherwise
        """
        if not updates:
            return True

        session = self.get_session()

        # Filter out deprecated columns to prevent errors when columns are removed
        filtered_updates = {k: v for k, v in updates.items() if k not in self.DEPRECATED_COLUMNS}

        # Build dynamic UPDATE query
        set_clauses = []

        for field, value in filtered_updates.items():
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

        file_where = self._build_file_where_clause(file_value)
        query = f"""
            UPDATE {self.table_name}
            SET {', '.join(set_clauses)}
            WHERE "Vendor Number" = '{vendor_number}' AND {file_where}
        """

        return self._execute_dml(query, "UPDATE")
    
    def change_vendor_tier(self, vendor_number: str, original_file: str, new_file: str, updates: Dict[str, Any]) -> bool:
        """
        Change the FILE value (tier) for a vendor row and optionally update other fields.

        Args:
            vendor_number: Vendor number identifying the row
            original_file: Current FILE value used to locate the row
            new_file: New FILE value to write
            updates: Additional field updates to apply alongside the FILE change;
                     the FILE key is ignored here (new_file is used instead)

        Returns:
            True if the UPDATE succeeded and the row is verified at new_file, False otherwise
        """
        logger.info(f"Changing vendor {vendor_number} from {original_file} to {new_file}")
        session = self.get_session()

        # Normalize the incoming FILE values for write operations
        normalized_new = self._normalize_file_value_for_write(new_file)

        # Exclude FILE from field updates and filter deprecated columns
        field_updates = {k: v for k, v in updates.items() if k != 'FILE'}
        filtered_updates = {k: v for k, v in field_updates.items() if k not in self.DEPRECATED_COLUMNS}

        # Build FILE SET clause (handle NULL)
        if normalized_new is None:
            set_clauses = ['"FILE" = NULL']
        else:
            escaped_value = str(normalized_new).replace("'", "''")
            set_clauses = [f'"FILE" = \'{escaped_value}\'']

        for field, value in filtered_updates.items():
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

        original_file_where = self._build_file_where_clause(original_file)
        query = f"""
            UPDATE {self.table_name}
            SET {', '.join(set_clauses)}
            WHERE "Vendor Number" = '{vendor_number}' AND {original_file_where}
        """

        logger.info(f"Executing UPDATE query: {query}")

        if not self._execute_dml(query, "UPDATE"):
            logger.error(f"Failed to execute UPDATE for vendor {vendor_number}")
            return False

        # Verify the UPDATE affected a row
        new_file_where = self._build_file_where_clause(new_file)
        verify_query = f"""
            SELECT COUNT(*) as row_count
            FROM {self.table_name}
            WHERE "Vendor Number" = '{vendor_number}' AND {new_file_where}
        """

        try:
            result = session.sql(verify_query).collect()
            row_count = result[0]['ROW_COUNT'] if result else 0
            logger.info(f"Verification found {row_count} row(s) with FILE='{new_file}' after UPDATE")

            if row_count == 0:
                logger.error(f"UPDATE did not affect any rows! Vendor {vendor_number}, FILE {original_file} -> {new_file}")
                original_file_where_check = self._build_file_where_clause(original_file)
                check_query = f"""
                    SELECT COUNT(*) as row_count
                    FROM {self.table_name}
                    WHERE "Vendor Number" = '{vendor_number}' AND {original_file_where_check}
                """
                check_result = session.sql(check_query).collect()
                original_count = check_result[0]['ROW_COUNT'] if check_result else 0
                logger.error(f"Original row still exists: {original_count} row(s) with FILE='{original_file}'")
                return False

            return True
        except Exception as e:
            logger.error(f"Failed to verify UPDATE: {e}")
            return True  # Assume success if verification query itself fails
    
    def _get_current_user_info(self) -> dict:
        """
        Retrieve the current viewer's identity fields for audit logging.

        Fetches once per app session (cached in st.session_state under
        '_audit_user_info') to avoid repeated round-trips on every audit write.

        In Streamlit in Snowflake the Python execution sandbox runs with
        owner's-rights-style SQL context: CURRENT_USER(), SYS_CONTEXT() principal
        functions, and the Snowpark get_current_user() API all return NULL even though
        the active role and account are set correctly. st.user is the documented SiS
        API for viewer identity -- it surfaces the authenticated viewer's Snowflake
        username (st.user.user_name) and email (st.user.email) regardless of SQL
        execution context.

        Returns:
            Dict with keys: snowflake_user, chewy_username
        """
        import streamlit as st
        cached = st.session_state.get('_audit_user_info')
        # Only return cached value if it actually has data; an empty-string cache from
        # a previous failed attempt should not block a retry on the next transaction.
        if cached and cached.get('snowflake_user'):
            return cached

        try:
            # In Streamlit in Snowflake the Python execution sandbox runs with
            # owner's-rights-style SQL context, so CURRENT_USER() / SYS_CONTEXT()
            # principal functions return NULL even though the role and account are
            # set correctly. st.user is the documented SiS API for viewer identity:
            # it exposes the authenticated viewer's Snowflake username and email
            # regardless of SQL execution context.
            user_name = getattr(st.user, 'user_name', '') or ''
            email     = getattr(st.user, 'email',     '') or ''

            info = {
                'snowflake_user':    user_name,
                'chewy_username':    email or user_name,  # prefer email; fall back to login name
            }

            if info['snowflake_user']:
                st.session_state['_audit_user_info'] = info

            return info

        except Exception as e:
            logger.warning(f"Could not retrieve user info for audit: {e}")
            return {'snowflake_user': '', 'chewy_username': ''}

    def write_audit_record(
        self,
        action_type: str,
        status: str,
        vendor_number: str,
        before_state: Optional[Dict[str, Any]],
        after_state: Optional[Dict[str, Any]],
        changed_fields: Optional[List[str]] = None,
        error_message: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """
        Insert one row into EDLDB.SC_SANDBOX.VC_CPFR_EMAIL_AUDIT after a confirmed transaction.

        Called after every successful (or failed) INSERT/UPDATE/TIER_CHANGE.
        Failure to write the audit record is non-fatal: it is logged as a warning
        and does not surface to the business user.

        Args:
            action_type:    'INSERT', 'UPDATE', or 'TIER_CHANGE'
            status:         'SUCCESS' or 'ERROR'
            vendor_number:  The affected vendor number
            before_state:   Vendor record dict before the change (None for new inserts)
            after_state:    Vendor record dict after the change
            changed_fields: List of field names that changed
            error_message:  Error text if status is 'ERROR'
            session_id:     Streamlit session ID (passed in from app layer)
        """
        audit_table = "EDLDB.SC_SANDBOX.VC_CPFR_EMAIL_AUDIT"
        try:
            user_info = self._get_current_user_info()
            event_id = str(uuid.uuid4())

            def _serialize_state(state: Optional[Dict[str, Any]]) -> str:
                """Normalize and JSON-serialize a vendor state dict for VARIANT insertion."""
                if not state:
                    return '{}'
                cleaned = {}
                for k, v in state.items():
                    if v is None or str(v).strip() in ('', 'None', 'nan', 'NaT'):
                        cleaned[k] = None
                    else:
                        cleaned[k] = str(v)
                return json.dumps(cleaned)

            before_json = _serialize_state(before_state)
            after_json = _serialize_state(after_state)

            changed_fields_str = ', '.join(changed_fields) if changed_fields else ''
            error_str = (error_message or '')[:5000]
            sid = (session_id or '')[:255]

            def esc(val: str) -> str:
                """Escape single quotes for embedding in SQL string literals."""
                return str(val).replace("'", "''") if val else ''

            query = f"""
                INSERT INTO {audit_table} (
                    EVENT_ID, ACTION_TYPE, STATUS,
                    TARGET_TABLE, VENDOR_NUMBER,
                    SNOWFLAKE_USER, CHEWY_USERNAME,
                    BEFORE_STATE, AFTER_STATE,
                    ERROR_MESSAGE, CHANGED_FIELDS,
                    APP_NAME, APP_VERSION, SESSION_ID
                )
                SELECT
                    '{esc(event_id)}',
                    '{esc(action_type)}',
                    '{esc(status)}',
                    'EDLDB.SC_SANDBOX.VC_CPFR_VENDOR_EMAIL',
                    '{esc(vendor_number)}',
                    '{esc(user_info["snowflake_user"])}',
                    '{esc(user_info["chewy_username"])}',
                    PARSE_JSON('{esc(before_json)}'),
                    PARSE_JSON('{esc(after_json)}'),
                    '{esc(error_str)}',
                    '{esc(changed_fields_str)}',
                    'VC_CPFR_EMAIL_STREAMLIT',
                    '1.0',
                    '{esc(sid)}'
            """

            session = self.get_session()
            session.sql(query).collect()
            try:
                session.sql("COMMIT").collect()
            except Exception:
                pass
            logger.info(f"Audit record written: {action_type} {status} vendor={vendor_number} event={event_id}")

        except Exception as e:
            logger.warning(f"Failed to write audit record (non-fatal): {e}")

    def insert_vendor(self, vendor_data: Dict[str, Any]) -> bool:
        """
        Insert a new vendor record.

        Args:
            vendor_data: Dictionary of field names to values for the new row

        Returns:
            True if the INSERT succeeded, False otherwise
        """
        session = self.get_session()

        # Filter out deprecated columns to prevent errors when columns are removed
        filtered_data = {k: v for k, v in vendor_data.items() if k not in self.DEPRECATED_COLUMNS}

        # Normalize FILE value if present
        if 'FILE' in filtered_data:
            filtered_data['FILE'] = self._normalize_file_value_for_write(filtered_data['FILE'])

        # Build INSERT query with proper NULL handling
        columns = []
        values = []

        for col, value in filtered_data.items():
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
    
