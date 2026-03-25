<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { Download, FileSpreadsheet } from 'lucide-svelte';
    export let downloadUrl: string | null = null;
    export let apiBase: string;
    const dispatch = createEventDispatcher();
</script>

<div class="card col-span-1 flex flex-col items-center justify-center text-center h-full p-6">
    
    <div class="mb-6 bg-green-50 p-4 rounded-full">
        <FileSpreadsheet size={32} class="text-green-600" />
    </div>

    <div class="mb-5">
        <h4 class="font-bold text-gray-800 text-xl mb-2">Detailed Report</h4>
        <p class="text-sm text-gray-500 whitespace-nowrap leading-relaxed">
            Download the complete analysis as an Excel file.
        </p>
    </div>
    
    {#if downloadUrl}
        <a 
            href={`${apiBase}${downloadUrl}`} 
            download 
            on:click={() => dispatch('download')}
            class="btn-dark flex items-center gap-2 shadow-lg hover:shadow-xl hover:-translate-y-1 transform transition-all"
        >
            <Download size={16} /> Download
        </a>
    {:else}
        <button class="btn-dark flex items-center gap-2 opacity-50 cursor-not-allowed" disabled>
            <Download size={16} /> Waiting for Analysis...
        </button>
    {/if}
</div>

<style>
    /* Added 'min-height: 350px' to match the other cards if grid allows */
    .card { background: white; border-radius: 1.5rem; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    .btn-dark { background: #1f2937; color: white; padding: 0.5rem 1.5rem; border-radius: 0.75rem; font-weight: 600; text-decoration: none; transition: 0.2s; }
    .btn-dark:hover { background: #374151; }
</style>