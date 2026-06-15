# Walkthrough Phase 1, 2 va 4

Tai lieu nay tong hop nhung thay doi va buoc verification da thuc hien cho:

- Phase 1: khoi tao va baseline;
- Phase 2: correlation ID, log enrichment va PII scrubbing;
- Phase 4: Langfuse tracing.

Phase 3 duoc ghi rieng trong `docs/phase3-walkthrough.md`.

## Phase 1 - Khoi tao va baseline

### 1. Moi truong

Repo su dung virtual environment tai `.venv` va dependencies trong
`requirements.txt`.

Nhung package chinh da duoc xac nhan:

```text
fastapi 0.118.0
structlog 25.4.0
langfuse 3.2.1
pytest 8.3.5
```

File `.env` da co:

- `APP_ENV`;
- `APP_NAME`;
- `LOG_LEVEL`;
- `LOG_PATH`;
- `LANGFUSE_PUBLIC_KEY`;
- `LANGFUSE_SECRET_KEY`;
- `LANGFUSE_HOST`.

Secrets khong duoc ghi vao tai lieu va `.env` da nam trong `.gitignore`.

### 2. Baseline commands

Chay test:

```bash
.venv/bin/pytest -q
```

Ket qua cuoi:

```text
8 passed
```

Khoi dong app:

```bash
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Kiem tra health:

```bash
curl http://127.0.0.1:8000/health
```

Response sau khi hoan thanh Phase 4:

```json
{
  "ok": true,
  "tracing_enabled": true,
  "incidents": {
    "rag_slow": false,
    "tool_fail": false,
    "cost_spike": false
  }
}
```

## Phase 2 - Logging va PII

### 1. Correlation ID

File: `app/middleware.py`

`CorrelationIdMiddleware` da duoc hoan thien theo flow:

1. Goi `clear_contextvars()` o dau request.
2. Doc header `x-request-id`.
3. Neu header rong, sinh ID dang `req-<8-char-hex>`.
4. Bind `correlation_id` vao structlog context.
5. Luu ID vao `request.state.correlation_id`.
6. Tra ve `x-request-id` va `x-response-time-ms`.

Test bao phu:

- giu nguyen request ID do client gui;
- tu sinh ID khi header bi thieu;
- nam request song song co context rieng, khong ro ri session/correlation ID.

### 2. Log enrichment

File: `app/main.py`

Endpoint `/chat` bind cac field sau truoc khi ghi log:

```text
user_id_hash
session_id
feature
model
env
correlation_id
```

Raw `user_id` khong duoc ghi vao log. Cac event `request_received`,
`response_sent` va `request_failed` dung chung request context.

Sau Phase 4, log `response_sent` con co `trace_id`, giup di tu log sang Langfuse
trace khi dieu tra incident.

### 3. PII scrubbing

Files:

- `app/logging_config.py`;
- `app/pii.py`.

`scrub_event` duoc dat trong structlog processor chain truoc JSON renderer va
file writer. Scrubber xu ly de quy string, dictionary, list va tuple.

Nhung pattern duoc redact:

- email;
- so dien thoai Viet Nam;
- CCCD;
- credit card;
- passport;
- dia chi Viet Nam.

Vi du:

```text
student@vinuni.edu.vn -> [REDACTED_EMAIL]
4111-1111-1111-1111 -> [REDACTED_CREDIT_CARD]
```

Regex passport chi nhan chu cai in hoa va bay chu so:

```regex
\b[A-Z]\d{7}\b
```

Dieu nay tranh redact nham correlation ID nhu `req-e3606108`.

### 4. Verification Phase 2

Validator cuoi cung:

```text
Total log records analyzed: 23
Records with missing required fields: 0
Records with missing enrichment (context): 0
Unique correlation IDs found: 11
Potential PII leaks detected: 0
Estimated Score: 100/100
```

## Phase 4 - Langfuse tracing

### 1. Van de trong starter code

Starter code import:

```python
from langfuse.decorators import observe, langfuse_context
```

Module nay khong ton tai trong `langfuse==3.2.1`. Exception bi fallback layer
nuot, nen decorator tro thanh no-op va khong co trace nao duoc gui.

Ung dung cung chua goi `load_dotenv()`, nen Langfuse credentials trong `.env`
khong duoc nap khi khoi dong app.

### 2. Langfuse v3 integration

File: `app/tracing.py`

Da chuyen sang API v3:

```python
from langfuse import get_client, observe
```

File tracing:

- nap `.env` truoc khi tao client;
- cung cap `tracing_enabled()`;
- cung cap `current_trace_id()`;
- cung cap `flush_traces()`;
- giu graceful fallback neu Langfuse import that bai.

App goi `flush_traces()` trong shutdown hook de day het batch trace len backend
truoc khi process dung.

### 3. Trace waterfall

File: `app/agent.py`

Moi request tao mot trace co cau truc:

```text
agent-run
|-- rag-retrieval
`-- llm-generation
```

Trace `agent-run` co:

- hashed user ID;
- session ID;
- tags `lab`, feature va model;
- input da scrub voi `query_preview`;
- output gom latency va quality score;
- metadata gom `doc_count`, `query_preview`, feature va model.

Span `rag-retrieval` co:

- sanitized query preview;
- document count;
- retrieval timing.

Generation `llm-generation` co:

- model `claude-sonnet-4-5`;
- sanitized input/output preview;
- input, output va total token usage;
- estimated total cost;
- metadata `doc_count` va `query_preview`.

Raw message co PII khong duoc gui vao Langfuse. Decorator cua root span dat
`capture_input=False` va `capture_output=False`; input/output duoc cap nhat thu
cong bang du lieu da sanitize.

### 4. Khong gui trace trong unit test

File: `tests/conftest.py`

Unit tests dat:

```text
LANGFUSE_TRACING_ENABLED=false
```

Do do test van kiem tra behavior cua app ma khong lam ban project Langfuse that.

### 5. Load test

App duoc chay va `/health` tra ve:

```text
tracing_enabled=true
```

Sau do chay:

```bash
.venv/bin/python scripts/load_test.py --concurrency 5
```

Ket qua:

- 10/10 request tra ve HTTP `200`;
- 10 trace ID rieng duoc ghi vao log `response_sent`;
- moi trace co waterfall RAG va LLM.

### 6. Automated trace verification

File: `scripts/verify_traces.py`

Script:

1. Kiem tra Langfuse configuration va authentication.
2. Flush trace queue.
3. Doc trace `agent-run` trong mot gio gan nhat.
4. Retry de xu ly ingestion delay.
5. Kiem tra it nhat 10 trace.
6. Kiem tra user hash, session, tags, metadata, token usage va waterfall.
7. In trace ID va URL lam evidence.

Lenh:

```bash
.venv/bin/python scripts/verify_traces.py --minimum 10
```

Ket qua:

```text
Authentication: passed
Verified traces: 10
Required metadata/tags: passed
Token usage: passed
Waterfall observations: agent-run, rag-retrieval, llm-generation
Evidence trace ID: 3afcdb243971144352bac81c76816a33
```

Evidence trace:

https://cloud.langfuse.com/project/cmqex8io700rrad0d67b6o8en/traces/3afcdb243971144352bac81c76816a33

Trace ID nay co the duoc dung trong incident report o phase sau.

## Chay lai toan bo

Terminal 1:

```bash
rm -f data/logs.jsonl
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Terminal 2:

```bash
curl http://127.0.0.1:8000/health
.venv/bin/python scripts/load_test.py --concurrency 5
```

Dung app bang `Ctrl+C` de shutdown hook flush traces, sau do:

```bash
.venv/bin/pytest -q
.venv/bin/python scripts/validate_logs.py
.venv/bin/python scripts/verify_traces.py --minimum 10
```

