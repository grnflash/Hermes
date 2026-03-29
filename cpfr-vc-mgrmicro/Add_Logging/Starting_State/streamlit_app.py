"""
CPFR Vendor Contact Streamlit Manager - For Streamlit in Snowflake

Main Streamlit application for managing vendor contact information.
One row per (Vendor Number, FILE); no Tier2+6Months dual-entry logic.
Duplicate rows for the same vendor are shown with labels; cleanup is handled in the database.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any
import logging

from database_manager import DatabaseManager
from vendor_processor import VendorProcessor, VendorSearchResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Field name mapping: database field names -> display labels
FIELD_DISPLAY_NAMES = {
    'Parent Vendor': 'Parent Company',
    'CM_Email': 'Category Manager Email',
    'CM Manager_Email': 'Category Merch AD Email',
    'SP_Email': 'In-Stock Manager Email',
    'SP Manager_Email': 'In-Stock AD Email',
    'OVERRIDE_EMAIL': 'Override Email'
}

def get_field_display_name(field_name: str) -> str:
    """Get display name for a field, or return original if no mapping exists"""
    return FIELD_DISPLAY_NAMES.get(field_name, field_name)

# CRITICAL: Check for reset flag FIRST, before any other initialization
# This allows us to force a complete reset by setting this flag
if st.session_state.get('_force_reset', False):
    # Clear everything except essential objects
    db_manager = st.session_state.get('db_manager')
    vendor_processor = st.session_state.get('vendor_processor')

    # Get all keys and delete them
    keys_to_delete = [key for key in st.session_state.keys() if key not in ['db_manager', 'vendor_processor']]
    for key in keys_to_delete:
        del st.session_state[key]

    # Restore essential objects
    if db_manager:
        st.session_state.db_manager = db_manager
    if vendor_processor:
        st.session_state.vendor_processor = vendor_processor

    # Unset the reset flag
    if '_force_reset' in st.session_state:
        del st.session_state['_force_reset']

    # Force immediate rerun to apply the reset
    st.rerun()

# Initialize session state - matching ReferenceApp pattern exactly
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

if 'vendor_processor' not in st.session_state:
    st.session_state.vendor_processor = VendorProcessor()

if 'current_mode' not in st.session_state:
    st.session_state.current_mode = 'search'  # 'search', 'results', 'edit', 'new', 'receipt'

if 'search_results' not in st.session_state:
    st.session_state.search_results = None

if 'selected_vendor' not in st.session_state:
    st.session_state.selected_vendor = None

if 'search_type' not in st.session_state:
    st.session_state.search_type = 'Vendor Number'

if 'search_value' not in st.session_state:
    st.session_state.search_value = ''

# UI state for tracking file changes across form submit -> confirm flow
if 'tier_change_receipt' not in st.session_state:
    st.session_state.tier_change_receipt = None  # Stores receipt data

# Additional state variables not in ReferenceApp - but needed for functionality
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

if 'pending_changes' not in st.session_state:
    st.session_state.pending_changes = None

if 'original_vendor' not in st.session_state:
    st.session_state.original_vendor = None

if 'file_changing' not in st.session_state:
    st.session_state.file_changing = False

def main():
    """Main application entry point"""
    # CRITICAL: st.set_page_config() MUST be the first Streamlit command
    st.set_page_config(
        page_title="CPFR and VC | Vendor Configuration Manager",
        page_icon="📧",
        layout="wide"
        # initial_sidebar_state="collapsed"  # REMOVED - ReferenceApp doesn't have this
    )

    # REMOVED - This was causing corruption by modifying state during initialization
    # validate_session_state() should NEVER be called here
    # If validation is needed, call it during user interactions, not initialization

    st.title("📧 CPFR VC Vendor Info Manager")

    # Verify connection (silently) - cached to avoid long-running queries
    if 'connection_verified' not in st.session_state:
        try:
            session = st.session_state.db_manager.get_session()
            try:
                user_info = session.sql("SELECT CURRENT_USER(), CURRENT_ROLE()").collect()
                logger.info(f"User: {user_info[0][0] if user_info else 'Unknown'}, Role: {user_info[0][1] if user_info else 'Unknown'}")
                st.session_state.connection_verified = True
            except Exception as user_error:
                logger.warning(f"Could not get user context: {user_error}")
                st.session_state.connection_verified = False
        except Exception as e:
            st.error(f"❌ Failed to connect to Snowflake: {e}")
            st.error("This app must be run in Streamlit in Snowflake (under Projects).")
            return
    elif not st.session_state.get('connection_verified', False):
        # Connection failed previously, show error
        st.error("❌ Failed to connect to Snowflake")
        st.error("This app must be run in Streamlit in Snowflake (under Projects).")
        return
    
    # Main state machine
    if st.session_state.current_mode == 'search':
        show_search_screen()
    elif st.session_state.current_mode == 'results':
        show_results_screen()
    elif st.session_state.current_mode == 'edit':
        show_edit_screen()
    elif st.session_state.current_mode == 'new':
        show_new_entry_screen()
    elif st.session_state.current_mode == 'receipt':
        show_receipt_screen()
    else:
        st.error("Invalid application state")
        st.session_state.current_mode = 'search'

def show_search_screen():
    """Display vendor search interface"""
    st.header("🔍 Search Vendors")
    
    # Quick start guidance
    st.info("""💡 **NOTE:**

- Vendors are tracked by Vendor Number, or you may also search by Vendor Name/Parent/Company.
- If no result is found for a Vendor Number, you can create a new entry.
- Tier 1 vendors should be searched by Parent Company""")
    
    # Search type selection - 50/50 split (expander appears auxiliary due to inherent visual differences)
    col1, col2 = st.columns([1, 1])
    with col1:
        search_type_display = st.selectbox(
            "",
            ["Vendor Number", "Vendor Name", "Parent Company", "Vendor Contacts"],
            key="search_type_input",
            label_visibility="collapsed"
        )
        # Map display name back to database field name
        search_type = "Parent Vendor" if search_type_display == "Parent Company" else search_type_display
    with col2:
        # Top-align expander now that label is removed - styled to look auxiliary like info box
        with st.expander("ℹ️ About Search Types", expanded=False):
            st.markdown("""
            - **Vendor Number**: Exact match required
            - **Vendor Name**: Partial match (case-insensitive)
            - **Parent Company**: Partial match
            - **Vendor Contacts**: Partial match (searches email addresses)
            """)
    
    # Search input
    search_value = st.text_input(
        f"Enter {search_type_display.lower()}:",
        help="Enter partial text for name/company searches, exact number for vendor number",
        key="search_value_input"
    )
    
    # Search button
    search_clicked = st.button("🔍 Search", type="primary")
    
    # Handle search
    if search_clicked and search_value:
        perform_search(search_type, search_value)
    
    # Show create button only after search with no results
    if search_type == "Vendor Number":
        # Check if we just performed a search with no results
        if (st.session_state.search_performed and 
            st.session_state.search_results and 
            len(st.session_state.search_results.vendors) == 0):
            
            st.success("✅ No vendor found - you can create a new entry")
            new_entry_clicked = st.button("➕ Create New Entry", type="secondary")
            if new_entry_clicked:
                st.session_state.search_value = search_value
                st.session_state.current_mode = 'new'
                # Clear search state before transitioning
                st.session_state.search_performed = False
                st.session_state.search_results = None
                st.rerun()
        else:
            # Show helpful message
            if search_value:
                st.info("💡 Click 'Search' to check if this vendor already exists")
    

def _get_streamlit_session_id() -> str:
    """
    Retrieve the current Streamlit session ID for audit logging.

    Returns an empty string if the session context is unavailable,
    ensuring this never raises in the audit call path.

    Returns:
        Streamlit session ID string, or '' if unavailable
    """
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        return ctx.session_id if ctx else ''
    except Exception:
        return ''


def perform_search(search_type: str, search_value: str):
    """Perform vendor search and transition to results screen"""
    try:
        with st.spinner("Searching vendors..."):
            df = st.session_state.db_manager.search_vendors(search_type, search_value)
            search_result = st.session_state.vendor_processor.process_search_results(df)
        
        # Mark that a search has been performed
        st.session_state.search_performed = True
        
        if not search_result.vendors:
            st.warning(f"No vendors found matching '{search_value}'")
            # Store empty results for create button logic
            st.session_state.search_results = search_result
            st.session_state.search_type = search_type
            st.session_state.search_value = search_value
            return
        
        # Store results and transition to results screen
        st.session_state.search_results = search_result
        st.session_state.search_type = search_type
        st.session_state.search_value = search_value
        st.session_state.current_mode = 'results'
        st.rerun()
            
    except Exception as e:
        st.error(f"Search failed: {str(e)}")
        logger.error(f"Search error: {e}")

def show_results_screen():
    """Display search results and handle vendor selection"""
    search_result = st.session_state.search_results
    
    if not search_result:
        st.error("No search results available")
        st.session_state.current_mode = 'search'
        st.rerun()
        return
    
    st.header(f"📋 Search Results ({len(search_result.vendors)} found)")
    # Map database field name to display name for search type
    search_type_display = "Parent Company" if st.session_state.search_type == "Parent Vendor" else st.session_state.search_type
    st.write(f"Searching by: {search_type_display}")
    st.write(f"Search term: {st.session_state.search_value}")
    
    # Back to search button
    if st.button("← Back to Search"):
        st.session_state.current_mode = 'search'
        st.session_state.search_results = None
        st.rerun()
    
    if any(v.get('duplicate_label') for v in search_result.vendors):
        st.caption("Rows marked (duplicate) are disfavored; rationalize duplicates in the database.")
    # Single list view: all rows with duplicate labels where applicable
    display_results_list(search_result)

def display_results_list(search_result: VendorSearchResult):
    """Display all result rows in a single list; show duplicate label on subordinate rows."""
    st.subheader("📋 Search Results")
    
    for i, vendor in enumerate(search_result.vendors):
        vendor_number = vendor['Vendor Number']
        vendor_name = vendor.get('Vendor Name', 'Unknown')
        file_value = vendor.get('FILE', 'Unknown')
        dup_label = vendor.get('duplicate_label') or ''
        display_file = f"{file_value} {dup_label}".strip()
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(f"**{vendor_number}** - {vendor_name} ({display_file})")
        
        with col2:
            if st.button(f"Edit", key=f"edit_{i}"):
                try:
                    fresh_vendor = st.session_state.db_manager.get_vendor(vendor_number, vendor['FILE'])
                    st.session_state.selected_vendor = fresh_vendor if fresh_vendor else vendor
                except Exception:
                    st.session_state.selected_vendor = vendor
                st.session_state.current_mode = 'edit'
                st.rerun()

def show_edit_screen():
    """Display vendor editing interface"""
    vendor = st.session_state.selected_vendor
    
    if not vendor:
        st.error("No vendor selected for editing")
        st.session_state.pending_changes = None
        st.session_state.original_vendor = None
        st.session_state.current_mode = 'search'
        st.rerun()
        return
    
    file_value = vendor.get('FILE', 'Unknown')
    st.header(f"✏️ Edit Vendor: {vendor.get('Vendor Number', 'Unknown')} ({file_value})")
    
    # Edit form
    with st.form("vendor_edit_form"):
        st.subheader("Vendor Information")

        # Field guidance
        override_email_label = get_field_display_name('OVERRIDE_EMAIL')
        st.info(f"""💡 **NOTE:**

- Only **Vendor Contacts** will receive CPFR emails
- If **{override_email_label}** is populated, *only* those recipients will receive reports and receipt by **Vendor Contacts** will be temporarily halted.
- To restore receipt by recipients in **Vendor Contacts**, ensure that **{override_email_label}** is empty.
""")
        
        # FILE field - editable with special handling
        current_file = vendor.get('FILE', 'None')
        
        # Normalize current_file: convert None/NaN to 'None', '3Months' to '6Months'
        if current_file is None or (isinstance(current_file, float) and pd.isna(current_file)):
            current_file = 'None'
        elif current_file == '3Months':
            current_file = '6Months'
        
        # FILE options - ordered: 6Months -> Tier2 -> Tier1 -> None (single row per entry)
        file_options = ["6Months", "Tier2", "Tier1", "None"]
        col1, col2 = st.columns([2, 3])
        with col1:
            if current_file in file_options:
                file_index = file_options.index(current_file)
            else:
                file_index = 0
                logger.warning(f"Unrecognized FILE value '{current_file}', defaulting to '6Months'")
            
            updated_file = st.selectbox(
                "FILE",
                file_options,
                index=file_index,
                help="Tier1 changes require CPFR team authorization. Select 6Months, Tier2, Tier1, or None.",
                key="edit_file_field"
            )
        
        # Tier1 authorization note
        tier1_error = updated_file == "Tier1" and current_file != "Tier1"
        with col2:
            if tier1_error:
                st.error("⚠️ **Tier1 changes require CPFR team authorization.**")
                st.markdown(f"Please contact the CPFR team: [nmiles1@chewy.com](mailto:nmiles1@chewy.com)")
            elif updated_file == "Tier1":
                st.info("ℹ️ Current value is Tier1. Changes to Tier1 require CPFR team authorization.")
        
        updated_data = {"FILE": updated_file}
        
        # Get editable fields
        editable_fields = st.session_state.vendor_processor.get_editable_fields()
        
        # Create form fields
        for field in editable_fields:
            current_value = vendor.get(field, '')
            
            # Handle NULL values for display
            display_value = str(current_value).strip() if current_value and str(current_value).strip() else ''
            
            # Get display name for field label
            field_label = get_field_display_name(field)
            
            if field == 'Vendor Contacts':
                # Vendor Contacts uses text_area
                updated_data[field] = st.text_area(
                    field_label,
                    value=display_value,
                    help="Enter semicolon-separated email addresses (leave empty for NULL)"
                )
                st.caption("💡 **Format**: `email1@example.com;email2@example.com;email3@example.com` (semicolon-separated). This format applies to all email fields below.")
            elif field in ['CM_Email', 'CM Manager_Email', 'SP_Email', 'SP Manager_Email']:
                # These email fields use text_input (single line)
                updated_data[field] = st.text_input(
                    field_label,
                    value=display_value,
                    help="Enter semicolon-separated email addresses (leave empty for NULL)"
                )
            elif field == 'OVERRIDE_EMAIL':
                # OVERRIDE_EMAIL uses text_area
                updated_data[field] = st.text_area(
                    field_label,
                    value=display_value,
                    help="Enter semicolon-separated email addresses (leave empty for NULL)"
                )
            elif field in ['Soft Chargeback Effective Date', 'Hard Chargeback Effective Date']:
                # Date fields with NULL option
                current_date = None
                has_date = False
                
                if current_value and str(current_value).strip() and current_value != 'None':
                    try:
                        current_date = pd.to_datetime(current_value).date()
                        has_date = True
                    except:
                        current_date = None
                        has_date = False
                
                # Checkbox to enable/disable date
                st.caption("💡 Use the checkbox to enable/disable the date. Uncheck to set to NULL.")
                enable_date = st.checkbox(f"Set {field_label}", value=has_date, key=f"edit_enable_{field}")
                
                if enable_date:
                    st.caption("💡 Date will be saved when you submit the form.")
                    date_value = st.date_input(
                        field_label,
                        value=current_date,
                        help="Select effective date",
                        key=f"edit_date_{field}"
                    )
                    updated_data[field] = date_value.strftime('%Y-%m-%d') if date_value else None
                else:
                    updated_data[field] = None
                    st.info(f"💡 {field_label} will be set to NULL")
            else:
                # Regular text fields
                updated_data[field] = st.text_input(
                    field_label,
                    value=display_value,
                    help=f"Enter {field_label.lower()} (leave empty for NULL)"
                )
        
        # Submit button
        submitted = st.form_submit_button("💾 Save Changes", type="primary")
        
        # Back button at bottom of form (visible even when confirmation view appears below)
        st.markdown("---")
        back_clicked = st.form_submit_button("← Back to Search", use_container_width=True)
        
        if submitted and not back_clicked:
            save_vendor_changes(vendor, updated_data)
        
        if back_clicked:
            # If we have search results, go back to results screen; otherwise go to search screen
            if st.session_state.search_results:
                st.session_state.current_mode = 'results'
            else:
                st.session_state.current_mode = 'search'
                st.session_state.search_results = None
            st.session_state.selected_vendor = None
            st.rerun()
    
    # Show confirmation button if there are pending changes
    if st.session_state.pending_changes:
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("✅ Confirm Changes", type="primary"):
                # st.rerun() lives here, NOT inside confirm_vendor_changes(), so
                # Streamlit's internal RerunException is never swallowed by that
                # function's except block.
                if confirm_vendor_changes():
                    st.rerun()
        
        with col2:
            if st.button("❌ Cancel Changes"):
                st.session_state.pending_changes = None
                st.session_state.original_vendor = None
                st.rerun()
    

def save_vendor_changes(original_vendor: Dict[str, Any], updated_data: Dict[str, Any]):
    """Save vendor changes to database"""
    try:
        # Normalize FILE values for comparison: convert None/NaN to 'None', '3Months' to '6Months'
        original_file = original_vendor.get('FILE', 'None')
        if original_file is None or (isinstance(original_file, float) and pd.isna(original_file)):
            original_file = 'None'
        elif original_file == '3Months':
            original_file = '6Months'
        
        new_file = updated_data.get('FILE', original_file)
        # Normalize new_file for comparison
        if new_file == '3Months':
            new_file = '6Months'
        
        # Block Tier1 selection (unless it's already Tier1)
        if new_file == "Tier1" and original_file != "Tier1":
            st.error("❌ **Tier1 changes require CPFR team authorization.**")
            st.markdown(f"Please contact the CPFR team: [nmiles1@chewy.com](mailto:nmiles1@chewy.com)")
            return
        
        # Validate the updated data
        validation_result = st.session_state.vendor_processor.validate_vendor_data(updated_data)
        
        if not validation_result.is_valid:
            st.error("❌ Validation errors found:")
            for error in validation_result.errors:
                st.error(f"  - {error}")
            return
        
        # Check if FILE field is being changed
        file_changing = original_file != new_file
        
        # Calculate changes (including FILE if it changed)
        changes = st.session_state.vendor_processor.calculate_changes(original_vendor, updated_data)
        if file_changing and 'FILE' not in changes:
            changes['FILE'] = new_file
        
        if not changes:
            st.info("ℹ️ No changes detected")
            return
        
        # Show changes summary
        st.subheader("📝 Changes Summary")
        for field, new_value in changes.items():
            old_value = original_vendor.get(field, '')
            field_label = get_field_display_name(field)
            st.write(f"**{field_label}**:")
            st.write(f"  From: {old_value or '(empty)'}")
            st.write(f"  To: {new_value or '(empty)'}")
        
        # Store changes in session state for confirmation
        st.session_state.pending_changes = changes
        st.session_state.original_vendor = original_vendor
        st.session_state.file_changing = file_changing
    
    except Exception as e:
        st.error(f"❌ Error saving changes: {str(e)}")
        logger.error(f"Save error: {e}")

def confirm_vendor_changes() -> bool:
    """
    Confirm and save pending vendor changes.

    Returns:
        True if the operation succeeded and the caller should trigger st.rerun();
        False otherwise. st.rerun() is intentionally NOT called here so that
        Streamlit's RerunException is never swallowed by this function's except block.
    """
    # Set fallback values so the outer except block can always reference these
    vendor_number = ''
    audit_action = 'UPDATE'
    changes = {}
    original_vendor = {}

    try:
        changes = st.session_state.pending_changes
        original_vendor = st.session_state.original_vendor
        file_changing = st.session_state.get('file_changing', False)

        # Update database
        vendor_number = original_vendor['Vendor Number']
        original_file = original_vendor['FILE']
        new_file = changes.get('FILE', original_file)
        audit_action = 'TIER_CHANGE' if (file_changing and original_file != new_file) else 'UPDATE'

        # Check if FILE is changing - if so, use tier change logic
        if file_changing and original_file != new_file:
            try:
                success = st.session_state.db_manager.change_vendor_tier(
                    vendor_number, original_file, new_file, changes
                )

                if not success:
                    st.error("❌ Failed to change tier. Please check the application logs for details.")
            except Exception as tier_error:
                logger.error(f"Exception in change_vendor_tier: {tier_error}", exc_info=True)
                st.error(f"❌ Error changing tier: {str(tier_error)}")
                success = False
        else:
            # Regular update (FILE not changing)
            try:
                success = st.session_state.db_manager.update_vendor(
                    vendor_number, original_file, changes
                )
                if not success:
                    st.error("❌ Failed to update vendor. Please check the application logs for details.")
            except Exception as update_error:
                logger.error(f"Exception in update_vendor: {update_error}", exc_info=True)
                st.error(f"❌ Error updating vendor: {str(update_error)}")
                success = False

        if success:
            # Fetch fresh data from database
            try:
                # Use new_file if tier changed, otherwise use original_file
                fetch_file = new_file if file_changing and original_file != new_file else original_file
                fresh_vendor = st.session_state.db_manager.get_vendor(vendor_number, fetch_file)
                if not fresh_vendor:
                    # Fallback
                    fresh_vendor = original_vendor.copy()
                    fresh_vendor.update(changes)
            except Exception as e:
                # Fallback
                fresh_vendor = original_vendor.copy()
                fresh_vendor.update(changes)
                logger.warning(f"Could not fetch fresh data: {e}")

            # Write audit record for successful transaction
            st.session_state.db_manager.write_audit_record(
                action_type=audit_action,
                status='SUCCESS',
                vendor_number=vendor_number,
                before_state=original_vendor,
                after_state=fresh_vendor,
                changed_fields=list(changes.keys()),
                session_id=_get_streamlit_session_id(),
            )

            # Create receipt data
            receipt_data = {
                'vendor_number': vendor_number,
                'original_vendor': original_vendor,
                'updated_vendor': fresh_vendor,
                'changes': changes,
                'file_changed': file_changing,
                'original_file': original_file,
                'new_file': new_file if file_changing else original_file
            }

            # Clear pending changes and move to receipt screen
            st.session_state.pending_changes = None
            st.session_state.original_vendor = None

            # Store receipt and move to receipt screen
            st.session_state.tier_change_receipt = receipt_data
            st.session_state.current_mode = 'receipt'
            return True
        else:
            # Write audit record for failed transaction (DB returned False)
            st.session_state.db_manager.write_audit_record(
                action_type=audit_action,
                status='ERROR',
                vendor_number=vendor_number,
                before_state=original_vendor,
                after_state=None,
                changed_fields=list(changes.keys()),
                error_message='Database operation returned False; see application logs.',
                session_id=_get_streamlit_session_id(),
            )
            st.error("❌ Failed to save changes. Please try again.")
            return False

    except Exception as e:
        logger.error(f"Error in confirm_vendor_changes: {e}", exc_info=True)
        # Write audit record for unexpected exception
        st.session_state.db_manager.write_audit_record(
            action_type=audit_action,
            status='ERROR',
            vendor_number=vendor_number,
            before_state=original_vendor if original_vendor else None,
            after_state=None,
            changed_fields=list(changes.keys()) if changes else None,
            error_message=str(e)[:5000],
            session_id=_get_streamlit_session_id(),
        )
        st.error(f"❌ Error confirming changes: {str(e)}")
        return False

def show_receipt_screen():
    """Display persistent receipt screen showing what was changed"""
    receipt = st.session_state.tier_change_receipt

    if not receipt:
        st.error("No receipt data available")
        st.session_state.current_mode = 'search'
        st.rerun()
        return
    
    st.header("✅ Changes Saved Successfully")
    st.success(f"Vendor **{receipt['vendor_number']}** has been updated.")
    
    # Success message
    st.info("""
    **✅ Changes Saved**: Your updates have been applied successfully.
    """)
    
    # Show what changed
    st.subheader("📝 Changes Made")
    
    changes = receipt['changes']
    original_vendor = receipt['original_vendor']
    
    if receipt['file_changed']:
        st.info(f"**Tier Changed:** {receipt['original_file']} → {receipt['new_file']}")
    
    # Show field changes
    if changes:
        for field, new_value in changes.items():
            if field == 'FILE':
                continue  # Already shown above
            old_value = original_vendor.get(field, '')
            field_label = get_field_display_name(field)
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write(f"**{field_label}:**")
            with col2:
                st.write(f"{old_value or '(empty)'} → {new_value or '(empty)'}")
    
    # Show current vendor info
    st.subheader("📋 Current Vendor Information")
    updated_vendor = receipt['updated_vendor']
    
    # Display in a nice format
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Vendor Number:** {updated_vendor.get('Vendor Number', 'N/A')}")
        st.write(f"**FILE:** {updated_vendor.get('FILE', 'N/A')}")
        st.write(f"**Vendor Name:** {updated_vendor.get('Vendor Name', 'N/A')}")
        st.write(f"**Vendor Contacts:** {updated_vendor.get('Vendor Contacts', 'N/A')}")
        st.write(f"**{get_field_display_name('Parent Vendor')}:** {updated_vendor.get('Parent Vendor', 'N/A')}")
    
    with col2:
        st.write(f"**{get_field_display_name('CM_Email')}:** {updated_vendor.get('CM_Email', 'N/A')}")
        st.write(f"**{get_field_display_name('CM Manager_Email')}:** {updated_vendor.get('CM Manager_Email', 'N/A')}")
        st.write(f"**{get_field_display_name('SP_Email')}:** {updated_vendor.get('SP_Email', 'N/A')}")
        st.write(f"**{get_field_display_name('SP Manager_Email')}:** {updated_vendor.get('SP Manager_Email', 'N/A')}")
        st.write(f"**{get_field_display_name('OVERRIDE_EMAIL')}:** {updated_vendor.get('OVERRIDE_EMAIL', 'N/A')}")
    
    # Navigation button - receipt screen is now standalone, needs navigation
    st.markdown("---")
    if st.button("← Back to Search", type="primary", use_container_width=True):
        st.session_state.current_mode = 'search'
        st.session_state.tier_change_receipt = None
        st.rerun()

def show_new_entry_screen():
    """Display new vendor entry form"""
    vendor_number = st.session_state.search_value
    st.header(f"➕ Create New Vendor Entry: {vendor_number}")
    
    # New entry guidance
    st.info("""
    **📝 New Vendor Entry**: Fill in the required fields below. One row per (Vendor Number, FILE).
    """)
    
    # New entry form
    with st.form("new_vendor_form"):
        st.subheader("Vendor Information")
        
        # Vendor Number (read-only)
        st.text_input("Vendor Number", value=vendor_number, disabled=True)
        
        # FILE selection - ordered: 6Months -> Tier2 -> Tier1 -> None, default to 6Months
        col1, col2 = st.columns([2, 3])
        with col1:
            file_value = st.selectbox(
                "FILE",
                ["6Months", "Tier2", "Tier1", "None"],
                index=0,  # Default to '6Months'
                help="Tier1 requires CPFR team authorization. Select 6Months, Tier2, Tier1, or None.",
                key="new_file_field"
            )
        
        # Check if Tier1 was selected and show error
        tier1_error = file_value == "Tier1"
        
        # Show error message if Tier1 was attempted
        with col2:
            if tier1_error:
                st.error("⚠️ **Tier1 requires CPFR team authorization.**")
                st.markdown(f"Please contact the CPFR team: [nmiles1@chewy.com](mailto:nmiles1@chewy.com)")
                # Reset to default (Tier2) - this will be validated again on submission
                file_value = "Tier2"
        
        # Get required and editable fields
        required_fields = st.session_state.vendor_processor.get_required_fields()
        editable_fields = st.session_state.vendor_processor.get_editable_fields()
        
        # Create form fields
        new_vendor_data = {"Vendor Number": vendor_number, "FILE": file_value}
        
        for field in editable_fields:
            # Get display name for field label
            field_label = get_field_display_name(field)
            
            if field == 'Vendor Contacts':
                new_vendor_data[field] = st.text_area(
                    field_label,
                    help="Enter semicolon-separated email addresses"
                )
                st.caption("💡 **Format**: `email1@example.com;email2@example.com` (semicolon-separated, required)")
            elif field in ['CM_Email', 'CM Manager_Email', 'SP_Email', 'SP Manager_Email']:
                # These email fields use text_input (single line)
                new_vendor_data[field] = st.text_input(
                    field_label,
                    help="Enter semicolon-separated email addresses (optional)"
                )
                st.caption("💡 Semicolon-delimited format (optional)")
            elif field == 'OVERRIDE_EMAIL':
                new_vendor_data[field] = st.text_area(
                    field_label,
                    help="Enter semicolon-separated email addresses (optional)"
                )
                st.caption("💡 Semicolon-delimited format (optional)")
            elif field in ['Soft Chargeback Effective Date', 'Hard Chargeback Effective Date']:
                # Use a checkbox to enable/disable date input
                enable_date = st.checkbox(f"Set {field_label}", key=f"enable_{field}")
                if enable_date:
                    date_value = st.date_input(
                        field_label,
                        help="Select effective date",
                        key=f"date_{field}"
                    )
                    new_vendor_data[field] = date_value.strftime('%Y-%m-%d') if date_value else None
                else:
                    new_vendor_data[field] = None
                    st.info(f"💡 {field_label} will be set to NULL")
            else:
                new_vendor_data[field] = st.text_input(
                    field_label,
                    help=f"Enter {field_label.lower()}"
                )
        
        # Submit button
        submitted = st.form_submit_button("💾 Create Vendor", type="primary")
        
        # Back button at bottom of form (visible even when confirmation view appears below)
        st.markdown("---")
        back_clicked = st.form_submit_button("← Back to Search", use_container_width=True)
    
    # Handle form submission outside the form
    if submitted and not back_clicked:
        save_new_vendor(new_vendor_data, file_value)
    
    if back_clicked:
        st.session_state.current_mode = 'search'
        st.session_state.search_results = None
        st.session_state.selected_vendor = None
        st.session_state.search_value = ''
        st.rerun()

def save_new_vendor(vendor_data: Dict[str, Any], file_value: str):
    """Save new vendor to database"""
    vendor_number = vendor_data.get('Vendor Number', '')

    try:
        # Validate FILE field - prevent Tier1 selection
        if file_value == "Tier1":
            st.error("❌ **Tier1 requires CPFR team authorization.**")
            st.markdown(f"Please contact the CPFR team: [nmiles1@chewy.com](mailto:nmiles1@chewy.com)")
            return
        
        # Validate the data
        validation_result = st.session_state.vendor_processor.validate_vendor_data(vendor_data)
        
        if not validation_result.is_valid:
            st.error("❌ Validation errors found:")
            for error in validation_result.errors:
                st.error(f"  - {error}")
            return
        
        # Check required fields
        required_fields = st.session_state.vendor_processor.get_required_fields()
        missing_fields = [field for field in required_fields if not vendor_data.get(field)]
        
        if missing_fields:
            st.error(f"❌ Required fields missing: {', '.join(missing_fields)}")
            return
        
        success = st.session_state.db_manager.insert_vendor(vendor_data)
        
        if success:
            st.success("✅ Vendor created successfully!")

            # Write audit record for successful insert
            st.session_state.db_manager.write_audit_record(
                action_type='INSERT',
                status='SUCCESS',
                vendor_number=vendor_number,
                before_state=None,
                after_state=vendor_data,
                changed_fields=list(vendor_data.keys()),
                session_id=_get_streamlit_session_id(),
            )
            
            # Show created vendor info that persists
            st.subheader("📋 Created Vendor Information")
            for field, value in vendor_data.items():
                if field not in ['Vendor Number', 'FILE']:
                    display_value = str(value).strip() if value and str(value).strip() else '(null)'
                    field_label = get_field_display_name(field)
                    st.write(f"**{field_label}**: {display_value}")
            
            # Don't auto-return to search - keep form visible
        else:
            # Write audit record for failed insert (DB returned False)
            st.session_state.db_manager.write_audit_record(
                action_type='INSERT',
                status='ERROR',
                vendor_number=vendor_number,
                before_state=None,
                after_state=None,
                changed_fields=list(vendor_data.keys()),
                error_message='Database operation returned False; see application logs.',
                session_id=_get_streamlit_session_id(),
            )
            st.error("❌ Failed to create vendor")
    
    except Exception as e:
        # Write audit record for unexpected exception
        st.session_state.db_manager.write_audit_record(
            action_type='INSERT',
            status='ERROR',
            vendor_number=vendor_number,
            before_state=None,
            after_state=None,
            changed_fields=list(vendor_data.keys()) if vendor_data else None,
            error_message=str(e)[:5000],
            session_id=_get_streamlit_session_id(),
        )
        st.error(f"❌ Error creating vendor: {str(e)}")
        logger.error(f"Create vendor error: {e}")

if __name__ == "__main__":
    main()
