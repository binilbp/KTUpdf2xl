import { fetchUserFiles, processPDF } from "./api.js";

// Get JWT token
const token = localStorage.getItem('jwtToken');
if (!token) {
  window.location.href = './index.html';
}

// DOM elements
const usernameEl = document.getElementById('username');
const avatarEl = document.getElementById('userAvatar');

function renderCharts(chartsData) {
    const topChartEl = document.querySelector('.chart-left');
    const bottomChartEl = document.querySelector('.bottom-chart p');

    // Clear previous content
    topChartEl.innerHTML = '';
    bottomChartEl.innerHTML = '';

    if (!chartsData || chartsData.length === 0) {
        topChartEl.textContent = 'No chart data available';
        bottomChartEl.textContent = 'No chart data available';
        return;
    }

    // --- TOP CHART (Bar Chart) ---
    topChartEl.innerHTML = '<canvas id="topChartCanvas"></canvas>';
    const bar_ctx = document.getElementById('topChartCanvas').getContext('2d');

    // Destroy previous chart if exists
    if (window.topChart) window.topChart.destroy();

    window.topChart = new Chart(bar_ctx, {
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
            animation: {
                duration: 900,
                easing: 'easeOutCubic'
            },
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

    // --- BOTTOM CHART (Placeholder) ---
    bottomChartEl.textContent = JSON.stringify(chartsData, null, 2);
}


// Fetch and render user files
async function renderUserFiles() {
  const files = await fetchUserFiles(token);
  const listEl = document.getElementById('fileList');
  listEl.innerHTML = ''; // Clear current list

  files.forEach(f => {
    const li = document.createElement('li');
    li.textContent = f.filename;

    //click handler
    li.addEventListener('click', () => {
      renderCharts(f.json_charts);
    });

    listEl.appendChild(li);
  });
}

// Fetch user info from backend
async function fetchUserInfo() {  //only api call tht lives here add others to api.js
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

// Run on page load
fetchUserInfo().then(renderUserFiles);;


// MODAL LOGIC
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

// Close when clicking outside modal
window.addEventListener('click', (e) => {
  if (e.target === uploadModal) {
    uploadModal.style.display = 'none';
  }
});

// Handle confirm
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
      // If the server returns chart data, update UI dynamically:
      if (result.json_charts) {
        renderCharts(result.json_charts);
      }
      // Optionally refresh user files list
      await renderUserFiles();
    }
  } catch (err) {
    alert('Error uploading PDF: ' + err.message);
  } finally {
    confirmUpload.disabled = false;
    confirmUpload.textContent = 'Confirm';
    uploadModal.style.display = 'none';
    pdfFile.value = ''; // Reset input
  }
});

