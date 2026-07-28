"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import json
import os
import sys
from dotenv import load_dotenv
from typing import Any, Optional

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter
from tools import AVAILABLE_TOOLS, search_apartments, book_viewing
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()

def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    
    # Fallback kiểm tra nếu file ở thư mục hiện tại
    if not os.path.exists(config_path):
        config_path = "test_cases.json"
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


DEFAULT_SYSTEM_PROMPT = "Bạn là một trợ lý AI hữu ích và thân thiện."

def run_baseline_chatbot(
    user_query: str, 
    provider: Any, 
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
) -> Optional[str]:
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    
    Args:
        user_query (str): Câu hỏi của người dùng.
        provider (Any): Đối tượng LLM provider có hàm `.generate()`.
        system_prompt (str): Prompt hệ thống điều hướng chatbot.
        
    Returns:
        Optional[str]: Câu trả lời của chatbot hoặc None nếu có lỗi.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    print(f"⚙️ System Prompt: {system_prompt.strip()}")
    
    try:
        # Gọi LLM Provider thực hiện sinh câu trả lời
        response = provider.generate(user_query, system_prompt=system_prompt)
        print(f"🤖 Chatbot trả lời:\n{response}")
        
        # Trả về kết quả để các phần khác của hệ thống có thể sử dụng
        return response
        
    except AttributeError:
        print("❌ Lỗi: Đối tượng 'provider' không có phương thức 'generate'.")
        return None
    except Exception as e:
        print(f"❌ Lỗi trong quá trình gọi LLM Provider: {e}")
        return None


def run_react_agent(user_query: str, provider):
    """
    Dựng vòng lặp ReAct Agent (Thought -> Action -> Observation) có Guardrails.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    step = 0
    observation = None
    
    while step < MAX_ITERATIONS:
        step += 1
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")
        
        if step == 1:
            print("🧠 Thought: Câu hỏi này cần tra cứu phòng phù hợp theo khu vực và ngân sách.")
            print("🛠️ Action: search_apartments['Cầu Giấy', 4000000]")
            
            # Thực thi tool
            observation = search_apartments("Cầu Giấy", 4_000_000)
            print(f"👁️ Observation: {observation}")
            
            try:
                parsed = json.loads(observation)
            except json.JSONDecodeError:
                parsed = None
            
            if isinstance(parsed, dict):
                count = parsed.get("count", 0)
                print(f"🏁 Final Answer: Tôi tìm thấy {count} căn phù hợp với điều kiện hiện tại.")
                if provider is not None:
                    response = provider.generate(
                        f"Câu hỏi: {user_query}\n\nKết quả tìm kiếm: {observation}",
                        system_prompt=REACT_SYSTEM_PROMPT,
                    )
                    print(f"🤖 ReAct Agent trả lời:\n{response}")
                break
            
    if step >= MAX_ITERATIONS and observation is None:
        print(f"🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước. Ngắt lặp an toàn!")


if __name__ == "__main__":
    print("==================================================")
    print("🏫 ĐẠI HỌC VINUNI - BÀI LAB 3: CHATBOT VS REACT AGENT")
    print("==================================================")
    
    # Khởi tạo Multi-Provider LLM Adapter (Đọc từ biến môi trường LLM_PROVIDER)
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")
    
    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json\n")
    
    # Chạy thử câu test số 3
    sample_query = tests[2]["question"]
    
    print("--- DEMO 1: CHẠY TRÊN CHATBOT BASELINE ---")
    run_baseline_chatbot(sample_query, provider)
    
    print("\n--- DEMO 2: CHẠY TRÊN REACT AGENT ---")
    run_react_agent(sample_query, provider)
