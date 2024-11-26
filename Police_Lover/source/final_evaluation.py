import nlp


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

# Example usage:
fraud_detection = FraudDetection()

# Update results for each step with hypothetical percentages
fraud_detection.update_result("legitimacy_verification", 100)  # Example: 80% successful verification
fraud_detection.update_result("authenticity_evaluation", nlp.probability_of_fraud)  # Example: 70% successful evaluation
# fraud_detection.update_result("contact_checking", 100)  # Example: 60% successful checking
# fraud_detection.update_result("continuous_improvement", 100)  # Example: 90% improvement

# Analyze the overall percentage and risk level
overall_percentage, risk_level = fraud_detection.analyze()
print(f"Overall Percentage: {overall_percentage:.2f}%")
print(f"Risk Level: {risk_level}")
