def validate_prescription_data(prescriptions, patient_info, diagnosis):
    """
    Validates prescriptions and returns a structured result.
    prescriptions: list of dicts with keys ['medication', 'dosage', 'frequency', 'duration']
    patient_info: dict with keys ['age', 'weight', 'allergies', 'conditions']
    diagnosis: string
    """
    result = {
        'overall': 'approved',
        'items': [],
        'recommendations': []
    }

    for p in prescriptions:
        status = 'approved'
        issues = []

        # Example checks
        if not p['medication']:
            issues.append("Medication name missing")
            status = 'rejected'
        if not p['dosage']:
            issues.append("Dosage missing")
            status = 'rejected'

        # Allergy check
        if 'penicillin' in (p['medication'].lower()) and 'penicillin' in patient_info.get('allergies', '').lower():
            issues.append("ALLERGY ALERT: Patient allergic to penicillin")
            status = 'rejected'

        result['items'].append({
            'medication': p['medication'],
            'status': status,
            'message': '. '.join(issues) if issues else "Looks good"
        })

    if any(item['status'] == 'rejected' for item in result['items']):
        result['overall'] = 'rejected'
    elif any(item['status'] == 'warning' for item in result['items']):
        result['overall'] = 'warning'

    return result
