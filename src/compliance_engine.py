from typing import Any


def normalize_boolean(value: Any) -> bool:
    """
    Convert common input values into True or False.
    """

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() in {
            "yes",
            "true",
            "1",
            "available",
            "completed",
            "compliant",
        }

    return bool(value)


def calculate_compliance_score(compliance_data: dict) -> dict:
    """
    Calculate the compliance and regulatory readiness score
    of a FinTech startup.

    Parameters
    ----------
    compliance_data : dict
        Dictionary containing compliance-related startup information.

    Returns
    -------
    dict
        Compliance score, risk level, category scores,
        warnings and positive findings.
    """

    warnings = []
    positive_findings = []

    # --------------------------------------------------
    # 1. Regulatory Readiness – 25 points
    # --------------------------------------------------

    regulatory_score = 0

    regulator_identified = normalize_boolean(
        compliance_data.get("regulator_identified", False)
    )

    regulatory_registration = normalize_boolean(
        compliance_data.get("regulatory_registration", False)
    )

    required_licenses = normalize_boolean(
        compliance_data.get("required_licenses", False)
    )

    regulatory_penalties = int(
        compliance_data.get("regulatory_penalties", 0) or 0
    )

    if regulator_identified:
        regulatory_score += 5
        positive_findings.append(
            "The applicable financial regulator has been identified."
        )
    else:
        warnings.append(
            "The startup has not clearly identified its applicable regulator."
        )

    if regulatory_registration:
        regulatory_score += 10
        positive_findings.append(
            "Regulatory registration is available."
        )
    else:
        warnings.append(
            "Required regulatory registration has not been confirmed."
        )

    if required_licenses:
        regulatory_score += 10
        positive_findings.append(
            "The startup has confirmed the required operating licences."
        )
    else:
        warnings.append(
            "Required operating licences have not been confirmed."
        )

    if regulatory_penalties > 0:
        regulatory_score -= min(regulatory_penalties * 5, 15)
        warnings.append(
            f"The startup has reported {regulatory_penalties} "
            "regulatory penalty or enforcement incident(s)."
        )

    regulatory_score = max(0, min(25, regulatory_score))

    # --------------------------------------------------
    # 2. KYC and AML – 20 points
    # --------------------------------------------------

    kyc_implemented = normalize_boolean(
        compliance_data.get("kyc_implemented", False)
    )

    aml_implemented = normalize_boolean(
        compliance_data.get("aml_implemented", False)
    )

    transaction_monitoring = normalize_boolean(
        compliance_data.get("transaction_monitoring", False)
    )

    suspicious_activity_process = normalize_boolean(
        compliance_data.get("suspicious_activity_process", False)
    )

    kyc_aml_score = 0

    if kyc_implemented:
        kyc_aml_score += 5
        positive_findings.append(
            "A customer identity verification process is implemented."
        )
    else:
        warnings.append(
            "A proper KYC process has not been confirmed."
        )

    if aml_implemented:
        kyc_aml_score += 5
        positive_findings.append(
            "AML controls are implemented."
        )
    else:
        warnings.append(
            "AML controls have not been confirmed."
        )

    if transaction_monitoring:
        kyc_aml_score += 5
        positive_findings.append(
            "The startup monitors financial transactions."
        )
    else:
        warnings.append(
            "Automated or manual transaction monitoring is missing."
        )

    if suspicious_activity_process:
        kyc_aml_score += 5
        positive_findings.append(
            "A suspicious-activity handling process is available."
        )
    else:
        warnings.append(
            "No suspicious-activity review process was confirmed."
        )

    # --------------------------------------------------
    # 3. Data Security – 25 points
    # --------------------------------------------------

    data_encryption = normalize_boolean(
        compliance_data.get("data_encryption", False)
    )

    security_audit = normalize_boolean(
        compliance_data.get("security_audit", False)
    )

    pci_dss_compliant = normalize_boolean(
        compliance_data.get("pci_dss_compliant", False)
    )

    access_controls = normalize_boolean(
        compliance_data.get("access_controls", False)
    )

    incident_response_plan = normalize_boolean(
        compliance_data.get("incident_response_plan", False)
    )

    security_score = 0

    if data_encryption:
        security_score += 5
        positive_findings.append(
            "Sensitive data is protected using encryption."
        )
    else:
        warnings.append(
            "Data encryption has not been confirmed."
        )

    if security_audit:
        security_score += 5
        positive_findings.append(
            "A security audit has been completed."
        )
    else:
        warnings.append(
            "No recent security audit was reported."
        )

    if pci_dss_compliant:
        security_score += 5
        positive_findings.append(
            "Payment security compliance has been confirmed."
        )
    else:
        warnings.append(
            "Payment security compliance has not been confirmed."
        )

    if access_controls:
        security_score += 5
        positive_findings.append(
            "Internal access controls are implemented."
        )
    else:
        warnings.append(
            "Internal access controls are not clearly defined."
        )

    if incident_response_plan:
        security_score += 5
        positive_findings.append(
            "A security incident response plan is available."
        )
    else:
        warnings.append(
            "A security incident response plan is missing."
        )

    # --------------------------------------------------
    # 4. Fraud Prevention – 15 points
    # --------------------------------------------------

    fraud_detection = normalize_boolean(
        compliance_data.get("fraud_detection", False)
    )

    fraud_team = normalize_boolean(
        compliance_data.get("fraud_team", False)
    )

    fraud_incidents = int(
        compliance_data.get("fraud_incidents", 0) or 0
    )

    fraud_score = 0

    if fraud_detection:
        fraud_score += 8
        positive_findings.append(
            "A fraud-detection system is implemented."
        )
    else:
        warnings.append(
            "No fraud-detection system was confirmed."
        )

    if fraud_team:
        fraud_score += 7
        positive_findings.append(
            "A dedicated fraud or risk-management function exists."
        )
    else:
        warnings.append(
            "There is no dedicated fraud or risk-management function."
        )

    if fraud_incidents > 0:
        fraud_score -= min(fraud_incidents * 2, 10)
        warnings.append(
            f"The startup reported {fraud_incidents} fraud incident(s)."
        )

    fraud_score = max(0, min(15, fraud_score))

    # --------------------------------------------------
    # 5. Privacy and Legal Controls – 15 points
    # --------------------------------------------------

    privacy_policy = normalize_boolean(
        compliance_data.get("privacy_policy", False)
    )

    customer_consent = normalize_boolean(
        compliance_data.get("customer_consent", False)
    )

    data_retention_policy = normalize_boolean(
        compliance_data.get("data_retention_policy", False)
    )

    data_breaches = int(
        compliance_data.get("data_breaches", 0) or 0
    )

    privacy_score = 0

    if privacy_policy:
        privacy_score += 5
        positive_findings.append(
            "A formal privacy policy is available."
        )
    else:
        warnings.append(
            "A formal privacy policy is missing."
        )

    if customer_consent:
        privacy_score += 5
        positive_findings.append(
            "Customer consent is collected before using personal data."
        )
    else:
        warnings.append(
            "Customer consent procedures have not been confirmed."
        )

    if data_retention_policy:
        privacy_score += 5
        positive_findings.append(
            "A data-retention policy is documented."
        )
    else:
        warnings.append(
            "A data-retention policy is missing."
        )

    if data_breaches > 0:
        privacy_score -= min(data_breaches * 5, 15)
        warnings.append(
            f"The startup reported {data_breaches} historical data breach(es)."
        )

    privacy_score = max(0, min(15, privacy_score))

    # --------------------------------------------------
    # Overall score
    # --------------------------------------------------

    total_score = round(
        regulatory_score
        + kyc_aml_score
        + security_score
        + fraud_score
        + privacy_score,
        2,
    )

    if total_score >= 85:
        risk_level = "Low Risk"
        compliance_status = "Strong Compliance Readiness"

    elif total_score >= 70:
        risk_level = "Moderate Risk"
        compliance_status = "Generally Compliant – Further Verification Required"

    elif total_score >= 50:
        risk_level = "High Risk"
        compliance_status = "Major Compliance Gaps Identified"

    else:
        risk_level = "Critical Risk"
        compliance_status = "Not Ready for Investment Review"

    return {
        "compliance_score": total_score,
        "risk_level": risk_level,
        "compliance_status": compliance_status,
        "category_scores": {
            "Regulatory Readiness": regulatory_score,
            "KYC and AML": kyc_aml_score,
            "Data Security": security_score,
            "Fraud Prevention": fraud_score,
            "Privacy and Legal": privacy_score,
        },
        "category_max_scores": {
            "Regulatory Readiness": 25,
            "KYC and AML": 20,
            "Data Security": 25,
            "Fraud Prevention": 15,
            "Privacy and Legal": 15,
        },
        "warnings": warnings,
        "positive_findings": positive_findings,
    }