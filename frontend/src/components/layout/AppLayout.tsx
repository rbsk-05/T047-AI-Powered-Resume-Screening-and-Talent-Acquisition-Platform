import React, { useState } from "react";
import { Sidebar, NavTab } from "./Sidebar";
import { Header } from "./Header";

interface AppLayoutProps {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  pageTitle: string;
  breadcrumb?: string;
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({
  activeTab,
  onTabChange,
  pageTitle,
  breadcrumb,
  children,
}) => {
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

  return (
    <div className="app-container">
      {/* Sidebar for Desktop */}
      <Sidebar
        activeTab={activeTab}
        onTabChange={onTabChange}
        isOpen={mobileDrawerOpen}
        onClose={() => setMobileDrawerOpen(false)}
      />

      {/* Main Viewport Container */}
      <div className="main-content">
        <Header
          title={pageTitle}
          breadcrumb={breadcrumb}
          onMenuToggle={() => setMobileDrawerOpen(!mobileDrawerOpen)}
          onNavigateSettings={() => onTabChange("settings")}
          onNavigateProfile={() => onTabChange(activeTab === "settings" ? "dashboard" : "profile" as NavTab)}
        />
        <main className="page-body animate-fade-in">
          {children}
        </main>
      </div>
    </div>
  );
};
