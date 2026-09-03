import { AuthProvider, useAuth } from "./auth/AuthContext";
import { AuthScreen } from "./components/AuthScreen";
import { CandidatePortal } from "./components/CandidatePortal";
import { RecruiterDashboard } from "./components/RecruiterDashboard";

function Dashboard() {
  const { user, logout } = useAuth();
  if (!user) return null;

  return (
    <main>
      <div className="topbar">
        <div>
          <p className="eyebrow topbar-eyebrow">TalentLens AI</p>
          <p className="topbar-user">
            {user.full_name} · <span className="role-badge">{user.role}</span>
          </p>
        </div>
        <button type="button" className="ghost-button" onClick={logout}>
          Sign out
        </button>
      </div>
      {user.role === "recruiter" ? <RecruiterDashboard /> : <CandidatePortal />}
    </main>
  );
}

function AppShell() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <main>
        <p className="empty">Loading TalentLens AI…</p>
      </main>
    );
  }

  return user ? <Dashboard /> : <AuthScreen />;
}

export default function App() {
  return (
    <AuthProvider>
      <AppShell />
    </AuthProvider>
  );
}
