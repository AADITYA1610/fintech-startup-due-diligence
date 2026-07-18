from __future__ import annotations

from typing import Any

from src.compliance_engine import normalize_boolean


# ============================================================
# COMMON RISK UTILITIES
# ============================================================

VALID_SEVERITIES = {
    "Critical",
    "High",
    "Medium",
    "Low",
}


def create_risk_finding(
    category: str,
    title: str,
    description: str,
    severity: str,
    impact: str,
    recommendation: str,
) -> dict[str, str]:
    """
    Create a standard risk finding.

    Every risk identified by the system follows the same structure.
    This makes it easier to display risks on the Streamlit dashboard
    and include them in reports.
    """

    if severity not in VALID_SEVERITIES:
        raise ValueError(
            "Severity must be Critical, High, Medium, or Low."
        )

    return {
        "category": category,
        "title": title,
        "description": description,
        "severity": severity,
        "impact": impact,
        "recommendation": recommendation,
    }


def classify_risk_level(risk_score: float) -> str:
    """
    Convert a numerical risk score into a readable risk level.

    Higher risk score means greater risk.

    0-29.99   -> Low
    30-54.99  -> Medium
    55-74.99  -> High
    75-100    -> Critical
    """

    risk_score = max(0.0, min(float(risk_score), 100.0))

    if risk_score >= 75:
        return "Critical"

    if risk_score >= 55:
        return "High"

    if risk_score >= 30:
        return "Medium"

    return "Low"


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Safely convert a value into a float.
    """

    try:
        if value is None:
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def _safe_int(
    value: Any,
    default: int = 0,
) -> int:
    """
    Safely convert a value into an integer.
    """

    try:
        if value is None:
            return default

        return int(value)

    except (TypeError, ValueError):
        return default


# ============================================================
# FINANCIAL RISK ANALYSIS
# ============================================================

def analyze_financial_risk(
    startup_data: dict[str, Any],
    financial_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Analyse the startup's financial risk.

    Parameters
    ----------
    startup_data:
        Original startup form data.

    financial_result:
        Output returned by calculate_all_financial_metrics().

    Returns
    -------
    dict
        Financial risk score, risk level, findings,
        and positive signals.
    """

    risk_score = 0.0
    findings: list[dict[str, str]] = []
    positive_signals: list[str] = []

    monthly_revenue = _safe_float(
        startup_data.get("monthly_revenue", 0)
    )

    monthly_expenses = _safe_float(
        startup_data.get("monthly_expenses", 0)
    )

    total_debt = _safe_float(
        startup_data.get("total_debt", 0)
    )

    total_equity = _safe_float(
        startup_data.get("total_equity", 0)
    )

    financial_records_available = str(
        startup_data.get(
            "financial_records_available",
            "",
        )
    )

    profit_loss = _safe_float(
        financial_result.get("profit_loss", 0)
    )

    cash_runway_months = financial_result.get(
        "cash_runway_months"
    )

    profit_margin = financial_result.get(
        "profit_margin_percentage"
    )

    current_ratio = financial_result.get(
        "current_ratio"
    )

    debt_to_equity_ratio = financial_result.get(
        "debt_to_equity_ratio"
    )

    ltv_cac_ratio = financial_result.get(
        "ltv_cac_ratio"
    )

    financial_health_score = _safe_float(
        financial_result.get(
            "financial_health_score",
            0,
        )
    )

    # --------------------------------------------------------
    # 1. CASH RUNWAY RISK
    # --------------------------------------------------------

    if cash_runway_months is None:
        positive_signals.append(
            "The startup currently has no net monthly cash burn."
        )

    else:
        cash_runway_months = _safe_float(
            cash_runway_months
        )

        if cash_runway_months < 3:
            risk_score += 35

            findings.append(
                create_risk_finding(
                    category="Financial Risk",
                    title="Critically low cash runway",
                    description=(
                        "The startup has less than three months "
                        "of cash runway based on its current burn rate."
                    ),
                    severity="Critical",
                    impact=(
                        "The startup may face immediate liquidity "
                        "problems and may be unable to continue "
                        "operations without urgent funding."
                    ),
                    recommendation=(
                        "Prepare an immediate funding or cost-reduction "
                        "plan and extend the cash runway before investment."
                    ),
                )
            )

        elif cash_runway_months < 6:
            risk_score += 25

            findings.append(
                create_risk_finding(
                    category="Financial Risk",
                    title="Low cash runway",
                    description=(
                        "The startup has less than six months "
                        "of cash runway."
                    ),
                    severity="High",
                    impact=(
                        "A delay in fundraising or revenue growth "
                        "could disrupt business operations."
                    ),
                    recommendation=(
                        "Reduce avoidable expenditure and secure "
                        "additional working capital."
                    ),
                )
            )

        elif cash_runway_months < 12:
            risk_score += 12

            findings.append(
                create_risk_finding(
                    category="Financial Risk",
                    title="Limited cash runway",
                    description=(
                        "The startup has less than twelve months "
                        "of cash runway."
                    ),
                    severity="Medium",
                    impact=(
                        "The startup may become dependent on a new "
                        "funding round within the coming year."
                    ),
                    recommendation=(
                        "Create a fundraising plan and improve "
                        "cash-flow management."
                    ),
                )
            )

        else:
            positive_signals.append(
                "The startup has at least twelve months of cash runway."
            )

    # --------------------------------------------------------
    # 2. PROFITABILITY RISK
    # --------------------------------------------------------

    if monthly_revenue <= 0:
        risk_score += 12

        findings.append(
            create_risk_finding(
                category="Financial Risk",
                title="No current monthly revenue",
                description=(
                    "The startup has not reported any monthly revenue."
                ),
                severity="Medium",
                impact=(
                    "The business remains dependent on existing cash "
                    "or external funding to meet operating expenses."
                ),
                recommendation=(
                    "Validate the revenue model and establish measurable "
                    "revenue-generation milestones."
                ),
            )
        )

    elif profit_loss < 0:
        risk_score += 10

        findings.append(
            create_risk_finding(
                category="Financial Risk",
                title="Monthly operating loss",
                description=(
                    "Monthly expenses are currently higher "
                    "than monthly revenue."
                ),
                severity="Medium",
                impact=(
                    "Continued operating losses will reduce available "
                    "cash and increase funding dependency."
                ),
                recommendation=(
                    "Review operating expenses and define a realistic "
                    "path towards break-even."
                ),
            )
        )

    else:
        positive_signals.append(
            "Monthly revenue currently covers monthly expenses."
        )

    # --------------------------------------------------------
    # 3. PROFIT MARGIN RISK
    # --------------------------------------------------------

    if profit_margin is not None:
        profit_margin = _safe_float(profit_margin)

        if profit_margin < -30:
            risk_score += 15

            findings.append(
                create_risk_finding(
                    category="Financial Risk",
                    title="Severely negative profit margin",
                    description=(
                        "The startup's profit margin is below -30%."
                    ),
                    severity="High",
                    impact=(
                        "The current cost structure may be financially "
                        "unsustainable without rapid revenue improvement."
                    ),
                    recommendation=(
                        "Perform a detailed cost and pricing review "
                        "before further investment."
                    ),
                )
            )

        elif profit_margin < 0:
            risk_score += 8

            findings.append(
                create_risk_finding(
                    category="Financial Risk",
                    title="Negative profit margin",
                    description=(
                        "The startup currently reports a negative "
                        "profit margin."
                    ),
                    severity="Medium",
                    impact=(
                        "The business is not yet generating profit "
                        "from its current revenue."
                    ),
                    recommendation=(
                        "Improve unit economics, pricing, or operating "
                        "efficiency to reduce losses."
                    ),
                )
            )

        elif profit_margin >= 10:
            positive_signals.append(
                "The startup reports a positive profit margin "
                "of at least 10%."
            )

    # --------------------------------------------------------
    # 4. LIQUIDITY RISK
    # --------------------------------------------------------

    if current_ratio is None:
        current_liabilities = _safe_float(
            startup_data.get(
                "current_liabilities",
                0,
            )
        )

        if current_liabilities <= 0:
            positive_signals.append(
                "The startup reports no current liabilities."
            )

    else:
        current_ratio = _safe_float(current_ratio)

        if current_ratio < 0.75:
            risk_score += 15

            findings.append(
                create_risk_finding(
                    category="Financial Risk",
                    title="Severe liquidity weakness",
                    description=(
                        "The current ratio is below 0.75."
                    ),
                    severity="High",
                    impact=(
                        "The startup may struggle to meet its "
                        "short-term financial obligations."
                    ),
                    recommendation=(
                        "Increase liquid assets or reduce short-term "
                        "liabilities before investment."
                    ),
                )
            )

        elif current_ratio < 1:
            risk_score += 8

            findings.append(
                create_risk_finding(
                    category="Financial Risk",
                    title="Current liabilities exceed current assets",
                    description=(
                        "The startup's current ratio is below 1."
                    ),
                    severity="Medium",
                    impact=(
                        "Available current assets may be insufficient "
                        "to cover short-term liabilities."
                    ),
                    recommendation=(
                        "Improve working-capital management and review "
                        "short-term debt obligations."
                    ),
                )
            )

        elif current_ratio >= 1.5:
            positive_signals.append(
                "The startup has a healthy current ratio "
                "of at least 1.5."
            )

    # --------------------------------------------------------
    # 5. DEBT RISK
    # --------------------------------------------------------

    if debt_to_equity_ratio is None:
        if total_debt > 0 and total_equity <= 0:
            risk_score += 15

            findings.append(
                create_risk_finding(
                    category="Financial Risk",
                    title="Debt exists without positive equity",
                    description=(
                        "The startup reports debt but does not report "
                        "positive equity."
                    ),
                    severity="High",
                    impact=(
                        "The capital structure may be unstable and "
                        "creditor exposure may be significant."
                    ),
                    recommendation=(
                        "Verify the capital structure and assess the "
                        "startup's ability to service its debt."
                    ),
                )
            )

        elif total_debt <= 0:
            positive_signals.append(
                "The startup reports no outstanding debt."
            )

    else:
        debt_to_equity_ratio = _safe_float(
            debt_to_equity_ratio
        )

        if debt_to_equity_ratio > 3:
            risk_score += 15

            findings.append(
                create_risk_finding(
                    category="Financial Risk",
                    title="Very high debt-to-equity ratio",
                    description=(
                        "The debt-to-equity ratio is greater than 3."
                    ),
                    severity="High",
                    impact=(
                        "A high level of debt may increase repayment "
                        "pressure and reduce financial flexibility."
                    ),
                    recommendation=(
                        "Review debt repayment obligations and consider "
                        "reducing leverage before investment."
                    ),
                )
            )

        elif debt_to_equity_ratio > 2:
            risk_score += 8

            findings.append(
                create_risk_finding(
                    category="Financial Risk",
                    title="Elevated debt level",
                    description=(
                        "The debt-to-equity ratio is greater than 2."
                    ),
                    severity="Medium",
                    impact=(
                        "The startup may have limited flexibility "
                        "during periods of low revenue."
                    ),
                    recommendation=(
                        "Assess debt servicing capacity and future "
                        "borrowing requirements."
                    ),
                )
            )

        elif debt_to_equity_ratio <= 1.5:
            positive_signals.append(
                "The startup has a manageable debt-to-equity ratio."
            )

    # --------------------------------------------------------
    # 6. UNIT ECONOMICS RISK
    # --------------------------------------------------------

    if ltv_cac_ratio is not None:
        ltv_cac_ratio = _safe_float(ltv_cac_ratio)

        if ltv_cac_ratio < 1:
            risk_score += 10

            findings.append(
                create_risk_finding(
                    category="Financial Risk",
                    title="Unsustainable customer acquisition economics",
                    description=(
                        "Customer acquisition cost is greater than "
                        "customer lifetime value."
                    ),
                    severity="High",
                    impact=(
                        "The startup may lose money when acquiring "
                        "new customers."
                    ),
                    recommendation=(
                        "Reduce customer acquisition cost or improve "
                        "customer lifetime value before scaling."
                    ),
                )
            )

        elif ltv_cac_ratio < 3:
            risk_score += 5

            findings.append(
                create_risk_finding(
                    category="Financial Risk",
                    title="Weak LTV-to-CAC ratio",
                    description=(
                        "The LTV-to-CAC ratio is below the preferred "
                        "level of 3."
                    ),
                    severity="Medium",
                    impact=(
                        "Customer acquisition may not yet provide "
                        "sufficient long-term returns."
                    ),
                    recommendation=(
                        "Improve retention, pricing, or acquisition "
                        "efficiency."
                    ),
                )
            )

        else:
            positive_signals.append(
                "The startup has an LTV-to-CAC ratio of at least 3."
            )

    # --------------------------------------------------------
    # 7. FINANCIAL RECORD QUALITY
    # --------------------------------------------------------

    if financial_records_available == "No Records Available":
        risk_score += 10

        findings.append(
            create_risk_finding(
                category="Financial Risk",
                title="Financial records unavailable",
                description=(
                    "The startup has not provided financial records "
                    "for verification."
                ),
                severity="High",
                impact=(
                    "Reported financial information cannot be "
                    "independently verified."
                ),
                recommendation=(
                    "Request complete financial statements and "
                    "supporting transaction records."
                ),
            )
        )

    elif financial_records_available == "Partial Records Available":
        risk_score += 5

        findings.append(
            create_risk_finding(
                category="Financial Risk",
                title="Incomplete financial records",
                description=(
                    "Only partial financial records are available."
                ),
                severity="Medium",
                impact=(
                    "Important liabilities, expenses, or revenue details "
                    "may not be visible during due diligence."
                ),
                recommendation=(
                    "Obtain complete financial records before making "
                    "a final investment decision."
                ),
            )
        )

    elif financial_records_available == "Audited Records Available":
        positive_signals.append(
            "Audited financial records are available."
        )

    # --------------------------------------------------------
    # 8. OVERALL FINANCIAL HEALTH CHECK
    # --------------------------------------------------------

    if financial_health_score < 25:
        risk_score += 10

        findings.append(
            create_risk_finding(
                category="Financial Risk",
                title="Critical financial health score",
                description=(
                    "The calculated financial health score is below 25."
                ),
                severity="High",
                impact=(
                    "Multiple financial weaknesses may affect "
                    "the startup's sustainability."
                ),
                recommendation=(
                    "Conduct detailed financial due diligence before "
                    "considering investment."
                ),
            )
        )

    elif financial_health_score >= 80:
        positive_signals.append(
            "The startup has an excellent financial health score."
        )

    risk_score = round(
        min(max(risk_score, 0.0), 100.0),
        2,
    )

    return {
        "score": risk_score,
        "level": classify_risk_level(risk_score),
        "findings": findings,
        "positive_signals": positive_signals,
    }


# ============================================================
# COMPLIANCE RISK ANALYSIS
# ============================================================

def analyze_compliance_risk(
    startup_data: dict[str, Any],
    compliance_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert the FinTech compliance assessment into an
    investor-focused compliance risk analysis.

    The compliance engine measures readiness:
        Higher compliance score = better.

    This function measures risk:
        Higher risk score = worse.
    """

    findings: list[dict[str, str]] = []

    positive_signals = list(
        compliance_result.get(
            "positive_findings",
            [],
        )
    )

    compliance_score = _safe_float(
        compliance_result.get(
            "compliance_score",
            0,
        )
    )

    compliance_score = min(
        max(compliance_score, 0.0),
        100.0,
    )

    risk_score = 100.0 - compliance_score

    regulator_identified = normalize_boolean(
        startup_data.get(
            "regulator_identified",
            False,
        )
    )

    regulatory_registration = normalize_boolean(
        startup_data.get(
            "regulatory_registration",
            False,
        )
    )

    required_licenses = normalize_boolean(
        startup_data.get(
            "required_licenses",
            False,
        )
    )

    regulatory_penalties = _safe_int(
        startup_data.get(
            "regulatory_penalties",
            0,
        )
    )

    kyc_implemented = normalize_boolean(
        startup_data.get(
            "kyc_implemented",
            False,
        )
    )

    aml_implemented = normalize_boolean(
        startup_data.get(
            "aml_implemented",
            False,
        )
    )

    transaction_monitoring = normalize_boolean(
        startup_data.get(
            "transaction_monitoring",
            False,
        )
    )

    suspicious_activity_process = normalize_boolean(
        startup_data.get(
            "suspicious_activity_process",
            False,
        )
    )

    data_encryption = normalize_boolean(
        startup_data.get(
            "data_encryption",
            False,
        )
    )

    security_audit = normalize_boolean(
        startup_data.get(
            "security_audit",
            False,
        )
    )

    access_controls = normalize_boolean(
        startup_data.get(
            "access_controls",
            False,
        )
    )

    incident_response_plan = normalize_boolean(
        startup_data.get(
            "incident_response_plan",
            False,
        )
    )

    fraud_detection = normalize_boolean(
        startup_data.get(
            "fraud_detection",
            False,
        )
    )

    fraud_team = normalize_boolean(
        startup_data.get(
            "fraud_team",
            False,
        )
    )

    fraud_incidents = _safe_int(
        startup_data.get(
            "fraud_incidents",
            0,
        )
    )

    privacy_policy = normalize_boolean(
        startup_data.get(
            "privacy_policy",
            False,
        )
    )

    customer_consent = normalize_boolean(
        startup_data.get(
            "customer_consent",
            False,
        )
    )

    data_retention_policy = normalize_boolean(
        startup_data.get(
            "data_retention_policy",
            False,
        )
    )

    data_breaches = _safe_int(
        startup_data.get(
            "data_breaches",
            0,
        )
    )

    # --------------------------------------------------------
    # 1. REGULATORY RISKS
    # --------------------------------------------------------

    if not required_licenses:
        risk_score = max(risk_score, 80)

        findings.append(
            create_risk_finding(
                category="Compliance Risk",
                title="Required operating licences not confirmed",
                description=(
                    "The startup has not confirmed that it possesses "
                    "the licences required for its financial activities."
                ),
                severity="Critical",
                impact=(
                    "The startup may face operating restrictions, "
                    "financial penalties, or suspension of services."
                ),
                recommendation=(
                    "Complete a regulatory licence-gap assessment and "
                    "obtain all required licences before investment."
                ),
            )
        )

    if not regulatory_registration:
        risk_score = max(risk_score, 60)

        findings.append(
            create_risk_finding(
                category="Compliance Risk",
                title="Regulatory registration not confirmed",
                description=(
                    "The required regulatory registration has "
                    "not been confirmed."
                ),
                severity="High",
                impact=(
                    "The startup may not be authorised to conduct "
                    "some regulated financial activities."
                ),
                recommendation=(
                    "Verify registration requirements and obtain "
                    "documentary proof of registration."
                ),
            )
        )

    if not regulator_identified:
        findings.append(
            create_risk_finding(
                category="Compliance Risk",
                title="Applicable regulator not identified",
                description=(
                    "The startup has not clearly identified the "
                    "financial regulator applicable to its operations."
                ),
                severity="High",
                impact=(
                    "Regulatory obligations may be misunderstood "
                    "or overlooked."
                ),
                recommendation=(
                    "Conduct a regulatory applicability assessment "
                    "with qualified legal or compliance professionals."
                ),
            )
        )

    if regulatory_penalties > 0:
        penalty_severity = (
            "Critical"
            if regulatory_penalties >= 3
            else "High"
        )

        minimum_risk = (
            80
            if regulatory_penalties >= 3
            else 65
        )

        risk_score = max(
            risk_score,
            minimum_risk,
        )

        findings.append(
            create_risk_finding(
                category="Compliance Risk",
                title="Regulatory penalties reported",
                description=(
                    f"The startup has reported "
                    f"{regulatory_penalties} regulatory penalty "
                    "or enforcement incident(s)."
                ),
                severity=penalty_severity,
                impact=(
                    "Past enforcement activity may indicate repeated "
                    "compliance failures and may create financial "
                    "or reputational exposure."
                ),
                recommendation=(
                    "Review the cause, financial impact, corrective "
                    "actions, and current status of every incident."
                ),
            )
        )

    # --------------------------------------------------------
    # 2. KYC AND AML RISKS
    # --------------------------------------------------------

    if not kyc_implemented:
        risk_score = max(risk_score, 60)

        findings.append(
            create_risk_finding(
                category="Compliance Risk",
                title="KYC process not confirmed",
                description=(
                    "A customer identity verification process has "
                    "not been confirmed."
                ),
                severity="High",
                impact=(
                    "The startup may onboard fraudulent, prohibited, "
                    "or incorrectly identified customers."
                ),
                recommendation=(
                    "Implement documented KYC procedures before "
                    "expanding customer onboarding."
                ),
            )
        )

    if not aml_implemented:
        risk_score = max(risk_score, 65)

        findings.append(
            create_risk_finding(
                category="Compliance Risk",
                title="AML controls not confirmed",
                description=(
                    "Anti-money-laundering controls have not "
                    "been confirmed."
                ),
                severity="High",
                impact=(
                    "The platform may be exposed to money laundering, "
                    "regulatory action, and reputational damage."
                ),
                recommendation=(
                    "Implement a documented AML programme with "
                    "risk assessment, monitoring, and escalation controls."
                ),
            )
        )

    if not transaction_monitoring:
        findings.append(
            create_risk_finding(
                category="Compliance Risk",
                title="Transaction monitoring unavailable",
                description=(
                    "The startup has not confirmed automated or "
                    "manual monitoring of financial transactions."
                ),
                severity="High",
                impact=(
                    "Suspicious or abnormal financial activity "
                    "may remain undetected."
                ),
                recommendation=(
                    "Introduce risk-based transaction monitoring "
                    "and alert-review procedures."
                ),
            )
        )

    if not suspicious_activity_process:
        findings.append(
            create_risk_finding(
                category="Compliance Risk",
                title="Suspicious-activity process missing",
                description=(
                    "No formal process for reviewing or escalating "
                    "suspicious activity has been confirmed."
                ),
                severity="High",
                impact=(
                    "Potentially illegal activity may not be "
                    "investigated or reported appropriately."
                ),
                recommendation=(
                    "Document suspicious-activity investigation, "
                    "escalation, and reporting procedures."
                ),
            )
        )

    # --------------------------------------------------------
    # 3. DATA SECURITY RISKS
    # --------------------------------------------------------

    if not data_encryption:
        findings.append(
            create_risk_finding(
                category="Compliance Risk",
                title="Data encryption not confirmed",
                description=(
                    "Protection of sensitive customer and financial "
                    "data through encryption has not been confirmed."
                ),
                severity="High",
                impact=(
                    "Sensitive information may be exposed if systems "
                    "or databases are compromised."
                ),
                recommendation=(
                    "Implement encryption for sensitive data "
                    "at rest and in transit."
                ),
            )
        )

    if not security_audit:
        findings.append(
            create_risk_finding(
                category="Compliance Risk",
                title="Security audit not completed",
                description=(
                    "No recent independent or internal security audit "
                    "has been reported."
                ),
                severity="Medium",
                impact=(
                    "Unknown vulnerabilities may remain in the "
                    "startup's systems and processes."
                ),
                recommendation=(
                    "Complete a structured security assessment "
                    "and remediate identified vulnerabilities."
                ),
            )
        )

    if not access_controls:
        findings.append(
            create_risk_finding(
                category="Compliance Risk",
                title="Access controls not confirmed",
                description=(
                    "Internal access-control measures have "
                    "not been clearly defined."
                ),
                severity="High",
                impact=(
                    "Employees or third parties may gain unnecessary "
                    "access to sensitive systems and information."
                ),
                recommendation=(
                    "Implement role-based access control and "
                    "periodic access reviews."
                ),
            )
        )

    if not incident_response_plan:
        findings.append(
            create_risk_finding(
                category="Compliance Risk",
                title="Incident-response plan missing",
                description=(
                    "The startup does not have a confirmed security "
                    "incident-response plan."
                ),
                severity="High",
                impact=(
                    "The startup may respond slowly or inconsistently "
                    "during a cyberattack or data breach."
                ),
                recommendation=(
                    "Create, document, and test a security "
                    "incident-response plan."
                ),
            )
        )

    # --------------------------------------------------------
    # 4. FRAUD RISKS
    # --------------------------------------------------------

    if not fraud_detection:
        findings.append(
            create_risk_finding(
                category="Compliance Risk",
                title="Fraud-detection system unavailable",
                description=(
                    "A fraud-detection mechanism has not been confirmed."
                ),
                severity="High",
                impact=(
                    "Fraudulent transactions or account activity "
                    "may remain undetected."
                ),
                recommendation=(
                    "Introduce fraud rules, alerts, and case-review "
                    "procedures appropriate to the product."
                ),
            )
        )

    if not fraud_team:
        findings.append(
            create_risk_finding(
                category="Compliance Risk",
                title="Dedicated fraud or risk function missing",
                description=(
                    "The startup does not report a dedicated fraud "
                    "or risk-management function."
                ),
                severity="Medium",
                impact=(
                    "Fraud alerts and risk incidents may not receive "
                    "clear ownership or timely action."
                ),
                recommendation=(
                    "Assign responsibility for fraud and risk "
                    "management to qualified personnel."
                ),
            )
        )

    if fraud_incidents > 0:
        fraud_severity = (
            "Critical"
            if fraud_incidents >= 5
            else "High"
        )

        minimum_risk = (
            80
            if fraud_incidents >= 5
            else 60
        )

        risk_score = max(
            risk_score,
            minimum_risk,
        )

        findings.append(
            create_risk_finding(
                category="Compliance Risk",
                title="Historical fraud incidents reported",
                description=(
                    f"The startup has reported "
                    f"{fraud_incidents} fraud incident(s)."
                ),
                severity=fraud_severity,
                impact=(
                    "Repeated fraud incidents may create direct "
                    "financial losses and reduce customer trust."
                ),
                recommendation=(
                    "Review incident causes, financial losses, "
                    "control failures, and remediation evidence."
                ),
            )
        )

    # --------------------------------------------------------
    # 5. PRIVACY AND DATA-BREACH RISKS
    # --------------------------------------------------------

    if not privacy_policy:
        findings.append(
            create_risk_finding(
                category="Compliance Risk",
                title="Privacy policy missing",
                description=(
                    "A formal privacy policy has not been confirmed."
                ),
                severity="Medium",
                impact=(
                    "Customers may not be properly informed about "
                    "the collection and use of personal data."
                ),
                recommendation=(
                    "Publish and maintain a clear privacy policy "
                    "covering all personal-data processing activities."
                ),
            )
        )

    if not customer_consent:
        findings.append(
            create_risk_finding(
                category="Compliance Risk",
                title="Customer consent controls not confirmed",
                description=(
                    "The startup has not confirmed how customer "
                    "consent is collected and recorded."
                ),
                severity="High",
                impact=(
                    "Personal data may be processed without valid "
                    "or demonstrable permission."
                ),
                recommendation=(
                    "Implement auditable customer-consent collection "
                    "and withdrawal mechanisms."
                ),
            )
        )

    if not data_retention_policy:
        findings.append(
            create_risk_finding(
                category="Compliance Risk",
                title="Data-retention policy missing",
                description=(
                    "The startup has not documented how long "
                    "customer and transaction data is retained."
                ),
                severity="Medium",
                impact=(
                    "Data may be retained unnecessarily or deleted "
                    "before legal and operational requirements are met."
                ),
                recommendation=(
                    "Create a documented retention and secure-deletion "
                    "schedule for each major data category."
                ),
            )
        )

    if data_breaches > 0:
        breach_severity = (
            "Critical"
            if data_breaches >= 2
            else "High"
        )

        minimum_risk = (
            85
            if data_breaches >= 2
            else 70
        )

        risk_score = max(
            risk_score,
            minimum_risk,
        )

        findings.append(
            create_risk_finding(
                category="Compliance Risk",
                title="Historical data breach reported",
                description=(
                    f"The startup has reported "
                    f"{data_breaches} historical data breach(es)."
                ),
                severity=breach_severity,
                impact=(
                    "Data breaches may create legal liabilities, "
                    "regulatory action, remediation costs, and "
                    "loss of customer trust."
                ),
                recommendation=(
                    "Review breach investigation reports, affected "
                    "records, notifications, and remediation evidence."
                ),
            )
        )

    # --------------------------------------------------------
    # STRONG COMPLIANCE SIGNAL
    # --------------------------------------------------------

    if compliance_score >= 85:
        positive_signals.append(
            "The startup demonstrates strong overall "
            "FinTech compliance readiness."
        )

    risk_score = round(
        min(max(risk_score, 0.0), 100.0),
        2,
    )

    return {
        "score": risk_score,
        "level": classify_risk_level(risk_score),
        "findings": findings,
        "positive_signals": positive_signals,
        "compliance_readiness_score": compliance_score,
    }


# ============================================================
# TEAM RISK ANALYSIS
# ============================================================

def analyze_team_risk(
    team_data: dict[str, Any],
    team_score: float,
    initial_risk: str = "Information Not Available",
) -> dict[str, Any]:
    """
    Analyse founder and team-related risks.

    Parameters
    ----------
    team_data:
        Startup founder and team information.

    team_score:
        Team quality score calculated by calculate_team_score().

    initial_risk:
        User-provided initial team risk indicator.

    Returns
    -------
    dict
        Team risk score, risk level, findings,
        and positive signals.
    """

    risk_score = 100.0 - _safe_float(team_score)

    findings: list[dict[str, str]] = []
    positive_signals: list[str] = []

    founder_count = _safe_int(
        team_data.get("founder_count", 0)
    )

    founder_experience_years = _safe_float(
        team_data.get(
            "founder_experience_years",
            0,
        )
    )

    industry_experience_years = _safe_float(
        team_data.get(
            "industry_experience_years",
            0,
        )
    )

    previous_startup_experience = str(
        team_data.get(
            "previous_startup_experience",
            "Information Not Available",
        )
    )

    technical_team_strength = _safe_float(
        team_data.get(
            "technical_team_strength",
            1,
        )
    )

    business_team_strength = _safe_float(
        team_data.get(
            "business_team_strength",
            1,
        )
    )

    team_stability = _safe_float(
        team_data.get(
            "team_stability",
            1,
        )
    )

    key_person_dependency = str(
        team_data.get(
            "key_person_dependency",
            "Information Not Available",
        )
    )

    founder_details = str(
        team_data.get(
            "founder_details",
            "",
        )
    ).strip()

    # --------------------------------------------------------
    # 1. FOUNDER STRUCTURE
    # --------------------------------------------------------

    if founder_count <= 0:
        risk_score = max(risk_score, 85)

        findings.append(
            create_risk_finding(
                category="Team Risk",
                title="No founder information available",
                description=(
                    "The startup record does not contain a valid "
                    "founder count."
                ),
                severity="Critical",
                impact=(
                    "The ownership, leadership, and decision-making "
                    "structure cannot be assessed."
                ),
                recommendation=(
                    "Verify the founder structure and collect complete "
                    "leadership information before investment review."
                ),
            )
        )

    elif founder_count == 1:
        risk_score += 12

        findings.append(
            create_risk_finding(
                category="Team Risk",
                title="Single-founder dependency",
                description=(
                    "The startup currently has only one founder."
                ),
                severity="Medium",
                impact=(
                    "Business continuity and major decisions may depend "
                    "heavily on one individual."
                ),
                recommendation=(
                    "Assess succession planning, delegation, and the "
                    "strength of the broader leadership team."
                ),
            )
        )

    elif founder_count >= 3:
        positive_signals.append(
            "The startup has a multi-founder leadership structure."
        )

    # --------------------------------------------------------
    # 2. FOUNDER EXPERIENCE
    # --------------------------------------------------------

    if founder_experience_years <= 0:
        risk_score += 10

        findings.append(
            create_risk_finding(
                category="Team Risk",
                title="Founder experience not demonstrated",
                description=(
                    "The founders have not reported meaningful "
                    "professional experience."
                ),
                severity="Medium",
                impact=(
                    "The leadership team may lack experience in "
                    "execution, hiring, operations, or fundraising."
                ),
                recommendation=(
                    "Verify founder employment history, domain knowledge, "
                    "and relevant professional achievements."
                ),
            )
        )

    elif founder_experience_years < 2:
        risk_score += 7

        findings.append(
            create_risk_finding(
                category="Team Risk",
                title="Limited founder experience",
                description=(
                    "Average founder experience is below two years."
                ),
                severity="Medium",
                impact=(
                    "The founders may have limited exposure to complex "
                    "business and operational challenges."
                ),
                recommendation=(
                    "Strengthen the leadership team through experienced "
                    "advisors or senior hires."
                ),
            )
        )

    elif founder_experience_years >= 5:
        positive_signals.append(
            "The founders report at least five years of "
            "average professional experience."
        )

    # --------------------------------------------------------
    # 3. INDUSTRY EXPERIENCE
    # --------------------------------------------------------

    if industry_experience_years <= 0:
        risk_score += 10

        findings.append(
            create_risk_finding(
                category="Team Risk",
                title="No relevant industry experience",
                description=(
                    "The founding team has not reported direct "
                    "experience in the target industry."
                ),
                severity="High",
                impact=(
                    "The team may misunderstand regulatory, customer, "
                    "operational, or competitive realities."
                ),
                recommendation=(
                    "Add experienced industry advisors or leadership "
                    "personnel before scaling."
                ),
            )
        )

    elif industry_experience_years < 2:
        risk_score += 6

        findings.append(
            create_risk_finding(
                category="Team Risk",
                title="Limited industry experience",
                description=(
                    "Average relevant industry experience is below "
                    "two years."
                ),
                severity="Medium",
                impact=(
                    "The team may require additional support in market "
                    "strategy and regulatory navigation."
                ),
                recommendation=(
                    "Strengthen the team with experienced industry "
                    "professionals or advisors."
                ),
            )
        )

    elif industry_experience_years >= 5:
        positive_signals.append(
            "The team has at least five years of average "
            "industry experience."
        )

    # --------------------------------------------------------
    # 4. PREVIOUS STARTUP EXPERIENCE
    # --------------------------------------------------------

    if previous_startup_experience == "No":
        risk_score += 5

        findings.append(
            create_risk_finding(
                category="Team Risk",
                title="No previous startup experience",
                description=(
                    "The founders have not previously worked on "
                    "or operated a startup."
                ),
                severity="Low",
                impact=(
                    "The founders may be unfamiliar with rapid growth, "
                    "fundraising, uncertainty, and limited resources."
                ),
                recommendation=(
                    "Provide mentoring and verify that experienced "
                    "operators are available to support the founders."
                ),
            )
        )

    elif previous_startup_experience == "Information Not Available":
        risk_score += 4

        findings.append(
            create_risk_finding(
                category="Team Risk",
                title="Startup experience not verified",
                description=(
                    "Information about previous startup experience "
                    "is unavailable."
                ),
                severity="Low",
                impact=(
                    "The team's ability to operate in an early-stage "
                    "environment cannot be fully assessed."
                ),
                recommendation=(
                    "Verify previous startup roles, responsibilities, "
                    "and outcomes."
                ),
            )
        )

    elif previous_startup_experience == "Yes":
        positive_signals.append(
            "The founders report previous startup experience."
        )

    # --------------------------------------------------------
    # 5. TECHNICAL TEAM STRENGTH
    # --------------------------------------------------------

    if technical_team_strength <= 3:
        risk_score += 15

        findings.append(
            create_risk_finding(
                category="Team Risk",
                title="Weak technical team",
                description=(
                    "Technical team strength is rated at three "
                    "or below out of ten."
                ),
                severity="High",
                impact=(
                    "The startup may struggle to build, maintain, secure, "
                    "or scale its technology."
                ),
                recommendation=(
                    "Recruit experienced technical leadership and "
                    "strengthen engineering capability."
                ),
            )
        )

    elif technical_team_strength <= 5:
        risk_score += 8

        findings.append(
            create_risk_finding(
                category="Team Risk",
                title="Moderate technical capability",
                description=(
                    "Technical team strength is rated between four "
                    "and five out of ten."
                ),
                severity="Medium",
                impact=(
                    "The current team may face difficulty delivering "
                    "complex product and scaling requirements."
                ),
                recommendation=(
                    "Assess technical hiring needs and create a "
                    "clear engineering expansion plan."
                ),
            )
        )

    elif technical_team_strength >= 8:
        positive_signals.append(
            "The startup reports strong technical team capability."
        )

    # --------------------------------------------------------
    # 6. BUSINESS TEAM STRENGTH
    # --------------------------------------------------------

    if business_team_strength <= 3:
        risk_score += 15

        findings.append(
            create_risk_finding(
                category="Team Risk",
                title="Weak business team",
                description=(
                    "Business team strength is rated at three "
                    "or below out of ten."
                ),
                severity="High",
                impact=(
                    "The startup may struggle with sales, partnerships, "
                    "finance, strategy, and operations."
                ),
                recommendation=(
                    "Add experienced commercial and operational "
                    "leadership before major expansion."
                ),
            )
        )

    elif business_team_strength <= 5:
        risk_score += 8

        findings.append(
            create_risk_finding(
                category="Team Risk",
                title="Moderate business capability",
                description=(
                    "Business team strength is rated between four "
                    "and five out of ten."
                ),
                severity="Medium",
                impact=(
                    "Growth may be limited by weak commercial "
                    "or operational execution."
                ),
                recommendation=(
                    "Strengthen sales, strategy, finance, and "
                    "operations capabilities."
                ),
            )
        )

    elif business_team_strength >= 8:
        positive_signals.append(
            "The startup reports strong business team capability."
        )

    # --------------------------------------------------------
    # 7. TEAM STABILITY
    # --------------------------------------------------------

    if team_stability <= 3:
        risk_score += 18

        findings.append(
            create_risk_finding(
                category="Team Risk",
                title="Very low team stability",
                description=(
                    "Team stability is rated at three or below "
                    "out of ten."
                ),
                severity="High",
                impact=(
                    "Frequent departures or internal conflict may "
                    "disrupt execution and investor confidence."
                ),
                recommendation=(
                    "Investigate turnover, founder relationships, "
                    "employee retention, and internal governance."
                ),
            )
        )

    elif team_stability <= 5:
        risk_score += 9

        findings.append(
            create_risk_finding(
                category="Team Risk",
                title="Team stability requires attention",
                description=(
                    "Team stability is rated between four "
                    "and five out of ten."
                ),
                severity="Medium",
                impact=(
                    "Operational continuity may be affected if key "
                    "employees or founders leave."
                ),
                recommendation=(
                    "Review retention measures, employee agreements, "
                    "and founder alignment."
                ),
            )
        )

    elif team_stability >= 8:
        positive_signals.append(
            "The startup reports high team stability."
        )

    # --------------------------------------------------------
    # 8. KEY-PERSON DEPENDENCY
    # --------------------------------------------------------

    if key_person_dependency == "High":
        risk_score += 15

        findings.append(
            create_risk_finding(
                category="Team Risk",
                title="High key-person dependency",
                description=(
                    "The startup depends heavily on one or a few "
                    "individuals."
                ),
                severity="High",
                impact=(
                    "The departure or unavailability of a key person "
                    "could seriously affect operations."
                ),
                recommendation=(
                    "Document critical responsibilities, create "
                    "succession plans, and distribute knowledge."
                ),
            )
        )

    elif key_person_dependency == "Moderate":
        risk_score += 7

        findings.append(
            create_risk_finding(
                category="Team Risk",
                title="Moderate key-person dependency",
                description=(
                    "Some important responsibilities depend on "
                    "a limited number of individuals."
                ),
                severity="Medium",
                impact=(
                    "Business continuity may be affected if a key "
                    "team member becomes unavailable."
                ),
                recommendation=(
                    "Improve delegation, documentation, and "
                    "cross-functional backup."
                ),
            )
        )

    elif key_person_dependency == "Low":
        positive_signals.append(
            "The startup reports low key-person dependency."
        )

    # --------------------------------------------------------
    # 9. FOUNDER INFORMATION QUALITY
    # --------------------------------------------------------

    if not founder_details:
        risk_score += 5

        findings.append(
            create_risk_finding(
                category="Team Risk",
                title="Founder details incomplete",
                description=(
                    "Detailed founder backgrounds, roles, or "
                    "achievements were not provided."
                ),
                severity="Low",
                impact=(
                    "The leadership team's credibility and suitability "
                    "cannot be fully verified."
                ),
                recommendation=(
                    "Collect founder biographies, role descriptions, "
                    "employment history, and references."
                ),
            )
        )

    else:
        positive_signals.append(
            "Detailed founder and key-team information is available."
        )

    # --------------------------------------------------------
    # 10. INITIAL MANUAL RISK INDICATOR
    # --------------------------------------------------------

    manual_risk_floors = {
        "Low": 0,
        "Moderate": 30,
        "High": 55,
        "Information Not Available": 0,
    }

    risk_score = max(
        risk_score,
        manual_risk_floors.get(initial_risk, 0),
    )

    risk_score = round(
        min(max(risk_score, 0.0), 100.0),
        2,
    )

    return {
        "score": risk_score,
        "level": classify_risk_level(risk_score),
        "findings": findings,
        "positive_signals": positive_signals,
        "source_score": clamp_source_score(team_score),
    }


# ============================================================
# PRODUCT AND TECHNOLOGY RISK ANALYSIS
# ============================================================

def clamp_source_score(score: float) -> float:
    """
    Safely limit an existing category score between 0 and 100.
    """

    return round(
        min(max(_safe_float(score), 0.0), 100.0),
        2,
    )


def analyze_product_technology_risk(
    product_data: dict[str, Any],
    product_score: float,
    initial_risk: str = "Information Not Available",
) -> dict[str, Any]:
    """
    Analyse product maturity and technology-related risks.

    Parameters
    ----------
    product_data:
        Product and technology information.

    product_score:
        Product score calculated by calculate_product_score().

    initial_risk:
        User-provided initial technology-risk indicator.

    Returns
    -------
    dict
        Product and technology risk assessment.
    """

    risk_score = 100.0 - clamp_source_score(product_score)

    findings: list[dict[str, str]] = []
    positive_signals: list[str] = []

    product_name = str(
        product_data.get(
            "product_name",
            "",
        )
    ).strip()

    problem_statement = str(
        product_data.get(
            "problem_statement",
            "",
        )
    ).strip()

    product_description = str(
        product_data.get(
            "product_description",
            "",
        )
    ).strip()

    product_stage = str(
        product_data.get(
            "product_stage",
            "Concept Only",
        )
    )

    working_mvp = str(
        product_data.get(
            "working_mvp",
            "Information Not Available",
        )
    )

    intellectual_property = str(
        product_data.get(
            "intellectual_property",
            "Information Not Available",
        )
    )

    product_uniqueness = _safe_float(
        product_data.get(
            "product_uniqueness",
            1,
        )
    )

    technology_readiness = _safe_float(
        product_data.get(
            "technology_readiness",
            1,
        )
    )

    product_scalability = _safe_float(
        product_data.get(
            "product_scalability",
            1,
        )
    )

    unique_selling_proposition = str(
        product_data.get(
            "unique_selling_proposition",
            "",
        )
    ).strip()

    # --------------------------------------------------------
    # 1. PRODUCT STAGE
    # --------------------------------------------------------

    if product_stage == "Concept Only":
        risk_score = max(risk_score, 70)

        findings.append(
            create_risk_finding(
                category="Product & Technology Risk",
                title="Product remains at concept stage",
                description=(
                    "The startup has not yet progressed beyond "
                    "the concept stage."
                ),
                severity="High",
                impact=(
                    "Technical feasibility, customer acceptance, "
                    "and execution ability remain largely unproven."
                ),
                recommendation=(
                    "Develop and validate a functional prototype "
                    "before significant investment."
                ),
            )
        )

    elif product_stage == "Prototype":
        risk_score = max(risk_score, 55)

        findings.append(
            create_risk_finding(
                category="Product & Technology Risk",
                title="Product limited to prototype stage",
                description=(
                    "The startup has developed a prototype but "
                    "has not yet demonstrated a complete market-ready product."
                ),
                severity="High",
                impact=(
                    "Significant development, testing, and customer "
                    "validation may still be required."
                ),
                recommendation=(
                    "Complete MVP development and validate the product "
                    "with real target customers."
                ),
            )
        )

    elif product_stage == "Minimum Viable Product":
        risk_score = max(risk_score, 35)

        findings.append(
            create_risk_finding(
                category="Product & Technology Risk",
                title="MVP requires further validation",
                description=(
                    "The product is at the minimum viable product stage."
                ),
                severity="Medium",
                impact=(
                    "The product may still contain usability, reliability, "
                    "or product-market-fit uncertainties."
                ),
                recommendation=(
                    "Collect structured customer feedback and verify "
                    "performance before scaling."
                ),
            )
        )

    elif product_stage in {
        "Market Ready",
        "Scaling",
    }:
        positive_signals.append(
            "The product has reached an advanced commercial stage."
        )

    # --------------------------------------------------------
    # 2. WORKING MVP
    # --------------------------------------------------------

    if working_mvp == "No":
        risk_score = max(risk_score, 70)

        findings.append(
            create_risk_finding(
                category="Product & Technology Risk",
                title="No working MVP available",
                description=(
                    "The startup has not demonstrated a working "
                    "minimum viable product."
                ),
                severity="High",
                impact=(
                    "The product's technical feasibility and practical "
                    "value remain unverified."
                ),
                recommendation=(
                    "Require a working MVP and technical demonstration "
                    "before investment approval."
                ),
            )
        )

    elif working_mvp == "Under Development":
        risk_score = max(risk_score, 50)

        findings.append(
            create_risk_finding(
                category="Product & Technology Risk",
                title="MVP still under development",
                description=(
                    "The minimum viable product is not yet complete."
                ),
                severity="Medium",
                impact=(
                    "Development delays, cost overruns, or technical "
                    "issues may affect launch plans."
                ),
                recommendation=(
                    "Review the product roadmap, development milestones, "
                    "budget, and technical blockers."
                ),
            )
        )

    elif working_mvp == "Information Not Available":
        risk_score += 8

        findings.append(
            create_risk_finding(
                category="Product & Technology Risk",
                title="MVP status not verified",
                description=(
                    "The availability of a working MVP has "
                    "not been confirmed."
                ),
                severity="Medium",
                impact=(
                    "Product maturity and technical feasibility "
                    "cannot be independently assessed."
                ),
                recommendation=(
                    "Request a live product demonstration and "
                    "technical documentation."
                ),
            )
        )

    elif working_mvp == "Yes":
        positive_signals.append(
            "A working MVP is available."
        )

    # --------------------------------------------------------
    # 3. TECHNOLOGY READINESS
    # --------------------------------------------------------

    if technology_readiness <= 3:
        risk_score += 18

        findings.append(
            create_risk_finding(
                category="Product & Technology Risk",
                title="Very low technology readiness",
                description=(
                    "Technology readiness is rated at three "
                    "or below out of ten."
                ),
                severity="High",
                impact=(
                    "The product may not be reliable, secure, stable, "
                    "or ready for real users."
                ),
                recommendation=(
                    "Conduct a technical audit and define a detailed "
                    "readiness-improvement plan."
                ),
            )
        )

    elif technology_readiness <= 5:
        risk_score += 10

        findings.append(
            create_risk_finding(
                category="Product & Technology Risk",
                title="Technology readiness requires improvement",
                description=(
                    "Technology readiness is rated between four "
                    "and five out of ten."
                ),
                severity="Medium",
                impact=(
                    "The platform may require important engineering "
                    "work before commercial expansion."
                ),
                recommendation=(
                    "Prioritise reliability, security, testing, "
                    "and infrastructure improvements."
                ),
            )
        )

    elif technology_readiness >= 8:
        positive_signals.append(
            "The startup reports high technology readiness."
        )

    # --------------------------------------------------------
    # 4. PRODUCT SCALABILITY
    # --------------------------------------------------------

    if product_scalability <= 3:
        risk_score += 16

        findings.append(
            create_risk_finding(
                category="Product & Technology Risk",
                title="Low product scalability",
                description=(
                    "Product scalability is rated at three "
                    "or below out of ten."
                ),
                severity="High",
                impact=(
                    "The product may experience performance, cost, "
                    "or operational problems as usage increases."
                ),
                recommendation=(
                    "Review architecture, infrastructure costs, "
                    "capacity limits, and scaling plans."
                ),
            )
        )

    elif product_scalability <= 5:
        risk_score += 8

        findings.append(
            create_risk_finding(
                category="Product & Technology Risk",
                title="Scalability requires further validation",
                description=(
                    "Product scalability is rated between four "
                    "and five out of ten."
                ),
                severity="Medium",
                impact=(
                    "Growth may require substantial redevelopment "
                    "or infrastructure investment."
                ),
                recommendation=(
                    "Conduct load testing and prepare a documented "
                    "technical scaling roadmap."
                ),
            )
        )

    elif product_scalability >= 8:
        positive_signals.append(
            "The startup reports strong product scalability."
        )

    # --------------------------------------------------------
    # 5. PRODUCT UNIQUENESS
    # --------------------------------------------------------

    if product_uniqueness <= 3:
        risk_score += 14

        findings.append(
            create_risk_finding(
                category="Product & Technology Risk",
                title="Low product differentiation",
                description=(
                    "Product uniqueness is rated at three "
                    "or below out of ten."
                ),
                severity="High",
                impact=(
                    "Customers may have little reason to choose "
                    "the startup over existing alternatives."
                ),
                recommendation=(
                    "Strengthen the value proposition and identify "
                    "defensible product differentiation."
                ),
            )
        )

    elif product_uniqueness <= 5:
        risk_score += 7

        findings.append(
            create_risk_finding(
                category="Product & Technology Risk",
                title="Limited product differentiation",
                description=(
                    "Product uniqueness is rated between four "
                    "and five out of ten."
                ),
                severity="Medium",
                impact=(
                    "Competitive pressure may reduce pricing power "
                    "and customer acquisition."
                ),
                recommendation=(
                    "Clarify the unique benefits, features, or "
                    "business-model advantages."
                ),
            )
        )

    elif product_uniqueness >= 8:
        positive_signals.append(
            "The product demonstrates strong differentiation."
        )

    # --------------------------------------------------------
    # 6. INTELLECTUAL PROPERTY
    # --------------------------------------------------------

    if intellectual_property == "No Intellectual Property":
        risk_score += 6

        findings.append(
            create_risk_finding(
                category="Product & Technology Risk",
                title="No formal intellectual property protection",
                description=(
                    "The startup reports no registered or formal "
                    "intellectual property protection."
                ),
                severity="Low",
                impact=(
                    "Competitors may be able to copy important "
                    "product features or branding."
                ),
                recommendation=(
                    "Assess whether patents, trademarks, copyrights, "
                    "or trade-secret protections are appropriate."
                ),
            )
        )

    elif intellectual_property == "Information Not Available":
        risk_score += 5

        findings.append(
            create_risk_finding(
                category="Product & Technology Risk",
                title="Intellectual property status not verified",
                description=(
                    "Information about intellectual property ownership "
                    "or protection is unavailable."
                ),
                severity="Medium",
                impact=(
                    "The startup may face ownership disputes or weak "
                    "protection against competitors."
                ),
                recommendation=(
                    "Verify code, brand, patent, and technology ownership."
                ),
            )
        )

    elif intellectual_property in {
        "Patent Granted",
        "Patent Filed",
        "Trademark Registered",
        "Internally Developed Technology",
    }:
        positive_signals.append(
            "The startup reports identifiable intellectual property "
            "or internally developed technology."
        )

    # --------------------------------------------------------
    # 7. PRODUCT DOCUMENTATION
    # --------------------------------------------------------

    if not product_name:
        risk_score += 3

        findings.append(
            create_risk_finding(
                category="Product & Technology Risk",
                title="Product identity incomplete",
                description=(
                    "A clear product or service name was not provided."
                ),
                severity="Low",
                impact=(
                    "The product record may be incomplete or "
                    "poorly documented."
                ),
                recommendation=(
                    "Provide a clear product name and version information."
                ),
            )
        )

    if not problem_statement:
        risk_score += 7

        findings.append(
            create_risk_finding(
                category="Product & Technology Risk",
                title="Customer problem not clearly defined",
                description=(
                    "The startup has not clearly explained the "
                    "problem being solved."
                ),
                severity="Medium",
                impact=(
                    "The product may lack a validated customer need "
                    "or focused value proposition."
                ),
                recommendation=(
                    "Define the target customer's problem using "
                    "evidence from interviews or market research."
                ),
            )
        )

    if not product_description:
        risk_score += 5

        findings.append(
            create_risk_finding(
                category="Product & Technology Risk",
                title="Product description incomplete",
                description=(
                    "A complete product or service description "
                    "was not provided."
                ),
                severity="Low",
                impact=(
                    "The product's features, process, and customer "
                    "benefits cannot be fully assessed."
                ),
                recommendation=(
                    "Provide a complete product description and "
                    "technical overview."
                ),
            )
        )

    if not unique_selling_proposition:
        risk_score += 8

        findings.append(
            create_risk_finding(
                category="Product & Technology Risk",
                title="Unique selling proposition missing",
                description=(
                    "The startup has not clearly explained why "
                    "customers should choose its product."
                ),
                severity="Medium",
                impact=(
                    "Customer acquisition and competitive positioning "
                    "may be difficult."
                ),
                recommendation=(
                    "Define and validate a clear unique selling proposition."
                ),
            )
        )

    else:
        positive_signals.append(
            "A unique selling proposition has been documented."
        )

    # --------------------------------------------------------
    # 8. INITIAL MANUAL RISK INDICATOR
    # --------------------------------------------------------

    manual_risk_floors = {
        "Low": 0,
        "Moderate": 30,
        "High": 55,
        "Information Not Available": 0,
    }

    risk_score = max(
        risk_score,
        manual_risk_floors.get(initial_risk, 0),
    )

    risk_score = round(
        min(max(risk_score, 0.0), 100.0),
        2,
    )

    return {
        "score": risk_score,
        "level": classify_risk_level(risk_score),
        "findings": findings,
        "positive_signals": positive_signals,
        "source_score": clamp_source_score(product_score),
    }

# ============================================================
# MARKET RISK ANALYSIS
# ============================================================

def analyze_market_risk(
    market_data: dict[str, Any],
    market_score: float,
    initial_risk: str = "Information Not Available",
) -> dict[str, Any]:
    """
    Analyse market opportunity and competition-related risks.
    """

    risk_score = 100.0 - clamp_source_score(market_score)

    findings: list[dict[str, str]] = []
    positive_signals: list[str] = []

    target_customers = str(
        market_data.get("target_customers", "")
    ).strip()

    total_market = _safe_float(
        market_data.get("total_addressable_market", 0)
    )

    serviceable_market = _safe_float(
        market_data.get("serviceable_available_market", 0)
    )

    market_growth_rate = _safe_float(
        market_data.get("market_growth_rate", 0)
    )

    competitor_count = _safe_int(
        market_data.get("competitor_count", 0)
    )

    competition_level = str(
        market_data.get(
            "competition_level",
            "Information Not Available",
        )
    )

    competitive_advantage = _safe_float(
        market_data.get(
            "competitive_advantage_strength",
            1,
        )
    )

    competitor_details = str(
        market_data.get("competitor_details", "")
    ).strip()

    # --------------------------------------------------------
    # 1. TARGET CUSTOMER CLARITY
    # --------------------------------------------------------

    if not target_customers:
        risk_score += 12

        findings.append(
            create_risk_finding(
                category="Market Risk",
                title="Target customers not clearly defined",
                description=(
                    "The startup has not clearly identified its "
                    "primary target customer group."
                ),
                severity="High",
                impact=(
                    "Product positioning, pricing, marketing, and "
                    "customer acquisition may remain unfocused."
                ),
                recommendation=(
                    "Define customer segments using demographic, "
                    "business, behavioural, and geographic characteristics."
                ),
            )
        )

    else:
        positive_signals.append(
            "The startup has documented its target customer segment."
        )

    # --------------------------------------------------------
    # 2. TOTAL ADDRESSABLE MARKET
    # --------------------------------------------------------

    if total_market <= 0:
        risk_score += 15

        findings.append(
            create_risk_finding(
                category="Market Risk",
                title="Total addressable market not estimated",
                description=(
                    "No valid estimate of the total addressable "
                    "market was provided."
                ),
                severity="High",
                impact=(
                    "The startup's maximum growth opportunity and "
                    "commercial potential cannot be evaluated."
                ),
                recommendation=(
                    "Prepare a documented market-size estimate using "
                    "reliable industry and customer data."
                ),
            )
        )

    elif total_market < 100_000_000:
        risk_score += 8

        findings.append(
            create_risk_finding(
                category="Market Risk",
                title="Limited total addressable market",
                description=(
                    "The reported total addressable market is below "
                    "₹100 million."
                ),
                severity="Medium",
                impact=(
                    "The startup may have limited long-term revenue "
                    "and valuation potential."
                ),
                recommendation=(
                    "Verify the market estimate and assess adjacent "
                    "customer segments or expansion opportunities."
                ),
            )
        )

    elif total_market >= 1_000_000_000:
        positive_signals.append(
            "The startup reports a substantial total addressable market."
        )

    # --------------------------------------------------------
    # 3. SERVICEABLE MARKET
    # --------------------------------------------------------

    if serviceable_market <= 0:
        risk_score += 10

        findings.append(
            create_risk_finding(
                category="Market Risk",
                title="Serviceable market not estimated",
                description=(
                    "The realistic serviceable market has not "
                    "been quantified."
                ),
                severity="Medium",
                impact=(
                    "The startup may be relying on an overly broad "
                    "market opportunity that it cannot practically reach."
                ),
                recommendation=(
                    "Estimate the market that can realistically be served "
                    "using the startup's product, geography, and resources."
                ),
            )
        )

    elif total_market > 0:
        serviceable_percentage = (
            serviceable_market / total_market
        ) * 100

        if serviceable_market > total_market:
            risk_score += 10

            findings.append(
                create_risk_finding(
                    category="Market Risk",
                    title="Serviceable market exceeds total market",
                    description=(
                        "The reported serviceable market is larger than "
                        "the total addressable market."
                    ),
                    severity="High",
                    impact=(
                        "The market-sizing assumptions may be inaccurate "
                        "or internally inconsistent."
                    ),
                    recommendation=(
                        "Recalculate TAM and SAM using a consistent "
                        "market-sizing methodology."
                    ),
                )
            )

        elif serviceable_percentage < 5:
            risk_score += 5

            findings.append(
                create_risk_finding(
                    category="Market Risk",
                    title="Very small serviceable market share",
                    description=(
                        "The serviceable market is below five percent "
                        "of the total addressable market."
                    ),
                    severity="Low",
                    impact=(
                        "The startup's immediately reachable market "
                        "may be limited."
                    ),
                    recommendation=(
                        "Assess whether geographic, regulatory, or product "
                        "constraints can be reduced."
                    ),
                )
            )

    # --------------------------------------------------------
    # 4. MARKET GROWTH
    # --------------------------------------------------------

    if market_growth_rate < 0:
        risk_score += 18

        findings.append(
            create_risk_finding(
                category="Market Risk",
                title="Market is contracting",
                description=(
                    "The reported annual market growth rate is negative."
                ),
                severity="High",
                impact=(
                    "A declining market may reduce demand, pricing power, "
                    "and future growth opportunities."
                ),
                recommendation=(
                    "Verify the decline and assess whether the startup "
                    "can target a growing niche or adjacent market."
                ),
            )
        )

    elif market_growth_rate < 5:
        risk_score += 10

        findings.append(
            create_risk_finding(
                category="Market Risk",
                title="Low market growth",
                description=(
                    "The reported market growth rate is below five percent."
                ),
                severity="Medium",
                impact=(
                    "The startup may need to gain customers mainly by "
                    "taking market share from established competitors."
                ),
                recommendation=(
                    "Validate the growth assumptions and assess whether "
                    "the startup has a strong customer-switching advantage."
                ),
            )
        )

    elif market_growth_rate >= 20:
        positive_signals.append(
            "The startup operates in a rapidly growing market."
        )

    # --------------------------------------------------------
    # 5. COMPETITION LEVEL
    # --------------------------------------------------------

    if competition_level == "Very High":
        risk_score += 18

        findings.append(
            create_risk_finding(
                category="Market Risk",
                title="Very high competitive intensity",
                description=(
                    "The startup reports a very high level of competition."
                ),
                severity="High",
                impact=(
                    "Customer acquisition costs, pricing pressure, and "
                    "market-entry difficulty may be substantial."
                ),
                recommendation=(
                    "Verify differentiation, customer acquisition strategy, "
                    "pricing power, and competitive barriers."
                ),
            )
        )

    elif competition_level == "High":
        risk_score += 12

        findings.append(
            create_risk_finding(
                category="Market Risk",
                title="High competitive intensity",
                description=(
                    "The startup operates in a highly competitive market."
                ),
                severity="Medium",
                impact=(
                    "Strong incumbents may limit customer growth and "
                    "increase marketing expenditure."
                ),
                recommendation=(
                    "Develop a clear positioning strategy and focus on "
                    "a defensible customer segment."
                ),
            )
        )

    elif competition_level == "Information Not Available":
        risk_score += 7

        findings.append(
            create_risk_finding(
                category="Market Risk",
                title="Competition level not assessed",
                description=(
                    "The level of market competition has not been confirmed."
                ),
                severity="Medium",
                impact=(
                    "The startup may underestimate existing alternatives "
                    "and market-entry barriers."
                ),
                recommendation=(
                    "Conduct structured competitor and substitute analysis."
                ),
            )
        )

    elif competition_level == "Low":
        positive_signals.append(
            "The startup reports relatively low competitive intensity."
        )

    # --------------------------------------------------------
    # 6. COMPETITIVE ADVANTAGE
    # --------------------------------------------------------

    if competitive_advantage <= 3:
        risk_score += 18

        findings.append(
            create_risk_finding(
                category="Market Risk",
                title="Weak competitive advantage",
                description=(
                    "Competitive advantage strength is rated at three "
                    "or below out of ten."
                ),
                severity="High",
                impact=(
                    "Competitors may easily copy the product or attract "
                    "the startup's target customers."
                ),
                recommendation=(
                    "Build defensibility through technology, distribution, "
                    "data, partnerships, branding, or regulatory capability."
                ),
            )
        )

    elif competitive_advantage <= 5:
        risk_score += 10

        findings.append(
            create_risk_finding(
                category="Market Risk",
                title="Limited competitive advantage",
                description=(
                    "Competitive advantage strength is rated between "
                    "four and five out of ten."
                ),
                severity="Medium",
                impact=(
                    "The startup may struggle to maintain pricing power "
                    "or long-term differentiation."
                ),
                recommendation=(
                    "Strengthen and validate the startup's defensible "
                    "market advantage."
                ),
            )
        )

    elif competitive_advantage >= 8:
        positive_signals.append(
            "The startup reports a strong competitive advantage."
        )

    # --------------------------------------------------------
    # 7. COMPETITOR RESEARCH
    # --------------------------------------------------------

    if competitor_count <= 0 and not competitor_details:
        risk_score += 10

        findings.append(
            create_risk_finding(
                category="Market Risk",
                title="Competitor research not demonstrated",
                description=(
                    "No competitors or competing solutions were identified."
                ),
                severity="Medium",
                impact=(
                    "The startup may underestimate direct competitors, "
                    "indirect alternatives, or substitute products."
                ),
                recommendation=(
                    "Identify major competitors and compare pricing, "
                    "features, strengths, and weaknesses."
                ),
            )
        )

    elif competitor_details:
        positive_signals.append(
            "Competitor information has been documented."
        )

    # --------------------------------------------------------
    # 8. INITIAL MANUAL RISK INDICATOR
    # --------------------------------------------------------

    manual_risk_floors = {
        "Low": 0,
        "Moderate": 30,
        "High": 55,
        "Information Not Available": 0,
    }

    risk_score = max(
        risk_score,
        manual_risk_floors.get(initial_risk, 0),
    )

    risk_score = round(
        min(max(risk_score, 0.0), 100.0),
        2,
    )

    return {
        "score": risk_score,
        "level": classify_risk_level(risk_score),
        "findings": findings,
        "positive_signals": positive_signals,
        "source_score": clamp_source_score(market_score),
    }


# ============================================================
# CUSTOMER AND TRACTION RISK ANALYSIS
# ============================================================

def analyze_customer_risk(
    customer_data: dict[str, Any],
    customer_score: float,
    initial_risk: str = "Information Not Available",
) -> dict[str, Any]:
    """
    Analyse customer traction, retention, churn,
    unit economics, and concentration risks.
    """

    risk_score = 100.0 - clamp_source_score(customer_score)

    findings: list[dict[str, str]] = []
    positive_signals: list[str] = []

    total_customers = _safe_int(
        customer_data.get("total_customers", 0)
    )

    new_customers = _safe_int(
        customer_data.get("new_customers_monthly", 0)
    )

    customers_lost = _safe_int(
        customer_data.get("customers_lost_monthly", 0)
    )

    customer_growth_rate = _safe_float(
        customer_data.get("customer_growth_rate", 0)
    )

    retention_rate = _safe_float(
        customer_data.get("retention_rate", 0)
    )

    churn_rate = _safe_float(
        customer_data.get("churn_rate", 0)
    )

    acquisition_cost = _safe_float(
        customer_data.get("customer_acquisition_cost", 0)
    )

    lifetime_value = _safe_float(
        customer_data.get("customer_lifetime_value", 0)
    )

    customer_dependency = str(
        customer_data.get(
            "major_customer_dependency",
            "Information Not Available",
        )
    )

    net_new_customers = new_customers - customers_lost

    # --------------------------------------------------------
    # 1. CUSTOMER BASE
    # --------------------------------------------------------

    if total_customers <= 0:
        risk_score = max(risk_score, 65)

        findings.append(
            create_risk_finding(
                category="Customer & Traction Risk",
                title="No existing customers reported",
                description=(
                    "The startup has not reported any current customers."
                ),
                severity="High",
                impact=(
                    "Customer demand and product-market fit remain unproven."
                ),
                recommendation=(
                    "Validate the product with pilot users or paying "
                    "customers before significant expansion."
                ),
            )
        )

    elif total_customers < 10:
        risk_score += 10

        findings.append(
            create_risk_finding(
                category="Customer & Traction Risk",
                title="Very limited customer traction",
                description=(
                    "The startup reports fewer than ten customers."
                ),
                severity="Medium",
                impact=(
                    "Current traction may be insufficient to demonstrate "
                    "repeatable demand."
                ),
                recommendation=(
                    "Collect customer feedback and demonstrate a repeatable "
                    "customer acquisition process."
                ),
            )
        )

    elif total_customers >= 1000:
        positive_signals.append(
            "The startup has established a meaningful customer base."
        )

    # --------------------------------------------------------
    # 2. NET CUSTOMER ACQUISITION
    # --------------------------------------------------------

    if customers_lost > new_customers:
        risk_score += 18

        findings.append(
            create_risk_finding(
                category="Customer & Traction Risk",
                title="Customer base is shrinking",
                description=(
                    "Monthly customer losses exceed new customer acquisition."
                ),
                severity="High",
                impact=(
                    "The startup may be experiencing dissatisfaction, "
                    "weak demand, or product-market-fit problems."
                ),
                recommendation=(
                    "Investigate churn causes and improve onboarding, "
                    "product quality, support, and customer value."
                ),
            )
        )

    elif net_new_customers == 0 and total_customers > 0:
        risk_score += 7

        findings.append(
            create_risk_finding(
                category="Customer & Traction Risk",
                title="Customer growth is stagnant",
                description=(
                    "The startup is not achieving positive net "
                    "monthly customer acquisition."
                ),
                severity="Medium",
                impact=(
                    "Revenue growth and market expansion may remain limited."
                ),
                recommendation=(
                    "Review acquisition channels, conversion rates, "
                    "pricing, and retention strategy."
                ),
            )
        )

    elif net_new_customers > 0:
        positive_signals.append(
            "Monthly customer acquisition exceeds customer losses."
        )

    # --------------------------------------------------------
    # 3. CUSTOMER GROWTH RATE
    # --------------------------------------------------------

    if customer_growth_rate < 0:
        risk_score += 15

        findings.append(
            create_risk_finding(
                category="Customer & Traction Risk",
                title="Negative customer growth",
                description=(
                    "The reported customer growth rate is negative."
                ),
                severity="High",
                impact=(
                    "The startup may be losing market relevance or "
                    "failing to retain customers."
                ),
                recommendation=(
                    "Analyse acquisition and retention data and implement "
                    "a customer recovery plan."
                ),
            )
        )

    elif customer_growth_rate < 5:
        risk_score += 7

        findings.append(
            create_risk_finding(
                category="Customer & Traction Risk",
                title="Low customer growth",
                description=(
                    "The reported customer growth rate is below five percent."
                ),
                severity="Medium",
                impact=(
                    "The startup may struggle to achieve scalable revenue growth."
                ),
                recommendation=(
                    "Improve distribution, conversion, partnerships, "
                    "and customer acquisition efficiency."
                ),
            )
        )

    elif customer_growth_rate >= 15:
        positive_signals.append(
            "The startup reports strong customer growth."
        )

    # --------------------------------------------------------
    # 4. RETENTION
    # --------------------------------------------------------

    if retention_rate <= 0 and total_customers > 0:
        risk_score += 10

        findings.append(
            create_risk_finding(
                category="Customer & Traction Risk",
                title="Customer retention not measured",
                description=(
                    "A valid customer retention rate was not provided."
                ),
                severity="Medium",
                impact=(
                    "The startup cannot demonstrate whether customers "
                    "continue using the product."
                ),
                recommendation=(
                    "Track cohort-based retention and repeat usage."
                ),
            )
        )

    elif retention_rate < 50:
        risk_score += 18

        findings.append(
            create_risk_finding(
                category="Customer & Traction Risk",
                title="Very low customer retention",
                description=(
                    "The reported customer retention rate is below 50 percent."
                ),
                severity="High",
                impact=(
                    "The startup may face weak product satisfaction and "
                    "high replacement-acquisition costs."
                ),
                recommendation=(
                    "Investigate customer drop-off and improve product value, "
                    "service quality, and engagement."
                ),
            )
        )

    elif retention_rate < 70:
        risk_score += 10

        findings.append(
            create_risk_finding(
                category="Customer & Traction Risk",
                title="Customer retention requires improvement",
                description=(
                    "The reported retention rate is below 70 percent."
                ),
                severity="Medium",
                impact=(
                    "Revenue predictability and customer lifetime value "
                    "may be limited."
                ),
                recommendation=(
                    "Improve onboarding, support, engagement, and "
                    "customer-success processes."
                ),
            )
        )

    elif retention_rate >= 90:
        positive_signals.append(
            "The startup reports excellent customer retention."
        )

    # --------------------------------------------------------
    # 5. CHURN
    # --------------------------------------------------------

    if churn_rate > 30:
        risk_score += 20

        findings.append(
            create_risk_finding(
                category="Customer & Traction Risk",
                title="Critical customer churn",
                description=(
                    "The reported churn rate exceeds 30 percent."
                ),
                severity="Critical",
                impact=(
                    "The startup may be unable to maintain a stable "
                    "customer base or sustainable revenue."
                ),
                recommendation=(
                    "Treat churn reduction as an immediate priority and "
                    "identify the main cancellation reasons."
                ),
            )
        )

    elif churn_rate > 20:
        risk_score += 15

        findings.append(
            create_risk_finding(
                category="Customer & Traction Risk",
                title="Very high customer churn",
                description=(
                    "The reported churn rate exceeds 20 percent."
                ),
                severity="High",
                impact=(
                    "High customer replacement costs may weaken growth "
                    "and profitability."
                ),
                recommendation=(
                    "Perform churn segmentation and improve customer "
                    "experience and product value."
                ),
            )
        )

    elif churn_rate > 10:
        risk_score += 9

        findings.append(
            create_risk_finding(
                category="Customer & Traction Risk",
                title="Elevated customer churn",
                description=(
                    "The reported churn rate exceeds ten percent."
                ),
                severity="Medium",
                impact=(
                    "Customer lifetime value and recurring revenue "
                    "may be negatively affected."
                ),
                recommendation=(
                    "Track churn by customer segment and implement "
                    "targeted retention measures."
                ),
            )
        )

    elif 0 <= churn_rate <= 5 and total_customers > 0:
        positive_signals.append(
            "The startup reports a low customer churn rate."
        )

    # --------------------------------------------------------
    # 6. UNIT ECONOMICS
    # --------------------------------------------------------

    if acquisition_cost <= 0 and lifetime_value <= 0:
        risk_score += 10

        findings.append(
            create_risk_finding(
                category="Customer & Traction Risk",
                title="Customer unit economics unavailable",
                description=(
                    "Neither customer acquisition cost nor customer "
                    "lifetime value was provided."
                ),
                severity="Medium",
                impact=(
                    "The sustainability and efficiency of customer "
                    "growth cannot be assessed."
                ),
                recommendation=(
                    "Calculate CAC and LTV using documented customer, "
                    "sales, and revenue data."
                ),
            )
        )

    elif acquisition_cost > 0:
        ltv_cac_ratio = lifetime_value / acquisition_cost

        if ltv_cac_ratio < 1:
            risk_score += 20

            findings.append(
                create_risk_finding(
                    category="Customer & Traction Risk",
                    title="Unsustainable LTV-to-CAC ratio",
                    description=(
                        "Customer lifetime value is lower than customer "
                        "acquisition cost."
                    ),
                    severity="Critical",
                    impact=(
                        "The startup may lose money on every newly "
                        "acquired customer."
                    ),
                    recommendation=(
                        "Reduce acquisition cost, improve retention, "
                        "increase pricing, or improve customer monetisation."
                    ),
                )
            )

        elif ltv_cac_ratio < 2:
            risk_score += 12

            findings.append(
                create_risk_finding(
                    category="Customer & Traction Risk",
                    title="Weak LTV-to-CAC ratio",
                    description=(
                        "The LTV-to-CAC ratio is below two."
                    ),
                    severity="High",
                    impact=(
                        "Customer acquisition may not generate sufficient "
                        "economic value."
                    ),
                    recommendation=(
                        "Improve customer lifetime value and acquisition "
                        "efficiency before aggressive scaling."
                    ),
                )
            )

        elif ltv_cac_ratio < 3:
            risk_score += 6

            findings.append(
                create_risk_finding(
                    category="Customer & Traction Risk",
                    title="LTV-to-CAC ratio requires improvement",
                    description=(
                        "The LTV-to-CAC ratio is below three."
                    ),
                    severity="Medium",
                    impact=(
                        "Unit economics may provide limited protection "
                        "against marketing or retention costs."
                    ),
                    recommendation=(
                        "Improve conversion, pricing, retention, and "
                        "marketing efficiency."
                    ),
                )
            )

        elif ltv_cac_ratio >= 3:
            positive_signals.append(
                "The startup reports a healthy LTV-to-CAC ratio."
            )

    # --------------------------------------------------------
    # 7. CUSTOMER CONCENTRATION
    # --------------------------------------------------------

    if customer_dependency == "High":
        risk_score += 16

        findings.append(
            create_risk_finding(
                category="Customer & Traction Risk",
                title="High customer concentration",
                description=(
                    "The startup depends heavily on one or a few "
                    "major customers."
                ),
                severity="High",
                impact=(
                    "The loss of a major customer could materially "
                    "reduce revenue and cash flow."
                ),
                recommendation=(
                    "Diversify the customer base and monitor revenue "
                    "concentration by customer."
                ),
            )
        )

    elif customer_dependency == "Moderate":
        risk_score += 8

        findings.append(
            create_risk_finding(
                category="Customer & Traction Risk",
                title="Moderate customer concentration",
                description=(
                    "A meaningful share of business depends on "
                    "a limited number of customers."
                ),
                severity="Medium",
                impact=(
                    "Revenue may be vulnerable to contract non-renewal "
                    "or customer bargaining power."
                ),
                recommendation=(
                    "Increase customer diversification and strengthen "
                    "renewal visibility."
                ),
            )
        )

    elif customer_dependency == "Information Not Available":
        risk_score += 5

        findings.append(
            create_risk_finding(
                category="Customer & Traction Risk",
                title="Customer concentration not verified",
                description=(
                    "Information about dependency on major customers "
                    "is unavailable."
                ),
                severity="Low",
                impact=(
                    "Revenue concentration risk cannot be properly assessed."
                ),
                recommendation=(
                    "Collect customer-level revenue and contract data."
                ),
            )
        )

    elif customer_dependency == "Low":
        positive_signals.append(
            "The startup reports low dependency on major customers."
        )

    manual_risk_floors = {
        "Low": 0,
        "Moderate": 30,
        "High": 55,
        "Information Not Available": 0,
    }

    risk_score = max(
        risk_score,
        manual_risk_floors.get(initial_risk, 0),
    )

    risk_score = round(
        min(max(risk_score, 0.0), 100.0),
        2,
    )

    return {
        "score": risk_score,
        "level": classify_risk_level(risk_score),
        "findings": findings,
        "positive_signals": positive_signals,
        "source_score": clamp_source_score(customer_score),
    }


# ============================================================
# FUNDING RISK ANALYSIS
# ============================================================

def analyze_funding_risk(
    funding_data: dict[str, Any],
    funding_score: float,
) -> dict[str, Any]:
    """
    Analyse fundraising history, valuation, funding ask,
    investor support, equity dilution, and use-of-funds risks.
    """

    risk_score = 100.0 - clamp_source_score(funding_score)

    findings: list[dict[str, str]] = []
    positive_signals: list[str] = []

    previous_funding = _safe_float(
        funding_data.get("previous_funding", 0)
    )

    funding_rounds = _safe_int(
        funding_data.get("number_of_funding_rounds", 0)
    )

    current_valuation = _safe_float(
        funding_data.get("current_valuation", 0)
    )

    funding_sought = _safe_float(
        funding_data.get("funding_sought", 0)
    )

    equity_offered = _safe_float(
        funding_data.get("equity_offered", 0)
    )

    investor_count = _safe_int(
        funding_data.get("investor_count", 0)
    )

    investor_details = str(
        funding_data.get("investor_details", "")
    ).strip()

    use_of_funds = str(
        funding_data.get("use_of_funds", "")
    ).strip()

    # --------------------------------------------------------
    # 1. FUNDING HISTORY CONSISTENCY
    # --------------------------------------------------------

    if previous_funding > 0 and funding_rounds <= 0:
        risk_score += 8

        findings.append(
            create_risk_finding(
                category="Funding Risk",
                title="Funding history is inconsistent",
                description=(
                    "Previous funding is reported, but no funding "
                    "rounds have been recorded."
                ),
                severity="Medium",
                impact=(
                    "Funding information may be incomplete or inaccurate."
                ),
                recommendation=(
                    "Verify investment agreements, funding dates, "
                    "investors, and round classifications."
                ),
            )
        )

    elif previous_funding <= 0 and funding_rounds > 0:
        risk_score += 8

        findings.append(
            create_risk_finding(
                category="Funding Risk",
                title="Funding-round information is inconsistent",
                description=(
                    "Funding rounds are reported, but the previous "
                    "funding amount is zero."
                ),
                severity="Medium",
                impact=(
                    "The startup's capital history cannot be reliably assessed."
                ),
                recommendation=(
                    "Reconcile funding-round records with the amount received."
                ),
            )
        )

    elif previous_funding > 0 and funding_rounds > 0:
        positive_signals.append(
            "The startup reports an established funding history."
        )

    # --------------------------------------------------------
    # 2. EXISTING INVESTORS
    # --------------------------------------------------------

    if previous_funding > 0 and investor_count <= 0:
        risk_score += 10

        findings.append(
            create_risk_finding(
                category="Funding Risk",
                title="Previous investors not identified",
                description=(
                    "The startup reports previous funding but no "
                    "existing investors."
                ),
                severity="High",
                impact=(
                    "The funding source, governance rights, and ownership "
                    "structure may be unclear."
                ),
                recommendation=(
                    "Verify the cap table, investor agreements, and "
                    "funding sources."
                ),
            )
        )

    elif investor_count > 0 and not investor_details:
        risk_score += 6

        findings.append(
            create_risk_finding(
                category="Funding Risk",
                title="Investor details incomplete",
                description=(
                    "Existing investors are reported, but their details "
                    "were not provided."
                ),
                severity="Medium",
                impact=(
                    "Investor credibility, ownership, and potential "
                    "conflicts cannot be assessed."
                ),
                recommendation=(
                    "Collect investor names, investment amounts, dates, "
                    "and ownership rights."
                ),
            )
        )

    elif investor_count >= 3 and investor_details:
        positive_signals.append(
            "The startup reports multiple documented investors."
        )

    # --------------------------------------------------------
    # 3. VALUATION AVAILABILITY
    # --------------------------------------------------------

    if funding_sought > 0 and current_valuation <= 0:
        risk_score += 15

        findings.append(
            create_risk_finding(
                category="Funding Risk",
                title="Valuation not provided",
                description=(
                    "The startup is seeking funding without reporting "
                    "a current valuation."
                ),
                severity="High",
                impact=(
                    "The proposed investment terms and ownership dilution "
                    "cannot be evaluated."
                ),
                recommendation=(
                    "Obtain a documented valuation basis and proposed "
                    "pre-money or post-money valuation."
                ),
            )
        )

    elif current_valuation > 0:
        positive_signals.append(
            "A current startup valuation has been provided."
        )

    # --------------------------------------------------------
    # 4. FUNDING ASK RELATIVE TO VALUATION
    # --------------------------------------------------------

    if current_valuation > 0 and funding_sought > 0:
        funding_percentage = (
            funding_sought / current_valuation
        ) * 100

        if funding_percentage > 80:
            risk_score += 18

            findings.append(
                create_risk_finding(
                    category="Funding Risk",
                    title="Funding ask is extremely high relative to valuation",
                    description=(
                        "The funding sought exceeds 80 percent of the "
                        "reported valuation."
                    ),
                    severity="High",
                    impact=(
                        "The funding proposal may indicate financial "
                        "distress, unrealistic valuation, or major dilution."
                    ),
                    recommendation=(
                        "Review the valuation methodology, capital needs, "
                        "and proposed ownership structure."
                    ),
                )
            )

        elif funding_percentage > 60:
            risk_score += 12

            findings.append(
                create_risk_finding(
                    category="Funding Risk",
                    title="Funding ask is high relative to valuation",
                    description=(
                        "The funding sought exceeds 60 percent of the "
                        "reported valuation."
                    ),
                    severity="High",
                    impact=(
                        "The investment may result in substantial dilution "
                        "or indicate an aggressive funding requirement."
                    ),
                    recommendation=(
                        "Validate the funding requirement and negotiate "
                        "appropriate investment terms."
                    ),
                )
            )

        elif funding_percentage > 40:
            risk_score += 7

            findings.append(
                create_risk_finding(
                    category="Funding Risk",
                    title="Elevated funding ask",
                    description=(
                        "The funding sought exceeds 40 percent of the "
                        "reported valuation."
                    ),
                    severity="Medium",
                    impact=(
                        "The funding round may create significant ownership "
                        "and governance changes."
                    ),
                    recommendation=(
                        "Review dilution, milestone-based funding, and "
                        "capital-efficiency assumptions."
                    ),
                )
            )

        elif funding_percentage <= 20:
            positive_signals.append(
                "The funding ask is moderate relative to valuation."
            )

    # --------------------------------------------------------
    # 5. EQUITY OFFERED
    # --------------------------------------------------------

    if funding_sought > 0 and equity_offered <= 0:
        risk_score += 12

        findings.append(
            create_risk_finding(
                category="Funding Risk",
                title="Equity offer not specified",
                description=(
                    "The startup is seeking funding but has not specified "
                    "the equity offered."
                ),
                severity="High",
                impact=(
                    "The proposed investment terms cannot be assessed."
                ),
                recommendation=(
                    "Provide the proposed equity, valuation basis, "
                    "and investor rights."
                ),
            )
        )

    elif equity_offered > 50:
        risk_score += 20

        findings.append(
            create_risk_finding(
                category="Funding Risk",
                title="Excessive equity offered",
                description=(
                    "The startup is offering more than 50 percent equity."
                ),
                severity="Critical",
                impact=(
                    "Founders may lose control and future fundraising "
                    "flexibility may be significantly reduced."
                ),
                recommendation=(
                    "Review the capital structure and consider staged "
                    "funding or alternative financing."
                ),
            )
        )

    elif equity_offered > 40:
        risk_score += 14

        findings.append(
            create_risk_finding(
                category="Funding Risk",
                title="Very high equity dilution",
                description=(
                    "The startup is offering more than 40 percent equity."
                ),
                severity="High",
                impact=(
                    "Founder motivation, governance, and future dilution "
                    "may become problematic."
                ),
                recommendation=(
                    "Reassess valuation, funding size, and ownership terms."
                ),
            )
        )

    elif equity_offered > 25:
        risk_score += 8

        findings.append(
            create_risk_finding(
                category="Funding Risk",
                title="High proposed equity dilution",
                description=(
                    "The startup is offering more than 25 percent equity."
                ),
                severity="Medium",
                impact=(
                    "The round may materially reduce founder ownership."
                ),
                recommendation=(
                    "Assess whether the funding amount and valuation "
                    "justify the proposed dilution."
                ),
            )
        )

    elif 5 <= equity_offered <= 25:
        positive_signals.append(
            "The proposed equity range appears broadly reasonable."
        )

    # --------------------------------------------------------
    # 6. USE OF FUNDS
    # --------------------------------------------------------

    if funding_sought > 0 and not use_of_funds:
        risk_score += 16

        findings.append(
            create_risk_finding(
                category="Funding Risk",
                title="Use of funds not defined",
                description=(
                    "The startup has not explained how the requested "
                    "funding will be used."
                ),
                severity="High",
                impact=(
                    "Investors cannot assess capital discipline, priorities, "
                    "or expected outcomes."
                ),
                recommendation=(
                    "Provide a detailed use-of-funds plan with budgets, "
                    "timelines, and measurable milestones."
                ),
            )
        )

    elif use_of_funds:
        positive_signals.append(
            "The startup has documented its planned use of funds."
        )

    # --------------------------------------------------------
    # 7. FUNDING REQUEST WITHOUT DOCUMENTATION
    # --------------------------------------------------------

    if (
        funding_sought > 0
        and current_valuation <= 0
        and equity_offered <= 0
        and not use_of_funds
    ):
        risk_score = max(risk_score, 80)

        findings.append(
            create_risk_finding(
                category="Funding Risk",
                title="Funding proposal is materially incomplete",
                description=(
                    "The startup is seeking funding without a valuation, "
                    "equity proposal, or use-of-funds plan."
                ),
                severity="Critical",
                impact=(
                    "The investment opportunity cannot be evaluated "
                    "responsibly in its current form."
                ),
                recommendation=(
                    "Do not proceed until complete funding terms and "
                    "capital-allocation information are provided."
                ),
            )
        )

    risk_score = round(
        min(max(risk_score, 0.0), 100.0),
        2,
    )

    return {
        "score": risk_score,
        "level": classify_risk_level(risk_score),
        "findings": findings,
        "positive_signals": positive_signals,
        "source_score": clamp_source_score(funding_score),
    }

# ============================================================
# OVERALL RISK REPORT
# ============================================================

RISK_CATEGORY_WEIGHTS = {
    "Financial Health": 0.25,
    "Founders & Team": 0.15,
    "Product & Technology": 0.15,
    "Market Opportunity": 0.15,
    "Customers & Traction": 0.10,
    "Funding Position": 0.08,
    "Legal & Compliance": 0.12,
}


SEVERITY_PRIORITY = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1,
}


def _apply_manual_risk_floor(
    risk_result: dict[str, Any],
    initial_risk: str,
) -> dict[str, Any]:
    """
    Apply a minimum risk score using a manually selected
    initial-risk indicator.

    A manually reported high risk must not be hidden by
    an otherwise favourable calculated score.
    """

    manual_risk_floors = {
        "Low": 0.0,
        "Moderate": 30.0,
        "High": 55.0,
        "Information Not Available": 0.0,
    }

    result = dict(risk_result)

    current_score = _safe_float(
        result.get("score", 0.0)
    )

    minimum_score = manual_risk_floors.get(
        initial_risk,
        0.0,
    )

    adjusted_score = round(
        min(
            max(
                current_score,
                minimum_score,
                0.0,
            ),
            100.0,
        ),
        2,
    )

    result["score"] = adjusted_score
    result["level"] = classify_risk_level(adjusted_score)

    return result


def _sort_findings_by_severity(
    findings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Sort risk findings from most severe to least severe.
    """

    return sorted(
        findings,
        key=lambda finding: SEVERITY_PRIORITY.get(
            str(finding.get("severity", "Low")),
            0,
        ),
        reverse=True,
    )


def _group_findings_by_severity(
    findings: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """
    Group consolidated findings by severity.
    """

    grouped_findings: dict[
        str,
        list[dict[str, Any]],
    ] = {
        "Critical": [],
        "High": [],
        "Medium": [],
        "Low": [],
    }

    for finding in findings:
        severity = str(
            finding.get(
                "severity",
                "Low",
            )
        )

        if severity not in grouped_findings:
            severity = "Low"

        grouped_findings[severity].append(finding)

    return grouped_findings


def _count_findings_by_severity(
    findings: list[dict[str, Any]],
) -> dict[str, int]:
    """
    Count findings for each severity level.
    """

    grouped_findings = _group_findings_by_severity(
        findings
    )

    return {
        severity: len(severity_findings)
        for severity, severity_findings
        in grouped_findings.items()
    }


def _get_highest_risk_categories(
    category_risks: dict[str, dict[str, Any]],
    limit: int = 3,
) -> list[dict[str, Any]]:
    """
    Return the highest-risk categories in descending order.
    """

    sorted_categories = sorted(
        category_risks.items(),
        key=lambda item: _safe_float(
            item[1].get("score", 0.0)
        ),
        reverse=True,
    )

    highest_risks: list[dict[str, Any]] = []

    for category, result in sorted_categories[:limit]:
        highest_risks.append(
            {
                "category": category,
                "score": round(
                    _safe_float(
                        result.get("score", 0.0)
                    ),
                    2,
                ),
                "level": result.get(
                    "level",
                    "Low",
                ),
                "finding_count": len(
                    result.get(
                        "findings",
                        [],
                    )
                ),
            }
        )

    return highest_risks


def _get_overall_risk_level(
    adjusted_score: float,
    critical_findings: list[dict[str, Any]],
) -> str:
    """
    Determine the overall risk level.

    Any critical finding forces the final level to Critical,
    even when the weighted score is lower.
    """

    if critical_findings:
        return "Critical"

    return classify_risk_level(adjusted_score)


def _get_risk_review_status(
    overall_level: str,
) -> str:
    """
    Convert the overall risk level into a due-diligence
    review status.
    """

    status_mapping = {
        "Low": (
            "Standard Due Diligence"
        ),
        "Moderate": (
            "Enhanced Review Recommended"
        ),
        "High": (
            "Major Risks Require Resolution"
        ),
        "Critical": (
            "Do Not Proceed Until Critical Risks Are Resolved"
        ),
    }

    return status_mapping.get(
        overall_level,
        "Enhanced Review Recommended",
    )


def calculate_overall_risk(
    startup_record: dict[str, Any],
    scoring_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Calculate the complete startup risk report.

    Parameters
    ----------
    startup_record:
        Complete startup information saved from the
        Streamlit startup form.

    scoring_result:
        Result returned by calculate_due_diligence_scores().

    Returns
    -------
    dict
        Complete category-level and overall risk report.
    """

    category_scores = scoring_result.get(
        "category_scores",
        {},
    )

    initial_risks = startup_record.get(
        "initial_risks",
        {},
    )

    # --------------------------------------------------------
    # 1. FINANCIAL RISK
    # --------------------------------------------------------

    financial_risk = analyze_financial_risk(
        startup_record.get(
            "financial",
            {},
        ),
        startup_record.get(
            "calculated_metrics",
            {},
        ),
    )

    financial_risk = _apply_manual_risk_floor(
        financial_risk,
        str(
            initial_risks.get(
                "financial_risk",
                "Information Not Available",
            )
        ),
    )

    # --------------------------------------------------------
    # 2. TEAM RISK
    # --------------------------------------------------------

    team_risk = analyze_team_risk(
        team_data=startup_record.get(
            "founders_and_team",
            {},
        ),
        team_score=_safe_float(
            category_scores.get(
                "Founders & Team",
                0.0,
            )
        ),
        initial_risk=str(
            initial_risks.get(
                "team_risk",
                "Information Not Available",
            )
        ),
    )

    # --------------------------------------------------------
    # 3. PRODUCT AND TECHNOLOGY RISK
    # --------------------------------------------------------

    product_risk = analyze_product_technology_risk(
        product_data=startup_record.get(
            "product",
            {},
        ),
        product_score=_safe_float(
            category_scores.get(
                "Product & Technology",
                0.0,
            )
        ),
        initial_risk=str(
            initial_risks.get(
                "technology_risk",
                "Information Not Available",
            )
        ),
    )

    # --------------------------------------------------------
    # 4. MARKET RISK
    # --------------------------------------------------------

    market_risk = analyze_market_risk(
        market_data=startup_record.get(
            "market",
            {},
        ),
        market_score=_safe_float(
            category_scores.get(
                "Market Opportunity",
                0.0,
            )
        ),
        initial_risk=str(
            initial_risks.get(
                "market_risk",
                "Information Not Available",
            )
        ),
    )

    # --------------------------------------------------------
    # 5. CUSTOMER AND TRACTION RISK
    # --------------------------------------------------------

    customer_risk = analyze_customer_risk(
        customer_data=startup_record.get(
            "customers",
            {},
        ),
        customer_score=_safe_float(
            category_scores.get(
                "Customers & Traction",
                0.0,
            )
        ),
        initial_risk=str(
            initial_risks.get(
                "customer_risk",
                "Information Not Available",
            )
        ),
    )

    # --------------------------------------------------------
    # 6. FUNDING RISK
    # --------------------------------------------------------

    funding_risk = analyze_funding_risk(
        funding_data=startup_record.get(
            "funding",
            {},
        ),
        funding_score=_safe_float(
            category_scores.get(
                "Funding Position",
                0.0,
            )
        ),
    )

    # --------------------------------------------------------
    # 7. LEGAL AND COMPLIANCE RISK
    # --------------------------------------------------------

    compliance_result = scoring_result.get(
        "compliance_result",
        {},
    )

    compliance_risk = analyze_compliance_risk(
        startup_record.get(
            "compliance",
            {},
        ),
        compliance_result,
    )

    compliance_risk = _apply_manual_risk_floor(
        compliance_risk,
        str(
            initial_risks.get(
                "legal_risk",
                "Information Not Available",
            )
        ),
    )

    # --------------------------------------------------------
    # 8. CATEGORY RISK RESULTS
    # --------------------------------------------------------

    category_risks = {
        "Financial Health": financial_risk,
        "Founders & Team": team_risk,
        "Product & Technology": product_risk,
        "Market Opportunity": market_risk,
        "Customers & Traction": customer_risk,
        "Funding Position": funding_risk,
        "Legal & Compliance": compliance_risk,
    }

    # --------------------------------------------------------
    # 9. WEIGHTED RISK SCORE
    # --------------------------------------------------------

    weighted_risk_score = sum(
        _safe_float(
            category_risks[category].get(
                "score",
                0.0,
            )
        )
        * RISK_CATEGORY_WEIGHTS[category]
        for category in RISK_CATEGORY_WEIGHTS
    )

    weighted_risk_score = round(
        min(
            max(
                weighted_risk_score,
                0.0,
            ),
            100.0,
        ),
        2,
    )

    # --------------------------------------------------------
    # 10. CONSOLIDATE FINDINGS
    # --------------------------------------------------------

    all_findings: list[dict[str, Any]] = []

    all_positive_signals: list[dict[str, str]] = []

    for category, result in category_risks.items():
        category_findings = result.get(
            "findings",
            [],
        )

        for finding in category_findings:
            finding_copy = dict(finding)

            if not finding_copy.get("category"):
                finding_copy["category"] = category

            all_findings.append(finding_copy)

        for positive_signal in result.get(
            "positive_signals",
            [],
        ):
            all_positive_signals.append(
                {
                    "category": category,
                    "signal": str(positive_signal),
                }
            )

    sorted_findings = _sort_findings_by_severity(
        all_findings
    )

    grouped_findings = _group_findings_by_severity(
        sorted_findings
    )

    severity_counts = _count_findings_by_severity(
        sorted_findings
    )

    critical_findings = grouped_findings["Critical"]
    high_findings = grouped_findings["High"]

    # --------------------------------------------------------
    # 11. CRITICAL-RISK OVERRIDES
    # --------------------------------------------------------

    adjusted_risk_score = weighted_risk_score

    override_applied = False
    override_reasons: list[str] = []

    critical_category_names = sorted(
        {
            str(
                finding.get(
                    "category",
                    "Unknown",
                )
            )
            for finding in critical_findings
        }
    )

    if critical_findings:
        adjusted_risk_score = max(
            adjusted_risk_score,
            75.0,
        )

        override_applied = True

        override_reasons.append(
            "One or more critical risk findings were identified."
        )

    very_high_risk_categories = [
        category
        for category, result in category_risks.items()
        if _safe_float(
            result.get(
                "score",
                0.0,
            )
        ) >= 80
    ]

    if very_high_risk_categories:
        adjusted_risk_score = max(
            adjusted_risk_score,
            70.0,
        )

        override_applied = True

        override_reasons.append(
            "At least one risk category has a score of "
            "80 or above."
        )

    if len(high_findings) >= 5:
        adjusted_risk_score = max(
            adjusted_risk_score,
            60.0,
        )

        override_applied = True

        override_reasons.append(
            "Five or more high-severity findings were identified."
        )

    adjusted_risk_score = round(
        min(
            max(
                adjusted_risk_score,
                0.0,
            ),
            100.0,
        ),
        2,
    )

    overall_risk_level = _get_overall_risk_level(
        adjusted_score=adjusted_risk_score,
        critical_findings=critical_findings,
    )

    # --------------------------------------------------------
    # 12. RISK SUMMARY
    # --------------------------------------------------------

    highest_risk_categories = (
        _get_highest_risk_categories(
            category_risks=category_risks,
            limit=3,
        )
    )

    risk_summary = {
        "total_findings": len(sorted_findings),
        "critical_findings": severity_counts["Critical"],
        "high_findings": severity_counts["High"],
        "medium_findings": severity_counts["Medium"],
        "low_findings": severity_counts["Low"],
        "positive_signal_count": len(
            all_positive_signals
        ),
        "highest_risk_categories": highest_risk_categories,
        "critical_categories": critical_category_names,
        "very_high_risk_categories": (
            very_high_risk_categories
        ),
    }

    # --------------------------------------------------------
    # 13. FINAL REPORT
    # --------------------------------------------------------

    return {
        "category_risks": category_risks,
        "category_weights": RISK_CATEGORY_WEIGHTS,
        "weighted_risk_score": weighted_risk_score,
        "overall_risk_score": adjusted_risk_score,
        "overall_risk_level": overall_risk_level,
        "review_status": _get_risk_review_status(
            overall_risk_level
        ),
        "override_applied": override_applied,
        "override_reasons": override_reasons,
        "all_findings": sorted_findings,
        "findings_by_severity": grouped_findings,
        "positive_signals": all_positive_signals,
        "risk_summary": risk_summary,
    }


def generate_risk_report(
    startup_record: dict[str, Any],
    scoring_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Public convenience function for generating the complete
    startup risk report.

    This function currently delegates to calculate_overall_risk()
    and provides a clearer name for dashboards, PDF reports,
    and recommendation modules.
    """

    return calculate_overall_risk(
        startup_record=startup_record,
        scoring_result=scoring_result,
    )