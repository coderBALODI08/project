/**
 * SURAKSHA Citizen Reports History & Tracking - reports.js
 */

const ReportsHistory = {
  reportsList: [],

  async init() {
    await this.loadReports();

    // Check if ?ref= is in URL to open detail modal immediately
    const urlParams = new URLSearchParams(window.location.search);
    const targetRef = urlParams.get('ref');
    if (targetRef) {
      this.openReportDetail(targetRef);
    }
  },

  async loadReports() {
    const listContainer = document.getElementById('reports-container');
    const emptyState = document.getElementById('reports-empty-state');
    if (!listContainer) return;

    try {
      if (Auth.isLoggedIn()) {
        this.reportsList = await ApiClient.incidents.myReports();
      } else {
        // For guest, show all public recent incidents as demonstration
        this.reportsList = await ApiClient.incidents.list({ limit: 10 });
      }

      if (!this.reportsList || this.reportsList.length === 0) {
        if (emptyState) emptyState.style.display = 'block';
        listContainer.style.display = 'none';
        return;
      }

      if (emptyState) emptyState.style.display = 'none';
      listContainer.style.display = 'block';
      this.renderReportsList(this.reportsList);
    } catch (err) {
      console.warn('[Reports] Error fetching reports:', err);
      listContainer.innerHTML = `<div class="card" style="text-align: center; color: var(--emergency-red);">Unable to load reports at this time. Please try again.</div>`;
    }
  },

  renderReportsList(reports) {
    const tbody = document.getElementById('reports-table-body');
    if (!tbody) return;

    tbody.innerHTML = reports.map(r => {
      const timeStr = App.timeAgo(r.created_at);
      const catColor = this.getCategoryColorClass(r.category);
      const statusClass = this.getStatusClass(r.status);

      return `
        <tr>
          <td><strong style="font-family: monospace; font-size: 13px; color: var(--navy-900);">${r.reference_id}</strong></td>
          <td>
            <span class="badge badge-${catColor}">${r.category}</span>
          </td>
          <td><strong>${r.title}</strong></td>
          <td style="color: var(--slate-500); font-size: 13px;">📍 ${r.address}</td>
          <td><span class="badge ${statusClass}">${r.status}</span></td>
          <td style="color: var(--slate-400); font-size: 12px;">${timeStr}</td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="ReportsHistory.openReportDetail('${r.reference_id}')">
              Track Status →
            </button>
          </td>
        </tr>
      `;
    }).join('');
  },

  getCategoryColorClass(category) {
    switch (category) {
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
  },

  async openReportDetail(referenceId) {
    try {
      const incident = await ApiClient.incidents.get(referenceId);
      if (!incident) return;

      document.getElementById('modal-report-ref').textContent = incident.reference_id;
      document.getElementById('modal-report-title').textContent = incident.title;
      document.getElementById('modal-report-category').textContent = incident.category;
      document.getElementById('modal-report-location').textContent = `📍 ${incident.address}`;
      document.getElementById('modal-report-desc').textContent = incident.description;

      // Status Badge
      const statusBadge = document.getElementById('modal-report-status');
      statusBadge.textContent = incident.status;
      statusBadge.className = `badge ${this.getStatusClass(incident.status)}`;

      // Render Closed-Loop Timeline
      const timelineContainer = document.getElementById('modal-report-timeline');
      if (timelineContainer && incident.status_history) {
        timelineContainer.innerHTML = incident.status_history.map((h, idx) => {
          const isLatest = idx === incident.status_history.length - 1;
          const dotClass = isLatest ? 'active' : 'completed';

          return `
            <div class="timeline-item ${dotClass}">
              <div class="timeline-dot">
                <div class="timeline-dot-inner"></div>
              </div>
              <div class="timeline-header">
                <div class="timeline-title">${h.status}</div>
                <div class="timeline-time">${App.timeAgo(h.timestamp)}</div>
              </div>
              ${h.comment ? `<div class="timeline-comment">${h.comment}</div>` : ''}
              ${h.changed_by_name ? `<div class="timeline-officer">🛡️ Logged by: ${h.changed_by_name}</div>` : ''}
            </div>
          `;
        }).join('');
      }

      // Render Photos if present
      const photosContainer = document.getElementById('modal-report-photos');
      if (photosContainer) {
        if (incident.evidence && incident.evidence.length > 0) {
          photosContainer.style.display = 'block';
          photosContainer.innerHTML = `
            <div style="font-size: 13px; font-weight: 700; color: var(--navy-900); margin-bottom: 8px;">Attached Evidence:</div>
            <div class="evidence-preview-grid">
              ${incident.evidence.map(e => `
                <div class="preview-item">
                  <a href="${e.file_path}" target="_blank" title="View Full Evidence">
                    <img src="${e.file_path}" alt="${e.file_name}" />
                  </a>
                </div>
              `).join('')}
            </div>
          `;
        } else {
          photosContainer.style.display = 'none';
        }
      }

      App.openModal('report-detail-modal');
    } catch (err) {
      App.showToast(`Unable to fetch report: ${err.message}`, 'error');
    }
  }
};

window.ReportsHistory = ReportsHistory;
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('reports-container')) {
    ReportsHistory.init();
  }
});
