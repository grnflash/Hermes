# Session State Analysis - Hanging Issue on Corporate Presence

## Executive Summary

After comparing the current app with the ReferenceApp, I've identified **several critical session state management issues** that could cause the app to hang, especially when:
- Users forget to close the page (leaving stale state)
- Multiple users access the app simultaneously
- The app is accessed from corporate network (which may have different timeout/connection behavior)

## Critical Issues Found

### 1. **Uninitialized Session State Variables** ⚠️ HIGH PRIORITY

The current app uses several session state variables that are **NOT initialized at module level** but are accessed throughout the code. These can persist in inconsistent states:

**Variables NOT initialized but used:**
- `search_performed` - Used in `show_search_screen()` (line 277) but never initialized
- `pending_changes` - Used extensively in edit flow but never initialized
- `original_vendor` - Used in edit flow but never initialized  
- `file_changing` - Used in edit flow but never initialized
- `help_section` - Used in help screen but never initialized

**Impact:**
- If a user's session ends abruptly (forgot to close page), these variables may be in an inconsistent state
- When the app reloads, it may try to access these variables in a state that causes infinite loops or blocking operations
- Multiple users won't share these (they're session-specific), but stale state from one user's abandoned session could affect their own subsequent sessions

**ReferenceApp Comparison:**
- ReferenceApp also has `search_performed`, `pending_changes`, `original_vendor`, and `file_changing` uninitialized
- **BUT** ReferenceApp does NOT have `help_section` - this is unique to current app
- ReferenceApp is simpler overall (no help mode), reducing state complexity

### 2. **Help Mode State Management** ⚠️ MEDIUM PRIORITY

The current app has a `help` mode that the ReferenceApp doesn't have:

**Current App:**
- Has `current_mode == 'help'` (line 228)
- Has `help_section` state variable (lines 1136-1238)
- Help section state persists across reruns

**ReferenceApp:**
- No help mode
- No help_section variable

**Impact:**
- Additional state complexity increases chance of state corruption
- If help mode is entered and user abandons session, `help_section` may be in inconsistent state
- When app reloads, it may try to render help screen with invalid state

### 3. **Reset Flag Logic Difference** ⚠️ LOW PRIORITY

**Current App (line 37):**
```python
if db_manager is not None:
    st.session_state.db_manager = db_manager
```

**ReferenceApp (line 36):**
```python
if db_manager:
    st.session_state.db_manager = db_manager
```

**Impact:**
- Subtle difference: `is not None` will restore even if db_manager is in an error state (evaluates to False but is not None)
- This could potentially restore a corrupted DatabaseManager instance
- However, this is unlikely to be the root cause since both patterns are generally safe

### 4. **DatabaseManager Initialization Timing** ⚠️ MEDIUM PRIORITY

Both apps initialize `DatabaseManager()` at module level (before `st.set_page_config()`):

**Current App (line 51):**
```python
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()
```

**ReferenceApp (line 50):**
```python
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()
```

**Impact:**
- If `DatabaseManager()` initialization hangs (e.g., network timeout on corporate network), the entire app hangs
- This happens BEFORE `st.set_page_config()`, which means Streamlit can't even render an error message
- The initialization includes a test query: `session.sql("SELECT 1 as test").collect()` which could block
- On corporate networks with strict firewalls/timeouts, this blocking operation could cause the hang

**Why ReferenceApp might work:**
- ReferenceApp may have been deployed when network conditions were better
- ReferenceApp may have cached a successful connection that persists
- ReferenceApp may be on a different subdomain with different firewall rules

## Root Cause Hypothesis

Based on the analysis, I believe the hanging issue is caused by a **combination of factors**:

1. **Primary Cause: Uninitialized State Variables**
   - When a user abandons a session (forgets to close page), session state variables like `pending_changes`, `tier_change_state`, `help_section` may be left in inconsistent states
   - When the app reloads (especially on corporate network with different timeout behavior), it tries to process this stale state
   - The app may enter an infinite loop or blocking state trying to reconcile inconsistent state

2. **Secondary Cause: DatabaseManager Initialization Blocking**
   - On corporate networks, the initial `get_active_session()` call or test query may timeout or hang
   - Since this happens at module level (before `set_page_config()`), Streamlit can't render an error
   - The app appears to hang indefinitely

3. **Contributing Factor: Help Mode Complexity**
   - The additional `help` mode and `help_section` state variable add complexity
   - More state = more opportunities for state corruption
   - ReferenceApp doesn't have this complexity

## Why ReferenceApp Doesn't Have Issues

1. **Simpler State Management**: No help mode, fewer state variables
2. **Different Deployment History**: May have been deployed when network conditions were better, or on a different subdomain
3. **Cached Successful State**: May have a cached successful DatabaseManager connection that persists
4. **Less State to Corrupt**: Fewer state variables means fewer opportunities for corruption

## Solutions

### Solution 1: Initialize All Session State Variables (RECOMMENDED)

Add initialization for all session state variables at module level:

```python
# Add after line 79 in streamlit_app.py
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

if 'pending_changes' not in st.session_state:
    st.session_state.pending_changes = None

if 'original_vendor' not in st.session_state:
    st.session_state.original_vendor = None

if 'file_changing' not in st.session_state:
    st.session_state.file_changing = False

if 'help_section' not in st.session_state:
    st.session_state.help_section = None
```

**Benefits:**
- Ensures all state variables have known initial values
- Prevents accessing undefined state variables
- Makes state transitions more predictable

### Solution 2: Add State Validation on App Start

Add a function to validate and reset inconsistent state:

```python
def validate_session_state():
    """Validate and reset inconsistent session state"""
    # Reset if we're in an invalid state
    if st.session_state.current_mode == 'help' and 'help_section' not in st.session_state:
        st.session_state.current_mode = 'search'
        st.session_state.help_section = None
    
    # Reset if we have pending changes but no original vendor
    if st.session_state.get('pending_changes') and not st.session_state.get('original_vendor'):
        st.session_state.pending_changes = None
        st.session_state.file_changing = False
    
    # Reset tier change state if inconsistent
    if st.session_state.get('tier_change_state') == 'warning' and not st.session_state.get('tier_change_warning'):
        st.session_state.tier_change_state = None
```

Call this function at the start of `main()`.

### Solution 3: Make DatabaseManager Initialization Non-Blocking

Wrap DatabaseManager initialization in a try/except and defer connection:

```python
# At module level
if 'db_manager' not in st.session_state:
    try:
        st.session_state.db_manager = DatabaseManager()
    except Exception as e:
        logger.error(f"Failed to initialize DatabaseManager: {e}")
        # Set to None, will retry in main()
        st.session_state.db_manager = None

# In main(), after set_page_config()
if not st.session_state.db_manager:
    try:
        st.session_state.db_manager = DatabaseManager()
    except Exception as e:
        st.error(f"❌ Failed to connect to Snowflake: {e}")
        st.error("This app must be run in Streamlit in Snowflake (under Projects).")
        return
```

**Note:** This was tried before (COE-004) and didn't work, but it's worth reconsidering with proper state initialization.

### Solution 4: Remove Help Mode (Match ReferenceApp)

If the help mode isn't critical, consider removing it to match ReferenceApp exactly:
- Remove `help` mode from state machine
- Remove `help_section` state variable
- Remove `show_help_screen()` function

This reduces state complexity and matches the ReferenceApp pattern.

## Recommended Action Plan

1. **Immediate (High Priority):**
   - ✅ Initialize all session state variables at module level (Solution 1)
   - ✅ Add state validation function (Solution 2)

2. **Short-term (Medium Priority):**
   - Consider removing help mode if not critical (Solution 4)
   - Add better error handling for DatabaseManager initialization

3. **Long-term (Low Priority):**
   - Monitor for recurrence
   - If issue persists, implement Solution 3 (non-blocking initialization)

## Testing Recommendations

After implementing fixes:
1. Test with abandoned sessions (open app, navigate to edit mode, close browser without saving)
2. Test with multiple users simultaneously
3. Test on corporate network specifically
4. Monitor for any state corruption issues

## Comparison Summary

| Feature | Current App | ReferenceApp | Risk Level |
|---------|-------------|--------------|------------|
| Help mode | ✅ Yes | ❌ No | Medium |
| help_section state | ✅ Yes | ❌ No | Medium |
| search_performed init | ❌ No | ❌ No | High |
| pending_changes init | ❌ No | ❌ No | High |
| original_vendor init | ❌ No | ❌ No | High |
| file_changing init | ❌ No | ❌ No | High |
| DatabaseManager init | Module level | Module level | Medium |
| Reset flag logic | `is not None` | Truthy check | Low |

## Conclusion

**UPDATE**: Session state fixes were implemented but did NOT resolve the hanging issue. The app still hangs at "Step 1 of 6: Checking warehouse status".

**NEW ROOT CAUSE IDENTIFIED**: The issue is NOT session state corruption, but **module-level DatabaseManager initialization** that happens BEFORE Streamlit in Snowflake completes warehouse initialization. When `DatabaseManager.__init__()` calls `get_active_session()` during module import, it tries to access the session before the warehouse is ready, causing a deadlock.

**See**: `WAREHOUSE_HANG_ANALYSIS.md` for detailed analysis of the actual root cause.

**Status of Session State Fixes**:
- ✅ Good practice to initialize all state variables
- ✅ Help mode removal reduces complexity
- ❌ Did not resolve the hanging issue
- The real issue is timing of DatabaseManager initialization, not state management

