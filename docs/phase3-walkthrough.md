# Phase 3 Walkthrough

Tai lieu nay mo ta cac thay doi da thuc hien de hoan thanh Phase 3 -
Verification Gate cua Observability Lab.

## 1. Muc tieu

Phase 3 yeu cau:

- test suite pass;
- load test chay voi concurrency 5;
- log JSON co correlation ID va context day du;
- khong de lo PII;
- `scripts/validate_logs.py` dat `100/100`;
- co evidence voi correlation ID `phase3-check`.

## 2. Correlation ID middleware

File: `app/middleware.py`

Da hoan thien `CorrelationIdMiddleware` theo flow:

1. Goi `clear_contextvars()` khi bat dau request de context cua request truoc
   khong bi ro sang request sau.
2. Doc `x-request-id` tu request header.
3. Neu client khong gui ID, tao ID moi theo format `req-<8-char-hex>`.
4. Bind ID vao structlog context bang `bind_contextvars()`.
5. Luu ID vao `request.state.correlation_id` de endpoint dua vao response body.
6. Tra ve hai response header:
   - `x-request-id`;
   - `x-response-time-ms`.

Ket qua la correlation ID cua client duoc giu nguyen, con request khong co header
se nhan mot ID moi.

## 3. Log enrichment

File: `app/main.py`

Truoc khi ghi log `request_received`, endpoint `/chat` bind cac field:

- `user_id_hash`: hash cua user ID, khong ghi raw user ID;
- `session_id`;
- `feature`;
- `model`;
- `env`.

Vi cac field duoc bind bang structlog contextvars, log `request_received`,
`response_sent` va `request_failed` trong cung request se co chung correlation
ID va context.

## 4. PII scrubbing

Files:

- `app/logging_config.py`;
- `app/pii.py`.

Da dang ky `scrub_event` trong processor chain truoc khi log duoc render va ghi
vao `data/logs.jsonl`.

Scrubber duoc mo rong de xu ly de quy:

- string;
- dictionary;
- list;
- tuple.

Nho do, PII trong `event`, `payload` va cac payload long nhau deu duoc redact.

Nhung pattern duoc ho tro:

- email;
- so dien thoai Viet Nam;
- CCCD;
- credit card;
- passport Viet Nam dang mot chu cai in hoa va bay chu so;
- dia chi Viet Nam co cac keyword nhu `Dia chi`, `So`, `Phuong`, `Quan`.

### Sua false positive cua passport

Ban regex passport ban dau khong phan biet chu hoa/chu thuong. Trong luc chay
load test, correlation ID `req-e3606108` bi nham thanh passport va bi ghi thanh
`req-[REDACTED_PASSPORT]`.

Regex da duoc sua thanh:

```regex
\b[A-Z]\d{7}\b
```

Pattern nay van redact `B1234567`, nhung khong con redact chuoi ky thuat
`req-e3606108`.

## 5. Test coverage

Files:

- `tests/test_pii.py`;
- `tests/test_observability.py`;
- `pytest.ini`.

Da bo sung test cho:

- email, phone, CCCD, credit card, passport va dia chi;
- payload long nhau;
- regression cua correlation ID bi nham thanh passport;
- giu nguyen client request ID;
- sinh request ID khi header bi thieu;
- context isolation khi gui nam request song song.

`pytest.ini` them project root vao Python path de test runner import duoc package
`app`.

Luu y: dependencies cua repo nam trong `.venv`, vi vay lenh verification da dung
`.venv/bin/pytest`. Lenh `pytest` global tren may khong co package `structlog`.

Ket qua:

```text
8 passed, 2 warnings in 0.86s
```

Hai warning la deprecation warning cua FastAPI `on_event`; chung khong anh huong
den Phase 3.

## 6. Load test va evidence

Server duoc chay bang:

```bash
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Load test:

```bash
.venv/bin/python scripts/load_test.py --concurrency 5
```

Ket qua:

- 10/10 request tra ve HTTP `200`;
- tao 10 correlation ID tu dong;
- request va response log co cung correlation ID.

Sau do gui them mot request co:

- header `x-request-id: phase3-check`;
- email `student@vinuni.edu.vn`;
- card `4111-1111-1111-1111`.

Response giu nguyen:

```text
x-request-id: phase3-check
```

Log chi chua:

```text
[REDACTED_EMAIL]
[REDACTED_CREDIT_CARD]
```

Raw email va card khong xuat hien trong file log.

## 7. Validation result

Lenh:

```bash
.venv/bin/python scripts/validate_logs.py
```

Ket qua cuoi:

```text
Total log records analyzed: 23
Records with missing required fields: 0
Records with missing enrichment (context): 0
Unique correlation IDs found: 11
Potential PII leaks detected: 0
Estimated Score: 100/100
```

Kiem tra bo sung xac nhan:

```text
correlation_pairs=11/11
phase3_check_preserved=true
raw_pii_present=false
redaction_markers_present=true
```

`data/logs.jsonl` la runtime evidence va da duoc `.gitignore`, khong dua PII hoac
log tam vao commit.

## 8. Cach chay lai Phase 3

Terminal 1:

```bash
rm -f data/logs.jsonl
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Terminal 2:

```bash
.venv/bin/pytest -q
.venv/bin/python scripts/load_test.py --concurrency 5
.venv/bin/python scripts/validate_logs.py
```

Gate dat khi:

- tat ca test pass;
- load test khong co request loi;
- validator dat `100/100`;
- co it nhat hai correlation ID;
- missing fields, missing enrichment va PII leaks deu bang `0`.

