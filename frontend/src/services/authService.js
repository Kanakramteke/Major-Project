import apiClient from './apiClient'

export async function registerDoctor(doctorData) {
  const response = await apiClient.post('/auth/register', doctorData)
  return response.data
}

export async function loginDoctor(credentials) {
  const response = await apiClient.post('/auth/login', credentials)
  return response.data
}