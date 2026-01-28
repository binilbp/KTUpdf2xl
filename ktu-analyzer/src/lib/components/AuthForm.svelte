<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    
    // Dispatcher to tell the parent page to open the doors
    const dispatch = createEventDispatcher<{ success: void }>();
    
    // --- STATE VARIABLES ---
    let isLogin: boolean = true;
    let isLoading: boolean = false;
    let errorMessage: string = '';

    // Form Fields (Bound to inputs)
    let email = '';
    let password = '';
    
    // Signup specific fields
    let userName = '';
    let institution = '';
    let designation = '';

    // --- CONFIGURATION ---
    // Matches your FastAPI default port. 
    // Ensure your backend is running on this URL.
    const API_BASE_URL = 'http://127.0.0.1:8000';

    function toggleMode() {
        isLogin = !isLogin;
        errorMessage = ''; // Clear errors on toggle
    }

    async function handleSubmit() {
        isLoading = true;
        errorMessage = '';

        try {
            if (isLogin) {
                // --- LOGIN LOGIC ---
                // Endpoint: gem/db/app/routers/auth.py -> @authrouter.post("/login")
                // Schema: UserInLogin { email, password }
                const response = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        email, 
                        password 
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || 'Login failed');
                }

                // Schema: UserWithToken { token: str }
                if (data.token) {
                    console.log("Login Successful, Token received.");
                    localStorage.setItem('auth_token', data.token);
                    dispatch('success'); // Triggers door animation
                } else {
                    throw new Error("Invalid response from server.");
                }

            } else {
                // --- SIGNUP LOGIC ---
                // Endpoint: gem/db/app/routers/auth.py -> @authrouter.post("/signup")
                // Schema: UserInCreate { user_name, institution, designation, email, password }
                
                const payload = {
                    user_name: userName, // MUST match pydantic model 'user_name'
                    institution: institution,
                    designation: designation,
                    email: email,
                    password: password
                };

                const response = await fetch(`${API_BASE_URL}/auth/signup`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (!response.ok) {
                    // Handle Validation Errors (422) usually sent by FastAPI
                    if (data.detail && Array.isArray(data.detail)) {
                        throw new Error(data.detail[0].msg || 'Validation error');
                    }
                    throw new Error(data.detail || 'Signup failed');
                }

                // Signup Successful
                alert('Account created successfully! Please sign in.');
                toggleMode(); // Switch to login view
            }

        } catch (error: any) {
            console.error('Auth Error:', error);
            errorMessage = error.message || 'An unexpected error occurred';
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="auth-card">
    <div class="logo-container">
        <img src="https://erp.vidyaacademy.ac.in/itf_vidya_base/static/src/img/logo2.png/" alt="logo" class="logo-img">
    </div>

    {#if errorMessage}
        <div class="error-banner">
            {errorMessage}
        </div>
    {/if}

    {#if isLogin}
        <h2 class="welcome-title">Welcome Back! 👋</h2>
        <p class="welcome-subtitle">Please sign-in to access the dashboard</p>
        
        <form on:submit|preventDefault={handleSubmit}>
            <label class="input-label" for="login-email">EMAIL</label>
            <input 
                type="email" 
                id="login-email" 
                bind:value={email} 
                placeholder="Enter your email" 
                class="input-field" 
                required
            >

            <div class="password-header">
                <label class="input-label" for="login-password">PASSWORD</label>
                <a href="#forgot" class="forgot-password-link">Forgot Password?</a>
            </div>
            <input 
                type="password" 
                id="login-password" 
                bind:value={password} 
                placeholder="••••••••" 
                class="input-field" 
                required
            >

            <button type="submit" class="signin-button" disabled={isLoading}>
                {isLoading ? 'Signing in...' : 'Sign in'}
            </button>
        </form>

        <p class="create-account-text">
            New here? <button class="link-btn" on:click={toggleMode}>Create an account</button>
        </p>

    {:else}
        <h2 class="welcome-title">Create Account 🚀</h2>
        <p class="welcome-subtitle">Start analyzing your results today</p>

        <form on:submit|preventDefault={handleSubmit}>
            <label class="input-label" for="user_name">USERNAME</label>
            <input 
                type="text" 
                id="user_name" 
                bind:value={userName} 
                placeholder="johndoe"
                class="input-field" 
                required
            >
            
            <label class="input-label" for="institution">INSTITUTION</label>
            <input 
                type="text" 
                id="institution" 
                bind:value={institution} 
                placeholder="College Name"
                class="input-field" 
                required
            >

            <label class="input-label" for="designation">DESIGNATION</label>
            <input 
                type="text" 
                id="designation" 
                bind:value={designation} 
                placeholder="e.g. Student, Faculty"
                class="input-field" 
                required
            >

            <label class="input-label" for="signup-email">EMAIL</label>
            <input 
                type="email" 
                id="signup-email" 
                bind:value={email} 
                class="input-field" 
                required
            >

            <label class="input-label" for="signup-password">PASSWORD</label>
            <input 
                type="password" 
                id="signup-password" 
                bind:value={password} 
                class="input-field" 
                required
            >

            <button type="submit" class="signin-button" disabled={isLoading}>
                {isLoading ? 'Creating Account...' : 'Sign up'}
            </button>
        </form>

        <p class="create-account-text">
            Already have an account? <button class="link-btn" on:click={toggleMode}>Sign in instead</button>
        </p>
    {/if}
</div>

<style>
    .auth-card { 
        background: white; 
        padding: 2rem; 
        border-radius: 1rem; 
        width: 100%; 
        max-width: 28rem; 
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); 
    }
    .logo-container { display: flex; justify-content: center; margin-bottom: 1.5rem; }
    .logo-img { height: 80px; }
    
    .error-banner {
        background-color: #fee2e2;
        color: #b91c1c;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        font-size: 0.875rem;
        text-align: center;
        border: 1px solid #fecaca;
    }

    .welcome-title { text-align: center; font-size: 1.25rem; font-weight: 700; color: var(--text-gray-800); }
    .welcome-subtitle { text-align: center; color: var(--text-gray-500); margin-bottom: 1.5rem; }
    
    .input-label { display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-gray-700); margin-bottom: 0.25rem; }
    .input-field { width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem; margin-bottom: 1rem; }
    
    .signin-button { width: 100%; background: var(--primary-purple); color: white; padding: 0.75rem; border-radius: 0.5rem; border: none; font-weight: 600; cursor: pointer; transition: opacity 0.2s; }
    .signin-button:hover { background: var(--primary-purple-hover); }
    .signin-button:disabled { opacity: 0.7; cursor: not-allowed; }
    
    .create-account-text { text-align: center; margin-top: 1rem; font-size: 0.9rem; color: var(--text-gray-500); }
    .link-btn { background: none; border: none; color: var(--primary-purple); cursor: pointer; font-weight: 600; text-decoration: underline; }
    .password-header { display: flex; justify-content: space-between; }
    .forgot-password-link { font-size: 0.8rem; color: var(--primary-purple); text-decoration: none; }
</style>