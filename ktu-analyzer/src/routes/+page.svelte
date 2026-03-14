<script lang="ts">
    import { onMount } from 'svelte';
    import { ArrowUp, LogOut, Info, Users, Star, Mail } from 'lucide-svelte';
    
    // --- COMPONENT IMPORTS ---
    import Navbar from '$lib/components/Navbar.svelte';
    import AuthForm from '$lib/components/AuthForm.svelte';
    import Section from '$lib/components/Section.svelte'; 
    
    // Dashboard Widgets
    import HeroCard from '$lib/components/dashboard/HeroCard.svelte';
    import HistoryList from '$lib/components/dashboard/HistoryList.svelte';
    import UploadWidget from '$lib/components/dashboard/UploadWidget.svelte';
    import SubjectAnalysis from '$lib/components/dashboard/SubjectAnalysis.svelte';
    import DownloadCard from '$lib/components/dashboard/DownloadCard.svelte';

    // --- CONFIGURATION ---
    const API_BASE = 'http://localhost:8000';

    // --- STATE ---
    let isLoggedIn = false;
    let isLoading = false;
    let isSessionExpired = false; 
    let sessionTimeout: ReturnType<typeof setTimeout> | undefined; 
    const SESSION_DURATION_MS = 15 * 60 * 1000;
    let progress: { status: string; percent: number; download_url: string | null } = { 
        status: 'Idle', 
        percent: 0, 
        download_url: null 
    };
    let uploadTaskId = '';
    
    let historyFiles: any[] = [];
    let dashboardData: any[] = [];
    let selectedBranchIndex = 0; 

    $: currentBranch = dashboardData[selectedBranchIndex] || null;

    // --- ANIMATION STATE ---
    let animationState: 'closed' | 'opening' | 'open' | 'closing' = 'closed';
    let scrollY: number = 0;
    let lastScrollY: number = 0;
    $: isLiftOpen = animationState === 'open' || animationState === 'opening';

    // NEW: Function to check and enforce session expiration
    function checkSession() {
        const loginTimestampStr = localStorage.getItem('login_timestamp');
        if (!loginTimestampStr) return;

        const loginTime = parseInt(loginTimestampStr, 10);
        const currentTime = Date.now();
        const elapsedTime = currentTime - loginTime;

        clearTimeout(sessionTimeout); // Clear any existing timer

        if (elapsedTime >= SESSION_DURATION_MS) {
            // Time already expired
            triggerSessionExpiry();
        } else {
            // Set timer for the remaining time
            const timeRemaining = SESSION_DURATION_MS - elapsedTime;
            sessionTimeout = setTimeout(() => {
                triggerSessionExpiry();
            }, timeRemaining);
        }
    }

    // NEW: Function to handle the actual expiration event
    function triggerSessionExpiry() {
        isSessionExpired = true;
        // Clear tokens immediately so backend calls don't fire with an expired token
        localStorage.removeItem('auth_token');
        localStorage.removeItem('login_timestamp');
    }

    // --- LIFECYCLE ---
    onMount(async () => {
        const token = localStorage.getItem('auth_token');
        if (token) {
            // Verify the token by trying to fetch history first
            const isTokenValid = await fetchHistory();
            
            if (isTokenValid) {
                isLoggedIn = true;
                animationState = 'open';
                document.body.style.overflow = 'auto'; 
                checkSession(); 
            } else {
                // Token is dead/invalid. Clean up and force them to log in.
                localStorage.removeItem('auth_token');
                localStorage.removeItem('login_timestamp');
                document.body.style.overflow = 'hidden';
                window.scrollTo(0, 0);
            }
        } else {
            document.body.style.overflow = 'hidden';
            window.scrollTo(0, 0);
        }
    });

    // --- ACTIONS ---
    async function fetchHistory() {
        const token = localStorage.getItem('auth_token');
        if (!token) return false;
        try {
            const res = await fetch(`${API_BASE}/userfiles/user/files`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            if (res.ok) {
                historyFiles = await res.json();
                return true; // Token is valid!
            } else {
                // If we get a 401 Unauthorized (or any other error), token is invalid
                console.warn("Token validation failed with status:", res.status);
                return false; 
            }
        } catch (e) { 
            console.error("Network error during token validation:", e);
            return false;
        }
    }

    async function handleUpload(event: CustomEvent) {
        const file = event.detail;
        const token = localStorage.getItem('auth_token');
        const formData = new FormData();
        formData.append('file', file);

        isLoading = true;
        progress = { status: 'Starting Upload...', percent: 5, download_url: null };

        try {
            const res = await fetch(`${API_BASE}/process-pdf/start`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            });
            const data = await res.json();
            uploadTaskId = data.task_id;
            pollStatus();
        } catch (error) {
            console.error(error);
            isLoading = false;
        }
    }

    async function pollStatus() {
        if (!uploadTaskId) return;
        const interval = setInterval(async () => {
            const res = await fetch(`${API_BASE}/process-pdf/status/${uploadTaskId}`);
            const data = await res.json();
            progress = data;

            if (data.percent >= 100) {
                clearInterval(interval);
                isLoading = false;
                if (data.result) {
                    dashboardData = data.result;
                    selectedBranchIndex = 0;
                    await fetchHistory();
                }
            }
        }, 1000);
    }

    function handleLoginSuccess() {
        isLoggedIn = true; 
        isSessionExpired = false; // NEW: reset expiration state
        openDoors();
        checkSession(); // NEW: Start the timer on fresh login
    }

    function handleLogout() {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('login_timestamp'); // NEW: Clear timestamp
        clearTimeout(sessionTimeout);               // NEW: Clear the timer
        dashboardData = [];
        historyFiles = [];
        closeDoors();
        setTimeout(() => { isLoggedIn = false; isSessionExpired = false; }, 500);
    }

    function handleAcknowledgeExpiry() {
        // Hide the popup
        isSessionExpired = false; 
        
        // Clear UI data
        dashboardData = [];
        historyFiles = [];
        
        // Trigger the door animation to go back to the login screen
        closeDoors();
        setTimeout(() => { isLoggedIn = false; }, 500);
    }

    function handleLoadHistory(event: CustomEvent) {
        const file = event.detail;
        
        if (file.json_charts) {
            dashboardData = typeof file.json_charts === 'string' ? JSON.parse(file.json_charts) : file.json_charts;
            selectedBranchIndex = 0;
        }

        if (file.download_path) {
            // Normalize slashes to catch Windows pathing bugs (\ vs /)
            const normalizedPath = file.download_path.replace(/\\/g, '/');
            const pathParts = normalizedPath.split('/');
            
            // Extract the user_id and generated file_name
            const downloadPathSuffix = pathParts.slice(-2).join('/');
            progress = { ...progress, download_url: `/download/${downloadPathSuffix}` };
        } else {
            // CRITICAL: Clear the URL if the DB record is missing the path, 
            // otherwise it tries to download the previous file or a broken link.
            progress = { ...progress, download_url: null };
        }
    }

    // --- ANIMATION LOGIC ---
    function openDoors() {
        if (animationState !== 'closed') return;
        window.scrollTo(0, 0);
        document.body.style.overflow = 'hidden'; 
        animationState = 'opening';
        if (isLoggedIn) fetchHistory();
        setTimeout(() => { 
            animationState = 'open'; 
            document.body.style.overflow = 'auto'; 
        }, 1000);
    }

    function closeDoors() {
        if (animationState !== 'open') return;
        window.scrollTo({ top: 0, behavior: 'smooth' });
        animationState = 'closing';
        setTimeout(() => { 
            animationState = 'closed'; 
            document.body.style.overflow = 'hidden'; 
        }, 1000);
    }

    function resetToHome() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (isLiftOpen && !isLoggedIn) closeDoors();
    }

    function handleSectionClick(event: CustomEvent) {
        const sectionId = event.detail;
        if (animationState === 'closed') {
            openDoors();
            setTimeout(() => {
                const el = document.getElementById(sectionId);
                if (el) el.scrollIntoView({ behavior: 'smooth' });
            }, 1100);
        } else {
            const el = document.getElementById(sectionId);
            if (el) el.scrollIntoView({ behavior: 'smooth' });
        }
    }

    function handleWheel(e: WheelEvent) {
        if (isLoggedIn) return; 
        const THRESHOLD = 10; 
        if (animationState === 'closed' && e.deltaY > THRESHOLD) openDoors(); 
        else if (animationState === 'open' && scrollY < 5 && e.deltaY < -THRESHOLD) closeDoors();
    }

    function handleScroll() {
        if (isLoggedIn) return;
        lastScrollY = scrollY;
    } 
</script>

<svelte:window bind:scrollY on:wheel={handleWheel} on:scroll={handleScroll} />

{#if !isLoggedIn}
    <Navbar isOpen={isLiftOpen} on:homeClick={resetToHome} on:sectionClick={handleSectionClick} />
{/if}

{#if isLoggedIn}
    <nav class="fixed top-0 left-0 w-full bg-white shadow-sm z-50 px-4 md:px-8 h-16 flex items-center justify-between transition-all duration-500">
        <div class="flex items-center gap-2">
            <span class="font-bold text-lg md:text-xl text-gray-800 tracking-tight">KTU ANALYZER</span>
            <span class="bg-purple-100 text-purple-700 text-[10px] md:text-xs px-2 py-1 rounded-full font-semibold">BETA</span>
        </div>
        <button on:click={handleLogout} class="flex items-center gap-2 text-sm text-gray-600 hover:text-red-600 font-medium transition-colors">
            <LogOut size={16} /> <span class="hidden md:inline">Sign Out</span>
        </button>
    </nav>
{/if}

<div class="hero-container">
    <div class="hero-panel left-door hidden lg:flex" class:open={isLiftOpen}>
        <div class="hero-content px-8">
            <h1 class="text-6xl font-extrabold text-gray-800 leading-tight mb-6">KTU RESULT<br>ANALYZER</h1>
            <p class="text-xl text-gray-500 leading-relaxed">Easily upload and analyze your KTU results. Get instant statistics and trends.</p>
        </div>
    </div>
    
    <div class="hero-panel right-door w-full lg:w-1/2 relative" class:open={isLiftOpen}>
        
        <div class="lg:hidden absolute top-10 left-5 w-full px-8 pt-24 text-left z-20">
            <h1 class="text-3xl font-extrabold text-gray-800 leading-none mb-4 tracking-tight">
                KTU RESULT<br>ANALYZER
            </h1>
            <p class="text-gray-500 text-sm leading-relaxed max-w-75">
                Easily upload and analyze your KTU results. Get instant statistics and trends.
            </p>
        </div>

        <div class="auth-wrapper px-4 w-full max-w-md" class:fade-out={isLiftOpen}>
            <AuthForm on:success={handleLoginSuccess} />
        </div>
    </div>
</div>

<main class="content-wrapper" class:visible={isLiftOpen}>
    
    {#if isLoggedIn}
        <div class="dashboard-section">
            <div class="dashboard-header flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-2">
                <h2 class="text-xl md:text-2xl font-bold text-gray-800">Analytics Dashboard</h2>
            </div>

            <div class="grid-layout">
                
                <div class="span-hero"> 
                    <HeroCard branches={dashboardData} bind:selectedIndex={selectedBranchIndex} />
                </div>
                
                <div class="span-1"> 
                    <HistoryList files={historyFiles} on:loadHistory={handleLoadHistory} />
                </div>

                <div class="span-1"> 
                    <SubjectAnalysis branch={currentBranch} />
                </div>

                <div class="span-1"> 
                    <UploadWidget {isLoading} {progress} on:upload={handleUpload} />
                </div>
                
                <div class="span-1"> 
                    <DownloadCard downloadUrl={progress.download_url} apiBase={API_BASE} />
                </div>

            </div>
        </div>

    {:else}
        <Section id="about" title="About Us" Icon={Info}>
            We are a dedicated team passionate about making academic data accessible.
        </Section>
        <Section id="team" title="Our Team" Icon={Users}>
            Our team consists of skilled developers and data analysts.
        </Section>
        <Section id="features" title="Features" Icon={Star}>
            Instantly calculate SGPA/CGPA and visualize performance.
        </Section>
        <Section id="contact" title="Contact Us" Icon={Mail}>
            Reach out to us at <a href="mailto:support@ktuanalyzer.com">support@ktuanalyzer.com</a>.
        </Section>
    {/if}

</main>

<button class="back-to-top" class:visible={isLiftOpen && !isLoggedIn && scrollY > 100} on:click={resetToHome}>
    <ArrowUp size={24} />
</button>

{#if isSessionExpired}
    <div class="fixed inset-0 bg-black/40 backdrop-blur-sm z-100 flex items-center justify-center p-4 transition-opacity">
        <div class="bg-white rounded-2xl shadow-2xl p-8 max-w-sm w-full text-center flex flex-col items-center transform transition-transform scale-100">
            
            <h3 class="text-2xl font-bold text-gray-800 mb-2">Session Expired</h3>
            
            <p class="text-gray-500 mb-6 leading-relaxed">
                Your session has expired. Please log in again to continue accessing your dashboard.
            </p>
            
            <button 
                on:click={handleAcknowledgeExpiry} 
                class="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-xl transition-colors"
            >
                Log In Again
            </button>
        </div>
    </div>
{/if}

<style>
    /* --- DASHBOARD RESPONSIVE LAYOUT --- */
    .dashboard-section {
        padding: 5rem 1rem 2rem 1rem; /* Less padding on mobile */
        background: #f5f4fb;
        min-height: 100vh;
        width: 100%;
        box-sizing: border-box;
    }

    /* DEFAULT: MOBILE (1 Column) */
    .grid-layout { 
        display: grid; 
        grid-template-columns: 1fr; 
        gap: 1rem; 
    }
    .span-hero, .span-1 { grid-column: span 1;}

    /* TABLET (2 Columns) */
    @media (min-width: 768px) {
        .dashboard-section { padding: 6rem 2rem 2rem 2rem; }
        .grid-layout { grid-template-columns: repeat(2, 1fr); gap: 1.5rem; }
        
        /* Hero spans full width on tablet */
        .span-hero { grid-column: span 2; } 
    }

    /* LAPTOP/DESKTOP (3 Columns) */
    @media (min-width: 1024px) {
        .grid-layout { grid-template-columns: repeat(3, 1fr); }
        
        /* Hero spans 2 cols, leaving 1 for History */
        .span-hero { grid-column: span 2; }
    }

    /* --- BASE STYLES --- */
    .hero-container { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; display: flex; z-index: 30; pointer-events: none; }
    
    .hero-panel { flex: 1; height: 100%; display: flex; align-items: center; transition: transform 1000ms ease-in-out; pointer-events: auto; }
    
    .left-door { background-color: var(--bg-left); padding-left: 80px; justify-content: flex-start; }
    .left-door.open { transform: translateX(-100%); }
    
    .right-door { background: linear-gradient(to bottom, var(--bg-right-start), var(--bg-right-end)); justify-content: center; }
    .right-door.open { transform: translateX(100%); }
    
    .hero-content { opacity: 1; transition: opacity 0.5s; max-width: 32rem; }
    .hero-panel.open .hero-content { opacity: 0; pointer-events: none; }
    
    /* Responsive Text Colors/Fonts handled by Tailwind classes in HTML */
    .hero-content h1 { color: var(--heading-color); line-height: 1.1; margin-bottom: 1.5rem; font-weight: 800; }
    .hero-content p { color: var(--text-gray-500); line-height: 1.6; }
    
    .auth-wrapper { opacity: 1; transition: opacity 0.5s; width: 100%; display: flex; justify-content: center;}
    .fade-out { opacity: 0; pointer-events: none; }
    
    .content-wrapper { position: relative; z-index: 10; opacity: 0; pointer-events: none; transition: opacity 1s; }
    .content-wrapper.visible { opacity: 1; pointer-events: auto; }
    
    .back-to-top { 
        position: fixed; bottom: 1.5rem; right: 1.5rem; /* Closer on mobile */
        width: 3rem; height: 3rem; 
        background: var(--primary-purple); color: white; 
        border-radius: 50%; border: none; 
        display: flex; align-items: center; justify-content: center; 
        cursor: pointer; opacity: 0; transform: scale(0); 
        transition: all 0.3s; z-index: 50; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        padding-bottom: env(safe-area-inset-bottom); /* iPhone safe area */
    }
    .back-to-top.visible { opacity: 1; transform: scale(1); }
    .back-to-top:hover { background: var(--primary-purple-hover); }

    /* Fix for Mobile Door */
    @media (max-width: 1024px) { 
        .left-door { display: none; } 
        .right-door { width: 100vw; flex: none; } 
        /* Mobile: Right door moves completely out */
        .right-door.open { transform: translateX(100%); }
    }
</style>