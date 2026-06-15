# Ke hoach hoan thanh Day 13 Observability Lab

## 1. Muc tieu dau ra

Hoan thanh lab trong khoang 4 gio va dat cac dieu kien:

- `python scripts/validate_logs.py` dat toi thieu `80/100`, muc tieu `100/100`.
- Moi API request co correlation ID hop le va duoc tra ve qua header/body.
- Log JSON co day du context, khong lo PII.
- Langfuse co toi thieu 10 traces, kem metadata va mot trace waterfall ro rang.
- Dashboard co du 6 panels, don vi va threshold/SLO line.
- Co toi thieu 3 alert rules va runbook link hop le.
- Hoan thanh incident drill theo flow `Metrics -> Traces -> Logs`.
- Dien day du `docs/blueprint-template.md` va thu thap du evidence.
- Co chuoi commit ro rang va mo ta day du phan viec ca nhan de bao ve 40 diem ca nhan.

## 2. Thu tu uu tien

### P0 - Bat buoc de qua lab

1. Hoan thanh tat ca `TODO` trong `app/`.
2. Chay test va dat diem log validation.
3. Tao it nhat 10 Langfuse traces.
4. Tao dashboard 6 panels.
5. Cau hinh va kiem thu 3 alerts.
6. Hoan thanh report va evidence.

### P1 - Toi da diem

1. Chay incident drill va chung minh root cause bang trace ID/log.
2. Chuan bi demo on dinh, co kich ban va nguoi phu trach.
3. Tao commit nho, ro nghia theo tung hang muc de chung minh toan bo qua trinh lam bai.

### P2 - Bonus neu con thoi gian

1. Tach audit log vao `data/audit.jsonl`.
2. Them custom metric hoac automation script.
3. Chung minh toi uu chi phi bang so lieu truoc/sau.
4. Cai thien giao dien dashboard.

## 3. Ke hoach 4 gio

| Thoi gian | Cong viec | Dau ra/Dieu kien hoan thanh |
|---|---|---|
| 00:00-00:20 | Cai moi truong, chay baseline | App khoi dong; test baseline va danh sach TODO duoc ghi nhan |
| 00:20-01:10 | Correlation ID, log enrichment, PII | API logs co schema/context; khong con PII ro ri |
| 01:10-01:30 | Unit/integration verification | `pytest` pass; `validate_logs.py` dat 100/100 |
| 01:30-02:00 | Langfuse tracing | Co >= 10 traces, metadata/tags va waterfall |
| 02:00-02:35 | Load test va dashboard | Dashboard du 6 panels, co unit va SLO line |
| 02:35-03:05 | Alerts va incident drill | 3 alerts hop le; xac dinh root cause theo observability flow |
| 03:05-03:35 | Evidence va blueprint report | Screenshot/link/so lieu duoc dien vao report |
| 03:35-04:00 | Rehearsal va final verification | Chay lai checklist, demo 5-7 phut khong loi |

## 4. Cac buoc thuc hien chi tiet

### Phase 1 - Khoi tao va baseline

- [x] Tao virtual environment va cai dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

- [x] Dien `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, va kiem tra `LANGFUSE_HOST` trong `.env`.
- [x] Chay test baseline:

```bash
pytest -q
```

- [x] Khoi dong app:

```bash
uvicorn app.main:app --reload
```

- [x] Kiem tra `GET /health`, `GET /metrics`, va mot request `POST /chat`.
- [x] Xoa log cu neu can mot lan validate sach:

```bash
rm -f data/logs.jsonl
```

### Phase 2 - Hoan thanh logging va PII

#### 2.1 Correlation ID - `app/middleware.py`

- [x] Goi `clear_contextvars()` dau moi request de tranh ro ri context.
- [x] Doc `x-request-id` tu request header.
- [x] Neu header rong, sinh ID dang `req-<8-char-hex>`.
- [x] Goi `bind_contextvars(correlation_id=...)`.
- [x] Gan ID vao `request.state.correlation_id`.
- [x] Them response headers:
  - `x-request-id`
  - `x-response-time-ms`
- [x] Kiem tra request ID do client gui vao duoc giu nguyen.
- [x] Kiem tra cac request song song co correlation ID rieng.

#### 2.2 Log enrichment - `app/main.py`

- [x] Truoc log `request_received`, bind:
  - `user_id_hash=hash_user_id(body.user_id)`
  - `session_id=body.session_id`
  - `feature=body.feature`
  - `model=agent.model`
  - `env=os.getenv("APP_ENV", "dev")`
- [x] Khong bind `user_id` dang raw.
- [x] Xac nhan `request_received`, `response_sent`, va `request_failed` cung mot request co cung correlation ID/context.

#### 2.3 PII scrubbing - `app/logging_config.py`, `app/pii.py`

- [x] Dang ky `scrub_event` trong processor chain truoc khi ghi file/render JSON.
- [x] Kiem tra redact email, so dien thoai Viet Nam, CCCD va credit card.
- [x] Them pattern passport va dia chi Viet Nam theo yeu cau TODO.
- [x] Bao dam PII trong ca `event` va `payload` deu duoc scrub.
- [x] Them test cho cac pattern moi va payload long nhau neu mo rong scrubber de quy.

### Phase 3 - Verification gate

- [x] Chay:

```bash
pytest -q
python scripts/load_test.py --concurrency 5
python scripts/validate_logs.py
```

- [x] Gate de di tiep:
  - `pytest`: 10 tests pass.
  - `Estimated Score`: `100/100`.
  - Co 11 correlation IDs khac nhau.
  - `missing required fields = 0`.
  - `missing enrichment = 0`.
  - `PII leaks = 0`.
- [x] Tao log JSON co correlation ID `phase3-check` de lam evidence.
- [x] Gui query chua email/card test; log da thay bang `[REDACTED_EMAIL]` va `[REDACTED_CREDIT_CARD]`.

### Phase 4 - Langfuse tracing

- [x] Xac nhan `/health` tra ve `tracing_enabled: true`.
- [x] Chay load test; file sample co 10 queries:

```bash
python scripts/load_test.py --concurrency 5
```

- [x] Langfuse co du 10 traces sau khi flush/upload hoan tat.
- [x] Xac nhan moi trace co:
  - hashed user ID
  - session ID
  - tags `lab`, feature, model
  - token usage
  - metadata `doc_count`, `query_preview`
- [x] Chon trace `3afcdb243971144352bac81c76816a33` co RAG/LLM flow lam waterfall evidence.
- [x] Ghi lai trace ID `3afcdb243971144352bac81c76816a33` de dung cho incident report.

### Phase 5 - Metrics va dashboard

- [x] Tao traffic bang load test, sau do doc `GET /metrics`.
- [x] Tao dashboard voi dung 6 panels:

| Panel | Metric |
|---|---|
| Latency | P50, P95, P99, don vi ms |
| Traffic | Request count hoac QPS |
| Errors | Error rate va breakdown theo `error_type` |
| Cost | Cost theo thoi gian/tong cost, don vi USD |
| Tokens | Input va output tokens |
| Quality | Average quality score |

- [x] Dat default time range la 1 gio.
- [x] Dat auto refresh 15 giay.
- [x] Them threshold/SLO line, latency P95 `< 3000 ms` va error rate `< 2%`.
- [x] Doi chieu muc tieu trong `config/slo.yaml`.
- [x] Luu screenshot `docs/evidence/dashboard-6-panels.png`.

### Phase 6 - Alerts va incident drill

#### 6.1 Alert rules

- [x] Kiem tra ba rules trong `config/alert_rules.yaml`:
  - `high_latency_p95`
  - `high_error_rate`
  - `cost_budget_spike`
- [x] Kiem tra severity, owner, condition va link toi dung heading trong `docs/alerts.md`.
- [x] Chup screenshot `docs/evidence/alert-rules.png`.

#### 6.2 Incident drill khuyen nghi: `rag_slow`

- [x] Ghi baseline P95 `157 ms` truoc incident.
- [x] Bat incident:

```bash
python scripts/inject_incident.py --scenario rag_slow
python scripts/load_test.py --concurrency 5
```

- [x] Dieu tra theo dung thu tu:
  1. Metrics: P95/P99 tang.
  2. Traces: tim request cham va span retrieval/RAG bat thuong.
  3. Logs: loc theo correlation ID cua trace va xac nhan request context.
- [x] Ghi symptoms, trace `65c9bd50639192acc5020afe53019648`, log correlation `incident-rag-slow`, root cause va mitigation.
- [x] Tat incident va chay lai; P95 phuc hoi ve `158 ms`:

```bash
python scripts/inject_incident.py --scenario rag_slow --disable
python scripts/load_test.py --concurrency 5
```

- [x] Custom quality/error-rate metrics va token/cost trace details da duoc bo sung; khong can bat them incident bonus.

### Phase 7 - Report, evidence va Git

- [x] Dien tat ca field trong `docs/blueprint-template.md`.
- [x] Dien bang SLO bang so lieu thuc te tu dashboard/metrics.
- [x] Dien incident report voi trace ID va log evidence cu the.
- [x] Gan link du 6 evidence trong `docs/grading-evidence.md`:
  - Langfuse list co >= 10 traces
  - mot full trace waterfall
  - JSON log co correlation ID
  - log co PII redaction
  - dashboard 6 panels
  - alert rules va runbook
- [x] Dien phan dong gop ca nhan, walkthrough/evidence va implementation commit `00c8c67`.
- [x] Ghi nhan cac nhom thay doi de tao Git evidence:

```text
feat: implement correlation id middleware
feat: enrich structured logs with request context
feat: redact pii from structured logs
test: cover pii patterns and correlation propagation
docs: complete slo alerts and incident evidence
docs: finalize observability blueprint report
```

## 5. Chien luoc lam bai ca nhan

Thuc hien tuan tu theo thu tu duoi day de tranh phai chuyen doi ngu canh lien tuc:

| Thu tu | Vai tro tam thoi | Trach nhiem | Evidence can luu |
|---:|---|---|---|
| 1 | Developer | Middleware, enrichment, PII scrubber | Commit code, test output, log screenshots |
| 2 | Test engineer | Unit test, concurrency, log validation | `pytest` va score `validate_logs.py` |
| 3 | Observability engineer | Langfuse metadata, tags, traces | Trace list, trace ID, waterfall screenshot |
| 4 | SRE | Metrics, SLO, dashboard, alerts | Dashboard va alert screenshots |
| 5 | Incident responder | Inject incident, RCA, recovery | Before/after metrics, trace va log evidence |
| 6 | Report owner | Blueprint, evidence sheet, demo | Report da dien va final checklist |

Nguyen tac quan ly thoi gian:

- Hoan thanh va verify tung phase truoc khi sang phase tiep theo.
- Luu screenshot ngay khi evidence xuat hien, khong doi den cuoi buoi.
- Moi hang muc lon nen co mot commit rieng de lich su Git de doc.
- Khong danh thoi gian cho bonus truoc khi tat ca P0 da hoan thanh.
- Neu sap het gio, uu tien theo thu tu: validation, traces, dashboard, report, incident, bonus.

## 6. Kich ban demo 5-7 phut

1. Gioi thieu kien truc va muc tieu observability.
2. Gui mot `/chat` request co `x-request-id`.
3. Mo JSON log, chi correlation ID, context va PII redaction.
4. Mo Langfuse, chi trace metadata va waterfall.
5. Mo dashboard, di qua 6 panels va SLO lines.
6. Bat `rag_slow`, tao traffic va chi latency tang.
7. Dung trace de khoanh vung RAG, dung log de xac nhan request/root cause.
8. Tat incident, chung minh metric phuc hoi.
9. Ket thuc bang alert/runbook va lich su commit chung minh qua trinh lam bai.

## 7. Final acceptance checklist

### Ky thuat

- [x] Khong con `TODO` can trien khai trong `app/`.
- [x] `pytest -q` pass.
- [x] `validate_logs.py` dat 100/100.
- [x] Correlation ID hop le trong response, logs va context.
- [x] Khong co PII raw trong `data/logs.jsonl`.
- [x] `/health` bao tracing enabled.
- [x] Langfuse co >= 10 traces.
- [x] Dashboard du 6 panels, co unit va threshold.
- [x] Co 3 alerts va runbook link hop le.
- [x] Incident da duoc bat, dieu tra, tat va xac nhan recovery.

### Nop bai va bao ve

- [x] Blueprint khong con placeholder chua dien.
- [x] Co du required screenshots.
- [x] SLO table dung so lieu thuc.
- [x] RCA co trace ID/log evidence.
- [x] Co implementation commit `00c8c67`, file-level evidence va walkthrough cho tung hang muc chinh.
- [x] Demo flow da duoc chay end-to-end mot lan.
- [x] `.env`, secrets va runtime raw log duoc gitignore; evidence chi chua du lieu da scrub.

## 8. Rui ro va cach xu ly

| Rui ro | Xu ly |
|---|---|
| Langfuse khong co trace | Kiem tra keys/host, `/health`, network va khoi dong lai app sau khi sua `.env` |
| Log validation van tru diem | Xoa log cu, tao lai traffic, mo tung JSON line va doi chieu cac field validator |
| Context bi lan giua request song song | Bao dam `clear_contextvars()` chay dau middleware va test voi concurrency 5 |
| PII van lo trong field moi | Scrub de quy moi string trong payload va them regression test |
| Dashboard thieu du lieu theo thoi gian | Tao traffic lien tuc, export/push metric truoc khi vao buoc dashboard |
| Demo incident qua cham | Chuan bi san terminal tabs va dung `rag_slow`, vi symptom de quan sat |
| Thieu diem ca nhan | Tao commit ro nghia theo tung phase, gan evidence link va chuan bi giai thich toan bo flow |
