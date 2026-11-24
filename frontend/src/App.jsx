import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import HomeOverview from './pages/HomeOverview';
import CompanyProfile from './pages/CompanyProfile';
import StockScreener from './pages/StockScreener';
import PeerComparison from './pages/PeerComparison';
import TrendAnalysis from './pages/TrendAnalysis';
import SectorAnalysis from './pages/SectorAnalysis';
import CapitalAllocation from './pages/CapitalAllocation';
import AnnualReports from './pages/AnnualReports';
import EquityResearch from './pages/EquityResearch';
import AdvancedAnalytics from './pages/AdvancedAnalytics';
import ExecutiveDashboard from './pages/ExecutiveDashboard';
import { useBluestockData } from './context/useBluestockData';

export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [sidebarWidth, setSidebarWidth] = useState(260);
  const { selectedTicker, setSelectedTicker, searchQuery, setSearchQuery, currentCompany } = useBluestockData();

  const handleSelectCompany = (ticker) => {
    setSelectedTicker(ticker);
    setActiveTab('profile');
  };

  const renderActiveScreen = () => {
    switch (activeTab) {
      case 'home':
        return <HomeOverview onSelectCompany={handleSelectCompany} />;
      case 'profile':
        return <CompanyProfile selectedTicker={selectedTicker} onSelectCompany={handleSelectCompany} />;
      case 'screener':
        return <StockScreener onSelectCompany={handleSelectCompany} />;
      case 'peers':
        return <PeerComparison />;
      case 'trends':
        return <TrendAnalysis />;
      case 'sectors':
        return <SectorAnalysis />;
      case 'capital':
        return <CapitalAllocation />;
      case 'reports':
        return <AnnualReports />;
      case 'equity':
        return <EquityResearch />;
      case 'analytics':
        return <AdvancedAnalytics />;
      case 'executive':
        return <ExecutiveDashboard />;
      default:
        return <HomeOverview onSelectCompany={handleSelectCompany} />;
    }
  };

  const getScreenMeta = () => {
    switch (activeTab) {
      case 'home':
        return { title: 'N100 Overview', subtitle: 'Real-time constituent market snapshot & aggregate fundamental indices' };
      case 'profile':
        return { title: 'Company Fundamental & Valuation Profile', subtitle: `Audited financial statements, valuation metrics, and balance sheet strength for ${selectedTicker}` };
      case 'screener':
        return { title: 'Institutional Investment Screener', subtitle: 'Dynamic multi-ratio filtering across all 92 constituents with pre-built investment themes' };
      case 'peers':
        return { title: 'Peer Comparison & Competitive Benchmarking', subtitle: '8-axis polar radar charts and direct company vs company duel' };
      case 'trends':
        return { title: 'Multi-Year Fundamental Trend Analysis', subtitle: '10-year growth trajectories and sales-to-cash conversion overlays' };
      case 'sectors':
        return { title: 'Sector Intelligence & Macro Weights', subtitle: 'Industry concentration, median ROE benchmarks, and constituent depth' };
      case 'capital':
        return { title: 'Capital Allocation Matrix & Cash Dynamics', subtitle: '8-pattern taxonomy categorizing organic CapEx, debt repayment, and dividend returns' };
      case 'reports':
        return { title: 'Annual Reports & Executive Tearsheets', subtitle: 'Direct BSE regulatory archives and 2-page PDF investment tearsheets' };
      case 'equity':
        return { title: 'Institutional Equity Research & DCF Models', subtitle: 'Analyst consensus targets, margin of safety, and intrinsic fair value' };
      case 'analytics':
        return { title: 'Advanced Quantitative Analytics & Modeling', subtitle: 'DuPont 3-stage mathematical decomposition and factor dispersion heatmaps' };
      case 'executive':
        return { title: 'Executive & CIO Boardroom Intelligence', subtitle: 'Macro market capital distribution, profit pool concentration, and systemic risk surveillance' };
      default:
        return { title: 'N100 Financial Intelligence', subtitle: '' };
    }
  };

  const meta = getScreenMeta();

  return (
    <div 
      className="flex min-h-screen bg-black text-white"
      style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#000000', color: '#FFFFFF', width: '100%', overflowX: 'hidden' }}
    >
      {/* Draggable Resizable Sidebar */}
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        onSelectCompany={handleSelectCompany}
        sidebarWidth={sidebarWidth}
        setSidebarWidth={setSidebarWidth}
      />

      {/* Main Content Area dynamically adjusting width */}
      <div 
        className="flex-1 flex flex-col min-w-0 overflow-y-auto"
        style={{ 
          flex: '1 1 0%', 
          minWidth: 0, 
          display: 'flex', 
          flexDirection: 'column', 
          width: `calc(100% - ${sidebarWidth}px)`, 
          height: '100vh', 
          overflowY: 'auto' 
        }}
      >
        <Header title={meta.title} subtitle={meta.subtitle} />
        <main className="flex-1 pb-12" style={{ flex: '1 1 0%' }}>
          {renderActiveScreen()}
        </main>
      </div>
    </div>
  );
}
