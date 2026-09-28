# Thông Tin Deploy — Checkpoint 5

> Điền file này sau khi deploy xong. `pytest tests/test_cp5.py` đọc file này
> để tìm địa chỉ service của bạn và gọi thử.
>
> **Chỉ ghi TÊN biến môi trường, tuyệt đối không dán giá trị API key vào đây.**
> Repo này công khai — dán khóa vào là mất khóa.

## Thông Tin Học Viên

| Mục         | Nội dung                                                                                           |
| ----------- | -------------------------------------------------------------------------------------------------- |
| Họ và tên   | Huỳnh Tấn Trung                                                                                    |
| Mã học viên | 2A202602742                                                                                        |
| Repo        | https://github.com/huynhtantrung/K4-L3A-DAY12-HuynhTanTrung-2A202602742-CloudServicesAndDeployment |

## Service

| Mục         | Nội dung                                     |
| ----------- | -------------------------------------------- |
| Public URL  | https://agent-production-838b.up.railway.app |
| Platform    | Railway                                      |
| Ngày deploy | 2026-09-28                                   |

## Biến Môi Trường Đã Set Trên Cloud

Ghi tên biến và **nguồn giá trị**, không ghi giá trị:

| Biến                    | Đã set | Ghi chú                                                                |
| ----------------------- | ------ | ---------------------------------------------------------------------- |
| `PORT`                  | ✅     | platform tự gán                                                        |
| `AGENT_API_KEY`         | ✅     | đặt trong dashboard, không nằm trong repo                              |
| `REDIS_URL`             | ✅     | Redis add-on của Railway (private networking `redis.railway.internal`) |
| `RATE_LIMIT_PER_MINUTE` | ✅     | 10                                                                     |
| `MONTHLY_BUDGET_USD`    | ✅     | 10.0                                                                   |
| `LOG_LEVEL`             | ✅     | INFO                                                                   |

## Lệnh Kiểm Tra

Thay `<URL>` bằng Public URL ở trên:

```bash
# 1. Liveness — mong đợi 200 {"status":"ok"}
curl -i https://agent-production-838b.up.railway.app/health
{"status":"ok","service":"day12-agent","version":"1.0.0"}

# 2. Readiness — mong đợi 200 {"status":"ready"} (đã nối được Redis)
curl -i https://agent-production-838b.up.railway.app/ready
{"status":"ready","redis":true}

# 3. Không có API key — mong đợi 401
curl -i -X POST https://agent-production-838b.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'
401: {"detail":"invalid or missing API key"}

# 4. Có API key — mong đợi 200 kèm câu trả lời
curl -i -X POST https://agent-production-838b.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $AGENT_API_KEY" \
  -H "X-User-Id: sv-test" \
  -d '{"question":"Deploy là gì?"}'
{"answer":"Ngắn gọn: Deploy là gì phụ thuộc vào ba yếu tố — cấu hình qua biến môi trường, orchestrator biết trạng thái, và giới hạn tài nguyên.","user_id":"sv-test","history_length":0,"cost_usd":2.265e-05,"tokens":{"in":3,"out":37}}

# 5. Rate limit — gọi 15 lần, những lần cuối phải trả 429
for i in $(seq 1 15); do
  curl -s -o /dev/null -w "%{http_code} " -X POST https://agent-production-838b.up.railway.app/ask \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $AGENT_API_KEY" \
    -H "X-User-Id: sv-test" \
    -d '{"question":"test"}'
200 200 200 200 200 200 200 200 200 200 429 429 429 429 429

done; echo
```
