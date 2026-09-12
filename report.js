/**
 * SURAKSHA 5-Step Incident Reporting Wizard - report.js
 */

const ReportWizard = {
  currentStep: 1,
  totalSteps: 5,
  miniMap: null,
  pickerMarker: null,
  
  formData: {
    category: '',
    latitude: 28.9845,
    longitude: 77.7064,
    address: '',
    landmark: '',
    title: '',
    severity: 'Moderate',
    description: '',
    people_affected: 0,
    reporter_name: '',
    reporter_contact: '',
    evidenceFiles: []
  },

  init() {
    this.initStepNavigation();
    this.initCategorySelection();
    this.initMiniMap();
    this.initEvidenceUpload();
    this.initPrefillFromUser();
  },

  initPrefillFromUser() {
    const user = ApiClient.getUser();
    if (user) {
      this.formData.reporter_name = user.full_name;
      this.formData.reporter_contact = user.phone || '';
      const nameInput = document.getElementById('reporter_name');
      const phoneInput = document.getElementById('reporter_contact');
      if (nameInput) nameInput.value = user.full_name;
      if (phoneInput && user.phone) phoneInput.value = user.phone;
    }
  },

  initStepNavigation() {
    document.querySelectorAll('.btn-wizard-next').forEach(btn => {
      btn.addEventListener('click', () => this.nextStep());
    });
    document.querySelectorAll('.btn-wizard-prev').forEach(btn => {
      btn.addEventListener('click', () => this.prevStep());
    });
  },

  initCategorySelection() {
    document.querySelectorAll('.category-card').forEach(card => {
      card.addEventListener('click', () => {
        document.querySelectorAll('.category-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        this.formData.category = card.getAttribute('data-category');
        
        // Auto set default title if empty
        const titleInput = document.getElementById('title');
        if (titleInput && (!titleInput.value || titleInput.dataset.autofilled)) {
          titleInput.value = `${this.formData.category} Incident`;
          titleInput.dataset.autofilled = 'true';
        }
      });
    });
  },

  initMiniMap() {
    const miniMapEl = document.getElementById('mini-picker-map');
    if (!miniMapEl) return;

    // Center on Meerut City Center
    this.miniMap = L.map('mini-picker-map').setView([28.9845, 77.7064], 14);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 18
    }).addTo(this.miniMap);

    const pinIcon = L.divIcon({
      className: 'picker-pin',
      html: '<div style="font-size: 28px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.4));">📍</div>',
      iconAnchor: [14, 28]
    });

    this.pickerMarker = L.marker([28.9845, 77.7064], { draggable: true, icon: pinIcon }).addTo(this.miniMap);

    this.pickerMarker.on('dragend', (e) => {
      const pos = e.target.getLatLng();
      this.setCoordinates(pos.lat, pos.lng);
    });

    this.miniMap.on('click', (e) => {
      this.pickerMarker.setLatLng(e.latlng);
      this.setCoordinates(e.latlng.lat, e.latlng.lng);
    });

    const gpsBtn = document.getElementById('btn-use-gps');
    if (gpsBtn) {
      gpsBtn.addEventListener('click', () => {
        if (!navigator.geolocation) {
          App.showToast('Geolocation is not supported by your browser.', 'warning');
          return;
        }
        App.showToast('Detecting your GPS location...', 'info');
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;
            this.pickerMarker.setLatLng([lat, lng]);
            this.miniMap.flyTo([lat, lng], 16);
            this.setCoordinates(lat, lng, 'Current Device Location');
            App.showToast('Incident location set from device GPS.', 'success');
          },
          () => {
            App.showToast('Could not fetch GPS. Please click on the map to set location.', 'warning');
          },
          { timeout: 5000 }
        );
      });
    }
  },

  setCoordinates(lat, lng, customAddress = '') {
    this.formData.latitude = parseFloat(lat.toFixed(6));
    this.formData.longitude = parseFloat(lng.toFixed(6));
    
    const coordDisplay = document.getElementById('coordinates-display');
    if (coordDisplay) {
      coordDisplay.textContent = `Selected: ${this.formData.latitude}, ${this.formData.longitude}`;
    }

    const addrInput = document.getElementById('address');
    if (addrInput && customAddress) {
      addrInput.value = customAddress;
      this.formData.address = customAddress;
    }
  },

  initEvidenceUpload() {
    const fileInput = document.getElementById('evidence-file-input');
    const dropzone = document.getElementById('evidence-dropzone');
    if (!fileInput || !dropzone) return;

    dropzone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
      const files = Array.from(e.target.files);
      files.forEach(file => {
        if (file.size > 5 * 1024 * 1024) {
          App.showToast(`File ${file.name} exceeds 5MB limit.`, 'error');
          return;
        }
        this.formData.evidenceFiles.push(file);
      });
      this.renderEvidencePreviews();
    });
  },

  renderEvidencePreviews() {
    const previewContainer = document.getElementById('evidence-preview-grid');
    if (!previewContainer) return;

    previewContainer.innerHTML = '';
    this.formData.evidenceFiles.forEach((file, index) => {
      const item = document.createElement('div');
      item.className = 'preview-item';
      
      const img = document.createElement('img');
      img.src = URL.createObjectURL(file);
      item.appendChild(img);

      const removeBtn = document.createElement('button');
      removeBtn.className = 'btn-remove';
      removeBtn.innerHTML = '✕';
      removeBtn.onclick = (e) => {
        e.stopPropagation();
        this.formData.evidenceFiles.splice(index, 1);
        this.renderEvidencePreviews();
      };
      item.appendChild(removeBtn);

      previewContainer.appendChild(item);
    });
  },

  validateStep(step) {
    if (step === 1) {
      if (!this.formData.category) {
        App.showToast('Please select an incident category to continue.', 'warning');
        return false;
      }
      return true;
    }

    if (step === 2) {
      const addrInput = document.getElementById('address');
      const landmarkInput = document.getElementById('landmark');
      if (!addrInput || !addrInput.value.trim()) {
        App.showToast('Please enter an approximate address or landmark.', 'warning');
        return false;
      }
      this.formData.address = addrInput.value.trim();
      this.formData.landmark = landmarkInput ? landmarkInput.value.trim() : '';
      return true;
    }

    if (step === 3) {
      const titleInput = document.getElementById('title');
      const descInput = document.getElementById('description');
      const severityInput = document.getElementById('severity');
      const peopleInput = document.getElementById('people_affected');

      if (!titleInput || !titleInput.value.trim()) {
        App.showToast('Please provide a short title for the report.', 'warning');
        return false;
      }
      if (!descInput || !descInput.value.trim() || descInput.value.trim().length < 10) {
        App.showToast('Please describe what happened (at least 10 characters).', 'warning');
        return false;
      }

      this.formData.title = titleInput.value.trim();
      this.formData.description = descInput.value.trim();
      this.formData.severity = severityInput ? severityInput.value : 'Moderate';
      this.formData.people_affected = peopleInput ? parseInt(peopleInput.value, 10) || 0 : 0;
      return true;
    }

    return true;
  },

  goToStep(step) {
    if (step < 1 || step > this.totalSteps) return;

    // Update Steps Progress Indicators
    document.querySelectorAll('.step-item').forEach((item, idx) => {
      const stepNum = idx + 1;
      item.classList.remove('active', 'completed');
      if (stepNum === step) {
        item.classList.add('active');
      } else if (stepNum < step) {
        item.classList.add('completed');
      }
    });

    // Update Step Panes
    document.querySelectorAll('.wizard-pane').forEach((pane, idx) => {
      pane.classList.remove('active');
      if (idx + 1 === step) {
        pane.classList.add('active');
      }
    });

    this.currentStep = step;

    // If entering step 2, trigger map size update
    if (step === 2 && this.miniMap) {
      setTimeout(() => this.miniMap.invalidateSize(), 200);
    }

    // If entering review step, populate summary
    if (step === 5) {
      this.populateReviewSummary();
    }
  },

  nextStep() {
    if (this.validateStep(this.currentStep)) {
      this.goToStep(this.currentStep + 1);
    }
  },

  prevStep() {
    this.goToStep(this.currentStep - 1);
  },

  populateReviewSummary() {
    document.getElementById('review-category').textContent = this.formData.category;
    document.getElementById('review-title').textContent = this.formData.title;
    document.getElementById('review-severity').textContent = this.formData.severity;
    document.getElementById('review-location').textContent = `${this.formData.address} (${this.formData.latitude}, ${this.formData.longitude})`;
    document.getElementById('review-description').textContent = this.formData.description;
    document.getElementById('review-photos-count').textContent = `${this.formData.evidenceFiles.length} photo(s) attached`;
  },

  async submitReport() {
    const submitBtn = document.getElementById('btn-submit-report');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = 'Submitting Report...';
    }

    try {
      const payload = {
        title: this.formData.title,
        category: this.formData.category,
        severity: this.formData.severity,
        description: this.formData.description,
        latitude: this.formData.latitude,
        longitude: this.formData.longitude,
        address: this.formData.address,
        landmark: this.formData.landmark,
        people_affected: this.formData.people_affected,
        reporter_name: this.formData.reporter_name || 'Anonymous Citizen',
        reporter_contact: this.formData.reporter_contact || ''
      };

      const createdIncident = await ApiClient.incidents.create(payload);

      // Upload evidence files if any
      if (this.formData.evidenceFiles.length > 0) {
        for (const file of this.formData.evidenceFiles) {
          const fd = new FormData();
          fd.append('file', file);
          try {
            await ApiClient.incidents.uploadEvidence(createdIncident.id, fd);
          } catch (uploadErr) {
            console.warn('[Evidence] Upload failed for a file:', uploadErr);
          }
        }
      }

      // Render submission success view
      document.getElementById('wizard-form-container').style.display = 'none';
      const successView = document.getElementById('wizard-success-view');
      successView.style.display = 'block';

      document.getElementById('success-reference-id').textContent = createdIncident.reference_id;
      document.getElementById('btn-track-submitted-report').href = `/reports.html?ref=${createdIncident.reference_id}`;

      App.showToast(`Report ${createdIncident.reference_id} submitted successfully!`, 'success');
    } catch (err) {
      App.showToast(`Error submitting report: ${err.message}`, 'error');
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Submit Incident Report';
      }
    }
  }
};

window.ReportWizard = ReportWizard;
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('wizard-form-container')) {
    ReportWizard.init();
  }
});
