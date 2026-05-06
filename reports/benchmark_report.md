# Benchmark Report

## 1. So sánh Baseline vs Multi-Agent

| Tiêu chí | Single-Agent Baseline | Multi-Agent Workflow | Nhận xét |
| :--- | :--- | :--- | :--- |
| **Latency (Thời gian)** | Nhanh (~5-10s) | Chậm hơn (phụ thuộc vào số vòng lặp) | Multi-Agent tốn nhiều thời gian hơn do phải giao tiếp (handoff) qua lại nhiều bước (Research -> Analyze -> Write -> Critic). |
| **Cost (Chi phí)** | Thấp | Cao hơn | Multi-Agent tốn nhiều token hơn do phải truyền `ResearchState` qua nhiều LLM calls. |
| **Quality (Chất lượng)** | Trung bình, dễ bị hallucination | Tốt, lập luận chặt chẽ | Multi-Agent có Critic kiểm định chéo và Researcher tìm kiếm web nên trích dẫn (citations) chính xác hơn. |
| **Citation Coverage** | Thấp / Ảo | Cao | Researcher fetch dữ liệu từ Wikipedia/Search Engine, Writer tổng hợp lại. |
| **Failure Rate** | Cao đối với câu hỏi khó | Thấp | Supervisor có khả năng retry/fallback khi worker thất bại. |

---

## 2. Failure Mode & Cách Fix

**Failure Mode phổ biến:**
- **Vòng lặp vô hạn (Infinite Loop):** Supervisor liên tục gọi lại Researcher -> Analyst nhưng không gọi Writer/Critic, khiến Agent chạy mãi không dừng gây tốn kém API.
- **Mất context (Context Loss):** `ResearchState` truyền đi thiếu dữ liệu, khiến Analyst không có thông tin để phân tích.
- **API Rate Limit/Timeout:** Lỗi mạng hoặc server quá tải do gọi nhiều LLM liên tục.

**Cách Fix đã áp dụng:**
1. **Guardrails:** Giới hạn `max_iterations = 6` trong `SupervisorAgent`. Nếu vượt qua ngưỡng này, ép buộc trả về state `done` để kết thúc vòng lặp.
2. **State Management:** Thiết kế `ResearchState` (Pydantic) lưu trữ trạng thái rõ ràng ở các mảng `sources`, `research_notes`, `analysis_notes` để không bị mất context.
3. **Resilience:** Thêm Decorator `@retry` của thư viện `tenacity` vào `LLMClient` để tự động gọi lại tối đa 3 lần với exponential backoff nếu gặp lỗi kết nối.

---

## 3. Exit Ticket

**Câu 1: Case nào nên dùng multi-agent? Vì sao?**
- **Nên dùng cho:** Các bài toán phức tạp đòi hỏi nhiều bước tư duy, tìm kiếm thông tin theo thời gian thực (như bài Research GraphRAG), hệ thống tự sinh mã nguồn (coding), nghiên cứu học thuật sâu, hoặc công việc cần đánh giá chéo nhau.
- **Vì sao:** Việc chia nhỏ bài toán ra cho các role (Agent) chuyên biệt giúp mỗi Prompt tập trung hơn (Focus), dễ debug (biết sai ở Agent nào), và có thể tích hợp khâu "Tự kiểm định" (Critic/Reviewer) để giảm thiểu Hallucination, đảm bảo chất lượng.

**Câu 2: Case nào không nên dùng multi-agent? Vì sao?**
- **Không nên dùng cho:** Các câu hỏi tra cứu đơn giản (FAQ), tóm tắt một đoạn văn bản nhỏ, dịch thuật, hoặc phân loại cảm xúc (sentiment analysis).
- **Vì sao:** Multi-agent làm tăng độ trễ (Latency) đáng kể và tốn kém chi phí (Token Cost) không cần thiết. Đối với các bài toán đơn giản, một Single-agent (LLM model mạnh) với Few-shot prompt là đủ để giải quyết bài toán nhanh và rẻ hơn rất nhiều.
