import apiClient from './apiClient'

export async function createPatient(patientData) {
  const response = await apiClient.post('/patients', patientData)
  return response.data
}

export async function getPatients() {
  const response = await apiClient.get('/patients')
  return response.data
}

export async function getPatient(patientId) {
  const response = await apiClient.get(`/patients/${patientId}`)
  return response.data
}