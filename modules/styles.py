def get_css():
    return """
<style>

/* ==========================================================
   GOOGLE FONTS IMPORT
========================================================== */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');


/* ==========================================================
   CSS VARIABLES — MEDLATEC BRIGHT MEDICAL THEME
========================================================== */
:root {
    /* Nền sáng chuẩn bệnh viện cao cấp (MEDLATEC Style) */
    --bg-primary: #ffffff;
    --bg-secondary: #f8fafc;
    --bg-tertiary: #f1f5f9;
    --bg-card: #ffffff;
    --bg-card-hover: #ffffff;
    --bg-sidebar: #ffffff;
    --bg-input: #ffffff;
    --bg-app: #f4f8fc;
    --bg-glass: rgba(255, 255, 255, 0.95);

    /* Màu sắc thương hiệu Y tế Medlatec (Xanh Dương Hoàng Gia & Xanh Lá Y Tế) */
    --med-blue: #005baa;
    --med-blue-dark: #004280;
    --med-blue-light: #e6f0fa;
    --med-cyan: #0088cc;
    --med-green: #00a651;
    --med-green-light: #e6f7ee;
    --med-red: #dc2626;
    --med-red-light: #fef2f2;
    --med-amber: #f59e0b;
    --med-amber-light: #fffbeb;

    /* Màu chữ sắc nét trên nền sáng */
    --text-primary: #0f172a;
    --text-secondary: #334155;
    --text-tertiary: #64748b;
    --text-sidebar: #0f172a;
    --text-sidebar-muted: #64748b;

    /* Viền & Đổ bóng hiện đại */
    --border-primary: #e2e8f0;
    --border-accent: rgba(0, 91, 170, 0.2);
    --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03);
    --shadow-md: 0 4px 14px rgba(0, 91, 170, 0.06), 0 2px 4px rgba(0, 0, 0, 0.03);
    --shadow-lg: 0 10px 25px rgba(0, 91, 170, 0.08), 0 4px 10px rgba(0, 0, 0, 0.04);

    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-full: 9999px;
}


/* ==========================================================
   GLOBAL APP STYLING (NỀN SÁNG, CHUẨN Y TẾ)
========================================================== */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif !important;
    background-color: var(--bg-app) !important;
    color: var(--text-primary) !important;
}

[data-testid="stAppViewBlockContainer"] {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1350px !important;
}

/* Sidebar sáng chuẩn bệnh viện */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
    box-shadow: 2px 0 12px rgba(0, 91, 170, 0.04) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

/* Ép toàn bộ ô nhập liệu & hộp chọn selectbox sáng màu rõ nét */
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] div[data-baseweb="select"],
[data-testid="stSidebar"] div[data-baseweb="select"] *,
[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background-color: #f8fafc !important;
    border-color: #cbd5e1 !important;
    color: #0f172a !important;
    border-radius: 8px !important;
}

[data-testid="stSidebar"] div[data-baseweb="popover"],
[data-testid="stSidebar"] ul[data-baseweb="menu"],
[data-testid="stSidebar"] ul[data-baseweb="menu"] * {
    background-color: #ffffff !important;
    color: #0f172a !important;
}

[data-testid="stSidebar"] .stCaption {
    color: #64748b !important;
}


/* ==========================================================
   TOPBAR MEDLATEC STYLE
========================================================== */
.medlatec-topbar {
    background: #ffffff;
    border-radius: 16px;
    padding: 14px 24px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: var(--shadow-md);
    border: 1px solid var(--border-primary);
}

.medlatec-logo-wrap {
    display: flex;
    align-items: center;
    gap: 16px;
}

.medlatec-logo-img {
    height: 70px;
    max-width: 250px;
    object-fit: contain;
    border-radius: 6px;
}

.medlatec-brand-title {
    font-size: 20px;
    font-weight: 800;
    color: var(--med-blue);
    letter-spacing: -0.5px;
    line-height: 1.2;
}

.medlatec-brand-sub {
    font-size: 11.5px;
    font-weight: 600;
    color: var(--med-green);
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.medlatec-menu-pills {
    display: flex;
    align-items: center;
    gap: 20px;
}

.medlatec-menu-item {
    font-size: 13.5px;
    font-weight: 600;
    color: #475569;
    text-decoration: none;
    transition: color 0.2s;
    cursor: pointer;
}

.medlatec-menu-item:hover, .medlatec-menu-item.active {
    color: var(--med-blue);
}

.medlatec-contact-pill {
    display: flex;
    align-items: center;
    gap: 12px;
    background: linear-gradient(135deg, #e6f0fa, #f0fdf4);
    border: 1px solid rgba(0, 91, 170, 0.15);
    padding: 8px 16px;
    border-radius: 999px;
}

.medlatec-hotline-icon {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--med-blue);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
}

.medlatec-hotline-num {
    font-size: 15px;
    font-weight: 800;
    color: var(--med-blue);
    line-height: 1.1;
}

.medlatec-hotline-label {
    font-size: 11px;
    color: #64748b;
    font-weight: 500;
}


/* ==========================================================
   CAROUSEL / BANNER SLIDER (TRƯỢT TỪ TRÁI SANG PHẢI)
========================================================== */
.banner-slider-container {
    position: relative;
    width: 100%;
    height: 270px;
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 24px;
    box-shadow: 0 8px 30px rgba(0, 91, 170, 0.1);
    border: 1px solid rgba(0, 91, 170, 0.12);
    background: #ffffff;
}

.banner-track {
    display: flex;
    width: 300%;
    height: 100%;
    animation: medlatecSlide 15s infinite ease-in-out;
}

.banner-track:hover {
    animation-play-state: paused;
}

.banner-slide {
    width: 33.333%;
    height: 100%;
    padding: 36px 48px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
    box-sizing: border-box;
}

/* Slide 1 Theme: Medlatec Mint & Cyan */
.slide-1 {
    background: linear-gradient(135deg, #e0f7f4 0%, #dcfce7 50%, #e0f2fe 100%);
}

/* Slide 2 Theme: Clinical Blue & Magenta */
.slide-2 {
    background: linear-gradient(135deg, #e6f0fa 0%, #ede9fe 50%, #fce7f3 100%);
}

/* Slide 3 Theme: NCKH Gold & Blue */
.slide-3 {
    background: linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 50%, #fef3c7 100%);
}

.banner-content {
    max-width: 65%;
    z-index: 2;
}

.banner-tag {
    display: inline-block;
    padding: 5px 14px;
    background: #ffffff;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    color: var(--med-blue);
    margin-bottom: 12px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
    border: 1px solid rgba(0, 91, 170, 0.15);
}

.banner-title {
    font-size: 26px;
    font-weight: 800;
    color: #0c4a6e;
    margin-bottom: 8px;
    line-height: 1.25;
}

.banner-title span {
    color: var(--med-blue);
}

.banner-desc {
    font-size: 14px;
    color: #334155;
    line-height: 1.5;
    margin-bottom: 16px;
}

.banner-pills-row {
    display: flex;
    align-items: center;
    gap: 12px;
}

.banner-mini-pill {
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(0, 91, 170, 0.15);
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 12.5px;
    font-weight: 600;
    color: #0f172a;
}

.banner-graphic {
    font-size: 100px;
    line-height: 1;
    z-index: 2;
    filter: drop-shadow(0 10px 15px rgba(0, 91, 170, 0.15));
    animation: floatAnim 3.5s ease-in-out infinite;
}

/* Keyframes cho hiệu ứng trượt tự động mượt mà từ trái sang phải */
@keyframes medlatecSlide {
    0%, 28% {
        transform: translateX(0%);
    }
    33%, 61% {
        transform: translateX(-33.333%);
    }
    66%, 95% {
        transform: translateX(-66.666%);
    }
    100% {
        transform: translateX(0%);
    }
}

@keyframes floatAnim {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
}


/* ==========================================================
   CARDS & CONTAINERS — GIAO DIỆN SÁNG CHUẨN Y KHOA
========================================================== */
.med-card {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 16px !important;
    padding: 20px 24px !important;
    margin-bottom: 18px !important;
    box-shadow: var(--shadow-sm) !important;
    transition: all 0.25s ease !important;
}

.med-card:hover {
    box-shadow: var(--shadow-md) !important;
    border-color: rgba(0, 91, 170, 0.25) !important;
}

.card-title {
    font-size: 17px !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    margin-top: 4px !important;
}

.card-subtitle {
    font-size: 13px !important;
    color: #64748b !important;
    margin-top: 2px !important;
}

.card-icon {
    font-size: 24px !important;
}


/* ==========================================================
   KPI STAT CARDS (SÁNG SỦA, TINH TẾ)
========================================================== */
.stat-card {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 14px !important;
    padding: 16px 18px !important;
    box-shadow: var(--shadow-sm) !important;
    transition: all 0.2s ease !important;
    border-top: 4px solid var(--med-blue) !important;
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md) !important;
}

.stat-card.teal { border-top-color: #00a651 !important; }
.stat-card.purple { border-top-color: #005baa !important; }
.stat-card.green { border-top-color: #0891b2 !important; }
.stat-card.cyan { border-top-color: #f59e0b !important; }

.stat-icon {
    font-size: 20px !important;
    margin-bottom: 6px !important;
}

.stat-label {
    font-size: 12.5px !important;
    color: #64748b !important;
    font-weight: 600 !important;
}

.stat-value {
    font-size: 20px !important;
    font-weight: 800 !important;
    color: #0f172a !important;
}


/* ==========================================================
   TABS STYLING (MEDLATEC BLUE ACCENT)
========================================================== */
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff !important;
    border-radius: 12px !important;
    padding: 6px !important;
    gap: 8px !important;
    box-shadow: var(--shadow-sm) !important;
    border: 1px solid #e2e8f0 !important;
    margin-bottom: 20px !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 10px 18px !important;
    font-weight: 600 !important;
    color: #475569 !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
}

.stTabs [aria-selected="true"] {
    background: var(--med-blue) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(0, 91, 170, 0.25) !important;
}


/* ==========================================================
   PRIMARY BUTTONS (MEDLATEC BLUE GRADIENT)
========================================================== */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #005baa 0%, #0072bc 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    padding: 12px 24px !important;
    box-shadow: 0 4px 14px rgba(0, 91, 170, 0.25) !important;
    transition: all 0.2s ease !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #004887 0%, #005baa 100%) !important;
    box-shadow: 0 6px 18px rgba(0, 91, 170, 0.35) !important;
    transform: translateY(-1px) !important;
}

.stButton > button[kind="secondary"] {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    color: #334155 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}


/* ==========================================================
   CDSS ALERTS (RÕ RÀNG, CHUẨN Y TẾ)
========================================================== */
.cdss-alert-box {
    border-radius: 14px;
    padding: 16px 20px;
    margin: 12px 0 18px 0;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: var(--shadow-sm);
    border: 1px solid;
}

.cdss-alert-danger {
    background: #fef2f2;
    border-color: #f87171;
    color: #991b1b;
}

.cdss-alert-warning {
    background: #fffbeb;
    border-color: #fbbf24;
    color: #92400e;
}

.cdss-alert-safe {
    background: #f0fdf4;
    border-color: #34d399;
    color: #065f46;
}

.cdss-item-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-left: 5px solid #dc2626;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 12px;
    box-shadow: var(--shadow-sm);
}

.cdss-item-card.warning {
    border-left-color: #f59e0b;
}

.cdss-item-card.safe {
    border-left-color: #00a651;
}


/* ==========================================================
   TRANSCRIPT CONTAINER (HỘI THOẠI ASR)
========================================================== */
.transcript-container {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 16px 20px;
    max-height: 280px;
    overflow-y: auto;
    font-size: 13.5px;
    line-height: 1.6;
    margin-bottom: 16px;
}

.transcript-bubble {
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 8px;
    background: #ffffff;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

.transcript-doctor {
    background: #e6f0fa;
    border-left: 3px solid var(--med-blue);
}

.transcript-patient {
    background: #f0fdf4;
    border-left: 3px solid var(--med-green);
}


/* ==========================================================
   MIC SECTION (SÁNG VÀ HIỆN ĐẠI)
========================================================== */
.mic-container {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 24px 16px;
    text-align: center;
    box-shadow: var(--shadow-sm);
    margin-bottom: 16px;
}

.mic-orb {
    width: 68px;
    height: 68px;
    border-radius: 50%;
    background: linear-gradient(135deg, #005baa, #00a651);
    color: white;
    font-size: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 12px auto;
    box-shadow: 0 8px 20px rgba(0, 91, 170, 0.25);
}

.mic-label {
    font-size: 15px;
    font-weight: 700;
    color: #0f172a;
}

.mic-sublabel {
    font-size: 12.5px;
    color: #64748b;
    margin-top: 2px;
}


/* ==========================================================
   PRESCRIPTION PREVIEW (BẢN IN ĐƠN THUỐC A4)
========================================================== */
.prescription-container {
    background: #f1f5f9;
    padding: 24px;
    border-radius: 16px;
    display: flex;
    justify-content: center;
}

.prescription-paper {
    background: #ffffff;
    width: 100%;
    max-width: 800px;
    min-height: 980px;
    padding: 40px 48px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    border: 1px solid #cbd5e1;
    font-family: 'Times New Roman', Times, serif;
    color: #111111;
}

.rx-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 2px solid #005baa;
    padding-bottom: 12px;
    margin-bottom: 16px;
}

.rx-hospital {
    font-size: 14px;
    line-height: 1.4;
    color: #005baa;
}

.rx-code {
    text-align: right;
    font-size: 13px;
    color: #475569;
}

.rx-title {
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    color: #005baa;
    margin: 16px 0;
    letter-spacing: 1px;
}

.rx-info {
    font-size: 14px;
    line-height: 1.7;
    margin-bottom: 16px;
    background: #f8fafc;
    padding: 12px 16px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
}

.rx-section {
    margin-bottom: 16px;
}

.rx-section-title {
    font-size: 13.5px;
    font-weight: bold;
    color: #005baa;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 4px;
    margin-bottom: 8px;
    text-transform: uppercase;
}

.rx-drug {
    font-size: 14px;
    line-height: 1.5;
    margin-bottom: 10px;
    padding-left: 8px;
    border-left: 2px solid #005baa;
}

.rx-signatures {
    display: flex;
    justify-content: space-between;
    margin-top: 40px;
    text-align: center;
}

.rx-sign-space {
    height: 70px;
}

.rx-note {
    font-size: 11.5px;
    color: #64748b;
    text-align: center;
    margin-top: 30px;
    border-top: 1px dashed #cbd5e1;
    padding-top: 10px;
    font-style: italic;
}


/* ==========================================================
   FOOTER (MEDLATEC CLEAN STYLE)
========================================================== */
.footer-container {
    margin-top: 40px;
    padding: 24px 0 16px 0;
    border-top: 1px solid #e2e8f0;
    text-align: center;
    font-size: 13px;
    color: #64748b;
    line-height: 1.6;
}

.footer-container b {
    color: var(--med-blue);
}

@media print {
    body * { visibility: hidden; }
    .prescription-paper, .prescription-paper * { visibility: visible; }
    .prescription-paper {
        position: absolute;
        left: 0;
        top: 0;
        width: 100% !important;
        box-shadow: none !important;
        border: none !important;
    }
}


/* ==========================================================
   BỔ SUNG: CÁC CLASS CÒN THIẾU (trước đây chưa có CSS)
========================================================== */
html, body { overflow-x: hidden; }
img { max-width: 100%; }

.metric-box {
    background: #ffffff; border: 1px solid var(--border-primary); border-radius: 14px;
    padding: 16px 12px; text-align: center; box-shadow: var(--shadow-sm); height: 100%;
}
.metric-val { font-size: 28px; font-weight: 800; line-height: 1.2; }
.metric-label { font-size: 12.5px; color: var(--text-tertiary); font-weight: 600; margin-top: 4px; }

.empty-card {
    background: #ffffff; border: 1px dashed #cbd5e1; border-radius: 16px;
    padding: 36px 24px; text-align: center; min-height: 340px;
    display: flex; align-items: center; justify-content: center;
}
.empty-icon { font-size: 48px; margin-bottom: 8px; }
.empty-title { font-size: 18px; font-weight: 700; color: var(--text-primary); }
.empty-description { font-size: 14px; color: #475569; line-height: 1.6; max-width: 520px; margin: 8px auto 20px; }
.empty-steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.empty-step { background: var(--bg-secondary); border: 1px solid var(--border-primary); border-radius: 12px; padding: 12px 8px; }
.empty-step-icon { font-size: 22px; }
.empty-step-label { font-size: 12px; font-weight: 600; color: #334155; margin-top: 4px; }

.mic-orb { position: relative; }
.mic-ring { position: absolute; inset: 0; border-radius: 50%; border: 2px solid rgba(0, 91, 170, 0.35); opacity: 0; }
.mic-container.recording .mic-ring { animation: micPulse 1.8s ease-out infinite; }
.mic-container.recording .mic-ring:nth-child(2) { animation-delay: 0.6s; }
.mic-container.recording .mic-ring:nth-child(3) { animation-delay: 1.2s; }
.mic-waves { display: flex; justify-content: center; align-items: center; gap: 4px; height: 32px; margin: 6px 0 10px; }
.mic-wave-bar { width: 4px; height: 6px; border-radius: 2px; background: #cbd5e1; }
.mic-container.recording .mic-wave-bar { background: var(--med-blue); animation: micWave 1s ease-in-out infinite; }
.mic-container.recording .mic-wave-bar:nth-child(odd) { animation-delay: 0.25s; }
.mic-container.recording .mic-wave-bar:nth-child(3n) { animation-delay: 0.5s; }
.mic-status { display: inline-flex; align-items: center; gap: 6px; margin-top: 10px; padding: 5px 14px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.mic-status.idle { background: #f1f5f9; color: #64748b; }
.mic-status.active { background: #fef2f2; color: #dc2626; }
.rec-dot { width: 8px; height: 8px; border-radius: 50%; background: #dc2626; animation: recBlink 1s infinite; }
@keyframes micPulse { 0% { transform: scale(1); opacity: 0.7; } 100% { transform: scale(1.9); opacity: 0; } }
@keyframes micWave { 0%, 100% { height: 6px; } 50% { height: 26px; } }
@keyframes recBlink { 50% { opacity: 0.25; } }

.cdss-icon { font-size: 28px; flex-shrink: 0; line-height: 1; }
.cdss-title { font-size: 14.5px; font-weight: 800; line-height: 1.3; }
.cdss-desc { font-size: 13px; line-height: 1.5; margin-top: 2px; }
.cdss-item-card > div:first-child { flex-wrap: wrap; gap: 6px; }

.rx-body { margin-bottom: 4px; }
.rx-line { font-size: 14px; line-height: 1.6; margin-bottom: 4px; }
.rx-sign-title { font-size: 13px; font-weight: bold; }
.footer-divider { display: none; }

/* Nút, tab, expander: không tràn chữ */
.stButton > button, .stDownloadButton > button {
    white-space: normal !important; line-height: 1.3 !important; min-height: 46px; border-radius: 10px !important; font-weight: 600;
}
[data-testid="stExpander"] summary p { white-space: normal !important; word-break: break-word; }
.stTabs [data-baseweb="tab-list"] { overflow-x: auto; flex-wrap: nowrap !important; scrollbar-width: none; }
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
.stTabs [data-baseweb="tab"] { white-space: nowrap; flex-shrink: 0; }
.medlatec-topbar { flex-wrap: wrap; gap: 12px; }
:focus-visible { outline: 2px solid var(--med-blue) !important; outline-offset: 2px; }

/* ==========================================================
   RESPONSIVE
========================================================== */
@media (max-width: 1100px) {
    .medlatec-menu-pills { display: none; }
    .banner-content { max-width: 75%; }
    .banner-graphic { font-size: 72px; }
}

@media (max-width: 768px) {
    [data-testid="stAppViewBlockContainer"] { padding: 0.75rem 0.9rem 2rem !important; }

    .medlatec-topbar { flex-direction: column; align-items: stretch; padding: 12px 14px; border-radius: 14px; }
    .medlatec-logo-wrap { gap: 10px; }
    .medlatec-logo-img { height: 48px; max-width: 120px; }
    .medlatec-brand-title { font-size: 17px; }
    .medlatec-brand-sub { font-size: 10px; letter-spacing: 0.2px; }
    .medlatec-contact-pill { justify-content: center; padding: 6px 12px; }

    .banner-slider-container { height: 400px; border-radius: 16px; }
    .banner-slide { padding: 20px 18px; align-items: flex-start; }
    .banner-content { max-width: 100%; }
    .banner-graphic { display: none; }
    .banner-tag { font-size: 10.5px; padding: 4px 10px; margin-bottom: 8px; }
    .banner-title { font-size: 19px; }
    .banner-desc { font-size: 12.5px; margin-bottom: 10px; }
    .banner-pills-row { flex-wrap: wrap; gap: 6px; }
    .banner-mini-pill { font-size: 11px; padding: 4px 9px; }

    /* Thẻ KPI và chỉ số benchmark xếp 2 cột thay vì 1 cột dài */
    [data-testid="stHorizontalBlock"]:has(.stat-card) > [data-testid="stColumn"],
    [data-testid="stHorizontalBlock"]:has(.stat-card) > [data-testid="column"],
    [data-testid="stHorizontalBlock"]:has(.metric-box) > [data-testid="stColumn"],
    [data-testid="stHorizontalBlock"]:has(.metric-box) > [data-testid="column"] {
        min-width: calc(50% - 0.5rem) !important; flex: 1 1 calc(50% - 0.5rem) !important;
    }
    .stat-card { padding: 12px 14px !important; }
    .stat-value { font-size: 17px !important; }
    .metric-val { font-size: 22px; }

    .med-card { padding: 16px 16px !important; }
    .card-title { font-size: 15.5px !important; }
    .empty-card { padding: 24px 14px; min-height: 0; }
    .empty-steps { grid-template-columns: repeat(2, 1fr); }
    .cdss-alert-box { padding: 12px 14px; gap: 12px; }

    .prescription-container { padding: 8px; }
    .prescription-paper { padding: 20px 16px; min-height: 0; }
    .rx-top { flex-direction: column; gap: 8px; }
    .rx-code { text-align: left; }
    .rx-title { font-size: 19px; }
    .rx-signatures { gap: 12px; margin-top: 28px; font-size: 13px; }
    .footer-container { font-size: 12px; padding: 18px 8px; }
}

@media (prefers-reduced-motion: reduce) {
    .banner-track, .banner-graphic, .mic-ring, .mic-wave-bar, .rec-dot { animation: none !important; }
}


/* Refined light interface: stable contrast across Streamlit states */
[data-testid="stAppViewContainer"], [data-testid="stHeader"] { background: #f5f8fc !important; color: #172b4d !important; }
[data-testid="stAppViewContainer"] p, [data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] li { color: #24364b; }
[data-testid="stAppViewContainer"] h1, [data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3, [data-testid="stAppViewContainer"] h4 { color: #12304a !important; }
[data-testid="stSidebar"] { background: #fff !important; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #24364b !important; }
.stTabs [data-baseweb="tab-list"] { border-radius: 18px !important; padding: 7px !important; gap: 7px !important; background: #fff !important; }
.stTabs [data-baseweb="tab"] {
    color: #334155 !important; background: #f1f5f9 !important; border-radius: 13px !important;
    padding: 12px 18px !important; transition: color .22s ease, background .22s ease, transform .22s ease, box-shadow .22s ease !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #075985 !important; background: #e0f2fe !important; transform: translateY(-1px); }
.stTabs [data-baseweb="tab"][aria-selected="true"] { color: #fff !important; background: linear-gradient(135deg,#0875b9,#0f9f8f) !important; border-radius: 13px !important; }
.stTabs [data-baseweb="tab"] p, .stTabs [data-baseweb="tab"] div { color: inherit !important; }
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] button {
    border-radius: 14px !important; transition: all .22s ease !important; color: #19324a !important;
}
.stButton > button:hover, .stDownloadButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(15, 80, 130, .14) !important; }
.stButton > button[kind="primary"] { color: #fff !important; }
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea, [data-baseweb="select"] * { color: #172b4d !important; }
[data-testid="stExpander"] { border-radius: 16px !important; overflow: hidden; }
.med-card, .stat-card, .metric-box { transition: transform .24s ease, box-shadow .24s ease !important; }
.med-card:hover, .stat-card:hover, .metric-box:hover { transform: translateY(-3px); box-shadow: 0 14px 32px rgba(15, 80, 130, .12) !important; }
.medlatec-logo-img { height: 88px !important; max-width: 290px !important; }
.medlatec-menu-item, .medlatec-menu-item.active { color: #334155 !important; }
.medlatec-menu-item:hover { color: #075985 !important; }
.medlatec-brand-sub { color: #64748b !important; }


/* Streamlit Cloud can keep dark BaseWeb widget surfaces even with a light app theme. */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input,
[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div,
[data-baseweb="select"] > div {
    background: #ffffff !important;
    background-color: #ffffff !important;
    color: #172b4d !important;
    border-color: #cbd5e1 !important;
    -webkit-text-fill-color: #172b4d !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder,
[data-baseweb="input"] input::placeholder,
[data-baseweb="textarea"] textarea::placeholder {
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
    opacity: 1 !important;
}
[data-baseweb="select"] div, [data-baseweb="select"] span { color: #172b4d !important; }
[data-baseweb="popover"] ul, [data-baseweb="popover"] li,
[data-baseweb="popover"] [role="option"] {
    background: #ffffff !important;
    color: #172b4d !important;
}
[data-testid="stExpander"] details,
[data-testid="stExpander"] details > summary,
[data-testid="stExpander"] details > summary:hover {
    background: #ffffff !important;
    color: #172b4d !important;
    border-color: #d8e2ec !important;
}
[data-testid="stExpander"] details > summary p,
[data-testid="stExpander"] details > summary span,
[data-testid="stExpander"] details > summary svg { color: #17324d !important; fill: #17324d !important; }
[data-testid="stExpander"] details > div,
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    background: #ffffff !important;
    color: #24364b !important;
}
[data-testid="stExpander"] { border: 1px solid #d8e2ec !important; box-shadow: 0 4px 16px rgba(15, 55, 90, .05) !important; }
[data-testid="stAppViewContainer"] input,
[data-testid="stAppViewContainer"] textarea { caret-color: #0875b9 !important; }

</style>
"""
