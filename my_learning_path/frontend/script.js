let topics = [];
let path = [];

// Build topics from URLs
const graphForm = document.getElementById('graphForm');
graphForm.onsubmit = async function(e) {
    e.preventDefault();
    document.getElementById('topicsSection').style.display = 'none';
    document.getElementById('pathSection').style.display = 'none';
    const urls = document.getElementById('urls').value.split('\n').map(u => u.trim()).filter(u => u);
    const res = await fetch('http://127.0.0.1:8000/build_graph', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ urls })
    });
    const data = await res.json();
    if (data.nodes) {
        topics = data.nodes;
        if (topics.length === 0) {
            alert('No topics found. Try different links.');
            return;
        }
        const topicsList = document.getElementById('topicsList');
        topicsList.innerHTML = '';
        topics.forEach(t => {
            const li = document.createElement('li');
            li.textContent = t;
            topicsList.appendChild(li);
        });
        // Populate selects
        const startSel = document.getElementById('startTopic');
        const goalSel = document.getElementById('goalTopic');
        startSel.innerHTML = '';
        goalSel.innerHTML = '';
        topics.forEach(t => {
            let opt1 = document.createElement('option');
            opt1.value = opt1.textContent = t;
            startSel.appendChild(opt1);
            let opt2 = document.createElement('option');
            opt2.value = opt2.textContent = t;
            goalSel.appendChild(opt2);
        });
        document.getElementById('topicsSection').style.display = '';
    } else {
        alert(data.detail || 'Error building topics.');
    }
};

// Find path
const pathForm = document.getElementById('pathForm');
pathForm.onsubmit = async function(e) {
    e.preventDefault();
    document.getElementById('pathSection').style.display = 'none';
    const start = document.getElementById('startTopic').value;
    const goal = document.getElementById('goalTopic').value;
    const weights = { time: 0.3, cognitive: 0.3, prereq: 0.2, interest: 0.2 };
    const res = await fetch('http://127.0.0.1:8000/find_path', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ start, goal, weights })
    });
    const data = await res.json();
    if (data.path) {
        path = data.path;
        const pathResult = document.getElementById('pathResult');
        pathResult.innerHTML = '';
        path.forEach((step, i) => {
            const span = document.createElement('span');
            span.className = 'path-step';
            span.textContent = step;
            pathResult.appendChild(span);
            if (i < path.length - 1) pathResult.appendChild(document.createTextNode('→'));
        });
        // Populate learned topic select
        const learnedSel = document.getElementById('learnedTopic');
        learnedSel.innerHTML = '';
        path.forEach(t => {
            let opt = document.createElement('option');
            opt.value = opt.textContent = t;
            learnedSel.appendChild(opt);
        });
        document.getElementById('pathSection').style.display = '';
    } else {
        document.getElementById('pathResult').innerHTML = '<span class="error">' + (data.detail || 'No path found.') + '</span>';
    }
};

// Mark topic as learned
const progressForm = document.getElementById('progressForm');
progressForm.onsubmit = async function(e) {
    e.preventDefault();
    const concept_id = document.getElementById('learnedTopic').value;
    const mastery = 1.0;
    const res = await fetch('http://127.0.0.1:8000/update_learner', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ concept_id, mastery })
    });
    const data = await res.json();
    document.getElementById('progressResult').innerHTML = data.knowledge_state ?
        '<span class="success">Marked as learned!</span>' :
        '<span class="error">' + (data.detail || 'Error updating progress.') + '</span>';
};
