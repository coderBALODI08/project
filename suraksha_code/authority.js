/**
 * SURAKSHA Police & Authority Command Center - authority.js
 */

const AuthorityCenter = {
  incidentsList: [],
  officersList: [],
  selectedIncident: null,
  tacticalMap: null,
  tacticalMarkers: null,

  async initDashboard() {
    Auth.requireAuthority();
    await this.loadDashboardMetrics();
    await this.loadOfficers();
  },

  async initIncidentsPage() {
    Auth.requireAuthority();
    await this.loadOfficers();
    await this.loadIncidentsTable();
    this.initTableFilters();
  },

  async initTacticalMap() {
    Auth.requireAuthority();
    await this.loadOfficers();
    this.createTacticalMap();
  },

  async loadOfficers() {
    try {
      this.officersList = await ApiClient.authority.getOfficers();
      const selectEl = document.getElementById('assign-officer-select');
      if (selectEl) {
        selectEl.innerHTML = `
          <option value="">Select Responding Officer / Unit...</option>
          ${this.officersList.map(o => `
            <option value="${o.id}">${o.full_name} (${o.badge_number || 'Unit'} - ${o.department || 'Patrol'})</option>
          `).join('')}
        `;
      }
    } catch (err) {
      console.warn('[Authority] Could not load officers list:', err);
    }
  },

  async loadDashboardMetrics() {
    try {
      const data = await ApiClient.dashboard.authority();

      // Populate KPIs
      document.getElementById('metric-total').textContent = data.total_incidents_today;
      document.getElementById('metric-active').textContent = data.active_incidents;
      document.getElementById('metric-sos').textContent = data.sos_alerts_active;
      document.getElementById('metric-verify').textContent = data.pending_verification;
      document.getElementById('metric-critical').textContent = data.critical_incidents;
      document.getElementById('metric-resolved').textContent = data.resolved_incidents;

      // Active SOS Alert Banner
      const sosContainer = document.getElementById('active-sos-container');
      if (sosContainer) {
        const activeSOS = data.recent_sos_alerts.filter(s => s.status !== 'RESOLVED');
        if (activeSOS.length > 0) {
          const first = activeSOS[0];
          sosContainer.innerHTML = `
            <div class="sos-banner-alert">
              <div class="sos-banner-left">
                <div class="sos-banner-icon">🚨</div>
                <div>
                  <div class="sos-banner-title">CRITICAL EMERGENCY SOS ACTIVE: ${first.reference_id}</div>
                  <div class="sos-banner-desc">
                    Triggered by <strong>${first.user_name}</strong> (${first.user_phone}) at 📍 ${first.address}
                  </div>
                </div>
              </div>
              <div>
                <button class="btn btn-secondary btn-sm" onclick="AuthorityCenter.openSOSDispatchModal(${first.id}, '${first.reference_id}')">
                  Update Dispatch Status
                </button>
              </div>
            </div>
          `;
          sosContainer.style.display = 'block';
        } else {
          sosContainer.style.display = 'none';
        }
      }

      // Recent incidents table on dashboard
      const tbody = document.getElementById('dashboard-recent-table');
      if (tbody && data.recent_incidents) {
        tbody.innerHTML = data.recent_incidents.map(inc => `
          <tr>
            <td><strong style="font-family: monospace;">${inc.reference_id}</strong></td>
            <td><span class="badge badge-${this.getCatClass(inc.category)}">${inc.category}</span></td>
            <td><strong>${inc.title}</strong></td>
            <td>📍 ${inc.address}</td>
            <td><span class="badge ${this.getStatusClass(inc.status)}">${inc.status}</span></td>
            <td>${App.timeAgo(inc.created_at)}</td>
            <td>
              <button class="btn btn-secondary btn-sm" onclick="AuthorityCenter.openInspectModal('${inc.reference_id}')">
                Inspect
              </button>
            </td>
          </tr>
        `).join('');
      }
    } catch (err) {
      console.warn('[Authority] Error loading dashboard:', err);
    }
  },

  async loadIncidentsTable(params = {}) {
    const tbody = document.getElementById('incidents-table-body');
    if (!tbody) return;

    try {
      this.incidentsList = await ApiClient.incidents.list(params);
      if (this.incidentsList.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 24px; color: var(--slate-400);">No incidents match the selected filter criteria.</td></tr>`;
        return;
      }

      tbody.innerHTML = this.incidentsList.map(inc => `
        <tr>
          <td><strong style="font-family: monospace; color: var(--navy-900);">${inc.reference_id}</strong></td>
          <td><span class="badge badge-${this.getCatClass(inc.category)}">${inc.category}</span></td>
          <td>
            <span class="badge ${inc.severity === 'Critical' ? 'badge-critical' : 'badge-moderate'}">
              ${inc.severity}
            </span>
          </td>
          <td>📍 ${inc.address}</td>
          <td><span class="badge ${this.getStatusClass(inc.status)}">${inc.status}</span></td>
          <td>${inc.assigned_team || '<span style="color: #94A3B8;">Unassigned</span>'}</td>
          <td style="color: var(--slate-400); font-size: 12px;">${App.timeAgo(inc.created_at)}</td>
          <td>
            <div class="table-actions">
              <button class="btn btn-secondary btn-sm" onclick="AuthorityCenter.openInspectModal('${inc.reference_id}')" title="Inspect">
                View
              </button>
              <button class="btn btn-primary btn-sm" onclick="AuthorityCenter.openAssignModal(${inc.id}, '${inc.reference_id}')" title="Assign">
                Assign
              </button>
            </div>
          </td>
        </tr>
      `).join('');
    } catch (err) {
      App.showToast(`Error loading incidents: ${err.message}`, 'error');
    }
  },

  initTableFilters() {
    const searchInput = document.getElementById('table-search');
    const categoryFilter = document.getElementById('filter-category');
    const statusFilter = document.getElementById('filter-status');
    const severityFilter = document.getElementById('filter-severity');

    const triggerFilter = () => {
      this.loadIncidentsTable({
        search: searchInput ? searchInput.value.trim() : '',
        category: categoryFilter ? categoryFilter.value : '',
        status: statusFilter ? statusFilter.value : '',
        severity: severityFilter ? severityFilter.value : ''
      });
    };

    if (searchInput) searchInput.addEventListener('input', () => triggerFilter());
    if (categoryFilter) categoryFilter.addEventListener('change', () => triggerFilter());
    if (statusFilter) statusFilter.addEventListener('change', () => triggerFilter());
    if (severityFilter) severityFilter.addEventListener('change', () => triggerFilter());
  },

  async openInspectModal(refId) {
    try {
      const inc = await ApiClient.incidents.get(refId);
      this.selectedIncident = inc;

      document.getElementById('inspect-ref').textContent = inc.reference_id;
      document.getElementById('inspect-title').textContent = inc.title;
      document.getElementById('inspect-category').textContent = inc.category;
      document.getElementById('inspect-severity').textContent = inc.severity;
      document.getElementById('inspect-location').textContent = `📍 ${inc.address} (GPS: ${inc.latitude}, ${inc.longitude})`;
      document.getElementById('inspect-desc').textContent = inc.description;
      document.getElementById('inspect-reporter').textContent = inc.reporter_name ? `${inc.reporter_name} (${inc.reporter_contact || 'No phone'})` : 'Anonymous Citizen';
      document.getElementById('inspect-status').textContent = inc.status;
      document.getElementById('inspect-verify-status').textContent = inc.verification_status;
      document.getElementById('inspect-assigned').textContent = inc.assigned_team || 'None';

      // Internal notes if any
      const notesEl = document.getElementById('inspect-notes');
      if (notesEl) {
        notesEl.textContent = inc.internal_notes || 'No internal officer notes entered yet.';
      }

      // Evidence photos
      const evidenceContainer = document.getElementById('inspect-evidence');
      if (evidenceContainer) {
        if (inc.evidence && inc.evidence.length > 0) {
          evidenceContainer.innerHTML = inc.evidence.map(e => `
            <div class="preview-item">
              <a href="${e.file_path}" target="_blank">
                <img src="${e.file_path}" alt="Evidence" />
              </a>
            </div>
          `).join('');
          evidenceContainer.style.display = 'grid';
        } else {
          evidenceContainer.innerHTML = '<span style="font-size: 13px; color: var(--slate-400);">No photo evidence attached with this report.</span>';
          evidenceContainer.style.display = 'block';
        }
      }

      // Action buttons
      document.getElementById('btn-action-verify').onclick = () => this.quickVerify(inc.id);
      document.getElementById('btn-action-reject').onclick = () => this.quickReject(inc.id);
      document.getElementById('btn-action-resolve').onclick = () => this.markResolved(inc.id);
      document.getElementById('btn-action-assign').onclick = () => {
        App.closeModal('inspect-modal');
        this.openAssignModal(inc.id, inc.reference_id);
      };

      App.openModal('inspect-modal');
    } catch (err) {
      App.showToast(`Could not inspect incident: ${err.message}`, 'error');
    }
  },

  async quickVerify(incidentId) {
    const reason = prompt('Add verification note (optional):', 'Verified on ground by beat patrol.');
    if (reason === null) return;

    try {
      await ApiClient.authority.verify(incidentId, reason);
      App.showToast('Incident marked as VERIFIED.', 'success');
      App.closeModal('inspect-modal');
      this.refreshCurrentView();
    } catch (err) {
      App.showToast(`Error verifying incident: ${err.message}`, 'error');
    }
  },

  async quickReject(incidentId) {
    const reason = prompt('Reason for rejection / flagging as inaccurate:', 'Duplicate report or unverified location.');
    if (reason === null) return;

    try {
      await ApiClient.authority.reject(incidentId, reason);
      App.showToast('Incident report REJECTED.', 'info');
      App.closeModal('inspect-modal');
      this.refreshCurrentView();
    } catch (err) {
      App.showToast(`Error rejecting report: ${err.message}`, 'error');
    }
  },

  async markResolved(incidentId) {
    const note = prompt('Enter resolution note:', 'Situation under control. Area secured by response team.');
    if (note === null) return;

    try {
      await ApiClient.incidents.updateStatus(incidentId, {
        status: 'Resolved',
        verification_status: 'Verified',
        comment: note
      });
      App.showToast('Incident marked as RESOLVED.', 'success');
      App.closeModal('inspect-modal');
      this.refreshCurrentView();
    } catch (err) {
      App.showToast(`Error resolving incident: ${err.message}`, 'error');
    }
  },

  openAssignModal(incidentId, refId) {
    document.getElementById('assign-modal-ref').textContent = refId;
    document.getElementById('btn-confirm-assign').onclick = () => this.confirmAssignment(incidentId);
    App.openModal('assign-modal');
  },

  async confirmAssignment(incidentId) {
    const officerSelect = document.getElementById('assign-officer-select');
    const teamInput = document.getElementById('assign-team-input');
    const noteInput = document.getElementById('assign-note-input');

    const officerId = officerSelect ? officerSelect.value : null;
    const teamName = teamInput ? teamInput.value.trim() : '';
    const note = noteInput ? noteInput.value.trim() : '';

    if (!officerId && !teamName) {
      App.showToast('Please select an officer or enter a responding unit.', 'warning');
      return;
    }

    try {
      await ApiClient.incidents.assign(incidentId, {
        assigned_to_id: officerId ? parseInt(officerId, 10) : null,
        assigned_team: teamName || (officerSelect.options[officerSelect.selectedIndex].text),
        note: note || 'Dispatched for active field response.'
      });

      App.showToast('Response team successfully assigned!', 'success');
      App.closeModal('assign-modal');
      this.refreshCurrentView();
    } catch (err) {
      App.showToast(`Error assigning incident: ${err.message}`, 'error');
    }
  },

  openSOSDispatchModal(sosId, refId) {
    const unit = prompt(`Update dispatch unit for ${refId}:`, 'PCR Patrol Van 07');
    if (unit === null) return;

    ApiClient.sos.updateStatus(sosId, {
      status: 'RESPONSE_INITIATED',
      dispatched_unit: unit,
      notes: 'Dispatched from command center.'
    }).then(() => {
      App.showToast(`SOS dispatch updated for ${refId}`, 'success');
      this.loadDashboardMetrics();
    }).catch(err => {
      App.showToast(`Error: ${err.message}`, 'error');
    });
  },

  createTacticalMap() {
    const mapEl = document.getElementById('tactical-leaflet-map');
    if (!mapEl) return;

    this.tacticalMap = L.map('tactical-leaflet-map').setView([28.9845, 77.7064], 14);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19
    }).addTo(this.tacticalMap);

    this.tacticalMarkers = L.layerGroup().addTo(this.tacticalMap);
    this.loadTacticalMapData();
  },

  async loadTacticalMapData() {
    try {
      const incidents = await ApiClient.map.getIncidents();
      this.tacticalMarkers.clearLayers();

      incidents.forEach(inc => {
        const iconSymbol = MapController.getCategoryIcon(inc.icon);
        const pin = L.divIcon({
          className: 'custom-pin-wrapper',
          html: `
            <div class="custom-pin" style="background-color: ${inc.color}; width: 36px; height: 36px;" title="${inc.reference_id}">
              <span>${iconSymbol}</span>
            </div>
          `,
          iconSize: [36, 36],
          iconAnchor: [18, 18]
        });

        const marker = L.marker([inc.latitude, inc.longitude], { icon: pin });
        marker.on('click', () => {
          this.loadTacticalSidebar(inc);
        });

        this.tacticalMarkers.addLayer(marker);
      });

      // Also render active SOS alerts with pulsing beacons
      const sosList = await ApiClient.sos.list(true);
      sosList.forEach(sos => {
        const sosPin = L.divIcon({
          className: 'sos-pin-wrapper',
          html: `
            <div class="sos-beacon" style="width: 38px; height: 38px; font-size: 18px; margin: 0; box-shadow: 0 0 0 4px rgba(220, 38, 38, 0.4);">
              🚨
            </div>
          `,
          iconAnchor: [19, 19]
        });

        const sosMarker = L.marker([sos.latitude, sos.longitude], { icon: sosPin });
        sosMarker.bindPopup(`
          <div style="font-size: 13px;">
            <strong style="color: #DC2626;">EMERGENCY SOS: ${sos.reference_id}</strong><br>
            Citizen: ${sos.user_name} (${sos.user_phone})<br>
            Status: ${sos.status}<br>
            Unit: ${sos.dispatched_unit || 'None'}
          </div>
        `);
        this.tacticalMarkers.addLayer(sosMarker);
      });
    } catch (err) {
      console.warn('[TacticalMap] Error loading telemetry:', err);
    }
  },

  loadTacticalSidebar(inc) {
    const sidebar = document.getElementById('tactical-sidebar-content');
    if (!sidebar) return;

    sidebar.innerHTML = `
      <div style="margin-bottom: 14px;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
          <span style="font-family: monospace; font-weight: 700; color: var(--navy-900);">${inc.reference_id}</span>
          <span class="badge ${this.getStatusClass(inc.status)}">${inc.status}</span>
        </div>
        <h4 style="margin: 8px 0 4px; font-size: 16px;">${inc.title}</h4>
        <div style="font-size: 12px; color: var(--slate-500); margin-bottom: 12px;">📍 ${inc.address}</div>
        <p style="font-size: 13px; color: var(--navy-700); line-height: 1.4; margin-bottom: 16px;">
          ${inc.description}
        </p>
      </div>

      <div style="display: flex; flex-direction: column; gap: 8px;">
        <button class="btn btn-primary btn-sm" onclick="AuthorityCenter.openInspectModal('${inc.reference_id}')">
          Full Inspection & Notes
        </button>
        <button class="btn btn-secondary btn-sm" onclick="AuthorityCenter.openAssignModal(${inc.id}, '${inc.reference_id}')">
          Assign Unit
        </button>
        <button class="btn btn-success btn-sm" onclick="AuthorityCenter.markResolved(${inc.id})">
          Mark Incident Resolved
        </button>
      </div>
    `;
  },

  refreshCurrentView() {
    if (document.getElementById('metric-total')) {
      this.loadDashboardMetrics();
    }
    if (document.getElementById('incidents-table-body')) {
      this.loadIncidentsTable();
    }
    if (this.tacticalMap) {
      this.loadTacticalMapData();
    }
  },

  getCatClass(cat) {
    switch (cat) {
      case 'Fire': return 'fire';
      case 'Road Accident': return 'accident';
      case 'Suspicious Activity': return 'suspicious';
      case 'Medical Emergency': return 'medical';
      case 'Missing Person': return 'missing';
      default: return 'critical';
    }
  },

  getStatusClass(status) {
    switch (status) {
      case 'Submitted': return 'status-submitted';
      case 'Received': return 'status-received';
      case 'Under Verification': return 'status-verification';
      case 'Authority Assigned': return 'status-assigned';
      case 'Action Taken': return 'status-action';
      case 'Resolved': return 'status-resolved';
      case 'Rejected': return 'status-rejected';
      default: return 'status-submitted';
    }
  }
};

window.AuthorityCenter = AuthorityCenter;
