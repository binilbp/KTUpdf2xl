import { fetchUserFiles, processPDF } from "./api.js";

// --- JWT Auth ---
const token = localStorage.getItem('jwtToken');
if (!token) {
  window.location.href = './index.html';
}

// --- DOM Elements ---
const usernameEl = document.getElementById('username');
const avatarEl = document.getElementById('userAvatar');

// --- Chart Variables ---
let topChartInstance = null;
let bottomChartInstance = null;
let currentIndex = 0;
let JSONdata = [];

// === PIE CHART FUNCTIONS ===
function renderPieChart(index) {
  const ctx = document.getElementById("pieChart").getContext("2d");
  const dept = JSONdata[index];

  if (bottomChartInstance) bottomChartInstance.destroy();

  bottomChartInstance = new Chart(ctx, {
    type: "pie",
    data: {
      labels: ["Pass", "Fail"],
      datasets: [{
        data: [dept.PassCount, dept.FailCount],
        backgroundColor: ["#4CAF50", "#F44336"]
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: `${dept.Department}`
        }
      }
    }
  });

  renderPaginationBullets();
}

function nextChart() {
  currentIndex = (currentIndex + 1) % JSONdata.length;
  renderPieChart(currentIndex);
}

function prevChart() {
  currentIndex = (currentIndex - 1 + JSONdata.length) % JSONdata.length;
  renderPieChart(currentIndex);
}

function renderPaginationBullets() {
  const pagination = document.getElementById('paginationBullets');
  pagination.innerHTML = '';

  JSONdata.forEach((_, i) => {
    const bullet = document.createElement('span');
    bullet.className = 'bullet' + (i === currentIndex ? ' active' : '');
    pagination.appendChild(bullet);
  });
}

// === MAIN CHART RENDER FUNCTION ===
function renderPieCharts(chartsData) {
  const topChartEl = document.querySelector('.chart-left');
  const bottomChartEl = document.querySelector('.bottom-chart');

  // Reset content
  topChartEl.innerHTML = '';
  bottomChartEl.innerHTML = '';

  if (!chartsData || chartsData.length === 0) {
    topChartEl.textContent = 'No chart data available';
    bottomChartEl.textContent = 'No chart data available';
    return;
  }

  // Save dataset globally
  JSONdata = chartsData;
  currentIndex = 0;

  // === BAR CHART ===
  topChartEl.innerHTML = '<canvas id="topChartCanvas"></canvas>';
  const bar_ctx = document.getElementById('topChartCanvas').getContext('2d');

  if (topChartInstance) topChartInstance.destroy();

  topChartInstance = new Chart(bar_ctx, {
    type: 'bar',
    data: {
      labels: chartsData.map(d => d.Department),
      datasets: [{
        label: 'Pass Percentage',
        data: chartsData.map(d => d.PassPercentage),
        backgroundColor: "#5874C6",
        borderColor: '#fff',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 900, easing: 'easeOutCubic' },
      plugins: {
        tooltip: {
          callbacks: {
            label: context => {
              const label = context.label || '';
              const value = context.parsed.y || 0;
              return `${label}: ${value}%`;
            }
          }
        },
        legend: {
          display: true,
          position: 'top',
          labels: { boxWidth: 20, padding: 15 }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: { display: true, text: 'Pass Percentage' }
        },
        x: {
          title: { display: true, text: 'Department' }
        }
      }
    }
  });

  // === PIE CHART + CONTROLS ===
  bottomChartEl.innerHTML = `
    <div class="chart-controls">
      <button id="prevChart">◀ Prev</button>
      <canvas id="pieChart" width="300" height="300"></canvas>
      <button id="nextChart">Next ▶</button>
    </div>
    <div id="paginationBullets" class="pagination"></div>
  `;

  renderPieChart(currentIndex);
  document.getElementById('prevChart').addEventListener('click', prevChart);
  document.getElementById('nextChart').addEventListener('click', nextChart);
}

// === FETCH USER FILES ===
async function renderUserFiles() {
  const files = await fetchUserFiles(token);
  const listEl = document.getElementById('fileList');
  listEl.innerHTML = '';

  if (!files.length) {
    listEl.innerHTML = '<li>No files uploaded yet</li>';
    return;
  }

  files.forEach(f => {
    const li = document.createElement('li');
    li.textContent = f.filename;
    li.addEventListener('click', () => {
      renderPieCharts(f.json_charts);
    });
    listEl.appendChild(li);
  });
}

// === FETCH USER INFO ===
async function fetchUserInfo() {
  try {
    const response = await fetch('/protected', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    const result = await response.json();

    if (response.ok) {
      const user = result.data;
      const name = user.user_name || 'User';
      usernameEl.textContent = name;
      avatarEl.textContent = name.charAt(0).toUpperCase();
    } else {
      localStorage.removeItem('jwtToken');
      window.location.href = './index.html';
    }
  } catch (err) {
    console.error('Error fetching user info:', err);
    localStorage.removeItem('jwtToken');
    window.location.href = './index.html';
  }
}

// === PAGE LOAD ===
fetchUserInfo().then(renderUserFiles);

// === UPLOAD MODAL LOGIC ===
const openModalBtn = document.getElementById('openModalBtn');
const uploadModal = document.getElementById('uploadModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const confirmUpload = document.getElementById('confirmUpload');
const pdfFile = document.getElementById('pdfFile');

// Open modal
openModalBtn.addEventListener('click', () => {
  uploadModal.style.display = 'flex';
});

// Close modal
closeModalBtn.addEventListener('click', () => {
  uploadModal.style.display = 'none';
});

// Close when clicking outside
window.addEventListener('click', (e) => {
  if (e.target === uploadModal) {
    uploadModal.style.display = 'none';
  }
});

// Handle confirm upload
confirmUpload.addEventListener('click', async () => {
  const file = pdfFile.files[0];
  if (!file) {
    alert('Please select a PDF file before confirming.');
    return;
  }

  confirmUpload.disabled = true;
  confirmUpload.textContent = 'Processing...';

  try {
    const result = await processPDF(file, token);
    console.log('Server Response:', result);

    if (result.error) {
      alert('Failed to process PDF: ' + result.error);
    } else {
      alert('PDF processed successfully!');
      if (result.json_charts) renderPieCharts(result.json_charts);
      await renderUserFiles();
    }
  } catch (err) {
    alert('Error uploading PDF: ' + err.message);
  } finally {
    confirmUpload.disabled = false;
    confirmUpload.textContent = 'Confirm';
    uploadModal.style.display = 'none';
    pdfFile.value = '';
  }
});
