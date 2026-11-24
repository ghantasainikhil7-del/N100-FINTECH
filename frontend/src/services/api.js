// Centralized API Client configured for both local and Render production backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://n100-api.onrender.com';

export async function fetchFromApi(endpoint) {
  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`);
    if (!res.ok) {
      throw new Error(`API error: ${res.status} ${res.statusText}`);
    }
    return await res.json();
  } catch (err) {
    console.warn(`[Bluestock API] Failed to fetch ${endpoint}, using client fallback:`, err.message);
    return null;
  }
}

export function getTearsheetPdfUrl(ticker) {
  return `${API_BASE_URL}/api/v1/reports/tearsheet/${ticker}`;
}

export function getSectorPdfUrl(sector) {
  return `${API_BASE_URL}/api/v1/reports/sector/${encodeURIComponent(sector)}`;
}

export { API_BASE_URL };
