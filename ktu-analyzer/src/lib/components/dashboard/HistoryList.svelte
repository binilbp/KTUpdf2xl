<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { History, FileText } from 'lucide-svelte';
    export let files: any[] = [];

    const dispatch = createEventDispatcher();
</script>

<div class="card col-span-1 h-87.5 flex flex-col">
    
    <div class="flex items-center gap-2 mb-4 shrink-0">
        <History size={20} class="text-gray-500"/>
        <h3 class="font-bold text-gray-700">History</h3>
    </div>
    
    <div class="history-list flex-1 overflow-y-auto pr-2 min-h-0">
        {#each files as file}
            <button 
                type="button"
                class="history-item w-full flex justify-between items-center py-3 px-2 border-b border-gray-100 last:border-0 cursor-pointer hover:bg-purple-50 transition-colors rounded-lg text-left"
                on:click={() => dispatch('loadHistory', file)}>
                <div class="flex items-center gap-3 w-full">
                    <div class="bg-blue-50 p-2 rounded-lg shrink-0">
                        <FileText size={16} class="text-blue-500" />
                    </div>
                    <div class="overflow-hidden flex-1">
                        <p class="text-sm font-bold text-gray-700 truncate">{file.filename}</p>
                        <p class="text-xs text-gray-400">{file.created_at}</p>
                    </div>
                </div>
            </button>
        {/each}
        {#if files.length === 0}
            <div class="flex flex-col items-center justify-center h-full text-gray-400">
                <p class="text-sm">No files uploaded yet</p>
            </div>
        {/if}
    </div>
</div>

<style>
    .card { background: white; border-radius: 1.5rem; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    
    /* Custom Scrollbar */
    .history-list::-webkit-scrollbar { width: 4px; }
    .history-list::-webkit-scrollbar-track { background: #f1f1f1; }
    .history-list::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 4px; }
    .history-list::-webkit-scrollbar-thumb:hover { background: #d1d5db; }
</style>