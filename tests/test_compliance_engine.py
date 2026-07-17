from src.compliance_engine import calculate_compliance_score


def test_strong_compliance_profile():
    compliance_data = {
        "regulator_identified": True,
        "regulatory_registration": True,
        "required_licenses": True,
        "regulatory_penalties": 0,
        "kyc_implemented": True,
        "aml_implemented": True,
        "transaction_monitoring": True,
        "suspicious_activity_process": True,
        "data_encryption": True,
        "security_audit": True,
        "pci_dss_compliant": True,
        "access_controls": True,
        "incident_response_plan": True,
        "fraud_detection": True,
        "fraud_team": True,
        "fraud_incidents": 0,
        "privacy_policy": True,
        "customer_consent": True,
        "data_retention_policy": True,
        "data_breaches": 0,
    }

    result = calculate_compliance_score(compliance_data)

    assert result["compliance_score"] == 100
    assert result["risk_level"] == "Low Risk"
    assert result["compliance_status"] == "Strong Compliance Readiness"
    assert len(result["warnings"]) == 0


def test_weak_compliance_profile():
    compliance_data = {
        "regulator_identified": False,
        "regulatory_registration": False,
        "required_licenses": False,
        "regulatory_penalties": 2,
        "kyc_implemented": False,
        "aml_implemented": False,
        "transaction_monitoring": False,
        "suspicious_activity_process": False,
        "data_encryption": False,
        "security_audit": False,
        "pci_dss_compliant": False,
        "access_controls": False,
        "incident_response_plan": False,
        "fraud_detection": False,
        "fraud_team": False,
        "fraud_incidents": 3,
        "privacy_policy": False,
        "customer_consent": False,
        "data_retention_policy": False,
        "data_breaches": 2,
    }

    result = calculate_compliance_score(compliance_data)

    assert result["compliance_score"] == 0
    assert result["risk_level"] == "Critical Risk"
    assert len(result["warnings"]) > 0


def test_partial_compliance_profile():
    compliance_data = {
        "regulator_identified": True,
        "regulatory_registration": True,
        "required_licenses": False,
        "regulatory_penalties": 0,
        "kyc_implemented": True,
        "aml_implemented": True,
        "transaction_monitoring": False,
        "suspicious_activity_process": False,
        "data_encryption": True,
        "security_audit": False,
        "pci_dss_compliant": False,
        "access_controls": True,
        "incident_response_plan": False,
        "fraud_detection": True,
        "fraud_team": False,
        "fraud_incidents": 0,
        "privacy_policy": True,
        "customer_consent": True,
        "data_retention_policy": False,
        "data_breaches": 0,
    }

    result = calculate_compliance_score(compliance_data)

    assert 0 <= result["compliance_score"] <= 100
    assert result["risk_level"] in {
        "Low Risk",
        "Moderate Risk",
        "High Risk",
        "Critical Risk",
    }

    assert len(result["warnings"]) > 0
    assert len(result["positive_findings"]) > 0


def test_missing_values_do_not_crash():
    result = calculate_compliance_score({})

    assert result["compliance_score"] == 0
    assert result["risk_level"] == "Critical Risk"