"""
Reference structures for healthcare blockchain records.
"""

# Example of a medical record structure stored on the blockchain
medical_record = {
    "type": "MEDICAL_RECORD",
    "patient_id": "fe3d9c724c7d20a949112d0542114e08f7842773cdb0322889fb3e29f1a1",
    "doctor_id": "af911c61b8cdf7d88f5280fc312c62ec0bfd89567525f71d9a094b284f34",
    "record_type": "diagnostic_report",
    "data": "encrypted-data-here",  # Encrypted in the actual blockchain
    "timestamp": 1632145890.327145,
    "access_list": [
        "fe3d9c724c7d20a949112d0542114e08f7842773cdb0322889fb3e29f1a1",  # patient
        "af911c61b8cdf7d88f5280fc312c62ec0bfd89567525f71d9a094b284f34",  # doctor
    ],
}

# Example of decrypted medical data structure (varies by record_type)
diagnostic_report_data = {
    "diagnosis": "Type 2 Diabetes Mellitus",
    "icd10_code": "E11.9",
    "description": "Patient presents with elevated blood glucose levels...",
    "treatment_plan": "Diet modification, exercise program, and oral medication...",
    "follow_up": "3 months",
    "attachments": ["lab_result_id_123"],
}

lab_result_data = {
    "test_name": "Comprehensive Metabolic Panel",
    "test_date": "2023-09-15T14:30:00",
    "results": [
        {
            "component": "Glucose",
            "value": 142,
            "unit": "mg/dL",
            "reference_range": "70-99",
            "flag": "H",  # H for High, L for Low, N for Normal
        },
        {
            "component": "Creatinine",
            "value": 0.8,
            "unit": "mg/dL",
            "reference_range": "0.6-1.2",
            "flag": "N",
        },
        # Additional components...
    ],
    "laboratory": "LabCorp",
    "notes": "Patient was fasting for 12 hours prior to blood draw.",
}

# Example of a patient consent record
consent_record = {
    "type": "MEDICAL_RECORD",
    "patient_id": "fe3d9c724c7d20a949112d0542114e08f7842773cdb0322889fb3e29f1a1",
    "doctor_id": "fe3d9c724c7d20a949112d0542114e08f7842773cdb0322889fb3e29f1a1",  # Self (patient)
    "record_type": "patient_consent",
    "data": {  # Would be encrypted in the actual blockchain
        "action": "grant",
        "provider_id": "5280fc312c62ec0bfd89567525f71d9a094b284f34af911c61b8cdf7d8f",
        "record_types": ["diagnostic_report", "lab_result"],
        "timestamp": 1632145890.327145,
        "expiration": 1663681890.327145,  # Optional expiration timestamp
    },
    "timestamp": 1632145890.327145,
    "access_list": [
        "fe3d9c724c7d20a949112d0542114e08f7842773cdb0322889fb3e29f1a1",  # patient
        "5280fc312c62ec0bfd89567525f71d9a094b284f34af911c61b8cdf7d8f",  # provider receiving access
    ],
}
