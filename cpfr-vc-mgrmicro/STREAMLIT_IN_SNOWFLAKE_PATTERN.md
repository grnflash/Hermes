# Streamlit in Snowflake - Warehouse Status Hanging Pattern

## Problem Statement
Streamlit in Snowflake apps get stuck at "Step 1 of X: Checking warehouse status" when accessed from certain network environments (typically corporate networks), while the same app works fine from other locations (home/VPN).

## Root Cause Analysis

### Primary Cause: Network Configuration
The most common cause is **network/firewall blocking WebSocket connections** needed for Streamlit in Snowflake to communicate with the backend.

### Secondary Causes
1. **Browser Security Settings** (Chrome local network access checks)
2. **Module-level Initialization Timing** (code pattern issues)
3. **Cached State Corruption** (from previous failed attempts)
4. **Warehouse Configuration** (suspension during initialization)

## Solution Pattern

### 1. Network Configuration (IT/Infrastructure Level)

**Required Allowlisting:**
- `*.snowflake.app` (critical for Streamlit apps)
- `*.snowflake.com` (for general Snowflake access)
- WebSocket protocols must not be blocked

**Verification Steps:**
```sql
-- Use SYSTEM$ALLOWLIST to get all required domains
SELECT SYSTEM$ALLOWLIST();
```

**For Split-Tunnel VPNs:**
Both domains must be added to network policy allowlist.

### 2. Browser Configuration (User Level)

**Chrome-Specific Fix:**
1. Navigate to: `chrome://flags#local-network-access-check`
2. Disable the flag
3. Restart Chrome

**Alternative Browsers:**
Try Edge, Firefox, or Safari if Chrome continues to have issues.

### 3. Code Pattern (Developer Level)

**Working Pattern for Streamlit in Snowflake:**

```python
"""
Streamlit in Snowflake App - Working Initialization Pattern
"""
import streamlit as st
from snowflake.snowpark.context import get_active_session
from database_manager import DatabaseManager
from vendor_processor import VendorProcessor

# IMPORTANT: Module-level initialization works in SiS
# This violates regular Streamlit best practices but is
# required for proper Snowflake warehouse initialization

# Handle reset flag first (if using state reset mechanism)
if st.session_state.get('_force_reset', False):
    # Clear state except essential objects
    db_manager = st.session_state.get('db_manager')
    vendor_processor = st.session_state.get('vendor_processor')

    # Clear all other keys
    keys_to_delete = [key for key in st.session_state.keys()
                     if key not in ['db_manager', 'vendor_processor']]
    for key in keys_to_delete:
        del st.session_state[key]

    # Restore essential objects
    if db_manager:
        st.session_state.db_manager = db_manager
    if vendor_processor:
        st.session_state.vendor_processor = vendor_processor

    # Clear reset flag and rerun
    if '_force_reset' in st.session_state:
        del st.session_state['_force_reset']
    st.rerun()

# Initialize session state at module level
# DO NOT defer these to after st.set_page_config()
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

if 'vendor_processor' not in st.session_state:
    st.session_state.vendor_processor = VendorProcessor()

# Initialize other state variables
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = 'default'

def main():
    """Main application entry point"""
    # st.set_page_config MUST be first in main()
    st.set_page_config(
        page_title="Your App Title",
        page_icon="icon",
        layout="wide"
    )

    # Access pre-initialized objects directly
    session = st.session_state.db_manager.get_session()

    # Rest of app logic...

if __name__ == "__main__":
    main()
```

**Key Differences from Regular Streamlit:**

| Aspect | Regular Streamlit | Streamlit in Snowflake |
|--------|------------------|------------------------|
| Session State Init | After `st.set_page_config()` | At module level (before) |
| Database Connection | Manual credentials | `get_active_session()` |
| Initialization Timing | Deferred/lazy | Immediate at import |
| Best Practice | Avoid module-level st calls | Module-level init works |

### 4. Recovery Steps (When App is Stuck)

**Quick Fixes (Try in Order):**
1. **Hard Refresh**: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
2. **Clear Browser Cache**: Settings → Privacy → Clear browsing data
3. **Incognito/Private Mode**: Eliminates cache/cookie issues
4. **Different Browser**: Try Edge if Chrome fails

**Deep Fixes (If Quick Fixes Fail):**
1. **Delete and Recreate App**:
   - In Snowflake UI, delete the app
   - Create new app with same code
   - This clears corrupted deployment state

2. **Warehouse Settings**:
   - Use dedicated warehouse for Streamlit apps
   - Set auto-suspend to minimum 30 seconds
   - Ensure warehouse size is appropriate (XS usually sufficient)

## Portable Solution Pattern

### For New Apps
Use this initialization template that works in both environments:

```python
from snowflake.snowpark.context import get_active_session
import snowflake.snowpark as sp

def get_snowflake_session():
    """
    Portable session getter - works in both SiS and external Streamlit
    """
    try:
        # Try native Streamlit in Snowflake
        return get_active_session()
    except:
        # Fall back to manual connection for external Streamlit
        # This allows local development/testing
        return sp.Session.builder.configs({
            "account": "your-account",
            "user": "your-user",
            "password": "your-password",
            "database": "your-db",
            "schema": "your-schema",
            "role": "your-role",
            "warehouse": "your-warehouse"
        }).create()

# At module level for SiS
if 'session' not in st.session_state:
    st.session_state.session = get_snowflake_session()
```

### For Existing Apps with Issues
1. **Match Working Pattern**: If you have a working reference app, match its initialization pattern exactly
2. **Module-Level Init**: Move session state initialization to module level
3. **Direct Access**: Access `st.session_state.db_manager` directly, not through helper functions
4. **Avoid Deferred Init**: Don't use lazy initialization patterns in SiS

## Verification Checklist

- [ ] `*.snowflake.app` is allowlisted in corporate firewall
- [ ] `*.snowflake.com` is allowlisted in corporate firewall
- [ ] WebSockets are not blocked by network policy
- [ ] Chrome local network access flag is disabled (if using Chrome)
- [ ] Warehouse has appropriate auto-suspend settings (30+ seconds)
- [ ] App uses module-level initialization pattern
- [ ] Browser cache/cookies have been cleared
- [ ] App has been recreated if previously stuck

## References
- [Snowflake Community: Streamlit app stuck on checking warehouse](https://community.snowflake.com/s/question/0D5VI000000OnUE0A0/streamlit-app-stuck-on-step-1-of-8-checking-warehouse-status-step)
- [Troubleshooting Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/troubleshooting)
- [Getting started with Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/getting-started)
- [SYSTEM$ALLOWLIST Function](https://docs.snowflake.com/en/sql-reference/functions/system_allowlist)
- [Private connectivity for Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/privatelink)

## Key Takeaway
**The "Checking warehouse status" hang is primarily a network/connectivity issue, not a code issue.** However, proper code initialization patterns can help avoid exacerbating the problem. When in doubt, ensure network configuration first, then verify code patterns match known working examples.