import json
import time
from google.genai import types
from .utils import extract_json, normalize_medical_record, clean_text
from .cdss_engine import run_cdss_analysis

FALLBACK_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-flash-latest"
]


def build_clinical_prompt(doctor_name):
    """
    Tạo Prompt chuyên sâu cho AI y tế:
    Vừa làm nhiệm vụ ASR (gỡ băng chi tiết), vừa bóc tách EMR chuẩn SOAP,
    đồng thời kích hoạt phân tích CDSS (Hỗ trợ ra quyết định lâm sàng).
    """
    return f"""
Bạn là MedScribe AI - Hệ thống Trợ lý Y tế Thông minh kiêm Chuyên gia Ra Quyết định Lâm sàng (CDSS).
Nhiệm vụ của bạn:
1. Gỡ băng chi tiết toàn bộ hội thoại giữa Bác sĩ và Bệnh nhân trong file âm thanh được cung cấp (ASR Transcription).
2. Chuẩn hóa hồ sơ bệnh án điện tử (EMR) theo cấu trúc chuẩn quốc tế SOAP (Subjective - Objective - Assessment - Plan).
3. Đóng vai trò hệ thống CDSS: Rà soát an toàn đơn thuốc, cảnh báo tương tác thuốc (DDI), phát hiện chống chỉ định/dị ứng, đề xuất chẩn đoán phân biệt và chỉ định cận lâm sàng.

Bác sĩ phụ trách: {doctor_name}

YÊU CẦU ĐẦU RA:
Trả về DUY NHẤT một chuỗi JSON hợp lệ. TUYỆT ĐỐI không dùng Markdown, không thẻ ```json, không giải thích bên ngoài JSON.

CẤU TRÚC JSON BẮT BUỘC:
{{
  "raw_transcript": "Ghi lại nguyên văn cuộc hội thoại có phân định người nói rõ ràng (ví dụ: 'Bác sĩ: Chào bác, hôm nay bác thấy thế nào?... Bệnh nhân: Dạ tôi bị đau...'). Không tự bịa nếu không nghe thấy.",
  "patient": {{
    "name": "Họ và tên bệnh nhân",
    "age": "Tuổi",
    "gender": "Nam hoặc Nữ",
    "address": "Quận Hoàn Kiếm, Hà Nội",
    "phone": "Số điện thoại nếu có"
  }},
  "soap": {{
    "subjective": {{
      "chief_complaint": "Lý do chính đến khám",
      "history_of_illness": "Bệnh sử hiện tại (thời gian, vị trí, tính chất đau...)",
      "medical_history": "Tiền sử bệnh bản thân và gia đình",
      "allergies": "Tiền sử dị ứng thuốc/thức ăn (nếu không có ghi 'Chưa ghi nhận')"
    }},
    "objective": {{
      "vital_signs": {{
        "blood_pressure": "Huyết áp (ví dụ: 125/80 mmHg)",
        "heart_rate": "Mạch (ví dụ: 78 bpm)",
        "temperature": "Nhiệt độ (ví dụ: 37.0 °C)",
        "spo2": "SpO2 (ví dụ: 98%)",
        "respiratory_rate": "Nhịp thở (ví dụ: 18 lần/phút)"
      }},
      "physical_exam": "Kết quả khám thực thể (tim, phổi, bụng, họng...)"
    }},
    "assessment": {{
      "primary_diagnosis": "Chẩn đoán xác định chính",
      "icd10": "Mã ICD-10 tương ứng (ví dụ: K29.5, I10, J20...)",
      "differential_diagnosis": "Chẩn đoán phân biệt cần lưu ý"
    }},
    "plan": {{
      "prescription": [
        {{
          "name": "Tên thuốc kèm hàm lượng",
          "dosage": "Liều dùng mỗi lần",
          "quantity": "Tổng số lượng",
          "instruction": "Cách dùng (uống sau ăn, sáng/tối...)"
        }}
      ],
      "lab_tests": "Các chỉ định xét nghiệm, chẩn đoán hình ảnh cần thực hiện",
      "advice": "Lời dặn chế độ ăn uống, sinh hoạt, kiêng cữ",
      "follow_up": "Thời gian hẹn tái khám"
    }}
  }},
  "cdss": {{
    "safety_verdict": "SAFE hoặc WARNING hoặc DANGER",
    "drug_interactions": [
      {{
        "drugs": ["Thuốc A", "Thuốc B"],
        "severity": "DANGER hoặc WARNING",
        "title": "Tên tương tác",
        "mechanism": "Cơ chế tác động",
        "risk": "Nguy cơ lâm sàng",
        "recommendation": "Khuyến nghị điều chỉnh"
      }}
    ],
    "contraindications": [
      {{
        "alert": "Cảnh báo chống chỉ định/dị ứng",
        "risk": "Nguy cơ",
        "recommendation": "Xử trí"
      }}
    ],
    "differential_suggestions": [
      {{
        "condition": "Bệnh phân biệt 1",
        "probability": "Cao/Trung bình",
        "rationale": "Lý do gợi ý"
      }}
    ],
    "recommended_tests": [
      {{
        "test": "Tên xét nghiệm/Cận lâm sàng",
        "purpose": "Mục đích chẩn đoán"
      }}
    ],
    "clinical_guidelines_summary": "Tóm lược phác đồ điều trị chuẩn theo hướng dẫn y khoa"
  }},
  "doctor": "{doctor_name}"
}}

QUY TẮC BẮT BUỘC:
- Dữ liệu trung thực bám sát nội dung âm thanh.
- Nếu không nghe rõ thông tin nào, để chuỗi rỗng "".
- Với thuốc, nếu không có thuốc nào được kê, prescription trả về [].
- Phải trả về JSON hoàn chỉnh, đóng ngoặc đầy đủ.
"""


def analyze_audio(client, model_id, audio_data, mime_type, doctor_name):
    """
    Phân tích file âm thanh buổi khám bằng Gemini API:
    Thực hiện nhận dạng giọng nói (ASR) + Trích xuất bệnh án SOAP + Đánh giá CDSS.
    """
    prompt = build_clinical_prompt(doctor_name)
    models_to_try = [model_id] + [m for m in FALLBACK_MODELS if m != model_id]

    last_error = None
    for model in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=[
                        prompt,
                        types.Part.from_bytes(data=audio_data, mime_type=mime_type)
                    ]
                )
                raw_text = response.text
                parsed = extract_json(raw_text)
                if not parsed:
                    return None, raw_text

                # Chuẩn hóa dữ liệu
                normalized = normalize_medical_record(parsed)

                # Chạy bổ trợ CDSS Rule Engine để đảm bảo 100% không bỏ sót tương tác thuốc nguy hiểm
                rx = normalized.get("soap", {}).get("plan", {}).get("prescription", [])
                enriched_cdss = run_cdss_analysis(normalized, rx, client, model)
                normalized["cdss"] = enriched_cdss

                return normalized, raw_text

            except Exception as e:
                last_error = str(e)
                if "429" in last_error or "RESOURCE_EXHAUSTED" in last_error:
                    if attempt == 0:
                        time.sleep(5)
                        continue
                    break
                if "404" in last_error or "NOT_FOUND" in last_error:
                    break
                # Lỗi kết nối hoặc lỗi khác
                break

    raise RuntimeError(
        f"Không thể kết nối đến mô hình AI hoặc API quota đã hết hạn.\n"
        f"Chi tiết lỗi: {last_error}"
    )


def consult_cdss_assistant(client, model_id, user_query, patient_context=None):
    """Trợ lý tham vấn lâm sàng tương tác trực tiếp với bác sĩ."""
    context_str = ""
    if patient_context:
        context_str = f"\nBỐI CẢNH BỆNH NHÂN HIỆN TẠI:\n{json.dumps(patient_context, ensure_ascii=False, indent=2)}\n"

    prompt = f"""
Bạn là Chuyên gia Tham vấn Quyết định Lâm sàng (CDSS Clinical Assistant) trong đề tài NCKH y tế.
Hãy trả lời câu hỏi chuyên môn của bác sĩ một cách chính xác, dựa trên bằng chứng (Evidence-Based Medicine),
các phác đồ điều trị của Bộ Y tế Việt Nam và các hiệp hội y khoa quốc tế (AHA/ACC, ADA, KDIGO, GINA, GOLD).

{context_str}

CÂU HỎI CỦA BÁC SĨ:
{user_query}

YÊU CẦU:
- Trả lời ngắn gọn, rõ ràng, gạch đầu dòng các ý chính.
- Nêu rõ cảnh báo an toàn thuốc, liều khuyến cáo và tài liệu tham khảo nếu có.
- Định dạng Markdown đẹp mắt.
"""
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"⚠️ Lỗi kết nối AI: {str(e)}"


# ── BỘ DỮ LIỆU CA LÂM SÀNG MẪU (BENCHMARK & DEMO NCKH) ────────
def get_sample_clinical_cases():
    """
    Cung cấp các ca bệnh lâm sàng chuẩn mực phục vụ trình diễn, kiểm thử
    và đánh giá khoa học trong các buổi nghiệm thu NCKH.
    """
    return [
        {
            "id": "CASE-01",
            "title": "🔴 Ca 1: Tim mạch & Tiêu hóa (Cảnh báo Tương tác thuốc DDI Nguy hiểm)",
            "specialty": "Tim mạch - Tiêu hóa",
            "description": "Bệnh nhân sau can thiệp mạch vành đang dùng Clopidogrel, đi khám vì đau thượng vị và được kê Omeprazole + NSAID.",
            "data": {
                "raw_transcript": (
                    "Bác sĩ: Chào bác Hùng, bác 58 tuổi đúng không ạ? Hôm nay bác thấy trong người thế nào?\n"
                    "Bệnh nhân: Chào bác sĩ, dạo này tôi hay bị đau quặn rát vùng trên rốn, nhất là sau khi ăn, lại còn ợ chua nhiều nữa.\n"
                    "Bác sĩ: Bác có tiền sử bệnh tim mạch gì không bác?\n"
                    "Bệnh nhân: Tôi mới đặt stent mạch vành cách đây 4 tháng, vẫn đang uống thuốc Plavix Clopidogrel đều mỗi ngày theo đơn tim mạch.\n"
                    "Bác sĩ: Được rồi, để tôi kiểm tra huyết áp... Huyết áp của bác là 130/80 mmHg, mạch 76 lần/phút. Bụng ấn đau tức vùng thượng vị, không có đề kháng thành bụng. Tôi chẩn đoán bác bị Viêm loét dạ dày - tá tràng cấp. Tôi sẽ kê cho bác thuốc giảm đau Meloxicam và thuốc giảm tiết acid Omeprazole nhé.\n"
                    "Bệnh nhân: Cảm ơn bác sĩ!"
                ),
                "patient": {
                    "name": "Nguyễn Văn Hùng",
                    "age": "58 tuổi",
                    "gender": "Nam",
                    "address": "Quận Hoàn Kiếm, Hà Nội",
                    "phone": "0912.345.678"
                },
                "soap": {
                    "subjective": {
                        "chief_complaint": "Đau rát vùng thượng vị, ợ hơi, ợ chua nhiều",
                        "history_of_illness": "Bệnh khởi phát 1 tuần nay, đau cồn cào rát bỏng vùng trên rốn tăng sau ăn, kèm ợ chua",
                        "medical_history": "Đặt Stent mạch vành 4 tháng trước, đang dùng Clopidogrel 75mg/ngày",
                        "allergies": "Không ghi nhận"
                    },
                    "objective": {
                        "vital_signs": {
                            "blood_pressure": "130/80 mmHg",
                            "heart_rate": "76 bpm",
                            "temperature": "36.8 °C",
                            "spo2": "98%",
                            "respiratory_rate": "18 lần/phút"
                        },
                        "physical_exam": "Bụng mềm, ấn đau tức điểm thượng vị, không có phản ứng thành bụng, tim đều, phổi thông khí rõ"
                    },
                    "assessment": {
                        "primary_diagnosis": "Viêm loét dạ dày - tá tràng trên bệnh nhân Đặt stent mạch vành",
                        "icd10": "K29.5 / I25.1",
                        "differential_diagnosis": "Hội chứng vành cấp thể đau ngực không điển hình, Trào ngược dạ dày thực quản (GERD)"
                    },
                    "plan": {
                        "prescription": [
                            {"name": "Clopidogrel (Plavix) 75mg", "dosage": "1 viên/ngày", "quantity": "30 viên", "instruction": "Uống sau bữa ăn sáng (duy trì)"},
                            {"name": "Omeprazole 20mg", "dosage": "1 viên/lần x 2 lần/ngày", "quantity": "28 viên", "instruction": "Uống trước ăn sáng và tối 30 phút"},
                            {"name": "Meloxicam 7.5mg", "dosage": "1 viên/ngày", "quantity": "7 viên", "instruction": "Uống sau ăn no khi đau nhiều"}
                        ],
                        "lab_tests": "Nội soi thực quản - dạ dày - tá tràng dải tần hẹp (NBI), Điện tâm đồ ECG 12 chuyển đạo",
                        "advice": "Ăn thức ăn mềm, tránh đồ chua cay nóng, cà phê, rượu bia. Không tự ý ngưng thuốc tim mạch.",
                        "follow_up": "Tái khám sau 2 tuần hoặc ngay khi có dấu hiệu đi ngoài phân đen, nôn ra máu."
                    }
                },
                "cdss": {
                    "safety_verdict": "DANGER",
                    "drug_interactions": [
                        {
                            "drugs": ["Clopidogrel 75mg", "Omeprazole 20mg"],
                            "severity": "DANGER",
                            "title": "Tương tác cạnh tranh enzyme CYP2C19",
                            "mechanism": "Omeprazole ức chế CYP2C19 làm giảm hoạt hóa Clopidogrel thành chất chuyển hóa có hoạt tính.",
                            "risk": "Làm mất tác dụng chống kết tập tiểu cầu, tăng nguy cơ huyết khối trong stent và tái phát nhồi máu cơ tim.",
                            "recommendation": "ĐỔI Omeprazole sang Pantoprazole 40mg hoặc Rabeprazole 20mg (nhóm PPI ít ảnh hưởng tới CYP2C19)."
                        },
                        {
                            "drugs": ["Clopidogrel 75mg", "Meloxicam 7.5mg"],
                            "severity": "DANGER",
                            "title": "Hiệp đồng tăng nguy cơ xuất huyết tiêu hóa",
                            "mechanism": "Phối hợp thuốc kháng kết tập tiểu cầu với NSAID gây tổn thương niêm mạc và rối loạn đông máu.",
                            "risk": "Xuất huyết tiêu hóa nghiêm trọng và loét thủng dạ dày.",
                            "recommendation": "Ngừng Meloxicam ngay. Thay thế giảm đau bằng Paracetamol liều thông thường."
                        }
                    ],
                    "contraindications": [
                        {
                            "alert": "CẢNH BÁO: Dùng NSAID (Meloxicam) trên bệnh nhân có tiền sử bệnh tim mạch thiếu máu cục bộ",
                            "risk": "Tăng nguy cơ biến cố tim mạch bất lợi (theo cảnh báo FDA đối với nhóm NSAID).",
                            "recommendation": "Tránh dùng tất cả các thuốc NSAID ở bệnh nhân sau hội chứng vành cấp."
                        }
                    ],
                    "differential_suggestions": [
                        {
                            "condition": "Thiếu máu cơ tim vùng hoành (vùng dưới)",
                            "probability": "Cần loại trừ khẩn cấp",
                            "rationale": "Cơn đau vùng thượng vị ở bệnh nhân có tiền sử bệnh mạch vành có thể là biểu hiện của nhồi máu cơ tim thành dưới."
                        }
                    ],
                    "recommended_tests": [
                        {
                            "test": "Điện tâm đồ (ECG 12 chuyển đạo)",
                            "purpose": "Loại trừ thiếu máu cơ tim cấp vùng dưới."
                        },
                        {
                            "test": "Nội soi dạ dày tá tràng",
                            "purpose": "Xác định mức độ tổn thương loét niêm mạc."
                        }
                    ],
                    "clinical_guidelines_summary": (
                        "Theo Khuyến cáo của Hội Tim mạch Việt Nam và Trường Môn Tim mạch Hoa Kỳ (ACC): "
                        "Bệnh nhân đang dùng Clopidogrel cần bảo vệ dạ dày bằng Pantoprazole thay vì Omeprazole/Esomeprazole."
                    )
                },
                "doctor": "BS. Nguyễn Văn A"
            }
        },
        {
            "id": "CASE-02",
            "title": "🟡 Ca 2: Hô hấp & Nhi khoa (Cảnh báo Chống chỉ định Độ tuổi & Dị ứng)",
            "specialty": "Hô hấp - Nhi khoa",
            "description": "Bé 10 tuổi bị ho sốt, mẹ có tiền sử bé dị ứng Penicillin nhưng bác sĩ kê Augmentin và Aspirin hạ sốt.",
            "data": {
                "raw_transcript": (
                    "Bác sĩ: Chào chị, cháu tên là gì và năm nay mấy tuổi rồi chị?\n"
                    "Bệnh nhân: Dạ cháu tên Trần Bảo An, năm nay cháu 10 tuổi bác sĩ ạ.\n"
                    "Bác sĩ: Cháu bị làm sao thế chị?\n"
                    "Bệnh nhân: Cháu bị ho nhiều, có đờm vàng đặc, sốt liên tục 2 ngày nay khoảng 38 độ rưỡi, thở hơi khò khè. Hồi nhỏ cháu từng bị nổi mề đay khó thở khi uống thuốc Amoxicillin đấy bác sĩ.\n"
                    "Bác sĩ: À vâng, để tôi nghe phổi cho cháu... Phổi có ít ran ẩm rải rác hai phế trường, họng đỏ có mủ ở amidan. Tôi kê cho cháu Augmentin kháng sinh và Aspirin để hạ sốt nhé.\n"
                    "Bệnh nhân: Vâng nhờ bác sĩ kê thuốc giúp cháu."
                ),
                "patient": {
                    "name": "Trần Bảo An",
                    "age": "10 tuổi",
                    "gender": "Nữ",
                    "address": "Quận Hoàn Kiếm, Hà Nội",
                    "phone": "0988.776.655"
                },
                "soap": {
                    "subjective": {
                        "chief_complaint": "Ho có đờm, sốt 38.5°C 2 ngày nay",
                        "history_of_illness": "Bé sốt 2 ngày, ho đờm vàng đặc tăng về đêm, mệt mỏi, ăn uống kém",
                        "medical_history": "Không có bệnh nền mạn tính",
                        "allergies": "Dị ứng Penicillin / Amoxicillin (từng bị mề đay khó thở)"
                    },
                    "objective": {
                        "vital_signs": {
                            "blood_pressure": "100/65 mmHg",
                            "heart_rate": "102 bpm",
                            "temperature": "38.5 °C",
                            "spo2": "97%",
                            "respiratory_rate": "22 lần/phút"
                        },
                        "physical_exam": "Họng sung huyết đỏ, hai amidan sưng to độ II có giả mạc mủ rải rác. Phổi nghe ran ẩm rải rác phế trường đáy phổi."
                    },
                    "assessment": {
                        "primary_diagnosis": "Viêm amidan hốc mủ / Viêm phế quản cấp",
                        "icd10": "J03.9 / J20.9",
                        "differential_diagnosis": "Viêm phổi mắc phải cộng đồng ở trẻ em, Nhiễm virus hợp bào hô hấp (RSV)"
                    },
                    "plan": {
                        "prescription": [
                            {"name": "Augmentin 625mg (Amoxicillin + Clavulanate)", "dosage": "1 viên x 2 lần/ngày", "quantity": "14 viên", "instruction": "Uống ngay đầu bữa ăn"},
                            {"name": "Aspirin 500mg", "dosage": "1/2 viên khi sốt > 38.5°C", "quantity": "10 viên", "instruction": "Uống sau ăn khi sốt cao"}
                        ],
                        "lab_tests": "Công thức máu (CBC), CRP định lượng, X-quang phổi thẳng",
                        "advice": "Uống nhiều nước ấm, súc họng bằng nước muối sinh lý, theo dõi sát nhiệt độ.",
                        "follow_up": "Khám lại sau 3 ngày hoặc ngay khi sốt cao không hạ, thở co rút lồng ngực."
                    }
                },
                "cdss": {
                    "safety_verdict": "DANGER",
                    "drug_interactions": [],
                    "contraindications": [
                        {
                            "alert": "CHỐNG CHỈ ĐỊNH TUYỆT ĐỐI: Aspirin ở trẻ em dưới 16 tuổi",
                            "risk": "Nguy cơ cao gây Hội chứng Reye dẫn đến suy gan cấp và phù não tử vong.",
                            "recommendation": "NGỪNG NGAY Aspirin. Thay thế bằng Paracetamol (10-15mg/kg mỗi 4-6h) để hạ sốt an toàn."
                        },
                        {
                            "alert": "CẢNH BÁO NGUY HIỂM: Kê Augmentin khi bệnh nhân có tiền sử dị ứng Amoxicillin/Penicillin",
                            "risk": "Augmentin chứa Amoxicillin, nguy cơ cao kích hoạt sốc phản vệ type I đe dọa tính mạng.",
                            "recommendation": "ĐỔI sang nhóm Macrolide (Azithromycin 10mg/kg/ngày hoặc Clarithromycin) hoặc Cefuroxime (nếu dị ứng nhẹ)."
                        }
                    ],
                    "differential_suggestions": [
                        {
                            "condition": "Viêm phổi thùy ở trẻ em",
                            "probability": "Trung bình",
                            "rationale": "Cần chụp X-quang ngực để loại trừ đông đặc nhu mô phổi khi nghe có ran ẩm."
                        }
                    ],
                    "recommended_tests": [
                        {
                            "test": "X-quang ngực thẳng (Chest X-Ray)",
                            "purpose": "Loại trừ tổn thương viêm phổi thùy."
                        },
                        {
                            "test": "Công thức máu (CBC) & CRP",
                            "purpose": "Đánh giá mức độ nhiễm khuẩn."
                        }
                    ],
                    "clinical_guidelines_summary": "Khuyến cáo Hướng dẫn Nhi khoa Bộ Y tế: Không dùng Aspirin hạ sốt cho trẻ em do nguy cơ Hội chứng Reye."
                },
                "doctor": "BS. Nguyễn Văn A"
            }
        },
        {
            "id": "CASE-03",
            "title": "🟢 Ca 3: Tim mạch & Tăng huyết áp (Đơn thuốc Chuẩn phác đồ An toàn)",
            "specialty": "Tim mạch - Nội tổng quát",
            "description": "Bệnh nhân nữ 64 tuổi tăng huyết áp độ 2, được kê đơn phối hợp chuẩn Amlodipine + Perindopril theo khuyến cáo Bộ Y tế.",
            "data": {
                "raw_transcript": (
                    "Bác sĩ: Chào bác Lan, 64 tuổi. Hôm nay bác đến khám vì vấn đề gì ạ?\n"
                    "Bệnh nhân: Chào bác sĩ, tôi dạo này hay bị váng đầu, nặng gáy vào buổi sáng, đo huyết áp ở nhà thấy toàn 160 trên 95.\n"
                    "Bác sĩ: Bác có đang uống thuốc hạ áp nào không?\n"
                    "Bệnh nhân: Trước tôi có uống một loại viên tròn nhỏ nhưng hết thuốc nửa tháng nay tôi quên mua lại.\n"
                    "Bác sĩ: Huyết áp hiện tại đo tại phòng khám của bác là 165/95 mmHg, nhịp tim 78 nhịp/phút. Tim đều, phổi không ran. Bác bị Tăng huyết áp nguyên phát độ 2. Tôi sẽ kê cho bác phác đồ phối hợp liều thấp Amlodipine và Perindopril để kiểm soát huyết áp ổn định suốt 24 giờ nhé.\n"
                    "Bệnh nhân: Vâng bác sĩ, uống thuốc này có cần kiêng khem gì không ạ?\n"
                    "Bác sĩ: Bác nhớ ăn nhạt, giảm muối dưới 5 gam mỗi ngày và tập thể dục nhẹ nhàng đều đặn."
                ),
                "patient": {
                    "name": "Lê Thị Lan",
                    "age": "64 tuổi",
                    "gender": "Nữ",
                    "address": "Quận Hoàn Kiếm, Hà Nội",
                    "phone": "0903.112.233"
                },
                "soap": {
                    "subjective": {
                        "chief_complaint": "Đau đầu váng gáy, huyết áp tăng cao 160-165 mmHg",
                        "history_of_illness": "Bệnh nhân tăng huyết áp 3 năm nay, bỏ thuốc 2 tuần, gần đây đau nặng đầu vùng chẩm buổi sáng",
                        "medical_history": "Tăng huyết áp nguyên phát, Rối loạn lipid máu",
                        "allergies": "Không ghi nhận"
                    },
                    "objective": {
                        "vital_signs": {
                            "blood_pressure": "165/95 mmHg",
                            "heart_rate": "78 bpm",
                            "temperature": "36.7 °C",
                            "spo2": "99%",
                            "respiratory_rate": "16 lần/phút"
                        },
                        "physical_exam": "Tim đều rõ, T1 T2 nghe rõ không âm thổi bệnh lý. Phổi không ran. Chi dưới không phù."
                    },
                    "assessment": {
                        "primary_diagnosis": "Tăng huyết áp nguyên phát độ 2 (theo Hội Tim mạch học Việt Nam)",
                        "icd10": "I10",
                        "differential_diagnosis": "Tăng huyết áp thứ phát do bệnh mạch thận hoặc u tủy thượng thận"
                    },
                    "plan": {
                        "prescription": [
                            {"name": "Amlodipine 5mg", "dosage": "1 viên/ngày", "quantity": "30 viên", "instruction": "Uống sau ăn sáng"},
                            {"name": "Perindopril 5mg (Coversyl)", "dosage": "1 viên/ngày", "quantity": "30 viên", "instruction": "Uống sáng trước ăn"},
                            {"name": "Atorvastatin 10mg", "dosage": "1 viên/ngày", "quantity": "30 viên", "instruction": "Uống trước khi đi ngủ"}
                        ],
                        "lab_tests": "Sinh hóa máu: Đường huyết đói, HbA1c, Creatinine, eGFR, Men gan, Bilan lipid máu; Tổng phân tích nước tiểu tìm đạm niệu; Điện tâm đồ",
                        "advice": "Hạn chế muối (<5g/ngày), hạn chế mỡ động vật, duy trì đi bộ 30 phút/ngày. Đo và ghi nhật ký huyết áp tại nhà.",
                        "follow_up": "Tái khám sau 1 tháng để đánh giá hiệu quả hạ áp và chức năng thận."
                    }
                },
                "cdss": {
                    "safety_verdict": "SAFE",
                    "drug_interactions": [],
                    "contraindications": [],
                    "differential_suggestions": [
                        {
                            "condition": "Tăng huyết áp thứ phát do hẹp động mạch thận",
                            "probability": "Thấp",
                            "rationale": "Cần theo dõi nếu huyết áp kháng trị sau khi dùng 3 thuốc phối hợp."
                        }
                    ],
                    "recommended_tests": [
                        {
                            "test": "Điện giải đồ (Na+, K+, Cl-)",
                            "purpose": "Đánh giá mức kali máu cơ bản khi bắt đầu dùng thuốc ức chế men chuyển (Perindopril)."
                        },
                        {
                            "test": "Creatinine và eGFR",
                            "purpose": "Kiểm tra chức năng lọc của cầu thận."
                        }
                    ],
                    "clinical_guidelines_summary": (
                        "Đơn thuốc hoàn toàn phù hợp với Khuyến cáo điều trị Tăng huyết áp của VNHA/VSH 2022 và ESC 2024: "
                        "Ưu tiên phối hợp đôi (Thuốc chẹn kênh Canxi + Thuốc ức chế men chuyển/thụ thể) ngay từ đầu cho Tăng huyết áp độ 2."
                    )
                },
                "doctor": "BS. Nguyễn Văn A"
            }
        }
    ]
