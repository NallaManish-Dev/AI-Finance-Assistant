const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1'

export async function apiRequest(path, options = {}) {
  const { headers, ...requestOptions } = options
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...requestOptions,
    headers: { 'Content-Type': 'application/json', ...headers },
  })
  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(data.error || 'Something went wrong. Please try again.')
  }

  return data
}
