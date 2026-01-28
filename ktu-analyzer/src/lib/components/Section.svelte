<script lang="ts">
    import { onMount, type ComponentType } from 'svelte';
    
    export let id: string = '';
    export let title: string = '';
    
    // This tells TypeScript that 'Icon' is a Svelte Component
    export let Icon: ComponentType; 
    
    let sectionRef: HTMLElement;
    let isVisible: boolean = false;

    onMount(() => {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) isVisible = true;
            });
        }, { threshold: 0.25 });
        
        if (sectionRef) observer.observe(sectionRef);
        return () => observer.disconnect();
    });
</script>

<section {id} bind:this={sectionRef} class="content-section" class:is-visible={isVisible}>
    <div class="section-content">
        <div class="icon-wrapper">
            <svelte:component this={Icon} size={48} color="var(--primary-purple)" />
        </div>
        <h2 class="section-title">{title}</h2>
        <p class="section-text"><slot /></p>
    </div>
</section>

<style>
    /* Same CSS as before */
    .content-section {
        min-height: 100vh;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        padding: 2rem;
        opacity: 0; transform: translateY(2rem);
        transition: opacity 0.7s ease, transform 0.7s ease;
    }
    .content-section.is-visible { opacity: 1; transform: translateY(0); }
    .section-content { max-width: 48rem; text-align: center; }
    .icon-wrapper { margin-bottom: 1.5rem; display: flex; justify-content: center; }
    .section-title { font-size: 2.25rem; font-weight: 700; color: var(--text-gray-800); margin-bottom: 1.5rem; }
    .section-text { font-size: 1.125rem; line-height: 1.75; color: var(--text-gray-700); }
</style>