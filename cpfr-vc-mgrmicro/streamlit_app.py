"""
CPFR Vendor Contact Streamlit Manager - For Streamlit in Snowflake

Main Streamlit application for managing vendor contact information.
Provides user-friendly interface for non-SQL users to search, edit, and create vendor records.

This version is optimized for Streamlit in Snowflake (under Projects),
using st.connection() for database access and simplifying permission handling.
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

# UI state machine for tier changes
if 'tier_change_state' not in st.session_state:
    st.session_state.tier_change_state = None  # None, 'warning', 'confirmation', 'receipt'

if 'tier_change_warning' not in st.session_state:
    st.session_state.tier_change_warning = None  # Stores warning message

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

def validate_session_state():
    """
    Validate and reset inconsistent session state.
    This prevents the app from hanging due to corrupted state from abandoned sessions.
    """
    # Reset if we have pending changes but no original vendor (inconsistent state)
    if st.session_state.pending_changes and not st.session_state.original_vendor:
        logger.warning("Detected inconsistent state: pending_changes without original_vendor. Resetting.")
        st.session_state.pending_changes = None
        st.session_state.file_changing = False
    
    # Reset tier change state if inconsistent
    if st.session_state.tier_change_state == 'warning' and not st.session_state.tier_change_warning:
        logger.warning("Detected inconsistent state: tier_change_state='warning' without tier_change_warning. Resetting.")
        st.session_state.tier_change_state = None
    
    # Reset if we're in receipt mode but no receipt data
    if st.session_state.current_mode == 'receipt' and not st.session_state.tier_change_receipt:
        logger.warning("Detected inconsistent state: receipt mode without receipt data. Resetting to search.")
        st.session_state.current_mode = 'search'
    
    # Reset if we're in edit mode but no selected vendor
    if st.session_state.current_mode == 'edit' and not st.session_state.selected_vendor:
        logger.warning("Detected inconsistent state: edit mode without selected vendor. Resetting to search.")
        st.session_state.current_mode = 'search'

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

    # Verify connection (silently) - user context display removed per requirements
    try:
        session = st.session_state.db_manager.get_session()
        
        # Connection verification - no UI display
        # User context code kept for potential future use but not displayed
        try:
            user_info = session.sql("SELECT CURRENT_USER(), CURRENT_ROLE()").collect()
            # User context available but not displayed (sidebar removed)
            logger.info(f"User: {user_info[0][0] if user_info else 'Unknown'}, Role: {user_info[0][1] if user_info else 'Unknown'}")
        except Exception as user_error:
            logger.warning(f"Could not get user context: {user_error}")
        
    except Exception as e:
        st.error(f"❌ Failed to connect to Snowflake: {e}")
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
    st.info("💡 **Quick Start**: Vendors are tracked by Vendor Number, or you may also search by Vendor Name/Parent/Company. If no result is found for a Vendor Number, you can create a new entry.")
    
    # Search type selection - 50/50 split (expander appears auxiliary due to inherent visual differences)
    col1, col2 = st.columns([1, 1])
    with col1:
        search_type = st.selectbox(
            "",
            ["Vendor Number", "Vendor Name", "Parent Vendor", "Vendor Contacts"],
            key="search_type_input",
            label_visibility="collapsed"
        )
    with col2:
        # Top-align expander now that label is removed - styled to look auxiliary like info box
        with st.expander("ℹ️ About Search Types", expanded=False):
            st.markdown("""
            - **Vendor Number**: Exact match required
            - **Vendor Name**: Partial match (case-insensitive)
            - **Parent Vendor**: Partial match
            - **Vendor Contacts**: Partial match (searches email addresses)
            """)
    
    # Search input
    search_value = st.text_input(
        f"Enter {search_type.lower()}:",
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
    st.write(f"Searching by: {st.session_state.search_type}")
    st.write(f"Search term: {st.session_state.search_value}")
    
    # Back to search button
    if st.button("← Back to Search"):
        st.session_state.current_mode = 'search'
        st.session_state.search_results = None
        st.rerun()
    
    # Dual entry explanation (shown before results if dual entries exist)
    if search_result.has_dual_entries:
        st.info("""
        **Note:** Tier 2 vendors require a secondary 6Months or 3Months entry. Both are shown for inspection, but **editing either entry synchronizes both automatically.**
        """)
    
    if search_result.has_dual_entries:
        display_dual_entry_results(search_result)
    else:
        display_single_entry_results(search_result)

def display_dual_entry_results(search_result: VendorSearchResult):
    """Display results with Tier2+6Months dual entries"""
    
    # Group by vendor number
    vendor_groups = {}
    for vendor in search_result.vendors:
        vendor_number = vendor['Vendor Number']
        if vendor_number not in vendor_groups:
            vendor_groups[vendor_number] = []
        vendor_groups[vendor_number].append(vendor)
    
    for vendor_number, vendor_list in vendor_groups.items():
        with st.expander(f"Vendor {vendor_number} - {vendor_list[0].get('Vendor Name', 'Unknown')}", expanded=True):
            # Check if this is a Tier2+6Months combination
            file_values = [v['FILE'] for v in vendor_list]
            
            if 'Tier2' in file_values and '6Months' in file_values:
                st.info("🔗 This vendor has Tier2+6Months dual entries")
                
                # Display both entries side by side
                col1, col2 = st.columns(2)
                
                tier2_vendor = next(v for v in vendor_list if v['FILE'] == 'Tier2')
                sixmonths_vendor = next(v for v in vendor_list if v['FILE'] == '6Months')
                
                with col1:
                    st.markdown("**Tier2 Entry**")
                    if st.button(f"Edit Tier2 Entry", key=f"edit_tier2_{vendor_number}"):
                        # Fetch fresh data for the selected entry
                        try:
                            fresh_tier2 = st.session_state.db_manager.get_vendor(vendor_number, 'Tier2')
                            st.session_state.selected_vendor = fresh_tier2 if fresh_tier2 else tier2_vendor
                        except:
                            st.session_state.selected_vendor = tier2_vendor
                        st.session_state.current_mode = 'edit'
                        st.rerun()
                
                with col2:
                    st.markdown("**6Months Entry**")
                    if st.button(f"Edit 6Months Entry", key=f"edit_6months_{vendor_number}"):
                        # Fetch fresh data for the selected entry
                        try:
                            fresh_6months = st.session_state.db_manager.get_vendor(vendor_number, '6Months')
                            st.session_state.selected_vendor = fresh_6months if fresh_6months else sixmonths_vendor
                        except:
                            st.session_state.selected_vendor = sixmonths_vendor
                        st.session_state.current_mode = 'edit'
                        st.rerun()
            else:
                # Single entry
                for i, vendor in enumerate(vendor_list):
                    st.markdown(f"**{vendor['FILE']} Entry**")
                    if st.button(f"Edit {vendor['FILE']} Entry", key=f"edit_{vendor_number}_{i}"):
                        # Fetch fresh data for the selected entry
                        try:
                            fresh_vendor = st.session_state.db_manager.get_vendor(vendor_number, vendor['FILE'])
                            st.session_state.selected_vendor = fresh_vendor if fresh_vendor else vendor
                        except:
                            st.session_state.selected_vendor = vendor
                        st.session_state.current_mode = 'edit'
                        st.rerun()

def display_single_entry_results(search_result: VendorSearchResult):
    """Display single entry search results"""
    st.subheader("📋 Search Results")
    
    for i, vendor in enumerate(search_result.vendors):
        vendor_number = vendor['Vendor Number']
        vendor_name = vendor.get('Vendor Name', 'Unknown')
        file_value = vendor.get('FILE', 'Unknown')
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(f"**{vendor_number}** - {vendor_name} ({file_value})")
        
        with col2:
            if st.button(f"Edit", key=f"edit_{i}"):
                # Fetch fresh data for the selected entry
                try:
                    fresh_vendor = st.session_state.db_manager.get_vendor(vendor['Vendor Number'], vendor['FILE'])
                    st.session_state.selected_vendor = fresh_vendor if fresh_vendor else vendor
                except:
                    st.session_state.selected_vendor = vendor
                st.session_state.current_mode = 'edit'
                st.rerun()

def show_edit_screen():
    """Display vendor editing interface"""
    vendor = st.session_state.selected_vendor
    
    if not vendor:
        st.error("No vendor selected for editing")
        st.session_state.current_mode = 'search'
        st.rerun()
        return
    
    file_value = vendor.get('FILE', 'Unknown')
    st.header(f"✏️ Edit Vendor: {vendor.get('Vendor Number', 'Unknown')} ({file_value})")
    
    # Check for dual entry mismatches
    if file_value in ['Tier2', '6Months']:
        try:
            # Get both entries to check for mismatches
            vendor_combinations = st.session_state.db_manager.get_vendor_combinations(vendor.get('Vendor Number', ''))
            tier2_entry = next((v for v in vendor_combinations if v.get('FILE') == 'Tier2'), None)
            sixmonths_entry = next((v for v in vendor_combinations if v.get('FILE') == '6Months'), None)
            
            if tier2_entry and sixmonths_entry:
                # Dual entry context at top of edit form
                st.info("""
                **🔄 Dual Entry**: This vendor has both Tier2 and 6Months entries. 
                Changes you make here will automatically sync to the other entry.
                """)
                
                # Check for mismatches (excluding FILE field and deprecated fields)
                editable_fields = st.session_state.vendor_processor.get_editable_fields()
                mismatches = []
                for field in editable_fields:
                    tier2_value = tier2_entry.get(field)
                    sixmonths_value = sixmonths_entry.get(field)
                    if str(tier2_value or '') != str(sixmonths_value or ''):
                        mismatches.append(field)
                
                if mismatches:
                    st.warning(f"⚠️ **Dual Entry Mismatch Detected!** The Tier2 and 6Months entries have different values for: {', '.join(mismatches)}. Updating this entry will synchronize both entries with the same values.")
        except Exception as e:
            logger.warning(f"Could not check for dual entry mismatches: {e}")
    
    # Edit form
    with st.form("vendor_edit_form"):
        st.subheader("Vendor Information")
        
        # FILE field - editable with special handling
        current_file = vendor.get('FILE', 'Unknown')
        
        # Determine available FILE options - show all 4 for visibility, but restrict Tier1
        file_options = ["Tier1", "Tier2", "6Months", "3Months"]
        
        # Check if we're editing a 6Months entry that's tied to a Tier2 entry
        disable_tier2 = False
        if current_file == '6Months':
            try:
                vendor_combinations = st.session_state.db_manager.get_vendor_combinations(vendor.get('Vendor Number', ''))
                tier2_entry = next((v for v in vendor_combinations if v.get('FILE') == 'Tier2'), None)
                if tier2_entry:
                    disable_tier2 = True
            except Exception as e:
                logger.warning(f"Could not check for Tier2 entry: {e}")
        
        # Create FILE selectbox - show all options for visibility
        col1, col2 = st.columns([2, 3])
        with col1:
            file_index = file_options.index(current_file) if current_file in file_options else 0
            updated_file = st.selectbox(
                "FILE",
                file_options,
                index=file_index,
                help="Tier1 changes require CPFR team authorization. Select Tier2, 6Months, or 3Months.",
                key="edit_file_field"
            )
        
        # Tier change guidance after FILE field selection
        if updated_file != current_file:
            if updated_file == 'Tier2':
                st.info("""
                **Tier2 Note**: Changing to Tier2 will create both Tier2 and 6Months entries with identical data.
                """)
            elif current_file in ['Tier2', '6Months'] and updated_file not in ['Tier2', '6Months']:
                st.warning("""
                **Tier Change**: Moving away from Tier2/6Months will merge dual entries into a single entry.
                """)
        
        # Check if Tier1 was selected (and it's not the current value)
        tier1_error = None
        if updated_file == "Tier1" and current_file != "Tier1":
            tier1_error = True
            # Note: We can't reset the selectbox value directly, but we'll block submission
            # The selectbox will show Tier1, but the error message will appear and submission will be blocked
        
        # Show error message if Tier1 was attempted
        with col2:
            if tier1_error:
                st.error("⚠️ **Tier1 changes require CPFR team authorization.**")
                st.markdown(f"Please contact the CPFR team: [nmiles1@chewy.com](mailto:nmiles1@chewy.com)")
            elif updated_file == "Tier1":
                # Current value is Tier1 - show info message
                st.info("ℹ️ Current value is Tier1. Changes to Tier1 require CPFR team authorization.")
        
        # Handle 6Months tied to Tier2 restriction
        if disable_tier2 and updated_file == 'Tier2':
            updated_file = current_file  # Prevent change
            st.warning("⚠️ Cannot change 6Months entry to Tier2 when a Tier2 entry already exists for this vendor.")
        
        updated_data = {"FILE": updated_file}
        
        # Get editable fields
        editable_fields = st.session_state.vendor_processor.get_editable_fields()
        
        # Create form fields
        for field in editable_fields:
            current_value = vendor.get(field, '')
            
            # Handle NULL values for display
            display_value = str(current_value).strip() if current_value and str(current_value).strip() else ''
            
            if field in ['Vendor Contacts', 'CM_Email', 'CM Manager_Email', 'SP_Email', 'SP Manager_Email', 'OVERRIDE_EMAIL']:
                # Email fields with validation - built-context pattern
                is_first_email_field = (field == 'Vendor Contacts')
                updated_data[field] = st.text_area(
                    field,
                    value=display_value,
                    help="Enter semicolon-separated email addresses (leave empty for NULL)"
                )
                # Full explanation for first email field - applies to all email fields
                if is_first_email_field:
                    st.caption("💡 **Format**: `email1@example.com;email2@example.com;email3@example.com` (semicolon-separated). This format applies to all email fields below.")
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
                enable_date = st.checkbox(f"Set {field}", value=has_date, key=f"edit_enable_{field}")
                
                if enable_date:
                    st.caption("💡 Date will be saved when you submit the form.")
                    date_value = st.date_input(
                        field,
                        value=current_date,
                        help="Select effective date",
                        key=f"edit_date_{field}"
                    )
                    updated_data[field] = date_value.strftime('%Y-%m-%d') if date_value else None
                else:
                    updated_data[field] = None
                    st.info(f"💡 {field} will be set to NULL")
            else:
                # Regular text fields
                updated_data[field] = st.text_input(
                    field,
                    value=display_value,
                    help=f"Enter {field.lower()} (leave empty for NULL)"
                )
        
        # Submit button
        submitted = st.form_submit_button("💾 Save Changes", type="primary")
        
        # Back button at bottom of form (visible even when confirmation view appears below)
        st.markdown("---")
        back_clicked = st.form_submit_button("← Back to Search", use_container_width=True)
        
        if submitted and not back_clicked:
            save_vendor_changes(vendor, updated_data)
        
        if back_clicked:
            st.session_state.current_mode = 'search'
            st.session_state.search_results = None
            st.session_state.selected_vendor = None
            st.rerun()
    
    # Handle tier change warning state
    if st.session_state.tier_change_state == 'warning':
        show_tier_change_warning()
        # Still show the back button even during warning state
        st.markdown("---")
        st.markdown("**Navigation:**")
        if st.button("← Back to Search", key="back_to_search_bottom_warning", help="Return to the search screen"):
            st.session_state.current_mode = 'search'
            st.session_state.search_results = None
            st.session_state.selected_vendor = None
            st.session_state.tier_change_state = None
            st.session_state.tier_change_warning = None
            st.session_state.pending_changes = None
            st.rerun()
        return
    
    # Show confirmation button if there are pending changes (non-tier changes)
    if st.session_state.pending_changes:
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("✅ Confirm Changes", type="primary"):
                confirm_vendor_changes()
        
        with col2:
            if st.button("❌ Cancel Changes"):
                st.session_state.pending_changes = None
                st.session_state.original_vendor = None
                st.rerun()
    

def save_vendor_changes(original_vendor: Dict[str, Any], updated_data: Dict[str, Any]):
    """Save vendor changes to database"""
    try:
        # Validate FILE field - prevent Tier1 changes
        original_file = original_vendor.get('FILE', '')
        new_file = updated_data.get('FILE', original_file)
        
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
        
        # If FILE is changing, add it to changes explicitly
        if file_changing and 'FILE' not in changes:
            changes['FILE'] = new_file
        
        if not changes:
            st.info("ℹ️ No changes detected")
            return
        
        # Handle tier changes with state machine
        if file_changing:
            # Check what kind of tier change this is
            warning_message = None
            if original_file in ['Tier2', '6Months'] and new_file not in ['Tier2', '6Months']:
                # Moving FROM Tier2+6Months to another tier
                try:
                    vendor_combinations = st.session_state.db_manager.get_vendor_combinations(original_vendor.get('Vendor Number', ''))
                    tier2_exists = any(v.get('FILE') == 'Tier2' for v in vendor_combinations)
                    sixmonths_exists = any(v.get('FILE') == '6Months' for v in vendor_combinations)
                    
                    if tier2_exists and sixmonths_exists:
                        warning_message = f"⚠️ **Tier Change Warning:** You are changing from a Tier2+6Months dual entry to a single {new_file} entry.\n\n**This will:**\n- Merge (synchronize) both Tier2 and 6Months entries\n- Combine them into a single {new_file} entry\n- **Remove the secondary entry**\n\nDo you want to continue?"
                except Exception as e:
                    logger.warning(f"Could not check for dual entries: {e}")
            
            elif original_file not in ['Tier2', '6Months'] and new_file == 'Tier2':
                # Moving TO Tier2 from another tier
                warning_message = f"⚠️ **Tier Change Warning:** You are changing from {original_file} to Tier2.\n\n**This will:**\n- Create both a Tier2 entry and a 6Months entry with identical data\n- **Remove the original {original_file} entry**\n\nDo you want to continue?"
            
            elif original_file in ['Tier2', '6Months'] and new_file in ['Tier2', '6Months'] and original_file != new_file:
                # Changing WITHIN dual entry pair (Tier2 ↔ 6Months)
                try:
                    vendor_combinations = st.session_state.db_manager.get_vendor_combinations(original_vendor.get('Vendor Number', ''))
                    tier2_exists = any(v.get('FILE') == 'Tier2' for v in vendor_combinations)
                    sixmonths_exists = any(v.get('FILE') == '6Months' for v in vendor_combinations)
                    
                    if tier2_exists and sixmonths_exists:
                        warning_message = f"⚠️ **Tier Change Warning:** You are changing from {original_file} to {new_file} within a Tier2+6Months dual entry.\n\n**This will:**\n- Merge (synchronize) both entries\n- Change this entry's FILE to {new_file}\n- **Remove the other entry** (you'll have a single {new_file} entry)\n\nDo you want to continue?"
                    else:
                        # Only one exists, simple change
                        warning_message = f"⚠️ **Tier Change Warning:** You are changing from {original_file} to {new_file}.\n\n**This will:**\n- Change the FILE value from {original_file} to {new_file}\n\nDo you want to continue?"
                except Exception as e:
                    logger.warning(f"Could not check for dual entries: {e}")
            
            # If we have a warning, enter warning state
            if warning_message:
                st.session_state.tier_change_state = 'warning'
                st.session_state.tier_change_warning = warning_message
                st.session_state.pending_changes = changes
                st.session_state.original_vendor = original_vendor
                st.session_state.file_changing = file_changing
                st.rerun()
                return
        
        # Non-tier changes or tier changes without warnings - show normal summary
        # Show changes summary
        st.subheader("📝 Changes Summary")
        for field, new_value in changes.items():
            old_value = original_vendor.get(field, '')
            st.write(f"**{field}**:")
            st.write(f"  From: {old_value or '(empty)'}")
            st.write(f"  To: {new_value or '(empty)'}")
        
        # Store changes in session state for confirmation
        st.session_state.pending_changes = changes
        st.session_state.original_vendor = original_vendor
        st.session_state.file_changing = file_changing
    
    except Exception as e:
        st.error(f"❌ Error saving changes: {str(e)}")
        logger.error(f"Save error: {e}")

def show_tier_change_warning():
    """Display tier change warning with Yes/No confirmation"""
    warning_message = st.session_state.tier_change_warning
    
    st.warning(warning_message)
    
    # Show changes summary
    if st.session_state.pending_changes:
        st.subheader("📝 Changes Summary")
        original_vendor = st.session_state.original_vendor
        changes = st.session_state.pending_changes
        
        for field, new_value in changes.items():
            old_value = original_vendor.get(field, '')
            st.write(f"**{field}**:")
            st.write(f"  From: {old_value or '(empty)'}")
            st.write(f"  To: {new_value or '(empty)'}")
    
    # Yes/No buttons
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("✅ Yes, Continue", type="primary"):
            # Move to confirmation and execute
            confirm_vendor_changes()
    
    with col2:
        if st.button("❌ No, Cancel"):
            # Clear warning state and return to edit
            st.session_state.tier_change_state = None
            st.session_state.tier_change_warning = None
            st.session_state.pending_changes = None
            st.session_state.original_vendor = None
            st.rerun()

def confirm_vendor_changes():
    """Confirm and save pending vendor changes"""
    try:
        changes = st.session_state.pending_changes
        original_vendor = st.session_state.original_vendor
        file_changing = st.session_state.get('file_changing', False)
        
        # Update database
        vendor_number = original_vendor['Vendor Number']
        original_file = original_vendor['FILE']
        new_file = changes.get('FILE', original_file)
        
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
            
            # Clear pending changes and warning state
            st.session_state.pending_changes = None
            st.session_state.original_vendor = None
            st.session_state.tier_change_state = None
            st.session_state.tier_change_warning = None
            
            # Store receipt and move to receipt screen
            st.session_state.tier_change_receipt = receipt_data
            st.session_state.current_mode = 'receipt'
            st.rerun()
        else:
            st.error("❌ Failed to save changes. Please try again.")
            # Clear warning state on failure
            st.session_state.tier_change_state = None
            st.session_state.tier_change_warning = None
    
    except Exception as e:
        logger.error(f"Error in confirm_vendor_changes: {e}", exc_info=True)
        st.error(f"❌ Error confirming changes: {str(e)}")
        # Clear warning state on error
        st.session_state.tier_change_state = None
        st.session_state.tier_change_warning = None

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
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write(f"**{field}:**")
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
        st.write(f"**PURCHASER:** {updated_vendor.get('PURCHASER', 'N/A')}")
        st.write(f"**Shipment Method Code:** {updated_vendor.get('Shipment Method Code', 'N/A')}")
        st.write(f"**Vendor Contacts:** {updated_vendor.get('Vendor Contacts', 'N/A')}")
        st.write(f"**Parent Vendor:** {updated_vendor.get('Parent Vendor', 'N/A')}")
        st.write(f"**CB Rollout Phase:** {updated_vendor.get('CB Rollout Phase', 'N/A')}")
    
    with col2:
        st.write(f"**Soft Chargeback Effective Date:** {updated_vendor.get('Soft Chargeback Effective Date', 'N/A')}")
        st.write(f"**Hard Chargeback Effective Date:** {updated_vendor.get('Hard Chargeback Effective Date', 'N/A')}")
        st.write(f"**CM_Email:** {updated_vendor.get('CM_Email', 'N/A')}")
        st.write(f"**CM Manager_Email:** {updated_vendor.get('CM Manager_Email', 'N/A')}")
        st.write(f"**SP_Email:** {updated_vendor.get('SP_Email', 'N/A')}")
        st.write(f"**SP Manager_Email:** {updated_vendor.get('SP Manager_Email', 'N/A')}")
        st.write(f"**OVERRIDE_EMAIL:** {updated_vendor.get('OVERRIDE_EMAIL', 'N/A')}")
    
    # Navigation handled by "Back to Search" button at bottom of edit form
    # Receipt screen is display-only - no buttons needed here

def show_new_entry_screen():
    """Display new vendor entry form"""
    vendor_number = st.session_state.search_value
    st.header(f"➕ Create New Vendor Entry: {vendor_number}")
    
    # New entry guidance
    st.info("""
    **📝 New Vendor Entry**: Fill in the required fields below. 
    **Note**: Selecting Tier2 will automatically create both Tier2 and 6Months entries with identical data.
    """)
    
    # New entry form
    with st.form("new_vendor_form"):
        st.subheader("Vendor Information")
        
        # Vendor Number (read-only)
        st.text_input("Vendor Number", value=vendor_number, disabled=True)
        
        # FILE selection - show all options but restrict Tier1
        col1, col2 = st.columns([2, 3])
        with col1:
            file_value = st.selectbox(
                "FILE",
                ["Tier1", "Tier2", "6Months", "3Months"],
                help="Tier1 requires CPFR team authorization. Select Tier2, 6Months, or 3Months.",
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
        
        # Show guidance for Tier2
        if file_value == "Tier2":
            st.caption("""
            💡 **Tier2**: Creates both Tier2 and 6Months entries automatically.
            💡 **Other tiers**: Creates single entry only.
            """)
        
        # Get required and editable fields
        required_fields = st.session_state.vendor_processor.get_required_fields()
        editable_fields = st.session_state.vendor_processor.get_editable_fields()
        
        # Create form fields
        new_vendor_data = {"Vendor Number": vendor_number, "FILE": file_value}
        
        for field in editable_fields:
            if field in ['Vendor Contacts', 'CM_Email', 'CM Manager_Email', 'SP_Email', 'SP Manager_Email', 'OVERRIDE_EMAIL']:
                is_first_email_field = (field == 'Vendor Contacts')
                new_vendor_data[field] = st.text_area(
                    field,
                    help="Enter semicolon-separated email addresses" if field == 'Vendor Contacts' else f"Enter {field.lower()}"
                )
                # Full explanation for first email field (Vendor Contacts is required), short for others
                if is_first_email_field:
                    st.caption("💡 **Format**: `email1@example.com;email2@example.com` (semicolon-separated, required)")
                else:
                    st.caption("💡 Semicolon-delimited format (optional)")
            elif field in ['Soft Chargeback Effective Date', 'Hard Chargeback Effective Date']:
                # Use a checkbox to enable/disable date input
                enable_date = st.checkbox(f"Set {field}", key=f"enable_{field}")
                if enable_date:
                    date_value = st.date_input(
                        field,
                        help="Select effective date",
                        key=f"date_{field}"
                    )
                    new_vendor_data[field] = date_value.strftime('%Y-%m-%d') if date_value else None
                else:
                    new_vendor_data[field] = None
                    st.info(f"💡 {field} will be set to NULL")
            else:
                new_vendor_data[field] = st.text_input(
                    field,
                    help=f"Enter {field.lower()}"
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
        
        # Use the new insert method (handles dual entry automatically)
        success = st.session_state.db_manager.insert_vendor(vendor_data)
        
        if success:
            if file_value == "Tier2":
                st.success("✅ Created both Tier2 and 6Months entries successfully!")
            else:
                st.success("✅ Vendor created successfully!")
            
            # Show created vendor info that persists
            st.subheader("📋 Created Vendor Information")
            for field, value in vendor_data.items():
                if field not in ['Vendor Number', 'FILE']:
                    display_value = str(value).strip() if value and str(value).strip() else '(null)'
                    st.write(f"**{field}**: {display_value}")
            
            
            # Don't auto-return to search - keep form visible
        else:
            st.error("❌ Failed to create vendor")
    
    except Exception as e:
        st.error(f"❌ Error creating vendor: {str(e)}")
        logger.error(f"Create vendor error: {e}")

if __name__ == "__main__":
    main()
