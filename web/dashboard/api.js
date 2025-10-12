// api.js
export async function fetchUserFiles(token) {
  try {
    const response = await fetch('/userfiles/user/files', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) throw new Error('Failed to fetch user files');

    return await response.json();
  } catch (err) {
    console.error(err);
    return [];
  }
}

export async function processPDF(file, token) {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/process-pdf/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
        //  Do NOT set Content-Type here — fetch adds it automatically for FormData
      },
      body: formData
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to process PDF: ${errorText}`);
    }

    const data = await response.json();
    return data; // JSON response from backend
  } catch (err) {
    console.error('Error uploading PDF:', err);
    return { error: err.message };
  }
}

