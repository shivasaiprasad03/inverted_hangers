import os
import json
from datetime import datetime
import google.generativeai as genai

class FitnessAI:
    def __init__(self, api_key):
        """Initialize the Fitness AI with Gemini API key"""
        genai.configure(api_key=AIzaSyAFe5o_UlsUkVQ3ZJo4w0VZPRChSgKnrDQ)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def calculate_bmi(self, height_cm, weight_kg):
        """Calculate BMI and return category"""
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        
        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal weight"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"
            
        return round(bmi, 1), category
    
    def calculate_bmr(self, weight, height, age, gender):
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
        if gender.lower() == 'male':
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        return bmr
    
    def generate_body_maker_plan(self, user_data):
        """Generate a comprehensive body building plan using Gemini AI"""
        
        prompt = f"""
        Create a detailed body building plan for a {user_data['age']}-year-old {user_data['gender']} 
        who is {user_data['height']}cm tall, weighs {user_data['weight']}kg, 
        has {user_data['fitness_level']} fitness level, and wants to achieve {user_data['goal']}.
        
        Please provide:
        1. Daily calorie requirements with macronutrient breakdown
        2. Detailed meal plan with 4-5 meals including specific foods and portions
        3. Weekly workout routine with specific exercises, sets, and reps
        4. Supplement recommendations
        5. Recovery and rest day suggestions
        6. Progress tracking metrics
        
        Format the response as a structured plan with clear sections.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_ai_response(response.text, 'body_maker', user_data)
        except Exception as e:
            return self._generate_fallback_plan('body_maker', user_data)
    
    def generate_body_maintainer_plan(self, user_data):
        """Generate a maintenance plan using Gemini AI"""
        
        prompt = f"""
        Create a body maintenance plan for a {user_data['age']}-year-old {user_data['gender']} 
        who is {user_data['height']}cm tall, weighs {user_data['weight']}kg, 
        follows a {user_data['diet_type']} diet, and has {user_data['activity_level']} activity level.
        
        Please provide:
        1. Daily calorie requirements for maintenance
        2. Balanced meal plan suitable for {user_data['diet_type']} diet
        3. Moderate exercise routine for maintenance
        4. Lifestyle recommendations
        5. Health monitoring suggestions
        
        Format the response as a structured maintenance plan.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_ai_response(response.text, 'body_maintainer', user_data)
        except Exception as e:
            return self._generate_fallback_plan('body_maintainer', user_data)
    
    def generate_weight_loss_plan(self, user_data):
        """Generate a weight loss plan using Gemini AI"""
        
        prompt = f"""
        Create a weight loss plan for a {user_data['age']}-year-old {user_data['gender']} 
        who is {user_data['height']}cm tall, currently weighs {user_data['weight']}kg, 
        wants to reach {user_data['target_weight']}kg in {user_data['timeline']}.
        
        Current eating habits: {user_data['food_habits']}
        
        Please provide:
        1. Safe weekly weight loss target
        2. Daily calorie deficit calculation
        3. Detailed meal plan with portion control
        4. High-intensity workout routine for fat loss
        5. Cardio recommendations
        6. Behavioral change suggestions
        7. Progress tracking methods
        
        Format the response as a comprehensive weight loss plan.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_ai_response(response.text, 'weight_loss', user_data)
        except Exception as e:
            return self._generate_fallback_plan('weight_loss', user_data)
    
    def _parse_ai_response(self, ai_response, plan_type, user_data):
        """Parse AI response and structure it for the frontend"""
        
        bmi, bmi_category = self.calculate_bmi(user_data['height'], user_data['weight'])
        bmr = self.calculate_bmr(user_data['weight'], user_data['height'], 
                                user_data['age'], user_data['gender'])
        
        # This is a simplified parser - in a real implementation, 
        # you would use more sophisticated NLP to extract structured data
        
        plan = {
            'title': f'Your AI-Generated {plan_type.replace("_", " ").title()} Plan',
            'bmi': bmi,
            'bmi_category': bmi_category,
            'bmr': round(bmr),
            'ai_analysis': ai_response,
            'generated_at': datetime.now().isoformat(),
            'plan_type': plan_type
        }
        
        # Add specific structured data based on plan type
        if plan_type == 'body_maker':
            plan.update(self._structure_body_maker_data(user_data, bmr))
        elif plan_type == 'body_maintainer':
            plan.update(self._structure_maintainer_data(user_data, bmr))
        elif plan_type == 'weight_loss':
            plan.update(self._structure_weight_loss_data(user_data, bmr))
        
        return plan
    
    def _structure_body_maker_data(self, user_data, bmr):
        """Structure body maker specific data"""
        daily_calories = round(bmr * 1.7)  # Active lifestyle
        protein = round(user_data['weight'] * 2.2)  # High protein for muscle building
        
        return {
            'nutrition': {
                'daily_calories': daily_calories,
                'protein_g': protein,
                'carbs_g': round(daily_calories * 0.45 / 4),
                'fats_g': round(daily_calories * 0.25 / 9)
            },
            'workout_schedule': [
                {'day': 'Monday', 'focus': 'Chest & Triceps', 'duration': '60-75 min'},
                {'day': 'Tuesday', 'focus': 'Back & Biceps', 'duration': '60-75 min'},
                {'day': 'Wednesday', 'focus': 'Legs', 'duration': '75-90 min'},
                {'day': 'Thursday', 'focus': 'Shoulders', 'duration': '45-60 min'},
                {'day': 'Friday', 'focus': 'Arms', 'duration': '45-60 min'},
                {'day': 'Saturday', 'focus': 'Cardio/Core', 'duration': '30-45 min'},
                {'day': 'Sunday', 'focus': 'Rest', 'duration': 'Recovery'}
            ]
        }
    
    def _structure_maintainer_data(self, user_data, bmr):
        """Structure maintenance specific data"""
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'very': 1.725
        }
        
        daily_calories = round(bmr * activity_multipliers.get(user_data['activity_level'], 1.4))
        protein = round(user_data['weight'] * 1.6)
        
        return {
            'nutrition': {
                'daily_calories': daily_calories,
                'protein_g': protein,
                'carbs_g': round(daily_calories * 0.50 / 4),
                'fats_g': round(daily_calories * 0.25 / 9)
            },
            'activity_recommendations': [
                '150 minutes moderate cardio per week',
                '2-3 strength training sessions',
                'Daily walking (8,000-10,000 steps)',
                'Flexibility/yoga 2-3 times per week'
            ]
        }
    
    def _structure_weight_loss_data(self, user_data, bmr):
        """Structure weight loss specific data"""
        maintenance_calories = round(bmr * 1.4)
        daily_calories = maintenance_calories - 500  # 500 calorie deficit
        protein = round(user_data['weight'] * 1.8)  # Higher protein for satiety
        
        weight_to_lose = user_data['weight'] - user_data['target_weight']
        timeline_weeks = {'3months': 12, '6months': 24, '1year': 52}
        weekly_loss = weight_to_lose / timeline_weeks.get(user_data['timeline'], 24)
        
        return {
            'nutrition': {
                'daily_calories': daily_calories,
                'protein_g': protein,
                'carbs_g': round(daily_calories * 0.40 / 4),
                'fats_g': round(daily_calories * 0.25 / 9),
                'calorie_deficit': 500
            },
            'weight_loss_projection': {
                'target_weekly_loss': round(weekly_loss, 1),
                'total_to_lose': weight_to_lose,
                'timeline': user_data['timeline']
            },
            'cardio_plan': [
                'HIIT training 3x per week (20-25 min)',
                'Steady-state cardio 2x per week (30-45 min)',
                'Daily walking (10,000+ steps)',
                'Active recovery on rest days'
            ]
        }
    
    def _generate_fallback_plan(self, plan_type, user_data):
        """Generate a basic plan if AI service fails"""
        bmi, bmi_category = self.calculate_bmi(user_data['height'], user_data['weight'])
        bmr = self.calculate_bmr(user_data['weight'], user_data['height'], 
                                user_data['age'], user_data['gender'])
        
        return {
            'title': f'Your {plan_type.replace("_", " ").title()} Plan',
            'bmi': bmi,
            'bmi_category': bmi_category,
            'bmr': round(bmr),
            'ai_analysis': 'AI service temporarily unavailable. Basic plan generated.',
            'generated_at': datetime.now().isoformat(),
            'plan_type': plan_type,
            'nutrition': {
                'daily_calories': round(bmr * 1.5),
                'protein_g': round(user_data['weight'] * 1.6),
                'carbs_g': 200,
                'fats_g': 70
            }
        }

# Example usage and API endpoint simulation
def create_fitness_plan(plan_type, user_data, api_key):
    """Main function to create fitness plans"""
    
    if not api_key:
        raise ValueError("Gemini API key is required")
    
    fitness_ai = FitnessAI(api_key)
    
    if plan_type == 'body_maker':
        return fitness_ai.generate_body_maker_plan(user_data)
    elif plan_type == 'body_maintainer':
        return fitness_ai.generate_body_maintainer_plan(user_data)
    elif plan_type == 'weight_loss':
        return fitness_ai.generate_weight_loss_plan(user_data)
    else:
        raise ValueError("Invalid plan type")

# Example usage
if __name__ == "__main__":
    # Example user data for body maker
    sample_data = {
        'height': 175,
        'weight': 70,
        'age': 25,
        'gender': 'male',
        'fitness_level': 'intermediate',
        'goal': 'muscle-gain'
    }
    
    # You would need to set your actual Gemini API key
    # api_key = "your-gemini-api-key-here"
    # plan = create_fitness_plan('body_maker', sample_data, api_key)
    # print(json.dumps(plan, indent=2))