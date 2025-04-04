document.addEventListener("DOMContentLoaded", function () {
    let fileInput = document.getElementById("pdfInput");
    let uploadButton = document.querySelector(".upload-button");
    let uploadedFile = document.querySelector(".file-block");
    let fileName = document.querySelector(".file-name");
    let fileSize = document.querySelector(".file-size");
    let progressBar = document.querySelector(".progress-bar");
    let cannotUploadMessage = document.querySelector(".cannot-upload-message");

    // Reset file input when clicked
    fileInput.addEventListener("click", () => {
        fileInput.value = '';
    });

    // Handle file selection
    fileInput.addEventListener("change", () => {
        let file = fileInput.files[0];
        if (!file) return;

        fileName.innerText = file.name;
        fileSize.innerText = (file.size / 1024).toFixed(1) + " KB";
        uploadedFile.style.display = "flex";
        progressBar.style.width = "0%";
    });

    // Form submission handling
    document.getElementById("uploadForm").addEventListener("submit", function (e) {
        e.preventDefault(); // Prevent default form submission

        let file = fileInput.files[0];
        if (!file) {
            cannotUploadMessage.style.display = "flex";
            return;
        }

        let formData = new FormData();
        formData.append("file", file);

        console.log("Uploading file:", file.name);

        fetch("http://127.0.0.1:8000/process-pdf/", {
            method: "POST",
            body: formData,
        })
        .then(response => {
            console.log("Response status:", response.status);
            if (!response.ok) {
                return response.text().then(text => { throw new Error(text) });
            }
            return response.blob();
        })
        .then(blob => {
            let link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = "output.xlsx";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            uploadButton.innerHTML = `<span class="material-icons-outlined upload-button-icon"> check_circle </span> Uploaded`;
        })
        .catch(error => {
            console.error("Upload Error:", error);
            cannotUploadMessage.style.display = "flex";
        });
    });
});
