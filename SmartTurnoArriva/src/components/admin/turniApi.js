import { TURNI_API_BASE } from '../../config.js';

async function request(path, { method = 'GET', adminKey, body } = {}) {
  const url = new URL(`${TURNI_API_BASE}${path}`);
  const isAdmin = path.startsWith('/api/admin');
  if (isAdmin && method === 'GET') url.searchParams.set('key', adminKey);

  const res = await fetch(url, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(isAdmin && method !== 'GET' ? { Authorization: `Bearer ${adminKey}` } : {}),
    },
    body: body ? JSON.stringify(isAdmin && method !== 'GET' ? { ...body, key: adminKey } : body) : undefined,
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new Error(data?.reason || `errore ${res.status}`);
  return data;
}

export const turniApi = {
  depots: () => request('/api/depots'),
  schedule: (depotId, from, to) =>
    request(`/api/schedule?depot=${encodeURIComponent(depotId)}&from=${from}&to=${to}`),
  drivers: (depotId, adminKey) => request(`/api/admin/depots/${depotId}/drivers`, { adminKey }),
  addDriver: (depotId, name, adminKey) =>
    request(`/api/admin/depots/${depotId}/drivers`, { method: 'POST', adminKey, body: { name } }),
  updateDriver: (id, patch, adminKey) =>
    request(`/api/admin/drivers/${id}`, { method: 'PUT', adminKey, body: patch }),
  reorderDriver: (id, swapWithDriverId, adminKey) =>
    request(`/api/admin/drivers/${id}/reorder`, { method: 'PUT', adminKey, body: { swapWithDriverId } }),

  depot: (depotId, adminKey) => request(`/api/admin/depots/${depotId}`, { adminKey }),
  updateDepot: (depotId, patch, adminKey) =>
    request(`/api/admin/depots/${depotId}`, { method: 'PUT', adminKey, body: patch }),

  blocks: (depotId, adminKey) => request(`/api/admin/depots/${depotId}/blocks`, { adminKey }),
  createBlock: (depotId, block_type, label, adminKey) =>
    request(`/api/admin/depots/${depotId}/blocks`, { method: 'POST', adminKey, body: { block_type, label } }),
  cells: (blockId, adminKey) => request(`/api/admin/blocks/${blockId}/cells`, { adminKey }),
  saveCells: (blockId, cells, adminKey) =>
    request(`/api/admin/blocks/${blockId}/cells`, { method: 'PUT', adminKey, body: { cells } }),

  specialPeriods: (depotId, adminKey) =>
    request(`/api/admin/special-periods?depot=${encodeURIComponent(depotId)}`, { adminKey }),
  createSpecialPeriod: (payload, adminKey) =>
    request('/api/admin/special-periods', { method: 'POST', adminKey, body: payload }),
  updateSpecialPeriod: (id, patch, adminKey) =>
    request(`/api/admin/special-periods/${id}`, { method: 'PUT', adminKey, body: patch }),
  deleteSpecialPeriod: (id, adminKey) =>
    request(`/api/admin/special-periods/${id}`, { method: 'DELETE', adminKey, body: {} }),

  schedulePreview: (depotId, date, adminKey) =>
    request(`/api/admin/schedule-preview?depot=${encodeURIComponent(depotId)}&date=${date}`, { adminKey }),

  schoolCalendarYears: (adminKey) => request('/api/admin/school-calendar-years', { adminKey }),
  updateSchoolCalendarYear: (year, patch, adminKey) =>
    request(`/api/admin/school-calendar-years/${year}`, { method: 'PUT', adminKey, body: patch }),
};

export const WEEKDAY_LABELS = ['Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab', 'Dom'];
