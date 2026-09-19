const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : window.location.origin);


async function fetchApi(endpoint) {
  const response = await fetch(
    `${API_BASE_URL}${endpoint}`
  );

  if (!response.ok) {
    throw new Error(
      `API request failed: ${response.status}`
    );
  }

  return response.json();
}


function buildFilterQuery(filters = {}) {
  const params = new URLSearchParams();

  if (filters.event_type) {
    params.append(
      "event_type",
      filters.event_type
    );
  }

  if (filters.state) {
    params.append(
      "state",
      filters.state
    );
  }

  if (filters.verification_status) {
    params.append(
      "verification_status",
      filters.verification_status
    );
  }

  const query = params.toString();

  return query ? `?${query}` : "";
}


export async function getDashboardSummary(
  filters = {}
) {
  return fetchApi(
    `/analytics/summary${buildFilterQuery(filters)}`
  );
}


export async function getRecentReports(
  limit = 10,
  filters = {}
) {
  const query = new URLSearchParams();

  query.append("limit", limit);

  if (filters.event_type) {
    query.append(
      "event_type",
      filters.event_type
    );
  }

  if (filters.state) {
    query.append(
      "state",
      filters.state
    );
  }

  if (filters.verification_status) {
    query.append(
      "verification_status",
      filters.verification_status
    );
  }

  return fetchApi(
    `/analytics/recent-reports?${query.toString()}`
  );
}


export async function getMapReports(
  filters = {}
) {
  return fetchApi(
    `/analytics/map-reports${buildFilterQuery(filters)}`
  );
}


export async function getEventDistribution(
  state = ""
) {
  const params = new URLSearchParams();

  if (state) {
    params.append("state", state);
  }

  const query = params.toString();

  return fetchApi(
    `/analytics/event-distribution${query ? `?${query}` : ""}`
  );
}


export async function getLocationDistribution(
  eventType = ""
) {
  const params = new URLSearchParams();

  if (eventType) {
    params.append(
      "event_type",
      eventType
    );
  }

  const query = params.toString();

  return fetchApi(
    `/analytics/location-distribution${query ? `?${query}` : ""}`
  );
}
