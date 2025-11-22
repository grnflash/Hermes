"""
Minimal test app to isolate DatabaseManager initialization issue
This can be temporarily renamed to streamlit_app.py to test
"""
import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CRITICAL: st.set_page_config() MUST be the first Streamlit command
st.set_page_config(
    page_title="DatabaseManager Test",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 DatabaseManager Initialization Test")

st.write("This is a minimal test to check if DatabaseManager can initialize properly.")

# Test 1: Try importing DatabaseManager
st.subheader("Test 1: Import DatabaseManager")
try:
    from database_manager import DatabaseManager
    st.success("✅ DatabaseManager imported successfully")
except Exception as e:
    st.error(f"❌ Failed to import DatabaseManager: {e}")
    st.stop()

# Test 2: Try initializing DatabaseManager
st.subheader("Test 2: Initialize DatabaseManager")
try:
    db_manager = DatabaseManager()
    st.success("✅ DatabaseManager initialized successfully")
except Exception as e:
    st.error(f"❌ Failed to initialize DatabaseManager: {e}")
    st.error(f"Error type: {type(e).__name__}")
    import traceback
    st.code(traceback.format_exc())
    st.stop()

# Test 3: Try getting session
st.subheader("Test 3: Get Session")
try:
    session = db_manager.get_session()
    if session:
        st.success("✅ Session retrieved successfully")
    else:
        st.error("❌ Session is None")
except Exception as e:
    st.error(f"❌ Failed to get session: {e}")
    st.error(f"Error type: {type(e).__name__}")
    import traceback
    st.code(traceback.format_exc())
    st.stop()

# Test 4: Try a simple query
st.subheader("Test 4: Execute Simple Query")
try:
    result = session.sql("SELECT 1 as test").collect()
    st.success(f"✅ Query executed successfully. Result: {result}")
except Exception as e:
    st.error(f"❌ Failed to execute query: {e}")
    st.error(f"Error type: {type(e).__name__}")
    import traceback
    st.code(traceback.format_exc())

st.success("🎉 All tests completed!")

