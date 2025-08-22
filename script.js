// UI Navigation
function showForm(formType) {
    document.getElementById('landingPage').style.display = 'none';
    document.getElementById('formSection').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
    // Hide all forms
    document.getElementById('bodyMakerForm').style.display = 'none';
    document.getElementById('bodyMaintainerForm').style.display = 'none';
    document.getElementById('weightLossForm').style.display = 'none';
    // Show selected form
    if (formType === 'bodyMaker') {
        document.getElementById('bodyMakerForm').style.display = 'block';
    } else if (formType === 'bodyMaintainer') {
        document.getElementById('bodyMaintainerForm').style.display = 'block';
    } else if (formType === 'weightLoss') {
        document.getElementById('weightLossForm').style.display = 'block';
    }
}

function showLanding() {
    document.getElementById('landingPage').style.display = 'block';
    document.getElementById('formSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
}

function showResults() {
    document.getElementById('landingPage').style.display = 'none';
    document.getElementById('formSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';
    document.getElementById('loading').style.display = 'block';
    document.getElementById('resultsContent').style.display = 'none';
}

// Form Submission Handlers
function handleFormSubmit(formId, goal) {
    const form = document.getElementById(formId);
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const userData = {};
        formData.forEach((value, key) => {
            userData[key] = value;
        });
        showResults();
        fetch('/generate-plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ goal: goal, userData: userData })
        })
        .then(res => res.json())
        .then(data => {
            setTimeout(() => { // Simulate loading
                document.getElementById('loading').style.display = 'none';
                if (data.success) {
                    renderResults(goal, userData, data.plan);
                } else {
                    document.getElementById('resultsContent').innerHTML = '<p>Sorry, something went wrong.</p>';
                    document.getElementById('resultsContent').style.display = 'block';
                }
            }, 1200);
        })
        .catch(() => {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('resultsContent').innerHTML = '<p>Network error. Please try again.</p>';
            document.getElementById('resultsContent').style.display = 'block';
        });
    });
}

// Render Results
function renderResults(goal, userData, plan) {
    // Plan Title
    let planTitle = '';
    if (goal === 'body-maker') planTitle = 'Body Maker Plan';
    else if (goal === 'body-maintainer') planTitle = 'Body Maintainer Plan';
    else if (goal === 'weight-loss') planTitle = 'Weight Loss Plan';
    else planTitle = 'Personalized Plan';
    document.getElementById('planTitle').textContent = planTitle;

    // BMI Info (if possible)
    let bmiHtml = '';
    if (userData.height && userData.weight) {
        const heightM = parseFloat(userData.height) / 100;
        const weight = parseFloat(userData.weight);
        if (heightM > 0 && weight > 0) {
            const bmi = (weight / (heightM * heightM)).toFixed(1);
            let bmiStatus = '';
            if (bmi < 18.5) bmiStatus = 'Underweight';
            else if (bmi < 25) bmiStatus = 'Normal';
            else if (bmi < 30) bmiStatus = 'Overweight';
            else bmiStatus = 'Obese';
            bmiHtml = `<strong>BMI:</strong> ${bmi} (${bmiStatus})`;
        }
    }
    document.getElementById('bmiInfo').innerHTML = bmiHtml;

    // Diet Plan
    let dietHtml = `<ul>`;
    plan.meals.forEach(meal => {
        dietHtml += `<li>${meal}</li>`;
    });
    dietHtml += `</ul>`;
    dietHtml += `<p><strong>Calories:</strong> ${plan.calories} kcal | <strong>Protein:</strong> ${plan.protein}g | <strong>Carbs:</strong> ${plan.carbs}g | <strong>Fats:</strong> ${plan.fats}g</p>`;
    document.getElementById('dietContent').innerHTML = dietHtml;

    // Workout Plan
    let workoutHtml = `<ul>`;
    plan.exercises.forEach(ex => {
        workoutHtml += `<li>${ex.name} <span style=\"color:#888;\">(${ex.sets})</span></li>`;
    });
    workoutHtml += `</ul>`;
    document.getElementById('workoutContent').innerHTML = workoutHtml;

    // Suggestions (optional)
    if (plan.suggestions) {
        workoutHtml += `<h4>Tips:</h4><ul>`;
        plan.suggestions.forEach(s => {
            workoutHtml += `<li>${s}</li>`;
        });
        workoutHtml += `</ul>`;
        document.getElementById('workoutContent').innerHTML = workoutHtml;
    }

    // Progress Tracker (simple mock)
    const todayScore = plan.exercises.reduce((sum, ex) => sum + (ex.points || 0), 0);
    document.getElementById('todayScore').textContent = todayScore;
    document.getElementById('targetScore').textContent = 100;
    renderProgressChart(todayScore, 100);

    document.getElementById('resultsContent').style.display = 'block';
}

// Progress Chart (simple bar)
function renderProgressChart(today, target) {
    const ctx = document.getElementById('progressChart').getContext('2d');
    if (window.progressChartInstance) window.progressChartInstance.destroy();
    window.progressChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Today', 'Target'],
            datasets: [{
                label: 'Score',
                data: [today, target],
                backgroundColor: ['#667eea', '#ffd700']
            }]
        },
        options: {
            responsive: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, max: 100 } }
        }
    });
}

// Attach form handlers on DOMContentLoaded
window.addEventListener('DOMContentLoaded', function() {
    handleFormSubmit('bodyMakerInputs', 'body-maker');
    handleFormSubmit('bodyMaintainerInputs', 'body-maintainer');
    handleFormSubmit('weightLossInputs', 'weight-loss');
});

// Load Chart.js dynamically if not present
(function loadChartJs() {
    if (!window.Chart) {
        var script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
        script.onload = function() { /* Chart.js loaded */ };
        document.head.appendChild(script);
    }
})();