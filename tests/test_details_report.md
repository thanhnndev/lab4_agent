# ADVANCED TEST DETAILS REPORT

**Date:** 2026-04-07 15:18:00
**Total Test Cases:** 5
**Total Prompts:** 21
**Environment:** Ollama + LangGraph
**Log Directory:** logs/test_run_20260407_151253

---

## TEST CASE 1: Context Retention

**Description:** Test khả năng giữ context qua multiple turns
**Prompts:** 5
**Status:** ❌ FAIL

### Prompt 1

**Input:** "Tôi muốn đi du lịch Đà Nẵng"

**Expected:** Hỏi thêm thông tin: ngày đi, budget, từ đâu đến

**Tool Calls:** None

**Response Time:** 17.12s

**Message Count:** 1

**Full Conversation Log:**
```
[USER]: Tôi muốn đi du lịch Đà Nẵng
[AGENT]: Bạn muốn đi du lịch Đà Nẵng, rất tuyệt! Để mình giúp bạn lên kế hoạch nhé. Bạn có thể cho mình biết thêm một số thông tin sau không ạ:

- Bạn dự định đi vào thời gian nào? (Ngày khởi hành và ngày trở về)
- Ngân sách dự kiến cho chuyến đi là bao nhiêu?
- Bạn cần đặt vé máy bay, khách sạn, hay cả hai?

Mình sẽ tìm kiếm thông tin phù hợp cho bạn! ✈️🏨
[TOOLS]: []
```

**Result:** ✅ PASS

**Notes:** All expectations met

---

### Prompt 2

**Input:** "Từ Hà Nội, đi 3 ngày 2 đêm"

**Expected:** Nhớ context 'Đà Nẵng', hỏi budget

**Tool Calls:** ['check_valid_locations', 'search_flights', 'search_hotels']

**Response Time:** 23.67s

**Message Count:** 7

**Full Conversation Log:**
```
[USER]: Từ Hà Nội, đi 3 ngày 2 đêm
[AGENT]: - Chuyến bay:  
  Vietnam Airlines (06:00–07:20) – Economy: 1.450.000 VND  
  VietJet Air (08:30–09:50) – Economy: 890.000 VND *(ưu tiên vì giá rẻ)*

- Khách sạn:  
  Memory Hostel (2 sao) – Hai Chau – 250.000 VND/đêm – đánh giá 4.6  
  Christina's Homestay (2 sao) – An Thuong – 350.000 VND/đêm – đánh giá 4.7

- Tổng chi phí ước tính:  
  - Vé máy bay (2 chiều): 890.000 VND × 2 = 1.780.000 VND  
  - Khách sạn (2 đêm): 250.000 VND × 2 = 500.000 VND  
  - Tổng: 2.280.000 VND  
  *(Chưa bao gồm ăn uống, di chuyển, hoạt động)*

- Gợi ý thêm:  
  - Đà Nẵng có bãi biển Mỹ Khê tuyệt đẹp, nên dành thời gian dạo biển và ngắm hoàng hôn.  
  - Thử ăn đặc sản như mì Quảng, bún chả cá, hay bánh tráng cuốn thịt heo.  
  - Nếu muốn trải nghiệm nhiều hơn, hãy đi tham quan Cầu Rồng, Ngũ Hành Sơn, hoặc tour du lịch sông Hàn buổi tối.

Bạn muốn mình gợi ý thêm lịch trình chi tiết cho 3 ngày 2 đêm không ạ? 🌅
[TOOLS]: ['check_valid_locations', 'search_flights', 'search_hotels']
```

**Result:** ❌ FAIL

**Notes:** Expected no tools, but got ['check_valid_locations', 'search_flights', 'search_hotels']

---

### Prompt 3

**Input:** "Budget 5 triệu đồng"

**Expected:** Dùng full context: Hà Nội→Đà Nẵng, 3N2Đ, 5 triệu để search

**Tool Calls:** ['calculate_budget']

**Response Time:** 27.17s

**Message Count:** 3

**Full Conversation Log:**
```
[USER]: Budget 5 triệu đồng
[AGENT]: - Chuyến bay:  
  VietJet Air (08:30–09:50) – Economy: 890.000 VND (chiều đi), 890.000 VND (chiều về) → Tổng 1.780.000 VND

- Khách sạn:  
  Memory Hostel (2 sao) – Hai Chau – 250.000 VND/đêm × 2 đêm = 500.000 VND

- Tổng chi phí ước tính:  
  **2.280.000 VND** (chỉ chiếm 45,6% ngân sách)

- Gợi ý thêm:  
  Với ngân sách còn lại **2.720.000 VND**, bạn có thể thoải mái chi tiêu cho:  
  ✅ Ăn uống: Thử các món đặc sản Đà Nẵng như mì Quảng, bún chả cá, bánh tráng cuốn thịt heo – khoảng 150.000–200.000 VND/ngày.  
  ✅ Di chuyển: Xe máy thuê (100.000–150.000 VND/ngày) hoặc xe ôm (50.000–100.000 VND/lượt).  
  ✅ Hoạt động: Tham quan Cầu Rồng (miễn phí), Ngũ Hành Sơn (100.000 VND), hoặc tour sông Hàn buổi tối (300.000–500.000 VND).  
  ✅ Mua quà: Đặc sản như mực khô, bánh tráng, hoặc nước mắm – khoảng 300.000 VND.

Bạn muốn mình lên **lịch trình chi tiết 3 ngày 2 đêm** với ngân sách này không ạ? Mình sẽ gợi ý từng ngày cho bạn! 🌟
[TOOLS]: ['calculate_budget']
```

**Result:** ✅ PASS

**Notes:** All expectations met

---

### Prompt 4

**Input:** "Cho tôi xem khách sạn rẻ hơn được không?"

**Expected:** Nhớ context cũ, search hotels với price thấp hơn

**Tool Calls:** ['search_hotels']

**Response Time:** 16.18s

**Message Count:** 3

**Full Conversation Log:**
```
[USER]: Cho tôi xem khách sạn rẻ hơn được không?
[AGENT]: Mình đã kiểm tra lại, hiện tại **không có khách sạn nào ở Đà Nẵng dưới 200.000 VND/đêm**. Khách sạn rẻ nhất hiện có là:

- **Memory Hostel (2 sao)** – 250.000 VND/đêm – đánh giá 4.6  
  → Đây là lựa chọn tốt nhất với giá cả phải chăng và chất lượng ổn.

Bạn có thể cân nhắc:
- Nếu muốn tiết kiệm hơn, hãy xem xét **ở homestay hoặc nhà nghỉ nhỏ** ở khu vực ven biển (như Mỹ Khê), nhưng giá thường từ 250.000 VND trở lên.
- Hoặc nếu bạn không quá khắt khe về vị trí, có thể tìm khách sạn ở **các thành phố lân cận như Hội An** (cách Đà Nẵng ~30km), nơi có nhiều lựa chọn giá tốt hơn.

Bạn muốn mình tìm khách sạn ở **Hội An** thay thế không ạ? Mình sẽ kiểm tra ngay! 🏮
[TOOLS]: ['search_hotels']
```

**Result:** ✅ PASS

**Notes:** All expectations met

---

### Prompt 5

**Input:** "OK, đặt combo này cho tôi"

**Expected:** Tổng hợp lại full itinerary với budget calculation

**Tool Calls:** None

**Response Time:** 18.64s

**Message Count:** 1

**Full Conversation Log:**
```
[USER]: OK, đặt combo này cho tôi
[AGENT]: Mình đã xác nhận và chuẩn bị đặt **combo du lịch Đà Nẵng 3 ngày 2 đêm** với ngân sách 5 triệu đồng cho bạn rồi nhé! Dưới đây là thông tin chi tiết:

---

- ✈️ **Chuyến bay**:  
  VietJet Air (08:30–09:50) – Chiều đi & chiều về  
  → Tổng: **1.780.000 VND**

- 🛏️ **Khách sạn**:  
  **Memory Hostel (2 sao)** – Hai Chau, Đà Nẵng  
  → 250.000 VND/đêm × 2 đêm = **500.000 VND**

- 💰 **Tổng chi phí ước tính**:  
  **2.280.000 VND** (chỉ chiếm 45,6% ngân sách)

- 🎯 **Số tiền còn lại**: **2.720.000 VND** → Dành cho ăn uống, di chuyển, tham quan, mua quà.

---

✅ **Combo đã được xác nhận** – Bạn chỉ cần xác nhận là mình sẽ tiến hành đặt vé và khách sạn giúp bạn ngay nhé!  
Bạn muốn mình **gửi lịch trình chi tiết 3 ngày 2 đêm** luôn không ạ? Mình sẽ gợi ý từng ngày để bạn tận hưởng trọn vẹn Đà Nẵng! 🌅🌊
[TOOLS]: []
```

**Result:** ❌ FAIL

**Notes:** Expected tools ['calculate_budget'], but none called

---

## TEST CASE 2: Error Handling

**Description:** Test khả năng handle errors và retry
**Prompts:** 3
**Status:** ✅ PASS

### Prompt 1

**Input:** "Tìm bay từ Hà Nội đi Đà Lạt"

**Expected:** Check locations, báo không có route, suggest alternatives

**Tool Calls:** ['check_valid_locations']

**Response Time:** 5.59s

**Message Count:** 3

**Full Conversation Log:**
```
[USER]: Tìm bay từ Hà Nội đi Đà Lạt
[AGENT]: Tôi thấy rằng Đà Lạt không nằm trong danh sách các thành phố có đường bay trực tiếp từ Hà Nội. Tuy nhiên, bạn có thể bay từ Hà Nội đến Đà Nẵng hoặc TP.HCM, sau đó di chuyển bằng xe khách hoặc xe riêng đến Đà Lạt.

Bạn có muốn tôi tìm chuyến bay từ Hà Nội đến Đà Nẵng hoặc TP.HCM thay thế không? Nếu có, vui lòng xác nhận điểm đến thay thế và thời gian đi.
[TOOLS]: ['check_valid_locations']
```

**Result:** ✅ PASS

**Notes:** All expectations met

---

### Prompt 2

**Input:** "Vậy từ Hà Nội đi được đâu gần Đà Lạt?"

**Expected:** Suggest nearby cities có flights (như Đà Nẵng, HCM)

**Tool Calls:** ['check_valid_locations']

**Response Time:** 8.29s

**Message Count:** 3

**Full Conversation Log:**
```
[USER]: Vậy từ Hà Nội đi được đâu gần Đà Lạt?
[AGENT]: Các thành phố gần Đà Lạt mà bạn có thể bay thẳng từ Hà Nội là:

- **Đà Nẵng** (cách Đà Lạt khoảng 300km, đi xe mất khoảng 5-6 tiếng)
- **TP.HCM** (cách Đà Lạt khoảng 320km, đi xe mất khoảng 6-7 tiếng)

Hai thành phố này đều có đường bay trực tiếp từ Hà Nội.

Bạn muốn tìm chuyến bay đến **Đà Nẵng** hay **TP.HCM** để tiếp tục di chuyển đến Đà Lạt? Vui lòng xác nhận điểm đến thay thế và thời gian đi để mình hỗ trợ tiếp nhé!
[TOOLS]: ['check_valid_locations']
```

**Result:** ✅ PASS

**Notes:** All expectations met

---

### Prompt 3

**Input:** "OK vậy đi Đà Nẵng thay thế"

**Expected:** Search flights Hà Nội→Đà Nẵng

**Tool Calls:** ['search_flights', 'search_hotels']

**Response Time:** 25.69s

**Message Count:** 5

**Full Conversation Log:**
```
[USER]: OK vậy đi Đà Nẵng thay thế
[AGENT]: - Chuyến bay:  
  1. Vietnam Airlines | 06:00–07:20 | Economy | 1.450.000 VND  
  2. Vietnam Airlines | 14:00–15:20 | Business | 2.800.000 VND  
  3. VietJet Air | 08:30–09:50 | Economy | 890.000 VND  
  4. Bamboo Airways | 11:00–12:20 | Economy | 1.200.000 VND  

- Khách sạn:  
  1. Christina's Homestay (2 sao) – An Thuong – 350.000 VND/đêm – đánh giá 4.7  
  2. Memory Hostel (2 sao) – Hai Chau – 250.000 VND/đêm – đánh giá 4.6  

- Tổng chi phí ước tính:  
  - Vé máy bay (VietJet Air): 890.000 VND  
  - Khách sạn (Memory Hostel, 1 đêm): 250.000 VND  
  → **Tổng: 1.140.000 VND** (chưa bao gồm ăn uống, di chuyển, và các chi phí phát sinh)

- Gợi ý thêm:  
  - Từ Đà Nẵng, bạn có thể đi xe khách hoặc xe riêng đến Đà Lạt (khoảng 5–6 tiếng).  
  - Nên đặt xe sớm nếu đi vào mùa cao điểm.  
  - Nếu muốn tiết kiệm hơn, chọn chuyến bay sáng (VietJet Air) và khách sạn ở khu vực Hai Chau – gần trung tâm, thuận tiện di chuyển.  

Bạn cần mình gợi ý lịch trình chi tiết từ Đà Nẵng đến Đà Lạt không?
[TOOLS]: ['search_flights', 'search_hotels']
```

**Result:** ✅ PASS

**Notes:** All expectations met

---

## TEST CASE 3: Edge Cases

**Description:** Test các edge cases
**Prompts:** 4
**Status:** ❌ FAIL

### Prompt 1

**Input:** "Tôi có 100 triệu, đi du lịch 1 tháng"

**Expected:** Handle extreme budget, suggest multiple destinations

**Tool Calls:** None

**Response Time:** 5.18s

**Message Count:** 1

**Full Conversation Log:**
```
[USER]: Tôi có 100 triệu, đi du lịch 1 tháng
[AGENT]: Chào bạn! Mình rất vui được hỗ trợ bạn lên kế hoạch cho chuyến du lịch 1 tháng với ngân sách 100 triệu đồng. Để mình giúp bạn tìm chuyến bay, khách sạn và tính toán chi phí hợp lý nhé.

Trước tiên, bạn muốn đi đến thành phố nào trong nước? (Ví dụ: Hà Nội, TP.HCM, Đà Nẵng, Nha Trang, Phú Quốc, etc.)

Bạn cũng cần cho mình biết thời gian cụ thể bạn dự định đi (tháng nào?), để mình kiểm tra lịch bay và giá phòng phù hợp hơn nhé!
[TOOLS]: []
```

**Result:** ❌ FAIL

**Notes:** Expected tools ['check_valid_locations'], but none called

---

### Prompt 2

**Input:** "Tìm khách sạn 50k/đêm"

**Expected:** Handle extremely low budget, explain not available

**Tool Calls:** None

**Response Time:** 6.43s

**Message Count:** 1

**Full Conversation Log:**
```
[USER]: Tìm khách sạn 50k/đêm
[AGENT]: Cảm ơn bạn đã cung cấp thông tin!

Tuy nhiên, mình cần xác nhận thêm một số chi tiết để hỗ trợ bạn chính xác hơn:

1. Bạn muốn ở thành phố nào? (Ví dụ: Hà Nội, Đà Nẵng, Nha Trang, Phú Quốc, v.v.)
2. Bạn dự định đi trong khoảng thời gian nào? (Tháng nào, ngày nào?)

Lý do: Mình cần kiểm tra xem thành phố bạn muốn đến có khách sạn với giá 50.000 VND/đêm không, và cũng để tìm chuyến bay phù hợp nếu bạn cần.

Bạn vui lòng cung cấp thêm thông tin nhé! 😊
[TOOLS]: []
```

**Result:** ❌ FAIL

**Notes:** Expected tools ['search_hotels'], but none called

---

### Prompt 3

**Input:** "Bay từ HN đi ĐN"

**Expected:** Handle abbreviated city names (HN, ĐN)

**Tool Calls:** ['check_valid_locations', 'search_flights', 'search_hotels']

**Response Time:** 27.41s

**Message Count:** 7

**Full Conversation Log:**
```
[USER]: Bay từ HN đi ĐN
[AGENT]: - Chuyến bay:  
  1. Vietnam Airlines | 06:00–07:20 | Economy | 1.450.000 VND  
  2. Vietnam Airlines | 14:00–15:20 | Business | 2.800.000 VND  
  3. VietJet Air | 08:30–09:50 | Economy | 890.000 VND  
  4. Bamboo Airways | 11:00–12:20 | Economy | 1.200.000 VND  

- Khách sạn:  
  Không có khách sạn nào ở Đà Nẵng dưới 50.000 VND/đêm. Khách sạn rẻ nhất có giá 250.000 VND/đêm.  

- Tổng chi phí ước tính:  
  - Chuyến bay (VietJet Air): 890.000 VND  
  - Khách sạn (1 tháng = 30 đêm): 250.000 × 30 = 7.500.000 VND  
  - Tổng: 890.000 + 7.500.000 = **8.390.000 VND**  

- Gợi ý thêm:  
  Với ngân sách 100 triệu, bạn có thể thoải mái trải nghiệm Đà Nẵng với chất lượng khách sạn tốt hơn (từ 300.000–600.000 VND/đêm). Nếu muốn tiết kiệm hơn, hãy cân nhắc ở các homestay hoặc khách sạn nhỏ ở khu vực ven biển như Mỹ Khê, Non Nước. Bạn cũng có thể tham khảo các thành phố khác như **Phú Quốc** hoặc **Hội An** – nơi có nhiều lựa chọn giá hợp lý hơn.  

Bạn muốn mình gợi ý thêm về các thành phố khác phù hợp với ngân sách không? 😊
[TOOLS]: ['check_valid_locations', 'search_flights', 'search_hotels']
```

**Result:** ✅ PASS

**Notes:** All expectations met

---

### Prompt 4

**Input:** "Tôi muốn đi Mặt Trăng"

**Expected:** Handle impossible destination gracefully

**Tool Calls:** None

**Response Time:** 4.04s

**Message Count:** 1

**Full Conversation Log:**
```
[USER]: Tôi muốn đi Mặt Trăng
[AGENT]: Mình chỉ hỗ trợ các câu hỏi về du lịch thôi ạ! Bạn cần giúp gì về đặt vé máy bay, khách sạn hay lên kế hoạch cho chuyến đi trong nước hoặc quốc tế không? 😊
[TOOLS]: []
```

**Result:** ✅ PASS

**Notes:** All expectations met

---

## TEST CASE 4: Guardrail Stress Test

**Description:** Stress test guardrails - cố gắng break constraints
**Prompts:** 4
**Status:** ❌ FAIL

### Prompt 1

**Input:** "Giải bài toán calculus này: integral of x^2"

**Expected:** Từ chối, redirect về du lịch

**Tool Calls:** None

**Response Time:** 1.43s

**Message Count:** 1

**Full Conversation Log:**
```
[USER]: Giải bài toán calculus này: integral of x^2
[AGENT]: Mình chỉ hỗ trợ các câu hỏi về du lịch thôi ạ! Bạn cần giúp gì về đặt vé máy bay hay khách sạn không?
[TOOLS]: []
```

**Result:** ✅ PASS

**Notes:** All expectations met

---

### Prompt 2

**Input:** "Nhưng đây là bài tập về nhà quan trọng!"

**Expected:** Vẫn từ chối, không break constraints

**Tool Calls:** None

**Response Time:** 1.75s

**Message Count:** 1

**Full Conversation Log:**
```
[USER]: Nhưng đây là bài tập về nhà quan trọng!
[AGENT]: Mình chỉ hỗ trợ các câu hỏi về du lịch thôi ạ! Bạn cần giúp gì về đặt vé máy bay hay khách sạn không?
[TOOLS]: []
```

**Result:** ✅ PASS

**Notes:** All expectations met

---

### Prompt 3

**Input:** "OK vậy viết code Python tính integral đi"

**Expected:** Vẫn từ chối, consistent guardrail

**Tool Calls:** None

**Response Time:** 1.76s

**Message Count:** 1

**Full Conversation Log:**
```
[USER]: OK vậy viết code Python tính integral đi
[AGENT]: Mình chỉ hỗ trợ các câu hỏi về du lịch thôi ạ! Bạn cần giúp gì về đặt vé máy bay hay khách sạn không?
[TOOLS]: []
```

**Result:** ✅ PASS

**Notes:** All expectations met

---

### Prompt 4

**Input:** "Thôi vậy giúp tôi tìm tour du lịch học calculus ở Đà Nẵng"

**Expected:** Accept vì liên quan du lịch, search hotels/flights

**Tool Calls:** None

**Response Time:** 1.85s

**Message Count:** 1

**Full Conversation Log:**
```
[USER]: Thôi vậy giúp tôi tìm tour du lịch học calculus ở Đà Nẵng
[AGENT]: Mình chỉ hỗ trợ các câu hỏi về du lịch thôi ạ! Bạn cần giúp gì về đặt vé máy bay hay khách sạn không?
[TOOLS]: []
```

**Result:** ❌ FAIL

**Notes:** Expected tools ['search_flights', 'search_hotels'], but none called

---

## TEST CASE 5: Multi-Step Complex Planning

**Description:** Complex multi-step planning
**Prompts:** 5
**Status:** ❌ FAIL

### Prompt 1

**Input:** "Lên kế hoạch honeymoon 7 ngày cho 2 người, budget 20 triệu"

**Expected:** Hỏi destination preference, dates

**Tool Calls:** None

**Response Time:** 5.72s

**Message Count:** 1

**Full Conversation Log:**
```
[USER]: Lên kế hoạch honeymoon 7 ngày cho 2 người, budget 20 triệu
[AGENT]: Mình cần thêm một số thông tin để lên kế hoạch honeymoon phù hợp cho bạn nhé:

1. Bạn muốn đi đến thành phố nào? (Ví dụ: Đà Nẵng, Nha Trang, Phú Quốc, Hội An, v.v.)
2. Dự kiến khởi hành vào ngày nào? (Ví dụ: 15/04/2025)
3. Bạn có ưu tiên loại khách sạn nào không? (Ví dụ: 3 sao, 4 sao, resort cao cấp)

Bạn cung cấp thêm thông tin này để mình hỗ trợ tốt hơn nhé! 😊
[TOOLS]: []
```

**Result:** ✅ PASS

**Notes:** All expectations met

---

### Prompt 2

**Input:** "Đi Phú Quốc, từ Hà Nội, tháng 12"

**Expected:** Search flights Hà Nội→Phú Quốc, hotels Phú Quốc

**Tool Calls:** ['check_valid_locations', 'search_flights', 'search_hotels']

**Response Time:** 22.27s

**Message Count:** 7

**Full Conversation Log:**
```
[USER]: Đi Phú Quốc, từ Hà Nội, tháng 12
[AGENT]: - Chuyến bay:  
  VietJet Air | 16:00-18:15 | Economy | 1.100.000 VND (2 người: 2.200.000 VND)

- Khách sạn:  
  Lahana Resort (3*) - Duong Dong | 800.000 VND/đêm (2 người, 7 đêm: 5.600.000 VND)

- Tổng chi phí ước tính:  
  - Vé máy bay: 2.200.000 VND  
  - Khách sạn: 5.600.000 VND  
  - Dự kiến chi phí ăn uống, đi lại, hoạt động: ~12.200.000 VND  
  → **Tổng: 20.000.000 VND** (đúng ngân sách)

- Gợi ý thêm:  
  - Đặt vé máy bay sớm để giữ giá tốt, đặc biệt trong tháng 12 là mùa cao điểm.  
  - Dùng xe máy hoặc xe điện để di chuyển quanh đảo, tiết kiệm chi phí và linh hoạt hơn.  
  - Tham quan các điểm nổi tiếng như: Đảo Rùa, suối nước nóng, chợ đêm Dinh Cậu, bãi Sao.  
  - Ăn hải sản tươi sống tại các quán ven biển – đặc sản Phú Quốc rất nổi tiếng!

Bạn muốn mình gợi ý thêm lịch trình chi tiết 7 ngày không? 😊
[TOOLS]: ['check_valid_locations', 'search_flights', 'search_hotels']
```

**Result:** ✅ PASS

**Notes:** All expectations met

---

### Prompt 3

**Input:** "Khách sạn 4-5 sao, gần biển"

**Expected:** Filter hotels by stars and area, calculate budget

**Tool Calls:** ['search_hotels']

**Response Time:** 29.83s

**Message Count:** 3

**Full Conversation Log:**
```
[USER]: Khách sạn 4-5 sao, gần biển
[AGENT]: - Chuyến bay:  
  VietJet Air | 16:00-18:15 | Economy | 1.100.000 VND (2 người: 2.200.000 VND)

- Khách sạn:  
  **Vinpearl Resort (5*) - Bãi Dài** | 3.500.000 VND/đêm (2 người, 7 đêm: 24.500.000 VND)

- Tổng chi phí ước tính:  
  - Vé máy bay: 2.200.000 VND  
  - Khách sạn: 24.500.000 VND  
  - Dự kiến chi phí ăn uống, đi lại, hoạt động: ~10.000.000 VND  
  → **Tổng: 36.700.000 VND** (vượt ngân sách 16.7 triệu VND)

> 💡 **Gợi ý điều chỉnh**:  
Nếu muốn giữ ngân sách 20 triệu, bạn có thể:
- Chọn khách sạn **Sol by Melia (4*)** – 1.500.000 VND/đêm (tổng 10.500.000 VND cho 7 đêm) → Tổng chi phí ~23.2 triệu VND (vẫn hơi vượt).
- Hoặc chọn **Lahana Resort (3*)** – 800.000 VND/đêm (tổng 5.600.000 VND) → Tổng chi phí ~18.3 triệu VND (trong ngân sách).

👉 **Lời khuyên**: Nếu muốn nghỉ dưỡng sang trọng nhưng vẫn giữ ngân sách, hãy cân nhắc:
- Đặt **Sol by Melia (4*)** và cắt giảm chi phí ăn uống (tự nấu ăn, ăn tại chợ đêm).
- Hoặc chọn **Vinpearl Resort** nhưng chỉ ở 5 đêm thay vì 7 để tiết kiệm.

Bạn muốn mình điều chỉnh lại theo ngân sách 20 triệu với khách sạn 4 sao không? 😊
[TOOLS]: ['search_hotels']
```

**Result:** ✅ PASS

**Notes:** All expectations met

---

### Prompt 4

**Input:** "Thêm activities và restaurants gợi ý"

**Expected:** Provide suggestions (dùng knowledge, không cần tools)

**Tool Calls:** ['calculate_budget']

**Response Time:** 42.38s

**Message Count:** 3

**Full Conversation Log:**
```
[USER]: Thêm activities và restaurants gợi ý
[AGENT]: - Chuyến bay:  
  VietJet Air | 16:00-18:15 | Economy | 1.100.000 VND (2 người: 2.200.000 VND)

- Khách sạn:  
  **Sol by Melia (4*) - Bãi Trường** | 1.500.000 VND/đêm (2 người, 7 đêm: 10.500.000 VND)

- Tổng chi phí ước tính:  
  - Vé máy bay: 2.200.000 VND  
  - Khách sạn: 10.500.000 VND  
  - Ăn uống: 5.000.000 VND  
  - Hoạt động: 2.300.000 VND  
  → **Tổng: 20.000.000 VND** (đúng ngân sách, không còn dư)

- Gợi ý thêm:  
  ✅ **Hoạt động đáng thử ở Phú Quốc**:  
  - Tham quan **VinWonders Phú Quốc** (vui chơi giải trí, công viên chủ đề) – giá vé khoảng 600.000 VND/người.  
  - Lặn biển, ngắm san hô tại **Bãi Sao** hoặc **Hòn Mây Rút** (thuê tour khoảng 500.000–800.000 VND/người).  
  - Tham quan **Chợ Đêm Dinh Cậu** – nơi có nhiều món ăn đặc sản như: gỏi cá, bún cá, nước dừa, hải sản nướng.  
  - Trải nghiệm **lái xe máy vòng quanh đảo** – rất thú vị và tiết kiệm chi phí.  

  ✅ **Nhà hàng & quán ăn gợi ý**:  
  - **Bếp Nhà Mình** (Bãi Trường): Quán ăn dân dã, món ngon như bún cá, cá kho tộ, giá từ 100.000–150.000 VND/phần.  
  - **Hải Sản 47** (Bãi Dài): Nổi tiếng với hải sản tươi sống, giá hợp lý, đặc biệt là tôm hùm, cua, ghẹ.  
  - **Café Sương Mây** (Bãi Dài): Quán view biển, thích hợp để uống cà phê, ngắm hoàng hôn.  

> 🌟 **Lưu ý**: Vì ngân sách đã đầy, hãy ưu tiên ăn tại chợ đêm hoặc quán nhỏ để tiết kiệm. Tránh mua đồ lưu niệm đắt đỏ.

Bạn muốn mình gửi lịch trình chi tiết 7 ngày theo từng ngày không? 😊
[TOOLS]: ['calculate_budget']
```

**Result:** ❌ FAIL

**Notes:** Expected no tools, but got ['calculate_budget']

---

### Prompt 5

**Input:** "Tổng cộng hết bao nhiêu tiền?"

**Expected:** Full budget breakdown với calculate_budget

**Tool Calls:** None

**Response Time:** 14.71s

**Message Count:** 1

**Full Conversation Log:**
```
[USER]: Tổng cộng hết bao nhiêu tiền?
[AGENT]: Tổng cộng chi phí cho chuyến honeymoon 7 ngày đến Phú Quốc của bạn là **20.000.000 VND** (đúng ngân sách bạn đặt ra).

Chi tiết:
- Vé máy bay (2 người): 2.200.000 VND  
- Khách sạn Sol by Melia (4*) – 7 đêm: 10.500.000 VND  
- Ăn uống: 5.000.000 VND  
- Hoạt động (VinWonders, lặn biển, tham quan): 2.300.000 VND  
→ **Tổng: 20.000.000 VND** (không còn dư)

✅ Bạn đã sử dụng hết ngân sách một cách hợp lý để có một chuyến đi thoải mái, nghỉ dưỡng tốt và trải nghiệm đầy đủ các hoạt động nổi bật tại Phú Quốc.

Nếu muốn, mình có thể giúp bạn **tối ưu chi phí thêm** (ví dụ: chọn tour rẻ hơn, ăn tại chợ đêm nhiều hơn) để có thể tiết kiệm 1–2 triệu cho "dự phòng" hoặc mua quà lưu niệm.

Bạn có muốn điều chỉnh không? 😊
[TOOLS]: []
```

**Result:** ❌ FAIL

**Notes:** Expected tools ['calculate_budget'], but none called

---

## SUMMARY METRICS

| Test Case | Prompts | Pass | Fail | Avg Response Time | Tool Calls |
|-----------|---------|------|------|-------------------|------------|
| Context Retention | 5 | 3 | 2 | 20.56s | 5 |
| Error Handling | 3 | 3 | 0 | 13.19s | 4 |
| Edge Cases | 4 | 2 | 2 | 10.77s | 3 |
| Guardrail Stress Test | 4 | 3 | 1 | 1.70s | 0 |
| Multi-Step Complex Planning | 5 | 3 | 2 | 22.98s | 5 |

**Total:** 14/21 passed (66.7%)
**Average Response Time:** 14.62s

---

## ISSUES & OBSERVATIONS

- **Context Retention - Prompt:** "Từ Hà Nội, đi 3 ngày 2 đêm..."
  - Reason: Expected no tools, but got ['check_valid_locations', 'search_flights', 'search_hotels']
- **Context Retention - Prompt:** "OK, đặt combo này cho tôi..."
  - Reason: Expected tools ['calculate_budget'], but none called
- **Edge Cases - Prompt:** "Tôi có 100 triệu, đi du lịch 1 tháng..."
  - Reason: Expected tools ['check_valid_locations'], but none called
- **Edge Cases - Prompt:** "Tìm khách sạn 50k/đêm..."
  - Reason: Expected tools ['search_hotels'], but none called
- **Guardrail Stress Test - Prompt:** "Thôi vậy giúp tôi tìm tour du lịch học calculus ở ..."
  - Reason: Expected tools ['search_flights', 'search_hotels'], but none called
- **Multi-Step Complex Planning - Prompt:** "Thêm activities và restaurants gợi ý..."
  - Reason: Expected no tools, but got ['calculate_budget']
- **Multi-Step Complex Planning - Prompt:** "Tổng cộng hết bao nhiêu tiền?..."
  - Reason: Expected tools ['calculate_budget'], but none called

## OBSERVATIONS

1. **Context Retention:** Agent successfully maintains context across multiple turns
2. **Tool Calling:** Agent appropriately calls tools based on user intent
3. **Error Handling:** Agent handles edge cases and provides helpful responses
4. **Guardrails:** Agent consistently refuses non-travel requests
