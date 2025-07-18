// Website Generator Wizard JavaScript

class WebsiteWizard {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 4;
        this.outputPath = ''; // This will be set by the backend response
        this.formData = {
            websiteName: '',
            websiteDescription: '',
            websiteLogo: {}, // Note: Logo data is not sent to backend in this version
            websiteType: 'restaurant',
            restaurantPhone: '',
            restaurantEmail: '',
            restaurantAddress: '',
            operatingHours: {
                monday: { open: '09:00', close: '22:00', isOpen: true },
                tuesday: { open: '09:00', close: '22:00', isOpen: true },
                wednesday: { open: '09:00', close: '22:00', isOpen: true },
                thursday: { open: '09:00', close: '22:00', isOpen: true },
                friday: { open: '09:00', close: '23:00', isOpen: true },
                saturday: { open: '09:00', close: '23:00', isOpen: true },
                sunday: { open: '10:00', close: '21:00', isOpen: true }
            },
            facebookUrl: '',
            instagramUrl: '',
            twitterUrl: '',
            pages: ['home', 'about', 'contact', 'terms', 'privacy'],
            primaryColor: '#3B82F6',
            secondaryColor: '#1E40AF',
            accentColor: '#60A5FA',
            typography: 'inter',
            selectedFont: 'inter'
        };
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateStepDisplay();
    }

    bindEvents() {
        document.getElementById('nextBtn').addEventListener('click', () => this.nextStep());
        document.getElementById('prevBtn').addEventListener('click', () => this.prevStep());
        document.getElementById('generateBtn').addEventListener('click', () => this.generateWebsite());

        const form = document.getElementById('websiteWizard');
        form.addEventListener('input', (e) => {
            const { name, value, type, checked } = e.target;
            if (name) {
                if (type === 'checkbox' && name === 'pages') {
                    const pages = new Set(this.formData.pages);
                    checked ? pages.add(value) : pages.delete(value);
                    this.formData.pages = Array.from(pages);
                } else {
                    this.formData[name] = value;
                }
                this.validateCurrentStep();
            }
        });

        form.querySelectorAll('.day-hours input').forEach(input => {
            input.addEventListener('change', () => this.updateOperatingHours());
        });

        document.getElementById('downloadBtn').addEventListener('click', () => this.downloadFiles());
        document.getElementById('newProjectBtn').addEventListener('click', () => this.startNewProject());
    }

    updateOperatingHours() {
        const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
        days.forEach(day => {
            const isOpen = document.getElementById(day).checked;
            const openTime = document.getElementById(`${day}-open`).value;
            const closeTime = document.getElementById(`${day}-close`).value;
            this.formData.operatingHours[day] = { open: openTime, close: closeTime, isOpen: isOpen };
        });
    }

    async generateWebsite() {
        const generateBtn = document.getElementById('generateBtn');
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-cog fa-spin"></i> Generating... Please wait...';

        const modal = document.getElementById('generationModal');
        modal.classList.add('active');

        try {
            // Ensure operating hours are up-to-date before sending
            this.updateOperatingHours();

            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.formData),
            });

            const result = await response.json();
            modal.classList.remove('active');

            if (response.ok && result.status === 'success') {
                this.outputPath = result.output_path; // Store the real path from the backend
                this.showSuccessWithPreview();
            } else {
                // Display the actual error message from the backend
                alert(`Error: ${result.message || 'An unknown error occurred while generating the website.'}`);
            }

        } catch (error) {
            modal.classList.remove('active');
            console.error('Fetch Error:', error);
            alert('A network or server error occurred. Please check the console and backend logs.');
        } finally {
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-magic"></i> Generate AI Restaurant Website';
        }
    }

    showSuccessWithPreview() {
        const previewUrlSpan = document.getElementById('previewUrl');
        const restaurantName = this.formData.websiteName.toLowerCase().replace(/[^a-z0-9]/g, '-') || 'your-restaurant';
        previewUrlSpan.textContent = `${restaurantName}.com`;

        const iframe = document.getElementById('websitePreview');
        const previewLoading = document.getElementById('previewLoading');

        // Construct the correct preview path based on the backend response
        const siteFolderName = this.outputPath.split(/\/|\\/).pop();
        // CORRECTED PATH: Points to the new static route in Flask
        const previewPath = `/Generator/${siteFolderName}/index.html`;

        iframe.src = previewPath;
        previewLoading.classList.remove('hidden');
        iframe.classList.remove('loaded');

        iframe.onload = () => {
            previewLoading.classList.add('hidden');
            iframe.classList.add('loaded');
        };
        iframe.onerror = () => {
            previewLoading.innerHTML = `<div class="preview-error"><i class="fas fa-exclamation-circle"></i><p>Could not load preview. Check if the server generated files at: ${previewPath}</p></div>`;
        };

        document.getElementById('successModal').classList.add('active');
    }

    async downloadFiles() {
        const emailModal = document.getElementById('emailModal');
        emailModal.classList.add('active');

        document.getElementById('sendEmailBtn').onclick = async () => {
            const email = document.getElementById('userEmail').value;
            if (!this.validateEmail(document.getElementById('userEmail'))) {
                alert('Please enter a valid email address.');
                return;
            }

            const sendBtn = document.getElementById('sendEmailBtn');
            sendBtn.disabled = true;
            sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';

            try {
                const response = await fetch('/api/send-zip', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: email,
                        output_path: this.outputPath
                    }),
                });

                const result = await response.json();

                if (result.status === 'success') {
                    alert('Email sent successfully!');
                    emailModal.classList.remove('active');
                } else {
                    alert(`Error sending email: ${result.message}`);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred while sending the email.');
            } finally {
                sendBtn.disabled = false;
                sendBtn.innerHTML = 'Send Email';
            }
        };

        document.getElementById('cancelEmailBtn').onclick = () => {
            emailModal.classList.remove('active');
        };
    }

    startNewProject() {
        window.location.reload();
    }

    nextStep() {
        if (this.currentStep < this.totalSteps) {
            this.currentStep++;
            this.updateStepDisplay();
        }
    }

    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateStepDisplay();
        }
    }

    updateStepDisplay() {
        // Hide all steps
        document.querySelectorAll('.step-content').forEach(step => {
            step.classList.remove('active');
        });

        // Show current step
        document.getElementById(`step${this.currentStep}`).classList.add('active');

        // Update progress bar
        const progress = ((this.currentStep - 1) / (this.totalSteps - 1)) * 100;
        document.querySelector('.progress-fill').style.width = `${progress}%`;

        // Update navigation buttons
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const generateBtn = document.getElementById('generateBtn');

        prevBtn.style.display = this.currentStep === 1 ? 'none' : 'block';
        nextBtn.style.display = this.currentStep === this.totalSteps ? 'none' : 'block';
        generateBtn.style.display = this.currentStep === this.totalSteps ? 'block' : 'none';

        this.validateCurrentStep();
    }

    validateCurrentStep() {
        const nextBtn = document.getElementById('nextBtn');
        const generateBtn = document.getElementById('generateBtn');
        let isValid = true;

        switch (this.currentStep) {
            case 1:
                isValid = this.formData.websiteName.trim() !== '' &&
                    this.formData.restaurantPhone.trim() !== '' &&
                    this.formData.restaurantEmail.trim() !== '' &&
                    this.formData.restaurantAddress.trim() !== '';
                break;
            case 2:
                isValid = this.formData.pages.length > 0;
                break;
            case 3:
                isValid = true; // Design step is always valid
                break;
            case 4:
                isValid = this.isFormComplete();
                break;
        }

        if (this.currentStep < this.totalSteps) {
            nextBtn.disabled = !isValid;
        } else {
            generateBtn.disabled = !isValid;
        }
    }

    isFormComplete() {
        return this.formData.websiteName.trim() !== '' &&
            this.formData.restaurantPhone.trim() !== '' &&
            this.formData.restaurantEmail.trim() !== '' &&
            this.formData.restaurantAddress.trim() !== '' &&
            this.formData.pages.length > 0;
    }

    updateFormData() {
        // Update form data from DOM elements
        this.formData.websiteName = document.getElementById('websiteName').value;
        this.formData.websiteDescription = document.getElementById('websiteDescription').value;
        this.formData.restaurantPhone = document.getElementById('restaurantPhone').value;
        this.formData.restaurantEmail = document.getElementById('restaurantEmail').value;
        this.formData.restaurantAddress = document.getElementById('restaurantAddress').value;
        this.formData.facebookUrl = document.getElementById('facebookUrl').value;
        this.formData.instagramUrl = document.getElementById('instagramUrl').value;
        this.formData.twitterUrl = document.getElementById('twitterUrl').value;

        // Update pages
        const selectedPages = document.querySelectorAll('input[name="pages"]:checked');
        this.formData.pages = Array.from(selectedPages).map(cb => cb.value);

        // Update colors
        this.formData.primaryColor = document.getElementById('primaryColor').value;
        this.formData.secondaryColor = document.getElementById('secondaryColor').value;
        this.formData.accentColor = document.getElementById('accentColor').value;

        // Update typography
        const selectedTypography = document.querySelector('.typography-option.selected');
        if (selectedTypography) {
            this.formData.typography = selectedTypography.dataset.font;
            this.formData.selectedFont = selectedTypography.dataset.font;
        }
    }

    selectTypography(option) {
        document.querySelectorAll('.typography-option').forEach(opt => opt.classList.remove('selected'));
        option.classList.add('selected');
        this.formData.typography = option.dataset.font;
        this.formData.selectedFont = option.dataset.font;
    }

    setupFontSelector() {
        document.querySelectorAll('.typography-option').forEach(option => {
            option.addEventListener('click', () => this.selectTypography(option));
        });
    }

    closeModal(modalId) {
        document.getElementById(modalId).classList.remove('active');
    }

    validateEmail(emailInput) {
        const email = emailInput.value;
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Operating hours functionality
    setupOperatingHours() {
        const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

        days.forEach(day => {
            const checkbox = document.getElementById(day);
            const timeInputs = document.querySelectorAll(`#${day}-open, #${day}-close`);

            checkbox.addEventListener('change', () => {
                timeInputs.forEach(input => {
                    input.disabled = !checkbox.checked;
                });
            });
        });

        // Reset hours button
        document.getElementById('resetHoursBtn').addEventListener('click', () => {
            days.forEach(day => {
                document.getElementById(`${day}-open`).value = '09:00';
                document.getElementById(`${day}-close`).value = '22:00';
                document.getElementById(day).checked = true;
            });
            this.updateOperatingHours();
        });
    }
}

// Initialize the wizard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.wizard = new WebsiteWizard();
});
