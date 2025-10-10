document.addEventListener("DOMContentLoaded", () => {
    // --- DOM ELEMENT REFERENCES ---
    const body = document.body;
    const hero = document.getElementById("hero");
    const contentSections = document.querySelectorAll(".content-section");
    const backToTopButton = document.getElementById("back-to-top");



    // --- STATE MANAGEMENT ---
    let animationState = "closed"; // 'closed', 'opening', 'open', 'closing'
    let isAnimating = false;
    let isProgrammaticScroll = false;
    let touchStartY = 0;
    
    // --- ANIMATION TIMING ---
    const ANIMATION_DURATION = 1000;

    // Attach login handler directly to button
    const loginButton = document.getElementById("login");
    if (loginButton) {
        loginButton.addEventListener("click", handleLogin);
    }

    //eda add validation nale

    async function handleLogin() {
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        await loginUser(email, password);
    }

    async function loginUser(email, password) {
        try {
            const response = await fetch("http://localhost:8000/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({email, password }),
            });

            if (!response.ok) {
            throw new Error("Login failed. Please check your credentials.");
            }

            const data = await response.json();

            // Assuming API returns { "access_token": "yourtokenhere" }
            if (data.token) {
            // Save token to localStorage for later use
            localStorage.setItem("token", data.access_token);
            console.log("Login successful! Token stored.");
            // Redirect or perform post-login action
            window.location.href = "app.html";
            } else {
            throw new Error("Invalid response format from server.");
            }
        } catch (error) {
            console.error("Error:", error);
            alert(error.message);
        }
    }

    
    // --- INITIAL SETUP ---
    if ("scrollRestoration" in history) {
        history.scrollRestoration = "manual";
    }
    window.scrollTo(0, 0);

    // --- ANIMATION SEQUENCES (Unchanged) ---
    const openSequence = () => {
        if (isAnimating || animationState !== "closed") return;
        
        isAnimating = true;
        animationState = "opening";
        
        body.classList.add("lift-open");
        
        setTimeout(() => {
            animationState = "open";
            hero.style.display = 'none';
            isAnimating = false;
        }, ANIMATION_DURATION);
    };

    const closeSequence = () => {
        if (isAnimating || animationState !== "open") return;
        
        isAnimating = true;
        animationState = "closing";

        hero.style.display = 'flex';
        requestAnimationFrame(() => {
            body.classList.remove("lift-open");
        });
        
        setTimeout(() => {
            animationState = "closed";
            isAnimating = false;
        }, ANIMATION_DURATION);
    };

    // --- EVENT LISTENERS (Updated for fast scroll fix) ---
    const onWheel = (e) => {
        if (isProgrammaticScroll || animationState !== 'closed') return;

        // **FIX**: Check position *before* checking deltaY and prevent default scroll
        if (window.scrollY <= 5) {
            if (e.deltaY > 8) { // Only prevent scroll if scrolling down
                e.preventDefault();
                openSequence();
            }
        }
    };

    const onTouchStart = (e) => {
        touchStartY = e.touches?.[0]?.clientY ?? 0;
    };

    const onTouchMove = (e) => {
        if (isProgrammaticScroll || animationState !== 'closed') return;
        
        // **FIX**: Check position *before* checking swipe distance and prevent default scroll
        if (window.scrollY <= 5) {
            const currY = e.touches?.[0]?.clientY ?? 0;
            if (touchStartY - currY > 20) { // Check for swipe up
                e.preventDefault();
                openSequence();
            }
        }
    };
    
    const onScroll = () => {
        if (isProgrammaticScroll) return;
        if (window.scrollY <= 5 && animationState === "open") closeSequence();
    };
    
    // **FIX**: Removed `{ passive: true }` to allow preventDefault()
    window.addEventListener("wheel", onWheel, { passive: false });
    window.addEventListener("touchstart", onTouchStart, { passive: true }); // Can remain passive
    window.addEventListener("touchmove", onTouchMove, { passive: false });
    window.addEventListener("scroll", onScroll, { passive: true }); // Can remain passive
    
    // --- SMOOTH SCROLL FOR NAV LINKS (Unchanged) ---
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            isProgrammaticScroll = true;
            const targetId = e.currentTarget.getAttribute("href");
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: "smooth", block: "start" });
            }
            setTimeout(() => isProgrammaticScroll = false, 1000);
        });
    });

    // --- DEDICATED LISTENER FOR BACK-TO-TOP BUTTON (Unchanged) ---
    backToTopButton.addEventListener('click', () => {
        isProgrammaticScroll = true;
        window.scrollTo({ top: 0, behavior: 'smooth' });
        setTimeout(() => isProgrammaticScroll = false, 1000);
    });

    // --- INTERSECTION OBSERVER (Unchanged) ---
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                } else {
                    entry.target.classList.remove("is-visible");
                }
            });
        }, { threshold: 0.25 }
    );
    contentSections.forEach(section => observer.observe(section));
});

