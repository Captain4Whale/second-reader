export const ACTIVE_FRONTEND_ENDPOINTS = [
  "POST /api/uploads/epub",
  "POST /api/books/{book_id}/analysis/start",
  "POST /api/books/{book_id}/analysis/resume",
  "GET /api/jobs/{job_id}",
  "GET /api/books",
  "GET /api/books/{book_id}",
  "GET /api/books/{book_id}/analysis-state",
  "GET /api/books/{book_id}/activity",
  "GET /api/books/{book_id}/marks",
  "GET /api/books/{book_id}/chapters/{chapter_id}",
  "GET /api/books/{book_id}/chapters/{chapter_id}/outline",
  "GET /api/books/{book_id}/cover",
  "GET /api/books/{book_id}/source",
  "GET /api/marks",
  "PUT /api/marks/{reaction_id}",
  "DELETE /api/marks/{reaction_id}",
  "WS /api/ws/books/{book_id}/analysis",
] as const;

export const ACTIVE_INTEGRATION_SPEC = {
  active_frontend_endpoints: [...ACTIVE_FRONTEND_ENDPOINTS],
} as const;
