/**
 * SURAKSHA SOS Emergency Response Experience - sos.js
 */
const SOSModule = {
  activeSOS: null,

  init() {
    this.createSOSModalMarkup();
    
    // Check if URL has ?action=sos
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('action') === 'sos') {
      setTimeout(() => this.openEmergencyDialog(), 300);
    }
  },

  createSOSModalMarkup() {
    if (document.getElementById('sos-modal-overlay')) return;

    const modalHTML = `
      <div class="modal-overlay" id="sos-modal-overlay">
        <div class="modal-card" style="max-width: 500px;">
          <div class="modal-header" style="background-color: var(--emergency-red); color: white;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <span style="font-size: 22px;">🚨</span>
              <h3 class="modal-title" style="color: white;">Emergency SOS Trigger</h3>
            </div>
            <button class="modal-close" style="color: white;" onclick="SOSModule.closeModal()">✕</button>
          </div>
          
          <div class="modal-body" id="sos-modal-content">
            <!-- Step 1: Confirmation -->
            <div id="sos-confirm-view">
              <div style="text-align: center; padding: 16px 0;">
                <div class="sos-beacon">🚨</div>
                <h4 style="font-size: 18px; margin-bottom: 8px;">Send Emergency Alert with Your Location?</h4>
                <p style="font-size: 14px; margin-bottom: 20px;">
                  This will broadcast an immediate high-priority alert to the SURAKSHA Command Center along with your current GPS coordinates.
                </p>
                <div style="background-color: var(--emergency-red-light); border: 1px solid var(--emergency-red-border); border-radius: 8px; padding: 12px; margin-bottom: 20px; text-align: left; font-size: 12px; color: var(--emergency-red);">
                  <strong>Official Safety Notice:</strong> For immediate life-threatening emergencies, please dial <strong>112</strong> or <strong>100</strong> immediately.
                </div>
                <div style="display: flex; gap: 12px; justify-content: center;">
                  <button class="btn btn-secondary" onclick="SOSModule.closeModal()">Cancel</button>
                  <button class="btn btn-emergency btn-lg" id="btn-confirm-sos" onclick="SOSModule.triggerSOS()">
                    <span>Send Emergency SOS</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Step 2: Active Alert View -->
            <div id="sos-active-view" style="display: none;">
              <div class="sos-pulse-card">
                <div class="sos-beacon">🚨</div>
                <div style="font-size: 12px; font-weight: 800; letter-spacing: 1px; color: var(--emergency-red); text-transform: uppercase;">SOS Alert Active</div>
                <h3 id="sos-active-ref" style="font-size: 22px; margin: 4px 0 12px;">SOS-2026-000000</h3>
                <p style="font-size: 13px; color: var(--navy-700); line-height: 1.4;">
                  Your emergency alert has been broadcast to central response units. Help is coordinating near your location.
                </p>
              </div>

              <!-- Status progression -->
              <div style="background-color: var(--slate-50); border: 1px solid var(--slate-200); border-radius: 10px; padding: 16px; margin-bottom: 20px;">
                <div style="font-size: 12px; font-weight: 700; color: var(--navy-800); text-transform: uppercase; margin-bottom: 12px;">
                  Dispatch Status
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; font-size: 12px; position: relative;">
                  <div style="text-align: center; flex: 1;">
                    <div style="width: 28px; height: 28px; border-radius: 50%; background-color: var(--safe-green); color: white; display: flex; align-items: center; justify-content: center; margin: 0 auto 4px; font-weight: bold;">✓</div>
                    <span style="font-weight: 600; color: var(--safe-green);">Alert Sent</span>
                  </div>
                  <div style="height: 2px; background-color: var(--safe-green); flex: 1; margin-bottom: 18px;"></div>
                  <div style="text-align: center; flex: 1;">
                    <div style="width: 28px; height: 28px; border-radius: 50%; background-color: var(--safe-green); color: white; display: flex; align-items: center; justify-content: center; margin: 0 auto 4px; font-weight: bold;">✓</div>
                    <span style="font-weight: 600; color: var(--safe-green);">Received</span>
                  </div>
                  <div style="height: 2px; background-color: var(--emergency-red); flex: 1; margin-bottom: 18px;"></div>
                  <div style="text-align: center; flex: 1;">
                    <div style="width: 28px; height: 28px; border-radius: 50%; background-color: var(--emergency-red); color: white; display: flex; align-items: center; justify-content: center; margin: 0 auto 4px; font-weight: bold; animation: beaconWave 1.5s infinite;">•</div>
                    <span style="font-weight: 700; color: var(--emergency-red);">Responding</span>
                  </div>
                </div>
              </div>

              <!-- Fast Dial Helplines -->
              <div style="margin-top: 16px;">
                <div style="font-size: 13px; font-weight: 700; color: var(--navy-900); margin-bottom: 8px;">
                  Direct Emergency Hotlines:
                </div>
                <div class="helpline-grid" id="sos-helpline-container">
                  <a href="tel:112" class="helpline-card">
                    <div class="helpline-number">112</div>
                    <div class="helpline-name">National Emergency</div>
                  </a>
                  <a href="tel:100" class="helpline-card">
                    <div class="helpline-number">100</div>
                    <div class="helpline-name">Police Control</div>
                  </a>
                  <a href="tel:108" class="helpline-card">
                    <div class="helpline-number">108</div>
                    <div class="helpline-name">Ambulance</div>
                  </a>
                  <a href="tel:101" class="helpline-card">
                    <div class="helpline-number">101</div>
                    <div class="helpline-name">Fire Rescue</div>
                  </a>
                </div>
              </div>

              <div style="text-align: center; margin-top: 24px;">
                <button class="btn btn-secondary" onclick="SOSModule.closeModal()">Keep Running in Background</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);
  },

  openEmergencyDialog() {
    this.createSOSModalMarkup();
    document.getElementById('sos-confirm-view').style.display = 'block';
    document.getElementById('sos-active-view').style.display = 'none';
    document.getElementById('sos-modal-overlay').classList.add('active');
  },

  closeModal() {
    const overlay = document.getElementById('sos-modal-overlay');
    if (overlay) overlay.classList.remove('active');
  },

  async triggerSOS() {
    const btn = document.getElementById('btn-confirm-sos');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = 'Capturing Location...';
    }

    let lat = 28.9845;
    let lng = 77.7064;
    let address = 'Meerut Monitored Sector';

    if (navigator.geolocation) {
      try {
        const position = await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 4000 });
        });
        lat = position.coords.latitude;
        lng = position.coords.longitude;
        address = `GPS Coordinates (${lat.toFixed(4)}, ${lng.toFixed(4)})`;
      } catch (err) {
        console.log('[SOS] Geolocation permission or timeout, using regional default:', err.message);
      }
    }

    const user = ApiClient.getUser();
    const sosPayload = {
      latitude: lat,
      longitude: lng,
      address: address,
      user_name: user ? user.full_name : 'Citizen in Immediate Need',
      user_phone: user ? user.phone : 'Not Provided',
      notes: 'High-priority SOS trigger via citizen interface.'
    };

    try {
      const result = await ApiClient.sos.trigger(sosPayload);
      this.activeSOS = result;

      document.getElementById('sos-confirm-view').style.display = 'none';
      const activeView = document.getElementById('sos-active-view');
      activeView.style.display = 'block';
      document.getElementById('sos-active-ref').textContent = result.reference_id;

      App.showToast(`Emergency alert ${result.reference_id} sent to response center.`, 'error');
    } catch (err) {
      alert(`Could not send SOS: ${err.message}`);
      this.closeModal();
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = 'Send Emergency SOS';
      }
    }
  }
};

window.SOSModule = SOSModule;
document.addEventListener('DOMContentLoaded', () => SOSModule.init());
