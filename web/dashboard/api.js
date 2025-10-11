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
