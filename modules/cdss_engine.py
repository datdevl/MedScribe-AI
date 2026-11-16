"""
Mô-đun CDSS (Clinical Decision Support System) - Hỗ trợ Ra Quyết định Lâm sàng
Trọng tâm nghiên cứu của Đề tài NCKH 129.

Chức năng:
1. Phát hiện Tương tác thuốc (Drug-Drug Interaction - DDI)
2. Kiểm tra Chống chỉ định & Cảnh báo Dị ứng theo độ tuổi, bệnh nền
3. Gợi ý Chẩn đoán phân biệt (Differential Diagnosis)
4. Đề xuất Cận lâm sàng & Hướng dẫn phác đồ điều trị
"""

import re
import json
from .utils import clean_text, extract_json

# ── CƠ SỞ TRI THỨC Y KHOA: CÁC TƯƠNG TÁC THUỐC ĐIỂN HÌNH ─────
KNOWN_DRUG_INTERACTIONS = [
    {
        "pair": (r"clopidogrel", r"(omeprazole|esomeprazole)"),
        "severity": "DANGER",
        "title": "Tương tác Clopidogrel và Thuốc ức chế bơm proton (PPI)",
        "mechanism": "Omeprazole/Esomeprazole ức chế enzyme CYP2C19, làm giảm chuyển hóa Clopidogrel thành dạng hoạt tính.",
        "risk": "Làm giảm hiệu quả chống kết tập tiểu cầu, tăng nguy cơ tái phát nhồi máu cơ tim hoặc huyết khối.",
        "recommendation": "Thay thế bằng Pantoprazole hoặc Rabeprazole (ít ảnh hưởng tới CYP2C19) nếu cần bảo vệ dạ dày."
    },
    {
        "pair": (r"(aspirin|ibuprofen|meloxicam|diclofenac|celecoxib|naproxen|piroxicam)", r"(warfarin|rivaroxaban|dabigatran|apixaban|heparin)"),
        "severity": "DANGER",
        "title": "Phối hợp NSAID và Thuốc chống đông máu",
        "mechanism": "NSAID ức chế COX-1 làm tổn thương niêm mạc dạ dày và kháng ngưng tập tiểu cầu, cộng hưởng với thuốc chống đông.",
        "risk": "Nguy cơ xuất huyết tiêu hóa nghiêm trọng và chảy máu không kiểm soát.",
        "recommendation": "Tránh phối hợp. Nếu bắt buộc giảm đau, ưu tiên Paracetamol hoặc phối hợp thêm thuốc bảo vệ dạ dày và theo dõi sát INR/Hb."
    },
    {
        "pair": (r"(aspirin|ibuprofen|meloxicam|diclofenac|celecoxib|naproxen)", r"(prednisone|prednisolone|methylprednisolone|dexamethasone|betamethasone)"),
        "severity": "DANGER",
        "title": "Phối hợp NSAID và Corticosteroid",
        "mechanism": "Cả hai nhóm thuốc đều ức chế tổng hợp Prostaglandin bảo vệ niêm mạc dạ dày.",
        "risk": "Tăng nguy cơ viêm loét, thủng dạ dày tá tràng và xuất huyết tiêu hóa lên gấp 4-10 lần.",
        "recommendation": "Hạn chế tối đa dùng đồng thời. Luôn kê kèm PPI (Pantoprazole/Omeprazole) liều chuẩn để dự phòng loét dạ dày."
    },
    {
        "pair": (r"(enalapril|lisinopril|perindopril|losartan|valsartan|telmisartan)", r"(spironolactone|eplerenone|potassium|kali)"),
        "severity": "WARNING",
        "title": "Phối hợp thuốc ức chế hệ RAAS và Lợi tiểu giữ Kali",
        "mechanism": "Cả hai đều làm giảm bài tiết kali tại ống thận.",
        "risk": "Tăng Kali máu nguy hiểm, có thể dẫn đến loạn nhịp tim hoặc ngừng tim.",
        "recommendation": "Kiểm tra định kỳ nồng độ Kali huyết thanh và chức năng thận (Creatinine/eGFR) sau 1-2 tuần bắt đầu điều trị."
    },
    {
        "pair": (r"(simvastatin|atorvastatin|lovastatin)", r"(clarithromycin|erythromycin|ketoconazole|itraconazole)"),
        "severity": "DANGER",
        "title": "Phối hợp Statin và Kháng sinh nhóm Macrolide / Kháng nấm",
        "mechanism": "Clarithromycin/Erythromycin ức chế mạnh CYP3A4, làm tăng vọt nồng độ Statin trong huyết tương.",
        "risk": "Tăng độc tính trên cơ, nguy cơ tiêu cơ vân cấp (Rhabdomyolysis) và suy thận cấp.",
        "recommendation": "Tạm dừng Statin trong thời gian điều trị bằng Macrolide, hoặc chuyển sang Rosuvastatin/Pravastatin hoặc dùng Azithromycin thay thế."
    },
    {
        "pair": (r"(ciprofloxacin|levofloxacin)", r"(maalox|alusi|canxi|calcium|sat|ferrovit|magnesi)"),
        "severity": "WARNING",
        "title": "Tương tác Fluoroquinolone và Cation kim loại (Antacid / Sắt / Canxi)",
        "mechanism": "Cation đa hóa trị (Al3+, Mg2+, Fe2+, Ca2+) tạo phức chelate không tan với kháng sinh Quinolone.",
        "risk": "Làm giảm hấp thu kháng sinh từ 50% đến 90%, dẫn đến thất bại điều trị nhiễm khuẩn.",
        "recommendation": "Uống Quinolone trước ít nhất 2 giờ hoặc sau 4 giờ so với thuốc chứa kim loại/thuốc dạ dày antacid."
    },
    {
        "pair": (r"metformin", r"(iod|can_quang|contrast)"),
        "severity": "DANGER",
        "title": "Metformin và Thuốc cản quang chứa Iod",
        "mechanism": "Thuốc cản quang có thể gây suy thận cấp, làm tích lũy Metformin.",
        "risk": "Gây nhiễm toan acid lactic đe dọa tính mạng (tỷ lệ tử vong tới 50%).",
        "recommendation": "Ngừng Metformin 48 giờ trước và sau khi chụp cản quang, chỉ dùng lại sau khi kiểm tra chức năng thận bình thường."
    },
    {
        "pair": (r"(sildenafil|tadalafil|vardenafil)", r"(nitroglycerin|isosorbide|nitrostat)"),
        "severity": "DANGER",
        "title": "Thuốc ức chế PDE-5 và Thuốc giãn mạch Nitrate",
        "mechanism": "Cả hai đều khuếch đại con đường NO-cGMP gây giãn mạch toàn thân cực mạnh.",
        "risk": "Tụt huyết áp nghiêm trọng, ngất, sốc và tử vong do trụy tuần hoàn.",
        "recommendation": "CHỐNG CHỈ ĐỊNH TUYỆT ĐỐI. Không được dùng cùng trong vòng 24 - 48 giờ."
    },
    {
        "pair": (r"paracetamol|acetaminophen|panadol|efferalgan", r"paracetamol|acetaminophen|panadol|efferalgan"),
        "severity": "WARNING",
        "title": "Trùng lặp hoạt chất Paracetamol",
        "mechanism": "Kê nhiều biệt dược khác nhau cùng chứa hoạt chất Paracetamol (ví dụ Panadol + Efferalgan).",
        "risk": "Dễ vượt quá liều tối đa (4000mg/ngày), dẫn đến ngộ độc gan cấp và hoại tử tế bào gan.",
        "recommendation": "Chỉ dùng một chế phẩm chứa Paracetamol, kiểm tra tổng liều hằng ngày không vượt quá 4g ở người lớn."
    }
]


# ── CƠ SỞ TRI THỨC VỀ CHỐNG CHỈ ĐỊNH VÀ DỊ ỨNG ───────────────
CONTRAINDICATION_RULES = [
    {
        "trigger": lambda age, med, hist, alg: age < 16 and re.search(r"aspirin", med, re.I),
        "alert": "CHỐNG CHỈ ĐỊNH: Aspirin ở trẻ em/thanh thiếu niên (< 16 tuổi)",
        "risk": "Nguy cơ cao mắc Hội chứng Reye (viêm não và thoái hóa mỡ gan cấp tính, tỷ lệ tử vong cao).",
        "recommendation": "Chuyển sang dùng Paracetamol hoặc Ibuprofen để hạ sốt/giảm đau an toàn cho trẻ."
    },
    {
        "trigger": lambda age, med, hist, alg: age < 18 and re.search(r"(ciprofloxacin|levofloxacin|ofloxacin)", med, re.I),
        "alert": "CẢNH BÁO THẬN TRỌNG: Fluoroquinolone ở trẻ em (< 18 tuổi)",
        "risk": "Nguy cơ thoái hóa sụn khớp ở các khớp chịu tải và tổn thương gân (gân Achilles).",
        "recommendation": "Hạn chế sử dụng ở trẻ vị thành niên trừ các chỉ định đặc biệt (viêm phổi xơ nang, than)."
    },
    {
        "trigger": lambda age, med, hist, alg: re.search(r"(loet|da day|xuat huyet|viem da day)", hist, re.I) and re.search(r"(ibuprofen|meloxicam|diclofenac|aspirin|piroxicam)", med, re.I),
        "alert": "CẢNH BÁO: Kê đơn NSAID trên bệnh nhân có tiền sử viêm loét/xuất huyết dạ dày",
        "risk": "Kích ứng niêm mạc dạ dày, tái phát loét và xuất huyết tiêu hóa ồ ạt.",
        "recommendation": "Ưu tiên giảm đau Paracetamol. Nếu bắt buộc dùng NSAID, chọn ức chế chọn lọc COX-2 (Celecoxib) kết hợp PPI."
    },
    {
        "trigger": lambda age, med, hist, alg: re.search(r"(hen|suyễn|asthma)", hist, re.I) and re.search(r"(propranolol|atenolol|timolol)", med, re.I),
        "alert": "CHỐNG CHỈ ĐỊNH: Thuốc chẹn Beta không chọn lọc ở bệnh nhân Hen phế quản",
        "risk": "Ức chế thụ thể Beta-2 ở phế quản, gây co thắt phế quản cấp tính nặng đe dọa tính mạng.",
        "recommendation": "Chống chỉ định. Thay thế bằng các nhóm thuốc hạ áp khác (Amlodipine, Perindopril)."
    },
    {
        "trigger": lambda age, med, hist, alg: re.search(r"(penicillin|amoxicillin|ampicillin)", alg, re.I) and re.search(r"(augmentin|amoxicillin|ampicillin|oxacillin)", med, re.I),
        "alert": "NGUY HIỂM DỊ ỨNG: Kê kháng sinh Penicillin trên người có tiền sử dị ứng Penicillin",
        "risk": "Nguy cơ sốc phản vệ type I (mày đay, phù mạch, co thắt đường thở, tụt huyết áp tử vong).",
        "recommendation": "Chống chỉ định tuyệt đối nhóm Penicillin. Thận trọng với Cephalosporin (nguy cơ dị ứng chéo ~5-10%). Chuyển sang Macrolide (Azithromycin) hoặc Quinolone."
    }
]


def check_rule_based_ddi(medicines):
    """Kiểm tra tương tác thuốc theo luật nội suy chuyên gia."""
    interactions = []
    if not medicines or len(medicines) < 2:
        return interactions

    med_names = [clean_text(m.get("name", "")).lower() for m in medicines if m.get("name")]

    for i in range(len(med_names)):
        for j in range(i + 1, len(med_names)):
            m1, m2 = med_names[i], med_names[j]
            for rule in KNOWN_DRUG_INTERACTIONS:
                p1, p2 = rule["pair"]
                match1 = bool(re.search(p1, m1, re.I) and re.search(p2, m2, re.I))
                match2 = bool(re.search(p1, m2, re.I) and re.search(p2, m1, re.I))
                if match1 or match2:
                    interactions.append({
                        "drugs": [medicines[i].get("name", m1), medicines[j].get("name", m2)],
                        "severity": rule["severity"],
                        "title": rule["title"],
                        "mechanism": rule["mechanism"],
                        "risk": rule["risk"],
                        "recommendation": rule["recommendation"]
                    })
    return interactions


def check_contraindications(patient_age_str, medicines, medical_history="", allergies=""):
    """Kiểm tra chống chỉ định và dị ứng theo quy tắc lâm sàng."""
    contraindications = []
    try:
        nums = re.findall(r"\d+", str(patient_age_str))
        age = int(nums[0]) if nums else 35
    except Exception:
        age = 35

    med_list = [clean_text(m.get("name", "")) for m in medicines]
    med_text = " ".join(med_list)

    for rule in CONTRAINDICATION_RULES:
        try:
            if rule["trigger"](age, med_text, medical_history, allergies):
                contraindications.append({
                    "alert": rule["alert"],
                    "risk": rule["risk"],
                    "recommendation": rule["recommendation"]
                })
        except Exception:
            continue

    return contraindications


def get_heuristic_differential_diagnosis(symptoms, primary_diagnosis=""):
    """
    Sinh gợi ý chẩn đoán phân biệt và cận lâm sàng dựa trên từ khóa triệu chứng.
    Hỗ trợ khi hệ thống chạy offline hoặc không có API key.
    """
    text = (symptoms + " " + primary_diagnosis).lower()
    differentials = []
    tests = []

    # Nhóm Tim mạch / Đau ngực
    if any(k in text for k in ["đau ngực", "tức ngực", "khó thở", "hồi hộp", "tim"]):
        differentials.append({
            "condition": "Hội chứng vành cấp / Thiếu máu cơ tim cục bộ",
            "probability": "Cao",
            "rationale": "Bệnh nhân có triệu chứng đau tức ngực, cần loại trừ nguy cơ tắc nghẽn mạch vành cấp tính."
        })
        differentials.append({
            "condition": "Trào ngược dạ dày thực quản (GERD) / Co thắt thực quản",
            "probability": "Trung bình",
            "rationale": "Cơn đau nóng rát sau xương ức dễ nhầm lẫn với cơn đau thắt ngực."
        })
        tests.append({"test": "Điện tâm đồ (ECG 12 chuyển đạo)", "purpose": "Khảo sát sóng ST-T tìm dấu hiệu thiếu máu cơ tim."})
        tests.append({"test": "Men tim (Troponin I/T siêu nhạy)", "purpose": "Loại trừ nhồi máu cơ tim cấp."})
        tests.append({"test": "Siêu âm tim Doppler màu", "purpose": "Đánh giá chức năng tâm thu thất trái và vận động vùng thành tim."})

    # Nhóm Tiêu hóa / Đau bụng
    elif any(k in text for k in ["đau bụng", "dạ dày", "thượng vị", "ợ chua", "buồn nôn", "tiêu chảy"]):
        differentials.append({
            "condition": "Viêm loét dạ dày - tá tràng / Nhiễm Helicobacter pylori",
            "probability": "Cao",
            "rationale": "Đau rát vùng thượng vị liên quan đến bữa ăn, kèm ợ hơi ợ chua."
        })
        differentials.append({
            "condition": "Viêm túi mật cấp / Sỏi mật",
            "probability": "Trung bình",
            "rationale": "Cần phân biệt nếu có đau hạ sườn phải hoặc sau bữa ăn nhiều dầu mỡ."
        })
        differentials.append({
            "condition": "Viêm tụy cấp thể nhẹ",
            "probability": "Cần theo dõi",
            "rationale": "Nếu đau dữ dội lan ra sau lưng kèm nôn ói nhiều."
        })
        tests.append({"test": "Nội soi thực quản - dạ dày - tá tràng (kèm test Clo-test tìm HP)", "purpose": "Xác định vị trí ổ loét và tình trạng nhiễm vi khuẩn H.pylori."})
        tests.append({"test": "Siêu âm ổ bụng tổng quát", "purpose": "Khảo sát gan, mật, tụy, thận để loại trừ sỏi hoặc viêm nhiễm cơ quan lân cận."})
        tests.append({"test": "Công thức máu toàn bộ (CBC) & CRP", "purpose": "Đánh giá tình trạng mất máu ẩn và mức độ viêm."})

    # Nhóm Hô hấp / Ho, Sốt
    elif any(k in text for k in ["ho", "sốt", "đờm", "viêm họng", "phổi", "khò khè"]):
        differentials.append({
            "condition": "Viêm phế quản cấp",
            "probability": "Cao",
            "rationale": "Ho có đờm, rát họng, sốt nhẹ hoặc vừa, nghe phổi có thể có ran rít nhẹ."
        })
        differentials.append({
            "condition": "Viêm phổi mắc phải cộng đồng (CAP)",
            "probability": "Trung bình",
            "rationale": "Cần loại trừ nếu sốt cao liên tục, khó thở hoặc nghe thấy ran ẩm/nổ ở phổi."
        })
        differentials.append({
            "condition": "Cúm mùa hoặc Nhiễm virus đường hô hấp trên",
            "probability": "Trung bình",
            "rationale": "Khởi phát cấp tính, đau mỏi toàn thân, nghẹt mũi kèm theo."
        })
        tests.append({"test": "X-quang ngực thẳng (Chest X-ray)", "purpose": "Phát hiện tổn thương thâm nhiễm nhu mô phổi hoặc đông đặc phổi."})
        tests.append({"test": "Công thức máu (CBC) và Định lượng Procalcitonin/CRP", "purpose": "Phân biệt nguyên nhân do vi khuẩn (bạch cầu tăng) hay virus."})

    # Nhóm Tăng huyết áp / Đau đầu, Chóng mặt
    elif any(k in text for k in ["huyết áp", "đau đầu", "chóng mặt", "hoa mắt"]):
        differentials.append({
            "condition": "Tăng huyết áp nguyên phát giai đoạn 2",
            "probability": "Cao",
            "rationale": "Chỉ số huyết áp đo được vượt ngưỡng 140/90 mmHg kèm đau đầu căng thẳng."
        })
        differentials.append({
            "condition": "Rối loạn tiền đình ngoại biên",
            "probability": "Trung bình",
            "rationale": "Chóng mặt dạng quay cuồng, mất thăng bằng tăng lên khi thay đổi tư thế."
        })
        tests.append({"test": "Đo huyết áp liên tục 24h (Holter huyết áp)", "purpose": "Đánh giá dao động huyết áp ngày đêm và khẳng định chẩn đoán."})
        tests.append({"test": "Sinh hóa máu: Đường huyết, HbA1c, Bộ mỡ máu (Lipid panel), Creatinine, Điện giải đồ", "purpose": "Đánh giá các yếu tố nguy cơ tim mạch đồng mắc và tổn thương cơ quan đích."})

    # Mặc định chung
    else:
        differentials.append({
            "condition": "Theo dõi đáp ứng điều trị ban đầu",
            "probability": "Trung bình",
            "rationale": "Triệu chứng chưa khu trú điển hình, cần tái khám đánh giá tiến triển sau 3-5 ngày."
        })
        tests.append({"test": "Công thức máu (CBC) & Tổng phân tích nước tiểu", "purpose": "Sàng lọc cơ bản các rối loạn chuyển hóa và tình trạng nhiễm trùng."})

    return differentials, tests


def run_cdss_analysis(clinical_data, prescription, client=None, model_id=None):
    """
    Chạy bộ máy CDSS toàn diện:
    1. Kiểm tra DDI và chống chỉ định theo rules (tốc độ cao, an toàn tuyệt đối).
    2. Nếu có client Gemini, bổ sung phân tích sâu bằng LLM.
    """
    medicines = prescription if isinstance(prescription, list) else []
    patient_info = clinical_data.get("patient", {})
    age_str = patient_info.get("age", "35")

    # Thu thập triệu chứng & bệnh sử
    soap = clinical_data.get("soap", {})
    subj = soap.get("subjective", {})
    symptoms = subj.get("chief_complaint", "") + " " + subj.get("history_of_illness", "")
    med_history = subj.get("medical_history", "")
    allergies = subj.get("allergies", "")
    primary_diag = soap.get("assessment", {}).get("primary_diagnosis", "")

    # BƯỚC 1: Rule-based verification
    rule_ddi = check_rule_based_ddi(medicines)
    rule_contra = check_contraindications(age_str, medicines, med_history, allergies)
    rule_diff, rule_tests = get_heuristic_differential_diagnosis(symptoms, primary_diag)

    # Đánh giá mức độ an toàn ban đầu
    safety_verdict = "SAFE"
    if any(item.get("severity") == "DANGER" for item in rule_ddi) or rule_contra:
        safety_verdict = "DANGER"
    elif rule_ddi:
        safety_verdict = "WARNING"

    cdss_result = {
        "safety_verdict": safety_verdict,
        "drug_interactions": rule_ddi,
        "contraindications": rule_contra,
        "differential_suggestions": rule_diff,
        "recommended_tests": rule_tests,
        "clinical_guidelines_summary": (
            "Khuyến cáo tuân thủ Hướng dẫn Chẩn đoán và Điều trị của Bộ Y tế Việt Nam. "
            "Luôn kiểm tra tiền sử dị ứng thuốc và chức năng gan thận trước khi bắt đầu phác đồ phối hợp."
        )
    }

    # BƯỚC 2: Tăng cường bằng LLM nếu có client
    if client and model_id and medicines:
        prompt = f"""
Bạn là chuyên gia Dược lâm sàng và Hệ thống Hỗ trợ Ra Quyết định Lâm sàng (CDSS).
Hãy phân tích an toàn đơn thuốc và ca lâm sàng sau:

THÔNG TIN BỆNH NHÂN:
- Tuổi: {age_str}
- Chẩn đoán: {primary_diag}
- Triệu chứng: {symptoms}
- Tiền sử bệnh nền: {med_history}
- Tiền sử dị ứng: {allergies}

ĐƠN THUỐC KÊ:
{json.dumps(medicines, ensure_ascii=False, indent=2)}

YÊU CẦU:
Trả về DUY NHẤT một chuỗi JSON hợp lệ với cấu trúc sau:
{{
  "safety_verdict": "SAFE" hoặc "WARNING" hoặc "DANGER",
  "llm_drug_interactions": [
    {{
      "drugs": ["Thuốc A", "Thuốc B"],
      "severity": "DANGER" hoặc "WARNING",
      "title": "Tên tương tác",
      "mechanism": "Cơ chế tác động dược lý",
      "risk": "Nguy cơ lâm sàng",
      "recommendation": "Khuyến cáo điều chỉnh"
    }}
  ],
  "llm_contraindications": [
    {{
      "alert": "Cảnh báo chống chỉ định/dị ứng",
      "risk": "Mức độ nguy cơ",
      "recommendation": "Hướng xử trí"
    }}
  ],
  "llm_clinical_notes": "Tóm lược khuyến nghị chuyên môn ngắn gọn 2-3 câu."
}}
Chỉ trả về JSON thuần túy, không dùng thẻ markdown.
"""
        try:
            resp = client.models.generate_content(
                model=model_id,
                contents=prompt
            )
            parsed = extract_json(resp.text)
            if parsed and isinstance(parsed, dict):
                # Hợp nhất kết quả LLM
                llm_ddi = parsed.get("llm_drug_interactions", [])
                if isinstance(llm_ddi, list) and llm_ddi:
                    # Ghép vào danh sách hiện tại nếu chưa có
                    existing_titles = {item.get("title") for item in cdss_result["drug_interactions"]}
                    for d in llm_ddi:
                        if d.get("title") not in existing_titles:
                            cdss_result["drug_interactions"].append(d)

                llm_contra = parsed.get("llm_contraindications", [])
                if isinstance(llm_contra, list) and llm_contra:
                    cdss_result["contraindications"].extend(llm_contra)

                if parsed.get("safety_verdict") in ["DANGER", "WARNING", "SAFE"]:
                    if parsed["safety_verdict"] == "DANGER" or cdss_result["safety_verdict"] == "DANGER":
                        cdss_result["safety_verdict"] = "DANGER"
                    elif parsed["safety_verdict"] == "WARNING" or cdss_result["safety_verdict"] == "WARNING":
                        cdss_result["safety_verdict"] = "WARNING"

                if parsed.get("llm_clinical_notes"):
                    cdss_result["clinical_guidelines_summary"] = clean_text(parsed["llm_clinical_notes"])
        except Exception:
            # Nếu LLM bận/lỗi, tiếp tục sử dụng kết quả Rule-based an toàn
            pass

    return cdss_result
