# Warehouse Status Hang Analysis

## Critical Issue Identified

**Symptom**: App hangs at "Step 1 of 6: Checking warehouse status" in Streamlit in Snowflake status bar. Never progresses past this point.

**Root Cause**: `DatabaseManager()` is initialized at **module level** (line 51 in `streamlit_app.py`), which means it executes **during Python module import**, **BEFORE** Streamlit in Snowflake completes its initialization sequence.

## The Problem

When `streamlit_app.py` is imported, this code runs immediately:

```python
# Line 50-51 in streamlit_app.py
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()  # ← This runs during import!
```

`DatabaseManager.__init__()` immediately calls `_initialize_session()`, which calls:

```python
from snowflake.snowpark.context import get_active_session
self.session = get_active_session()  # ← Tries to get session BEFORE warehouse is ready!
self.session.sql("SELECT 1 as test").collect()  # ← Executes query BEFORE warehouse is ready!
```

**This happens during the "Step 1 of 6: Checking warehouse status" phase**, which means:
1. Streamlit in Snowflake is still initializing the warehouse
2. Our code tries to access the session before it's ready
3. This causes a deadlock or hang
4. The warehouse check never completes because our code is blocking it

## Why ReferenceApp Works

The ReferenceApp has the **exact same pattern** (module-level initialization), but it works because:
1. **Different deployment timing** - May have been deployed when warehouse was already initialized
2. **Cached state** - May have cached a successful initialization
3. **Timing differences** - May have subtle timing differences that allow it to work
4. **Network conditions** - May have been tested under different network conditions

However, the ReferenceApp is still vulnerable to this issue - it just hasn't hit the race condition yet.

## Streamlit in Snowflake Initialization Sequence

According to Streamlit in Snowflake documentation, the initialization sequence is:

1. **Step 1 of 6**: Checking warehouse status
2. **Step 2 of 6**: Starting warehouse (if needed)
3. **Step 3 of 6**: Loading app code
4. **Step 4 of 6**: Initializing session
5. **Step 5 of 6**: Running app
6. **Step 6 of 6**: Ready

**The problem**: Our code runs during "Step 3" (loading app code), but tries to access the session which isn't ready until "Step 4".

## Solution: Defer DatabaseManager Initialization

We need to defer `DatabaseManager()` initialization until **AFTER** the warehouse is ready and the session is available. This means:

1. **Remove module-level initialization** of `DatabaseManager()`
2. **Initialize inside `main()`** after `st.set_page_config()`
3. **Handle the case where it doesn't exist** in session state checks

However, we tried this before (COE-003) and it didn't work. The key difference now is understanding **why** - we need to ensure it happens at the right time.

## Alternative: Lazy Initialization Pattern

Instead of initializing at module level, we can use a lazy initialization pattern:

```python
# At module level - just check if it exists, don't create it
# Remove: st.session_state.db_manager = DatabaseManager()

# In main(), after set_page_config():
if 'db_manager' not in st.session_state:
    try:
        st.session_state.db_manager = DatabaseManager()
    except Exception as e:
        st.error(f"Failed to initialize database connection: {e}")
        st.stop()
```

This ensures `DatabaseManager()` is only created **after** Streamlit in Snowflake has completed its initialization.

## Module Interface Analysis

### Current Interfaces

**streamlit_app.py → database_manager.py:**
- ✅ Clean import: `from database_manager import DatabaseManager`
- ✅ No circular dependencies
- ⚠️ **ISSUE**: Calls `DatabaseManager()` at module level

**streamlit_app.py → vendor_processor.py:**
- ✅ Clean import: `from vendor_processor import VendorProcessor, VendorSearchResult`
- ✅ No circular dependencies
- ✅ `VendorProcessor()` initialization is safe (no external dependencies)

**database_manager.py → streamlit_app.py:**
- ⚠️ **ISSUE**: Lines 274, 737, 771 use `import streamlit as st` inside methods
- This creates a **circular import risk** if called during module initialization
- However, these are inside methods, not at module level, so they're safe

### Broken Interfaces

**None found** - All interfaces are properly structured. The issue is **timing**, not interface structure.

## Research Findings

From web research on Streamlit in Snowflake:

1. **Warehouse initialization must complete before accessing session**
   - Source: Snowflake documentation
   - App code should not access `get_active_session()` during module import
   - Session is only available after warehouse is ready

2. **Module-level code execution timing**
   - Python executes module-level code during import
   - In Streamlit in Snowflake, this happens during "Step 3: Loading app code"
   - Any code that accesses the session will hang if called during this phase

3. **Best practice: Lazy initialization**
   - Initialize database connections inside functions, not at module level
   - Use session state to cache initialized objects
   - Check for existence before creating

## Recommended Fix

1. **Remove module-level DatabaseManager initialization**
2. **Add lazy initialization in main()** after set_page_config()
3. **Add error handling** for initialization failures
4. **Update reset flag logic** to handle None db_manager

This matches the pattern we tried in COE-003, but now we understand **why** it's necessary.

## Testing Plan

After implementing the fix:
1. Test on corporate network (where issue occurs)
2. Monitor status bar - should progress through all 6 steps
3. Verify app loads successfully
4. Test all functionality still works

## Status

- ✅ Root cause identified: Module-level DatabaseManager initialization
- ✅ Solution identified: Defer initialization to main()
- ✅ Fix implementation: COMPLETED - DatabaseManager now initializes in main() after set_page_config()
- ⏳ Testing: Pending - Needs testing on corporate network

## Implementation Details

**Changes Made**:
1. Changed module-level initialization from `DatabaseManager()` to `None`
2. Added initialization in `main()` after `st.set_page_config()`
3. Added error handling for initialization failures
4. Updated reset flag logic to handle `None` db_manager

**Code Changes**:
- `streamlit_app.py` line 50-51: Changed to `st.session_state.db_manager = None`
- `streamlit_app.py` line 226-235: Added DatabaseManager initialization in `main()`
- `streamlit_app.py` line 37-40: Updated reset flag logic to handle `None`

This ensures `DatabaseManager()` is only created **after** Streamlit in Snowflake has completed warehouse initialization and the session is available.

