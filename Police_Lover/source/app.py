from flask import Flask, render_template, request
import whois
import ssl
import socket
from datetime import datetime
import nlp
import ph_num
import fraud_ph_num

app = Flask(__name__)

# Route for landing page
@app.route('/')
def index():
    return render_template('index.html')  # This will render index.html first

# Route for form submission (where URL analysis happens)
@app.route('/url', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        url = request.form['url']
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        domain_info = get_domain_info(url)
        print("Domain info:", domain_info)  # Debugging output
        ssl_status = check_ssl(url)

        fraud_ph_exists = False
        phone_numbers = ph_num.full_phone_numbers_function(url)
        addable_numbers =  []
        for country_code, number in phone_numbers:
            if(fraud_ph_num.check_fraud(number, country_code)):
                fraud_ph_exists = True
            else:
                tempNum = []
                tempNum.append(number)
                tempNum.append(country_code)
                addable_numbers.append(tempNum)

        if fraud_ph_exists:
            total_score = 0
            risk_level = categorize_risk(total_score)
        else:
            # Calculate risk score
            trusted_domains = [".gov.in", ".edu.in", ".ac.in", ".co.in", ".org.in"]
            trusted = False
            for trusted_domain in trusted_domains:
                if url.endswith(trusted_domain):
                    trusted = True
                    break
            if trusted:
                score_1 = 100
                risk_level = categorize_risk(score_1)
            else:
                score_1, risk_level = evaluate_risk(domain_info, ssl_status)

            total_score = (score_1 * 0.7 + nlp.full_function(url, (score_1 < 50)) * 0.3)
            risk_level = categorize_risk(total_score)

            if total_score > 75:
                fraud_ph_num.more_entries(addable_numbers)

        return render_template('results.html', domain_info=domain_info, ssl_status=ssl_status, total_score=total_score, risk_level=risk_level)

    return render_template('url.html')  # Render url.html to display the form


# Route for Customer Care
@app.route('/customer_care', methods=['GET', 'POST'])
def customer_care():
    if request.method == 'POST':
        code = request.form['countryCode']
        id = request.form['phoneNumber']
        is_fraud = fraud_ph_num.check_fraud(id, code)
        if(is_fraud):
            mes = "The number is Fradulent"
        else:
            mes = "The number is not detected as Fradulent"
        return render_template('submit.html', mes=mes) 

    return render_template('customer_care.html')  # Render customer_care.html

@app.route('/about')
def about():
    return render_template('about.html')  # Make sure you have an about.html in the templates folder


@app.route('/submit' , methods=['GET'])
def submit():
    return render_template('submit.html', is_fraud=None) 


# Functions get_domain_info, check_ssl, categorize_risk, evaluate_risk remain unchanged
def get_domain_info(url):
    try:
        domain = whois.whois(url)
        return {
            'domain': domain.domain_name,
            'registrar': domain.registrar,
            'creation_date': domain.creation_date,
            'expiration_date': domain.expiration_date,
        }
    except Exception as e:
        print(f"Error retrieving domain info: {e}")  # Debugging output
        return {'error': 'Could not retrieve domain information'}

def check_ssl(url):
    try:
        # Create a connection to the server
        context = ssl.create_default_context()
        conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=url)
        conn.settimeout(5.0)
        
        # Connect to the server using port 443 (HTTPS)
        conn.connect((url, 443))
        
        # Get the server's SSL certificate
        cert = conn.getpeercert()
        
        # Extract certificate validity dates
        cert_valid_from = cert['notBefore']
        cert_valid_to = cert['notAfter']
        
        # Parse the validity dates into datetime objects
        valid_from = datetime.strptime(cert_valid_from, '%b %d %H:%M:%S %Y %Z')
        valid_to = datetime.strptime(cert_valid_to, '%b %d %H:%M:%S %Y %Z')
        
        # Check if the certificate is currently valid
        current_date = datetime.utcnow()
        if valid_from <= current_date <= valid_to:
            return {
                'valid': True,
                'valid_from': valid_from.strftime('%Y-%m-%d'),
                'valid_to': valid_to.strftime('%Y-%m-%d')
            }
        else:
            return {
                'valid': False,
                'valid_from': valid_from.strftime('%Y-%m-%d'),
                'valid_to': valid_to.strftime('%Y-%m-%d'),
                'error': 'SSL certificate has expired.'
            }
        
    except Exception as e:
        return {'error': str(e)}

def categorize_risk(score):
    if score >= 75:
        return "Low Risk"
    elif score >= 50:
        return "Medium Risk"
    else:
        return "High Risk"

def evaluate_risk(domain_info, ssl_info):
    weight_domain = 50
    weight_ssl = 50
    
    domain_score = 0
    # Ensure valid domain data
    if 'error' not in domain_info:
        if domain_info['creation_date']:
            # Calculate domain age and assign score
            try:
                domain_age = (datetime.now() - domain_info['creation_date']).days
                domain_score += min(domain_age / 365, 1) * weight_domain
            except Exception as e:
                print(f"Error in domain age calculation: {e}")
        else:
            print("No valid creation date found.")
        
        # Bonus score for trusted registrar (this is just an example check)
        if domain_info['registrar'] and "godaddy" in domain_info['registrar'].lower():
            domain_score += weight_domain * 0.5
    
    # Calculate SSL score
    ssl_score = weight_ssl if ssl_info.get('valid', False) else 0

    # Add these print statements for debugging
    print(f"Domain Info: {domain_info}")  # Print domain info data
    print(f"SSL Info: {ssl_info}")  # Print SSL info data
    print(f"Domain Score: {domain_score}")  # Print domain score
    print(f"SSL Score: {ssl_score}")  # Print SSL score
    
    total_weight = weight_domain + weight_ssl
    total_score = (domain_score + ssl_score) / total_weight * 100
    
    # Print final score and risk level for debugging
    print(f"Total Score: {total_score}")
    
    risk_level = categorize_risk(total_score)
    
    print(f"Risk Level: {risk_level}")  # Print risk level
    
    return total_score, risk_level

class FraudDetection:
    def __init__(self):
        self.weights = {
            "legitimacy_verification": 0.7,
            "authenticity_evaluation": 0.3
            # "contact_checking": 0.2,
            # "continuous_improvement": 0.2
        }
        self.results = {
            "legitimacy_verification": 0,
            "authenticity_evaluation": 0
            # "contact_checking": 0,
            # "continuous_improvement": 0
        }
        
    def update_result(self, step, percentage):
        if step in self.results:
            self.results[step] = percentage
            
    def calculate_overall_percentage(self):
        total_score = sum((self.results[step] / 100) * self.weights[step] for step in self.results)
        return total_score * 100  # Convert back to percentage
    
    def risk_o_meter(self, percentage):
        if percentage >= 75:
            return "Low Risk (Green)"
        elif 50 <= percentage < 75:
            return "Moderate Risk (Yellow)"
        else:
            return "High Risk (Red)"
    
    def analyze(self):
        overall_percentage = self.calculate_overall_percentage()
        risk_level = self.risk_o_meter(overall_percentage)
        return overall_percentage, risk_level
    
if __name__ == '__main__':
    app.run(debug=True)
