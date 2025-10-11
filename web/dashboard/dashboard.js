// dashboard.js

// Get JWT token
const token = localStorage.getItem('jwtToken');
if (!token) {
  window.location.href = './index.html';
}

// DOM elements
const usernameEl = document.getElementById('username');
const avatarEl = document.getElementById('userAvatar');

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
fetchUserInfo();


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

  // Example upload placeholder logic
  alert(`Uploaded: ${file.name}`);
  uploadModal.style.display = 'none';
});
