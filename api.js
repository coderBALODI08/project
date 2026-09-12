/**
 * SURAKSHA Unified API Client - api.js
 */
const API_BASE = '/api';

class ApiClient {
  static getToken() {
    return localStorage.getItem('suraksha_token');
  }

  static setToken(token) {
    localStorage.setItem('suraksha_token', token);
  }

  static clearSession() {
    localStorage.removeItem('suraksha_token');
    localStorage.removeItem('suraksha_user');
  }

  static getUser() {
    try {
      const userStr = localStorage.getItem('suraksha_user');
      return userStr ? JSON.parse(userStr) : null;
    } catch {
      return null;
    }
  }

  static setUser(user) {
    localStorage.setItem('suraksha_user', JSON.stringify(user));
  }

  static async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const token = this.getToken();

    const headers = {
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (response.status === 401) {
        // Unauthorized
        this.clearSession();
        if (window.location.pathname.includes('/authority/')) {
          window.location.href = '/authority/login.html';
        }
      }

      if (!response.ok) {
        let errorDetail = 'Something went wrong. Please try again.';
        try {
          const errData = await response.json();
          if (errData && errData.detail) {
            errorDetail = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
          }
        } catch {
          // ignore
        }
        throw new Error(errorDetail);
      }

      return await response.json();
    } catch (error) {
      console.warn(`[API] Error on ${endpoint}:`, error.message);
      throw error;
    }
  }

  // Auth APIs
  static auth = {
    login: (email, password) => ApiClient.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    }),
    register: (userData) => ApiClient.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    }),
    getMe: () => ApiClient.request('/auth/me'),
    getDemoUsers: () => ApiClient.request('/auth/demo-users')
  };

  // Incident APIs
  static incidents = {
    list: (params = {}) => {
      const query = new URLSearchParams();
      if (params.category) query.append('category', params.category);
      if (params.severity) query.append('severity', params.severity);
      if (params.status) query.append('status', params.status);
      if (params.verification_status) query.append('verification_status', params.verification_status);
      if (params.search) query.append('search', params.search);
      const qStr = query.toString();
      return ApiClient.request(`/incidents${qStr ? `?${qStr}` : ''}`);
    },
    myReports: () => ApiClient.request('/incidents/my-reports'),
    get: (idOrRef) => ApiClient.request(`/incidents/${idOrRef}`),
    create: (incidentData) => ApiClient.request('/incidents', {
      method: 'POST',
      body: JSON.stringify(incidentData)
    }),
    uploadEvidence: (incidentId, formData) => ApiClient.request(`/incidents/${incidentId}/evidence`, {
      method: 'POST',
      body: formData
    }),
    updateStatus: (incidentId, statusData) => ApiClient.request(`/incidents/${incidentId}/status`, {
      method: 'PUT',
      body: JSON.stringify(statusData)
    }),
    assign: (incidentId, assignData) => ApiClient.request(`/incidents/${incidentId}/assign`, {
      method: 'PUT',
      body: JSON.stringify(assignData)
    })
  };

  // SOS APIs
  static sos = {
    trigger: (sosData) => ApiClient.request('/sos', {
      method: 'POST',
      body: JSON.stringify(sosData)
    }),
    list: (activeOnly = false) => ApiClient.request(`/sos?active_only=${activeOnly}`),
    get: (idOrRef) => ApiClient.request(`/sos/${idOrRef}`),
    updateStatus: (id, updateData) => ApiClient.request(`/sos/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify(updateData)
    }),
    helplines: () => ApiClient.request('/sos/helplines')
  };

  // Map APIs
  static map = {
    getIncidents: (params = {}) => {
      const query = new URLSearchParams(params);
      const qStr = query.toString();
      return ApiClient.request(`/map/incidents${qStr ? `?${qStr}` : ''}`);
    },
    getZones: () => ApiClient.request('/map/zones'),
    getResources: () => ApiClient.request('/map/resources')
  };

  // Notifications
  static notifications = {
    list: () => ApiClient.request('/notifications'),
    markAllRead: () => ApiClient.request('/notifications/read-all', { method: 'POST' })
  };

  // Dashboards
  static dashboard = {
    citizen: () => ApiClient.request('/dashboard/citizen'),
    authority: () => ApiClient.request('/dashboard/authority')
  };

  // Authority Operations
  static authority = {
    getOfficers: () => ApiClient.request('/authority/officers'),
    getAuditLogs: (limit = 50) => ApiClient.request(`/authority/audit-logs?limit=${limit}`),
    verify: (incidentId, reason = '') => ApiClient.request(`/authority/verify/${incidentId}`, {
      method: 'POST',
      body: JSON.stringify({ reason })
    }),
    reject: (incidentId, reason = '') => ApiClient.request(`/authority/reject/${incidentId}`, {
      method: 'POST',
      body: JSON.stringify({ reason })
    })
  };
}

window.ApiClient = ApiClient;
