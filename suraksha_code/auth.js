/**
 * SURAKSHA Authentication & Session Management - auth.js
 */
const Auth = {
  isLoggedIn() {
    return !!ApiClient.getToken();
  },

  getUser() {
    return ApiClient.getUser();
  },

  isAuthority() {
    const user = this.getUser();
    return user && (user.role === 'authority' || user.role === 'admin' || user.role === 'police');
  },

  logout() {
    ApiClient.clearSession();
    window.location.href = '/login.html';
  },

  initNav() {
    const user = this.getUser();
    const navActions = document.getElementById('nav-user-actions');
    if (!navActions) return;

    if (user) {
      navActions.innerHTML = `
        <div class="user-menu-btn" id="user-profile-menu">
          <div class="user-avatar">${user.full_name ? user.full_name[0].toUpperCase() : 'U'}</div>
          <span style="font-size: 13px; font-weight: 600;">${user.full_name.split(' ')[0]}</span>
        </div>
        <button class="btn btn-secondary btn-sm" id="btn-logout" title="Log Out">Log Out</button>
      `;
      document.getElementById('btn-logout')?.addEventListener('click', () => this.logout());
      document.getElementById('user-profile-menu')?.addEventListener('click', () => {
        window.location.href = '/profile.html';
      });
    } else {
      navActions.innerHTML = `
        <a href="/login.html" class="btn btn-secondary btn-sm">Log In</a>
        <a href="/register.html" class="btn btn-primary btn-sm">Sign Up</a>
      `;
    }
  },

  async fillDemo(role = 'citizen') {
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    if (!emailInput || !passwordInput) return;

    if (role === 'citizen') {
      emailInput.value = 'citizen@suraksha.demo';
      passwordInput.value = 'Citizen@123';
    } else {
      emailInput.value = 'officer@suraksha.demo';
      passwordInput.value = 'Officer@123';
    }
  },

  requireAuth() {
    if (!this.isLoggedIn()) {
      window.location.href = `/login.html?redirect=${encodeURIComponent(window.location.pathname)}`;
    }
  },

  requireAuthority() {
    if (!this.isLoggedIn()) {
      window.location.href = `/authority/login.html?redirect=${encodeURIComponent(window.location.pathname)}`;
      return;
    }
    if (!this.isAuthority()) {
      alert('Access restricted to emergency response authorities.');
      window.location.href = '/dashboard.html';
    }
  }
};

window.Auth = Auth;
document.addEventListener('DOMContentLoaded', () => Auth.initNav());
