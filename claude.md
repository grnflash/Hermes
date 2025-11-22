# Claude AI Assistant - Master Context

**Template Version**: 2.1  
**Last Updated**: [DATE]  
**Purpose**: Efficient AI assistant context for rapid project convergence

---

## **Quick Reference - Read This First**

### **Project Type & Current State**
- **Project Name**: [PROJECT_NAME]
- **Primary Purpose**: [One sentence - what problem does this solve?]
- **Current Phase**: [Development/Testing/Production/Maintenance]
- **Key Files**: [List 3-5 most important files to understand the project]
- **Active Work**: [Current sprint/tasks/focus areas]

### **Technology Stack**
- **Language**: Python 3.11+
- **Database**: Snowflake (EDLDB) | Vertica (legacy)
- **Framework**: [Streamlit/FastAPI/CLI]
- **Key Libraries**: [pandas, sqlalchemy, etc.]
- **Deployment**: [Docker/Kubernetes/Local]

### **Critical Context**
- **Business Rules**: [Top 2-3 non-negotiable business rules]
- **Data Sources**: [Primary tables/APIs this project uses]
- **Integration Points**: [External systems this connects to]
- **Known Constraints**: [Performance limits, data restrictions, access controls]

---

## **AI Assistant Guidelines**

### **Character Encoding & Special Characters**
- **Code Files**: Use only ASCII characters (avoid emojis, special Unicode symbols)
- **Documentation (.md)**: Emojis/symbols acceptable for readability (AI assistants can parse these)
- **UI Elements**: Special characters allowed when explicitly part of user interface
- **Default Encoding**: UTF-8 for all files, but avoid characters that require it in code

**Rationale**: Special characters in code cause interoperability issues when snippets are passed to other systems, requiring re-encoding. This adds unnecessary retry cycles.

**Examples**:
```python
# ❌ Avoid in code files
def process_data():  # ✅ Status
    return {"status": "✓"}  # ❌ Checkmark in output

# ✅ Correct approach
def process_data():  # Status: success
    return {"status": "success"}  # Use words, not symbols
```

---

## **Development Philosophy & Priorities**

### **Working at Chewy - Core Principles**
1. **Favor Chewy-Compatible Technologies**: Snowflake, Python, Streamlit, Docker
2. **Data Warehouse First**: EDLDB.SC_SANDBOX is primary workspace for development
3. **Rich Annotation**: Code should be readable by technical non-programmers
4. **Test Meaningfully**: Evaluate test value before implementing (impact × frequency)
5. **Incremental CI/CD**: Small changes, unit tested, minimal integration complexity
6. **Docker-First Deployment**: Target Docker containers; Kubernetes readiness is a future consideration

### **Decision-Making Framework**
When uncertain, follow this hierarchy:
1. **Check Project Context** (this file) for project-specific guidance
2. **Industry Standards** for well-established patterns (REST, SQL, Docker)
3. **Ask User** for business rules, priorities, or ambiguous requirements
4. **Infer & Proceed** for technical implementation details if user is unavailable

### **Code Annotation Standards**
Every function MUST include:
```python
def function_name(param: Type) -> ReturnType:
    """
    [1-2 sentence purpose statement]
    
    [Additional context about business logic or technical approach]
    
    Args:
        param: [Description with business context]
        
    Returns:
        [Description with expected structure/format]
        
    Important Notes:
        - [Why specific libraries are chosen vs. alternatives]
        - [Performance characteristics: O(n), expected throughput]
        - [Business rules applied]
        - [Chewy-specific considerations]
        
    Raises:
        [Expected exceptions and when they occur]
    """
```

**Annotation Philosophy**: Favor too much over too little. Use inline comments for complex sections. Explain "why" not just "what".

---

## **Standard Project Structure**

```
project-name/
├── claude.md              # AI context (this file)
├── README.md              # Human documentation
├── requirements.txt       # Python dependencies
├── core/                  # Business logic
│   ├── database_manager.py
│   ├── business_logic.py
│   └── data_models.py
├── ui/                    # Interfaces (CLI/Streamlit)
├── utils/                 # Shared utilities
├── tests/                 # Test suite
│   ├── unit/
│   ├── integration/
│   └── test_data/
├── config/                # Configuration
└── docs/                  # Additional docs
```

**Key Conventions**:
- **core/**: Pure business logic, no UI dependencies
- **ui/**: Interface layer, imports from core, never vice versa
- **utils/**: Reusable functions with no project-specific business logic
- **tests/**: Mirror source structure (tests/core/, tests/ui/)

---

## **Chewy-Specific Technology Patterns**

### **Snowflake Connection Pattern**
```python
import snowflake.connector
from typing import Optional

class SnowflakeManager:
    """Standard Snowflake connection with Chewy configurations"""
    
    def __init__(self, account: str = None, warehouse: str = None):
        """
        Initialize Snowflake manager with Chewy defaults
        
        Args:
            account: Snowflake account (defaults to Chewy account)
            warehouse: Compute warehouse (defaults to CHEWY_ANALYST_WH)
            
        Important Notes:
            - Uses CHEWY_ANALYST_ROLE for standard access
            - Targets EDLDB database by default
            - SC_SANDBOX schema for development work
            - Auto-reconnect on connection loss
        """
        self.connection_params = {
            'account': account or 'chewy.us-east-1',
            'warehouse': warehouse or 'CHEWY_ANALYST_WH',
            'database': 'EDLDB',
            'schema': 'SC_SANDBOX',
            'role': 'CHEWY_ANALYST_ROLE'
        }
        self._connection: Optional[Connection] = None
    
    def get_connection(self) -> Connection:
        """Get or create connection with auto-retry"""
        if not self._connection or not self._is_connected():
            self._connection = snowflake.connector.connect(**self.connection_params)
        return self._connection
```

**Why This Pattern**:
- Chewy uses specific roles/warehouses for access control
- EDLDB is standard data warehouse
- SC_SANDBOX is dev/test schema
- Auto-reconnect handles intermittent network issues

### **Streamlit vs. CLI Decision Matrix**

| Use Streamlit When | Use CLI When |
|-------------------|--------------|
| Occasional users | Frequent/power users |
| Visual data exploration | Automated/scripted workflows |
| Multiple input fields | Simple, few parameters |
| Business user audience | Technical user audience |
| Browser-based access OK | Speed is critical |

### **Common Library Choices & Rationale**

| Need | Use | Why (vs. alternatives) |
|------|-----|------------------------|
| Snowflake connection | `snowflake-connector-python` | Official, well-maintained, Chewy standard |
| Vertica connection | `vertica-python` | Better than pyodbc for Vertica-specific features |
| ODBC (if required) | `pyodbc` | Windows compatibility, Chewy ODBC DSN support |
| Data manipulation | `pandas` | Industry standard, Snowflake native support |
| Type validation | `pydantic` | Runtime validation, excellent error messages |
| API framework | `fastapi` | Modern, async, auto-docs, Chewy approved |
| CLI framework | `click` or `argparse` | click for complex, argparse for simple |
| Testing | `pytest` | Fixture system, parametrization, industry standard |

---

## **Testing Strategy & Evaluation**

### **Test Evaluation Framework**
Before implementing tests, ask:
1. **Impact**: Could this fail in production and cause significant issues?
2. **Frequency**: How often will this code path execute?
3. **Complexity**: Is the code complex enough to benefit from tests?
4. **Risk**: Is manual testing sufficient, or do we need automation?

**Test Priority Matrix**:
```
High Impact + High Frequency = MUST TEST (business logic, data validation)
High Impact + Low Frequency = TEST (edge cases, critical failures)
Low Impact + High Frequency = CONSIDER (performance, user experience)
Low Impact + Low Frequency = SKIP (trivial paths, obvious code)
```

### **Standard Test Structure**
```python
# tests/core/test_business_logic.py
import pytest
from unittest.mock import Mock, patch
from core.business_logic import VendorProcessor

class TestVendorProcessor:
    """Test suite for VendorProcessor with focus on business rules"""
    
    @pytest.fixture
    def processor(self):
        """Fixture providing configured processor instance"""
        return VendorProcessor(validation_rules=self._get_test_rules())
    
    def test_tier2_requires_6months(self, processor):
        """
        Test critical business rule: Tier2 vendors must have 6Months entries
        
        Impact: High - could break vendor email distribution
        Frequency: High - runs on every vendor update
        """
        # Arrange
        vendor_data = {"tier": "Tier2", "vendor_id": "12345"}
        
        # Act
        result = processor.validate_vendor(vendor_data)
        
        # Assert
        assert result.requires_6months is True
        assert "6Months" in result.required_entries
    
    def test_edge_case_empty_vendor_list(self, processor):
        """
        Test edge case: empty vendor list should not crash
        
        Impact: High - could crash batch processing
        Frequency: Low - rare but possible
        """
        result = processor.process_vendors([])
        assert result.status == "success"
        assert result.processed_count == 0
```

### **When to Skip Tests**
- Trivial getters/setters with no logic
- Pass-through functions that just call other tested code
- Framework-provided functionality (e.g., Django ORM methods)
- Code you'll delete soon (prototypes, experiments)

---

## **Data Management Patterns**

### **Standard ETL Pattern**
```python
def extract_transform_load(source_query: str, target_table: str) -> ProcessingResult:
    """
    Standard ETL pattern with validation and error handling
    
    Args:
        source_query: SQL query to extract source data
        target_table: Target Snowflake table
        
    Returns:
        ProcessingResult with counts and any errors
        
    Important Notes:
        - Validates data before loading (fail fast)
        - Uses staging table for atomic loads
        - Logs all transformations for audit
        - Performance: Batch size 10K rows for optimal Snowflake loading
    """
    try:
        # Extract
        df = pd.read_sql(source_query, snowflake_conn)
        logger.info(f"Extracted {len(df)} rows from source")
        
        # Transform & Validate
        df_clean = validate_and_transform(df)
        validation_errors = check_business_rules(df_clean)
        if validation_errors:
            return ProcessingResult(status="error", errors=validation_errors)
        
        # Load (atomic via staging)
        load_to_staging(df_clean, f"{target_table}_STAGING")
        swap_tables(f"{target_table}_STAGING", target_table)
        
        return ProcessingResult(status="success", row_count=len(df_clean))
        
    except Exception as e:
        logger.error(f"ETL failed: {e}")
        rollback_staging_table(target_table)
        raise
```

### **Common Data Validation Patterns**
```python
# Use Pydantic for structured validation
from pydantic import BaseModel, validator, Field

class VendorRecord(BaseModel):
    """Vendor record with Chewy business rule validation"""
    
    vendor_id: str = Field(..., min_length=3, max_length=20)
    vendor_name: str = Field(..., max_length=350)
    tier: str = Field(..., regex="^(Tier1|Tier2|3Months|6Months)$")
    email_to: Optional[str] = None
    email_cc: Optional[str] = None
    
    @validator('email_to', 'email_cc')
    def validate_email_list(cls, v):
        """Validate semicolon-separated email lists"""
        if not v:
            return v
        emails = [e.strip() for e in v.split(';')]
        for email in emails:
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                raise ValueError(f"Invalid email format: {email}")
        return v
    
    @validator('tier')
    def validate_tier2_pairing(cls, v, values):
        """Tier2 requires corresponding 6Months entry (checked at service level)"""
        # This is a marker for the service layer to enforce
        return v
```

---

## **Common Pitfalls & Anti-Patterns**

### **Snowflake-Specific Pitfalls**
1. **Row-by-Row Inserts**: Use batch inserts (10K+ rows)
   - BAD: `for row in df: cursor.execute(insert_sql, row)`
   - GOOD: `df.to_sql(table, con, method='multi', chunksize=10000)`

2. **Result Set Fetching**: Don't fetch all rows unnecessarily
   - BAD: `cursor.execute(query); all_rows = cursor.fetchall()`
   - GOOD: `pd.read_sql(query, con)` or cursor with `fetch_pandas_batches()`

3. **Connection Leaks**: Always close connections
   - GOOD: Use context managers: `with conn.cursor() as cur:`

4. **Warehouse Costs**: Remember to use appropriate warehouse size
   - Development: X-Small or Small
   - Production: Scale based on workload

### **Python/Pandas Pitfalls**
1. **DataFrame Copies**: Be aware of views vs. copies
   - BAD: `df_subset = df[df['col'] > 0]` (might be a view)
   - GOOD: `df_subset = df[df['col'] > 0].copy()` (explicit copy)

2. **Iterating DataFrames**: Avoid row iteration where possible
   - BAD: `for idx, row in df.iterrows():`
   - GOOD: `df.apply()` or vectorized operations

3. **Memory Management**: Large DataFrames can exhaust memory
   - Use chunking: `pd.read_sql(query, con, chunksize=50000)`
   - Clear unused frames: `del df; gc.collect()`

### **Testing Anti-Patterns**
1. **Testing Implementation Details**: Test behavior, not internals
   - BAD: Testing private methods directly
   - GOOD: Testing public API that uses private methods

2. **Brittle Tests**: Don't over-specify assertions
   - BAD: `assert result == {"a": 1, "b": 2, "c": 3, "timestamp": "2025-01-01"}`
   - GOOD: `assert result["a"] == 1 and result["b"] == 2`

3. **Test Interdependence**: Tests should be independent
   - BAD: test_b assumes test_a ran first
   - GOOD: Each test sets up its own fixtures

### **Architecture Anti-Patterns**
1. **UI Business Logic**: Keep business logic in core/
   - BAD: Streamlit file with SQL queries and validation logic
   - GOOD: Streamlit imports from core modules

2. **Circular Dependencies**: core/ should never import from ui/
   - BAD: `core/processor.py` imports `ui/helpers.py`
   - GOOD: Extract shared code to utils/

3. **God Classes**: Break large classes into focused components
   - BAD: VendorManager with 30 methods
   - GOOD: VendorValidator, VendorRepository, VendorService

---

## **Error Handling Standards**

### **Standard Error Pattern**
```python
import logging
from typing import Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ProcessingResult:
    """Standard result object for all operations"""
    status: str  # "success", "error", "warning"
    data: Any = None
    message: str = ""
    errors: list = None
    
class BusinessLogicError(Exception):
    """Raised when business rules are violated"""
    pass

def process_with_error_handling(data: Dict[str, Any]) -> ProcessingResult:
    """
    Standard error handling template for all processing functions
    
    Returns structured result object instead of raising exceptions
    to caller, allowing graceful error handling in UI layer
    """
    try:
        # Validate input
        if not data:
            return ProcessingResult(
                status="error",
                message="Input data is empty",
                errors=["NO_DATA"]
            )
        
        # Business logic
        result = perform_business_logic(data)
        logger.info(f"Successfully processed {len(data)} records")
        
        return ProcessingResult(status="success", data=result)
        
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        return ProcessingResult(
            status="error",
            message="Data validation failed",
            errors=[str(e)]
        )
        
    except DatabaseError as e:
        logger.error(f"Database error: {e}", exc_info=True)
        return ProcessingResult(
            status="error",
            message="Database operation failed",
            errors=["DB_CONNECTION_FAILED"]
        )
        
    except BusinessLogicError as e:
        logger.warning(f"Business rule violation: {e}")
        return ProcessingResult(
            status="warning",
            message=str(e),
            errors=["BUSINESS_RULE_VIOLATION"]
        )
```

**Key Principles**:
- Return result objects, don't raise to UI layer
- Log with appropriate level (ERROR for technical, WARNING for business)
- Include `exc_info=True` for ERROR level to capture stack traces
- Never log sensitive data (passwords, API keys, PII)

---

## **Deployment Patterns**

### **Standard Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Snowflake/ODBC
RUN apt-get update && apt-get install -y \
    gcc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment setup
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check (customize endpoint)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "print('healthy')" || exit 1

CMD ["python", "main.py"]
```

**Note on Kubernetes**: While Chewy uses Kubernetes, deployment to K8s typically involves handoff to Data Engineering teams. Focus on Docker compatibility and include Kubernetes-friendly patterns (e.g., health checks, environment-based config) when they're low-cost to implement, but don't design specifically for Kubernetes unless explicitly required.

### **Environment Configuration**
```bash
# Development
DB_DATABASE=EDLDB
DB_SCHEMA=SC_SANDBOX
DB_WAREHOUSE=CHEWY_ANALYST_WH_SMALL
LOG_LEVEL=DEBUG
ENVIRONMENT=development

# Production
DB_DATABASE=EDLDB
DB_SCHEMA=SC_PRODUCTION
DB_WAREHOUSE=CHEWY_ANALYST_WH
LOG_LEVEL=INFO
ENVIRONMENT=production
```

---

## **Project-Specific Context**

### **Documentation Hierarchy: Root vs. Local**

**Root-Level claude.md** (this file):
- Documents **abstract patterns** and **general principles**
- Provides **reusable templates** applicable across projects
- Explains **WHY** patterns exist (rationale, trade-offs)
- Examples use **generic class names** (DataManager, BusinessLogic)
- **Purpose**: Teach patterns once, apply everywhere

**Local-Level claude.md** (project subfolders):
- Documents **concrete implementations** with actual class names
- Provides **project-specific workflows** and business logic
- Shows **HOW** this project implements root patterns
- Examples use **actual project classes** (VendorBusinessLogic, DatabaseManager)
- **Purpose**: Enable immediate work on this specific project

**Workflow Documentation Strategy**:
- **Root should**: Document abstract workflow patterns (data → business → transaction)
- **Local should**: Document complete end-to-end workflows with actual code
- **Timing**: Add workflow docs AFTER implementation, not before (extract patterns from working code)
- **Relationship**: Local workflows should reference root patterns they implement

### **When You Clone This Template:**
1. **Fill Quick Reference Section** at the top with project specifics
2. **Document Business Rules** that are non-obvious or critical
3. **List Integration Points** with actual table names, API endpoints
4. **Note Known Issues** or workarounds that save debugging time
5. **Delete Irrelevant Sections** (e.g., Streamlit patterns if it's a CLI tool)
6. **Defer Workflow Examples** until implementation exists (extract from working code)

### **What to Add to Project-Specific claude.md:**
- **Data Models**: Key tables, columns, relationships
- **Business Rules**: Domain-specific logic, validation rules
- **Integration Points**: External systems, APIs, file formats
- **Known Issues**: Current bugs, technical debt, workarounds
- **Performance Notes**: Bottlenecks, optimization done/needed
- **Security Notes**: Access controls, sensitive data locations
- **Deployment Notes**: Environment-specific configurations
- **Workflow Examples**: Complete end-to-end workflows (after implementation)

### **What NOT to Add:**
- NOT: Extensive tutorials (link to external docs instead)
- NOT: Complete API documentation (maintain separately)
- NOT: Changelog (use git history)
- NOT: Extensive troubleshooting guides (maintain wiki/docs)
- NOT: Workflow examples before code exists (extract patterns empirically)

---

## **Learning Resources & References**

### **Chewy-Specific Resources**
- Snowflake Access: [Internal Snowflake Portal]
- OKTA Authentication: [Internal OKTA Docs]
- Docker Registry: [Internal Registry URL]

### **External Documentation**
- **Snowflake**: https://docs.snowflake.com/
- **Pandas**: https://pandas.pydata.org/docs/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Streamlit**: https://docs.streamlit.io/
- **Pydantic**: https://docs.pydantic.dev/

### **Code Examples in This Repo**
- Database patterns: `snippet_snowflake_connector.py`, `snippet_vertica_connector.py`
- Vendor management: `cpfr_vmgr_slt/` (Streamlit + business logic)
- Batch processing: `cpfr-vfcst-mgr2/` (bulk upload patterns)
- Testing patterns: `SCOPT-vendor-email-bulk-uploader/tests/`

---

**Template Version**: 2.1  
**Last Updated**: [DATE]  
**Maintainer**: [YOUR_NAME]  
**Next Review**: [DATE]

---

## **Changelog**

### Version 2.1 (Current)
- **Character Encoding**: Added explicit guidelines to avoid emojis/special characters in code
- **Kubernetes Clarification**: Repositioned as future/handoff consideration, not primary deployment target
- **Removed Emojis**: Replaced all emoji section markers with plain text for better interoperability
- **Anti-Pattern Updates**: Changed emoji markers (checkmark/cross) to BAD/GOOD text labels

### Version 2.0
- **Token Optimization**: Removed generic content, focused on high-value context
- **Added**: Common pitfalls, decision frameworks, Chewy-specific patterns
- **Added**: Quick Reference section for rapid orientation
- **Added**: Test evaluation framework
- **Removed**: Generic troubleshooting, boilerplate security content
- **Streamlined**: Code examples to show patterns, not complete implementations

### Version 1.0
- Initial comprehensive template
- Full coverage of all topics
