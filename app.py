from flask import Flask, request, jsonify
from ai_service import create_fitness_plan
import os

app = Flask(__name__)

# Set your Gemini API key here
API_KEY = "API KEY"

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    data = request.get_json()
    goal = data.get('goal')
    user_data = data.get('userData')
    if not goal or not user_data:
        return jsonify({'success': False, 'error': 'Missing goal or user data'}), 400
    # Map frontend goal to backend plan_type
    plan_type_map = {
        'body-maker': 'body_maker',
        'body-maintainer': 'body_maintainer',
        'weight-loss': 'weight_loss'
    }
    plan_type = plan_type_map.get(goal, goal)
    try:
        plan = create_fitness_plan(plan_type, user_data, API_KEY)
        return jsonify({'success': True, 'plan': plan})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
