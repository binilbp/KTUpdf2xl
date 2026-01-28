<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { Chart, registerables, type ChartConfiguration } from 'chart.js';
    
    Chart.register(...registerables);

    // CHANGED: Removed 'selectedIndex' to fix the warning
    // Also ensuring we accept 'data' directly if you pass it as 'branches' or 'data'
    export let data: any[] = []; 
    
    let canvas: HTMLCanvasElement;
    let chartInstance: Chart | null = null;

    // Reactive update
    $: if (chartInstance && data.length > 0) {
        updateChart();
    }

    function updateChart() {
        if (!chartInstance) return;

        const labels = data.map(d => d.Department);
        const values = data.map(d => d.PassPercentage);
        
        const singleColor = '#7c3aed'; 

        chartInstance.data.labels = labels;
        chartInstance.data.datasets[0].data = values;
        chartInstance.data.datasets[0].backgroundColor = singleColor; 
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
                    borderRadius: 6,
                    barThickness: 30, 
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
                        grid: { display: false },
                        ticks: { font: { size: 10 } }
                    }, 
                    x: { 
                        grid: { display: false },
                        ticks: { 
                            display: true, 
                            autoSkip: false, 
                            maxRotation: 45,
                            minRotation: 0,
                            font: { size: 10 }
                        } 
                    } 
                } 
            }
        };

        chartInstance = new Chart(canvas, config);
        // Initial update if data exists
        if (data.length > 0) updateChart();
    });

    onDestroy(() => {
        if (chartInstance) chartInstance.destroy();
    });
</script>

<div class="card col-span-2 flex flex-col h-87.5">
    <div class="flex justify-between items-center mb-4 shrink-0">
        <h3 class="font-bold text-gray-700">Department Comparison</h3>
    </div>
    
    <div class="flex-1 w-full overflow-x-auto overflow-y-hidden pb-2">
        <div class="h-full min-w-150">
            <canvas bind:this={canvas}></canvas>
        </div>
    </div>
</div>

<style>
    .card { background: white; border-radius: 1.5rem; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    
    .overflow-x-auto::-webkit-scrollbar { height: 6px; }
    .overflow-x-auto::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 4px; }
    .overflow-x-auto::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 4px; }
    .overflow-x-auto::-webkit-scrollbar-thumb:hover { background: #9ca3af; }
</style>