<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { Upload, Loader2, FileText, X } from 'lucide-svelte';

    export let isLoading = false;
    export let progress = { status: '', percent: 0 };
    export let schemas: string[] = [];

    const dispatch = createEventDispatcher();
    let selectedFile: File | null = null;
    let selectedSchema: string = '';

    function handleFile(e: Event) {
        const target = e.target as HTMLInputElement;
        const file = target.files?.[0];
        if (file) {
            selectedFile = file;
        }
    }

    function handleSubmit() {
        if (selectedFile) {
            if (!selectedSchema) {
                alert("Please select a schema before analyzing.");
                return;
            }
            // UPDATED: Dispatch an object containing both
            dispatch('upload', { file: selectedFile, schema: selectedSchema });
        }
    }

    function clearFile() {
        selectedFile = null;
        selectedSchema = '';
    }
</script>

<div class="card col-span-1 bg-white text-gray-800 flex flex-col justify-center relative overflow-hidden group h-80 md:h-full">
    
    {#if isLoading}
        <div class="absolute inset-0 bg-white/95 backdrop-blur-sm z-20 flex flex-col items-center justify-center p-6 text-center">
            <Loader2 class="animate-spin mb-3 text-purple-600" size={32} />
            <h4 class="font-bold text-lg">{progress.percent}%</h4>
            <p class="text-xs text-gray-500 mt-1 max-w-[80%]">{progress.status}</p>
            <div class="w-full bg-gray-100 h-1.5 rounded-full mt-4 overflow-hidden">
                <div class="bg-purple-600 h-full transition-all duration-300" style="width: {progress.percent}%"></div>
            </div>
        </div>
    {/if}

    <div class="flex items-center justify-between mb-2">
        <h3 class="font-bold text-gray-800">Upload Result</h3>
        
        <select 
            id="schema-select" 
            bind:value={selectedSchema} 
            class="w-36 text-xs py-1.5 pl-3 pr-8 border border-gray-200 rounded-md bg-white cursor-pointer focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-400 text-gray-600 truncate shadow-sm"
        >
            <option value="" disabled selected>Select Schema</option>
            
            {#if schemas.length === 0}
                <option value="" disabled>Loading...</option>
            {:else}
                {#each schemas as schema}
                    <option value={schema}>{schema}</option>
                {/each}
            {/if}
        </select>
    </div>
    
    {#if !selectedFile}
        <p class="text-xs text-gray-500 mb-6">Drag & drop PDF to analyze</p>
        <label class="border-2 border-dashed border-gray-200 bg-gray-50/50 rounded-xl flex-1 w-full flex flex-col items-center justify-center cursor-pointer hover:border-purple-400 hover:bg-purple-50 transition-all">
            <Upload size={24} class="text-gray-400 mb-2 group-hover:text-purple-600 transition-colors" />
            <span class="text-xs font-medium text-gray-600 group-hover:text-purple-700">Select File</span>
            <input type="file" accept=".pdf" class="hidden" on:change={handleFile} />
        </label>
    {:else}
        <div class="flex flex-col h-full justify-between pt-2">
            
            <div class="flex items-center justify-between bg-transparent p-3 rounded-xl border border-gray-200">
                <div class="flex items-center gap-3 overflow-hidden">
                    <div class="bg-white shadow-sm p-2 rounded-lg border border-gray-100">
                        <FileText size={20} class="text-purple-600" />
                    </div>
                    <div class="overflow-hidden">
                        <p class="text-sm font-bold text-gray-800 truncate w-32">{selectedFile.name}</p>
                    </div>
                </div>
                <button on:click={clearFile} class="text-gray-400 hover:text-red-500 transition-colors p-1">
                    <X size={18} />
                </button>
            </div>
            
            <button 
                on:click={handleSubmit}
                class="w-full mt-4 bg-purple-600 hover:bg-purple-700 text-white font-semibold h-11 px-6 rounded-xl transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2 text-base transform active:scale-[0.98]"
            >
                <Upload size={24} /> Analyze PDF
            </button>
        </div>
    {/if}
</div>

<style>
    .card { background: white; border-radius: 1.5rem; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
</style>