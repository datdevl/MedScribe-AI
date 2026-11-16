import os
import streamlit as st
from google import genai

# ── Thông tin Đề tài Nghiên cứu Khoa học ──────────────────────
PROJECT_ID = "129"
PROJECT_NAME = "Hệ thống Bệnh án Điện tử Thông minh & Hỗ trợ Ra Quyết định Lâm sàng (MedScribe AI)"
PROJECT_FULL_TITLE = (
    "Nghiên cứu và xây dựng hệ thống hỗ trợ ghi chép hồ sơ bệnh án điện tử từ giọng nói "
    "kết hợp hỗ trợ ra quyết định lâm sàng sử dụng công nghệ nhận dạng giọng nói (ASR) "
    "và mô hình ngôn ngữ lớn (LLM)"
)
RESEARCHER_NAME = "Lê Văn Đạt"
RESEARCHER_ID = "1971020090"
SUPERVISOR = "ThS. Nguyễn Ngọc Ân"
FACULTY = "Khoa Công nghệ Thông tin"

APP_NAME = "MedScribe AI"
APP_ICON = "🏥"

# Danh sách mô hình AI hỗ trợ hoạt động chuẩn xác
AVAILABLE_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
    "gemini-flash-latest",
]
DEFAULT_MODEL = "gemini-3.6-flash"


def get_api_key():
    """Lấy API key từ Streamlit Secrets hoặc biến môi trường."""
    key = ""
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            key = str(st.secrets["GOOGLE_API_KEY"]).strip()
        elif "GEMINI_API_KEY" in st.secrets:
            key = str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass

    if not key:
        key = os.environ.get("GOOGLE_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")

    # Kiểm tra key trong session_state (nếu người dùng nhập trên giao diện)
    if not key and "user_api_key" in st.session_state and st.session_state.user_api_key:
        key = str(st.session_state.user_api_key).strip()

    return key


def get_client():
    """Khởi tạo Google GenAI Client."""
    api_key = get_api_key()
    if not api_key:
        return None

    # Tránh cảnh báo xung đột biến môi trường
    os.environ.pop("GOOGLE_API_KEY", None)
    os.environ.pop("GEMINI_API_KEY", None)

    try:
        return genai.Client(api_key=api_key)
    except Exception:
        return None


def get_model_id():
    """Lấy model ID đã cấu hình hoặc từ session state."""
    if "selected_model" in st.session_state and st.session_state.selected_model:
        return st.session_state.selected_model
    try:
        if "GEMINI_MODEL" in st.secrets:
            model = str(st.secrets["GEMINI_MODEL"]).strip()
            if model:
                return model
    except Exception:
        pass
    return DEFAULT_MODEL
