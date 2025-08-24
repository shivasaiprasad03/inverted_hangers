import os
import json
from datetime import datetime
import google.generativeai as genai

import numpy as np
from scipy.optimize import linprog

class FitnessAI:
    def __init__(self, api_key):
        # For adaptive coaching state (could be persisted in production)
        self.ema_weight = None
        self.ema_perf = None
        self.ema_readiness = None
        self.readiness_history = []
        self.last_pid_error = 0
        self.pid_integral = 0
        # Configure Gemini API key and model
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('models/gemini-1.0-pro')
    # --- Adaptive Coaching Core ---
    def update_ema(self, prev_ema, value, alpha=0.3):
        if prev_ema is None:
            return value
        return alpha * value + (1 - alpha) * prev_ema

    def pid_adjustment(self, target, actual, last_error, integral, kp=0.7, ki=0.1, kd=0.2, bounds=(-400, 400)):
        error = target - actual
        integral += error
        derivative = error - last_error
        output = kp * error + ki * integral + kd * derivative
        output = max(bounds[0], min(bounds[1], output))
        return output, error, integral

    def readiness_score(self, sleep_hrs, hr_rest, soreness, last_3d_vol):
        # Normalize and weight inputs, then EMA
        score = (
            0.4 * min(sleep_hrs / 8, 1.0) +
            0.2 * (1 - min(hr_rest / 80, 1.0)) +
            0.2 * (1 - min(soreness / 10, 1.0)) +
            0.2 * (1 - min(last_3d_vol / 5, 1.0))
        ) * 100
        self.ema_readiness = self.update_ema(self.ema_readiness, score, alpha=0.4)
        self.readiness_history.append(self.ema_readiness)
        return round(self.ema_readiness, 1)

    def auto_deload(self, threshold=60):
        # If readiness drops below threshold for 3+ days, trigger deload
        if len(self.readiness_history) >= 3 and all(r < threshold for r in self.readiness_history[-3:]):
            return True
        return False

    def periodized_workout_block(self, weeks=10, start_sets=10, fatigue_budget=100):
        # Simple periodization: Hypertrophy (4w), Strength (3w), Power (2w), Deload (1w)
        phases = ["Hypertrophy"]*4 + ["Strength"]*3 + ["Power"]*2 + ["Deload"]
        block = []
        sets = start_sets
        for i, phase in enumerate(phases[:weeks]):
            if phase == "Deload":
                sets = max(4, int(sets * 0.5))
            else:
                sets = min(sets + 2, fatigue_budget // weeks)
            block.append({"week": i+1, "phase": phase, "sets": sets})
        return block

    # --- Meal/Macro Optimization (Linear Programming) ---
    def optimize_meal_plan(self, pantry, macros_target, cost_dict, prev_meal=None, tolerance=0.05):
        # pantry: list of foods, each with macros per serving
        # macros_target: dict with 'protein', 'carbs', 'fats' (grams)
        # cost_dict: dict of food: cost per serving
        # prev_meal: dict of food: servings (for repetition penalty)
        n = len(pantry)
        prot = np.array([f['protein'] for f in pantry])
        carbs = np.array([f['carbs'] for f in pantry])
        fats = np.array([f['fats'] for f in pantry])
        cost = np.array([cost_dict.get(f['name'], 1) for f in pantry])
        rep_penalty = np.zeros(n)
        if prev_meal:
            for i, f in enumerate(pantry):
                rep_penalty[i] = 2 if prev_meal.get(f['name'], 0) > 0 else 0
        c = cost + rep_penalty
        # Constraints: macros within tolerance
        A = [prot, carbs, fats, -prot, -carbs, -fats]
        b = [
            macros_target['protein'] * (1 + tolerance),
            macros_target['carbs'] * (1 + tolerance),
            macros_target['fats'] * (1 + tolerance),
            -macros_target['protein'] * (1 - tolerance),
            -macros_target['carbs'] * (1 - tolerance),
            -macros_target['fats'] * (1 - tolerance)
        ]
        bounds = [(0, 5)] * n
        res = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')
        servings = res.x if res.success else [0]*n
        meal = {pantry[i]['name']: round(servings[i],2) for i in range(n) if servings[i]>0.1}
        explain = {
            'success': res.success,
            'cost': float(res.fun) if res.success else None,
            'status': res.message,
            'servings': meal
        }
        return meal, explain

    # --- Explainability Layer ---
    def explain_adjustment(self, adj_type, formula, inputs, delta):
        return {
            'type': adj_type,
            'formula': formula,
            'inputs': inputs,
            'delta': delta
        }
    
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
            print("[Gemini API] Raw response:", response)
            print("[Gemini API] Response text:", getattr(response, 'text', None))
            return self._parse_ai_response(response.text, 'body_maker', user_data)
        except Exception as e:
            print("[Gemini API] Exception occurred:", str(e))
            import traceback
            traceback.print_exc()
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
        bmr = self.calculate_bmr(user_data['weight'], user_data['height'], user_data['age'], user_data['gender'])
        plan = {
            'title': f'Your AI-Generated {plan_type.replace("_", " ").title()} Plan',
            'bmi': bmi,
            'bmi_category': bmi_category,
            'bmr': round(bmr),
            'ai_analysis': ai_response,
            'generated_at': datetime.now().isoformat(),
            'plan_type': plan_type,
            'explainability': []
        }
        # Adaptive feedback control (example: calories)
        if 'weight_trend' in user_data and 'target_weight_trend' in user_data:
            self.ema_weight = self.update_ema(self.ema_weight, user_data['weight_trend'])
            adj, err, integ = self.pid_adjustment(user_data['target_weight_trend'], self.ema_weight, self.last_pid_error, self.pid_integral)
            self.last_pid_error = err
            self.pid_integral = integ
            plan['calorie_adjustment'] = int(adj)
            plan['explainability'].append(self.explain_adjustment(
                'calorie',
                'PID: Kp*e + Ki*∑e + Kd*Δe',
                {'target': user_data['target_weight_trend'], 'actual': self.ema_weight, 'last_error': self.last_pid_error},
                adj
            ))
        # Readiness & auto deload
        if all(k in user_data for k in ['sleep_hrs','hr_rest','soreness','last_3d_vol']):
            readiness = self.readiness_score(user_data['sleep_hrs'], user_data['hr_rest'], user_data['soreness'], user_data['last_3d_vol'])
            plan['readiness'] = readiness
            plan['auto_deload'] = self.auto_deload()
            plan['explainability'].append(self.explain_adjustment(
                'readiness',
                '0.4*sleep/8 + 0.2*(1-HR/80) + 0.2*(1-soreness/10) + 0.2*(1-vol/5)',
                {k: user_data[k] for k in ['sleep_hrs','hr_rest','soreness','last_3d_vol']},
                readiness
            ))
        # Periodized block
        if user_data.get('periodize', False):
            block = self.periodized_workout_block()
            plan['periodized_block'] = block
            plan['explainability'].append(self.explain_adjustment(
                'periodization',
                'Algorithmic mesocycle: Hypertrophy→Strength→Power→Deload',
                {'weeks': 10, 'start_sets': 10, 'fatigue_budget': 100},
                block
            ))
        # Meal/macro optimization
        if 'pantry' in user_data and 'macros_target' in user_data and 'cost_dict' in user_data:
            meal, explain = self.optimize_meal_plan(user_data['pantry'], user_data['macros_target'], user_data['cost_dict'], user_data.get('prev_meal'))
            plan['optimized_meal'] = meal
            plan['meal_optimization_explain'] = explain
            plan['explainability'].append(self.explain_adjustment(
                'meal_optimization',
                'Linear programming: min(cost+repetition) s.t. macros≈target',
                {'macros_target': user_data['macros_target']},
                meal
            ))
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
        explainability = [
            self.explain_adjustment(
                'nutrition',
                'BMR*activity, protein=weight*1.6',
                {'bmr': bmr, 'weight': user_data['weight']},
                {
                    'daily_calories': round(bmr * 1.5),
                    'protein_g': round(user_data['weight'] * 1.6),
                    'carbs_g': 200,
                    'fats_g': 70
                }
            )
        ]
        if plan_type == 'body_maker':
            workout_schedule = [
                {'day': 'Monday', 'focus': 'Chest & Triceps', 'duration': '60-75 min'},
                {'day': 'Tuesday', 'focus': 'Back & Biceps', 'duration': '60-75 min'},
                {'day': 'Wednesday', 'focus': 'Legs', 'duration': '75-90 min'},
                {'day': 'Thursday', 'focus': 'Shoulders', 'duration': '45-60 min'},
                {'day': 'Friday', 'focus': 'Arms', 'duration': '45-60 min'},
                {'day': 'Saturday', 'focus': 'Cardio/Core', 'duration': '30-45 min'},
                {'day': 'Sunday', 'focus': 'Rest', 'duration': 'Recovery'}
            ]
            explainability.append(self.explain_adjustment(
                'workout',
                'Standard split routine',
                {},
                workout_schedule
            ))
            extra = {'workout_schedule': workout_schedule}
        elif plan_type == 'body_maintainer':
            activity_recommendations = [
                '150 minutes moderate cardio per week',
                '2-3 strength training sessions',
                'Daily walking (8,000-10,000 steps)',
                'Flexibility/yoga 2-3 times per week'
            ]
            explainability.append(self.explain_adjustment(
                'activity',
                'General health maintenance',
                {},
                activity_recommendations
            ))
            extra = {'activity_recommendations': activity_recommendations}
        elif plan_type == 'weight_loss':
            cardio_plan = [
                'HIIT training 3x per week (20-25 min)',
                'Steady-state cardio 2x per week (30-45 min)',
                'Daily walking (10,000+ steps)',
                'Active recovery on rest days'
            ]
            explainability.append(self.explain_adjustment(
                'cardio',
                'Standard weight loss cardio',
                {},
                cardio_plan
            ))
            extra = {'cardio_plan': cardio_plan}
        else:
            extra = {}
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
            },
            'explainability': explainability,
            **extra
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