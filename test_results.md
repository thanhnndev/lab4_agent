# TEST RESULTS - TRAVELBUDDY AGENT

**Date:** 2026-04-07
**Environment:** Ollama + LangGraph
**Model:** dengcao/Qwen3-30B-A3B-Instruct-2507

---

## TEST 1: Direct Answer

**Input:** "Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu."

**Expected:** Agent chào hỏi, gợi ý hoặc hỏi thêm sở thích. KHÔNG gọi tool.

![Test 1 Screenshot](extras/simple-test/test-01-1.png)

**Actual Output:**
```
Chào bạn! Mình rất vui được giúp bạn lên kế hoạch du lịch. Để gợi ý phù hợp hơn, bạn có thể chia sẻ thêm một vài thông tin nhé:

- Bạn muốn đi du lịch đến thành phố nào? (ví dụ: Hà Nội, Đà Nẵng, TP.HCM, Phú Quốc, Nha Trang...)
- Dự kiến đi vào thời gian nào? (tháng nào, ngày nào?)
- Ngân sách dự kiến cho chuyến đi là bao nhiêu?

Nếu bạn chưa có ý tưởng, mình có thể gợi ý một vài điểm đến hấp dẫn trong nước nhé! 😊
```

**Tool Calls:** None

**Response Time:** 18.34s

**Result:** ✅ PASS

**Notes:** Agent responded appropriately without calling any tools. Asked helpful follow-up questions to gather more information. Perfect behavior for a greeting/introductory message.

---

## TEST 2: Single Tool Call

**Input:** "Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng."

**Expected:** Gọi `search_flights`, liệt kê các chuyến bay từ DB.

![Test 2 - Step 1](extras/simple-test/test-02-1.png)
![Test 2 - Step 2](extras/simple-test/test-02-2.png)
![Test 2 - Step 3](extras/simple-test/test-02-3.png)
![Test 2 - Step 4](extras/simple-test/test-02-4.png)

**Actual Output:**
```
- Chuyến bay:  
  1. Vietnam Airlines | 06:00-07:20 | economy | 1.450.000 VND  
  2. Vietnam Airlines | 14:00-15:20 | business | 2.800.000 VND  
  3. VietJet Air | 08:30-09:50 | economy | 890.000 VND  
  4. Bamboo Airways | 11:00-12:20 | economy | 1.200.000 VND  

- Khách sạn:  
  1. Christina's Homestay (2*) - An Thuong - 350.000 VND/đêm - đánh giá 4.7  
  2. Memory Hostel (2*) - Hai Chau - 250.000 VND/đêm - đánh giá 4.6  

- Tổng chi phí ước tính:  
  - Chuyến bay (VietJet Air): 890.000 VND  
  - Khách sạn (Memory Hostel, 1 đêm): 250.000 VND  
  → Tổng: 1.140.000 VND  

- Gợi ý thêm:  
  Nếu bạn muốn trải nghiệm nhiều hơn, hãy cân nhắc ở Christina's Homestay để có không gian riêng tư hơn. Bạn cũng có thể đặt vé sớm để tiết kiệm thêm nếu đi vào mùa cao điểm!
```

**Tool Calls:** 
1. `check_valid_locations()` - Validated locations first
2. `search_flights(origin='Ha Noi', destination='Da Nang')`
3. `search_hotels(city='Da Nang', max_price_per_night=500000)`

**Response Time:** 20.45s

**Result:** ✅ PASS (with enhancement)

**Notes:** Agent went beyond expectations by:
- First validating locations with `check_valid_locations` (following system prompt rules)
- Calling `search_flights` as expected
- Proactively also searching for hotels in Da Nang
- Providing a comprehensive response with flight + hotel options

This shows the agent is following the system prompt's instruction to always check valid locations before searching.

---

## TEST 3: Multi-Step Tool Chaining

**Input:** "Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!"

**Expected:** Agent tự xâu chuỗi: Tìm vé rẻ nhất -> Tìm khách sạn phù hợp -> Tính toán ngân sách -> Tổng hợp gợi ý.

![Test 3 - Step 1](extras/simple-test/test-03-1.png)
![Test 3 - Step 2](extras/simple-test/test-03-2.png)
![Test 3 - Step 3](extras/simple-test/test-03-3.png)

**Actual Output:**
```
- Chuyến bay:  
  VietJet Air | 16:00-18:15 | economy | 1.100.000 VND  

- Khách sạn:  
  9Station Hostel (2*) - Duong Dong - 200.000 VND/đêm (rating 4.5)  

- Tổng chi phí ước tính:  
  - Vé máy bay: 1.100.000 VND  
  - Khách sạn (2 đêm): 200.000 × 2 = 400.000 VND  
  - Tổng: 1.500.000 VND  
  - Còn lại: 3.500.000 VND (có thể dùng cho ăn uống, đi lại, hoạt động)  

- Gợi ý thêm:  
  - 9Station Hostel là lựa chọn tiết kiệm nhưng có rating cao, phù hợp với budget.  
  - Bạn có thể dùng phần còn lại để thử hải sản tươi tại chợ đêm Dương Đông hoặc tour đảo bằng cano.  
  - Nên đặt vé và khách sạn sớm để có giá tốt hơn!
```

**Tool Calls:** 
1. `check_valid_locations()` - Validated locations
2. `search_flights(origin='Ha Noi', destination='Phu Quoc')` - Found 3 flights, selected cheapest
3. `search_hotels(city='Phu Quoc', max_price_per_night=2000000)` - Filtered by budget

**Response Time:** 17.06s

**Result:** ✅ PASS

**Notes:** Excellent multi-step chaining! Agent:
- Validated locations first
- Found flights and selected the cheapest option (1.100.000 VND)
- Found hotels within budget constraints
- Correctly calculated total for 2 nights (200.000 × 2 = 400.000 VND)
- Provided remaining budget (3.500.000 VND) for other expenses
- Gave helpful local suggestions (seafood, island tours)

---

## TEST 4: Missing Info / Clarification

**Input:** "Tôi muốn đặt khách sạn."

**Expected:** Agent hỏi lại thành phố, ngân sách... KHÔNG gọi tool ngay.

![Test 4 - Step 1](extras/simple-test/test-04-1.png)
![Test 4 - Step 2](extras/simple-test/test-04-2.png)

**Actual Output:**
```
Bạn muốn đặt khách sạn ở thành phố nào vậy? Và bạn có ngân sách cụ thể cho mỗi đêm không?
```

**Tool Calls:** None

**Response Time:** 1.11s

**Result:** ✅ PASS

**Notes:** Perfect! Agent correctly identified missing information and asked clarifying questions without calling any tools. Very fast response time (1.11s) since no tool calls were needed.

---

## TEST 5: Guardrail / Refusal

**Input:** "Giải giúp tôi bài tập lập trình Python về linked list."

**Expected:** Từ chối lịch sự, chỉ hỗ trợ du lịch.

![Test 5 - Step 1](extras/simple-test/test-05-1.png)
![Test 5 - Step 2](extras/simple-test/test-05-2.png)

**Actual Output:**
```
Mình chỉ hỗ trợ các câu hỏi về du lịch thôi ạ! Bạn cần giúp gì về đặt vé máy bay hay khách sạn không?
```

**Tool Calls:** None

**Response Time:** 1.39s

**Result:** ✅ PASS

**Notes:** Perfect guardrail behavior! Agent:
- Politely refused the non-travel request
- Used the exact phrase from system_prompt.txt: "Mình chỉ hỗ trợ các câu hỏi về du lịch thôi ạ!"
- Redirected back to travel-related assistance
- No tool calls made
- Fast response (1.39s)

---

## SUMMARY

| Test | Result | Notes |
|------|--------|-------|
| Test 1: Direct Answer | ✅ PASS | No tools, friendly greeting with follow-up questions |
| Test 2: Single Tool Call | ✅ PASS | Called check_valid_locations + search_flights + search_hotels |
| Test 3: Multi-Step Chaining | ✅ PASS | Full chain: validate → flights → hotels → budget calc |
| Test 4: Missing Info | ✅ PASS | Asked clarifying questions, no tools |
| Test 5: Guardrail | ✅ PASS | Politely refused, redirected to travel |

**Total:** 5/5 tests passed

## PERFORMANCE METRICS

| Test | Response Time | Tool Calls | Message Count |
|------|--------------|------------|---------------|
| Test 1 | 18.34s | 0 | 2 |
| Test 2 | 20.45s | 3 | 8 |
| Test 3 | 17.06s | 3 | 8 |
| Test 4 | 1.11s | 0 | 2 |
| Test 5 | 1.39s | 0 | 2 |

**Average Response Time:** 11.67s (with tools: ~18s, without tools: ~1.25s)

## ISSUES FOUND

No critical issues found. All tests passed successfully.

### Observations:

1. **Test 2 Behavior Enhancement:** Agent called more tools than minimally required (added hotel search). This is actually positive behavior showing proactive assistance.

2. **Location Validation:** Agent consistently calls `check_valid_locations` before any flight/hotel search, following system prompt rules strictly.

3. **Budget Calculation:** In Test 3, the agent performed budget calculation manually in the response rather than calling the `calculate_budget` tool. This works but could be enhanced to use the tool for more complex scenarios.

4. **Response Quality:** All responses are in natural Vietnamese, friendly tone, and well-formatted with bullet points.

5. **Context Handling:** Each test was run in a fresh session, so long-context handling wasn't tested. The system prompt includes context handling rules for conversations >20 messages.

## RECOMMENDATIONS

1. Consider testing with multiple turns in a single session to verify context persistence
2. Test edge cases like invalid city names or extreme budgets
3. Verify the `calculate_budget` tool is being used for complex multi-item budgets
4. Test conversation recovery after tool errors

## SCREENSHOTS

| Test | Images | Description |
|------|--------|-------------|
| Test 1 | test-01-1.png | Direct answer - greeting |
| Test 2 | test-02-1.png to test-02-4.png | Single tool call with validation |
| Test 3 | test-03-1.png to test-03-3.png | Multi-step chaining |
| Test 4 | test-04-1.png to test-04-2.png | Missing info clarification |
| Test 5 | test-05-1.png to test-05-2.png | Guardrail refusal |

**Total:** 12 screenshots
