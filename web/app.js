document.addEventListener('DOMContentLoaded', () => {
    // --- GLOBAL CHART & DATA VARIABLES ---
    let gradeAnalyticsChart = null;
    let passFailChart = null;
    let dashboardData = null;
    let currentSubjectIndex = 0;

    // --- DOM ELEMENT REFERENCES ---
    const prevSubjectBtn = document.getElementById('prev-subject');
    const nextSubjectBtn = document.getElementById('next-subject');
    
    // --- CHART BACKGROUND PLUGIN ---
    const chartBackgroundColor = {
      id: 'chartBackgroundColor',
      beforeDraw: (chart, args, options) => {
        if (options.color) {
          const {ctx} = chart;
          ctx.save();
          ctx.globalCompositeOperation = 'destination-over';
          ctx.fillStyle = options.color;
          ctx.fillRect(0, 0, chart.width, chart.height);
          ctx.restore();
        }
      }
    };
    Chart.register(chartBackgroundColor);

    // --- DATA FETCH & INITIALIZATION ---
    async function initializeDashboard() {
        try {
            const response = await fetch('data.json');
            if (!response.ok) throw new Error('Network response was not ok.');
            dashboardData = await response.json();
            
            renderDashboard(dashboardData);
            document.getElementById('branch-select').addEventListener('change', () => renderDashboard(dashboardData));
            setupNavListeners();
        } catch (error) {
            console.error('Failed to fetch and render dashboard data:', error);
        }
    }

    function renderDashboard(data) {
        updateSummaryCard(data.summary);
        updateGradeAnalyticsChart(data.courses);
        if (data.courses.length > 0) {
            currentSubjectIndex = 0;
            updatePassFailChart(data.courses[currentSubjectIndex]);
            updateNavButtons();
        }
    }

    // --- CHART UPDATE FUNCTIONS ---
    function updateSummaryCard(summary) {
        document.getElementById('summary-percentage').textContent = `${summary.passPercentage.toFixed(1)}%`;
    }

    function updateGradeAnalyticsChart(courses) {
        const ctx = document.getElementById('grade-analytics-chart').getContext('2d');
        const labels = courses.map(course => course.code);
        const data = courses.map(course => course.passPercentage);
        if (gradeAnalyticsChart) gradeAnalyticsChart.destroy();

        gradeAnalyticsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Pass %', data, backgroundColor: '#001f3f',
                    borderRadius: 8, barPercentage: 0.6,
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                scales: {
                    x: { grid: { display: false }, ticks: { color: 'var(--text-secondary)' } },
                    y: {
                        min: 0, max: 100,
                        grid: { color: 'var(--border-color)' },
                        ticks: {
                            color: 'var(--text-secondary)', stepSize: 10,
                            callback: value => {
                                const grades = { 100:'S', 90:'A+', 80:'A', 70:'B+', 60:'B', 50:'C', 40:'P', 0:'F' };
                                return grades[value] ?? ''; // Return grade or empty string
                            }
                        }
                    }
                },
                plugins: {
                    legend: { display: false }, tooltip: { enabled: true },
                    chartBackgroundColor: { color: 'transparent' } // Use transparent BG inside merged card
                }
            }
        });
    }

    function updatePassFailChart(course) {
        document.getElementById('current-subject-name').textContent = course.code;
        const passed = course.pass;
        const failed = course.fail;
        const total = passed + failed;
        const passPercentage = total > 0 ? (passed / total) * 100 : 0;
        
        // Update the center text
        document.getElementById('donut-center-text').querySelector('.donut-percentage').textContent = `${passPercentage.toFixed(0)}%`;

        // Update the new legend counts
        document.getElementById('total-passed').textContent = passed;
        document.getElementById('total-failed').textContent = failed;

        const ctx = document.getElementById('pass-fail-chart').getContext('2d');
        if (passFailChart) passFailChart.destroy();

        passFailChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [passed, failed],
                    // Explicitly setting Green and Red colors
                    backgroundColor: [
                        '#28a745', // --pass-color
                        '#dc3545'  // --fail-color
                    ],
                    borderWidth: 0,
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, cutout: '80%', plugins: { legend: { display: false }, tooltip: { enabled: true } } }
        });
    }
    
    // --- NAVIGATION LOGIC ---
    function setupNavListeners() {
        prevSubjectBtn.addEventListener('click', () => {
            if (currentSubjectIndex > 0) {
                currentSubjectIndex--;
                updatePassFailChart(dashboardData.courses[currentSubjectIndex]);
                updateNavButtons();
            }
        });
        nextSubjectBtn.addEventListener('click', () => {
            if (currentSubjectIndex < dashboardData.courses.length - 1) {
                currentSubjectIndex++;
                updatePassFailChart(dashboardData.courses[currentSubjectIndex]);
                updateNavButtons();
            }
        });
    }

    function updateNavButtons() {
        prevSubjectBtn.disabled = currentSubjectIndex === 0;
        nextSubjectBtn.disabled = currentSubjectIndex === dashboardData.courses.length - 1;
    }
    
    // --- UPLOAD & REPORT FLOW LOGIC (UNCHANGED) ---
    // This section remains identical to the previous version
    const dropZone = document.getElementById('drop-zone'), fileInput = document.getElementById('file-input');
    const uploadPreview = document.getElementById('upload-preview'), fileList = document.getElementById('file-list');
    const uploadError = document.getElementById('upload-error'), submitBtn = document.getElementById('submit-btn');
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', e => { e.preventDefault(); dropZone.classList.remove('dragover'); handleFiles(e.dataTransfer.files); });
    fileInput.addEventListener('change', () => handleFiles(fileInput.files));
    function handleFiles(files) { uploadError.hidden = true; if (files.length === 0) return; const file = files[0]; if (file.type !== 'application/pdf') { uploadError.textContent = 'Error: Only PDF files are accepted.'; uploadError.hidden = false; return; } fileList.innerHTML = `<li>${file.name} (${(file.size / 1024).toFixed(1)} KB)</li>`; dropZone.hidden = true; uploadPreview.hidden = false; }
    submitBtn.addEventListener('click', () => { uploadPreview.hidden = true; dropZone.hidden = false; fileInput.value = ''; triggerReportGeneration(); });
    function triggerReportGeneration() { const reportInitial = document.getElementById('report-initial-state'); const reportLoading = document.getElementById('report-loading-state'); const reportFinal = document.getElementById('report-final-state'); const loaderProgress = reportLoading.querySelector('.loader-progress'); const loaderPercentage = document.getElementById('loader-percentage'); reportInitial.hidden = true; reportLoading.hidden = false; reportFinal.hidden = true; let progress = 0; const circumference = 2 * Math.PI * 45; loaderProgress.style.strokeDashoffset = circumference; const interval = setInterval(() => { progress += 2; if (progress > 100) progress = 100; loaderPercentage.textContent = `${Math.floor(progress)}%`; const offset = circumference - (progress / 100) * circumference; loaderProgress.style.strokeDashoffset = offset; if (progress >= 100) { clearInterval(interval); setTimeout(() => { reportLoading.hidden = true; reportFinal.hidden = false; }, 500); } }, 60); }
    const downloadBtn = document.getElementById('download-btn');
    downloadBtn.addEventListener('click', () => { const content = "Simulated yearly report. Processed on: " + new Date().toUTCString(); const blob = new Blob([content], { type: 'text/plain' }); const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'Yearly-Report.txt'; a.click(); URL.revokeObjectURL(a.href); });

    // --- START THE APP ---
    initializeDashboard();
});