const dropArea = document.querySelector('.drop-section');
const listSection = document.querySelector('.list-section');
const listContainer = document.querySelector('.list');
const fileSelector = document.querySelector('.file-selector');
const fileSelectorInput = document.querySelector('.file-selector-input');
const button = document.querySelector('.list-section button');
const downloadButton = document.querySelector('.download-btn');
const analysisSection = document.querySelector('.analysis');//Analysis Section
const cards = document.querySelectorAll('.card')
const bar_ctx = document.getElementById('barChart').getContext('2d');

let downloadUrl = null; 
let JSONdata = null;
let selectedFile = null; // Store selected file until Convert is clicked

// Upload files with browse button
fileSelector.addEventListener('click', () => fileSelectorInput.click());

fileSelectorInput.addEventListener('change', () => {
    const file = fileSelectorInput.files[0];
    if (file && isPDF(file.type)) {
        prepareFile(file);
    }
});

// Drag file over the area
dropArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    if ([...e.dataTransfer.items].some(item => isPDF(item.type))) {
        dropArea.classList.add('drag-over-effect');
    }
});

dropArea.addEventListener('dragleave', () => {
    dropArea.classList.remove('drag-over-effect');
});

// Drop file in area
dropArea.addEventListener('drop', (e) => {
    e.preventDefault();
    dropArea.classList.remove('drag-over-effect');

    const file = (e.dataTransfer.items?.[0]?.getAsFile?.()) || e.dataTransfer.files[0];

    if (file && isPDF(file.type)) {
        prepareFile(file);
    }
});

function isPDF(type) {
    return type === 'application/pdf';
}

function prepareFile(file) {
    selectedFile = file;
    listContainer.innerHTML = '';
    listSection.style.display = 'block';

    const li = document.createElement('li');
    li.classList.add('in-prog');
    li.innerHTML = `
        <div class="col">
            <img class="pdflogo" src="./icons/pdf.svg" alt="pdf-logo">
        </div>
        <div class="col">
            <div class="file-name">
                <div class="name">${file.name}</div>
                <span></span>
            </div>
            <div class="file-progress"><span></span></div>
            <div class="file-size">${(file.size / (1024 * 1024)).toFixed(3)} MB</div>
        </div>
        <div class="col">
            <i class="fa-solid fa-trash-can trash"></i>
        </div>`;

    listContainer.prepend(li);
}

// Convert button (trigger upload)
button.addEventListener('click', () => {
    if (!selectedFile) return;

    const li = listContainer.querySelector('li');
    const progressSpan = li.querySelector('.file-progress span');
    const percentText = li.querySelector('.file-name span');

    button.disabled = true;
    button.classList.add('loading');
    button.querySelector('span').textContent = 'Converting...';

    const formData = new FormData();
    formData.append('file', selectedFile);

    fetch('/process-pdf', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log("JSON received from backend:", data);
        JSONdata = data.data;

        downloadUrl = data.download_url;
        downloadButton.style.display = 'flex';

        //button go brr brrr....
        li.classList.add('complete');
        li.classList.remove('in-prog');
        percentText.innerText = '100%';
        progressSpan.style.width = '100%';

        button.querySelector('span').textContent = 'Done!';
        setTimeout(() => {
            button.querySelector('span').textContent = 'Submitted';
            button.disabled = false;
        }, 2000);

        analysisSection.style.display = 'block';

        // //Analysis Scroll animation    
        // setTimeout(() => {
        //     analysisSection.scrollIntoView({ behavior: 'smooth' ,block: 'start'});
        // }, 300);

        const offset = analysisSection.offsetTop - (window.innerHeight / 2) + (analysisSection.offsetHeight / 2);
        window.scrollTo({
        top: offset,
        behavior: "smooth"
        });

        // Cards Fade in effect
        cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('visible');
        }, index * 100); // stagger effect , cards appear one after another 100ms delay
        });

        // cards[0].innerHTML = ` //how to set the content
        //     <pre>${JSON.stringify(JSONdata, null, 2)}</pre>
        // `;

        // Bar chart view
        const barChart = new Chart(bar_ctx, {
            type: 'bar',  
            data: {
                labels: JSONdata.map(d => d.Department),
                datasets: [{
                    label: 'Pass Percentage',
                    data: JSONdata.map(d => d.PassPercentage),
                    backgroundColor: JSONdata.map((_, i) => `hsl(${i * 40 % 360}, 70%, 60%)`),
                    borderColor: '#fff',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 900,
                    easing: 'easeOutCubic'
                },
                plugins: {
                    tooltip: {
                        enabled: true,
                        callbacks: {
                            label: context => {
                                const label = context.label || '';
                                const value = context.parsed.y || 0;
                                return `${label}: ${value}%`;
                            }
                        }
                    },
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            boxWidth: 20,
                            padding: 15
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Pass Percentage'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Department'
                        }
                    }
                }
            }
        });

    })
    .catch(error => {
        console.error("Upload error:", error);
        li.classList.add('error');
        percentText.innerText = 'Failed';
        progressSpan.style.backgroundColor = 'red';

        button.querySelector('span').textContent = 'Failed!';
        setTimeout(() => {
            button.querySelector('span').textContent = 'Convert';
            button.disabled = false;
        }, 2000);
    });
});

//Download Button
downloadButton.addEventListener('click', () => {
    if(!downloadUrl) return;

    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = 'processed_output.xlsx';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
});

// Deletion
listContainer.addEventListener('click', (e) => {
    if (e.target.classList.contains('trash')) {
        const fileItem = e.target.closest('li');
        if (fileItem) {
            const progressSpan = fileItem.querySelector('.file-progress span');
            const percentText = fileItem.querySelector('.file-name span');

            if (progressSpan) progressSpan.style.width = '0%';
            if (percentText) percentText.innerText = '0%';

            fileItem.classList.remove('complete', 'in-prog', 'error');

            fileItem.remove();
            listSection.style.display = 'none';
            selectedFile = null;
            fileSelectorInput.value = '';

            button.disabled = false;
            button.classList.remove('loading');
            button.querySelector('span').textContent = 'Submit';
        }
    }
});
