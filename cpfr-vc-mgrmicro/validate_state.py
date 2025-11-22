"""
State Machine Validator for CPFR VC App
Run this to check for state corruption or use as a module

Usage:
    As standalone: python validate_state.py
    As module: from validate_state import validate_current_state, generate_state_report
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Try to import Streamlit (may not be available in all contexts)
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    # Mock st.session_state for testing outside Streamlit
    class MockSessionState:
        def __init__(self):
            self._state = {}

        def get(self, key, default=None):
            return self._state.get(key, default)

        def __contains__(self, key):
            return key in self._state

        def __getitem__(self, key):
            return self._state[key]

        def keys(self):
            return self._state.keys()

    class MockSt:
        session_state = MockSessionState()

    st = MockSt()

# Expected state configurations
VALID_STATES = {
    'search': {
        'current_mode': 'search',
        'selected_vendor': None,
        'search_results': None,  # Can be None in search mode
        'required': ['db_manager', 'vendor_processor'],
        'description': 'User can search for vendors'
    },
    'results': {
        'current_mode': 'search',  # Still in search mode
        'search_results': 'NOT_NONE',  # Must have results
        'search_performed': True,
        'required': ['db_manager', 'vendor_processor'],
        'description': 'Search results are displayed'
    },
    'edit': {
        'current_mode': 'edit',
        'selected_vendor': 'NOT_NONE',  # Must have value
        'original_vendor': 'NOT_NONE',
        'required': ['db_manager', 'vendor_processor'],
        'description': 'Editing an existing vendor'
    },
    'new': {
        'current_mode': 'new',
        'selected_vendor': 'NOT_NONE',  # Template vendor
        'required': ['db_manager', 'vendor_processor'],
        'description': 'Creating a new vendor'
    },
    'receipt': {
        'current_mode': 'receipt',
        'tier_change_receipt': 'NOT_NONE',
        'required': ['db_manager'],
        'description': 'Displaying operation results'
    },
    'tier_warning': {
        'current_mode': 'edit',
        'tier_change_state': 'warning',
        'tier_change_warning': 'NOT_NONE',
        'required': ['db_manager', 'vendor_processor', 'selected_vendor'],
        'description': 'Warning about tier change impacts'
    }
}

# Corruption patterns to detect
CORRUPTION_PATTERNS = [
    {
        'name': 'orphaned_pending_changes',
        'condition': lambda s: s.get('pending_changes') and not s.get('original_vendor'),
        'severity': 'HIGH',
        'description': 'pending_changes exists without original_vendor',
        'fix': 'Clear pending_changes or set original_vendor'
    },
    {
        'name': 'edit_without_vendor',
        'condition': lambda s: s.get('current_mode') == 'edit' and not s.get('selected_vendor'),
        'severity': 'HIGH',
        'description': 'Edit mode without selected vendor',
        'fix': 'Return to search mode or set selected_vendor'
    },
    {
        'name': 'receipt_without_data',
        'condition': lambda s: s.get('current_mode') == 'receipt' and not s.get('tier_change_receipt'),
        'severity': 'MEDIUM',
        'description': 'Receipt mode without receipt data',
        'fix': 'Return to search mode or populate receipt'
    },
    {
        'name': 'warning_without_message',
        'condition': lambda s: s.get('tier_change_state') == 'warning' and not s.get('tier_change_warning'),
        'severity': 'MEDIUM',
        'description': 'Tier warning state without warning message',
        'fix': 'Clear tier_change_state or set warning message'
    },
    {
        'name': 'file_changing_stuck',
        'condition': lambda s: s.get('file_changing') and s.get('current_mode') not in ['edit', 'new'],
        'severity': 'LOW',
        'description': 'file_changing flag set outside edit/new mode',
        'fix': 'Clear file_changing flag'
    }
]

def detect_current_state() -> Optional[str]:
    """Detect which state the app is currently in"""

    current_mode = st.session_state.get('current_mode')

    if not current_mode:
        return None

    # Check for specific state conditions
    if current_mode == 'search':
        if st.session_state.get('search_results') is not None:
            return 'results'
        return 'search'

    elif current_mode == 'edit':
        if st.session_state.get('tier_change_state') == 'warning':
            return 'tier_warning'
        return 'edit'

    elif current_mode in ['new', 'receipt']:
        return current_mode

    return None

def validate_current_state() -> List[str]:
    """Check if current session state is valid"""

    issues = []

    # Detect current state
    detected_state = detect_current_state()

    if not detected_state:
        issues.append("Cannot detect current state - missing or invalid current_mode")
        return issues

    # Get expected configuration
    if detected_state not in VALID_STATES:
        issues.append(f"Unknown state: {detected_state}")
        return issues

    expected = VALID_STATES[detected_state]

    # Check expected values for current state
    for key, expected_value in expected.items():
        if key in ['required', 'description']:
            continue

        if key == 'required':
            for req_key in expected_value:
                if req_key not in st.session_state:
                    issues.append(f"Missing required key: {req_key}")
                elif st.session_state.get(req_key) is None:
                    issues.append(f"Required key is None: {req_key}")
        else:
            actual_value = st.session_state.get(key)

            if expected_value == 'NOT_NONE':
                if actual_value is None:
                    issues.append(f"{key} should not be None in {detected_state} state")
            elif expected_value is None:
                if actual_value is not None:
                    issues.append(f"{key} should be None in {detected_state} state, but is: {type(actual_value).__name__}")
            else:
                if actual_value != expected_value:
                    issues.append(f"{key}: expected='{expected_value}', actual='{actual_value}'")

    # Check for corruption patterns
    for pattern in CORRUPTION_PATTERNS:
        if pattern['condition'](st.session_state):
            issues.append(f"CORRUPTION [{pattern['severity']}]: {pattern['description']}")

    return issues

def generate_state_report() -> Dict[str, Any]:
    """Generate a comprehensive state machine health report"""

    detected_state = detect_current_state()
    issues = validate_current_state()

    report = {
        "timestamp": datetime.now().isoformat(),
        "detected_state": detected_state,
        "current_mode": st.session_state.get('current_mode', 'UNKNOWN'),
        "is_valid": len(issues) == 0,
        "validation_issues": issues,
        "session_keys": sorted(list(st.session_state.keys())),
        "state_snapshot": {},
        "corruption_check": []
    }

    # Capture non-sensitive state
    for key in st.session_state.keys():
        if key not in ['db_manager', 'vendor_processor', '_fragile_data']:  # Skip objects and internals
            value = st.session_state.get(key)
            if value is None:
                report["state_snapshot"][key] = None
            elif isinstance(value, bool):
                report["state_snapshot"][key] = value
            elif isinstance(value, (str, int, float)):
                report["state_snapshot"][key] = value
            elif isinstance(value, dict):
                report["state_snapshot"][key] = f"dict(keys={len(value)})"
            elif isinstance(value, list):
                report["state_snapshot"][key] = f"list(len={len(value)})"
            else:
                report["state_snapshot"][key] = f"{type(value).__name__}()"

    # Check all corruption patterns
    for pattern in CORRUPTION_PATTERNS:
        if pattern['condition'](st.session_state):
            report["corruption_check"].append({
                "pattern": pattern['name'],
                "severity": pattern['severity'],
                "detected": True,
                "fix": pattern['fix']
            })

    # Add state description if valid
    if detected_state and detected_state in VALID_STATES:
        report["state_description"] = VALID_STATES[detected_state].get('description', 'Unknown state')

    return report

def fix_corruption(dry_run: bool = True) -> List[str]:
    """Attempt to fix detected corruption patterns

    Args:
        dry_run: If True, only report what would be fixed without making changes

    Returns:
        List of actions taken or that would be taken
    """

    actions = []

    for pattern in CORRUPTION_PATTERNS:
        if pattern['condition'](st.session_state):
            action = f"Fix {pattern['name']}: {pattern['fix']}"
            actions.append(action)

            if not dry_run:
                # Apply fixes based on pattern
                if pattern['name'] == 'orphaned_pending_changes':
                    st.session_state.pending_changes = None
                    actions.append("  -> Cleared pending_changes")

                elif pattern['name'] == 'edit_without_vendor':
                    st.session_state.current_mode = 'search'
                    actions.append("  -> Reset to search mode")

                elif pattern['name'] == 'receipt_without_data':
                    st.session_state.current_mode = 'search'
                    actions.append("  -> Reset to search mode")

                elif pattern['name'] == 'warning_without_message':
                    st.session_state.tier_change_state = None
                    actions.append("  -> Cleared tier_change_state")

                elif pattern['name'] == 'file_changing_stuck':
                    st.session_state.file_changing = False
                    actions.append("  -> Reset file_changing flag")

    if not actions:
        actions.append("No corruption detected - no fixes needed")

    return actions

def save_report(report: Dict[str, Any], filename: Optional[str] = None) -> str:
    """Save state report to JSON file"""

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"state_report_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    return filename

# Command-line interface
if __name__ == "__main__" and HAS_STREAMLIT:
    st.set_page_config(page_title="State Validator", page_icon="🔍")
    st.title("🔍 State Machine Validator")
    st.markdown("Debug tool for CPFR VC App state machine")

    # Current state display
    col1, col2 = st.columns(2)
    with col1:
        detected = detect_current_state()
        if detected:
            st.success(f"Detected State: **{detected}**")
            if detected in VALID_STATES:
                st.info(VALID_STATES[detected]['description'])
        else:
            st.error("Cannot detect current state")

    with col2:
        mode = st.session_state.get('current_mode', 'UNKNOWN')
        st.info(f"Current Mode: **{mode}**")
        st.info(f"Session Keys: **{len(list(st.session_state.keys()))}**")

    # Validation
    st.header("Validation Results")

    if st.button("🔍 Validate State", type="primary"):
        report = generate_state_report()

        if report["is_valid"]:
            st.success("✅ State machine is valid!")
        else:
            st.error(f"❌ Found {len(report['validation_issues'])} issues:")
            for issue in report["validation_issues"]:
                if "CORRUPTION" in issue:
                    st.error(f"• {issue}")
                else:
                    st.warning(f"• {issue}")

        # Corruption fixes
        if report["corruption_check"]:
            st.header("Corruption Detection")
            for check in report["corruption_check"]:
                st.error(f"**{check['pattern']}** ({check['severity']})")
                st.info(f"Fix: {check['fix']}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔧 Show Fix Preview", type="secondary"):
                    fixes = fix_corruption(dry_run=True)
                    st.info("Would apply these fixes:")
                    for fix in fixes:
                        st.write(f"• {fix}")

            with col2:
                if st.button("⚠️ Apply Fixes", type="primary"):
                    fixes = fix_corruption(dry_run=False)
                    st.success("Applied fixes:")
                    for fix in fixes:
                        st.write(f"• {fix}")
                    st.balloons()

        # Full report
        with st.expander("📊 Full State Report"):
            st.json(report)

        # Save report
        if st.button("💾 Save Report to File"):
            filename = save_report(report)
            st.success(f"Report saved to: {filename}")

    # State explorer
    with st.expander("🔎 State Explorer"):
        st.subheader("Current Session State")
        for key in sorted(st.session_state.keys()):
            value = st.session_state[key]
            if key not in ['db_manager', 'vendor_processor']:
                if value is None:
                    st.write(f"• **{key}**: `None`")
                elif isinstance(value, bool):
                    st.write(f"• **{key}**: `{value}`")
                elif isinstance(value, (str, int, float)):
                    st.write(f"• **{key}**: `{value}`")
                else:
                    st.write(f"• **{key}**: `{type(value).__name__}`")

elif __name__ == "__main__":
    # Running outside Streamlit
    print("State Machine Validator - Offline Mode")
    print("=" * 50)
    print("\nNote: Running without Streamlit context.")
    print("To use with live app, import this module or run through Streamlit.\n")

    # You can add mock data here for testing
    print("Example validation report structure:")
    example_report = {
        "timestamp": datetime.now().isoformat(),
        "detected_state": "search",
        "current_mode": "search",
        "is_valid": True,
        "validation_issues": [],
        "session_keys": ["db_manager", "vendor_processor", "current_mode"],
        "state_snapshot": {
            "current_mode": "search",
            "selected_vendor": None
        }
    }
    print(json.dumps(example_report, indent=2))