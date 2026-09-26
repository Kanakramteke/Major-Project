import apiClient from './apiClient'

export async function getDoctorHistory() {
  const response = await apiClient.get('/history/')

  return response.data
}

export async function getPatientHistory(patientId) {
  const response = await apiClient.get(
    `/history/patients/${patientId}`,
  )

  return response.data
}

export async function getPrediction(predictionId) {
  const response = await apiClient.get(
    `/history/predictions/${predictionId}`,
  )

  return response.data
}