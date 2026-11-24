import React, { useState, useRef, useEffect, useCallback } from 'react';
import { 
  LayoutDashboard, 
  Building2, 
  Filter, 
  BarChart3, 
  TrendingUp, 
  Globe2, 
  PieChart, 
  FileText, 
  Search, 
  SlidersHorizontal, 
  Activity,
  X,
  GripVertical
} from 'lucide-react';
import { useBluestockData } from '../context/useBluestockData';

const NAV_ITEMS = [
  { id: 'home', label: 'Home Overview', icon: LayoutDashboard },
  { id: 'profile', label: 'Company Profile', icon: Building2 },
  { id: 'screener', label: 'Stock Screener', icon: Filter },
  { id: 'peers', label: 'Peer Comparison', icon: BarChart3 },
  { id: 'trends', label: 'Trend Analysis', icon: TrendingUp },
  { id: 'sectors', label: 'Sector Analysis', icon: Globe2 },
  { id: 'capital', label: 'Capital Allocation', icon: PieChart },
  { id: 'reports', label: 'Annual Reports', icon: FileText },
  { id: 'equity', label: 'Equity Research', icon: Search },
  { id: 'analytics', label: 'Advanced Analytics', icon: SlidersHorizontal },
  { id: 'executive', label: 'Executive Dashboard', icon: Activity },
];

const MIN_WIDTH = 200;
const MAX_WIDTH = 460;
const DEFAULT_WIDTH = 260;

export default function Sidebar({ 
  activeTab, 
  setActiveTab, 
  searchQuery, 
  setSearchQuery, 
  onSelectCompany,
  sidebarWidth = DEFAULT_WIDTH,
  setSidebarWidth
}) {
  const { companies } = useBluestockData();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const searchContainerRef = useRef(null);

  // Resize handler using mouse drag
  const startResizing = useCallback((e) => {
    e.preventDefault();
    setIsResizing(true);
  }, []);

  const stopResizing = useCallback(() => {
    setIsResizing(false);
  }, []);

  const resize = useCallback((e) => {
    if (isResizing && setSidebarWidth) {
      const newWidth = Math.min(Math.max(e.clientX, MIN_WIDTH), MAX_WIDTH);
      setSidebarWidth(newWidth);
    }
  }, [isResizing, setSidebarWidth]);

  useEffect(() => {
    if (isResizing) {
      window.addEventListener('mousemove', resize);
      window.addEventListener('mouseup', stopResizing);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    } else {
      window.removeEventListener('mousemove', resize);
      window.removeEventListener('mouseup', stopResizing);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }
    return () => {
      window.removeEventListener('mousemove', resize);
      window.removeEventListener('mouseup', stopResizing);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing, resize, stopResizing]);

  const filteredCompanies = companies.filter(c => 
    c.name.toLowerCase().includes((searchQuery || '').toLowerCase()) ||
    c.id.toLowerCase().includes((searchQuery || '').toLowerCase()) ||
    c.sector.toLowerCase().includes((searchQuery || '').toLowerCase()) ||
    (c.subSector && c.subSector.toLowerCase().includes((searchQuery || '').toLowerCase()))
  );

  useEffect(() => {
    function handleClickOutside(event) {
      if (searchContainerRef.current && !searchContainerRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const widthPx = `${sidebarWidth}px`;

  return (
    <aside 
      className="bg-[#121214] border-r border-[rgba(255,255,255,0.08)] flex flex-col h-screen select-none shrink-0 sticky top-0 overflow-y-auto z-50 relative group/sidebar"
      style={{
        width: widthPx,
        minWidth: widthPx,
        maxWidth: widthPx,
        flexShrink: 0,
        height: '100vh',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        backgroundColor: '#121214',
        borderRight: '1px solid rgba(255, 255, 255, 0.08)',
        display: 'flex',
        flexDirection: 'column',
        overflowY: 'auto'
      }}
    >
      {/* Brand Header */}
      <div className="p-4 pb-3 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-[#0A84FF] flex items-center justify-center font-bold text-white shadow-lg shadow-blue-500/20 shrink-0">
          N
        </div>
        <div className="overflow-hidden">
          <div className="font-bold text-sm text-white tracking-tight flex items-center gap-1.5 whitespace-nowrap">
            N100 <span className="text-[10px] bg-[#2C2C2E] text-[#30D158] px-1.5 py-0.5 rounded font-mono font-semibold">PRO</span>
          </div>
          <div className="text-[9.5px] font-semibold text-[#8E8E93] uppercase tracking-wider truncate">
            STOCKS INTELLIGENCE
          </div>
        </div>
      </div>

      <div className="h-[1px] bg-[rgba(255,255,255,0.06)] mx-4 mb-3" />

      {/* Equity Quick Search */}
      <div className="px-4 mb-3 relative" ref={searchContainerRef}>
        <div className="relative flex items-center">
          <Search className="w-3.5 h-3.5 absolute left-3 text-[#8E8E93] pointer-events-none" />
          <input
            type="text"
            placeholder={`Search ${companies.length} cos...`}
            value={searchQuery}
            onFocus={() => setIsDropdownOpen(true)}
            onClick={() => setIsDropdownOpen(true)}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setIsDropdownOpen(true);
            }}
            className="w-full bg-[#1C1C1E] border border-[rgba(255,255,255,0.08)] focus:border-[#0A84FF] text-xs rounded-xl py-2 pl-8 pr-7 text-white placeholder-[#636366] outline-none transition-all shadow-inner"
            style={{
              backgroundColor: '#1C1C1E',
              color: '#FFFFFF',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '12px',
              padding: '8px 28px 8px 32px',
              width: '100%',
              fontSize: '12px'
            }}
          />
          {searchQuery && (
            <button 
              type="button"
              onClick={() => {
                setSearchQuery('');
                setIsDropdownOpen(true);
              }}
              className="absolute right-2.5 text-[#8E8E93] hover:text-white"
            >
              <X className="w-3 h-3" />
            </button>
          )}
        </div>

        {/* Dropdown Menu */}
        {isDropdownOpen && (
          <div className="absolute left-4 right-4 top-11 bg-[#1C1C1E] border border-[rgba(255,255,255,0.12)] rounded-2xl shadow-2xl z-50 max-h-80 overflow-y-auto divide-y divide-[rgba(255,255,255,0.05)] backdrop-blur-xl">
            <div className="p-2 text-[9.5px] font-bold text-[#636366] uppercase tracking-wider flex justify-between items-center bg-[#18181A] sticky top-0 z-10">
              <span>NIFTY 100 BLUECHIPS</span>
              <span className="text-[#30D158] font-mono">{filteredCompanies.length} available</span>
            </div>
            
            {filteredCompanies.length > 0 ? (
              filteredCompanies.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  onClick={() => {
                    onSelectCompany(c.id);
                    setIsDropdownOpen(false);
                    setSearchQuery('');
                  }}
                  className="w-full text-left p-2.5 hover:bg-white/[0.08] flex items-center justify-between transition-colors group cursor-pointer"
                >
                  <div className="truncate pr-2">
                    <div className="flex items-center gap-1.5">
                      <span className="font-bold text-white text-xs group-hover:text-[#0A84FF] transition-colors">
                        {c.id}
                      </span>
                      <span className="text-[9px] px-1.5 py-0.2 rounded bg-[#2C2C2E] text-[#8E8E93] font-mono truncate">
                        {c.sector}
                      </span>
                    </div>
                    <div className="text-[10px] text-[#8E8E93] truncate max-w-[130px] mt-0.5">
                      {c.name}
                    </div>
                  </div>

                  <div className="text-right shrink-0">
                    <div className="text-xs font-mono font-semibold text-white">
                      ₹{c.price.toLocaleString('en-IN')}
                    </div>
                    <div className={`text-[9.5px] font-mono font-bold ${c.isPositive ? 'text-[#30D158]' : 'text-[#FF453A]'}`}>
                      {c.change}
                    </div>
                  </div>
                </button>
              ))
            ) : (
              <div className="p-4 text-center text-xs text-[#636366]">
                No matching companies found
              </div>
            )}
          </div>
        )}
      </div>

      {/* Navigation Sections */}
      <div className="px-3 flex-1 space-y-1">
        <div className="px-3 py-1 text-[9.5px] font-bold text-[#636366] uppercase tracking-wider">
          PLATFORM MODULES
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all duration-150 ${
                isActive
                  ? 'bg-[#2C2C2E] text-white shadow-sm border border-[rgba(255,255,255,0.1)]'
                  : 'text-[#8E8E93] hover:text-white hover:bg-white/[0.04]'
              }`}
            >
              <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-[#30D158]' : 'text-[#8E8E93]'}`} />
              <span className="truncate">{item.label}</span>
              {isActive && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-[#30D158] shadow-[0_0_8px_#30D158] shrink-0" />
              )}
            </button>
          );
        })}
      </div>

      {/* User Footer Profile */}
      <div className="p-3 border-t border-[rgba(255,255,255,0.06)] flex items-center justify-between">
        <div className="flex items-center gap-2.5 overflow-hidden">
          <div className="w-7 h-7 rounded-full bg-[#0A84FF] text-white font-bold text-xs flex items-center justify-center shrink-0">
            GN
          </div>
          <div className="truncate">
            <div className="text-xs font-semibold text-white truncate">Ghanta Sai Nikhil</div>
            <div className="text-[10px] text-[#30D158] font-medium truncate">Data Intern · Bluestock</div>
          </div>
        </div>
      </div>

      {/* Draggable Resizer Handle on the Right Border */}
      <div
        onMouseDown={startResizing}
        className={`absolute top-0 right-0 w-2 h-full cursor-col-resize z-50 transition-colors flex items-center justify-center group-hover/sidebar:bg-[rgba(10,132,255,0.3)] ${
          isResizing ? 'bg-[#0A84FF] w-2.5 shadow-[0_0_10px_#0A84FF]' : 'hover:bg-[#0A84FF]/40'
        }`}
        title="Drag left or right to resize sidebar"
      >
        <div className={`w-[2px] h-8 rounded-full transition-colors ${
          isResizing ? 'bg-white' : 'bg-white/20 group-hover/sidebar:bg-white/60'
        }`} />
      </div>
    </aside>
  );
}
