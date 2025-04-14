const dropArea = document.querySelector('.drop-section');
const listSection = document.querySelector('.list-section');
const listContainer = document.querySelector('.list');
const fileSelector = document.querySelector('.file-selector');
const fileSelectorInput = document.querySelector('.file-selector-input');
const button = document.querySelector('.list-section button');

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
    selectedFile = file; // Store the file for upload later
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
                <span>0%</span>
            </div>
            <div class="file-progress"><span></span></div>
            <div class="file-size">${(file.size / (1024 * 1024)).toFixed(3)} MB</div>
        </div>
        <div class="col">
            <i class="fas fa-xmark cross"></i>
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
    .then(response => response.blob())
    .then(blob => {
        // Download file
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'output.xlsx';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        li.classList.add('complete');
        li.classList.remove('in-prog');
        percentText.innerText = '100%';
        progressSpan.style.width = '100%';

        button.querySelector('span').textContent = 'Done!';
        setTimeout(() => {
            button.querySelector('span').textContent = 'Convert';
            button.disabled = false;
        }, 2000);
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

// Deletion
listContainer.addEventListener('click', (e) => {
    if (e.target.classList.contains('trash')) {
        const fileItem = e.target.closest('li');
        if (fileItem) {
            fileItem.remove();
            listSection.style.display = 'none';
            selectedFile = null;
            fileSelectorInput.value = '';
        }
    }
});
