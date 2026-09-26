import { Plus, Search, UserRound } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getPatients } from '../services/patientService'
import './Patients.css'

function Patients() {
  const navigate = useNavigate()

  const [patients, setPatients] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadPatients() {
      try {
        setLoading(true)
        setError('')

        const data = await getPatients()

        setPatients(data)
      } catch (error) {
        if (error.response?.status === 401) {
          setError('Your session has expired. Please log in again.')
        } else {
          setError('Unable to load patients. Please try again.')
        }
      } finally {
        setLoading(false)
      }
    }

    loadPatients()
  }, [])

  const filteredPatients = patients.filter((patient) => {
    const search = searchTerm.toLowerCase().trim()

    if (!search) {
      return true
    }

    return (
      patient.full_name.toLowerCase().includes(search) ||
      patient.patient_id.toLowerCase().includes(search)
    )
  })

  return (
    <div className="patients-page">
      <div className="patients-header">
        <div>
          <p className="patients-eyebrow">Patient management</p>

          <h1>Patients</h1>

          <p>
            Manage patient records and access their MRI analysis history.
          </p>
        </div>

        <button
          type="button"
          className="patients-add-button"
          onClick={() => navigate('/patients/new')}
        >
          <Plus size={17} />
          Add Patient
        </button>
      </div>

      <section className="patients-toolbar">
        <div className="patients-search">
          <Search size={17} />

          <input
            type="text"
            placeholder="Search by patient name or ID..."
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
          />
        </div>
      </section>

      {error && (
        <div
          style={{
            marginTop: '20px',
            padding: '13px 15px',
            borderRadius: '9px',
            background: '#fef2f2',
            color: '#991b1b',
            fontSize: '13px',
          }}
          role="alert"
        >
          {error}
        </div>
      )}

      {loading ? (
        <section className="patients-empty-state">
          <div className="patients-empty-icon">
            <UserRound size={25} />
          </div>

          <h2>Loading patients...</h2>

          <p>
            Fetching patient records from your workspace.
          </p>
        </section>
      ) : filteredPatients.length === 0 ? (
        <section className="patients-empty-state">
          <div className="patients-empty-icon">
            <UserRound size={25} />
          </div>

          <h2>
            {searchTerm ? 'No matching patients' : 'No patients yet'}
          </h2>

          <p>
            {searchTerm
              ? 'Try a different patient name or ID.'
              : 'Add your first patient to begin an MRI analysis.'}
          </p>

          {!searchTerm && (
            <button
              type="button"
              className="patients-empty-button"
              onClick={() => navigate('/patients/new')}
            >
              <Plus size={16} />
              Add First Patient
            </button>
          )}
        </section>
      ) : (
        <section className="patients-list-card">
          <div className="patients-list-header">
            <div>
              <h2>Patient Records</h2>

              <span>
                {filteredPatients.length}{' '}
                {filteredPatients.length === 1
                  ? 'patient'
                  : 'patients'}
              </span>
            </div>
          </div>

          <div className="patients-table-wrapper">
            <table className="patients-table">
              <thead>
                <tr>
                  <th>Patient ID</th>
                  <th>Name</th>
                  <th>Age</th>
                  <th>Gender</th>
                  <th>Contact</th>
                </tr>
              </thead>

              <tbody>
                {filteredPatients.map((patient) => (
                  <tr
                    key={patient.id}
                    onClick={() =>
                      navigate(`/patients/${patient.id}`)
                    }
                    style={{ cursor: 'pointer' }}
                  >
                    <td>
                      <span className="patients-id">
                        {patient.patient_id}
                      </span>
                    </td>

                    <td>
                      <div className="patients-name-cell">
                        <div className="patients-avatar">
                          <UserRound size={16} />
                        </div>

                        <strong>{patient.full_name}</strong>
                      </div>
                    </td>

                    <td>{patient.age}</td>

                    <td>
                      {patient.gender.charAt(0).toUpperCase() +
                        patient.gender.slice(1)}
                    </td>

                    <td>{patient.contact || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  )
}

export default Patients