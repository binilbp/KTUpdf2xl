<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    
    export let isOpen: boolean = false;

    // 1. Setup the dispatcher
    const dispatch = createEventDispatcher();

    function handleHomeClick(e: MouseEvent) {
        e.preventDefault();
        dispatch('homeClick'); // Tell parent to close doors
    }

    // 2. New handler for About, Team, etc.
    function handleSectionClick(e: MouseEvent, id: string) {
        e.preventDefault(); // Prevents the immediate jump/scroll
        dispatch('sectionClick', id); // Tell parent to "Open Doors -> Then Scroll"
    }
</script>

<nav class="navbar" class:visible={isOpen}>
    <div class="nav-heading-anchor">KTU RESULT ANALYZER</div>
    <div class="nav-links">
        <a href="#hero" class="nav-link" on:click={handleHomeClick}>Home</a>
        
        <a href="#about" class="nav-link" on:click={(e) => handleSectionClick(e, 'about')}>About</a>
        <a href="#team" class="nav-link" on:click={(e) => handleSectionClick(e, 'team')}>Team</a>
        <a href="#features" class="nav-link" on:click={(e) => handleSectionClick(e, 'features')}>Features</a>
        <a href="#contact" class="nav-link" on:click={(e) => handleSectionClick(e, 'contact')}>Contact</a>
    </div>
</nav>

<style>
    /* ... keep your existing styles ... */
    .navbar {
        position: fixed;
        top: 0; left: 0; right: 0;
        z-index: 40;
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 5rem;
        padding: 0 3rem;
        background-color: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        opacity: 0;
        pointer-events: none;
        transition: opacity var(--animation-duration) ease-in-out;
    }

    .navbar.visible {
        opacity: 1;
        pointer-events: auto;
    }

    .nav-heading-anchor { font-size: 1.5rem; font-weight: 800; color: var(--heading-color); }
    .nav-links { display: none; gap: 2rem; }
    .nav-link { color: var(--text-gray-700); text-decoration: none; font-weight: 500; }
    .nav-link:hover { color: var(--heading-color); text-decoration: underline; }

    @media (min-width: 768px) { .nav-links { display: flex; } }
</style>