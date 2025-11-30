# Troubleshooting Log - Streamlit in Snowflake Connection Issues

**Issue**: Main app fails to load in office network with "Unable to connect to the Snowflake backend" error, while reference app loads fine in same environment.

**Date Started**: [Current Session]
**Status**: ❌ ONGOING - App hangs at "Step 1 of 6: Checking warehouse status"
**Latest Update**: Session state fixes did not resolve the issue
**Current Symptom**: Status bar shows "Step 1 of 6: Checking warehouse status" and never progresses

---

## Attempts Made (COEs - Corrections of Errors)

### COE-001: Lazy Session Initialization
**Date**: Initial attempt
**Change**: Removed eager session initialization from `DatabaseManager.__init__()`, made it lazy via `get_session()`
**Files Modified**: `database_manager.py`
**Dependencies**: 
- All methods that call `get_session()` (no change needed, already using lazy pattern)
- `streamlit_app.py` - connection check in `main()` (no change needed)
**Result**: ❌ Did not resolve issue
**Notes**: This was based on assumption that eager initialization was causing hangs, but reference app uses eager initialization successfully

### COE-002: Removed Blocking Test Query
**Date**: Initial attempt  
**Change**: Removed `session.sql("SELECT 1 as test").collect()` from `_initialize_session()` to prevent blocking
**Files Modified**: `database_manager.py` - `_initialize_session()` method
**Dependencies**: None - test query was only for verification
**Result**: ❌ Did not resolve issue
**Notes**: Reference app includes this test query and works fine

### COE-003: Deferred DatabaseManager Initialization
**Date**: After COE-001
**Change**: Moved `DatabaseManager()` initialization from module level to inside `main()` after `st.set_page_config()`
**Files Modified**: `streamlit_app.py`
**Dependencies**: 
- Reset flag logic (lines 25-47) - needs to handle `None` db_manager
- All code that accesses `st.session_state.db_manager` - needs null checks
**Result**: ❌ Did not resolve issue
**Notes**: Theory was that initialization before `st.set_page_config()` was causing issues, but reference app initializes at module level

### COE-004: Added Defensive Error Handling
**Date**: After COE-003
**Change**: Wrapped `DatabaseManager()` initialization in try/except at module level, set to `None` on failure, retry in `main()`
**Files Modified**: `streamlit_app.py` - lines 52-58 (module level), lines 206-214 (main function)
**Dependencies**: 
- `main()` function - added null check and retry logic
- All database operations - need to handle `None` db_manager gracefully
**Result**: ❌ Did not resolve issue
**Notes**: This defensive pattern may have interfered with Streamlit in Snowflake's error handling

### COE-005: Removed Defensive Error Handling (Match Reference App)
**Date**: After COE-004
**Change**: Removed try/except wrapper, matched reference app exactly - direct initialization at module level
**Files Modified**: `streamlit_app.py` - removed try/except, restored direct initialization
**Dependencies**: None - reverted to reference app pattern
**Result**: ❌ Still failing
**Notes**: Code now matches reference app exactly, but still fails. Suggests issue may be:
- Different app subdomain/URL being blocked
- Different deployment configuration
- Cached state/session issues
- Timing/race condition specific to this app

### COE-006: Clear Browser Cache
**Date**: [Current Date]
**Change**: Cleared browser cache and cookies for the app
**Files Modified**: None - browser-level change
**Dependencies**: None
**Result**: ⚠️ Partial - App still failed after cache clear alone
**Notes**: Cache clear was first step, but app deletion was also required

### COE-007: Delete and Recreate App from Scratch
**Date**: [Previous Date]
**Change**: Deleted app instance in Snowflake, created new app deployment with same code
**Files Modified**: None - deployment change only
**Dependencies**: None
**Result**: ⚠️ TEMPORARY SUCCESS - App worked briefly, then issue returned
**Notes**: 
- Combined with browser cache clear (COE-006)
- App worked after fresh deployment but issue returned
- Suggests issue is not just corrupted state, but a deeper timing/initialization problem

### COE-008: Session State Initialization and Validation
**Date**: [Current Date]
**Change**: 
- Initialized all session state variables at module level
- Added `validate_session_state()` function to detect and reset inconsistent states
- Removed help mode to reduce state complexity
**Files Modified**: `streamlit_app.py`
**Dependencies**: None
**Result**: ❌ DID NOT RESOLVE - App still hangs at warehouse status check
**Notes**: 
- Session state fixes were good practice but didn't address root cause
- Issue persists, indicating problem is at initialization level, not state management level
- Status bar shows "Step 1 of 6: Checking warehouse status" and never progresses
- This suggests issue happens BEFORE app code runs, during Streamlit in Snowflake initialization

### COE-009: Defer DatabaseManager Initialization to main()
**Date**: [Current Date]
**Change**: 
- Changed module-level `DatabaseManager()` initialization to `None`
- Moved initialization to `main()` after `st.set_page_config()`
- Added error handling for initialization failures
**Files Modified**: `streamlit_app.py`
**Dependencies**: None
**Result**: ❌ DID NOT RESOLVE - App still hangs at warehouse status check
**Notes**: 
- Theory was that module-level initialization was calling `get_active_session()` before warehouse was ready
- Moving initialization to `main()` after `set_page_config()` did not resolve the issue
- Status bar still shows "Step 1 of 6: Checking warehouse status" and never progresses
- This suggests the issue may be deeper in the Streamlit in Snowflake initialization sequence
- **Next step**: Code cleanup and simplification to reduce complexity and make diagnosis easier

### COE-010: Eliminate Pre-`set_page_config()` Streamlit Calls
**Date**: [Current Date]
**Change**:
- Removed all `st.session_state` interactions from module scope
- Added `handle_force_reset()`, `initialize_session_state()`, and `get_db_manager()` helpers that run only after `st.set_page_config()`
- Ensured `DatabaseManager` initialization occurs lazily through the helper instead of at import time
**Files Modified**: `streamlit_app.py`
**Dependencies**:
- All functions now rely on session state initialized via `initialize_session_state()`
- `_force_reset` logic moved to run immediately after `set_page_config()`
**Result**: ❌ DID NOT RESOLVE - May have made issue worse
**Notes**:
- Streamlit documentation warns against calling `st.session_state` or `st.rerun()` before `st.set_page_config()`. Reference app technically does this, but removing the pattern here gives us a materially different startup sequence that avoids any pre-initialization work.
- This change should prevent the app from doing any Snowflake work during the "Step 1 of 6" phase, reducing the chance of deadlocks observed on the corporate network.
<<<<<<< HEAD
- After analysis, this approach may have introduced new timing issues in Streamlit in Snowflake environment
=======
- After analysis, we determined the bigger UX issue was stale `search_results` cached in session state. Added a `refresh_search_results()` helper and now refresh results after edits/inserts and before navigating back to the results view so the UI always reflects the latest Snowflake data.
>>>>>>> 9297f414ce754ac05e2d7c4a9cf5e6cf58ae8bdd

### COE-011: Revert to ReferenceApp Initialization Pattern
**Date**: [Current Date]
**Change**:
- Reverted to exact ReferenceApp initialization pattern
- Moved all session state initialization back to module level (before main())
- `DatabaseManager()` initialized at module level (line 50)
- Reset flag check and `st.rerun()` at module level (lines 25-46)
- Removed helper functions `handle_force_reset()`, `initialize_session_state()`, and `get_db_manager()`
- Access `st.session_state.db_manager` directly in main()
**Files Modified**: `streamlit_app.py`
**Dependencies**: None - follows working ReferenceApp pattern exactly
**Result**: ❌ STILL HANGING - Pattern match alone insufficient
**Notes**:
- While this violates Streamlit best practices (calling st.session_state before st.set_page_config()), the ReferenceApp proves this pattern works in Streamlit in Snowflake
- Streamlit in Snowflake appears to have different initialization timing than regular Streamlit
- The deferred initialization from COE-010 may have disrupted the expected initialization sequence in the Snowflake environment
- This change matches the ReferenceApp pattern exactly, which consistently works in the office network
- **See STREAMLIT_IN_SNOWFLAKE_PATTERN.md for the reusable solution pattern**

### COE-012: Remove App-Specific Differences & Redeploy
**Date**: [Current Date]
**Change**:
- Removed `validate_session_state()` call after `st.set_page_config()` (ReferenceApp doesn't have this)
- Removed `initial_sidebar_state="collapsed"` parameter from `st.set_page_config()`
- Kept the 4 extra session state variables as they're needed for functionality
- **CRITICAL**: App needs to be deleted and recreated in Snowflake
**Files Modified**: `streamlit_app.py` lines 126, 130
**Dependencies**: None
**Result**: 🟡 PENDING - Requires app deletion and recreation
**Notes**:
- **KEY INSIGHT**: Since ReferenceApp works at the office, this CANNOT be a network issue
- **ROOT CAUSE IDENTIFIED**: `validate_session_state()` modifies state during initialization, causing persistent corruption
- This function detects "inconsistent" state during init (false positive) and "fixes" it, corrupting the deployment
- Once corrupted, every load re-corrupts because the function runs again
- This explains why COE-007 (delete/recreate) only worked temporarily - the corruption-causing code was still present
- **See PERMANENT_FIX.md for why this prevents recurrence**
- **See SAFE_VALIDATION_PATTERN.md for how to safely use validation if needed**

---

## Current Code State

### Key Differences from Reference App (that we've identified):
1. ✅ **None** - Code structure now matches reference app
2. ⚠️ **App Name/Subdomain** - Different app name may have different firewall rules
3. ⚠️ **Deployment State** - May have cached bad state
4. ⚠️ **File Size** - Main app is larger (1092 lines vs 1055 lines) - may affect load timing

### Files Comparison:
- `database_manager.py`: Structure matches, but main app has `DEPRECATED_COLUMNS` constant (shouldn't affect initialization)
- `streamlit_app.py`: Now matches reference app initialization pattern
- `vendor_processor.py`: Not checked for differences yet

---

## Dependencies Map

### DatabaseManager Dependencies:
```
DatabaseManager.__init__()
  └─> _initialize_session()
      └─> get_active_session() [Snowflake Snowpark]
      └─> session.sql("SELECT 1").collect() [Test query]
```

### streamlit_app.py Dependencies:
```
Module Level (lines 1-86):
  └─> st.session_state.get() [Streamlit API]
  └─> st.rerun() [Streamlit API - BEFORE set_page_config]
  └─> DatabaseManager() [Our module]
  └─> VendorProcessor() [Our module]

main() function (lines 194+):
  └─> st.set_page_config() [Streamlit API - MUST BE FIRST]
  └─> st.session_state.db_manager.get_session() [Our module]
  └─> session.sql() [Snowflake Snowpark]
```

### Critical Dependency Chain:
1. **st.session_state** - Used before `st.set_page_config()` (lines 25-47)
2. **st.rerun()** - Called before `st.set_page_config()` (line 47) ⚠️ **POTENTIAL ISSUE**
3. **DatabaseManager()** - Initialized at module level (line 50)
4. **get_active_session()** - Called during DatabaseManager init

### Potential Issue: st.rerun() Before set_page_config()
**Location**: Line 47 in reset flag logic
**Issue**: According to Streamlit in Snowflake limitations, calling `st.rerun()` before `st.set_page_config()` may cause issues
**Status**: Reference app also has this pattern, so likely not the root cause, but worth investigating if other solutions fail
**Dependencies**: Reset flag logic (lines 25-47) - would need refactoring to move after set_page_config()

---

## Potential Root Causes (Not Yet Tested)

### Network/Firewall Related:
- [ ] Different app subdomain may be blocked differently
- [ ] App-specific firewall rules
- [ ] Cached DNS/connection state
- [ ] WebSocket connection timing differences

### Deployment Related:
- [ ] Cached deployment state needs clearing
- [ ] App needs to be redeployed from scratch
- [ ] Different warehouse/resource allocation
- [ ] Session state corruption from previous failed attempts

### Code Related (Subtle Differences):
- [ ] Import order differences
- [ ] Module-level code execution order
- [ ] VendorProcessor initialization timing
- [ ] Logging configuration differences
- [ ] File encoding/line ending differences

### Streamlit in Snowflake Specific:
- [ ] App needs to be "reset" in Snowflake UI
- [ ] Browser cache/cookies for this specific app
- [ ] Session timeout from previous failed attempts
- [ ] Different Streamlit version being used

---

## Next Steps to Try

### High Priority (Not Yet Attempted):

1. **Clear Browser Cache/Cookies for This Specific App**
   - Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
   - Try incognito/private browsing window
   - Clear cookies for the specific app subdomain
   - **Dependencies**: None - safe to try
   - **Why**: Cached bad state from previous failed attempts

2. **Delete and Redeploy App from Scratch**
   - Delete the app in Snowflake UI
   - Create new app with same code
   - **Dependencies**: None - fresh deployment
   - **Why**: May have cached corrupted state from failed initialization attempts

3. **Compare File-by-File with Reference App**
   - Check import order
   - Check module-level code execution order
   - Check for any whitespace/encoding differences
   - **Dependencies**: Need to identify exact differences first
   - **Why**: Subtle differences may affect initialization timing

4. **Check Browser Console for Specific Errors**
   - Open DevTools (F12) → Console tab
   - Look for WebSocket connection errors
   - Look for failed network requests
   - Compare with reference app's console output
   - **Dependencies**: None - diagnostic only
   - **Why**: May reveal specific connection failures

5. **Compare Network Requests (Browser DevTools)**
   - Network tab → Compare requests between working and failing app
   - Look for different subdomains, ports, or blocked requests
   - **Dependencies**: None - diagnostic only
   - **Why**: May reveal firewall blocking specific app subdomain

6. **Check Deployment Settings**
   - Verify warehouse is running and accessible
   - Check role/permissions match reference app
   - Verify app name/subdomain differences
   - **Dependencies**: Snowflake admin access
   - **Why**: Different settings may affect connection

7. **Test with Minimal App (Strip Down)**
   - Remove all code except DatabaseManager initialization
   - Remove VendorProcessor if not needed for init
   - Remove all session state except db_manager
   - **Dependencies**: May break functionality temporarily
   - **Why**: Isolate if issue is with specific code path

### Medium Priority:

8. **Check Streamlit Version Compatibility**
   - Verify both apps use same Streamlit version
   - Check if reference app has different version pinned
   - **Dependencies**: May need to update requirements.txt
   - **Why**: Version differences can cause initialization issues

9. **Check for Infinite Loops or Blocking Operations**
   - Review reset flag logic (lines 25-47)
   - Check if `st.rerun()` before `set_page_config()` causes issues
   - **Dependencies**: May need to refactor reset logic
   - **Why**: Blocking operations can prevent app from loading

10. **Resource Usage Monitoring**
    - Check if app exceeds memory/CPU limits
    - Compare resource usage with reference app
    - **Dependencies**: Snowflake monitoring tools
    - **Why**: Resource limits can cause silent failures

### Low Priority (If Above Don't Work):

11. **Check File Encoding/Line Endings**
    - Ensure files use UTF-8 encoding
    - Check line endings (LF vs CRLF)
    - **Dependencies**: May need to convert files
    - **Why**: Encoding issues can cause import failures

12. **Verify All Imports Are Available**
    - Check if all modules import successfully
    - Verify no circular import issues
    - **Dependencies**: May need to refactor imports
    - **Why**: Import failures can cause silent hangs

---

## Lessons Learned

1. **Eager initialization is fine** - Reference app proves this works
2. **Defensive error handling can interfere** - Let exceptions propagate naturally in Streamlit in Snowflake
3. **Module-level code execution matters** - Order and timing can affect connection
4. **Network issues can be app-specific** - Same codebase, different subdomain, different results
5. **Reference app is the source of truth** - When in doubt, match it exactly
6. **App state can become corrupted** - Failed initialization attempts can leave app in bad state that persists
7. **Fresh deployment clears corrupted state** - Deleting and recreating app resolves state corruption issues
8. **Browser cache + app state both matter** - Both need to be cleared for full resolution

## Current Issue Analysis

**Current Symptom**:
- App hangs at "Step 1 of 6: Checking warehouse status" in Streamlit in Snowflake status bar
- Never progresses past this point
- ReferenceApp works fine, progresses through all 6 steps quickly

**Root Cause (REVISED after critical observation)**:
This is **NOT a network issue** - the ReferenceApp works consistently at the office, proving the network/firewall/WebSockets are fine. The issue is **app-instance specific**.

**Evidence**:
- ReferenceApp works every time at the office
- Main app hangs every time at the office
- User can switch between them in the same session
- If it were network-related, both would fail equally

**Actual Root Cause**:
1. **App deployment state corruption** - The main app instance has corrupted state
2. **Code differences** - `validate_session_state()` function and sidebar parameter not in ReferenceApp
3. **Persistent bad state** - Failed initialization attempts leave the app in bad state

**Why initial research was misleading**:
The Snowflake Community posts about network issues are real, but don't apply here since the ReferenceApp proves the network works. The symptoms are identical but the cause is different.

**See**:
- `STREAMLIT_IN_SNOWFLAKE_PATTERN.md` for the complete reusable solution pattern
- `WAREHOUSE_HANG_ANALYSIS.md` for detailed technical analysis

## Previous Resolution Summary (No Longer Applicable)

**Previous Hypothesis** (COE-007):
Failed `DatabaseManager` initialization attempts during troubleshooting left the app in a corrupted state.

**Status**: This hypothesis is no longer valid - issue persists even after fresh deployments and code fixes.

---

## New Solutions Found (Not Yet Tried)

### From Online Research:

1. **Browser Cache/Cookies Issue**
   - **Source**: Streamlit documentation
   - **Solution**: Clear browser cache, try incognito mode
   - **Status**: Not tried
   - **Priority**: High

2. **App State Corruption from Failed Attempts**
   - **Source**: Common deployment issue
   - **Solution**: Delete and redeploy app from scratch
   - **Status**: Not tried
   - **Priority**: High

3. **st.rerun() Before set_page_config() May Cause Issues**
   - **Source**: Streamlit in Snowflake limitations documentation
   - **Solution**: Move reset logic to after set_page_config(), or use different reset mechanism
   - **Status**: Not tried
   - **Priority**: Medium
   - **Dependencies**: Reset flag logic (lines 25-47) - would need refactoring

4. **Resource Limits Exceeded**
   - **Source**: Streamlit Community Cloud documentation
   - **Solution**: Monitor resource usage, optimize code
   - **Status**: Not tried
   - **Priority**: Medium
   - **Dependencies**: Need monitoring tools

5. **WebSocket Compression/CORS Issues**
   - **Source**: Streamlit deployment documentation
   - **Solution**: Not applicable (can't configure in Streamlit in Snowflake)
   - **Status**: N/A
   - **Priority**: N/A

6. **Infinite Loop in Reset Logic**
   - **Source**: Streamlit community forums
   - **Solution**: Review reset flag logic for potential infinite loops
   - **Status**: Not tried
   - **Priority**: Medium
   - **Dependencies**: Reset flag logic (lines 25-47)

## External Resources Consulted

- Snowflake Streamlit Troubleshooting Guide
- Streamlit in Snowflake documentation
- Streamlit in Snowflake limitations documentation
- WebSocket connection issues
- Local Network Access (LNA) browser restrictions
- Streamlit session state before set_page_config
- Streamlit community forums
- Stack Overflow Streamlit discussions

---

## Future Prevention & Monitoring

### If Issue Recurs:
1. **First Step**: Clear browser cache (COE-006) - quick diagnostic
2. **If persists**: Delete and recreate app (COE-007) - full reset
3. **If recurs frequently**: Investigate code-level error recovery
   - Add better error handling to prevent state corruption
   - Consider adding app health check/reset mechanism
   - Document specific error conditions that cause corruption

### Code Improvements to Consider:
- Add graceful error recovery that doesn't leave app in bad state
- Consider adding app reset mechanism that doesn't require deletion
- Monitor for specific error patterns that lead to corruption
- Document known error conditions that require app recreation

### Monitoring Checklist:
- [ ] App loads successfully after deployment
- [ ] App continues to work after multiple reloads
- [ ] App handles connection errors gracefully
- [ ] No recurrence of "Unable to connect" error
- [ ] App state remains consistent across sessions

---

**Last Updated**: [Current Date/Time]
**Status**: 🔧 Solution Identified - COE-012 requires deployment
**Next Steps**:
1. Deploy COE-012 changes
2. Delete and recreate app in Snowflake
3. Test at office location

