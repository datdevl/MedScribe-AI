import re
import json
import html


def clean_text(value):
    """Làm sạch văn bản đầu vào, loại bỏ markdown code block, html tags."""
    if value is None:
        return ""
    value = str(value)
    value = re.sub(r"```(?:json|html|text|markdown)?", "", value, flags=re.IGNORECASE)
    value = value.replace("```", "")
    value = re.sub(r"<[^>]+>", "", value)
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    return value.strip()


def safe(value):
    """Escape ký tự HTML để hiển thị an toàn trên giao diện."""
    return html.escape(clean_text(value))


def get_mime_type(filename):
    """Xác định MIME type từ tên file âm thanh."""
    if not filename:
        return "audio/wav"
    filename = filename.lower()
    if filename.endswith(".mp3"):
        return "audio/mpeg"
    if filename.endswith(".m4a"):
        return "audio/mp4"
    if filename.endswith(".ogg"):
        return "audio/ogg"
    if filename.endswith(".flac"):
        return "audio/flac"
    return "audio/wav"


def extract_json(text):
    """Trích xuất và parse JSON từ chuỗi phản hồi của LLM."""
    if not text:
        return {}
    cleaned = clean_text(text)
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # Tìm khối JSON giữa dấu ngoặc nhọn đầu tiên và cuối cùng
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(cleaned[start:end + 1])
        except Exception:
            pass

    # Thử tìm với regex khối JSON
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass

    return {}


def normalize_medical_record(data):
    """
    Chuẩn hóa dữ liệu bệnh án điện tử đầy đủ theo chuẩn SOAP
    kết hợp hỗ trợ ra quyết định lâm sàng (CDSS).
    """
    default_structure = {
        "raw_transcript": "",
        "patient": {
            "name": "",
            "age": "",
            "gender": "",
            "address": "",
            "phone": ""
        },
        "soap": {
            "subjective": {
                "chief_complaint": "",       # Lý do đến khám
                "history_of_illness": "",    # Bệnh sử hiện tại
                "medical_history": "",       # Tiền sử bệnh nền
                "allergies": "Không ghi nhận" # Tiền sử dị ứng
            },
            "objective": {
                "vital_signs": {             # Dấu hiệu sinh tồn
                    "blood_pressure": "120/80 mmHg",
                    "heart_rate": "75 bpm",
                    "temperature": "37.0 °C",
                    "spo2": "98%",
                    "respiratory_rate": "18 lần/phút"
                },
                "physical_exam": ""          # Thăm khám thực thể
            },
            "assessment": {
                "primary_diagnosis": "",     # Chẩn đoán xác định
                "icd10": "",                 # Mã ICD-10
                "differential_diagnosis": "" # Chẩn đoán phân biệt
            },
            "plan": {
                "prescription": [],          # Danh sách thuốc
                "lab_tests": "",             # Chỉ định cận lâm sàng
                "advice": "",                # Lời dặn
                "follow_up": ""              # Hẹn tái khám
            }
        },
        "cdss": {
            "safety_verdict": "SAFE",        # SAFE, WARNING, DANGER
            "drug_interactions": [],         # Cảnh báo tương tác thuốc
            "contraindications": [],         # Cảnh báo chống chỉ định & dị ứng
            "differential_suggestions": [],  # Gợi ý chẩn đoán phân biệt
            "recommended_tests": [],         # Gợi ý cận lâm sàng cần làm
            "clinical_guidelines_summary": "" # Tóm tắt khuyến cáo phác đồ
        },
        "doctor": ""
    }

    if not isinstance(data, dict):
        return default_structure

    # 1. Transcript
    default_structure["raw_transcript"] = clean_text(
        data.get("raw_transcript", data.get("transcript", ""))
    )

    # 2. Patient
    pat = data.get("patient", {})
    if isinstance(pat, dict):
        for k in default_structure["patient"]:
            default_structure["patient"][k] = clean_text(pat.get(k, ""))

    # 3. SOAP
    # Xử lý tương thích ngược nếu data có dạng cũ: clinical: {symptoms, examination, diagnosis}
    old_clinical = data.get("clinical", {})
    soap_in = data.get("soap", {})

    subj_in = soap_in.get("subjective", {}) if isinstance(soap_in, dict) else {}
    obj_in = soap_in.get("objective", {}) if isinstance(soap_in, dict) else {}
    ass_in = soap_in.get("assessment", {}) if isinstance(soap_in, dict) else {}
    plan_in = soap_in.get("plan", {}) if isinstance(soap_in, dict) else {}

    # Subjective
    default_structure["soap"]["subjective"]["chief_complaint"] = clean_text(
        subj_in.get("chief_complaint", old_clinical.get("symptoms", ""))
    )
    default_structure["soap"]["subjective"]["history_of_illness"] = clean_text(
        subj_in.get("history_of_illness", "")
    )
    default_structure["soap"]["subjective"]["medical_history"] = clean_text(
        subj_in.get("medical_history", "")
    )
    default_structure["soap"]["subjective"]["allergies"] = clean_text(
        subj_in.get("allergies", "Không ghi nhận")
    )

    # Objective
    if isinstance(obj_in.get("vital_signs"), dict):
        for vk, vv in obj_in["vital_signs"].items():
            if vk in default_structure["soap"]["objective"]["vital_signs"]:
                default_structure["soap"]["objective"]["vital_signs"][vk] = clean_text(vv)
    default_structure["soap"]["objective"]["physical_exam"] = clean_text(
        obj_in.get("physical_exam", old_clinical.get("examination", ""))
    )

    # Assessment
    default_structure["soap"]["assessment"]["primary_diagnosis"] = clean_text(
        ass_in.get("primary_diagnosis", old_clinical.get("diagnosis", data.get("diagnosis", "")))
    )
    default_structure["soap"]["assessment"]["icd10"] = clean_text(ass_in.get("icd10", ""))
    default_structure["soap"]["assessment"]["differential_diagnosis"] = clean_text(
        ass_in.get("differential_diagnosis", "")
    )

    # Plan
    raw_rx = plan_in.get("prescription", data.get("prescription", []))
    cleaned_rx = []
    if isinstance(raw_rx, list):
        for item in raw_rx:
            if isinstance(item, dict):
                cleaned_rx.append({
                    "name": clean_text(item.get("name", "")),
                    "dosage": clean_text(item.get("dosage", "")),
                    "quantity": clean_text(item.get("quantity", "")),
                    "instruction": clean_text(item.get("instruction", ""))
                })
            elif isinstance(item, str) and item.strip():
                cleaned_rx.append({
                    "name": clean_text(item),
                    "dosage": "",
                    "quantity": "",
                    "instruction": ""
                })
    default_structure["soap"]["plan"]["prescription"] = cleaned_rx
    default_structure["soap"]["plan"]["lab_tests"] = clean_text(plan_in.get("lab_tests", ""))
    default_structure["soap"]["plan"]["advice"] = clean_text(
        plan_in.get("advice", data.get("advice", ""))
    )
    default_structure["soap"]["plan"]["follow_up"] = clean_text(plan_in.get("follow_up", ""))

    # 4. CDSS
    cdss_in = data.get("cdss", {})
    if isinstance(cdss_in, dict):
        default_structure["cdss"]["safety_verdict"] = clean_text(
            cdss_in.get("safety_verdict", "SAFE")
        )
        default_structure["cdss"]["drug_interactions"] = cdss_in.get("drug_interactions", [])
        default_structure["cdss"]["contraindications"] = cdss_in.get("contraindications", [])
        default_structure["cdss"]["differential_suggestions"] = cdss_in.get(
            "differential_suggestions", []
        )
        default_structure["cdss"]["recommended_tests"] = cdss_in.get("recommended_tests", [])
        default_structure["cdss"]["clinical_guidelines_summary"] = clean_text(
            cdss_in.get("clinical_guidelines_summary", "")
        )

    # 5. Doctor
    default_structure["doctor"] = clean_text(data.get("doctor", ""))

    return default_structure


# ── Đánh giá Khoa học (ASR Benchmark Metrics) ─────────────────

def calculate_wer(reference, hypothesis):
    """
    Tính Word Error Rate (WER) giữa văn bản gốc chuẩn và văn bản nhận dạng ASR.
    Sử dụng thuật toán quy hoạch động Levenshtein Distance trên đơn vị từ.
    Công thức: WER = (Substitutions + Insertions + Deletions) / N
    """
    r = clean_text(reference).lower().split()
    h = clean_text(hypothesis).lower().split()

    if not r:
        return 0.0 if not h else 1.0

    d = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]
    for i in range(len(r) + 1):
        d[i][0] = i
    for j in range(len(h) + 1):
        d[0][j] = j

    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            if r[i - 1] == h[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                substitution = d[i - 1][j - 1] + 1
                insertion = d[i][j - 1] + 1
                deletion = d[i - 1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)

    wer = d[len(r)][len(h)] / len(r)
    return round(wer, 4)


def calculate_cer(reference, hypothesis):
    """Tính Character Error Rate (CER) trên đơn vị ký tự."""
    r = clean_text(reference).lower().replace(" ", "")
    h = clean_text(hypothesis).lower().replace(" ", "")

    if not r:
        return 0.0 if not h else 1.0

    d = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]
    for i in range(len(r) + 1):
        d[i][0] = i
    for j in range(len(h) + 1):
        d[0][j] = j

    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            if r[i - 1] == h[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = min(
                    d[i - 1][j - 1] + 1,
                    d[i][j - 1] + 1,
                    d[i - 1][j] + 1
                )

    cer = d[len(r)][len(h)] / len(r)
    return round(cer, 4)
