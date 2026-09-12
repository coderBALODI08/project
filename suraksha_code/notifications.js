/**
 * SURAKSHA Notifications Feed Controller - notifications.js
 */

const NotificationsModule = {
  notifications: [],

  async init() {
    await this.loadNotifications();
    const markReadBtn = document.getElementById('btn-mark-all-read');
    if (markReadBtn) {
      markReadBtn.addEventListener('click', () => this.markAllRead());
    }
  },

  async loadNotifications() {
    try {
      this.notifications = await ApiClient.notifications.list();
      this.updateBadge();
      this.renderList();
    } catch (err) {
      console.warn('[Notifications] Could not fetch feed:', err);
    }
  },

  updateBadge() {
    const unreadCount = this.notifications.filter(n => !n.is_read).length;
    const badge = document.getElementById('notif-badge');
    if (badge) {
      if (unreadCount > 0) {
        badge.textContent = unreadCount > 9 ? '9+' : unreadCount;
        badge.style.display = 'flex';
      } else {
        badge.style.display = 'none';
      }
    }
  },

  renderList() {
    const list = document.getElementById('notif-drawer-list');
    if (!list) return;

    if (this.notifications.length === 0) {
      list.innerHTML = `
        <li style="padding: 24px; text-align: center; color: var(--slate-400); font-size: 13px;">
          No new alerts. Your area is quiet.
        </li>
      `;
      return;
    }

    list.innerHTML = this.notifications.map(n => {
      let icon = '🔔';
      if (n.type === 'sos_alert') icon = '🚨';
      if (n.type === 'incident_update') icon = '📋';

      return `
        <li class="notif-item ${!n.is_read ? 'unread' : ''}" onclick="NotificationsModule.handleNotifClick('${n.incident_reference_id || ''}')">
          <div style="display: flex; gap: 8px; align-items: flex-start;">
            <span>${icon}</span>
            <div style="flex: 1;">
              <div class="notif-item-title">${n.title}</div>
              <div class="notif-item-msg">${n.message}</div>
              <div class="notif-item-time">${App.timeAgo(n.created_at)}</div>
            </div>
          </div>
        </li>
      `;
    }).join('');
  },

  async markAllRead() {
    try {
      await ApiClient.notifications.markAllRead();
      this.notifications.forEach(n => n.is_read = true);
      this.updateBadge();
      this.renderList();
      App.showToast('All notifications marked as read.', 'success');
    } catch (err) {
      App.showToast('Could not mark read.', 'warning');
    }
  },

  handleNotifClick(refId) {
    if (refId) {
      if (refId.startsWith('SOS')) {
        if (window.location.pathname.includes('/authority/')) {
          window.location.href = '/authority/dashboard.html';
        } else {
          window.location.href = '/dashboard.html';
        }
      } else {
        window.location.href = `/reports.html?ref=${refId}`;
      }
    }
  }
};

window.NotificationsModule = NotificationsModule;
document.addEventListener('DOMContentLoaded', () => NotificationsModule.init());
