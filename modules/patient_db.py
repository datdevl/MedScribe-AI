import sqlite3
import json
import os
import time

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "patients.db")


def _get_conn():
    """Khởi tạo kết nối SQLite và tự động nâng cấp schema nếu cần."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Tạo bảng nếu chưa tồn tại
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL DEFAULT '',
            age TEXT DEFAULT '',
            gender TEXT DEFAULT '',
            address TEXT DEFAULT '',
            symptoms TEXT DEFAULT '',
            examination TEXT DEFAULT '',
            diagnosis TEXT DEFAULT '',
            prescription TEXT DEFAULT '[]',
            advice TEXT DEFAULT '',
            doctor TEXT DEFAULT '',
            clinic_name TEXT DEFAULT '',
            clinic_addr TEXT DEFAULT '',
            clinic_phone TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime'))
        )
    """)
    conn.commit()

    # Kiểm tra và tự động thêm các cột phục vụ NCKH (SOAP, ASR Transcript, CDSS)
    cursor = conn.execute("PRAGMA table_info(patients)")
    existing_cols = {col[1] for col in cursor.fetchall()}

    new_columns = [
        ("raw_transcript", "TEXT DEFAULT ''"),
        ("soap_subjective", "TEXT DEFAULT ''"),
        ("soap_objective", "TEXT DEFAULT ''"),
        ("soap_assessment", "TEXT DEFAULT ''"),
        ("soap_plan", "TEXT DEFAULT ''"),
        ("icd10_code", "TEXT DEFAULT ''"),
        ("vital_signs", "TEXT DEFAULT ''"),
        ("cdss_analysis", "TEXT DEFAULT '{}'"),
    ]

    for col_name, col_def in new_columns:
        if col_name not in existing_cols:
            try:
                conn.execute(f"ALTER TABLE patients ADD COLUMN {col_name} {col_def}")
                conn.commit()
            except Exception:
                pass

    return conn


def save_patient(data, clinic_info=None):
    """Lưu hồ sơ bệnh án mới vào CSDL."""
    conn = _get_conn()
    clinic_info = clinic_info or {}

    patient = data.get("patient", {})
    soap = data.get("soap", {})
    subj = soap.get("subjective", {})
    obj = soap.get("objective", {})
    ass = soap.get("assessment", {})
    plan = soap.get("plan", {})
    cdss = data.get("cdss", {})

    # Giá trị tương thích ngược
    symptoms = subj.get("chief_complaint", "") or subj.get("history_of_illness", "")
    examination = obj.get("physical_exam", "")
    diagnosis = ass.get("primary_diagnosis", "")
    prescription_list = plan.get("prescription", data.get("prescription", []))
    advice = plan.get("advice", data.get("advice", ""))
    doctor = data.get("doctor", "")

    cursor = conn.execute("""
        INSERT INTO patients (
            name, age, gender, address, symptoms, examination,
            diagnosis, prescription, advice, doctor,
            clinic_name, clinic_addr, clinic_phone,
            raw_transcript, soap_subjective, soap_objective,
            soap_assessment, soap_plan, icd10_code, vital_signs, cdss_analysis
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        patient.get("name", ""),
        patient.get("age", ""),
        patient.get("gender", ""),
        patient.get("address", ""),
        symptoms,
        examination,
        diagnosis,
        json.dumps(prescription_list, ensure_ascii=False),
        advice,
        doctor,
        clinic_info.get("clinic_name", ""),
        clinic_info.get("clinic_addr", ""),
        clinic_info.get("clinic_phone", ""),
        data.get("raw_transcript", ""),
        json.dumps(subj, ensure_ascii=False),
        json.dumps(obj, ensure_ascii=False),
        json.dumps(ass, ensure_ascii=False),
        json.dumps(plan, ensure_ascii=False),
        ass.get("icd10", ""),
        json.dumps(obj.get("vital_signs", {}), ensure_ascii=False),
        json.dumps(cdss, ensure_ascii=False),
    ))
    conn.commit()
    pid = cursor.lastrowid
    conn.close()
    return pid


def update_patient(pid, data, clinic_info=None):
    """Cập nhật hồ sơ bệnh án đã có."""
    conn = _get_conn()
    clinic_info = clinic_info or {}

    patient = data.get("patient", {})
    soap = data.get("soap", {})
    subj = soap.get("subjective", {})
    obj = soap.get("objective", {})
    ass = soap.get("assessment", {})
    plan = soap.get("plan", {})
    cdss = data.get("cdss", {})

    symptoms = subj.get("chief_complaint", "") or subj.get("history_of_illness", "")
    examination = obj.get("physical_exam", "")
    diagnosis = ass.get("primary_diagnosis", "")
    prescription_list = plan.get("prescription", data.get("prescription", []))
    advice = plan.get("advice", data.get("advice", ""))
    doctor = data.get("doctor", "")

    conn.execute("""
        UPDATE patients SET
            name=?, age=?, gender=?, address=?, symptoms=?, examination=?,
            diagnosis=?, prescription=?, advice=?, doctor=?, clinic_name=?,
            clinic_addr=?, clinic_phone=?, raw_transcript=?, soap_subjective=?,
            soap_objective=?, soap_assessment=?, soap_plan=?, icd10_code=?,
            vital_signs=?, cdss_analysis=?, updated_at=datetime('now','localtime')
        WHERE id=?
    """, (
        patient.get("name", ""),
        patient.get("age", ""),
        patient.get("gender", ""),
        patient.get("address", ""),
        symptoms,
        examination,
        diagnosis,
        json.dumps(prescription_list, ensure_ascii=False),
        advice,
        doctor,
        clinic_info.get("clinic_name", ""),
        clinic_info.get("clinic_addr", ""),
        clinic_info.get("clinic_phone", ""),
        data.get("raw_transcript", ""),
        json.dumps(subj, ensure_ascii=False),
        json.dumps(obj, ensure_ascii=False),
        json.dumps(ass, ensure_ascii=False),
        json.dumps(plan, ensure_ascii=False),
        ass.get("icd10", ""),
        json.dumps(obj.get("vital_signs", {}), ensure_ascii=False),
        json.dumps(cdss, ensure_ascii=False),
        pid,
    ))
    conn.commit()
    conn.close()


def get_all_patients(search=""):
    """Lấy danh sách tất cả bệnh nhân có hỗ trợ tìm kiếm."""
    conn = _get_conn()
    if search:
        term = f"%{search.strip()}%"
        rows = conn.execute(
            """SELECT * FROM patients
               WHERE name LIKE ? OR diagnosis LIKE ? OR icd10_code LIKE ?
               ORDER BY created_at DESC""",
            (term, term, term)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM patients ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_patient(pid):
    """Lấy thông tin chi tiết một bệnh nhân theo ID."""
    conn = _get_conn()
    row = conn.execute("SELECT * FROM patients WHERE id=?", (pid,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def delete_patient(pid):
    """Xóa hồ sơ bệnh nhân theo ID."""
    conn = _get_conn()
    conn.execute("DELETE FROM patients WHERE id=?", (pid,))
    conn.commit()
    conn.close()


def row_to_medical_data(row):
    """Chuyển đổi một bản ghi SQLite thành cấu trúc JSON chuẩn."""
    if not row:
        return {}

    # Parse prescription
    try:
        prescription = json.loads(row.get("prescription") or "[]")
    except Exception:
        prescription = []

    # Parse SOAP components
    try:
        subj = json.loads(row.get("soap_subjective") or "{}")
    except Exception:
        subj = {"chief_complaint": row.get("symptoms", ""), "history_of_illness": ""}

    try:
        obj = json.loads(row.get("soap_objective") or "{}")
    except Exception:
        obj = {"physical_exam": row.get("examination", "")}

    try:
        ass = json.loads(row.get("soap_assessment") or "{}")
    except Exception:
        ass = {"primary_diagnosis": row.get("diagnosis", ""), "icd10": row.get("icd10_code", "")}

    try:
        plan = json.loads(row.get("soap_plan") or "{}")
    except Exception:
        plan = {"prescription": prescription, "advice": row.get("advice", "")}

    try:
        cdss = json.loads(row.get("cdss_analysis") or "{}")
    except Exception:
        cdss = {}

    # Đảm bảo plan có đơn thuốc
    if "prescription" not in plan or not plan["prescription"]:
        plan["prescription"] = prescription
    if "advice" not in plan or not plan["advice"]:
        plan["advice"] = row.get("advice", "")

    return {
        "raw_transcript": row.get("raw_transcript", ""),
        "patient": {
            "name": row.get("name", ""),
            "age": row.get("age", ""),
            "gender": row.get("gender", ""),
            "address": row.get("address", ""),
            "phone": ""
        },
        "soap": {
            "subjective": subj,
            "objective": obj,
            "assessment": ass,
            "plan": plan
        },
        "cdss": cdss,
        "doctor": row.get("doctor", "")
    }


def get_stats():
    """Thống kê tổng quan số liệu bệnh nhân phục vụ dashboard."""
    conn = _get_conn()
    total = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    today = conn.execute(
        "SELECT COUNT(*) FROM patients WHERE date(created_at)=date('now','localtime')"
    ).fetchone()[0]

    # Đếm số ca có cảnh báo nguy hiểm hoặc chú ý trong CDSS
    warning_count = 0
    try:
        rows = conn.execute("SELECT cdss_analysis FROM patients WHERE cdss_analysis IS NOT NULL").fetchall()
        for r in rows:
            content = r[0] or ""
            if "DANGER" in content or "WARNING" in content:
                warning_count += 1
    except Exception:
        warning_count = 0

    conn.close()
    return {
        "total": total,
        "today": today,
        "warnings": warning_count
    }
