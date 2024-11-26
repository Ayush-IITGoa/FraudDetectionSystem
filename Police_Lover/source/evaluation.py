from datetime import datetime

def evaluate_legitimacy(domain_info, ssl_info):
    weight_domain = 50
    weight_ssl = 50
    
    # Calculate domain score
    domain_score = 0
    if 'error' not in domain_info:
        if domain_info['creation_date']:
            domain_age = (datetime.now() - domain_info['creation_date']).days
            domain_score += min(domain_age / 365, 1) * weight_domain  # Normalize to weight
        if domain_info['registrar'] and "trusted_registrar" in domain_info['registrar'].lower():
            domain_score += weight_domain * 0.5  # Example trusted registrar check

    # Calculate SSL score
    ssl_score = weight_ssl if ssl_info.get('valid', False) else 0

    # Total score calculation
    total_weight = weight_domain + weight_ssl
    total_score = (domain_score + ssl_score) / total_weight * 100

    # Determine risk level
    risk_level = categorize_risk(total_score)

    return total_score, risk_level

def categorize_risk(score):
    if score >= 75:
        return "Low Risk"
    elif score >= 50:
        return "Medium Risk"
    else:
        return "High Risk"
