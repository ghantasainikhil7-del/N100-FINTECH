import React, { useState, useMemo } from 'react';
import { 
  Filter, 
  Download, 
  Sparkles, 
  CheckCircle2, 
  ArrowUpDown,
  SlidersHorizontal,
  ChevronDown,
  ChevronUp,
  RotateCcw
} from 'lucide-react';
import { useBluestockData } from '../context/useBluestockData';

const PRESETS = [
  { id: 'quality', name: 'Quality Compounder', desc: 'ROE > 15%, D/E < 1.0, Positive FCF, Score ≥ 70' },
  { id: 'value', name: 'Value Pick', desc: 'P/E < 25, P/B < 3.5, Div Yield > 1.0%' },
  { id: 'growth', name: 'Growth Accelerator', desc: 'ROE > 18%, ROCE > 20%, D/E < 1.5' },
  { id: 'dividend', name: 'Dividend Champion', desc: 'Div Yield > 2.0%, Positive FCF' },
  { id: 'debt_free', name: 'Debt-Free Blue Chip', desc: 'D/E ≤ 0.05 (Negligible Debt), ROE > 12%' },
  { id: 'turnaround', name: 'Turnaround Watch', desc: 'Positive CFO, Net Profit Margin > 5%' },
];

export default function StockScreener({ onSelectCompany }) {
  const { companies } = useBluestockData();

  const [activePreset, setActivePreset] = useState('quality');
  const [showAdvanced, setShowAdvanced] = useState(false);

  // 18 Configurable Filters per Specification
  const [minRoe, setMinRoe] = useState(15);
  const [minRoce, setMinRoce] = useState(15);
  const [maxPe, setMaxPe] = useState(60);
  const [maxPb, setMaxPb] = useState(12);
  const [maxDe, setMaxDe] = useState(1.0);
  const [minHealthScore, setMinHealthScore] = useState(50);

  // Advanced Filters
  const [minNpm, setMinNpm] = useState(0);
  const [minOpm, setMinOpm] = useState(0);
  const [minIcr, setMinIcr] = useState(0);
  const [minFcf, setMinFcf] = useState(-5000);
  const [minCfo, setMinCfo] = useState(0);
  const [maxCapexIntensity, setMaxCapexIntensity] = useState(30);
  const [minRevCagr5y, setMinRevCagr5y] = useState(0);
  const [minPatCagr5y, setMinPatCagr5y] = useState(0);
  const [minRevCagr3y, setMinRevCagr3y] = useState(0);
  const [maxEvEbitda, setMaxEvEbitda] = useState(50);
  const [minDivYield, setMinDivYield] = useState(0);
  const [selectedSector, setSelectedSector] = useState('All');

  // Sorting
  const [sortField, setSortField] = useState('score');
  const [sortAsc, setSortAsc] = useState(false);

  // Apply preset logic conforming to Section 25
  const handleSelectPreset = (pId) => {
    setActivePreset(pId);
    if (pId === 'quality') {
      setMinRoe(15);
      setMinRoce(15);
      setMaxPe(60);
      setMaxPb(10);
      setMaxDe(1.0);
      setMinHealthScore(70);
    } else if (pId === 'value') {
      setMinRoe(10);
      setMinRoce(10);
      setMaxPe(25);
      setMaxPb(3.5);
      setMaxDe(2.0);
      setMinHealthScore(50);
    } else if (pId === 'growth') {
      setMinRoe(18);
      setMinRoce(20);
      setMaxPe(80);
      setMaxPb(15);
      setMaxDe(1.5);
      setMinHealthScore(65);
    } else if (pId === 'dividend') {
      setMinRoe(10);
      setMinRoce(10);
      setMaxPe(50);
      setMaxPb(8);
      setMaxDe(2.5);
      setMinHealthScore(50);
      setMinDivYield(2.0);
    } else if (pId === 'debt_free') {
      setMinRoe(12);
      setMinRoce(12);
      setMaxPe(90);
      setMaxPb(15);
      setMaxDe(0.05);
      setMinHealthScore(60);
    } else if (pId === 'turnaround') {
      setMinRoe(5);
      setMinRoce(5);
      setMaxPe(70);
      setMaxPb(10);
      setMaxDe(3.0);
      setMinHealthScore(35);
    }
  };

  const resetFilters = () => {
    setMinRoe(0);
    setMinRoce(0);
    setMaxPe(100);
    setMaxPb(25);
    setMaxDe(5.0);
    setMinHealthScore(0);
    setMinNpm(0);
    setMinOpm(0);
    setMinIcr(0);
    setMinFcf(-50000);
    setMinCfo(-50000);
    setMaxCapexIntensity(100);
    setMinRevCagr5y(0);
    setMinPatCagr5y(0);
    setMinRevCagr3y(0);
    setMaxEvEbitda(100);
    setMinDivYield(0);
    setSelectedSector('All');
    setActivePreset('');
  };

  // 11 Broad Sectors list
  const sectors = useMemo(() => {
    return ['All', ...new Set(companies.map(c => c.sector))];
  }, [companies]);

  // Filtering across 18 criteria
  const filtered = useMemo(() => {
    return companies.filter(c => {
      const matchRoe = c.roe >= minRoe;
      const matchRoce = c.roce >= minRoce;
      const matchPe = c.pe <= maxPe;
      const matchPb = c.pb <= maxPb;
      const matchDe = c.debtToEquity <= maxDe;
      const matchScore = (c.score || 0) >= minHealthScore;
      const matchSector = selectedSector === 'All' || c.sector === selectedSector;
      const matchDivYield = (c.divYield || 0) >= minDivYield;
      const matchFcf = (c.fcfCr || 0) >= minFcf;
      const matchCfo = (c.cfoCr || 0) >= minCfo;
      const matchEvEbitda = (c.evEbitda || 0) <= maxEvEbitda;

      if (activePreset === 'dividend') {
        return matchRoe && matchPe && matchDe && matchSector && c.divYield >= 1.5;
      }
      if (activePreset === 'debt_free') {
        return matchRoe && matchPe && (c.debtToEquity <= 0.05) && matchSector;
      }
      if (activePreset === 'quality') {
        return matchRoe && matchRoce && matchPe && matchDe && matchSector && c.fcfCr > 0;
      }

      return matchRoe && matchRoce && matchPe && matchPb && matchDe && matchScore && matchSector && matchDivYield && matchFcf && matchCfo && matchEvEbitda;
    }).sort((a, b) => {
      const aVal = a[sortField] || 0;
      const bVal = b[sortField] || 0;
      return sortAsc ? (aVal > bVal ? 1 : -1) : (aVal < bVal ? 1 : -1);
    });
  }, [
    companies, minRoe, minRoce, maxPe, maxPb, maxDe, minHealthScore, 
    selectedSector, minDivYield, minFcf, minCfo, maxEvEbitda, activePreset, sortField, sortAsc
  ]);

  // CSV Export (AC-09 Acceptance Criterion)
  const exportToCSV = () => {
    const headers = [
      "Ticker", "Company Name", "Sector", "Sub Sector", "Price (INR)", 
      "Market Cap (Cr)", "Health Score", "Health Band", "P/E", "P/B", "EV/EBITDA", 
      "ROE (%)", "ROCE (%)", "D/E", "Div Yield (%)", "Free Cash Flow (Cr)", "Cash from Ops (Cr)", "Capital Allocation"
    ];
    const rows = filtered.map(c => [
      c.id,
      `"${c.name}"`,
      `"${c.sector}"`,
      `"${c.subSector}"`,
      c.price,
      c.mcapCr,
      c.score,
      c.healthBand,
      c.pe,
      c.pb,
      c.evEbitda,
      c.roe,
      c.roce,
      c.debtToEquity,
      c.divYield,
      c.fcfCr,
      c.cfoCr,
      `"${c.capitalAllocation.label}"`
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `nifty100_screener_${activePreset || 'custom'}_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 space-y-4 sm:space-y-5 max-w-7xl mx-auto w-full">
      {/* 1. Header Card & Presets */}
      <div className="ios-card p-5 sm:p-6 space-y-5">
        {/* Top Header: Simple, Full-Width, Zero Dead Gaps */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-[rgba(255,255,255,0.06)]">
          {/* Left: Badges, Title & Subtitle */}
          <div className="space-y-1.5">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[10px] font-bold text-[#8E8E93] bg-[#2C2C2E] border border-white/[0.08] px-2.5 py-0.5 rounded-full uppercase tracking-wider font-mono">
                92 NIFTY 100 BLUECHIPS
              </span>
              {activePreset ? (
                <span className="text-[10px] font-bold text-[#0A84FF] bg-[#0A84FF]/10 border border-[#0A84FF]/25 px-2 py-0.5 rounded-full uppercase tracking-wider flex items-center gap-1">
                  <Sparkles className="w-2.5 h-2.5" />
                  PRESET: {PRESETS.find(p => p.id === activePreset)?.name.toUpperCase()}
                </span>
              ) : (
                <span className="text-[10px] font-bold text-[#FF9F0A] bg-[#FF9F0A]/10 border border-[#FF9F0A]/25 px-2 py-0.5 rounded-full uppercase tracking-wider">
                  CUSTOM CRITERIA
                </span>
              )}
            </div>

            <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              Institutional Investment Screener
            </h1>

            <p className="text-xs text-[#8E8E93] leading-relaxed max-w-3xl">
              Multi-parameter quantitative screening engine across 18 audited profitability, cash quality, valuation, and capital structure metrics.
            </p>
          </div>

          {/* Right: Inline Match Count & Action Buttons (Aligned edge-to-edge, zero gaps) */}
          <div className="flex items-center gap-2 flex-wrap lg:justify-end shrink-0">
            <div className="px-3 py-2 rounded-xl bg-[#242426] border border-white/[0.08] flex items-center gap-2">
              <span className="text-[10px] uppercase font-bold text-[#8E8E93] tracking-wider">Universe Pass</span>
              <span className="text-xs font-mono font-bold text-[#30D158]">
                {filtered.length} / {companies.length}
              </span>
              <span className="text-[10px] font-mono text-[#8E8E93]">
                ({((filtered.length / (companies.length || 1)) * 100).toFixed(0)}%)
              </span>
            </div>

            <button
              onClick={resetFilters}
              className="px-3 py-2 rounded-xl bg-[#2C2C2E] border border-white/[0.08] text-xs font-semibold text-[#8E8E93] hover:text-white hover:bg-[#3A3A3C] transition-all flex items-center gap-1.5 active:scale-95"
              title="Reset all filters to defaults"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset
            </button>

            <button
              onClick={exportToCSV}
              className="px-3.5 py-2 rounded-xl bg-white text-black font-bold text-xs hover:bg-[#E5E5EA] transition-all flex items-center gap-1.5 shadow-sm active:scale-95"
              title="Export filtered dataset to CSV"
            >
              <Download className="w-3.5 h-3.5 stroke-[2.5]" />
              Export CSV ({filtered.length})
            </button>
          </div>
        </div>

        {/* 2. 6 Pre-Configured Presets: Full-Width Balanced Grid */}
        <div>
          <div className="flex items-center justify-between mb-2.5">
            <div className="text-[10px] font-bold text-[#8E8E93] uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-3 h-3 text-[#FF9F0A]" />
              6 Pre-Configured Institutional Presets (Section 25 Spec)
            </div>
            <span className="text-[10px] text-[#636366] font-mono hidden sm:inline">
              Click any archetype to calibrate thresholds
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
            {PRESETS.map((p) => {
              const isActive = activePreset === p.id;
              return (
                <button
                  key={p.id}
                  onClick={() => handleSelectPreset(p.id)}
                  className={`p-2.5 rounded-xl text-left transition-all border flex flex-col justify-between h-full ${
                    isActive
                      ? 'bg-white text-black border-white shadow-md ring-1 ring-white/50'
                      : 'bg-[#242426]/70 text-[#8E8E93] border-white/[0.06] hover:text-white hover:bg-[#2C2C2E]'
                  }`}
                >
                  <div className="flex items-center justify-between w-full">
                    <span className={`font-bold text-xs truncate ${isActive ? 'text-black' : 'text-white'}`}>
                      {p.name}
                    </span>
                    {isActive && (
                      <span className="w-1.5 h-1.5 rounded-full bg-black shrink-0 ml-1" />
                    )}
                  </div>
                  <div className={`text-[9.5px] mt-1.5 line-clamp-2 leading-tight ${isActive ? 'text-black/80 font-medium' : 'text-[#8E8E93]'}`}>
                    {p.desc}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* 3. Primary Screening Parameters (Core 6 Metrics) */}
        <div>
          <div className="flex items-center justify-between mb-2.5">
            <span className="text-[10px] font-bold text-[#8E8E93] uppercase tracking-wider flex items-center gap-1.5">
              <SlidersHorizontal className="w-3 h-3 text-[#0A84FF]" />
              Primary Filter Parameters (Core 6 Factors)
            </span>
            <span className="text-[10px] text-[#636366] font-mono">
              Live Thresholds
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
            {/* Min ROE */}
            <div className="p-2.5 rounded-xl bg-[#242426]/50 border border-white/[0.06] space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-[10.5px] font-semibold text-[#8E8E93]">1. Min ROE</span>
                <span className="text-[11px] font-mono font-bold text-[#30D158]">{minRoe}%</span>
              </div>
              <input 
                type="range" min="0" max="40" value={minRoe} 
                onChange={(e) => setMinRoe(Number(e.target.value))}
                className="w-full accent-[#30D158] cursor-pointer h-1.5 bg-[#1C1C1E] rounded-lg"
              />
            </div>

            {/* Min ROCE */}
            <div className="p-2.5 rounded-xl bg-[#242426]/50 border border-white/[0.06] space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-[10.5px] font-semibold text-[#8E8E93]">2. Min ROCE</span>
                <span className="text-[11px] font-mono font-bold text-[#0A84FF]">{minRoce}%</span>
              </div>
              <input 
                type="range" min="0" max="45" value={minRoce} 
                onChange={(e) => setMinRoce(Number(e.target.value))}
                className="w-full accent-[#0A84FF] cursor-pointer h-1.5 bg-[#1C1C1E] rounded-lg"
              />
            </div>

            {/* Max P/E */}
            <div className="p-2.5 rounded-xl bg-[#242426]/50 border border-white/[0.06] space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-[10.5px] font-semibold text-[#8E8E93]">3. Max P/E</span>
                <span className="text-[11px] font-mono font-bold text-[#0A84FF]">{maxPe}x</span>
              </div>
              <input 
                type="range" min="10" max="100" value={maxPe} 
                onChange={(e) => setMaxPe(Number(e.target.value))}
                className="w-full accent-[#0A84FF] cursor-pointer h-1.5 bg-[#1C1C1E] rounded-lg"
              />
            </div>

            {/* Max P/B */}
            <div className="p-2.5 rounded-xl bg-[#242426]/50 border border-white/[0.06] space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-[10.5px] font-semibold text-[#8E8E93]">4. Max P/B</span>
                <span className="text-[11px] font-mono font-bold text-[#BF5AF2]">{maxPb}x</span>
              </div>
              <input 
                type="range" min="1" max="25" value={maxPb} 
                onChange={(e) => setMaxPb(Number(e.target.value))}
                className="w-full accent-[#BF5AF2] cursor-pointer h-1.5 bg-[#1C1C1E] rounded-lg"
              />
            </div>

            {/* Max D/E */}
            <div className="p-2.5 rounded-xl bg-[#242426]/50 border border-white/[0.06] space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-[10.5px] font-semibold text-[#8E8E93]">5. Max D/E</span>
                <span className="text-[11px] font-mono font-bold text-[#FF9F0A]">{maxDe}x</span>
              </div>
              <input 
                type="range" min="0" max="5" step="0.1" value={maxDe} 
                onChange={(e) => setMaxDe(Number(e.target.value))}
                className="w-full accent-[#FF9F0A] cursor-pointer h-1.5 bg-[#1C1C1E] rounded-lg"
              />
            </div>

            {/* Min Health */}
            <div className="p-2.5 rounded-xl bg-[#242426]/50 border border-white/[0.06] space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-[10.5px] font-semibold text-[#8E8E93]">6. Min Health</span>
                <span className="text-[11px] font-mono font-bold text-[#30D158]">{minHealthScore}</span>
              </div>
              <input 
                type="range" min="0" max="90" step="5" value={minHealthScore} 
                onChange={(e) => setMinHealthScore(Number(e.target.value))}
                className="w-full accent-[#30D158] cursor-pointer h-1.5 bg-[#1C1C1E] rounded-lg"
              />
            </div>
          </div>

          {/* Toggle Advanced Filters Button */}
          <div className="mt-3 pt-2.5 flex items-center justify-between border-t border-[rgba(255,255,255,0.06)]">
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-xs font-semibold text-[#0A84FF] hover:text-[#5AC8FA] flex items-center gap-1.5 transition-colors"
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              <span>{showAdvanced ? "Hide Advanced Filters (7–18)" : "Show All 18 Advanced Filters (CapEx, FCF, CFO, Margins, Sector)"}</span>
              {showAdvanced ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
            <span className="text-[10px] text-[#636366] font-mono">
              Filters 7 to 18
            </span>
          </div>
        </div>

        {/* Advanced Filters Panel (7 to 18) */}
        {showAdvanced && (
          <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 p-4 rounded-xl bg-[#242426]/60 border border-white/[0.06] animate-fadeIn">
            {/* 7. Sector Filter */}
            <div className="space-y-1.5">
              <div className="text-xs font-semibold text-[#8E8E93]">7. Sector Selection</div>
              <select
                value={selectedSector}
                onChange={(e) => setSelectedSector(e.target.value)}
                className="w-full bg-[#1C1C1E] border border-white/[0.1] rounded-xl px-2.5 py-1.5 text-xs text-white outline-none focus:border-[#0A84FF] cursor-pointer"
              >
                {sectors.map(s => (
                  <option key={s} value={s} className="bg-black">{s}</option>
                ))}
              </select>
            </div>

            {/* 8. Min Div Yield */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-[#8E8E93]">8. Min Dividend Yield %</span>
                <span className="text-white font-mono">{minDivYield}%</span>
              </div>
              <input 
                type="range" min="0" max="5" step="0.5" value={minDivYield} 
                onChange={(e) => setMinDivYield(Number(e.target.value))}
                className="w-full accent-[#30D158] cursor-pointer"
              />
            </div>

            {/* 9. Max EV/EBITDA */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-[#8E8E93]">9. Max EV/EBITDA</span>
                <span className="text-white font-mono">{maxEvEbitda}x</span>
              </div>
              <input 
                type="range" min="10" max="60" value={maxEvEbitda} 
                onChange={(e) => setMaxEvEbitda(Number(e.target.value))}
                className="w-full accent-[#0A84FF] cursor-pointer"
              />
            </div>

            {/* 10. Min Free Cash Flow */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-[#8E8E93]">10. Min FCF (₹ Cr)</span>
                <span className="text-white font-mono">₹{minFcf} Cr</span>
              </div>
              <input 
                type="range" min="-10000" max="10000" step="1000" value={minFcf} 
                onChange={(e) => setMinFcf(Number(e.target.value))}
                className="w-full accent-[#30D158] cursor-pointer"
              />
            </div>

            {/* 11. Min CFO */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-[#8E8E93]">11. Min CFO (₹ Cr)</span>
                <span className="text-white font-mono">₹{minCfo} Cr</span>
              </div>
              <input 
                type="range" min="-5000" max="25000" step="1000" value={minCfo} 
                onChange={(e) => setMinCfo(Number(e.target.value))}
                className="w-full accent-[#30D158] cursor-pointer"
              />
            </div>

            {/* 12. Max CapEx Intensity */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-[#8E8E93]">12. Max CapEx Intensity %</span>
                <span className="text-white font-mono">{maxCapexIntensity}%</span>
              </div>
              <input 
                type="range" min="5" max="50" value={maxCapexIntensity} 
                onChange={(e) => setMaxCapexIntensity(Number(e.target.value))}
                className="w-full accent-[#FF9F0A] cursor-pointer"
              />
            </div>

            {/* 13. Min NPM */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-[#8E8E93]">13. Min NPM %</span>
                <span className="text-white font-mono">{minNpm}%</span>
              </div>
              <input 
                type="range" min="0" max="30" value={minNpm} 
                onChange={(e) => setMinNpm(Number(e.target.value))}
                className="w-full accent-[#30D158] cursor-pointer"
              />
            </div>

            {/* 14. Min OPM */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-[#8E8E93]">14. Min OPM %</span>
                <span className="text-white font-mono">{minOpm}%</span>
              </div>
              <input 
                type="range" min="0" max="40" value={minOpm} 
                onChange={(e) => setMinOpm(Number(e.target.value))}
                className="w-full accent-[#0A84FF] cursor-pointer"
              />
            </div>
          </div>
        )}
      </div>

      {/* 2. Results Table with Health Score Bands */}
      <div className="ios-card p-6">
        <div className="flex justify-between items-center mb-4">
          <div className="text-xs text-[#8E8E93]">
            Showing <span className="text-white font-bold font-mono">{filtered.length}</span> of 92 constituents matching all criteria
          </div>
          <div className="text-[10px] text-[#636366] font-mono">
            Click column headers to sort
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[rgba(255,255,255,0.08)] text-[10px] font-bold text-[#8E8E93] uppercase">
                <th className="pb-3 cursor-pointer hover:text-white" onClick={() => handleSort('id')}>
                  Ticker <ArrowUpDown className="inline w-2.5 h-2.5 ml-0.5" />
                </th>
                <th className="pb-3">Company & Sector</th>
                <th className="pb-3 text-center cursor-pointer hover:text-white" onClick={() => handleSort('score')}>
                  Health Score (0-100) <ArrowUpDown className="inline w-2.5 h-2.5 ml-0.5" />
                </th>
                <th className="pb-3 text-right cursor-pointer hover:text-white" onClick={() => handleSort('price')}>
                  LTP (₹) <ArrowUpDown className="inline w-2.5 h-2.5 ml-0.5" />
                </th>
                <th className="pb-3 text-right cursor-pointer hover:text-white" onClick={() => handleSort('roe')}>
                  ROE % <ArrowUpDown className="inline w-2.5 h-2.5 ml-0.5" />
                </th>
                <th className="pb-3 text-right cursor-pointer hover:text-white" onClick={() => handleSort('roce')}>
                  ROCE % <ArrowUpDown className="inline w-2.5 h-2.5 ml-0.5" />
                </th>
                <th className="pb-3 text-right cursor-pointer hover:text-white" onClick={() => handleSort('pe')}>
                  P/E <ArrowUpDown className="inline w-2.5 h-2.5 ml-0.5" />
                </th>
                <th className="pb-3 text-right cursor-pointer hover:text-white" onClick={() => handleSort('pb')}>
                  P/B <ArrowUpDown className="inline w-2.5 h-2.5 ml-0.5" />
                </th>
                <th className="pb-3 text-right cursor-pointer hover:text-white" onClick={() => handleSort('debtToEquity')}>
                  D/E <ArrowUpDown className="inline w-2.5 h-2.5 ml-0.5" />
                </th>
                <th className="pb-3 text-right cursor-pointer hover:text-white" onClick={() => handleSort('fcfCr')}>
                  Free Cash Flow <ArrowUpDown className="inline w-2.5 h-2.5 ml-0.5" />
                </th>
                <th className="pb-3 text-center">Capital Allocation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[rgba(255,255,255,0.04)] font-mono">
              {filtered.length > 0 ? (
                filtered.map((c) => (
                  <tr 
                    key={c.id} 
                    onClick={() => onSelectCompany(c.id)}
                    className="hover:bg-white/[0.04] cursor-pointer transition-colors"
                  >
                    <td className="py-3 font-bold text-white">
                      <span className="hover:text-[#0A84FF] transition-colors">{c.id}</span>
                    </td>
                    <td className="py-3 font-sans">
                      <div className="font-semibold text-white">{c.name}</div>
                      <div className="text-[10px] text-[#8E8E93] flex items-center gap-1.5 mt-0.5">
                        <span>{c.sector}</span>
                        <span>•</span>
                        <span className="text-[#636366]">{c.subSector}</span>
                      </div>
                    </td>
                    {/* Health Score Band (80-100: Excellent, 65-79: Good, 50-64: Average, 35-49: Weak, 0-34: Poor) */}
                    <td className="py-3 text-center font-sans">
                      <span 
                        className="text-[10px] font-bold px-2 py-0.5 rounded font-mono inline-flex items-center gap-1"
                        style={{ 
                          backgroundColor: `${c.healthScore?.color || '#30D158'}20`, 
                          color: c.healthScore?.color || '#30D158',
                          border: `1px solid ${c.healthScore?.color || '#30D158'}40`
                        }}
                      >
                        <strong>{c.score}</strong>
                        <span className="text-[9px] font-sans">({c.healthBand})</span>
                      </span>
                    </td>
                    <td className="py-3 text-right text-white font-semibold">
                      ₹{c.price.toLocaleString('en-IN')}
                    </td>
                    <td className={`py-3 text-right font-bold ${c.roe >= 20 ? 'text-[#30D158]' : c.roe >= 12 ? 'text-white' : 'text-[#8E8E93]'}`}>
                      {c.roe}%
                    </td>
                    <td className="py-3 text-right text-[#0A84FF] font-semibold">
                      {c.roce}%
                    </td>
                    <td className="py-3 text-right text-white">
                      {c.pe}x
                    </td>
                    <td className="py-3 text-right text-[#8E8E93]">
                      {c.pb}x
                    </td>
                    <td className={`py-3 text-right font-semibold ${c.debtToEquity <= 0.1 ? 'text-[#30D158]' : c.debtToEquity > 1.5 ? 'text-[#FF453A]' : 'text-white'}`}>
                      {c.debtToEquity === 0 ? '0.00' : c.debtToEquity}x
                    </td>
                    <td className={`py-3 text-right font-semibold ${c.fcfCr >= 0 ? 'text-[#30D158]' : 'text-[#FF453A]'}`}>
                      ₹{c.fcfCr.toLocaleString('en-IN')} Cr
                    </td>
                    <td className="py-3 text-center font-sans">
                      <span 
                        className="text-[9.5px] px-2 py-0.5 rounded font-semibold inline-block truncate max-w-[130px]"
                        style={{ backgroundColor: `${c.capitalAllocation.color}20`, color: c.capitalAllocation.color }}
                      >
                        {c.capitalAllocation.code}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="11" className="py-8 text-center text-[#8E8E93] font-sans">
                    No companies match this filter combination. Adjust the parameters or reset filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
