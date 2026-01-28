<script lang="ts">
    import { TrendingUp, ChevronDown, Check } from 'lucide-svelte';
    import { slide } from 'svelte/transition';
    import { onMount, onDestroy } from 'svelte';
    import { Chart, registerables, type ChartConfiguration } from 'chart.js';

    Chart.register(...registerables);
    
    export let branches: any[] = []; 
    export let selectedIndex: number = 0; 

    let isOpen = false;
    let dropdownRef: HTMLDivElement;
    let canvas: HTMLCanvasElement;
    let chartInstance: Chart | null = null;

    $: currentBranch = branches[selectedIndex] || null;

    $: if (chartInstance && branches.length > 0) {
        updateChart();
    }

    function toggleDropdown() { isOpen = !isOpen; }
    
    function selectBranch(index: number) {
        selectedIndex = index;
        isOpen = false;
    }

    function handleClickOutside(event: MouseEvent) {
        if (isOpen && dropdownRef && !dropdownRef.contains(event.target as Node)) {
            isOpen = false;
        }
    }

    function updateChart() {
        if (!chartInstance) return;

        const labels = branches.map(d => d.Department);
        const values = branches.map(d => d.PassPercentage);
        const singleColor = '#7c3aed'; 

        chartInstance.data.labels = labels;
        chartInstance.data.datasets[0].data = values;
        chartInstance.data.datasets[0].backgroundColor = singleColor;
        chartInstance.data.datasets[0].borderColor = 'transparent';
        chartInstance.update();
    }

    onMount(() => {
        if (!canvas) return;

        const config: ChartConfiguration<'bar'> = {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Pass %',
                    data: [],
                    backgroundColor: '#7c3aed', 
                    borderRadius: 4,
                    // Dynamic thickness: max 24px, but shrinks if needed to fit screen
                    maxBarThickness: 24, 
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { 
                    y: { 
                        beginAtZero: true, 
                        max: 100, 
                        grid: { display: true, color: '#f3f4f6' }, 
                        ticks: { display: true, font: { size: 10 }, color: '#9ca3af', stepSize: 20 },
                        border: { display: false }
                    }, 
                    x: { 
                        grid: { display: false },
                        ticks: { 
                            display: true,
                            font: { size: 9 }, 
                            color: '#6b7280',
                            autoSkip: false, 
                            maxRotation: 45,
                            minRotation: 0
                        } 
                    } 
                },
                onHover: (event, elements) => {
                    const nativeEvent = event.native;
                    if(nativeEvent && nativeEvent.target) {
                        (nativeEvent.target as HTMLElement).style.cursor = elements.length ? 'pointer' : 'default';
                    }
                },
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        selectedIndex = elements[0].index;
                    }
                }
            }
        };

        chartInstance = new Chart(canvas, config);
        updateChart();
    });

    onDestroy(() => {
        if (chartInstance) chartInstance.destroy();
    });
</script>

<svelte:window on:click={handleClickOutside} />

<div class="card hero-card w-full h-full relative">
    
    <div class="flex flex-col md:flex-row h-full w-full gap-4">
        
        <div class="flex-1 flex flex-col justify-between z-10">
            <div class="flex justify-between items-start">
                <div>
                    <h2 class="text-lg font-bold text-gray-700">Overall Performance</h2>
                    <div class="mt-2 relative" bind:this={dropdownRef}>
                        <button 
                            on:click={toggleDropdown}
                            class="relative inline-flex items-center gap-2 bg-purple-50 border border-purple-100 rounded-lg px-3 py-1.5 cursor-pointer hover:bg-purple-100 transition-colors text-left"
                        >
                            <span class="text-xs font-bold text-purple-400 uppercase tracking-wide whitespace-nowrap">Branches</span>
                            <span class="text-sm font-semibold text-purple-800">-</span>
                            <span class="text-sm font-bold text-purple-900 truncate max-w-37.5">
                                {currentBranch ? currentBranch.Department : 'Select Branch'}
                            </span>
                            <ChevronDown size={14} class="text-purple-600 shrink-0 transition-transform duration-200 {isOpen ? 'rotate-180' : ''}" />
                        </button>

                        {#if isOpen}
                            <div transition:slide={{ duration: 200, axis: 'y' }} class="absolute top-full left-0 mt-2 w-full min-w-60 bg-white border border-gray-100 rounded-xl shadow-xl z-50 overflow-hidden">
                                <div class="max-h-60 overflow-y-auto py-1 custom-scrollbar">
                                    {#each branches as branch, i}
                                        <button 
                                            class="w-full text-left px-4 py-3 text-sm flex items-center justify-between hover:bg-purple-50 transition-colors border-b border-gray-50 last:border-0 {i === selectedIndex ? 'bg-purple-50 text-purple-900 font-bold' : 'text-gray-600 font-medium'}"
                                            on:click={() => selectBranch(i)}
                                        >
                                            <span class="truncate pr-2">{branch.Department}</span>
                                            {#if i === selectedIndex} <Check size={16} class="text-purple-600 shrink-0" /> {/if}
                                        </button>
                                    {/each}
                                </div>
                            </div>
                        {/if}
                    </div>
                </div>
            </div>
            
            <div class="mt-6">
                <span class="big-number text-6xl font-extrabold text-purple-700 leading-none tracking-tight">
                    {currentBranch ? currentBranch.PassPercentage : '--'}%
                </span>
                <p class="sub-text text-gray-400 font-medium mt-2">Total Pass Percentage</p>
            </div>
            
            <div class="flex gap-8 mt-auto pt-6">
                <div class="mini-stat flex flex-col">
                    <span class="label text-xs font-bold text-gray-400 uppercase tracking-wide">Total</span>
                    <span class="value text-2xl font-bold text-gray-800">{currentBranch ? currentBranch.StudentsCount : 0}</span>
                </div>
                <div class="mini-stat flex flex-col">
                    <span class="label text-xs font-bold text-gray-400 uppercase tracking-wide">Passed</span>
                    <span class="value text-2xl font-bold text-green-600">{currentBranch ? currentBranch.PassCount : 0}</span>
                </div>
                <div class="mini-stat flex flex-col">
                    <span class="label text-xs font-bold text-gray-400 uppercase tracking-wide">Failed</span>
                    <span class="value text-2xl font-bold text-red-600">{currentBranch ? currentBranch.FailCount : 0}</span>
                </div>
            </div>
        </div>

        <div class="flex-none w-full md:w-[45%] flex flex-col justify-end relative pt-4 md:pt-0 pl-0 md:pl-2 border-t md:border-t-0 md:border-l border-gray-100">
            <div class="absolute top-0 right-0 p-2 bg-purple-50 rounded-xl text-purple-600 hidden md:block">
                <TrendingUp size={24} />
            </div>
            
            <p class="text-xs font-bold text-gray-400 uppercase mb-4 text-left md:text-right pr-2">Dept Comparison</p>
            
            <div class="h-55 w-full">
                <canvas bind:this={canvas}></canvas>
            </div>
        </div>

    </div>
</div>

<style>
    .card { background: white; border-radius: 1.5rem; padding: 2rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); min-height: 350px; }
    
    .custom-scrollbar::-webkit-scrollbar { width: 4px; }
    .custom-scrollbar::-webkit-scrollbar-track { background: #f1f1f1; }
    .custom-scrollbar::-webkit-scrollbar-thumb { background: #d8b4fe; border-radius: 4px; }
</style>