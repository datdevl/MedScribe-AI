import streamlit as st
import streamlit.components.v1 as stc
import time
import base64
import os
from .utils import safe
from .patient_db import get_stats
from .config import (
    APP_NAME, APP_ICON, AVAILABLE_MODELS, get_model_id, get_api_key
)

# ── Đường dẫn và xử lý Base64 cho Logo ──────────────────────
LOGO_WEB = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo_web.png")
LOGO_ORIG = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")

def get_logo_base64():
    """Lấy chuỗi base64 của logo để nhúng trực tiếp vào HTML."""
    target = LOGO_WEB if os.path.exists(LOGO_WEB) else LOGO_ORIG
    if os.path.exists(target):
        try:
            with open(target, "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
        except Exception:
            pass
    return ""


def render_html_clean(html_content):
    """
    Làm sạch triệt để toàn bộ khoảng trắng đầu dòng và dòng trống
    để ngăn chặn CommonMark phân tích nhầm HTML thành markdown code block.
    """
    lines = [line.strip() for line in html_content.strip().splitlines() if line.strip()]
    st.markdown("\n".join(lines), unsafe_allow_html=True)


def render_sidebar():
    """Hiển thị sidebar sáng chuẩn y tế chứa thông tin đề tài, bác sĩ và AI."""
    logo_b64 = get_logo_base64()
    logo_html = (
        f'<img src="{logo_b64}" style="max-height: 118px; max-width: 280px; object-fit: contain; margin-bottom: 6px;" alt="Logo" />'
        if logo_b64 else f'<div style="font-size: 32px;">{APP_ICON}</div>'
    )

    with st.sidebar:
        # ── Logo & Tên dự án chuẩn sáng ──
        render_html_clean(f"""
<div style="text-align: center; padding: 10px 0 14px 0; border-bottom: 1px solid #e2e8f0; margin-bottom: 14px;">
{logo_html}
<div style="font-size: 17px; font-weight: 800; color: #005baa; letter-spacing: -0.3px;">{APP_NAME}</div>
<div style="font-size: 11.5px; font-weight: 600; color: #00a651; text-transform: uppercase;">Hệ Thống EMR & CDSS Thông Minh</div>
</div>
""")

        st.divider()

        # ── Cấu hình Mô hình AI & API Key ──
        st.markdown('<div style="font-size: 12px; font-weight: 700; color: #005baa; text-transform: uppercase; margin-bottom: 6px;">⚙️ CẤU HÌNH AI & MÔ HÌNH</div>', unsafe_allow_html=True)
        
        current_model = get_model_id()
        model_idx = AVAILABLE_MODELS.index(current_model) if current_model in AVAILABLE_MODELS else 0
        selected_model = st.selectbox(
            "Mô hình AI:",
            AVAILABLE_MODELS,
            index=model_idx,
            key="model_selector"
        )
        st.session_state.selected_model = selected_model

        has_api_key = bool(get_api_key())
        if has_api_key:
            st.markdown('<div style="font-size: 12px; color: #00a651; font-weight: 600;">🟢 API Key: Đã sẵn sàng</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size: 12px; color: #f59e0b; font-weight: 600;">⚠️ Chưa có API Key</div>', unsafe_allow_html=True)
            user_key = st.text_input("Nhập Google Gemini API Key:", type="password", key="user_key_input")
            if user_key:
                st.session_state.user_api_key = user_key

        st.divider()

        # ── Thông tin Bác sĩ phụ trách ──
        st.markdown('<div style="font-size: 12px; font-weight: 700; color: #005baa; text-transform: uppercase; margin-bottom: 6px;">👨‍⚕️ THÔNG TIN PHÒNG KHÁM</div>', unsafe_allow_html=True)

        doctor_name = st.text_input("Bác sĩ phụ trách", "BS. Lê Văn Đạt", placeholder="Tên bác sĩ...")
        clinic_name = st.text_input("Cơ sở y tế", "Hệ thống Y tế Đa khoa Quốc tế", placeholder="Tên cơ sở...")
        clinic_addr = st.text_input("Địa chỉ", "Quận Hoàn Kiếm, Hà Nội", placeholder="Địa chỉ...")
        clinic_phone = st.text_input("Đường dây nóng", "1900 56 56 56", placeholder="Số điện thoại...")

        st.session_state.doctor_name = doctor_name
        st.session_state.clinic_name = clinic_name
        st.session_state.clinic_addr = clinic_addr
        st.session_state.clinic_phone = clinic_phone

        st.divider()

        # ── Trạng thái CSDL ──
        stats = get_stats()
        render_html_clean(f"""
<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 12px; font-size: 12.5px; color: #334155;">
<span style="display: inline-block; width: 8px; height: 8px; background: #00a651; border-radius: 50%; margin-right: 6px;"></span>
Hệ thống Online &bull; <b>{stats['total']}</b> hồ sơ &bull; <b>{stats['today']}</b> hôm nay
</div>
""")

        st.caption("⚠️ Hệ thống CDSS hỗ trợ phân tích và cảnh báo an toàn. Bác sĩ điều trị chịu trách nhiệm quyết định y khoa cuối cùng.")

    return doctor_name


def render_header():
    """
    Hiển thị Header chuẩn phong cách MEDLATEC (https://medlatec.vn):
    1. Thanh Topbar sáng: Logo từ assets/logo.png, Menu điều hướng, Hotline 1900 56 56 56.
    2. Banner Carousel Slider trượt mượt mà từ trái sang phải.
    """
    logo_b64 = get_logo_base64()
    logo_tag = (
        f'<img src="{logo_b64}" class="medlatec-logo-img" alt="MedScribe Logo" />'
        if logo_b64 else f'<div style="font-size: 36px; line-height: 1;">{APP_ICON}</div>'
    )

    header_html = f"""
<div class="medlatec-topbar">
<div class="medlatec-logo-wrap">
{logo_tag}
<div>
<div class="medlatec-brand-title">{APP_NAME}</div>
<div class="medlatec-brand-sub">HỆ THỐNG Y TẾ THÔNG MINH</div>
</div>
</div>
<div class="medlatec-menu-pills">
<span class="medlatec-menu-item">Trang chủ</span>
<span class="medlatec-menu-item">Khám bệnh ASR</span>
<span class="medlatec-menu-item">Trợ lý CDSS</span>
<span class="medlatec-menu-item">Hồ sơ bệnh nhân</span>
<span class="medlatec-menu-item">Nghiên cứu khoa học</span>
</div>
<div class="medlatec-contact-pill">
<div class="medlatec-hotline-icon">📞</div>
<div>
<div class="medlatec-hotline-label">Đường dây nóng 24/7</div>
<div class="medlatec-hotline-num">1900 56 56 56</div>
</div>
</div>
</div>

<div class="banner-slider-container">
<div class="banner-track">
<div class="banner-slide slide-1">
<div class="banner-content">
<div class="banner-tag">✨ ĐỘT PHÁ CÔNG NGHỆ NHẬN DẠNG GIỌNG NÓI (ASR)</div>
<div class="banner-title">Chuyển Đổi Thoại Khám Bệnh <span>Thành Bệnh Án Điện Tử</span></div>
<div class="banner-desc">Tự động số hóa cuộc đối thoại giữa Bác sĩ và Người bệnh thành hồ sơ bệnh án điện tử chuẩn SOAP trong 2 giây. Tiết kiệm 70% thời gian ghi chép thủ công.</div>
<div class="banner-pills-row">
<span class="banner-mini-pill">🎙️ Gỡ băng đa phương thức</span>
<span class="banner-mini-pill">📝 Chuẩn hóa SOAP quốc tế</span>
<span class="banner-mini-pill">⚡ Xử lý thời gian thực</span>
</div>
</div>
<div class="banner-graphic">🩺</div>
</div>

<div class="banner-slide slide-2">
<div class="banner-content">
<div class="banner-tag" style="color: #005baa; border-color: rgba(0, 91, 170, 0.3);">🛡️ HỖ TRỢ RA QUYẾT ĐỊNH LÂM SÀNG (CDSS)</div>
<div class="banner-title">An Toàn Người Bệnh Là Trên Hết: <span>Cảnh Báo Tương Tác Thuốc DDI</span></div>
<div class="banner-desc">Tự động rà soát tương tác thuốc nguy hiểm, phát hiện chống chỉ định dị ứng theo độ tuổi và bệnh nền, gợi ý chẩn đoán phân biệt và cận lâm sàng theo phác đồ Bộ Y tế.</div>
<div class="banner-pills-row">
<span class="banner-mini-pill">🚨 Cảnh báo 9+ cặp DDI nguy hiểm</span>
<span class="banner-mini-pill">🚫 Kiểm tra dị ứng & độ tuổi</span>
<span class="banner-mini-pill">🔬 Đề xuất xét nghiệm chuẩn</span>
</div>
</div>
<div class="banner-graphic">🧠</div>
</div>

<div class="banner-slide slide-3">
<div class="banner-content">
<div class="banner-tag">📊 PHÂN TÍCH LÂM SÀNG THÔNG MINH</div>
<div class="banner-title">MedScribe AI: <span>Khoa Công Nghệ Thông Tin</span></div>
<div class="banner-desc">Chuyển đổi hội thoại khám bệnh thành hồ sơ điện tử chuẩn SOAP, kết hợp phân tích giọng nói và hỗ trợ quyết định lâm sàng.</div>
<div class="banner-pills-row">
<span class="banner-mini-pill">📊 Đo lường WER / CER</span>
<span class="banner-mini-pill">📄 Mẫu in đơn thuốc A4 chuẩn</span>
<span class="banner-mini-pill">💾 Cơ sở dữ liệu SQLite EMR</span>
</div>
</div>
<div class="banner-graphic">🔬</div>
</div>
</div>
</div>
"""
    render_html_clean(header_html)



def render_stats():
    """Hiển thị 4 thẻ KPI thông số hệ thống."""
    stats = get_stats()
    has_record = bool(st.session_state.get("medical_data"))
    status_text = "Đang xem hồ sơ" if has_record else "Sẵn sàng nhận ca"

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        st.markdown("""
<div class="stat-card teal">
    <div class="stat-icon">🎙️</div>
    <div class="stat-label">Nhận dạng ASR</div>
    <div class="stat-value">Multimodal</div>
</div>""", unsafe_allow_html=True)

    with s2:
        st.markdown(f"""
<div class="stat-card purple">
    <div class="stat-icon">🧠</div>
    <div class="stat-label">CDSS Engine</div>
    <div class="stat-value">{stats['warnings']} cảnh báo</div>
</div>""", unsafe_allow_html=True)

    with s3:
        st.markdown(f"""
<div class="stat-card green">
    <div class="stat-icon">📋</div>
    <div class="stat-label">Tổng hồ sơ bệnh án</div>
    <div class="stat-value">{stats['total']}</div>
</div>""", unsafe_allow_html=True)

    with s4:
        st.markdown(f"""
<div class="stat-card cyan">
    <div class="stat-icon">🩺</div>
    <div class="stat-label">Trạng thái phiên</div>
    <div class="stat-value" style="font-size: 15px; font-weight: 600;">{status_text}</div>
</div>""", unsafe_allow_html=True)

    st.write("")


def render_empty_state():
    """Trạng thái khi chưa có ca khám nào được xử lý."""
    st.markdown("""
<div class="empty-card">
<div>
    <div class="empty-icon">🩺</div>
    <div class="empty-title">Chưa có dữ liệu buổi khám</div>
    <div class="empty-description">
        Chọn một phương thức đầu vào: <b>Ghi âm trực tiếp qua Micro</b>, <b>Tải file âm thanh</b> hoặc 
        chọn <b>Ca lâm sàng mẫu NCKH</b> từ thanh công cụ bên trái để hệ thống tự động bóc tách và phân tích CDSS.
    </div>
    <div class="empty-steps">
        <div class="empty-step">
            <div class="empty-step-icon">🎤</div>
            <div class="empty-step-label">1. Ghi âm / Tải file</div>
        </div>
        <div class="empty-step">
            <div class="empty-step-icon">🎙️</div>
            <div class="empty-step-label">2. Gỡ băng ASR</div>
        </div>
        <div class="empty-step">
            <div class="empty-step-icon">📝</div>
            <div class="empty-step-label">3. Chuẩn hóa SOAP</div>
        </div>
        <div class="empty-step">
            <div class="empty-step-icon">🧠</div>
            <div class="empty-step-label">4. Cảnh báo CDSS</div>
        </div>
    </div>
</div>
</div>
""", unsafe_allow_html=True)


def render_mic_section():
    """Giao diện mô phỏng sóng âm micro khi ghi âm."""
    st.markdown("""
<div class="mic-container" id="micContainer">
    <div class="mic-orb" id="micOrb">
        <div class="mic-ring"></div>
        <div class="mic-ring"></div>
        <div class="mic-ring"></div>
        🎤
    </div>
    <div class="mic-waves">
        <div class="mic-wave-bar"></div>
        <div class="mic-wave-bar"></div>
        <div class="mic-wave-bar"></div>
        <div class="mic-wave-bar"></div>
        <div class="mic-wave-bar"></div>
        <div class="mic-wave-bar"></div>
        <div class="mic-wave-bar"></div>
        <div class="mic-wave-bar"></div>
        <div class="mic-wave-bar"></div>
        <div class="mic-wave-bar"></div>
        <div class="mic-wave-bar"></div>
        <div class="mic-wave-bar"></div>
    </div>
    <div class="mic-label" id="micLabel">Ghi âm hội thoại khám bệnh</div>
    <div class="mic-sublabel">Nhấn nút bên dưới để bắt đầu thu âm</div>
    <div class="mic-status idle" id="micStatus">
        <span>⏸ Chờ ghi âm</span>
    </div>
</div>
""", unsafe_allow_html=True)


def render_mic_js():
    """Tự động phát hiện trạng thái thu âm của nút streamlit_mic_recorder."""
    stc.html("""
<script>
(function() {
    function detectRecording() {
        const micContainer = window.parent.document.getElementById('micContainer');
        if (!micContainer) return;

        const buttons = window.parent.document.querySelectorAll('button');
        let isRecording = false;

        for (const btn of buttons) {
            const text = btn.textContent || btn.innerText || '';
            if (text.includes('Hoàn thành ghi âm') || text.includes('⏹️')) {
                isRecording = true;
                break;
            }
        }

        const micLabel = window.parent.document.getElementById('micLabel');
        const micStatus = window.parent.document.getElementById('micStatus');

        if (isRecording) {
            micContainer.classList.add('recording');
            if (micLabel) micLabel.textContent = 'Đang ghi âm buổi khám...';
            if (micStatus) {
                micStatus.className = 'mic-status active';
                micStatus.innerHTML = '<span class="rec-dot"></span> REC • Đang ghi âm';
            }
        } else {
            micContainer.classList.remove('recording');
            if (micLabel) micLabel.textContent = 'Ghi âm hội thoại khám bệnh';
            if (micStatus) {
                micStatus.className = 'mic-status idle';
                micStatus.innerHTML = '<span>⏸ Chờ ghi âm</span>';
            }
        }
    }

    setInterval(detectRecording, 300);
    setTimeout(detectRecording, 100);
})();
</script>
""", height=0)


def render_transcript_box(transcript_text):
    """Hiển thị bản gỡ băng chi tiết hội thoại ASR giữa Bác sĩ và Bệnh nhân."""
    st.markdown("""
<div class="med-card" style="margin-bottom: 12px;">
    <div class="card-icon">🎙️</div>
    <div class="card-title">Bản gỡ băng hội thoại ASR (Transcript)</div>
    <div class="card-subtitle">Chuyển đổi trực tiếp từ giọng nói sang văn bản kèm phân định người nói</div>
</div>
""", unsafe_allow_html=True)

    if not transcript_text:
        st.info("Chưa có bản ghi hội thoại.")
        return

    lines = transcript_text.strip().split("\n")
    bubble_html = ""
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        if line_clean.lower().startswith("bác sĩ:") or line_clean.lower().startswith("bs:"):
            bubble_html += f'<div class="transcript-bubble transcript-doctor"><b>👨‍⚕️ {safe(line_clean)}</b></div>'
        elif line_clean.lower().startswith("bệnh nhân:") or line_clean.lower().startswith("bn:"):
            bubble_html += f'<div class="transcript-bubble transcript-patient"><b>🧑 {safe(line_clean)}</b></div>'
        else:
            bubble_html += f'<div class="transcript-bubble" style="background: rgba(241,245,249,0.7);">{safe(line_clean)}</div>'

    st.markdown(f'<div class="transcript-container">{bubble_html}</div>', unsafe_allow_html=True)


def render_cdss_panel(cdss_data, clinical_data=None):
    """
    Hiển thị Bảng điều khiển CDSS (Clinical Decision Support System)
    Trực quan, phân loại mức độ rủi ro bằng màu sắc chuẩn y khoa.
    """
    st.markdown("""
<div class="med-card" style="margin-bottom: 12px;">
    <div class="card-icon">🧠</div>
    <div class="card-title">Hỗ Trợ Ra Quyết Định Lâm Sàng (CDSS Engine)</div>
    <div class="card-subtitle">Phân tích tương tác thuốc DDI &bull; Chống chỉ định &bull; Chẩn đoán phân biệt &bull; Phác đồ chuẩn</div>
</div>
""", unsafe_allow_html=True)

    if not cdss_data:
        st.info("Chưa có dữ liệu phân tích lâm sàng.")
        return

    verdict = cdss_data.get("safety_verdict", "SAFE").upper()
    drug_interactions = cdss_data.get("drug_interactions", [])
    contraindications = cdss_data.get("contraindications", [])
    differentials = cdss_data.get("differential_suggestions", [])
    recommended_tests = cdss_data.get("recommended_tests", [])
    guidelines_summary = cdss_data.get("clinical_guidelines_summary", "")

    # ── 1. Banner Mức độ an toàn tổng quan ──
    if verdict == "DANGER" or drug_interactions or contraindications:
        if any(d.get("severity") == "DANGER" for d in drug_interactions) or contraindications:
            st.markdown("""
<div class="cdss-alert-box cdss-alert-danger">
    <div class="cdss-icon">🚨</div>
    <div>
        <div class="cdss-title">CẢNH BÁO NGUY CƠ CAO (HIGH RISK DETECTED)</div>
        <div class="cdss-desc">Phát hiện tương tác thuốc nghiêm trọng hoặc chống chỉ định y khoa. Bác sĩ cần rà soát và điều chỉnh đơn thuốc trước khi duyệt.</div>
    </div>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown("""
<div class="cdss-alert-box cdss-alert-warning">
    <div class="cdss-icon">⚠️</div>
    <div>
        <div class="cdss-title">CẦN LƯU Ý THEO DÕI (MODERATE WARNING)</div>
        <div class="cdss-desc">Có tương tác thuốc cần theo dõi lâm sàng hoặc kiểm tra chức năng thận/điện giải.</div>
    </div>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div class="cdss-alert-box cdss-alert-safe">
    <div class="cdss-icon">✅</div>
    <div>
        <div class="cdss-title">ĐƠN THUỐC ĐẠT CHUẨN AN TOÀN (ALL CLEAR)</div>
        <div class="cdss-desc">Không phát hiện tương tác thuốc bất lợi đối kháng hoặc chống chỉ định nghiêm trọng theo dữ liệu hiện hành.</div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ── 2. Chi tiết Tương tác thuốc (DDI) ──
    if drug_interactions:
        st.markdown("##### 💊 Cảnh báo Tương tác thuốc (Drug-Drug Interactions)")
        for idx, item in enumerate(drug_interactions, start=1):
            sev = item.get("severity", "WARNING").upper()
            css_class = "danger" if sev == "DANGER" else "warning"
            badge_color = "#ef4444" if sev == "DANGER" else "#f59e0b"
            drugs_str = " + ".join(item.get("drugs", []))
            st.markdown(f"""
<div class="cdss-item-card {css_class}">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <span style="font-weight: 700; font-size: 14.5px; color: #0f172a;">{idx}. {safe(item.get('title', 'Tương tác thuốc'))}</span>
        <span style="background: {badge_color}; color: white; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 700;">{sev}</span>
    </div>
    <div style="font-size: 13px; color: #475569; margin-bottom: 4px;"><b>Cặp thuốc liên quan:</b> <code style="color: #b91c1c;">{safe(drugs_str)}</code></div>
    <div style="font-size: 13px; color: #334155; margin-bottom: 4px;"><b>Cơ chế:</b> {safe(item.get('mechanism', ''))}</div>
    <div style="font-size: 13px; color: #b91c1c; margin-bottom: 4px;"><b>Nguy cơ:</b> {safe(item.get('risk', ''))}</div>
    <div style="font-size: 13px; color: #047857; background: rgba(16,185,129,0.08); padding: 6px 10px; border-radius: 6px;"><b>Khuyến nghị CDSS:</b> {safe(item.get('recommendation', ''))}</div>
</div>
""", unsafe_allow_html=True)

    # ── 3. Chống chỉ định & Dị ứng ──
    if contraindications:
        st.markdown("##### 🚫 Chống chỉ định & Cảnh báo Dị ứng")
        for idx, item in enumerate(contraindications, start=1):
            st.markdown(f"""
<div class="cdss-item-card danger">
    <div style="font-weight: 700; color: #b91c1c; font-size: 14px; margin-bottom: 4px;">{idx}. {safe(item.get('alert', ''))}</div>
    <div style="font-size: 13px; color: #475569; margin-bottom: 4px;"><b>Nguy cơ:</b> {safe(item.get('risk', ''))}</div>
    <div style="font-size: 13px; color: #047857; background: rgba(16,185,129,0.08); padding: 6px 10px; border-radius: 6px;"><b>Hướng xử trí:</b> {safe(item.get('recommendation', ''))}</div>
</div>
""", unsafe_allow_html=True)

    # ── 4. Gợi ý Chẩn đoán phân biệt & Cận lâm sàng ──
    col_d, col_t = st.columns(2)
    with col_d:
        st.markdown("##### 🔎 Gợi ý Chẩn đoán phân biệt")
        if differentials:
            for d in differentials:
                prob = d.get("probability", "Trung bình")
                prob_color = "#ef4444" if "cao" in prob.lower() or "khẩn" in prob.lower() else "#3b82f6"
                st.markdown(f"""
<div style="background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 14px; margin-bottom: 8px;">
    <div style="display: flex; justify-content: space-between;">
        <b>{safe(d.get('condition', ''))}</b>
        <span style="color: {prob_color}; font-weight: 600; font-size: 12px;">{safe(prob)}</span>
    </div>
    <div style="font-size: 12.5px; color: #64748b; margin-top: 3px;">{safe(d.get('rationale', ''))}</div>
</div>
""", unsafe_allow_html=True)
        else:
            st.caption("Chưa có gợi ý chẩn đoán phân biệt.")

    with col_t:
        st.markdown("##### 🧪 Đề xuất Cận lâm sàng cần làm")
        if recommended_tests:
            for t in recommended_tests:
                st.markdown(f"""
<div style="background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 14px; margin-bottom: 8px;">
    <div style="font-weight: 600; color: #0d9488;">🔬 {safe(t.get('test', ''))}</div>
    <div style="font-size: 12.5px; color: #64748b; margin-top: 2px;">{safe(t.get('purpose', ''))}</div>
</div>
""", unsafe_allow_html=True)
        else:
            st.caption("Chưa có đề xuất cận lâm sàng.")

    # ── 5. Tóm tắt Hướng dẫn Phác đồ Y tế ──
    if guidelines_summary:
        st.markdown(f"""
<div style="background: rgba(241,245,249,0.8); border-left: 4px solid #0d9488; border-radius: 8px; padding: 10px 14px; margin-top: 10px; font-size: 13px; color: #334155;">
    <b>📚 Căn cứ Phác đồ & Y học Bằng chứng:</b> {safe(guidelines_summary)}
</div>
""", unsafe_allow_html=True)


def render_soap_editor(data):
    """Giao diện biên tập hồ sơ bệnh án chuẩn SOAP."""
    st.markdown("""
<div class="med-card" style="margin-bottom: 12px;">
    <div class="card-icon">📋</div>
    <div class="card-title">Hồ Sơ Bệnh Án Điện Tử Chuẩn SOAP</div>
    <div class="card-subtitle">Chỉnh sửa và bổ sung thông tin trước khi lưu trữ vào CSDL</div>
</div>
""", unsafe_allow_html=True)

    patient = data.get("patient", {})
    soap = data.get("soap", {})
    subj = soap.get("subjective", {})
    obj = soap.get("objective", {})
    vital = obj.get("vital_signs", {})
    ass = soap.get("assessment", {})
    plan = soap.get("plan", {})

    # ── 1. Thông tin Hành chính ──
    with st.expander("👤 THÔNG TIN HÀNH CHÍNH BỆNH NHÂN", expanded=True):
        p1, p2, p3 = st.columns([1.5, 1, 1])
        with p1:
            name = st.text_input("Họ và tên", patient.get("name", ""), key="pat_name")
            address = st.text_input("Địa chỉ", patient.get("address", ""), key="pat_addr")
        with p2:
            age = st.text_input("Tuổi", patient.get("age", ""), key="pat_age")
            phone = st.text_input("Điện thoại", patient.get("phone", ""), key="pat_phone")
        with p3:
            gender = st.selectbox(
                "Giới tính",
                ["Nam", "Nữ", "Khác"],
                index=0 if patient.get("gender") == "Nam" else (1 if patient.get("gender") == "Nữ" else 2),
                key="pat_gender"
            )

    # ── 2. S - Subjective (Chủ quan) ──
    with st.expander("📝 S - SUBJECTIVE (Lý do khám & Tiền sử)", expanded=True):
        chief_complaint = st.text_input(
            "Lý do đến khám (Chief Complaint)",
            subj.get("chief_complaint", ""),
            key="soap_cc"
        )
        s1, s2 = st.columns(2)
        with s1:
            history_of_illness = st.text_area(
                "Bệnh sử hiện tại (History of Present Illness)",
                subj.get("history_of_illness", ""),
                height=80,
                key="soap_hpi"
            )
        with s2:
            medical_history = st.text_area(
                "Tiền sử bệnh nền (Past Medical History)",
                subj.get("medical_history", ""),
                height=80,
                key="soap_pmh"
            )
        allergies = st.text_input(
            "Tiền sử dị ứng thuốc & thức ăn",
            subj.get("allergies", "Không ghi nhận"),
            key="soap_alg"
        )

    # ── 3. O - Objective (Khách quan & Thăm khám) ──
    with st.expander("🩺 O - OBJECTIVE (Dấu hiệu sinh tồn & Khám thực thể)", expanded=True):
        v1, v2, v3, v4, v5 = st.columns(5)
        with v1:
            bp = st.text_input("Huyết áp", vital.get("blood_pressure", "120/80 mmHg"), key="vital_bp")
        with v2:
            hr = st.text_input("Mạch / Tim", vital.get("heart_rate", "75 bpm"), key="vital_hr")
        with v3:
            temp = st.text_input("Nhiệt độ", vital.get("temperature", "37.0 °C"), key="vital_temp")
        with v4:
            spo2 = st.text_input("SpO2", vital.get("spo2", "98%"), key="vital_spo2")
        with v5:
            rr = st.text_input("Nhịp thở", vital.get("respiratory_rate", "18 lần/p"), key="vital_rr")

        physical_exam = st.text_area(
            "Kết quả thăm khám thực thể",
            obj.get("physical_exam", ""),
            height=80,
            key="soap_pe"
        )

    # ── 4. A - Assessment (Đánh giá & Chẩn đoán) ──
    with st.expander("🧠 A - ASSESSMENT (Chẩn đoán & Mã ICD-10)", expanded=True):
        a1, a2 = st.columns([2, 1])
        with a1:
            primary_diag = st.text_input(
                "Chẩn đoán xác định chính",
                ass.get("primary_diagnosis", ""),
                key="soap_diag"
            )
        with a2:
            icd10 = st.text_input(
                "Mã ICD-10",
                ass.get("icd10", ""),
                key="soap_icd"
            )
        diff_diag = st.text_input(
            "Chẩn đoán phân biệt",
            ass.get("differential_diagnosis", ""),
            key="soap_diff"
        )

    # ── 5. P - Plan (Kế hoạch điều trị & Đơn thuốc) ──
    updated_rx = []
    with st.expander("💊 P - PLAN (Kế hoạch điều trị & Đơn thuốc)", expanded=True):
        st.markdown("**Đơn thuốc kê chi tiết:**")
        rx_list = plan.get("prescription", data.get("prescription", []))

        # Thêm nút thêm thuốc mới
        if rx_list:
            for idx, med in enumerate(rx_list):
                c1, c2, c3, c4 = st.columns([1.5, 0.8, 0.8, 1.2])
                with c1:
                    m_name = st.text_input(f"Tên thuốc #{idx+1}", med.get("name", ""), key=f"rx_name_{idx}")
                with c2:
                    m_dose = st.text_input(f"Liều #{idx+1}", med.get("dosage", ""), key=f"rx_dose_{idx}")
                with c3:
                    m_qty = st.text_input(f"Số lượng #{idx+1}", med.get("quantity", ""), key=f"rx_qty_{idx}")
                with c4:
                    m_ins = st.text_input(f"Cách dùng #{idx+1}", med.get("instruction", ""), key=f"rx_ins_{idx}")

                if m_name.strip():
                    updated_rx.append({
                        "name": m_name,
                        "dosage": m_dose,
                        "quantity": m_qty,
                        "instruction": m_ins
                    })
        else:
            st.info("Chưa có thuốc trong đơn. Bác sĩ có thể nhập thuốc bổ sung bên dưới:")
            c1, c2, c3, c4 = st.columns([1.5, 0.8, 0.8, 1.2])
            with c1:
                m_name = st.text_input("Tên thuốc", "", key="new_rx_name")
            with c2:
                m_dose = st.text_input("Liều dùng", "", key="new_rx_dose")
            with c3:
                m_qty = st.text_input("Số lượng", "", key="new_rx_qty")
            with c4:
                m_ins = st.text_input("Cách dùng", "", key="new_rx_ins")
            if m_name.strip():
                updated_rx.append({
                    "name": m_name, "dosage": m_dose, "quantity": m_qty, "instruction": m_ins
                })

        st.markdown("<br>", unsafe_allow_html=True)
        lab_tests = st.text_area("Chỉ định Cận lâm sàng (Lab / Chẩn đoán hình ảnh)", plan.get("lab_tests", ""), height=65, key="soap_labs")
        p_advice, p_fu = st.columns(2)
        with p_advice:
            advice = st.text_area("Lời dặn bệnh nhân", plan.get("advice", data.get("advice", "")), height=70, key="soap_adv")
        with p_fu:
            follow_up = st.text_area("Hẹn tái khám", plan.get("follow_up", ""), height=70, key="soap_fu")

    # Trả về đối tượng dữ liệu hoàn chỉnh
    return {
        "raw_transcript": data.get("raw_transcript", ""),
        "patient": {
            "name": name,
            "age": age,
            "gender": gender,
            "address": address,
            "phone": phone
        },
        "soap": {
            "subjective": {
                "chief_complaint": chief_complaint,
                "history_of_illness": history_of_illness,
                "medical_history": medical_history,
                "allergies": allergies
            },
            "objective": {
                "vital_signs": {
                    "blood_pressure": bp,
                    "heart_rate": hr,
                    "temperature": temp,
                    "spo2": spo2,
                    "respiratory_rate": rr
                },
                "physical_exam": physical_exam
            },
            "assessment": {
                "primary_diagnosis": primary_diag,
                "icd10": icd10,
                "differential_diagnosis": diff_diag
            },
            "plan": {
                "prescription": updated_rx,
                "lab_tests": lab_tests,
                "advice": advice,
                "follow_up": follow_up
            }
        },
        "cdss": data.get("cdss", {}),
        "doctor": st.session_state.get("doctor_name", "")
    }


def prescription_html(data):
    """Tạo mẫu đơn thuốc in ấn khổ giấy A4 chuẩn Bộ Y tế."""
    patient = data.get("patient", {})
    soap = data.get("soap", {})
    subj = soap.get("subjective", {})
    ass = soap.get("assessment", {})
    plan = soap.get("plan", {})
    medicines = plan.get("prescription", data.get("prescription", []))
    cdss = data.get("cdss", {})

    code = str(int(time.time()))[-8:]
    date_now = time.strftime("%d/%m/%Y")

    medicine_html = ""
    if medicines:
        for idx, med in enumerate(medicines, start=1):
            name = safe(med.get("name", ""))
            dosage = safe(med.get("dosage", ""))
            quantity = safe(med.get("quantity", ""))
            instruction = safe(med.get("instruction", ""))
            medicine_html += f"""
<div class="rx-drug">
<b>{idx}. {name}</b> &nbsp;&nbsp;&bull;&nbsp;&nbsp; <i>Số lượng: {quantity}</i><br>
Liều dùng: {dosage}<br>
Cách dùng: {instruction}
</div>"""
    else:
        medicine_html = '<div class="rx-line">Không kê đơn thuốc tân dược.</div>'

    labs_html = ""
    if plan.get("lab_tests"):
        labs_html = f"""
<div class="rx-section">
<div class="rx-section-title">CHỈ ĐỊNH CẬN LÂM SÀNG</div>
<div class="rx-body"><div class="rx-line">{safe(plan.get("lab_tests"))}</div></div>
</div>"""

    # Huy hiệu xác nhận an toàn CDSS
    safety_verdict = cdss.get("safety_verdict", "SAFE")
    cdss_stamp = (
        '<span style="color: #059669; font-weight: 600;">[✓] ĐÃ KIỂM TRA TƯƠNG TÁC THUỐC CDSS: AN TOÀN</span>'
        if safety_verdict == "SAFE" else
        '<span style="color: #dc2626; font-weight: 600;">[!] CẢNH BÁO CDSS: CẦN THẬN TRỌNG PHỐI HỢP THUỐC</span>'
    )

    return f"""
<div class="prescription-container">
<div class="prescription-paper">

<div class="rx-top">
<div class="rx-hospital">
<b>{safe(st.session_state.get('clinic_name', ''))}</b><br>
Địa chỉ: {safe(st.session_state.get('clinic_addr', ''))}<br>
Hotline: {safe(st.session_state.get('clinic_phone', ''))}
</div>
<div class="rx-code"><b>MÃ BỆNH ÁN</b><br>MS-{code}</div>
</div>

<div class="rx-title">ĐƠN THUỐC & BỆNH ÁN NGOẠI TRÚ</div>

<div class="rx-info">
<b>Bác sĩ điều trị:</b> {safe(st.session_state.get('doctor_name', ''))}<br>
<b>Ngày khám:</b> {date_now}<br>
<b>Bệnh nhân:</b> {safe(patient.get("name", ""))}<br>
<b>Tuổi:</b> {safe(patient.get("age", ""))} &nbsp;&nbsp;&bull;&nbsp;&nbsp; <b>Giới tính:</b> {safe(patient.get("gender", ""))}<br>
<b>Địa chỉ:</b> {safe(patient.get("address", ""))}<br>
<b>Tiền sử dị ứng:</b> {safe(subj.get("allergies", "Không ghi nhận"))}
</div>

<div class="rx-section">
<div class="rx-section-title">CHẨN ĐOÁN LÂM SÀNG</div>
<div class="rx-body">
<div class="rx-line"><b>Chẩn đoán xác định:</b> {safe(ass.get("primary_diagnosis", ""))} {f'(Mã ICD-10: {safe(ass.get("icd10"))})' if ass.get("icd10") else ''}</div>
{f'<div class="rx-line"><b>Chẩn đoán phân biệt:</b> {safe(ass.get("differential_diagnosis"))}</div>' if ass.get("differential_diagnosis") else ''}
</div>
</div>

{labs_html}

<div class="rx-section">
<div class="rx-section-title">CHỈ ĐỊNH DÙNG THUỐC</div>
<div class="rx-body">{medicine_html}</div>
</div>

<div class="rx-section">
<div class="rx-section-title">LỜI DẶN BÁC SĨ</div>
<div class="rx-body">
<div class="rx-line">{safe(plan.get("advice", data.get("advice", "")))}</div>
{f'<div class="rx-line"><b>Hẹn tái khám:</b> {safe(plan.get("follow_up"))}</div>' if plan.get("follow_up") else ''}
</div>
</div>

<div class="rx-signatures">
<div>
<div class="rx-sign-title">BỆNH NHÂN / THÂN NHÂN</div>
<div class="rx-sign-space"></div>
<i>(Ký và ghi rõ họ tên)</i>
</div>
<div>
<div class="rx-sign-title">BÁC SĨ ĐIỀU TRỊ</div>
<div class="rx-sign-space"></div>
<b>{safe(st.session_state.get('doctor_name', ''))}</b><br>
<i>(Ký và đóng dấu)</i>
</div>
</div>

<div class="rx-note">
{cdss_stamp}<br>
MedScribe AI.
</div>

</div>
</div>
"""


def render_footer():
    st.markdown("""
<div class="footer-container"><div class="footer-divider"></div>
<div class="footer-text">MedScribe AI &bull; Hệ thống bệnh án điện tử từ giọng nói kết hợp hỗ trợ quyết định lâm sàng<br>© 2026 MedScribe AI</div>
</div>
""", unsafe_allow_html=True)
