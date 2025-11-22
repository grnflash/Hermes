# Safe Pattern for Session State Validation

## If You Need validate_session_state() Functionality

The validation logic itself isn't bad - it's WHERE it runs that causes corruption. Here's how to use it safely:

## UNSAFE (Causes Corruption):
```python
def main():
    st.set_page_config(...)
    validate_session_state()  # ❌ NEVER HERE - corrupts during init
    st.title("App")
```

## SAFE Option 1: In User Action Handlers
```python
def show_search_screen():
    """Display vendor search interface"""
    st.header("🔍 Search Vendors")

    # Safe to validate here - initialization is complete
    validate_session_state()

    # Rest of search logic...

def show_edit_screen():
    """Display vendor edit interface"""
    # Safe to validate before showing edit screen
    validate_session_state()

    st.header("✏️ Edit Vendor")
    # Rest of edit logic...
```

## SAFE Option 2: Lazy Validation on First User Interaction
```python
def main():
    st.set_page_config(...)
    st.title("App")

    # Track if we've validated this session
    if 'validated_session' not in st.session_state:
        st.session_state.validated_session = False

    # Only validate after user interacts
    if st.button("Search") and not st.session_state.validated_session:
        validate_session_state()
        st.session_state.validated_session = True
```

## SAFE Option 3: Validate Only on Mode Transitions
```python
def switch_to_edit_mode(vendor):
    """Safely transition to edit mode"""
    # Validate state before transition
    validate_session_state()

    st.session_state.current_mode = 'edit'
    st.session_state.selected_vendor = vendor
    st.rerun()
```

## Why These Are Safe

1. **Initialization is complete** - Streamlit in Snowflake has finished setting up
2. **State is fully populated** - All variables exist and have values
3. **No race conditions** - Not competing with initialization
4. **User-triggered** - Only runs when user is actively using the app

## Rule of Thumb

Ask yourself:
- Is Streamlit fully initialized? ✅
- Has the user interacted with the app? ✅
- Am I inside a callback or event handler? ✅

If YES to all → Safe to validate
If NO to any → Don't validate yet

## Recommended Approach

For maximum safety, remove `validate_session_state()` entirely. The ReferenceApp doesn't have it and works perfectly. Instead:

1. **Initialize state properly** at module level (already done)
2. **Handle edge cases** in the specific functions that need them
3. **Trust Streamlit's state management** - it's quite robust

The state validation was added to fix a problem that might not even exist anymore, especially with proper initialization.