import apiClient from './apiClient'

export async function getDoctorReports() {
  const response = await apiClient.get('/reports/')
  return response.data
}

export async function createReport(predictionId) {
  const response = await apiClient.post(
    `/reports/predictions/${predictionId}`,
  )

  return response.data
}

export async function getReport(predictionId) {
  const response = await apiClient.get(
    `/reports/predictions/${predictionId}`,
  )

  return response.data
}