document.addEventListener("DOMContentLoaded", function() {
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("fileInput");
    const uploadStatus = document.getElementById("uploadStatus");
    const fileListElement = document.getElementById("fileList");

    // Event handlers for drag-and-drop zone
    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("dragover");
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        const files = e.dataTransfer.files;
        uploadFiles(files);
    });

    fileInput.addEventListener("change", (e) => {
        uploadFiles(e.target.files);
    });

    // Event handles from buttom "Refresh File List"
    const refreshButton = document.getElementById("refreshButton");
    if (refreshButton) {
        refreshButton.addEventListener("click", fetchFiles);
    } else {
        console.error("Refresh button not found");
    }

    // Function load file
    async function uploadFiles(files) {
        const formData = new FormData();
        for (let file of files) {
            formData.append("file", file);
        }

        uploadStatus.innerHTML = `<div class="alert alert-info">Uploading file(s)...</div>`;

        try {
            const response = await fetch("/files/upload", { method: "POST", body: formData });
            if (response.ok) {
                uploadStatus.innerHTML = `<div class="alert alert-success">File uploaded successfully!</div>`;
                const fileData = await response.json();
                addFileToList(fileData.file);

                // Refresh list files after succesffull load
                await fetchFiles();
            } else {
                const errorData = await response.json();
                uploadStatus.innerHTML = `<div class="alert alert-danger">Error uploading file: ${errorData.detail || "Unknown error"}</div>`;
            }
        } catch (error) {
            uploadStatus.innerHTML = `<div class="alert alert-danger">Network error: ${error.message}</div>`;
            console.error("Upload error:", error);
        }
    }

    // Funcition added file in list
    function addFileToList(file) {
        const listItem = document.createElement('li');
        listItem.classList.add('file-item');
        listItem.innerHTML = `
            <div class="file-info">
                <span class="file-name">${file.file_name}</span>
                <span class="file-size">Size: ${file.size} bytes</span>
                <span class="file-uploaded">Uploaded at: ${new Date(file.uploaded_at).toLocaleString()}</span>
            </div>
            <div class="file-actions">
                <button class="btn btn-success download-btn" data-file-id="${file.id}" data-file-name="${file.file_name}">Download</button>
                <button class="btn btn-danger delete-btn" data-file-id="${file.id}" data-file-name="${file.file_name}">Delete</button>
            </div>
        `;

        const downloadBtn = listItem.querySelector('.download-btn');
        downloadBtn.addEventListener('click', () => {
            const fileId = downloadBtn.getAttribute('data-file-id');
            const fileName = downloadBtn.getAttribute('data-file-name');
            downloadFile(fileId, fileName);
        });

        const deleteBtn = listItem.querySelector('.delete-btn');
        deleteBtn.addEventListener('click', () => {
            const fileId = deleteBtn.getAttribute('data-file-id');
            const fileName = deleteBtn.getAttribute('data-file-name');
            deleteFile(fileId, fileName, listItem);
        });

        fileListElement.appendChild(listItem);
    }

    // Function download file
    async function downloadFile(fileId, fileName) {
        try {
            const encodedFileName = encodeURIComponent(fileName);
            const response = await fetch(`/files/download?file_name=${encodedFileName}`, { method: 'GET' });
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = fileName;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            } else {
                alert('Failed to download file.');
            }
        } catch (error) {
            console.error('Error downloading file:', error);
            alert('Error downloading file.');
        }
    }

    // Function deleted file
    async function deleteFile(fileId, fileName, listItem) {
        if (confirm('Are you sure you want to delete this file?')) {
            listItem.innerHTML = `<div class="alert alert-info">Deleting file...</div>`;
            try {
                const encodedFileName = encodeURIComponent(fileName);
                const response = await fetch(`/files/delete?file_name=${encodedFileName}`, { method: 'DELETE' });
                if (response.ok) {
                    listItem.remove();
                    alert('File deleted successfully.');
                } else {
                    listItem.innerHTML = `<div class="alert alert-danger">Failed to delete file.</div>`;
                }
            } catch (error) {
                listItem.innerHTML = `<div class="alert alert-danger">Error deleting file: ${error.message}</div>`;
                console.error('Error deleting file:', error);
            }
        }
    }

    // Function load list files
    async function fetchFiles() {
        try {
            fileListElement.innerHTML = `<div class="alert alert-info">Loading files...</div>`;
            const response = await fetch('/files/list-files', { method: 'GET' });
            const data = await response.json();

            if (data.files && data.files.length > 0) {
                fileListElement.innerHTML = ''; // Clean list before added new files
                data.files.forEach(file => {
                    addFileToList(file);
                });
            } else {
                fileListElement.innerHTML = `<div class="alert alert-warning">No files uploaded yet.</div>`;
            }
        } catch (error) {
            fileListElement.innerHTML = `<div class="alert alert-danger">Failed to load files: ${error.message}</div>`;
            console.error("Error fetching files:", error);
        }
    }

    // Initialization list files when load pages
    fetchFiles();
});