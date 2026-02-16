# AI Assistant - Master Context

**Version**: 3.0 | **Updated**: 2026-02-12

Orient to this file first. It establishes baseline patterns, principles, and technology context for all work in this repository. Local `CLAUDE.md` files in subdirectories provide project-specific overrides and details.

---

## Quick Reference

### Project Template
- **Project Name**: [PROJECT_NAME]
- **Purpose**: [One sentence]
- **Phase**: [Development/Testing/Production/Maintenance]
- **Key Files**: [3-5 most important files]
- **Active Work**: [Current focus]

### Technology Stack
- **Language**: Python 3.11+
- **Database**: Snowflake (EDLDB) -- Vertica is fully sunset; mention only for legacy file disambiguation
- **Framework**: [Streamlit-in-Snowflake / FastAPI / CLI]
- **Key Libraries**: [pandas, pydantic, etc.]
- **Container Runtime**: Docker (via Colima on macOS)

### Critical Context
- **Business Rules**: [Top 2-3 non-negotiable rules]
- **Data Sources**: [Primary tables/APIs]
- **Integration Points**: [External systems]
- **Known Constraints**: [Limits, restrictions, access controls]

---

## AI Assistant Guidelines

### Using This File Across AI Platforms
This file is designed to work with any AI coding assistant (Claude, GPT, Gemini, etc.). When starting a session, use a prompt like:

> "Orient yourself to CLAUDE.md -- this is our baseline context unless I say otherwise."

The file uses `CLAUDE.md` (uppercase) at the repository root for maximum auto-discovery across tools (Claude Code, Cursor, etc.). Subdirectory files should also use `CLAUDE.md`. Do not rename to `claude-local.md` or similar -- the root-vs-subdirectory hierarchy already handles scoping.

### Character Encoding
- **Code files**: ASCII only. No emojis or special Unicode in code, strings, or comments.
- **Documentation (.md)**: Emojis/symbols acceptable for readability.
- **Rationale**: Special characters cause re-encoding issues when code passes between systems.

### Non-Code Work
This context file is primarily about coding, but the assistant may also be used for document drafting, planning, analysis, and general knowledge work. When the task is non-code:
- Follow the **Document & Analysis Standards** section below for written deliverables.
- Still follow the Decision-Making Framework for ambiguous instructions.
- Apply the same "explain why, not just what" philosophy to written analysis.
- Planning and analysis outputs should be structured, concise, and actionable.

---

## Development Philosophy

### Core Principles (Chewy)
1. **Chewy-Compatible Technologies**: Snowflake, Python, Streamlit, Docker
2. **Data Warehouse First**: EDLDB.SC_SANDBOX is the primary dev workspace
3. **Readable Code**: Annotated for technical non-programmers (see Annotation Standards)
4. **Test Meaningfully**: Evaluate test value before implementing (impact x frequency)
5. **Incremental Changes**: Small commits, unit tested, minimal integration complexity
6. **Container-First Deployment**: Docker containers via Colima; K8s handoff to Data Engineering

### Decision-Making Framework
When uncertain, follow this hierarchy:
1. **Project Context** (local CLAUDE.md) for project-specific guidance
2. **This File** for general patterns and principles
3. **Industry Standards** for well-established patterns (REST, SQL, Docker)
4. **Ask the User** for business rules, priorities, or ambiguous requirements
5. **Infer & Proceed** for technical details when the user is unavailable

### Flat Call Structures
Avoid deeply nested, recursive, or highly cyclic call graphs. They are almost always unnecessarily complex and make code difficult to read and debug. Prefer flattening call structures to 2-3 layers (4 at most).

**When encountering deep nesting in existing code**: Confirm with the user before refactoring, but default to simplification unless there is a clear reason to preserve depth (loss of functionality, meaningful efficiency cost, or divergence from a well-known and broadly adopted pattern).

**Why**: Deeply nested call chains are more often a sign of over-engineering than genuine necessity. Flat, linear code is easier to trace, test, and review.

### Platform Separation
Streamlit and CLI versions of an application should be independent deployable units. They may share business logic modules and snippet patterns, but should not create cross-platform runtime dependencies. Treat them as separate apps that happen to use common libraries -- the same reason you would not create internal dependencies between macOS and Windows versions of an application.

---

## Code Annotation Standards

### Mandatory (every function, no exceptions)
```python
def function_name(param: Type) -> ReturnType:
    """
    [1-2 sentence purpose statement]

    Args:
        param: [Description with business context]

    Returns:
        [Description with expected structure/format]
    """
```

### Optional (use when they materially affect correctness, errors, or code review)
- **Additional context**: Business logic rationale, technical approach
- **Important Notes**: Library choices, performance characteristics, business rules
- **Raises**: Expected exceptions and when they occur

**Guideline**: Treat optional sections as mandatory on a case-by-case basis whenever omitting them would lead to errors, omissions, or reduced efficacy of code review. When in doubt, annotate -- favor too much over too little.

### Inline Comments
Use inline comments when:
1. **Parameter scope is unclear** or deviates from usage elsewhere in the script
2. **Uncommon constructs** are used (ternaries, lambdas, list comprehensions with side effects, complex unpacking)
3. **Cross-cutting concerns** are not obvious to a narrowly focused reader (e.g., `# prevents SQL injection`, `# allows external system to wait gracefully during processing`, `# required for Snowflake session timeout`)

Explain "why", not "what". The code shows what; the comment explains why it matters.

---

## Project Structure

### Recommended for Standalone Projects
```
project-name/
+-- CLAUDE.md              # AI context (project-specific)
+-- README.md              # Human documentation
+-- requirements.txt       # Python dependencies
+-- core/                  # Business logic (no UI dependencies)
+-- ui/                    # Interface layer (imports from core, never vice versa)
+-- utils/                 # Reusable functions (no project-specific logic)
+-- tests/                 # Mirrors source structure
+-- config/                # Configuration
```

### Streamlit-in-Snowflake Apps
SiS apps deploy as a flat file set within Snowflake Projects. The standalone structure above is too heavy. Instead:
```
project-name/
+-- CLAUDE.md              # AI context
+-- streamlit_app.py       # Main entry point (required name)
+-- database_manager.py    # DB operations module
+-- business_logic.py      # Validation, processing, rules
+-- environment.yml        # Conda dependencies (SiS requirement)
```

### Key Conventions
- **Business logic** never imports from UI modules
- **UI modules** import from business logic, never the reverse
- **Shared utilities** go in a separate module with no project-specific logic
- **Tests** mirror the source structure they cover

---

## Snowflake Patterns

### Standalone Connection Pattern
For scripts, CLI tools, and batch jobs that run outside Snowflake:
```python
import snowflake.connector
from typing import Optional

class SnowflakeManager:
    """Snowflake connection with Chewy defaults"""

    def __init__(self, warehouse: str = None, role: str = None):
        """
        Initialize with user's assigned Snowflake defaults.

        Args:
            warehouse: Override warehouse (defaults to user's assigned WH)
            role: Override role (defaults to user's assigned role)
        """
        # Replace these with your assigned Snowflake credentials/role
        self.connection_params = {
            'account': 'chewy.us-east-1',
            'warehouse': warehouse or '<YOUR_DEFAULT_WAREHOUSE>',
            'database': 'EDLDB',
            'schema': 'SC_SANDBOX',
            'role': role or '<YOUR_DEFAULT_ROLE>'
        }
        self._connection: Optional[snowflake.connector.SnowflakeConnection] = None

    def get_connection(self) -> snowflake.connector.SnowflakeConnection:
        """Get or create connection with auto-reconnect"""
        if not self._connection or self._connection.is_closed():
            self._connection = snowflake.connector.connect(**self.connection_params)
        return self._connection
```

### Streamlit-in-Snowflake Connection Pattern
**CRITICAL**: SiS apps use `get_active_session()` -- never `snowflake.connector.connect()` with credentials.

```python
from snowflake.snowpark.context import get_active_session

class DatabaseManager:
    """Database operations for Streamlit-in-Snowflake apps"""

    def __init__(self):
        self.session = None
        self._initialize_session()

    def _initialize_session(self):
        """
        Initialize Snowpark session from SiS environment.

        Returns:
            None (sets self.session)

        Important Notes:
            - get_active_session() is the only valid connection method in SiS
            - Set STATEMENT_TIMEOUT to prevent long-running queries
            - Attempt dedicated warehouse, fall back to default gracefully
        """
        from snowflake.snowpark.context import get_active_session
        self.session = get_active_session()
        if not self.session:
            raise ConnectionError("No active session. Must run in Streamlit-in-Snowflake.")

        # Prevent runaway queries
        try:
            self.session.sql("ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 30").collect()
        except Exception as e:
            logger.warning(f"Could not set session timeout: {e}")

        # Prefer dedicated Streamlit warehouse, fall back to default
        try:
            self.session.sql("USE WAREHOUSE STREAMLIT_XS_WH").collect()
        except Exception:
            pass  # Default warehouse is acceptable

    def get_session(self):
        """Lazy session accessor with auto-reconnect"""
        if not self.session:
            self._initialize_session()
        return self.session
```

**SiS Anti-Patterns**:
- BAD: `snowflake.connector.connect(user=..., password=...)` -- standalone pattern, will not work
- BAD: Module-level `session = get_active_session()` -- can hang on app load
- BAD: Test queries in `__init__` with `.collect()` -- blocks initialization
- GOOD: Lazy initialization, defensive error handling, session timeout

**SiS Defensive Initialization** (in `streamlit_app.py`):
```python
if 'db_manager' not in st.session_state:
    try:
        st.session_state.db_manager = DatabaseManager()
    except Exception as e:
        st.session_state.db_manager = None  # Allow app to load
        logger.error(f"DB init failed: {e}")
```

### Caching in Streamlit-in-Snowflake
**Cache user intent and navigation state** (search terms, pagination, selected tabs). This preserves continuity when users navigate back to a previous screen.

**Never cache data that represents current DB state** (search results, edit form values, receipt/confirmation data). These must always reflect real-time database state to prevent stale reads after writes.

**Principle**: If another user (or this user in another tab) could change the underlying data, do not cache it. If it is purely local to this user's navigation flow, caching is safe.

```python
# GOOD: Cache navigation state
if 'search_type' not in st.session_state:
    st.session_state.search_type = "Vendor Number"

# BAD: Caching DB query results with long TTL
@st.cache_data(ttl=300)  # 5 min -- stale data risk on edit screens
def get_vendor(vendor_id): ...

# GOOD: Fresh query for data that may have just been modified
def get_vendor(vendor_id):
    return db_manager.query_vendor(vendor_id)  # Always current
```

### Snowflake Pitfalls
1. **Row-by-Row Inserts**: Use batch inserts (10K+ rows)
   - BAD: `for row in df: cursor.execute(insert_sql, row)`
   - GOOD: `write_pandas()` or `chunksize=10000`

2. **Fetching Everything**: Don't `fetchall()` when you need a DataFrame
   - GOOD: `pd.read_sql(query, con)` or `fetch_pandas_batches()`

3. **Connection Leaks**: Always use context managers: `with conn.cursor() as cur:`

4. **Warehouse Sizing**: X-Small/Small for dev, scale for production workloads

---

## Testing

### Evaluation Framework
Before writing tests, assess: **Impact** (production failure severity) x **Frequency** (how often the code path runs).

```
High Impact + High Frequency = MUST TEST
High Impact + Low Frequency = TEST
Low Impact + High Frequency = CONSIDER
Low Impact + Low Frequency = SKIP
```

### Structure
Follow standard pytest idioms: fixtures for setup, Arrange/Act/Assert pattern, class grouping by component. See [pytest documentation](https://docs.pytest.org/en/stable/) for conventions.

```python
import pytest

class TestVendorProcessor:
    @pytest.fixture
    def processor(self):
        return VendorProcessor(validation_rules=get_test_rules())

    def test_tier2_requires_6months(self, processor):
        """Impact: High | Frequency: High"""
        result = processor.validate_vendor({"tier": "Tier2", "vendor_id": "12345"})
        assert result.requires_6months is True

    def test_empty_vendor_list(self, processor):
        """Impact: High | Frequency: Low"""
        result = processor.process_vendors([])
        assert result.status == "success"
```

### When to Skip Tests
- Trivial getters/setters with no logic
- Pass-through functions that delegate to already-tested code
- Framework-provided functionality
- Throwaway prototypes

### Testing Anti-Patterns
- BAD: Testing private methods directly (test public behavior instead)
- BAD: Over-specified assertions (`assert result == {full_dict_with_timestamp}`)
- BAD: Test interdependence (test_b assumes test_a ran first)
- GOOD: Each test sets up its own state via fixtures

---

## Data Management Patterns

### ETL Pattern
```python
def extract_transform_load(source_query: str, target_table: str) -> ProcessingResult:
    """
    Standard ETL with validation and atomic loading.

    Args:
        source_query: SQL to extract source data
        target_table: Destination Snowflake table

    Returns:
        ProcessingResult with row counts and any errors
    """
    try:
        df = pd.read_sql(source_query, snowflake_conn)
        df_clean = validate_and_transform(df)
        errors = check_business_rules(df_clean)
        if errors:
            return ProcessingResult(status="error", errors=errors)

        load_to_staging(df_clean, f"{target_table}_STAGING")
        swap_tables(f"{target_table}_STAGING", target_table)
        return ProcessingResult(status="success", row_count=len(df_clean))
    except Exception as e:
        logger.error(f"ETL failed: {e}")
        rollback_staging_table(target_table)
        raise
```

### Pydantic Validation
```python
from pydantic import BaseModel, validator, Field

class VendorRecord(BaseModel):
    vendor_id: str = Field(..., min_length=3, max_length=20)
    vendor_name: str = Field(..., max_length=350)
    tier: str = Field(..., regex="^(Tier1|Tier2|3Months|6Months)$")
    email_to: Optional[str] = None

    @validator('email_to')
    def validate_email_list(cls, v):
        """Validates semicolon-separated email lists"""
        if not v:
            return v
        for email in [e.strip() for e in v.split(';')]:
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                raise ValueError(f"Invalid email: {email}")
        return v
```

---

## Python Pitfalls

1. **DataFrame Copies**: `df[df['col'] > 0]` may be a view. Use `.copy()` when modifying.
2. **Row Iteration**: Prefer `df.apply()` or vectorized operations over `iterrows()`.
3. **Memory**: Use `chunksize` for large queries. Clear unused frames with `del df; gc.collect()`.

---

## Error Handling

### Standard Pattern
```python
@dataclass
class ProcessingResult:
    status: str  # "success", "error", "warning"
    data: Any = None
    message: str = ""
    errors: list = None

def process_with_error_handling(data: Dict[str, Any]) -> ProcessingResult:
    """
    Template for functions that should not raise to the UI layer.

    Args:
        data: Input data to process

    Returns:
        ProcessingResult with structured status and error info
    """
    try:
        if not data:
            return ProcessingResult(status="error", message="No data", errors=["NO_DATA"])
        result = perform_business_logic(data)
        return ProcessingResult(status="success", data=result)
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        return ProcessingResult(status="error", message="Validation failed", errors=[str(e)])
    except DatabaseError as e:
        logger.error(f"DB error: {e}", exc_info=True)
        return ProcessingResult(status="error", message="DB operation failed", errors=["DB_ERROR"])
```

**Principles**: Return result objects (don't raise to UI). Log ERROR for technical failures (with `exc_info=True`), WARNING for business rule violations. Never log credentials or PII.

---

## Architecture Anti-Patterns

1. **Business logic in UI**: Keep SQL, validation, and processing in `core/` or dedicated modules
2. **Circular imports**: Business logic must never import from UI modules
3. **God classes**: Break 30-method classes into focused components (Validator, Repository, Service)
4. **Deep nesting**: See "Flat Call Structures" above

---

## Deployment

### Dockerfile (Standard)
```dockerfile
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "print('healthy')" || exit 1

CMD ["python", "main.py"]
```

**Runtime**: Chewy uses Colima (not Docker Desktop) as the local container runtime on macOS. Dockerfiles and docker-compose files are identical -- Colima runs the standard Docker Engine. Start Colima with: `colima start --vm-type vz --mount-type virtiofs` (macOS 13+) to avoid volume mount permission issues.

**Kubernetes**: K8s deployment is handled by Data Engineering. Include K8s-friendly patterns (health checks, env-based config) when low-cost, but don't design for K8s unless explicitly required.

### Environment Configuration
```bash
# Development
DB_DATABASE=EDLDB
DB_SCHEMA=SC_SANDBOX
DB_WAREHOUSE=<YOUR_DEV_WAREHOUSE>    # e.g. SC_AUTOSHIP_WH, STREAMLIT_XS_WH
DB_ROLE=<YOUR_ASSIGNED_ROLE>         # e.g. SC_AUTOSHIP_USER
LOG_LEVEL=DEBUG
ENVIRONMENT=development

# Production
DB_DATABASE=EDLDB
DB_SCHEMA=SC_PRODUCTION
DB_WAREHOUSE=<YOUR_PROD_WAREHOUSE>
DB_ROLE=<YOUR_ASSIGNED_ROLE>
LOG_LEVEL=INFO
ENVIRONMENT=production
```

---

## Library Quick Reference

| Need | Use | Notes |
|------|-----|-------|
| Snowflake (standalone) | `snowflake-connector-python` | Official connector |
| Snowflake (SiS) | `snowflake-snowpark-python` | Via `get_active_session()` |
| Data manipulation | `pandas` | Industry standard, Snowflake native support |
| Validation | `pydantic` | Runtime validation with clear error messages |
| API framework | `fastapi` | Async, auto-docs |
| CLI framework | `click` or `argparse` | click for complex CLIs, argparse for simple |
| Testing | `pytest` | Fixtures, parametrization |

---

## Document & Analysis Standards

These standards apply when drafting planning documents, proposals, comparison analyses, vision docs, or any written deliverable intended for stakeholders. Chewy's culture derives strongly from Amazon; these patterns reflect that lineage.

### Writing Principles

1. **Work backwards**: Start from the customer or stakeholder outcome, then describe how to get there. Never lead with the solution.
2. **The "so what" test**: Every section must answer "why does this matter" within its first two sentences. If it doesn't, rewrite the opening.
3. **Narrative-first, data-second**: Open with plain-language explanation of the problem or opportunity. Data, tables, and metrics support the narrative -- they don't replace it.
4. **Direct voice**: State positions clearly. "We need X" not "It might be beneficial to consider X." Passive hedging undermines the document's purpose.
5. **Mechanisms over heroics**: Propose repeatable processes, not one-time efforts. If a solution depends on a single person's sustained effort, it is not a solution.
6. **Write to decide, not to inform**: Documents should drive decisions. Every document should have a clear ask or recommendation. If there is no decision to be made, reconsider whether the document is necessary.

### Document Structure

Use tiered depth so readers self-select their level of detail:

```
Executive Summary        (1 paragraph -- the whole story in brief)
Current State            (where we are, what's working, what isn't)
Problem / Opportunity    (the "why now")
Proposed Actions         (what we will do, framed as Defect/Action/ETA)
Long-Term Vision         (where this leads in 1-2 years)
FAQ / Risks              (preempt objections; address them directly)
Appendices               (supporting data, tables, detailed breakdowns)
```

**Deliverable framing** -- use the Defect/Action/ETA pattern:
- **Defect**: What is the current gap or pain point?
- **Action**: What will be done to address it?
- **ETA**: When will it be delivered?

**FAQ as persuasion**: FAQ sections are not afterthoughts. Use them to surface disagreements transparently, preempt objections, and propose resolutions. A strong FAQ answers "but what about..." before the reader asks.

### Comparison & Alternatives Analysis

When evaluating options, use structured comparison tables with consistent dimensions across all candidates. Dimensions should include at minimum:
- Level of effort (build vs. sustain)
- Advantages and risks
- Data governance / extensibility
- Dependencies on other teams

The recommendation should be self-evident from the analysis. If the table doesn't make the answer obvious, the dimensions need refinement -- not more prose.

### Tone & Conventions

- Match the tone of existing documents in the repo when drafting in an established context
- Use Chewy's terminology (IMPACT, ICC, ISM, etc.) when the audience expects it
- Avoid jargon when writing for cross-functional audiences; define acronyms on first use
- Confidentiality markings (e.g., "Chewy Confidential -- For Internal Use Only") should be applied to documents containing operational data or vendor-specific information

---

## Documentation Hierarchy

**Root CLAUDE.md** (this file): Abstract patterns, general principles, "why" explanations.

**Local CLAUDE.md** (project subdirectories): Concrete implementations, actual class names, project-specific workflows, business rules.

**Timing**: Add workflow documentation *after* implementation -- extract patterns from working code, not before it exists.

### Creating a Local CLAUDE.md
1. Fill in the Quick Reference template with project specifics
2. Document non-obvious business rules
3. List actual table names, API endpoints, integration points
4. Note known issues and workarounds
5. Delete sections from the template that do not apply
6. Add workflow examples only after the code works

---

## References

### Chewy Resources
- Snowflake: [Internal Portal]
- OKTA Auth: [Internal Docs]
- Container Registry: [Internal Registry]

### External Docs
- [Snowflake](https://docs.snowflake.com/) | [Pandas](https://pandas.pydata.org/docs/) | [FastAPI](https://fastapi.tiangolo.com/) | [Streamlit](https://docs.streamlit.io/) | [Pydantic](https://docs.pydantic.dev/) | [pytest](https://docs.pytest.org/)
