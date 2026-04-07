# LAB 4: XÂY DỰNG AI AGENT ĐẦU TIÊN VỚI LANGGRAPH

**Thời lượng:** 240 Phút (4 Giờ)

## Bối cảnh

Bạn được giao nhiệm vụ xây dựng một **"Trợ lý Du lịch Thông minh"** cho startup TravelBuddy. Agent này giúp người dùng lên kế hoạch chuyến đi bằng cách tự động tra cứu chuyến bay, kiểm tra ngân sách, và tìm kiếm khách sạn phù hợp.

**Điểm đặc biệt:** Agent phải biết **KẾT HỢP** thông tin từ nhiều nguồn để đưa ra gợi ý tối ưu – không chỉ trả lời từng câu rời rạc.

*Ví dụ:* Khi user nói "Tôi muốn đi Đà Nẵng cuối tuần này, budget 5 triệu", Agent phải tự tra vé máy bay, tính chi phí còn lại, rồi tìm khách sạn vừa túi tiền – tất cả trong một cuộc hội thoại.

---

## PHẦN 0: SETUP MÔI TRƯỜNG (30 Phút)

**Mục tiêu:** Đảm bảo gọi được API thành công trước khi vào bài.

### 1. Khởi tạo dự án & Cài đặt thư viện

```bash
mkdir lab4_agent && cd lab4_agent
python -m venv venv

# Mac/Linux
source venv/bin/activate
# Windows
# venv\Scripts\activate

pip install langchain langchain-openai langgraph python-dotenv
```

### 2. Cấu hình API Key

Tạo file `.env`:

```text
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Sanity Check

Tạo file `test_api.py`:

```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")
print(llm.invoke("Xin chào?").content)
```

*Chạy `python test_api.py`, nếu in ra câu trả lời, có thể bắt đầu bài tập.*

---

## PHẦN 1: THIẾT KẾ SYSTEM PROMPT (45 Phút)

**Mục tiêu:** Định hình "Não bộ" của Agent – cách nó suy nghĩ và hành xử.

**Nhiệm vụ:** Tạo file `system_prompt.txt` theo cấu trúc XML gồm các phần sau:

```xml
<persona>
Bạn là trợ lý du lịch của TravelBuddy – thân thiện, am hiểu du lịch Việt Nam, và luôn tư vấn dựa trên ngân sách thực tế của khách hàng. Bạn nói chuyện tự nhiên như một người bạn đi du lịch nhiều, không robot.
</persona>

<rules>
1. Trả lời bằng tiếng Việt.
2. [Sinh viên bổ sung thêm các quy tắc...]
</rules>

<tools_instruction>
Bạn có 3 công cụ:
- search_flights: Tìm chuyến bay.
- search_hotels: Tìm khách sạn.
- calculate_budget: Tính toán ngân sách còn lại.
</tools_instruction>

<response_format>
Khi tư vấn chuyến đi, trình bày theo cấu trúc:
- Chuyến bay:
- Khách sạn:
- Tổng chi phí ước tính:
- Gợi ý thêm:
</response_format>

<constraints>
Từ chối mọi yêu cầu không liên quan đến du lịch/đặt phòng/đặt vé (VD: viết code, làm bài tập, tư vấn tài chính, chính trị).
</constraints>
```

**Bài tập:** Dựa trên mẫu trên, hãy tùy chỉnh và bổ sung thêm rules hoặc constraints mà bạn cho là cần thiết. Giải thích lý do trong comment.

---

## PHẦN 2: LẬP TRÌNH CUSTOM TOOLS (45 Phút)

**Mục tiêu:** Thiết kế "Tay chân" cho Agent với 3 tools sử dụng mock data.

**Nhiệm vụ:** Tạo file `tools.py` và triển khai các hàm theo yêu cầu.

```python
from langchain_core.tools import tool

# MOCK DATA
FLIGHTS_DB = {
    ("Hà Nội", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "07:20", "price": 1450000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "14:00", "arrival": "15:20", "price": 2800000, "class": "business"},
        {"airline": "VietJet Air", "departure": "08:30", "arrival": "09:50", "price": 890000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "11:00", "arrival": "12:20", "price": 1200000, "class": "economy"},
    ],
    ("Hà Nội", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "07:00", "arrival": "09:15", "price": 2100000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "10:00", "arrival": "12:15", "price": 1350000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "16:00", "arrival": "18:15", "price": 1100000, "class": "economy"},
    ],
    ("Hà Nội", "Hồ Chí Minh"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "08:10", "price": 1600000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "07:30", "arrival": "09:40", "price": 950000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "12:00", "arrival": "14:10", "price": 1300000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "18:00", "arrival": "20:10", "price": 3200000, "class": "business"},
    ],
    ("Hồ Chí Minh", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "09:00", "arrival": "10:20", "price": 1300000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "13:00", "arrival": "14:20", "price": 780000, "class": "economy"},
    ],
    ("Hồ Chí Minh", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "08:00", "arrival": "09:00", "price": 1100000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "15:00", "arrival": "16:00", "price": 650000, "class": "economy"},
    ],
}

HOTELS_DB = {
    "Đà Nẵng": [
        {"name": "Mường Thanh Luxury", "stars": 5, "price_per_night": 1800000, "area": "Mỹ Khê", "rating": 4.5},
        {"name": "Sala Danang Beach", "stars": 4, "price_per_night": 1200000, "area": "Mỹ Khê", "rating": 4.3},
        {"name": "Fivitel Danang", "stars": 3, "price_per_night": 650000, "area": "Sơn Trà", "rating": 4.1},
        {"name": "Memory Hostel", "stars": 2, "price_per_night": 250000, "area": "Hải Châu", "rating": 4.6},
        {"name": "Christina's Homestay", "stars": 2, "price_per_night": 350000, "area": "An Thượng", "rating": 4.7},
    ],
    "Phú Quốc": [
        {"name": "Vinpearl Resort", "stars": 5, "price_per_night": 3500000, "area": "Bãi Dài", "rating": 4.4},
        {"name": "Sol by Meliá", "stars": 4, "price_per_night": 1500000, "area": "Bãi Trường", "rating": 4.2},
        {"name": "Lahana Resort", "stars": 3, "price_per_night": 800000, "area": "Dương Đông", "rating": 4.0},
        {"name": "9Station Hostel", "stars": 2, "price_per_night": 200000, "area": "Dương Đông", "rating": 4.5},
    ],
    "Hồ Chí Minh": [
        {"name": "Rex Hotel", "stars": 5, "price_per_night": 2800000, "area": "Quận 1", "rating": 4.3},
        {"name": "Liberty Central", "stars": 4, "price_per_night": 1400000, "area": "Quận 1", "rating": 4.1},
        {"name": "Cochin Zen Hotel", "stars": 3, "price_per_night": 550000, "area": "Quận 3", "rating": 4.4},
        {"name": "The Common Room", "stars": 2, "price_per_night": 1800000, "area": "Quận 1", "rating": 4.6},
    ],
}

@tool
def search_flights(origin: str, destination: str) -> str:
    """Tìm kiếm các chuyến bay giữa hai thành phố."""
    # TODO: Sinh viên tự triển khai
    # 1. Tra cứu FLIGHTS_DB với key (origin, destination)
    # 2. Nếu không tìm thấy, thử tra ngược (destination, origin)
    # 3. Format danh sách chuyến bay dễ đọc kèm giá tiền (VD: 1.450.000₫)
    pass

@tool
def search_hotels(city: str, max_price_per_night: int = 99999999) -> str:
    """Tìm kiếm khách sạn tại một thành phố, có thể lọc theo giá tối đa."""
    # TODO: Sinh viên tự triển khai
    # 1. Tra cứu HOTELS_DB[city]
    # 2. Lọc theo max_price_per_night
    # 3. Sắp xếp theo rating giảm dần
    # 4. Format kết quả đẹp hoặc báo lỗi nếu không tìm thấy
    pass

@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """Tính toán ngân sách còn lại sau khi trừ các khoản chi phí."""
    # TODO: Sinh viên tự triển khai
    # 1. Parse chuỗi expenses thành dict {'tên khoản': số tiền}
    # 2. Tính tổng chi phí và số tiền còn lại
    # 3. Format bảng chi tiết và cảnh báo nếu vượt ngân sách
    pass
```

**Yêu cầu logic:**

- `search_flights`: Xử lý tra cứu cả hai chiều.
- `search_hotels`: Lọc theo giá và sắp xếp theo đánh giá.
- `calculate_budget`: Phải thực hiện tính toán thực tế và xử lý lỗi định dạng.

---

## PHẦN 3: TRIỂN KHAI LANGGRAPH (60 Phút)

**Mục tiêu:** Tạo vòng lặp Agent để tự động quyết định gọi tool.

**Nhiệm vụ:** Tạo file `agent.py`.

```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from tools import search_flights, search_hotels, calculate_budget
from dotenv import load_dotenv

load_dotenv()

# 1. Đọc System Prompt
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# 2. Khai báo State
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# 3. Khởi tạo LLM và Tools
tools_list = [search_flights, search_hotels, calculate_budget]
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools_list)

# 4. Agent Node
def agent_node(state: AgentState):
    messages = state["messages"]
    if not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    
    response = llm_with_tools.invoke(messages)
    
    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"Gọi tool: {tc['name']}({tc['args']})")
    else:
        print(f"Trả lời trực tiếp")
        
    return {"messages": [response]}

# 5. Xây dựng Graph
builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
tool_node = ToolNode(tools_list)
builder.add_node("tools", tool_node)

# TODO: Sinh viên khai báo các cạnh (edges)
# builder.add_edge(START, "agent")
# builder.add_conditional_edges("agent", tools_condition)
# builder.add_edge("tools", "agent")

graph = builder.compile()

# 6. Chat loop
if __name__ == "__main__":
    print("="*60)
    print("TravelBuddy - Trợ lý Du lịch Thông minh")
    print("Gõ 'quit' để thoát")
    print("="*60)
    
    while True:
        user_input = input("\nBạn: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        
        print("\nTravelBuddy đang suy nghĩ...")
        result = graph.invoke({"messages": [("human", user_input)]})
        final_result = result["messages"][-1]
        print(f"\nTravelBuddy: {final_result.content}")
```

---

## PHẦN 4: TEST CASES & CHẨN ĐOÁN (45 Phút)

Sinh viên chạy agent và thực hiện 5 kịch bản sau, lưu lại kết quả vào `test_results.md`:

1. **Test 1: Direct Answer (Không cần tool)**
  - User: "Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu."
    - Kỳ vọng: Agent chào hỏi, gợi ý hoặc hỏi thêm sở thích. Không gọi tool.
2. **Test 2: Single Tool Call**
  - User: "Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng."
    - Kỳ vọng: Gọi `search_flights`, liệt kê các chuyến bay từ DB.
3. **Test 3: Multi-Step Tool Chaining**
  - User: "Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!"
    - Kỳ vọng: Agent tự xâu chuỗi: Tìm vé rẻ nhất -> Tìm khách sạn phù hợp -> Tính toán ngân sách -> Tổng hợp gợi ý.
4. **Test 4: Missing Info / Clarification**
  - User: "Tôi muốn đặt khách sạn."
    - Kỳ vọng: Agent hỏi lại thông tin thành phố, ngân sách... không gọi tool ngay.
5. **Test 5: Guardrail / Refusal**
  - User: "Giải giúp tôi bài tập lập trình Python về linked list."
    - Kỳ vọng: Từ chối lịch sự, chỉ hỗ trợ du lịch.

---

## PHẦN 5: DELIVERABLES & ĐÁNH GIÁ (15 Phút)

**Nộp bài:** Nén thành file `MSSV_Lab4.zip` gồm:

- `system_prompt.txt`
- `tools.py`
- `agent.py`
- `test_results.md` (Kèm console log của 5 test cases)

### Rubric Đánh giá:


| Tiêu chí                                                     | Điểm |
| ------------------------------------------------------------ | ---- |
| Setup LangGraph đúng (Nodes, Edges, Graph chạy được)         | 25%  |
| Tool implementations đúng logic + xử lý lỗi                  | 25%  |
| System Prompt kiên cố (Vượt Test 4 + Test 5)                 | 20%  |
| Agent thực hiện multi-step tool chaining thành công (Test 3) | 20%  |
| Code sạch, có type hints, logging rõ ràng                    | 10%  |


