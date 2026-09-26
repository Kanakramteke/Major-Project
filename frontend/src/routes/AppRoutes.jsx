import { Navigate, Route, Routes } from 'react-router-dom'

import Dashboard from '../pages/Dashboard'
import DashboardLayout from '../layouts/DashboardLayout'
import Home from '../pages/Home'
import Login from '../pages/Login'
import PatientDetails from '../pages/PatientDetails'
import Patients from '../pages/Patients'
import Register from '../pages/Register'
import Upload from '../pages/Upload'
import Results from '../pages/Results'
import History from '../pages/History'
import Reports from '../pages/Reports'

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route element={<DashboardLayout />}>
        <Route path="/dashboard" element={<Dashboard />} />

        <Route path="/patients" element={<Patients />} />

        <Route
          path="/patients/new"
          element={<PatientDetails />}
        />

        <Route
          path="/patients/:patientId"
          element={<PatientDetails />}
        />

        <Route
          path="/upload"
          element={<Upload />}
        />

        <Route path="/results" element={<Results />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
      <Route path="/history" element={<History />} />
      <Route path="/reports" element={<Reports />} />
    </Routes>
  )
}

export default AppRoutes