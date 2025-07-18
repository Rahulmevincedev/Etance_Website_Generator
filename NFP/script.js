// Website Generator Wizard JavaScript

class WebsiteWizard {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 4;
        this.outputPath = '';
        this.formData = {
            websiteName: '',
            websiteDescription: '',
            websiteLogo: null,
            websiteType: 'restaurant', // Always restaurant
            // Contact Information
            restaurantPhone: '',
            restaurantEmail: '',
            restaurantAddress: '',
            // Operating Hours
            operatingHours: {
                monday: { open: '09:00', close: '22:00', isOpen: true },
                tuesday: { open: '09:00', close: '22:00', isOpen: true },
                wednesday: { open: '09:00', close: '22:00', isOpen: true },
                thursday: { open: '09:00', close: '22:00', isOpen: true },
                friday: { open: '09:00', close: '23:00', isOpen: true },
                saturday: { open: '09:00', close: '23:00', isOpen: true },
                sunday: { open: '10:00', close: '21:00', isOpen: true }
            },
            // Social Media
            facebookUrl: '',
            instagramUrl: '',
            twitterUrl: '',
            // Pages
            pages: ['home', 'menu', 'about', 'contact', 'terms', 'privacy'],
            // Design
            primaryColor: '#3B82F6',
            secondaryColor: '#1E40AF',
            accentColor: '#60A5FA',
            typography: '',
            selectedFont: 'inter'
            // layout: '' // Commented out for future use
        };

        this.init();
    }

    init() {
        this.currentStep = 1;
        this.updateStepDisplay();
        this.bindEvents();
        this.setupOperatingHoursListeners();
        this.setupColorPreview();
        this.setupFontSelector();

        // Set default typography
        const defaultTypography = document.querySelector('.typography-option[data-font="inter"]');
        if (defaultTypography) {
            this.selectTypography(defaultTypography);
        }

        // Initialize form data
        this.updateFormData();
    }

    bindEvents() {
        // Navigation buttons
        document.getElementById('nextBtn').addEventListener('click', () => this.nextStep());
        document.getElementById('prevBtn').addEventListener('click', () => this.prevStep());
        document.getElementById('generateBtn').addEventListener('click', () => this.generateWebsite());

        // Basic info inputs with validation
        document.getElementById('websiteName').addEventListener('input', (e) => {
            this.formData.websiteName = e.target.value;
            this.validateCurrentStep();
        });

        document.getElementById('websiteDescription').addEventListener('input', (e) => {
            this.formData.websiteDescription = e.target.value;
            this.validateCurrentStep();
        });

        // Contact information inputs with validation
        document.getElementById('restaurantPhone').addEventListener('input', (e) => {
            this.formData.restaurantPhone = e.target.value;
            this.validatePhoneNumber(e.target);
            this.validateCurrentStep();
        });

        document.getElementById('restaurantEmail').addEventListener('input', (e) => {
            this.formData.restaurantEmail = e.target.value;
            this.validateEmail(e.target);
            this.validateCurrentStep();
        });

        document.getElementById('restaurantAddress').addEventListener('input', (e) => {
            this.formData.restaurantAddress = e.target.value;
            this.validateCurrentStep();
        });

        // Operating hours event listeners
        this.setupOperatingHoursListeners();

        // Social media inputs
        document.getElementById('facebookUrl').addEventListener('input', (e) => {
            this.formData.facebookUrl = e.target.value;
            this.validateUrl(e.target);
            this.validateCurrentStep();
        });

        document.getElementById('instagramUrl').addEventListener('input', (e) => {
            this.formData.instagramUrl = e.target.value;
            this.validateUrl(e.target);
            this.validateCurrentStep();
        });

        document.getElementById('twitterUrl').addEventListener('input', (e) => {
            this.formData.twitterUrl = e.target.value;
            this.validateUrl(e.target);
            this.validateCurrentStep();
        });

        // Website logo upload
        document.getElementById('websiteLogo').addEventListener('change', (e) => {
            this.handleLogoUpload(e);
        });

        // Page checkboxes
        document.addEventListener('change', (e) => {
            if (e.target.name === 'pages') {
                this.updateFormData();
                this.validateCurrentStep();
            }
        });

        // Color picker inputs
        document.getElementById('primaryColor').addEventListener('input', (e) => {
            this.formData.primaryColor = e.target.value;
            this.updateColorPreview();
            this.validateCurrentStep();
        });

        document.getElementById('secondaryColor').addEventListener('input', (e) => {
            this.formData.secondaryColor = e.target.value;
            this.updateColorPreview();
            this.validateCurrentStep();
        });

        document.getElementById('accentColor').addEventListener('input', (e) => {
            this.formData.accentColor = e.target.value;
            this.updateColorPreview();
            this.validateCurrentStep();
        });

        // Typography options
        document.querySelectorAll('.typography-option').forEach(option => {
            option.addEventListener('click', () => this.selectTypography(option));
        });

        // Modal close buttons
        document.getElementById('openFullPreview').addEventListener('click', () => this.openFullPreview());
        document.getElementById('refreshPreview').addEventListener('click', () => this.refreshPreview());
        document.getElementById('downloadBtn').addEventListener('click', () => this.downloadFiles());
        document.getElementById('newProjectBtn').addEventListener('click', () => this.startNewProject());

        // Website preview iframe loading
        const iframe = document.getElementById('websitePreview');
        iframe.addEventListener('load', () => this.handlePreviewLoad());

        // Also listen for when srcdoc is set
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'srcdoc') {
                    // Give it a moment to render
                    setTimeout(() => this.handlePreviewLoad(), 500);
                }
            });
        });
        observer.observe(iframe, { attributes: true });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight' || e.key === 'Enter') {
                if (this.currentStep < this.totalSteps && this.isCurrentStepValid()) {
                    this.nextStep();
                }
            } else if (e.key === 'ArrowLeft') {
                if (this.currentStep > 1) {
                    this.prevStep();
                }
            }
        });
    }

    // Validation methods
    validateEmail(input) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const isValid = emailRegex.test(input.value);
        this.setInputValidation(input, isValid, 'Please enter a valid email address');
        return isValid;
    }

    validatePhoneNumber(input) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        const cleanPhone = input.value.replace(/[\s\-\(\)]/g, '');
        const isValid = phoneRegex.test(cleanPhone) && cleanPhone.length >= 10;
        this.setInputValidation(input, isValid, 'Please enter a valid phone number (minimum 10 digits)');
        return isValid;
    }

    validateUrl(input) {
        if (input.value.trim() === '') return true; // Optional field
        try {
            new URL(input.value);
            this.setInputValidation(input, true);
            return true;
        } catch {
            this.setInputValidation(input, false, 'Please enter a valid URL');
            return false;
        }
    }

    setInputValidation(input, isValid, errorMessage = '') {
        input.classList.remove('error', 'valid');

        // Remove existing error message
        const existingError = input.parentNode.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        if (input.value.trim() !== '') {
            if (isValid) {
                input.classList.add('valid');
            } else {
                input.classList.add('error');
                if (errorMessage) {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'error-message';
                    errorDiv.textContent = errorMessage;
                    input.parentNode.appendChild(errorDiv);
                }
            }
        }
    }

    // Operating Hours Setup
    setupOperatingHoursListeners() {
        const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

        days.forEach(day => {
            // Day checkbox listeners
            const checkbox = document.getElementById(day);
            if (checkbox) {
                checkbox.addEventListener('change', (e) => {
                    this.formData.operatingHours[day].isOpen = e.target.checked;
                    this.updateDayTimeInputs(day);
                    this.validateCurrentStep();
                });
            }

            // Time input listeners
            const openInput = document.getElementById(`${day}-open`);
            const closeInput = document.getElementById(`${day}-close`);

            if (openInput) {
                openInput.addEventListener('change', (e) => {
                    this.formData.operatingHours[day].open = e.target.value;
                    this.validateCurrentStep();
                });
            }

            if (closeInput) {
                closeInput.addEventListener('change', (e) => {
                    this.formData.operatingHours[day].close = e.target.value;
                    this.validateCurrentStep();
                });
            }
        });

        // Action button listeners
        const copyBtn = document.getElementById('copyHoursBtn');
        const resetBtn = document.getElementById('resetHoursBtn');

        if (copyBtn) {
            copyBtn.addEventListener('click', (e) => {
                e.preventDefault(); // Prevent form submission
                e.stopPropagation(); // Stop event bubbling
                this.copyHoursToAllDays();
            });
        }

        if (resetBtn) {
            resetBtn.addEventListener('click', (e) => {
                e.preventDefault(); // Prevent form submission
                e.stopPropagation(); // Stop event bubbling
                this.resetOperatingHours();
            });
        }
    }

    updateDayTimeInputs(day) {
        const dayRow = document.querySelector(`[data-day="${day}"]`);
        const timeInputs = dayRow.querySelectorAll('input[type="time"]');
        const isOpen = this.formData.operatingHours[day].isOpen;

        timeInputs.forEach(input => {
            input.disabled = !isOpen;
        });

        dayRow.setAttribute('data-closed', !isOpen);
    }

    copyHoursToAllDays() {
        // Get Monday's hours as the template
        const mondayHours = this.formData.operatingHours.monday;
        const days = ['tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

        days.forEach(day => {
            this.formData.operatingHours[day] = {
                open: mondayHours.open,
                close: mondayHours.close,
                isOpen: mondayHours.isOpen
            };

            // Update UI
            const checkbox = document.getElementById(day);
            const openInput = document.getElementById(`${day}-open`);
            const closeInput = document.getElementById(`${day}-close`);

            if (checkbox) checkbox.checked = mondayHours.isOpen;
            if (openInput) openInput.value = mondayHours.open;
            if (closeInput) closeInput.value = mondayHours.close;

            this.updateDayTimeInputs(day);
        });

        this.validateCurrentStep();
    }

    resetOperatingHours() {
        const defaultHours = {
            monday: { open: '09:00', close: '22:00', isOpen: true },
            tuesday: { open: '09:00', close: '22:00', isOpen: true },
            wednesday: { open: '09:00', close: '22:00', isOpen: true },
            thursday: { open: '09:00', close: '22:00', isOpen: true },
            friday: { open: '09:00', close: '23:00', isOpen: true },
            saturday: { open: '09:00', close: '23:00', isOpen: true },
            sunday: { open: '10:00', close: '21:00', isOpen: true }
        };

        Object.keys(defaultHours).forEach(day => {
            this.formData.operatingHours[day] = { ...defaultHours[day] };

            // Update UI
            const checkbox = document.getElementById(day);
            const openInput = document.getElementById(`${day}-open`);
            const closeInput = document.getElementById(`${day}-close`);

            if (checkbox) checkbox.checked = defaultHours[day].isOpen;
            if (openInput) openInput.value = defaultHours[day].open;
            if (closeInput) closeInput.value = defaultHours[day].close;

            this.updateDayTimeInputs(day);
        });

        this.validateCurrentStep();
    }

    formatOperatingHours() {
        const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
        const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

        const formattedHours = days.map((day, index) => {
            const hours = this.formData.operatingHours[day];
            if (!hours.isOpen) {
                return `${dayNames[index]}: Closed`;
            }

            const openTime = this.formatTime(hours.open);
            const closeTime = this.formatTime(hours.close);
            return `${dayNames[index]}: ${openTime} - ${closeTime}`;
        });

        return formattedHours.join('<br>');
    }

    formatTime(time24) {
        const [hours, minutes] = time24.split(':');
        const hour12 = parseInt(hours) % 12 || 12;
        const ampm = parseInt(hours) >= 12 ? 'PM' : 'AM';
        return `${hour12}:${minutes} ${ampm}`;
    }

    // Color preview setup and update
    setupColorPreview() {
        this.updateColorPreview();
    }

    updateColorPreview() {
        const previewHeader = document.getElementById('previewHeader');
        const previewButton = document.getElementById('previewButton');

        if (previewHeader && previewButton) {
            previewHeader.style.backgroundColor = this.formData.primaryColor;
            previewButton.style.backgroundColor = this.formData.accentColor;

            // Update CSS custom properties for dynamic theming
            document.documentElement.style.setProperty('--preview-primary', this.formData.primaryColor);
            document.documentElement.style.setProperty('--preview-secondary', this.formData.secondaryColor);
            document.documentElement.style.setProperty('--preview-accent', this.formData.accentColor);
        }
    }

    handleLogoUpload(event) {
        const file = event.target.files[0];
        if (file && file.type.startsWith('image/')) {
            this.formData.websiteLogo = file;
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = new Image();
                img.onload = () => {
                    // Create canvas to analyze image
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);

                    // Get image data for color analysis
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
                    const colors = this.extractDominantColors(imageData);

                    // Update color inputs with extracted colors
                    document.getElementById('primaryColor').value = colors.primary;
                    document.getElementById('secondaryColor').value = colors.secondary;
                    document.getElementById('accentColor').value = colors.accent;

                    // Update form data
                    this.formData.primaryColor = colors.primary;
                    this.formData.secondaryColor = colors.secondary;
                    this.formData.accentColor = colors.accent;

                    // Update color preview
                    this.updateColorPreview();

                    // Update logo preview
                    const logoPreview = document.getElementById('logoPreview');
                    logoPreview.innerHTML = `
                        <div class="logo-preview-content">
                            <img src="${e.target.result}" alt="Logo Preview">
                            <button type="button" class="delete-logo-btn" title="Remove Logo">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    `;

                    // Add delete functionality
                    const deleteBtn = logoPreview.querySelector('.delete-logo-btn');
                    if (deleteBtn) {
                        deleteBtn.addEventListener('click', () => this.deleteLogo());
                    }
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    }

    extractDominantColors(imageData) {
        const colorMap = new Map();
        const quality = 10; // Skip some pixels for better performance

        // Analyze pixels with quality setting
        for (let i = 0; i < imageData.length; i += 4 * quality) {
            const r = imageData[i];
            const g = imageData[i + 1];
            const b = imageData[i + 2];
            const a = imageData[i + 3];

            // Skip transparent pixels
            if (a < 128) continue;

            // Convert to hex
            const hex = this.rgbToHex(r, g, b);
            colorMap.set(hex, (colorMap.get(hex) || 0) + 1);
        }

        // Sort colors by frequency
        const sortedColors = Array.from(colorMap.entries())
            .sort((a, b) => b[1] - a[1])
            .map(entry => entry[0]);

        // Get distinct colors with good contrast
        const distinctColors = [];
        for (const color of sortedColors) {
            // Skip if we already have 3 colors
            if (distinctColors.length >= 3) break;

            // Convert hex to RGB for contrast calculation
            const rgb = this.hexToRgb(color);

            // Check if this color has good contrast with existing colors
            const hasGoodContrast = distinctColors.every(existingColor => {
                const existingRgb = this.hexToRgb(existingColor);
                return this.calculateContrastRatio(rgb, existingRgb) >= 1.5;
            });

            if (hasGoodContrast) {
                distinctColors.push(color);
            }
        }

        // If we only have two colors, generate a complementary accent
        if (distinctColors.length === 2) {
            const primaryRgb = this.hexToRgb(distinctColors[0]);
            const secondaryRgb = this.hexToRgb(distinctColors[1]);

            // Create accent by adjusting the primary color's brightness and saturation
            const accentRgb = {
                r: Math.round(Math.min(255, primaryRgb.r * 1.2)),
                g: Math.round(Math.min(255, primaryRgb.g * 1.2)),
                b: Math.round(Math.min(255, primaryRgb.b * 1.2))
            };

            distinctColors[2] = this.rgbToHex(accentRgb.r, accentRgb.g, accentRgb.b);
        }

        return {
            primary: distinctColors[0] || '#3B82F6',   // Default blue if no color found
            secondary: distinctColors[1] || '#1E40AF', // Darker blue
            accent: distinctColors[2] || '#60A5FA'     // Lighter blue
        };
    }

    calculateContrastRatio(rgb1, rgb2) {
        // Calculate relative luminance
        const getLuminance = (r, g, b) => {
            const [rs, gs, bs] = [r, g, b].map(c => {
                c = c / 255;
                return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
            });
            return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
        };

        const l1 = getLuminance(rgb1.r, rgb1.g, rgb1.b);
        const l2 = getLuminance(rgb2.r, rgb2.g, rgb2.b);

        const lighter = Math.max(l1, l2);
        const darker = Math.min(l1, l2);

        return (lighter + 0.05) / (darker + 0.05);
    }

    rgbToHex(r, g, b) {
        return '#' + [r, g, b].map(x => {
            const hex = x.toString(16);
            return hex.length === 1 ? '0' + hex : hex;
        }).join('');
    }

    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }

    deleteLogo() {
        // Reset the file input
        const fileInput = document.getElementById('websiteLogo');
        fileInput.value = '';

        // Reset the preview
        const logoPreview = document.getElementById('logoPreview');
        logoPreview.innerHTML = `
            <div class="logo-placeholder">
                <i class="fas fa-camera"></i>
                <span>Upload Logo</span>
            </div>
        `;

        // Reset the form data
        this.formData.websiteLogo = null;

        this.validateCurrentStep();
    }

    selectTypography(option) {
        document.querySelectorAll('.typography-option').forEach(o => o.classList.remove('selected'));
        option.classList.add('selected');
        this.formData.typography = option.dataset.font;
        this.formData.selectedFont = option.dataset.font;
        this.validateCurrentStep();
    }

    // Layout selection - Commented out for future use
    // selectLayout(option) {
    //     document.querySelectorAll('.layout-option').forEach(o => o.classList.remove('selected'));
    //     option.classList.add('selected');
    //     this.formData.layout = option.dataset.layout;
    //     this.validateCurrentStep();
    // }

    updateFormData() {
        // Update pages
        this.formData.pages = Array.from(document.querySelectorAll('input[name="pages"]:checked'))
            .map(input => input.value);
    }

    validateCurrentStep() {
        const currentStep = document.querySelector('.step-content.active');
        let isValid = true;

        if (currentStep.id === 'step1') {
            // Restaurant Name validation (3-40 characters)
            const nameInput = document.getElementById('websiteName');
            if (nameInput.value.length < 3 || nameInput.value.length > 40) {
                this.setInputValidation(nameInput, false, 'Restaurant name must be between 3 and 40 characters');
                isValid = false;
            } else {
                this.setInputValidation(nameInput, true);
            }

            // Description validation (max 500 characters)
            const descInput = document.getElementById('websiteDescription');
            if (descInput.value.length > 500) {
                this.setInputValidation(descInput, false, 'Description must not exceed 500 characters');
                isValid = false;
            } else {
                this.setInputValidation(descInput, true);
            }

            // Phone validation (improved regex for international format)
            const phoneInput = document.getElementById('restaurantPhone');
            const phoneRegex = /^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$/;
            if (!phoneRegex.test(phoneInput.value)) {
                this.setInputValidation(phoneInput, false, 'Please enter a valid phone number');
                isValid = false;
            } else {
                this.setInputValidation(phoneInput, true);
            }

            // Email validation (improved regex)
            const emailInput = document.getElementById('restaurantEmail');
            const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            if (!emailRegex.test(emailInput.value)) {
                this.setInputValidation(emailInput, false, 'Please enter a valid email address');
                isValid = false;
            } else {
                this.setInputValidation(emailInput, true);
            }

            // Address validation (min 10, max 200 characters)
            const addressInput = document.getElementById('restaurantAddress');
            if (addressInput.value.length < 10 || addressInput.value.length > 200) {
                this.setInputValidation(addressInput, false, 'Address must be between 10 and 200 characters');
                isValid = false;
            } else {
                this.setInputValidation(addressInput, true);
            }

            // Social Media URL validations (optional)
            const socialInputs = ['facebookUrl', 'instagramUrl', 'twitterUrl'];
            socialInputs.forEach(id => {
                const input = document.getElementById(id);
                if (input.value && !this.validateUrl(input.value)) {
                    this.setInputValidation(input, false, 'Please enter a valid URL');
                    isValid = false;
                } else {
                    this.setInputValidation(input, true);
                }
            });
        }

        // Update navigation buttons
        const nextBtn = document.getElementById('nextBtn');
        const generateBtn = document.getElementById('generateBtn');
        const requiredMsg = document.getElementById('requiredFieldsMsg');

        if (this.currentStep < this.totalSteps) {
            nextBtn.disabled = !isValid;
            if (requiredMsg) {
                requiredMsg.style.display = !isValid ? 'flex' : 'none';
            }
        }

        if (this.currentStep === this.totalSteps) {
            // generateBtn.disabled = !this.isFormComplete(); // TEMP: Disabled validation for generate button
        }

        return isValid;
    }

    isCurrentStepValid() {
        return this.validateCurrentStep();
    }

    isFormComplete() {
        const nameValid = this.formData.websiteName.trim() !== '';
        const phoneValid = this.formData.restaurantPhone.trim() !== '' &&
            this.validatePhoneNumber(document.getElementById('restaurantPhone'));
        const emailValid = this.formData.restaurantEmail.trim() !== '' &&
            this.validateEmail(document.getElementById('restaurantEmail'));
        const addressValid = this.formData.restaurantAddress.trim() !== '';
        const pagesValid = this.formData.pages.length > 0;
        const colorsValid = this.formData.primaryColor !== '' &&
            this.formData.secondaryColor !== '' &&
            this.formData.accentColor !== '';
        const designValid = this.formData.typography !== '';
        // && this.formData.layout !== ''; // Layout commented out for future use

        return nameValid && phoneValid && emailValid && addressValid &&
            pagesValid && colorsValid && designValid;
    }

    nextStep() {
        if (this.currentStep < this.totalSteps && this.isCurrentStepValid()) {
            this.currentStep++;
            this.updateStepDisplay();
            this.updateProgress();

            if (this.currentStep === 4) {
                this.updateReview();
            }
        }
    }

    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateStepDisplay();
            this.updateProgress();
        }
    }

    updateStepDisplay() {
        // Hide all step contents
        document.querySelectorAll('.step-content').forEach(step => {
            step.classList.remove('active');
        });

        // Show current step
        document.getElementById(`step${this.currentStep}`).classList.add('active');

        // Update progress steps
        document.querySelectorAll('.step').forEach((step, index) => {
            const stepNumber = index + 1;
            step.classList.remove('active', 'completed');

            if (stepNumber === this.currentStep) {
                step.classList.add('active');
            } else if (stepNumber < this.currentStep) {
                step.classList.add('completed');
            }
        });

        // Update navigation buttons
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');

        prevBtn.disabled = this.currentStep === 1;

        if (this.currentStep === this.totalSteps) {
            nextBtn.style.display = 'none';
        } else {
            nextBtn.style.display = 'flex';
            nextBtn.disabled = !this.isCurrentStepValid();
        }

        // Update form data if on step 2
        if (this.currentStep === 2) {
            this.updateFormData();
        }

        this.validateCurrentStep();
    }

    updateProgress() {
        const progressFill = document.getElementById('progressFill');
        const percentage = (this.currentStep / this.totalSteps) * 100;
        progressFill.style.width = `${percentage}%`;
    }

    updateReview() {
        // Update restaurant info
        document.getElementById('reviewName').innerHTML = `
            <div class="review-item">
                <strong>${this.formData.websiteName || 'Not specified'}</strong>
                <p>${this.formData.websiteDescription || 'No description provided'}</p>
                ${this.formData.websiteLogo ?
                `<div class="review-logo">
                        <img src="${URL.createObjectURL(this.formData.websiteLogo)}" alt="Logo" style="max-width: 60px; max-height: 60px; border-radius: 4px; margin-top: 8px;">
                    </div>` :
                '<p class="no-logo">No logo uploaded</p>'
            }
            </div>
        `;

        // Update contact details
        const socialLinks = [];
        if (this.formData.facebookUrl) socialLinks.push(`Facebook: ${this.formData.facebookUrl}`);
        if (this.formData.instagramUrl) socialLinks.push(`Instagram: ${this.formData.instagramUrl}`);
        if (this.formData.twitterUrl) socialLinks.push(`Twitter: ${this.formData.twitterUrl}`);

        document.getElementById('reviewContact').innerHTML = `
            <div class="contact-details">
                <div class="contact-item">
                    <strong>Phone:</strong> ${this.formData.restaurantPhone || 'Not provided'}
                </div>
                <div class="contact-item">
                    <strong>Email:</strong> ${this.formData.restaurantEmail || 'Not provided'}
                </div>
                <div class="contact-item">
                    <strong>Address:</strong> ${this.formData.restaurantAddress || 'Not provided'}
                </div>
                <div class="contact-item">
                    <strong>Operating Hours:</strong><br>
                    ${this.formatOperatingHours()}
                </div>
                ${socialLinks.length > 0 ?
                `<div class="contact-item"><strong>Social Media:</strong><br>${socialLinks.join('<br>')}</div>` : ''
            }
            </div>
        `;

        // Update pages
        document.getElementById('reviewPages').innerHTML = `
            <ul class="review-list">
                ${this.formData.pages.map(page => `<li>${this.formatPageName(page)}</li>`).join('')}
            </ul>
        `;

        // Update design with color swatches
        document.getElementById('reviewDesign').innerHTML = `
            <div class="review-content">
                <div class="color-review">
                    <div class="color-item">
                        <strong>Primary Color:</strong>
                        <div class="color-swatch" style="background-color: ${this.formData.primaryColor}"></div>
                    </div>
                    <div class="color-item">
                        <strong>Secondary Color:</strong>
                        <div class="color-swatch" style="background-color: ${this.formData.secondaryColor}"></div>
                    </div>
                    <div class="color-item">
                        <strong>Accent Color:</strong>
                        <div class="color-swatch" style="background-color: ${this.formData.accentColor}"></div>
                    </div>
                </div>
                <p><strong>Typography:</strong> ${this.formatFontName(this.formData.typography)}</p>
            </div>
        `;
    }

    formatPageName(page) {
        const pageNames = {
            'home': 'Homepage',
            'menu': 'Food Menu',
            'about': 'About Us',
            'contact': 'Contact & Location',
            'drinks-menu': 'Drinks & Wine List',
            'dessert-menu': 'Dessert Menu',
            'specials': 'Daily Specials',


            'terms': 'Terms & Conditions',
            'privacy': 'Privacy Policy'
        };

        return pageNames[page] || page.charAt(0).toUpperCase() + page.slice(1).replace(/[-_]/g, ' ');
    }

    formatColorName(color) {
        const colors = {
            '#3B82F6': 'Professional Blue',
            '#10B981': 'Nature Green',
            '#8B5CF6': 'Creative Purple',
            '#F97316': 'Energetic Orange',
            '#EF4444': 'Bold Red',
            '#1E40AF': 'Modern Dark'
        };
        return colors[color] || color;
    }

    formatFontName(font) {
        const fonts = {
            inter: 'Inter (Modern)',
            roboto: 'Roboto (Clean)',
            playfair: 'Playfair Display (Elegant)',
            opensans: 'Open Sans (Friendly)',
            montserrat: 'Montserrat (Professional)',
            lato: 'Lato (Readable)',
            poppins: 'Poppins (Trendy)',
            oswald: 'Oswald (Bold)',
            nunito: 'Nunito (Rounded)',
            quicksand: 'Quicksand (Soft)',
            merriweather: 'Merriweather (Classic)',
            lora: 'Lora (Warm)',
            ptserif: 'PT Serif (Traditional)',
            cormorant: 'Cormorant Garamond (Luxury)',
            dancing: 'Dancing Script (Stylish)',
            pacifico: 'Pacifico (Casual)',
            satisfy: 'Satisfy (Smooth)',
            greatvibes: 'Great Vibes (Elegant Script)',
            bebas: 'Bebas Neue (Impact)',
            righteous: 'Righteous (Fun)'
        };
        return fonts[font] || font;
    }

    formatLayoutName(layout) {
        return layout.charAt(0).toUpperCase() + layout.slice(1);
    }

    async generateWebsite() {
        const generateBtn = document.getElementById('generateBtn');
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-cog fa-spin"></i> Generating...';

        // Show generation modal
        const modal = document.getElementById('generationModal');
        modal.classList.add('active');

        // Simulate generation process in the modal
        await this.simulateGeneration();

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.formData),
            });

            const result = await response.json();

            if (result.status === 'success') {
                this.outputPath = result.output_path; // Store the output path
                modal.classList.remove('active');
                this.showSuccessWithPreview();
            } else {
                alert(`Error generating website: ${result.message}`);
                modal.classList.remove('active');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while generating the website.');
            modal.classList.remove('active');
        } finally {
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-magic"></i> Generate AI Restaurant Website';
        }
    }

    showSuccessWithPreview() {
        // Update preview URL with restaurant name
        const previewUrl = document.getElementById('previewUrl');
        const restaurantName = this.formData.websiteName.toLowerCase()
            .replace(/[^a-z0-9]/g, '-')
            .replace(/-+/g, '-')
            .replace(/^-|-$/g, '');
        previewUrl.textContent = `${restaurantName || 'your-restaurant'}.com`;

        // Show loading state
        const previewLoading = document.getElementById('previewLoading');
        const websitePreview = document.getElementById('websitePreview');

        previewLoading.classList.remove('hidden');
        websitePreview.classList.remove('loaded');

        // Show success modal
        document.getElementById('successModal').classList.add('active');

        // Generate custom preview with user data
        setTimeout(() => {
            this.generateCustomPreview();
        }, 1000);
    }

    generateCustomPreview() {
        const iframe = document.getElementById('websitePreview');
        const previewLoading = document.getElementById('previewLoading');

        try {
            // Generate custom HTML with user data
            const customHTML = this.createCustomPreviewHTML();

            // Set iframe content
            iframe.srcdoc = customHTML;

            // Add event listener for iframe load
            iframe.onload = () => {
                // Add Font Awesome to the iframe
                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                const fontAwesome = iframeDoc.createElement('link');
                fontAwesome.rel = 'stylesheet';
                fontAwesome.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
                iframeDoc.head.appendChild(fontAwesome);

                // Add all required Google Fonts
                const fonts = iframeDoc.createElement('link');
                fonts.rel = 'stylesheet';
                fonts.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto:wght@300;400;500;700&family=Playfair+Display:wght@400;500;600;700&family=Open+Sans:wght@300;400;500;600;700&family=Montserrat:wght@300;400;500;600;700&family=Lato:wght@300;400;700&family=Poppins:wght@300;400;500;600;700&family=Oswald:wght@300;400;500;600;700&family=Merriweather:wght@300;400;700&family=Dancing+Script:wght@400;500;600;700&family=Nunito:wght@300;400;600;700&family=Quicksand:wght@300;400;500;700&family=Lora:wght@400;500;600;700&family=PT+Serif:wght@400;700&family=Cormorant+Garamond:wght@400;500;600;700&family=Pacifico&family=Satisfy&family=Great+Vibes&family=Bebas+Neue&family=Righteous&display=swap';
                iframeDoc.head.appendChild(fonts);

                // Show the preview
                setTimeout(() => {
                    iframe.classList.add('loaded');
                    previewLoading.classList.add('hidden');
                }, 500);
            };
        } catch (error) {
            console.error('Error generating custom preview:', error);
            previewLoading.innerHTML = `
                <div class="preview-error">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Error loading preview. Please try again.</p>
                </div>
            `;
        }
    }

    createCustomPreviewHTML() {
        // Check if logo exists
        let hasLogo = this.formData.websiteLogo ? true : false;
        let logoHtml = '';
        if (hasLogo) {
            try {
                const logoSrc = URL.createObjectURL(this.formData.websiteLogo);
                logoHtml = `<img class="logo-main scale-with-grid" src="${logoSrc}" alt="${this.formData.websiteName} Logo" style="max-width:120px;max-height:120px;border-radius:50%;background:#fff;padding:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);"/>`;
            } catch (error) {
                hasLogo = false;
            }
        } else {
            logoHtml = `<img class="logo-main scale-with-grid" src="/NFP2/Cafe/assets/images/cafe-logo-white.png" alt="Cafe Logo" style="max-width:120px;max-height:120px;border-radius:50%;background:#fff;padding:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);"/>`;
        }

        // Navigation links
        const navLinks = [
            { href: '#home', label: 'HOME' },
            { href: '#about', label: 'ABOUT US' },
            { href: '#gallery', label: 'GALLERY' },
            { href: '#menu', label: 'MENU' },
            { href: '#contact', label: 'CONTACT' }
        ].map(link => `<li><a href="${link.href}"><span>${link.label}</span></a></li>`).join('');

        // Contact info
        const phone = this.formData.restaurantPhone || '+61 (0) 333 333 333';
        const email = this.formData.restaurantEmail || 'info@eatanceapp.com';
        const address = this.formData.restaurantAddress || 'Level 13, 2 Elizabeth St, Melbourne, Victoria 3000, Australia';
        const description = this.formData.websiteDescription || 'Welcome to our cafe! Enjoy delicious food and a cozy atmosphere.';
        const name = this.formData.websiteName || 'Eatance Cafe';

        // Hours
        const hoursHtml = this.generateHoursHTML();

        // Font mapping for Google Fonts
        const fontMap = {
            'inter': 'Inter',
            'roboto': 'Roboto',
            'playfair': 'Playfair+Display',
            'opensans': 'Open+Sans',
            'montserrat': 'Montserrat',
            'lato': 'Lato',
            'poppins': 'Poppins',
            'oswald': 'Oswald',
            'nunito': 'Nunito',
            'quicksand': 'Quicksand',
            'merriweather': 'Merriweather',
            'lora': 'Lora',
            'ptserif': 'PT+Serif',
            'cormorant': 'Cormorant+Garamond',
            'dancing': 'Dancing+Script',
            'pacifico': 'Pacifico',
            'satisfy': 'Satisfy',
            'greatvibes': 'Great+Vibes',
            'bebas': 'Bebas+Neue',
            'righteous': 'Righteous'
        };
        const selectedFontKey = this.formData.selectedFont || 'inter';
        const selectedFont = fontMap[selectedFontKey] || 'Inter';
        const googleFontLink = `<link href="https://fonts.googleapis.com/css2?family=${selectedFont}:wght@300;400;500;600;700&display=swap" rel="stylesheet">`;
        const fontFamily = this.getFontFamily(selectedFontKey);

        // Cafe-style preview HTML with dynamic color and font overrides
        return `
<!DOCTYPE html>
<html class="no-js">
<head>
    <meta charset="utf-8" />
    <title>${name}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
    <link rel="stylesheet" href="/NFP2/Cafe/assets/css/global.css" />
    <link rel="stylesheet" href="/NFP2/Cafe/assets/css/structure.css" />
    <link rel="stylesheet" href="/NFP2/Cafe/assets/css/cafe3.css" />
    <link rel="stylesheet" href="/NFP2/Cafe/assets/css/style-demo.css" />
    ${googleFontLink}
    <link href="https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
    <style>
      body, html {
        font-family: ${fontFamily} !important;
      }
      .header--banner, .btnstyle, .button_label, .footer_copy, .themecolor, .highlight, .mcb-section {
        /* Use primary color for main highlights */
        --primary-color: ${this.formData.primaryColor};
      }
      .header--banner {
        background-color: ${this.formData.primaryColor} !important;
      }
      .btnstyle, .button_label {
        background: ${this.formData.accentColor} !important;
        border-color: ${this.formData.accentColor} !important;
        color: #fff !important;
      }
      .themecolor, .highlight {
        color: ${this.formData.primaryColor} !important;
      }
      .mcb-section, .section--pad {
        background-color: ${this.formData.secondaryColor}10 !important;
      }
      a, .footer-link:hover {
        color: ${this.formData.accentColor} !important;
      }
      h1, h2, h3, h4, h5, h6 {
        font-family: ${fontFamily} !important;
      }
    </style>
    <style>body { pointer-events: none; }</style>
</head>
<body class="home">
    <div id="Header_creative">
        <div class="creative-wrapper">
            <div id="Top_bar">
                <div class="one clearfix">
                    <div class="top_bar_left">
                        <div class="logo" style="text-align:center;">${logoHtml}</div>
                        <div class="menu_wrapper">
                            <nav id="menu">
                                <ul id="menu-main-menu" class="menu menu-main">
                                    ${navLinks}
                                </ul>
                            </nav>
                        </div>
                    </div>
                    <div class="banner_wrapper">
                        <p style="color: #fff;">${address.replace(/\n/g, '<br/>')}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div id="Wrapper">
        <div class="header--banner" style="background-image: url(/NFP2/Cafe/assets/images/cafe3-slider-bg.jpg);">
            <div class="header--banner-inner">
                <span class="angle-top"></span>
                <span class="angle-bottom"></span>
                <h1>Welcome To ${name}</h1>
                <p>${description}</p>
            </div>
        </div>
        <div id="Content">
            <div class="content_wrapper clearfix">
                <div class="sections_group">
                    <div class="entry-content">
                        <div class="section mcb-section about--section section--pad" id="about">
                            <div class="section_wrapper mcb-section-inner">
                                <div class="column_wrap mob--reverse">
                                    <div class="wrap mcb-wrap one-second valign-top clearfix mob--mt25">
                                        <div class="mcb-wrap-inner">
                                            <div class="column mcb-column column_column">
                                                <div class="column_attr clearfix">
                                                    <h6 class="themecolor">ABOUT US —</h6>
                                                    <h2 class="mb30">A few words about our cafe</h2>
                                                    <p class="mb20">${description}</p>
                                                    <ul class="list_check mb20">
                                                        <li>Fresh ingredients, daily specials</li>
                                                        <li>Cozy atmosphere, friendly staff</li>
                                                    </ul>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="wrap mcb-wrap one-second valign-top clearfix about--img">
                                        <div class="mcb-wrap-inner">
                                            <div class="column mcb-column full-width column_image">
                                                <div class="image_frame image_item scale-with-grid no_border">
                                                    <div class="image_wrapper">
                                                        <img class="scale-with-grid" src="/NFP2/Cafe/assets/images/cafe3-home-pic1.jpg" />
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="section mcb-section section--pad" id="menu">
                            <div class="section_wrapper mcb-section-inner">
                                <div class="column_wrap">
                                    <div class="wrap mcb-wrap one valign-top clearfix">
                                        <div class="mcb-wrap-inner">
                                            <div class="column mcb-column column_column">
                                                <div class="column_attr clearfix align_center">
                                                    <h6 class="themecolor mb30">OUR MENU</h6>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="wrap mcb-wrap one-third valign-top clearfix mob--mb30">
                                        <div class="mcb-wrap-inner">
                                            <div class="column mcb-column column_image">
                                                <div class="image_frame image_item scale-with-grid aligncenter no_border">
                                                    <div class="image_wrapper">
                                                        <img class="scale-with-grid" src="/NFP2/Cafe/assets/images/cafe3-offer-pic1.jpg" />
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="column mcb-column column_column mt30">
                                                <div class="column_attr clearfix">
                                                    <h3>Aliquam fringilla</h3>
                                                    <h5 class="mb20">Proin risus erat <span style="font-weight: 700; color: #2f1d19;">$1.2</span></h5>
                                                    <p class="mb30" style="color: #a8aaae;">Sed ultrices nisl velit, eu ornare est ullamcorper a. Nunc quis nibh magna. Proin risus erat, fringilla vel purus.</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="wrap mcb-wrap one-third valign-top clearfix mob--mb30">
                                        <div class="mcb-wrap-inner">
                                            <div class="column mcb-column column_image">
                                                <div class="image_frame image_item scale-with-grid aligncenter no_border">
                                                    <div class="image_wrapper">
                                                        <img class="scale-with-grid" src="/NFP2/Cafe/assets/images/cafe3-offer-pic2.jpg" />
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="column mcb-column column_column mt30">
                                                <div class="column_attr clearfix">
                                                    <h3>Quisque lorem</h3>
                                                    <h5 class="mb20">Etiam ullamcorper <span style="font-weight: 700; color: #2f1d19;">$3.5</span></h5>
                                                    <p class="mb30" style="color: #a8aaae;">Sed ultrices nisl velit, eu ornare est ullamcorper a. Nunc quis nibh magna. Proin risus erat, fringilla vel purus.</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="wrap mcb-wrap one-third valign-top clearfix mob--mb30">
                                        <div class="mcb-wrap-inner">
                                            <div class="column mcb-column column_image">
                                                <div class="image_frame image_item scale-with-grid aligncenter no_border">
                                                    <div class="image_wrapper">
                                                        <img class="scale-with-grid" src="/NFP2/Cafe/assets/images/cafe3-offer-pic2.jpg" />
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="column mcb-column column_column mt30">
                                                <div class="column_attr clearfix">
                                                    <h3>Curabitur etkjs ligula</h3>
                                                    <h5 class="mb20">Phasellus fermentum in <span style="font-weight: 700; color: #2f1d19;">$4</span></h5>
                                                    <p class="mb30" style="color: #a8aaae;">Sed ultrices nisl velit, eu ornare est ullamcorper.</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="wrap mcb-wrap full-width valign-top clearfix mt30">
                                        <div class="mcb-wrap-inner">
                                            <div class="column mcb-column full-width column_button">
                                                <div class="button_align align_center">
                                                    <a class="btnstyle" href="#menu"><span class="button_label">SEE FULL MENU</span></a>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="section mcb-section section--pad" id="gallery">
                            <div class="section_wrapper mcb-section-inner">
                                <div class="column_wrap">
                                    <div class="wrap mcb-wrap one valign-top clearfix">
                                        <div class="mcb-wrap-inner">
                                            <div class="column mcb-column column_column">
                                                <div class="column_attr clearfix align_center">
                                                    <h6 class="themecolor mb30">GALLERY</h6>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="wrap mcb-wrap one-fourth valign-top bg-cover clearfix" style="background-image: url(/NFP2/Cafe/assets/images/cafe3-columnbg1.jpg); background-repeat: no-repeat; background-position: center;">
                                        <div class="mcb-wrap-inner">
                                            <div class="column mcb-column column_divider">
                                                <hr class="no_line" style="margin: 0 auto 150px;" />
                                            </div>
                                        </div>
                                    </div>
                                    <div class="wrap mcb-wrap one-fourth valign-top bg-cover clearfix" style="background-image: url(/NFP2/Cafe/assets/images/cafe3-columnbg2.jpg); background-repeat: no-repeat; background-position: center;">
                                        <div class="mcb-wrap-inner">
                                            <div class="column mcb-column column_divider">
                                                <hr class="no_line" style="margin: 0 auto 150px;" />
                                            </div>
                                        </div>
                                    </div>
                                    <div class="wrap mcb-wrap one-fourth valign-top bg-cover clearfix" style="background-image: url(/NFP2/Cafe/assets/images/cafe3-home-pic2.jpg); background-repeat: no-repeat; background-position: center;">
                                        <div class="mcb-wrap-inner">
                                            <div class="column mcb-column column_divider">
                                                <hr class="no_line" style="margin: 0 auto 150px;" />
                                            </div>
                                        </div>
                                    </div>
                                    <div class="wrap mcb-wrap one-fourth valign-top bg-cover clearfix" style="background-image: url(/NFP2/Cafe/assets/images/cafe3-home-pic3.jpg); background-repeat: no-repeat; background-position: center;">
                                        <div class="mcb-wrap-inner">
                                            <div class="column mcb-column column_divider">
                                                <hr class="no_line" style="margin: 0 auto 150px;" />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="section mcb-section section--pad" id="contact">
                            <div class="section_wrapper mcb-section-inner">
                                <div class="column_wrap">
                                    <div class="wrap mcb-wrap one valign-top clearfix">
                                        <div class="mcb-wrap-inner">
                                            <div class="column mcb-column column_column">
                                                <div class="column_attr clearfix align_center">
                                                    <h6 class="themecolor mb30">CONTACT US</h6>
                                                    <p><strong>Phone:</strong> ${phone}<br/><strong>Email:</strong> ${email}<br/><strong>Address:</strong> ${address.replace(/\n/g, '<br/>')}</p>
                                                    <div class="hours-section" style="margin-top:2rem;">${hoursHtml}</div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <footer id="Footer" class="clearfix">
            <div class="widgets_wrapper">
                <div class="container">
                    <div class="column one-third">
                        <aside class="widget_text widget widget_custom_html">
                            <div class="textwidget custom-html-widget">
                                <div style="text-align: center;">
                                    <h6 class="themecolor">DO YOU HAVE A QUESTION?</h6>
                                    <p><a href="mailto:${email}">${email}</a></p>
                                </div>
                            </div>
                        </aside>
                    </div>
                    <div class="column one-third">
                        <aside class="widget_text widget widget_custom_html">
                            <div class="textwidget custom-html-widget">
                                <div style="text-align: center;">
                                    <p>${address.replace(/\n/g, '<br/>')}</p>
                                    <p style="font-size: 28px;">
                                        <a href="#"><i class="icon-twitter-circled"></i></a><a href="#"><i class="icon-facebook-circled"></i></a><a href="#"><i class="icon-skype-circled"></i></a>
                                    </p>
                                </div>
                            </div>
                        </aside>
                    </div>
                    <div class="column one-third">
                        <aside class="widget_text widget widget_custom_html">
                            <div class="textwidget custom-html-widget">
                                <div style="text-align: center;">
                                    <h6 class="themecolor">BOOK A TABLE</h6>
                                    <p>${phone}</p>
                                </div>
                            </div>
                        </aside>
                    </div>
                </div>
            </div>
            <div class="footer_copy">
                <div class="container">
                    <div class="column one">
                        <div class="copyright">&copy; Copyrights & Powered By <a target="_blank" href="https://evincedev.com/"> EvinceDev</a></div>
                    </div>
                </div>
            </div>
        </footer>
    </div>
</body>
</html>
        `;
    }

    generateHoursHTML() {
        const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
        const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

        return days.map((day, index) => {
            const hours = this.formData.operatingHours && this.formData.operatingHours[day] ?
                this.formData.operatingHours[day] :
                { open: '09:00', close: '22:00', isOpen: true };

            const timeDisplay = hours.isOpen ?
                `${this.formatTime(hours.open)} - ${this.formatTime(hours.close)}` :
                'Closed';

            return `
                <div class="hours-day">
                    <span class="day-name">${dayNames[index]}</span>
                    <span class="day-time">${timeDisplay}</span>
                </div>
            `;
        }).join('');
    }

    getSelectedFont() {
        const fontMap = {
            'inter': "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            'roboto': "'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            'playfair': "'Playfair Display', Georgia, serif",
            'opensans': "'Open Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            'montserrat': "'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            'lato': "'Lato', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            'poppins': "'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            'oswald': "'Oswald', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            'nunito': "'Nunito', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            'quicksand': "'Quicksand', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            'merriweather': "'Merriweather', Georgia, serif",
            'lora': "'Lora', Georgia, serif",
            'ptserif': "'PT Serif', Georgia, serif",
            'cormorant': "'Cormorant Garamond', Georgia, serif",
            'dancing': "'Dancing Script', cursive",
            'pacifico': "'Pacifico', cursive",
            'satisfy': "'Satisfy', cursive",
            'greatvibes': "'Great Vibes', cursive",
            'bebas': "'Bebas Neue', sans-serif",
            'righteous': "'Righteous', cursive"
        };
        return fontMap[this.formData.typography] || fontMap['inter'];
    }

    getFontFamily(font) {
        const fontMap = {
            'inter': "'Inter', sans-serif",
            'roboto': "'Roboto', sans-serif",
            'playfair': "'Playfair Display', serif",
            'opensans': "'Open Sans', sans-serif",
            'montserrat': "'Montserrat', sans-serif",
            'lato': "'Lato', sans-serif",
            'poppins': "'Poppins', sans-serif",
            'oswald': "'Oswald', sans-serif",
            'nunito': "'Nunito', sans-serif",
            'quicksand': "'Quicksand', sans-serif",
            'merriweather': "'Merriweather', serif",
            'lora': "'Lora', serif",
            'ptserif': "'PT Serif', serif",
            'cormorant': "'Cormorant Garamond', serif",
            'dancing': "'Dancing Script', cursive",
            'pacifico': "'Pacifico', cursive",
            'satisfy': "'Satisfy', cursive",
            'greatvibes': "'Great Vibes', cursive",
            'bebas': "'Bebas Neue', sans-serif",
            'righteous': "'Righteous', cursive"
        };
        return fontMap[font] || fontMap['inter'];
    }

    loadPreview() {
        // Fallback method for loading static preview
        const iframe = document.getElementById('websitePreview');
        const previewLoading = document.getElementById('previewLoading');

        // Set iframe source to load the preview
        iframe.src = '../nina-vista-restaurant/public/index.html';

        // Set a timeout in case the iframe doesn't load
        setTimeout(() => {
            if (!iframe.classList.contains('loaded')) {
                this.handlePreviewLoad();
            }
        }, 3000);
    }

    handlePreviewLoad() {
        const iframe = document.getElementById('websitePreview');
        const previewLoading = document.getElementById('previewLoading');

        if (iframe && previewLoading) {
            iframe.classList.add('loaded');
            previewLoading.classList.add('hidden');
        }
    }

    openFullPreview() {
        // Open the generated site in a new tab
        window.open('../nina-vista-restaurant/public/index.html', '_blank');
    }

    refreshPreview() {
        const iframe = document.getElementById('websitePreview');
        const previewLoading = document.getElementById('previewLoading');
        const refreshBtn = document.getElementById('refreshPreview');

        // Show loading state
        iframe.classList.remove('loaded');
        previewLoading.classList.remove('hidden');

        // Add spinning animation to refresh button
        refreshBtn.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i>';

        // Clear current content
        iframe.srcdoc = '';
        iframe.src = '';

        // Regenerate custom preview with updated data
        setTimeout(() => {
            this.generateCustomPreview();
        }, 500);

        // Reset refresh button after a delay
        setTimeout(() => {
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
        }, 1500);
    }

    viewGeneratedSite() {
        // This method is no longer used, but keeping for compatibility
        this.openFullPreview();
        this.closeModal('successModal');
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
        // Reset wizard
        this.currentStep = 1;
        this.formData = {
            websiteName: '',
            websiteDescription: '',
            websiteLogo: null,
            websiteType: 'restaurant',
            // Contact Information
            restaurantPhone: '',
            restaurantEmail: '',
            restaurantAddress: '',
            // Operating Hours
            operatingHours: {
                monday: { open: '09:00', close: '22:00', isOpen: true },
                tuesday: { open: '09:00', close: '22:00', isOpen: true },
                wednesday: { open: '09:00', close: '22:00', isOpen: true },
                thursday: { open: '09:00', close: '22:00', isOpen: true },
                friday: { open: '09:00', close: '23:00', isOpen: true },
                saturday: { open: '09:00', close: '23:00', isOpen: true },
                sunday: { open: '10:00', close: '21:00', isOpen: true }
            },
            // Social Media
            facebookUrl: '',
            instagramUrl: '',
            twitterUrl: '',
            // Pages
            pages: ['home', 'menu', 'about', 'contact', 'terms', 'privacy'],
            // Design
            primaryColor: '#3B82F6',
            secondaryColor: '#1E40AF',
            accentColor: '#60A5FA',
            typography: '',
            selectedFont: 'inter'
            // layout: '' // Commented out for future use
        };

        // Reset UI
        document.querySelectorAll('.selected').forEach(el => el.classList.remove('selected'));
        document.querySelectorAll('input[type="checkbox"]').forEach(input => {
            const defaultPages = ['home', 'about', 'contact', 'terms', 'privacy']; // 'menu' removed
            input.checked = defaultPages.includes(input.value);
        });

        // Reset form inputs
        document.getElementById('websiteName').value = '';
        document.getElementById('websiteDescription').value = '';
        document.getElementById('websiteLogo').value = '';
        document.getElementById('restaurantPhone').value = '';
        document.getElementById('restaurantEmail').value = '';
        document.getElementById('restaurantAddress').value = '';
        document.getElementById('facebookUrl').value = '';
        document.getElementById('instagramUrl').value = '';
        document.getElementById('twitterUrl').value = '';

        // Reset operating hours
        this.resetOperatingHours();

        // Reset color pickers
        document.getElementById('primaryColor').value = '#3B82F6';
        document.getElementById('secondaryColor').value = '#1E40AF';
        document.getElementById('accentColor').value = '#60A5FA';

        // Reset validation states
        document.querySelectorAll('.error, .valid').forEach(el => {
            el.classList.remove('error', 'valid');
        });
        document.querySelectorAll('.error-message').forEach(el => el.remove());

        document.getElementById('logoPreview').innerHTML = `
            <div class="logo-placeholder">
                <i class="fas fa-camera"></i>
                <span>Upload Logo</span>
            </div>
        `;

        this.updateColorPreview();
        this.updateStepDisplay();
        this.updateProgress();
        this.closeModal('successModal');
    }

    closeModal(modalId) {
        document.getElementById(modalId).classList.remove('active');
    }

    async simulateGeneration() {
        const steps = document.querySelectorAll('.progress-step');

        for (let i = 0; i < steps.length; i++) {
            const step = steps[i];
            const icon = step.querySelector('i');

            // Update current step to loading
            icon.className = 'fas fa-cog fa-spin';

            // Wait for simulation
            await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));

            // Mark as completed
            icon.className = 'fas fa-check';
        }
    }

    setupFontSelector() {
        const wizard = this; // Fix context for inner functions
        // Store original HTML for revert
        if (!wizard._originalFontDropdownHTML) {
            const dropdown = document.querySelector('.typography-dropdown');
            wizard._originalFontDropdownHTML = dropdown ? dropdown.innerHTML : '';
        }
        const fontDropdown = document.getElementById('customFontDropdown');
        if (!fontDropdown) return;

        // Font data
        const fontGroups = [
            {
                label: 'Recommended', options: [
                    { value: 'inter', label: 'Inter (Modern)' },
                    { value: 'roboto', label: 'Roboto (Clean)' },
                    { value: 'playfair', label: 'Playfair Display (Elegant)' },
                    { value: 'opensans', label: 'Open Sans (Friendly)' },
                    { value: 'montserrat', label: 'Montserrat (Professional)' },
                ]
            },
            {
                label: 'Sans-serif', options: [
                    { value: 'lato', label: 'Lato (Readable)' },
                    { value: 'poppins', label: 'Poppins (Trendy)' },
                    { value: 'oswald', label: 'Oswald (Bold)' },
                    { value: 'nunito', label: 'Nunito (Rounded)' },
                    { value: 'quicksand', label: 'Quicksand (Soft)' },
                ]
            },
            {
                label: 'Serif', options: [
                    { value: 'merriweather', label: 'Merriweather (Classic)' },
                    { value: 'lora', label: 'Lora (Warm)' },
                    { value: 'ptserif', label: 'PT Serif (Traditional)' },
                    { value: 'cormorant', label: 'Cormorant Garamond (Luxury)' },
                ]
            },
            {
                label: 'Handwritten / Script', options: [
                    { value: 'dancing', label: 'Dancing Script (Stylish)' },
                    { value: 'pacifico', label: 'Pacifico (Casual)' },
                    { value: 'satisfy', label: 'Satisfy (Smooth)' },
                    { value: 'greatvibes', label: 'Great Vibes (Elegant Script)' },
                ]
            },
            {
                label: 'Display', options: [
                    { value: 'bebas', label: 'Bebas Neue (Impact)' },
                    { value: 'righteous', label: 'Righteous (Fun)' },
                ]
            }
        ];
        let selectedFont = wizard.formData.typography || 'inter';
        // Ensure default selection on first load
        if (!wizard.formData.typography) {
            wizard.formData.typography = 'inter';
            wizard.formData.selectedFont = 'inter';
            // Update preview
            const typographyPreview = document.getElementById('typographyPreview');
            if (typographyPreview) {
                typographyPreview.querySelector('.font-preview').style.fontFamily = wizard.getFontFamily('inter');
            }
        }
        let open = false;
        let search = '';
        let focusedIndex = -1;
        let filteredOptions = [];

        // Render function
        const render = () => {
            fontDropdown.innerHTML = '';
            fontDropdown.className = 'custom-dropdown' + (open ? ' open' : '');
            // Selected
            const selected = document.createElement('div');
            selected.className = 'custom-dropdown-selected';
            selected.tabIndex = 0;
            selected.setAttribute('role', 'button');
            selected.setAttribute('aria-haspopup', 'listbox');
            selected.setAttribute('aria-expanded', open ? 'true' : 'false');
            selected.innerHTML = fontGroups.flatMap(g => g.options).find(o => o.value === selectedFont)?.label || 'Select font';
            selected.innerHTML += '<span class="custom-dropdown-arrow"><i class="fas fa-chevron-down"></i></span>';
            fontDropdown.appendChild(selected);

            // Panel
            if (open) {
                const panel = document.createElement('div');
                panel.className = 'custom-dropdown-panel';
                // Search
                const searchInput = document.createElement('input');
                searchInput.className = 'custom-dropdown-search';
                searchInput.type = 'text';
                searchInput.placeholder = 'Search fonts...';
                searchInput.value = search;
                panel.appendChild(searchInput);

                // Options container
                const optionsContainer = document.createElement('div');
                optionsContainer.className = 'custom-dropdown-options';
                panel.appendChild(optionsContainer);

                // Function to update options list only
                function updateOptionsList() {
                    optionsContainer.innerHTML = '';
                    filteredOptions = [];
                    fontGroups.forEach(group => {
                        const groupOptions = group.options.filter(o => o.label.toLowerCase().includes(searchInput.value.toLowerCase()));
                        if (groupOptions.length) {
                            const groupLabel = document.createElement('div');
                            groupLabel.className = 'custom-dropdown-group';
                            groupLabel.textContent = group.label;
                            optionsContainer.appendChild(groupLabel);
                            groupOptions.forEach(option => {
                                const opt = document.createElement('div');
                                opt.className = 'custom-dropdown-option' + (option.value === selectedFont ? ' selected' : '');
                                opt.setAttribute('role', 'option');
                                opt.setAttribute('data-value', option.value);
                                opt.textContent = option.label;
                                opt.tabIndex = -1;
                                optionsContainer.appendChild(opt);
                                filteredOptions.push(opt);
                            });
                        }
                    });
                    if (!filteredOptions.length) {
                        const noResults = document.createElement('div');
                        noResults.className = 'custom-dropdown-no-results';
                        noResults.textContent = 'No fonts found.';
                        optionsContainer.appendChild(noResults);
                    }
                    // Focus first option if available
                    if (filteredOptions.length && focusedIndex === -1) focusedIndex = 0;
                    filteredOptions.forEach((opt, i) => {
                        opt.classList.toggle('focused', i === focusedIndex);
                    });
                    // Option click
                    filteredOptions.forEach((opt, i) => {
                        opt.addEventListener('mousedown', e => {
                            e.preventDefault();
                            select(opt.getAttribute('data-value'));
                        });
                    });
                }

                // Initial options render
                updateOptionsList();

                // Event listeners
                searchInput.addEventListener('input', e => {
                    search = e.target.value;
                    focusedIndex = -1;
                    updateOptionsList();
                });
                searchInput.addEventListener('keydown', e => {
                    if (e.key === 'ArrowDown') {
                        e.preventDefault();
                        if (filteredOptions.length) {
                            focusedIndex = (focusedIndex + 1) % filteredOptions.length;
                            updateOptionsList();
                        }
                    } else if (e.key === 'ArrowUp') {
                        e.preventDefault();
                        if (filteredOptions.length) {
                            focusedIndex = (focusedIndex - 1 + filteredOptions.length) % filteredOptions.length;
                            updateOptionsList();
                        }
                    } else if (e.key === 'Enter') {
                        e.preventDefault();
                        if (filteredOptions[focusedIndex]) {
                            select(filteredOptions[focusedIndex].getAttribute('data-value'));
                        }
                    } else if (e.key === 'Escape') {
                        open = false;
                        render();
                        selected.focus();
                    }
                });

                fontDropdown.appendChild(panel);
                // Focus search input
                setTimeout(() => {
                    searchInput.focus();
                    searchInput.setSelectionRange(searchInput.value.length, searchInput.value.length);
                }, 0);
            }
            // Selected click
            selected.addEventListener('click', () => {
                open = !open;
                render();
            });
            selected.addEventListener('keydown', e => {
                if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
                    open = true;
                    render();
                }
            });
        };
        // Select function
        const select = (value) => {
            selectedFont = value;
            wizard.formData.typography = value;
            wizard.formData.selectedFont = value;
            open = false;
            search = '';
            focusedIndex = -1;
            render();
            // Update preview
            const typographyPreview = document.getElementById('typographyPreview');
            if (typographyPreview) {
                typographyPreview.querySelector('.font-preview').style.fontFamily = wizard.getFontFamily(value);
            }
            wizard.validateCurrentStep();
            // If on review/generate step, update the preview iframe
            if (wizard.currentStep === 4) {
                wizard.generateCustomPreview();
            }
        };
        // Initial render
        render();
    }
}

// Color scheme data for preview generation
const colorSchemes = {
    blue: { primary: '#3B82F6', secondary: '#1E40AF', accent: '#60A5FA' },
    green: { primary: '#10B981', secondary: '#047857', accent: '#34D399' },
    purple: { primary: '#8B5CF6', secondary: '#6D28D9', accent: '#A78BFA' },
    orange: { primary: '#F97316', secondary: '#C2410C', accent: '#FB923C' },
    red: { primary: '#EF4444', secondary: '#B91C1C', accent: '#F87171' },
    dark: { primary: '#1F2937', secondary: '#111827', accent: '#374151' }
};

// Initialize wizard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.wizard = new WebsiteWizard();

    // Add some interactive enhancements

    // Add loading animation to buttons
    document.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', function (e) {
            if (!this.disabled && !this.classList.contains('loading')) {
                this.classList.add('loading');
                setTimeout(() => this.classList.remove('loading'), 300);
            }
        });
    });

    // Add smooth scrolling for step transitions
    const wizard = document.querySelector('.wizard');
    wizard.addEventListener('click', () => {
        wizard.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });

    // Add keyboard shortcuts info
    console.log('🍽️ Restaurant Website Generator loaded!');
    console.log('Keyboard shortcuts:');
    console.log('→ / Enter: Next step');
    console.log('← : Previous step');

    // Add easter egg
    let konamiCode = [];
    const konami = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65]; // ↑↑↓↓←→←→BA

    document.addEventListener('keydown', (e) => {
        konamiCode.push(e.keyCode);
        konamiCode = konamiCode.slice(-10);

        if (konamiCode.join(',') === konami.join(',')) {
            document.body.style.animation = 'rainbow 2s ease-in-out';
            setTimeout(() => {
                document.body.style.animation = '';
            }, 2000);
        }
    });

    // Add rainbow animation for easter egg
    const style = document.createElement('style');
    style.textContent = `
        @keyframes rainbow {
            0% { filter: hue-rotate(0deg); }
            100% { filter: hue-rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
});

// Export for potential external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebsiteWizard;
}