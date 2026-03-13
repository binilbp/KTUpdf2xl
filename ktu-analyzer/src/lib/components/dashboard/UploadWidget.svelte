<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { Upload, Loader2, FileText, X } from 'lucide-svelte';

    export let isLoading = false;
    export let progress = { status: '', percent: 0 };

    const dispatch = createEventDispatcher();
    let selectedFile: File | null = null;

    function handleFile(e: Event) {
        const target = e.target as HTMLInputElement;
        const file = target.files?.[0];
        if (file) {
            selectedFile = file;
        }
    }

    function handleSubmit() {
        if (selectedFile) {
            dispatch('upload', selectedFile);
        }
    }

    function clearFile() {
        selectedFile = null;
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

    <h3 class="font-bold text-gray-800 mb-1">Upload Result</h3>
    
    {#if !selectedFile}
        <p class="text-xs text-gray-500 mb-6">Drag & drop PDF to analyze</p>
        <label class="border-2 border-dashed border-gray-200 bg-gray-50/50 rounded-xl flex-1 w-full flex flex-col items-center justify-center cursor-pointer hover:border-purple-400 hover:bg-purple-50 transition-all">
            <Upload size={24} class="text-gray-400 mb-2 group-hover:text-purple-600 transition-colors" />
            <span class="text-xs font-medium text-gray-600 group-hover:text-purple-700">Select File</span>
            <input type="file" accept=".pdf" class="hidden" on:change={handleFile} />
        </label>
    {:else}
        <div class="flex flex-col h-full justify-between pt-2">
            <div class="flex items-start justify-between bg-purple-50 p-3 rounded-xl border border-purple-100">
                <div class="flex items-center gap-3 overflow-hidden">
                    <div class="bg-white shadow-sm p-2 rounded-lg border border-purple-100">
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
                class="w-full mt-6 bg-purple-600 hover:bg-purple-700 text-white font-semibold h-11 px-6 rounded-xl transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2 text-base transform active:scale-[0.98]"
            >
                <Upload size={24} /> Analyze PDF
            </button>
        </div>
    {/if}
</div>

<style>
    .card { background: white; border-radius: 1.5rem; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
</style>