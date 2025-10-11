let isLogin = true; // toggle state

const toggleBtn = document.getElementById('toggleForm');
const formTitle = document.getElementById('formTitle');
const submitBtn = document.getElementById('submitBtn');

toggleBtn.addEventListener('click', () => {
    isLogin = !isLogin;

    document.getElementById('user_name').style.display = isLogin ? 'none' : 'block';
    document.getElementById('institution').style.display = isLogin ? 'none' : 'block';
    document.getElementById('designation').style.display = isLogin ? 'none' : 'block';

    formTitle.textContent = isLogin ? 'Login' : 'Sign Up';
    submitBtn.textContent = isLogin ? 'Login' : 'Sign Up';
    toggleBtn.textContent = isLogin ? 'Sign up' : 'Login';
});

document.getElementById('authForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();
    const messageEl = document.getElementById('message');

    messageEl.textContent = '';

    try {
        if (isLogin) {
            // --- LOGIN FLOW ---
            const loginResp = await fetch('/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            const loginResult = await loginResp.json();

            if (loginResult.token) {
                localStorage.setItem('jwtToken', loginResult.token);
                window.location.href = 'dashboard/dashboard.html';
            } else {
                messageEl.textContent = loginResult.message || 'Login failed';
            }
        } else {
            // --- SIGNUP FLOW ---
            const user_name = document.getElementById('user_name').value.trim();
            const institution = document.getElementById('institution').value.trim();
            const designation = document.getElementById('designation').value.trim();

            if (!user_name || !institution || !designation) {
                messageEl.textContent = 'Please fill in all fields';
                return;
            }

            const signupResp = await fetch('/auth/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_name, institution, designation, email, password })
            });

            const signupResult = await signupResp.json();

            if (signupResp.ok) {
                // Signup succeeded → now login automatically
                const loginResp = await fetch('/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const loginResult = await loginResp.json();
                if (loginResult.token) {
                    localStorage.setItem('jwtToken', loginResult.token);
                    window.location.href = 'dashboard/dashboard.html';
                } else {
                    messageEl.textContent = 'Account created, but login failed';
                }
            } else {
                messageEl.textContent = signupResult.message || 'Signup failed';
            }
        }
    } catch (error) {
        messageEl.textContent = 'An error occurred';
        console.error(error);
    }
});
