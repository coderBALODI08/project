/**
 * SURAKSHA Global UI Controller - app.js
 */
const App = {
  init() {
    this.initToasts();
    this.initSOSButtons();
    this.initNotificationsDrawer();
    this.initModalListeners();
  },

  initToasts() {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      document.body.appendChild(container);
    }
  },

  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '⚠️';
    if (type === 'warning') icon = '🔔';

    toast.innerHTML = `
      <span>${icon}</span>
      <div style="flex: 1;">${message}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  },

  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
    }
  },

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('active');
    }
  },

  initModalListeners() {
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('active');
      }
      if (e.target.classList.contains('modal-close') || e.target.closest('.modal-close')) {
        const overlay = e.target.closest('.modal-overlay');
        if (overlay) overlay.classList.remove('active');
      }
    });
  },

  initSOSButtons() {
    document.querySelectorAll('.btn-sos-trigger, #header-sos-btn, #mobile-sos-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        this.openSOSModal();
      });
    });
  },

  openSOSModal() {
    // If dedicated SOS module is loaded, invoke its start modal
    if (window.SOSModule) {
      window.SOSModule.openEmergencyDialog();
    } else {
      window.location.href = '/dashboard.html?action=sos';
    }
  },

  initNotificationsDrawer() {
    const notifBtn = document.getElementById('nav-notif-btn');
    const drawer = document.getElementById('notif-drawer');
    if (!notifBtn || !drawer) return;

    notifBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      drawer.classList.toggle('active');
      if (drawer.classList.contains('active') && window.NotificationsModule) {
        window.NotificationsModule.loadNotifications();
      }
    });

    document.addEventListener('click', (e) => {
      if (!drawer.contains(e.target) && !notifBtn.contains(e.target)) {
        drawer.classList.remove('active');
      }
    });
  },

  timeAgo(isoString) {
    if (!isoString) return 'Just now';
    const now = new Date();
    const past = new Date(isoString);
    const diffSec = Math.floor((now - past) / 1000);

    if (diffSec < 60) return 'Just now';
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin}m ago`;
    const diffHours = Math.floor(diffMin / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  }
};

window.App = App;
document.addEventListener('DOMContentLoaded', () => App.init());
