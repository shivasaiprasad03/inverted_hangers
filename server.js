const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('.'));

// Serve the main HTML file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Mock AI service endpoint (since Python AI service won't work in WebContainer)
app.post('/generate-plan', (req, res) => {
    const { goal, userData } = req.body;
    
    // Mock response with realistic fitness data
    const mockPlans = {
        'body-maker': {
            calories: 2800,
            protein: 150,
            carbs: 300,
            fats: 90,
            meals: [
                "Breakfast: 3 eggs, 2 slices whole grain toast, 1 banana, protein shake",
                "Lunch: 200g chicken breast, 150g rice, mixed vegetables",
                "Snack: Greek yogurt with berries and nuts",
                "Dinner: 200g salmon, sweet potato, broccoli",
                "Post-workout: Protein shake with banana"
            ],
            exercises: [
                { name: "Deadlifts", sets: "4x6-8", points: 25 },
                { name: "Bench Press", sets: "4x8-10", points: 20 },
                { name: "Squats", sets: "4x8-10", points: 20 },
                { name: "Pull-ups", sets: "3x8-12", points: 15 },
                { name: "Overhead Press", sets: "3x8-10", points: 15 },
                { name: "Barbell Rows", sets: "3x8-10", points: 15 }
            ],
            suggestions: [
                "Focus on progressive overload - increase weight gradually",
                "Get 7-9 hours of sleep for optimal recovery",
                "Stay hydrated - aim for 3-4 liters of water daily",
                "Consider creatine supplementation (3-5g daily)"
            ]
        },
        'body-maintainer': {
            calories: 2200,
            protein: 110,
            carbs: 220,
            fats: 80,
            meals: [
                "Breakfast: Oatmeal with fruits and nuts",
                "Lunch: Grilled chicken salad with quinoa",
                "Snack: Apple with almond butter",
                "Dinner: Lean beef with vegetables and brown rice",
                "Evening: Greek yogurt"
            ],
            exercises: [
                { name: "Push-ups", sets: "3x12-15", points: 15 },
                { name: "Bodyweight Squats", sets: "3x15-20", points: 15 },
                { name: "Plank", sets: "3x45-60s", points: 10 },
                { name: "Lunges", sets: "3x12 each leg", points: 15 },
                { name: "Mountain Climbers", sets: "3x30s", points: 15 },
                { name: "Burpees", sets: "3x8-10", points: 20 }
            ],
            suggestions: [
                "Maintain consistent workout schedule",
                "Balance cardio and strength training",
                "Monitor portion sizes to maintain weight",
                "Stay active throughout the day"
            ]
        },
        'weight-loss': {
            calories: 1800,
            protein: 120,
            carbs: 150,
            fats: 70,
            meals: [
                "Breakfast: Vegetable omelet with spinach",
                "Lunch: Grilled fish with steamed vegetables",
                "Snack: Handful of almonds",
                "Dinner: Chicken breast with cauliflower rice",
                "Evening: Herbal tea"
            ],
            exercises: [
                { name: "HIIT Cardio", sets: "20 minutes", points: 25 },
                { name: "Jump Rope", sets: "3x2 minutes", points: 20 },
                { name: "Burpees", sets: "4x10", points: 20 },
                { name: "Mountain Climbers", sets: "4x30s", points: 15 },
                { name: "High Knees", sets: "4x30s", points: 10 },
                { name: "Walking", sets: "30 minutes", points: 10 }
            ],
            suggestions: [
                "Create a calorie deficit of 500-750 calories daily",
                "Drink water before meals to help with satiety",
                "Include more fiber-rich foods in your diet",
                "Track your food intake for better awareness"
            ]
        }
    };

    const plan = mockPlans[goal] || mockPlans['body-maintainer'];
    
    res.json({
        success: true,
        plan: plan
    });
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});