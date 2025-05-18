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
        uploadForm.addEventListener('submit', (e) => {
            // e.preventDefault(); // Remove this if you want the native form submission to occur for Flask.
                               // Or, keep it and handle submission with fetch for more control over UI updates (e.g., progress bar)
            
            if (!fileInput.files || fileInput.files.length === 0) {
                e.preventDefault(); // Prevent submission if no file
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
                currentStatus.textContent = 'Uploading file...';

                // Simulate progress for now.
                // In a real app, you'd use XHR/Fetch API and listen to 'progress' events
                // or use a library that handles this.
                // For Flask, since it's a direct form submission, detailed progress is harder without client-side handling of the upload.
                // We'll show a generic "processing" state.
                let progress = 0;
                const interval = setInterval(() => {
                    progress += 10;
                    if (progress <= 100) {
                        progressBar.style.width = progress + '%';
                        progressPercentage.textContent = progress + '%';
                        if (progress === 100) {
                           currentStatus.textContent = 'Processing on server... Please wait.';
                        }
                    } else {
                        // If we were using fetch, we wouldn't need this part of the interval.
                        // Since it's a form submit, the page will reload or redirect.
                        // This is just a visual placeholder.
                        clearInterval(interval);
                    }
                }, 200);
            }
            
            // Allow form to submit after UI updates if not using fetch
            // If using fetch, the e.preventDefault() above would be active,
            // and you would trigger the fetch request here.
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