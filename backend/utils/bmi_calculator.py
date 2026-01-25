def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate BMI from weight and height"""
    if height_cm <= 0 or weight_kg <= 0:
        return 0.0
    
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)

def get_bmi_category(bmi: float) -> str:
    """Get BMI category"""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def get_diet_recommendation(bmi: float) -> str:
    """Get diet recommendation based on BMI"""
    if bmi < 18.5:
        return "high-calorie"
    elif bmi < 25:
        return "balanced"
    elif bmi < 30:
        return "low-calorie"
    else:
        return "low-fat"
