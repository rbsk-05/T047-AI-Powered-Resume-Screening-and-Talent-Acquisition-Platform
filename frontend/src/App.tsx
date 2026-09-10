import React, { useState } from "react";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import { LandingPage } from "./components/LandingPage";
import { AuthScreen } from "./components/AuthScreen";
import { AppLayout } from "./components/layout/AppLayout";
import { NavTab, CandidateNavTab, RecruiterNavTab } from "./components/layout/Sidebar";
import { StoredJob } from "./api";

// Candidate views
import { CandidateDashboard } from "./components/candidate/CandidateDashboard";
import { CandidateBrowseJobs } from "./components/candidate/CandidateBrowseJobs";
import { JobDetailsModal } from "./components/candidate/JobDetailsModal";
import { ApplyModal } from "./components/ApplyModal";
import { MyApplications } from "./components/MyApplications";
import { CandidateSkillAnalysis } from "./components/candidate/CandidateSkillAnalysis";
import { CandidateRecommendations } from "./components/candidate/CandidateRecommendations";
import { CandidateProfile } from "./components/candidate/CandidateProfile";

// Recruiter views
import { RecruiterDashboard } from "./components/recruiter/RecruiterDashboard";
import { RecruiterCompanyProfile } from "./components/recruiter/RecruiterCompanyProfile";
import { RecruiterJobManagement } from "./components/recruiter/RecruiterJobManagement";
import { CreateJobModal } from "./components/recruiter/CreateJobModal";
import { JobApplicationsView } from "./components/JobApplicationsView";
import { RecruiterCandidatesPage } from "./components/recruiter/RecruiterCandidatesPage";
import { RecruiterCandidateRankingPage } from "./components/recruiter/RecruiterCandidateRankingPage";
import { RecruiterCandidateComparisonPage } from "./components/recruiter/RecruiterCandidateComparisonPage";
import { RecruiterAnalytics } from "./components/recruiter/RecruiterAnalytics";

// Common views
import { SettingsView } from "./components/common/SettingsView";
import { LoadingState } from "./components/ui/LoadingState";
import { listJobs } from "./api";

function CandidateAppShell() {
  const [activeTab, setActiveTab] = useState<CandidateNavTab>("dashboard");
  const [jobs, setJobs] = useState<StoredJob[]>([]);
  const [selectedJobForDetails, setSelectedJobForDetails] = useState<StoredJob | null>(null);
  const [selectedJobForApply, setSelectedJobForApply] = useState<StoredJob | null>(null);

  React.useEffect(() => {
    listJobs().then(setJobs).catch(console.error);
  }, []);

  const getPageMeta = () => {
    switch (activeTab) {
      case "browse_jobs":
        return { title: "Browse Open Positions", breadcrumb: "Candidate / Job Discovery" };
      case "my_applications":
        return { title: "My Applications & ATS Reports", breadcrumb: "Candidate / Applications" };
      case "skill_analysis":
        return { title: "Skill Gap Analysis", breadcrumb: "Candidate / Intelligence" };
      case "recommendations":
        return { title: "Personalized Upskilling Roadmaps", breadcrumb: "Candidate / Recommendations" };
      case "profile":
        return { title: "My Profile & Verified Skills", breadcrumb: "Candidate / Account" };
      case "settings":
        return { title: "Settings & Preferences", breadcrumb: "Candidate / Settings" };
      case "dashboard":
      default:
        return { title: "Candidate Dashboard", breadcrumb: "Candidate / Overview" };
    }
  };

  const meta = getPageMeta();

  return (
    <AppLayout
      activeTab={activeTab}
      onTabChange={(tab) => setActiveTab(tab as CandidateNavTab)}
      pageTitle={meta.title}
      breadcrumb={meta.breadcrumb}
    >
      {activeTab === "dashboard" && (
        <CandidateDashboard
          onNavigate={(tab) => setActiveTab(tab)}
          onSelectJob={(job) => setSelectedJobForDetails(job)}
        />
      )}

      {activeTab === "browse_jobs" && (
        <CandidateBrowseJobs
          jobs={jobs}
          onSelectJob={(job) => setSelectedJobForDetails(job)}
          onApplyJob={(job) => setSelectedJobForApply(job)}
        />
      )}

      {activeTab === "my_applications" && (
        <MyApplications onBrowseJobs={() => setActiveTab("browse_jobs")} />
      )}

      {activeTab === "skill_analysis" && <CandidateSkillAnalysis />}

      {activeTab === "recommendations" && <CandidateRecommendations />}

      {activeTab === "profile" && <CandidateProfile />}

      {activeTab === "settings" && <SettingsView />}

      {/* Job Details Modal */}
      {selectedJobForDetails && (
        <JobDetailsModal
          job={selectedJobForDetails}
          onClose={() => setSelectedJobForDetails(null)}
          onApply={(job) => {
            setSelectedJobForDetails(null);
            setSelectedJobForApply(job);
          }}
        />
      )}

      {/* Apply Modal */}
      {selectedJobForApply && (
        <ApplyModal
          job={selectedJobForApply}
          onClose={() => setSelectedJobForApply(null)}
          onSuccess={() => {
            setSelectedJobForApply(null);
            setActiveTab("my_applications");
          }}
        />
      )}
    </AppLayout>
  );
}

function RecruiterAppShell() {
  const [activeTab, setActiveTab] = useState<RecruiterNavTab>("dashboard");
  const [selectedJob, setSelectedJob] = useState<StoredJob | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const getPageMeta = () => {
    switch (activeTab) {
      case "company_profile":
        return { title: "Company Profile", breadcrumb: "Recruiter / Organization" };
      case "jobs":
        return { title: "Job Management", breadcrumb: "Recruiter / Open Roles" };
      case "applications":
        return { title: "Applications Intake", breadcrumb: "Recruiter / Applicants" };
      case "candidates":
      case "candidate_ranking":
        return { title: "Candidate Rankings & Pool", breadcrumb: "Recruiter / Talent Directory" };
      case "candidate_comparison":
        return { title: "Candidate Comparison Tool", breadcrumb: "Recruiter / Evaluation" };
      case "analytics":
        return { title: "Recruitment Pipeline Analytics", breadcrumb: "Recruiter / Insights" };
      case "settings":
        return { title: "Settings & Preferences", breadcrumb: "Recruiter / Settings" };
      case "dashboard":
      default:
        return { title: "Recruiter Dashboard", breadcrumb: "Recruiter / Command Center" };
    }
  };

  const meta = getPageMeta();

  return (
    <AppLayout
      activeTab={activeTab}
      onTabChange={(tab) => {
        setSelectedJob(null);
        setActiveTab(tab as RecruiterNavTab);
      }}
      pageTitle={selectedJob ? `Applicants: ${selectedJob.title}` : meta.title}
      breadcrumb={selectedJob ? "Recruiter / Applicants" : meta.breadcrumb}
    >
      {selectedJob ? (
        <JobApplicationsView job={selectedJob} onBack={() => setSelectedJob(null)} />
      ) : (
        <>
          {activeTab === "dashboard" && (
            <RecruiterDashboard
              onNavigate={(tab) => setActiveTab(tab)}
              onCreateJob={() => setShowCreateModal(true)}
              onSelectJob={(job) => setSelectedJob(job)}
            />
          )}

          {activeTab === "company_profile" && <RecruiterCompanyProfile />}

          {activeTab === "jobs" && (
            <RecruiterJobManagement
              onCreateJob={() => setShowCreateModal(true)}
              onSelectJob={(job) => setSelectedJob(job)}
            />
          )}

          {(activeTab === "applications" || activeTab === "candidates") && (
            <RecruiterCandidatesPage />
          )}

          {activeTab === "candidate_ranking" && (
            <RecruiterCandidateRankingPage />
          )}

          {activeTab === "candidate_comparison" && (
            <RecruiterCandidateComparisonPage />
          )}

          {activeTab === "analytics" && <RecruiterAnalytics />}

          {activeTab === "settings" && <SettingsView />}
        </>
      )}

      {/* Create Job Modal */}
      {showCreateModal && (
        <CreateJobModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onSuccess={(newJob) => {
            setShowCreateModal(false);
            setActiveTab("jobs");
          }}
        />
      )}
    </AppLayout>
  );
}

function MainRouter() {
  const { user, isLoading } = useAuth();
  const [viewState, setViewState] = useState<"landing" | "auth">("landing");

  if (isLoading) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: "var(--bg-primary)" }}>
        <LoadingState message="Initializing TalentLens AI platform..." />
      </div>
    );
  }

  if (!user) {
    if (viewState === "landing") {
      return (
        <LandingPage
          onGetStarted={() => setViewState("auth")}
          onLogin={() => setViewState("auth")}
        />
      );
    }
    return <AuthScreen onBackToLanding={() => setViewState("landing")} />;
  }

  return user.role === "recruiter" ? <RecruiterAppShell /> : <CandidateAppShell />;
}

export default function App() {
  return (
    <AuthProvider>
      <MainRouter />
    </AuthProvider>
  );
}
