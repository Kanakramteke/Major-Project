import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import {
  Brain,
  ClipboardList,
  FileText,
  History,
  LayoutDashboard,
  LogOut,
  Users,
} from 'lucide-react'
import './DashboardLayout.css'

function DashboardLayout() {
  const navigate = useNavigate()

  function handleLogout() {
    localStorage.removeItem('access_token')
    navigate('/login', { replace: true })
  }

  const navigationItems = [
    {
      label: 'Dashboard',
      path: '/dashboard',
      icon: LayoutDashboard,
    },
    {
      label: 'Patients',
      path: '/patients',
      icon: Users,
    },
    {
      label: 'MRI Analysis',
      path: '/upload',
      icon: Brain,
    },
    {
      label: 'Reports',
      path: '/reports',
      icon: FileText,
    },
    {
      label: 'History',
      path: '/history',
      icon: History,
    },
  ]

  return (
    <div className="dashboard-shell">
      <aside className="dashboard-sidebar">
        <div className="dashboard-brand">
          <div className="dashboard-brand-icon">
            <Brain size={22} />
          </div>

          <div>
            <h1>MedExplain AI</h1>
            <span>Clinical AI Platform</span>
          </div>
        </div>

        <nav className="dashboard-navigation">
          <p className="dashboard-navigation-title">Workspace</p>

          {navigationItems.map((item) => {
            const Icon = item.icon

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `dashboard-nav-link ${isActive ? 'active' : ''}`
                }
              >
                <Icon size={19} />
                <span>{item.label}</span>
              </NavLink>
            )
          })}
        </nav>

        <div className="dashboard-sidebar-footer">
          <button
            type="button"
            className="dashboard-logout"
            onClick={handleLogout}
          >
            <LogOut size={19} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      <main className="dashboard-main">
        <header className="dashboard-topbar">
          <div>
            <span className="dashboard-topbar-label">
              Doctor Workspace
            </span>
          </div>

          <div className="dashboard-user">
            <div className="dashboard-user-avatar">
              D
            </div>

            <div className="dashboard-user-info">
              <strong>Doctor</strong>
              <span>Medical Professional</span>
            </div>
          </div>
        </header>

        <section className="dashboard-content">
          <Outlet />
        </section>
      </main>
    </div>
  )
}

export default DashboardLayout