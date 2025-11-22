# Integrating State Machine Monitoring into Your App

## Quick Integration (Minimal Changes)

Add this to your `streamlit_app.py` after the imports:

```python
# State monitoring (optional - remove in production)
DEBUG_MODE = False  # Set to True for debugging

if DEBUG_MODE:
    try:
        from validate_state import validate_current_state, detect_current_state
        HAS_VALIDATOR = True
    except ImportError:
        HAS_VALIDATOR = False
else:
    HAS_VALIDATOR = False
```

Then in your `main()` function, add a debug sidebar:

```python
def main():
    st.set_page_config(
        page_title="CPFR and VC | Vendor Configuration Manager",
        page_icon="📧",
        layout="wide"
    )

    # Debug mode indicator (only if enabled)
    if DEBUG_MODE and HAS_VALIDATOR:
        with st.sidebar:
            st.markdown("### 🔍 Debug Mode")

            # Show current state
            current_state = detect_current_state()
            if current_state:
                st.success(f"State: {current_state}")
            else:
                st.warning("State: Unknown")

            # Validate button
            if st.button("Validate State"):
                issues = validate_current_state()
                if issues:
                    st.error(f"{len(issues)} issues found:")
                    for issue in issues:
                        st.warning(f"• {issue}")
                else:
                    st.success("✅ State valid")

            # State explorer
            with st.expander("State Values"):
                for key in ['current_mode', 'selected_vendor', 'search_results']:
                    val = st.session_state.get(key)
                    if val is None:
                        st.text(f"{key}: None")
                    elif isinstance(val, (str, int, bool)):
                        st.text(f"{key}: {val}")
                    else:
                        st.text(f"{key}: {type(val).__name__}")

    # Rest of your app...
```

## Production Integration (Logging Only)

For production, use logging instead of UI:

```python
import logging
from validate_state import validate_current_state, generate_state_report

# After state changes
def log_state_health():
    """Log state machine health for monitoring"""
    issues = validate_current_state()
    if issues:
        logger.warning(f"State validation issues: {issues}")

        # Generate detailed report for severe issues
        if any("CORRUPTION" in issue for issue in issues):
            report = generate_state_report()
            logger.error(f"State corruption detected: {json.dumps(report, indent=2)}")

# Call after major state transitions
def transition_to_edit(vendor):
    st.session_state.current_mode = 'edit'
    st.session_state.selected_vendor = vendor
    st.session_state.original_vendor = vendor.copy()

    # Log state health after transition
    if DEBUG_MODE:
        log_state_health()

    st.rerun()
```

## Development Workflow

### 1. Daily Development
```bash
# Set DEBUG_MODE = True in your app
# Run with state validation visible
streamlit run streamlit_app.py
```

### 2. Before Deployment
```bash
# Run standalone validator
python validate_state.py

# Generate visualization
python visualize_state_machine.py

# Review state_machine.png for any issues
```

### 3. When Issues Occur
```bash
# 1. Enable debug mode
# 2. Navigate to the problematic state
# 3. Click "Validate State"
# 4. Save the report
# 5. Check against state_machine_schema.json
```

## VSCode Integration

### Add to `.vscode/tasks.json`:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Validate State Machine",
            "type": "shell",
            "command": "python",
            "args": ["validate_state.py"],
            "group": "test",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            }
        },
        {
            "label": "Visualize State Machine",
            "type": "shell",
            "command": "python",
            "args": ["visualize_state_machine.py"],
            "group": "build",
            "problemMatcher": []
        }
    ]
}
```

### Add to `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Streamlit with Debug",
            "type": "python",
            "request": "launch",
            "module": "streamlit",
            "args": ["run", "streamlit_app.py"],
            "env": {
                "STREAMLIT_DEBUG": "1"
            }
        },
        {
            "name": "Validate State",
            "type": "python",
            "request": "launch",
            "program": "validate_state.py"
        }
    ]
}
```

## Maintaining the State Machine

### When Adding New Features

1. **Before coding**, update `state_machine_schema.json`:
   - Add new states
   - Define transitions
   - Set corruption risk levels

2. **Update the validators**:
   ```python
   # In validate_state.py, add to VALID_STATES:
   'new_feature_state': {
       'current_mode': 'new_feature',
       'required': ['db_manager', 'new_feature_data'],
       'description': 'New feature description'
   }
   ```

3. **Test the state flow**:
   ```bash
   python visualize_state_machine.py
   # Review the generated diagram
   ```

### When Debugging Issues

1. **Enable state capture**:
   ```python
   # Add to problematic function
   if DEBUG_MODE:
       report = generate_state_report()
       with open(f"state_dump_{datetime.now():%Y%m%d_%H%M%S}.json", 'w') as f:
           json.dump(report, f, indent=2)
   ```

2. **Compare states**:
   ```python
   # Load and compare state dumps
   import json

   with open("state_dump_working.json") as f:
       working = json.load(f)

   with open("state_dump_broken.json") as f:
       broken = json.load(f)

   # Find differences
   for key in working['state_snapshot']:
       if working['state_snapshot'][key] != broken['state_snapshot'].get(key):
           print(f"Difference in {key}:")
           print(f"  Working: {working['state_snapshot'][key]}")
           print(f"  Broken:  {broken['state_snapshot'].get(key)}")
   ```

## Excel/Office Integration

The `state_transitions.csv` file can be:
1. Opened in Excel for easy viewing/editing
2. Imported into PowerBI for visualization
3. Used in Power Automate for monitoring

To update from Excel:
1. Edit `state_transitions.csv` in Excel
2. Save as CSV
3. Run: `python update_schema_from_csv.py` (you'd need to create this)

## Benefits of This Approach

1. **Clear documentation** - Always know what state the app should be in
2. **Easy debugging** - Quickly identify corruption patterns
3. **Preventive maintenance** - Catch issues before users report them
4. **Knowledge transfer** - New developers understand the app flow
5. **Multiple formats** - JSON for code, CSV for Excel, diagrams for docs

## Quick Commands Cheat Sheet

```bash
# Check current state health
python -c "from validate_state import generate_state_report; import json; print(json.dumps(generate_state_report(), indent=2))"

# Generate all visualizations
python visualize_state_machine.py

# Open state diagram (Windows)
start state_machine.png

# Open state diagram (Mac)
open state_machine.png

# View in Excel (Windows)
start state_transitions.csv

# Quick validate (if Streamlit running)
curl http://localhost:8501/_stcore/health
```