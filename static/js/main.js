document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const browseButton = document.getElementById('browse-button');
    const fileInfo = document.getElementById('file-info');
    const fileNameDisplay = document.getElementById('file-name');
    const fileSizeDisplay = document.getElementById('file-size');
    const removeFileButton = document.getElementById('remove-file');
    const startProcessButton = document.getElementById('start-process');
    const uploadForm = document.getElementById('upload-form');
    
    // Theme toggle
    const themeToggleButton = document.getElementById('theme-toggle');
    const themeToggleDarkIcon = document.getElementById('theme-toggle-dark-icon');
    const themeToggleLightIcon = document.getElementById('theme-toggle-light-icon');

    function updateThemeIcon() {
        if (localStorage.getItem('color-theme') === 'dark' || (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            themeToggleLightIcon.classList.remove('hidden');
            themeToggleDarkIcon.classList.add('hidden');
            document.documentElement.classList.add('dark');
        } else {
            themeToggleDarkIcon.classList.remove('hidden');
            themeToggleLightIcon.classList.add('hidden');
            document.documentElement.classList.remove('dark');
        }
    }

    updateThemeIcon(); // Set initial icon

    themeToggleButton.addEventListener('click', () => {
        // toggle theme
        if (localStorage.getItem('color-theme')) {
            if (localStorage.getItem('color-theme') === 'light') {
                localStorage.setItem('color-theme', 'dark');
            } else {
                localStorage.setItem('color-theme', 'light');
            }
        } else {
            if (document.documentElement.classList.contains('dark')) {
                localStorage.setItem('color-theme', 'light');
            } else {
                localStorage.setItem('color-theme', 'dark');
            }
        }
        updateThemeIcon();
    });


    // File Upload Logic
    if (dropZone && fileInput && browseButton && fileInfo && fileNameDisplay && fileSizeDisplay && removeFileButton && startProcessButton) {
        browseButton.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', () => {
            handleFile(fileInput.files[0]);
        });

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('border-accent1', 'dark:border-accent1');
            dropZone.classList.remove('border-accent1/50');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('border-accent1', 'dark:border-accent1');
            dropZone.classList.add('border-accent1/50');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-accent1', 'dark:border-accent1');
            dropZone.classList.add('border-accent1/50');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files; // Important to assign to the input
                handleFile(files[0]);
            }
        });
        
        removeFileButton.addEventListener('click', () => {
            fileInput.value = ''; // Clear the file input
            fileInfo.classList.add('hidden');
            dropZone.classList.remove('hidden');
            startProcessButton.disabled = true;
            // Hide progress bar if it was visible
            const progressContainer = document.getElementById('progress-container');
            if (progressContainer) {
                progressContainer.classList.add('hidden');
            }
        });

        function handleFile(file) {
            if (file && file.type === 'text/csv') {
                fileNameDisplay.textContent = file.name;
                fileSizeDisplay.textContent = `${(file.size / 1024).toFixed(1)} KB`;
                fileInfo.classList.remove('hidden');
                dropZone.classList.add('hidden'); // Hide drop zone
                startProcessButton.disabled = false;
            } else {
                // Reset if not a CSV or no file
                removeFileButton.click(); // Simulate click to reset UI
                alert('Please upload a valid .csv file.');
            }
        }
    } else {
        console.error('One or more file upload elements are missing from the DOM.');
    }

    // Form submission and progress - basic version
    if (uploadForm && startProcessButton) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault(); // Prevent default form submission

            if (!fileInput.files || fileInput.files.length === 0) {
                alert('Please select a CSV file to upload.');
                return;
            }

            startProcessButton.disabled = true;
            startProcessButton.textContent = 'Processing...';

            const progressContainer = document.getElementById('progress-container');
            const progressBar = document.getElementById('progress-bar');
            const progressPercentage = document.getElementById('progress-percentage');
            const currentStatus = document.getElementById('current-status');

            if (progressContainer && progressBar && progressPercentage && currentStatus) {
                progressContainer.classList.remove('hidden');
                progressBar.style.width = '0%';
                progressPercentage.textContent = '0%';
                currentStatus.textContent = 'Preparing to upload...';
            }

            const formData = new FormData(uploadForm);

            try {
                if (currentStatus) currentStatus.textContent = 'Uploading file...';
                // Visually indicate upload has started
                if (progressBar) progressBar.style.width = '50%'; 
                if (progressPercentage) progressPercentage.textContent = '50%';

                const response = await fetch('/upload_csv', {
                    method: 'POST',
                    body: formData,
                });

                if (response.ok) {
                    let successMessage = 'File uploaded and processed successfully!';
                    try {
                        const resultText = await response.text(); // Changed from response.json()
                        // If the server sends a meaningful text response, you might use it.
                        // For now, we'll stick to a generic success message if response.ok, 
                        // as parsing HTML for a specific message can be unreliable.
                        // If you expect a specific text format, you can parse resultText here.
                        if (resultText && resultText.trim() !== "") {
                            // Example: if server sends plain text success
                            // successMessage = resultText;
                        }
                        console.log('Server success response (text):', resultText); // Log the text response
                    } catch (textError) {
                        console.warn('Error reading response text on success:', textError);
                    }

                    if (currentStatus) currentStatus.textContent = successMessage;
                    if (progressBar) progressBar.style.width = '100%';
                    if (progressPercentage) progressPercentage.textContent = '100%';
                    // הצגת הודעת הצלחה
                    const successMessageDiv = document.getElementById('success-message');
                    if (successMessageDiv) {
                        successMessageDiv.classList.remove('hidden');
                    }
                } else {
                    let errorMessage = '❌ Error uploading file.';
                    let errorDetails = `Server responded with status ${response.status}`;
                    try {
                        const errorText = await response.text(); // Changed from response.json()
                        console.warn('Server error response (text):', errorText); // Log the text error
                        // You could try to extract a more specific error from HTML/text if needed,
                        // but for now, we use a generic message + status.
                        if (errorText && errorText.trim() !== "") {
                           // errorDetails = errorText; // This might be too verbose if it's full HTML
                        }
                        errorMessage = `❌ Error uploading file: ${errorDetails}`;
                    } catch (textError) {
                        console.warn('Error reading response text on error:', textError);
                        errorMessage = `❌ Error uploading file: ${errorDetails} (and unable to read error body)`;
                    }
                    if (currentStatus) currentStatus.textContent = errorMessage;
                    if (progressBar) {
                        progressBar.style.width = '50%';
                    }
                    if (progressPercentage) progressPercentage.textContent = 'Error';
                }
            } catch (error) {
                console.error('Fetch error:', error);
                const networkErrorMessage = '❌ Error uploading file: Network error or server unavailable.';
                if (currentStatus) currentStatus.textContent = networkErrorMessage;
                if (progressBar) progressBar.style.width = '0%';
                if (progressPercentage) progressPercentage.textContent = 'Error';
                // alert(networkErrorMessage); // Alert was not explicitly requested for network errors
            } finally {
                startProcessButton.disabled = false;
                startProcessButton.textContent = 'Start Process';
                // The user did not ask to hide the progress bar or reset the file input here
                // So we leave it as is, allowing the user to see the final status.
            }
        });
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
}); 