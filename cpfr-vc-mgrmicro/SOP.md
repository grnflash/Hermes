# Standard Operating Procedure: CPFR VC Vendor Info Manager

## Overview
The CPFR VC Vendor Info Manager is a Streamlit application in Snowflake for managing vendor contact information in the `EDLDB.SC_SANDBOX.VC_CPFR_VENDOR_EMAIL` table. This tool provides a user-friendly interface for non-SQL users to search, edit, and create vendor records.

## Access
- **Location**: Snowflake Streamlit Apps (under Projects)
- **Database**: EDLDB.SC_SANDBOX
- **Table**: VC_CPFR_VENDOR_EMAIL

## Core Workflows

### 1. Search for a Vendor
1. **Select Search Type**: Choose from Vendor Number, Vendor Name, Parent Vendor, or Vendor Contacts
   - **Vendor Number**: Requires exact match
   - **Vendor Name/Parent/Contacts**: Partial match (case-insensitive)
2. **Enter Search Value**: Type your search term in the text field
3. **Click Search**: Results display below showing matching vendors
4. **View Results**: Each result shows Vendor Number, Name, and FILE type
   - **Dual Entries**: Tier2 vendors show both Tier2 and 6Months entries (editing either syncs both)

### 2. Edit an Existing Vendor
1. **Search and Select**: Find the vendor using search, then click "Edit" on the desired entry
2. **Review Dual Entry Status**: If editing a Tier2 or 6Months entry, the app shows if dual entries exist and will sync changes
3. **Modify Fields**: Update any editable field (see Field Guidelines below)
4. **FILE Field Changes**: 
   - Changing to/from Tier2 triggers a warning (creates/removes dual entries)
   - Tier1 changes require CPFR team authorization
5. **Save Changes**: Click "Save Changes" to review summary, then "Confirm Changes"
6. **Receipt Screen**: View confirmation of saved changes

### 3. Create a New Vendor
1. **Search by Vendor Number**: Enter a vendor number that doesn't exist
2. **No Results Found**: After search shows no results, click "Create New Entry"
3. **Fill Required Fields**: 
   - Vendor Number (pre-filled)
   - FILE (select Tier2, 6Months, or 3Months - Tier1 requires authorization)
   - Vendor Contacts (required, semicolon-separated emails)
4. **Fill Optional Fields**: Complete other fields as needed
5. **Submit**: Click "Create Vendor" to save

## Field Guidelines

### Email Fields (Semicolon-Separated Format)
- **Format**: `email1@example.com;email2@example.com;email3@example.com`
- **Fields**: Vendor Contacts, CM_Email, CM Manager_Email, SP_Email, SP Manager_Email, OVERRIDE_EMAIL
- **Required**: Vendor Contacts (for new entries)
- **Empty Values**: Leave blank to set to NULL

### Date Fields
- **Fields**: Soft Chargeback Effective Date, Hard Chargeback Effective Date
- **Usage**: Check the "Set [Field Name]" checkbox to enable date selection
- **NULL Values**: Uncheck the checkbox to set field to NULL

### FILE Field Rules
- **Tier1**: Requires CPFR team authorization (contact: nmiles1@chewy.com)
- **Tier2**: Automatically creates both Tier2 and 6Months entries with identical data
- **6Months/3Months**: Creates single entry
- **Changing Tiers**: Moving between tiers may merge or split entries (warning shown)

## Important Notes

### Dual Entry Synchronization
- Tier2 vendors require both Tier2 and 6Months entries
- Editing either entry automatically synchronizes changes to both
- The app detects and warns about mismatches between dual entries

### Tier Change Warnings
- Changing from Tier2/6Months to another tier merges dual entries into a single entry
- Changing to Tier2 from another tier creates dual entries
- Always review the warning message before confirming tier changes

### Navigation
- **Back to Search**: Available on all screens to return to the search interface
- **Receipt Screen**: Shows after successful saves - displays what changed and current vendor info

## Troubleshooting

### App Won't Load
- Clear browser cache or try incognito mode
- Verify network allows `*.snowflake.app` and `*.snowflake.com`
- Contact IT if issues persist

### Search Returns No Results
- Verify search type matches your input (exact for Vendor Number, partial for others)
- Check spelling and case (name searches are case-insensitive)
- If vendor doesn't exist, use "Create New Entry" button

### Changes Not Saving
- Verify all required fields are filled
- Check for validation errors (shown in red)
- Ensure you clicked both "Save Changes" and "Confirm Changes"

## Support
For issues or questions, contact the CPFR team: **nmiles1@chewy.com**

---
*Last Updated: 2024-11-21*

