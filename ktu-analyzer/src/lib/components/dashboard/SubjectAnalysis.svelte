<script lang="ts">
    import { onDestroy } from 'svelte'; // Removed onMount (we rely on reactive statements now)
    import { Chart, registerables, type ChartConfiguration } from 'chart.js';

    Chart.register(...registerables);

    export let branch: any = null;
    
    let canvas: HTMLCanvasElement;
    let chartInstance: Chart | null = null;
    let hasData = false;

    const subjectColors = [
        '#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', 
        '#ec4899', '#6366f1', '#14b8a6', '#f97316', '#84cc16'
    ];

    // --- ROBUST REACTIVITY ---
    // Whenever 'branch' changes, this block runs.
    $: if (branch && branch.CoursesAnalysis && branch.CoursesAnalysis.length > 0) {
        hasData = true;
        // setTimeout ensures the <canvas> is rendered in the DOM before we try to draw on it
        setTimeout(() => renderChart(branch.CoursesAnalysis), 0);
    } else {
        hasData = false;
        destroyChart(); // Cleanup if data is empty
    }

    function destroyChart() {
        if (chartInstance) {
            chartInstance.destroy();
            chartInstance = null;
        }
    }

    function renderChart(courses: any[]) {
        if (!canvas) return;

        // 1. ALWAYS destroy the old chart before creating a new one.
        // This fixes the "White Canvas" bug.
        destroyChart();

        // 2. Parse Data Safely
        const labels = courses.map(c => c.Course);
        const data = courses.map(c => {
            let val = c.PassPercentage;
            if (typeof val === 'string') {
                val = parseFloat(val.replace('%', '').trim());
            }
            return (val === null || val === undefined || isNaN(val)) ? 0 : val;
        });
        const bgColors = courses.map((_, i) => subjectColors[i % subjectColors.length]);

        // 3. Create NEW Chart
        const config: ChartConfiguration<'doughnut'> = {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Pass %',
                    data: data,
                    backgroundColor: bgColors,
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%', 
                animation: false, // <--- ANIMATION DISABLED
                layout: { padding: 10 },
                plugins: { 
                    legend: { 
                        position: 'right', 
                        labels: { 
                            boxWidth: 10, 
                            font: { size: 10 }, 
                            color: '#6b7280',
                            usePointStyle: true 
                        } 
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return ` ${context.label}: ${context.parsed}% Passing`;
                            }
                        }
                    }
                }
            }
        };

        chartInstance = new Chart(canvas, config);
    }

    onDestroy(() => {
        destroyChart();
    });
</script>

<div class="card col-span-1 h-87.5 flex flex-col">
    <div class="mb-2 shrink-0">
        <h3 class="font-bold text-gray-700">Subject Performance</h3>
        <p class="text-xs text-gray-400">Pass Percentage per Subject</p>
    </div>
    
    {#if hasData}
        <div class="flex-1 relative w-full min-h-0">
            <canvas bind:this={canvas}></canvas>
        </div>
    {:else}
        <div class="flex-1 flex flex-col items-center justify-center text-center opacity-60 min-h-0">
            <div class="bg-gray-100 p-3 rounded-full mb-3">
                <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
            </div>
            <p class="text-sm font-medium text-gray-500">No subject details found</p>
        </div>
    {/if}
</div>

<style>
    .card { background: white; border-radius: 1.5rem; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
</style>