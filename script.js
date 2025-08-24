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
            // Convert numeric fields to numbers
            if (["height", "weight", "age", "target_weight"].includes(key)) {
                userData[key] = Number(value);
            } else {
                userData[key] = value;
            }
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

    // BMI Info
    let bmiHtml = '';
    if (plan.bmi && plan.bmi_category) {
        bmiHtml = `<strong>BMI:</strong> ${plan.bmi} (${plan.bmi_category})`;
    }
    document.getElementById('bmiInfo').innerHTML = bmiHtml;


    // Diet Plan & Meal Adjustments
    let dietHtml = '';
    if (plan.optimized_meal && Object.keys(plan.optimized_meal).length > 0) {
        dietHtml += `<div class=\"meal-item animated-flipIn\">
            <h4><i class=\"fas fa-seedling\"></i> Optimized Meal Plan</h4>
            <ul>`;
        Object.entries(plan.optimized_meal).forEach(([food, servings]) => {
            dietHtml += `<li>${food}: <strong>${servings}</strong> servings</li>`;
        });
        dietHtml += `</ul></div>`;
    }
    if (plan.nutrition) {
        dietHtml += `<div class=\"nutrition-info\">
            <p><strong>Calories:</strong> ${plan.nutrition.daily_calories} kcal</p>
            <p><strong>Protein:</strong> ${plan.nutrition.protein_g}g | <strong>Carbs:</strong> ${plan.nutrition.carbs_g}g | <strong>Fats:</strong> ${plan.nutrition.fats_g}g</p>
        </div>`;
    }
    if (!dietHtml) {
        dietHtml = `<div class='empty-section'>No diet plan data available.</div>`;
    }
    document.getElementById('dietContent').innerHTML = dietHtml;

    // Meal Adjustments (before/after)

    let workoutHtml = '';
    if (plan.workout_schedule && plan.workout_schedule.length > 0) {
        workoutHtml += `<ul class=\"animated-fadeIn\">`;
        plan.workout_schedule.forEach(day => {
            workoutHtml += `<li><strong>${day.day}:</strong> ${day.focus} <span style=\"color:#888;\">(${day.duration})</span></li>`;
        });
        workoutHtml += `</ul>`;
    }
    if (plan.activity_recommendations && plan.activity_recommendations.length > 0) {
        workoutHtml += `<h4>Activity Recommendations</h4><ul>`;
        plan.activity_recommendations.forEach(rec => {
            workoutHtml += `<li>${rec}</li>`;
        });
        workoutHtml += `</ul>`;
    }
    if (plan.cardio_plan && plan.cardio_plan.length > 0) {
        workoutHtml += `<h4>Cardio Plan</h4><ul>`;
        plan.cardio_plan.forEach(rec => {
            workoutHtml += `<li>${rec}</li>`;
        });
        workoutHtml += `</ul>`;
    }
    if (!workoutHtml) {
        workoutHtml = `<div class='empty-section'>No workout plan data available.</div>`;
    }
    document.getElementById('workoutContent').innerHTML = workoutHtml;

    // Periodized Block
    let blockHtml = '';
    if (plan.periodized_block) {
        blockHtml += `<div class="periodized-block-visual animated-flipIn">
            <h4>Periodized Mesocycle</h4>
            <table class="period-table"><tr><th>Week</th><th>Phase</th><th>Sets</th></tr>`;
        plan.periodized_block.forEach(w => {
            blockHtml += `<tr><td>${w.week}</td><td>${w.phase}</td><td>${w.sets}</td></tr>`;
        });
        blockHtml += `</table></div>`;
    }
    document.getElementById('periodizedBlock').innerHTML = blockHtml;

    // Readiness Info
    let readinessHtml = '';
    if (plan.readiness !== undefined) {
        readinessHtml += `<div class="readiness-bar animated-fadeIn">
            <span>Readiness Score: <strong>${plan.readiness}</strong></span>
            <div class="readiness-bar-outer"><div class="readiness-bar-inner" style="width:${plan.readiness}%;"></div></div>
        </div>`;
        if (plan.auto_deload) {
            readinessHtml += `<div class="deload-alert animated-pulse"><i class="fas fa-exclamation-triangle"></i> Auto Deload Triggered!</div>`;
        }
    }
    document.getElementById('readinessInfo').innerHTML = readinessHtml;

    // Explainability
    let explainHtml = '';
    if (plan.explainability && plan.explainability.length > 0) {
        plan.explainability.forEach(exp => {
            explainHtml += `<div class="explain-card animated-fadeIn">
                <strong>${exp.type.toUpperCase()}</strong><br>
                <span class="explain-formula">Formula: <code>${exp.formula}</code></span><br>
                <span class="explain-inputs">Inputs: <code>${JSON.stringify(exp.inputs)}</code></span><br>
                <span class="explain-delta">Delta: <code>${JSON.stringify(exp.delta)}</code></span>
            </div>`;
        });
    }
    document.getElementById('explainabilityContent').innerHTML = explainHtml;

    // Progress Tracker (simple mock)
    let todayScore = 0;
    if (plan.exercises && Array.isArray(plan.exercises)) {
        todayScore = plan.exercises.reduce((sum, ex) => sum + (ex.points || 0), 0);
    }
    document.getElementById('todayScore').textContent = todayScore;
    document.getElementById('targetScore').textContent = 100;
    renderProgressChart(todayScore, 100);

    // Animate results in
    document.getElementById('resultsContent').style.display = 'block';
    document.getElementById('resultsContent').classList.add('animated-fadeIn');
}
// Ensure functions are globally available
window.showForm = showForm;
window.showLanding = showLanding;
window.handleFormSubmit = handleFormSubmit;
window.renderResults = renderResults;
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
    console.log('DOM loaded, attaching form handlers...');
    const forms = [
        {id: 'bodyMakerInputs', goal: 'body-maker'},
        {id: 'bodyMaintainerInputs', goal: 'body-maintainer'},
        {id: 'weightLossInputs', goal: 'weight-loss'}
    ];
    forms.forEach(f => {
        const form = document.getElementById(f.id);
        if (form) {
            console.log('Attaching handler to', f.id);
            handleFormSubmit(f.id, f.goal);
        } else {
            console.warn('Form not found:', f.id);
        }
    });
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
// End of script.js