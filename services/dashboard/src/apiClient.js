/* Centralized API client helpers for the dashboard
 * - getApiCandidates(): returns ordered API base URL candidates
 * - getWsCandidates(): returns ordered WebSocket base URL candidates
 * - fetchWithFallback(path, options): tries candidates in order until one succeeds
 *
 * This module is designed to handle Codespaces (app.github.dev) hostnames,
 * locally-run dev server (relative paths) and explicit `REACT_APP_API_URL` values.
 */

function logClient(...args) {
  try {
    if (typeof window !== 'undefined') {
      window.__EVENT_DEBUG_LOG = window.__EVENT_DEBUG_LOG || [];
      const text = args.map(a => (typeof a === 'object' ? JSON.stringify(a) : String(a))).join(' ');
      window.__EVENT_DEBUG_LOG.push(`${new Date().toISOString()} ${text}`);
      if (window.__EVENT_DEBUG_LOG.length > 200) window.__EVENT_DEBUG_LOG.shift();
    }
  } catch (e) {}
  // eslint-disable-next-line no-console
  console.debug(...args);
}

function warnClient(...args) {
  try { if (typeof window !== 'undefined') { window.__EVENT_DEBUG_LOG = window.__EVENT_DEBUG_LOG || []; window.__EVENT_DEBUG_LOG.push(`${new Date().toISOString()} WARN ${args.join(' ')}`); if (window.__EVENT_DEBUG_LOG.length > 200) window.__EVENT_DEBUG_LOG.shift(); } } catch(e) {}
  // eslint-disable-next-line no-console
  console.warn(...args);
}

function isLocalhostCandidate(u) {
  if (!u) return false;
  return /localhost|127\.0\.0\.1|\[::1\]/i.test(u);
}

export function getApiCandidates() {
  const apiUrl = process.env.REACT_APP_API_URL;
  const hostname = (typeof window !== 'undefined' && window.location && window.location.hostname) ? window.location.hostname : '';
  const protocol = (typeof window !== 'undefined' && window.location && window.location.protocol === 'https:') ? 'https' : 'http';

  const codespaceMatch = hostname.match(/^(.*)-(\d+)\.app\.github\.dev$/);

  // If an explicit env was provided at runtime, prefer it. If it points at localhost
  // but we're running in Codespaces, rewrite to the codespace-accessible hostname.
  if (apiUrl && apiUrl.trim()) {
    try {
      const trimmed = apiUrl.trim();
      if (isLocalhostCandidate(trimmed) && codespaceMatch) {
        const base = codespaceMatch[1];
        const primary = `${protocol}://${base}-8000.app.github.dev`;
        const fallback = `${protocol}://${hostname}:8000`;
        logClient('apiClient: rewritten REACT_APP_API_URL from localhost to codespace candidate', { original: trimmed, candidates: [primary, fallback] });
        return [primary, fallback];
      }
      const fallback = `${protocol}://${hostname}:8000`;
      logClient('apiClient: using REACT_APP_API_URL with fallback', { env: trimmed, fallback });
      return [trimmed, fallback];
    } catch (e) {
      warnClient('apiClient: error parsing REACT_APP_API_URL', e && e.message ? e.message : e);
    }
  }

  // No explicit env - auto-detect
  if (codespaceMatch) {
    const base = codespaceMatch[1];
    const primary = `${protocol}://${base}-8000.app.github.dev`;
    const fallback = `${protocol}://${hostname}:8000`;
    logClient('apiClient: codespace-detected candidates', [primary, fallback]);
    return [primary, fallback];
  }

  // Development: use relative path so CRA proxy works
  if (process.env.NODE_ENV === 'development') {
    logClient('apiClient: development -> using relative API path');
    return [''];
  }

  // Default: assume API on same host port 8000
  const prod = `${protocol}://${hostname}:8000`;
  logClient('apiClient: default production candidate', prod);
  return [prod];
}

export function getWsCandidates() {
  const apiCandidates = getApiCandidates();
  const proto = (typeof window !== 'undefined' && window.location && window.location.protocol === 'https:') ? 'wss' : 'ws';
  const hostname = (typeof window !== 'undefined' && window.location && window.location.hostname) ? window.location.hostname : '';
  const codespaceMatch = hostname.match(/^(.*)-(\d+)\.app\.github\.dev$/);

  const ws = apiCandidates.map(u => {
    if (!u) {
      if (codespaceMatch) {
        const apiHost = `${codespaceMatch[1]}-8000.app.github.dev`;
        return `${proto}://${apiHost}`;
      }
      const host = (typeof window !== 'undefined' && window.location && window.location.host) ? window.location.host.replace(/:3000$/, ':8000') : `${hostname}:8000`;
      return `${proto}://${host}`;
    }
    return `${u.startsWith('https') ? 'wss' : 'ws'}://${u.replace(/^https?:\/\//, '')}`;
  });
  logClient('apiClient: websocket candidates', ws);
  return ws;
}

export async function fetchWithFallback(path, options = {}) {
  const candidatesRaw = getApiCandidates();

  // Auto-inject Auth token if present
  const token = localStorage.getItem('event_token');
  if (token) {
    options.headers = {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    };
  }

  // Filter out localhost/127.0.0.1 candidates if the browser is not on localhost
  const hostname = (typeof window !== 'undefined' && window.location && window.location.hostname) ? window.location.hostname : '';
  const runningOnLocalhost = hostname === 'localhost' || hostname === '127.0.0.1';

  const candidates = candidatesRaw.filter(c => {
    if (!c) return true; // keep relative candidate
    if (isLocalhostCandidate(c) && !runningOnLocalhost) {
      logClient('apiClient.fetchWithFallback: skipping localhost candidate in non-local browser', c);
      return false;
    }
    return true;
  });

  logClient('apiClient.fetchWithFallback: candidates to try', candidates);

  const errors = [];
  for (const base of candidates) {
    const url = base ? `${base}${path.startsWith('/') ? path : `/${path}`}` : path;
    logClient('apiClient.fetchWithFallback: trying', url);
    try {
      const res = await fetch(url, options);
      logClient('apiClient.fetchWithFallback: response', url, res.status);
      if (!res.ok) {
        warnClient('apiClient.fetchWithFallback: non-OK response', url, res.status);
        return res;
      }
      return res;
    } catch (err) {
      warnClient('apiClient.fetchWithFallback: error for', url, err && err.message ? err.message : err);
      errors.push({ url, err });
    }
  }

  const last = errors.length ? errors[errors.length - 1].err : new Error('No API candidates available');
  throw last;
}

export default {
  getApiCandidates,
  getWsCandidates,
  fetchWithFallback,
};
