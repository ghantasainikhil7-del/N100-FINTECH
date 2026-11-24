import React, { useState, useMemo } from 'react';
import { useBluestockData } from '../context/useBluestockData';
import { PieChart, ArrowUpRight, CheckCircle2, TrendingUp, AlertTriangle, ShieldCheck } from 'lucide-react';

const PATTERN_DEFINITIONS = [
  {
    code: "REINVEST_RETURN",
    name: "Organic Compounder & Deleveraging",
    signs: "CFO > 0, CFI < 0, CFF < 0",
    desc: "The gold standard. Operating cash generated is sufficient to fund internal organic CapEx, retire debt, and return dividends simultaneously without reliance on external borrowing.",
    color: "#30D158",
    badge: "Compounder"
  },
  {
    code: "GROWTH_LEVERAGED",
    name: "Aggressive Expansion (Debt/Equity Funded)",
    signs: "CFO > 0, CFI < 0, CFF > 0",
    desc: "Aggressive capacity expansion. Operational cash is augmented by debt or equity capital to finance large-scale Greenfield CapEx or strategic corporate acquisitions.",
    color: "#0A84FF",
    badge: "Aggressive Growth"
  },
  {
    code: "DIVEST_RETURN",
    name: "Divestiture & Capital Return",
    signs: "CFO > 0, CFI > 0, CFF < 0",
    desc: "Mature or restructuring corporations liquidating investments or non-core assets to pay down legacy borrowings or distribute special dividends.",
    color: "#BF5AF2",
    badge: "Capital Return"
  },
  {
    code: "EARLY_STAGE_BURNING",
    name: "Early Stage / Intensive CapEx",
    signs: "CFO < 0, CFI < 0, CFF > 0",
    desc: "Capital-intensive expansion phase where operating activity has not yet reached cash breakeven, requiring external financing rounds.",
    color: "#FF9F0A",
    badge: "CapEx Heavy"
  },
  {
    code: "OPERATIONAL_DISTRESS",
    name: "Operational Distress / Survival Capital",
    signs: "CFO < 0, CFF > 0",
    desc: "Red flag: Core operations burning cash, relying on emergency debt issuance or equity dilution to service working capital obligations.",
    color: "#FF453A",
    badge: "High Risk"
  },
  {
    code: "BALANCED_CAPITAL",
    name: "Prudent Operational Reinvestment",
    signs: "Balanced cash conversion",
    desc: "Steady cash flows with disciplined CapEx deployment aligned with depreciation schedules.",
    color: "#8E8E93",
    badge: "Steady State"
  }
];

export default function CapitalAllocation() {
  const { companies, setSelectedTicker } = useBluestockData();
  const [selectedPattern, setSelectedPattern] = useState("REINVEST_RETURN");

  // Group companies by capital allocation code
  const patternCounts = useMemo(() => {
    const map = {};
    PATTERN_DEFINITIONS.forEach(p => { map[p.code] = []; });

    companies.forEach(c => {
      const code = c.capitalAllocation?.code || "BALANCED_CAPITAL";
      if (!map[code]) map[code] = [];
      map[code].push(c);
    });

    return map;
  }, [companies]);

  const activePatternMeta = PATTERN_DEFINITIONS.find(p => p.code === selectedPattern) || PATTERN_DEFINITIONS[0];
  const matchingCompanies = patternCounts[selectedPattern] || [];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto w-full">
      {/* 1. Header Card */}
      <div className="ios-card p-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-bold text-[#8E8E93] bg-[#2C2C2E] border border-white/[0.08] px-2.5 py-0.5 rounded-full uppercase tracking-wider font-mono">
                8-PATTERN TAXONOMY (SECTION 7.7)
              </span>
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">Capital Allocation Matrix & Cash Dynamics</h2>
            <p className="text-xs text-[#8E8E93] mt-0.5">
              Behavioral taxonomy categorizing how constituents deploy core operating cash across internal CapEx, debt repayment, and shareholder returns.
            </p>
          </div>
        </div>

        {/* 6 Category Selection Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {PATTERN_DEFINITIONS.map((p) => {
            const count = patternCounts[p.code]?.length || 0;
            const isSelected = selectedPattern === p.code;

            return (
              <div
                key={p.code}
                onClick={() => setSelectedPattern(p.code)}
                className={`p-4 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between ${
                  isSelected
                    ? 'bg-[#2C2C2E] border-white shadow-lg'
                    : 'bg-[#1C1C1E] border-white/[0.08] hover:border-white/[0.16] hover:bg-white/[0.04]'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span 
                      className="text-[10px] font-bold px-2 py-0.5 rounded uppercase font-mono tracking-wider"
                      style={{ backgroundColor: `${p.color}20`, color: p.color }}
                    >
                      {p.badge}
                    </span>
                    <span className="text-xs font-mono font-bold text-white">
                      {count} Bluechips
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-white mb-1">{p.name}</h3>
                  <div className="text-[10px] text-[#8E8E93] font-mono mb-2">{p.signs}</div>
                  <p className="text-xs text-[#8E8E93] leading-relaxed line-clamp-3">
                    {p.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 2. Companies in Selected Category */}
      <div className="ios-card p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <div>
            <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: activePatternMeta.color }} />
              {activePatternMeta.name} ({matchingCompanies.length} Constituents)
            </h3>
            <p className="text-xs text-[#8E8E93] mt-0.5">
              Audited cash flow deployment matching {activePatternMeta.signs}
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-white/[0.08] text-[10px] font-bold text-[#8E8E93] uppercase">
                <th className="pb-3">Constituent</th>
                <th className="pb-3">Sector</th>
                <th className="pb-3 text-right">LTP (₹)</th>
                <th className="pb-3 text-right">Cash from Ops (₹ Cr)</th>
                <th className="pb-3 text-right">CapEx (₹ Cr)</th>
                <th className="pb-3 text-right">Free Cash Flow (₹ Cr)</th>
                <th className="pb-3 text-right">D/E Ratio</th>
                <th className="pb-3 text-right">ROE %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.04] font-mono">
              {matchingCompanies.length > 0 ? (
                matchingCompanies.map((c) => (
                  <tr 
                    key={c.id} 
                    onClick={() => setSelectedTicker(c.id)}
                    className="hover:bg-white/[0.04] cursor-pointer transition-colors"
                  >
                    <td className="py-3 font-bold text-white hover:text-[#0A84FF] transition-colors">
                      {c.id}
                      <span className="block text-[10px] font-normal text-[#8E8E93] font-sans">{c.name}</span>
                    </td>
                    <td className="py-3 font-sans text-[#8E8E93]">{c.sector}</td>
                    <td className="py-3 text-right text-white font-semibold">₹{c.price.toLocaleString('en-IN')}</td>
                    <td className={`py-3 text-right font-bold ${c.cfoCr >= 0 ? 'text-[#30D158]' : 'text-[#FF453A]'}`}>
                      ₹{c.cfoCr.toLocaleString('en-IN')} Cr
                    </td>
                    <td className="py-3 text-right text-[#8E8E93]">
                      ₹{c.capexCr.toLocaleString('en-IN')} Cr
                    </td>
                    <td className={`py-3 text-right font-bold ${c.fcfCr >= 0 ? 'text-[#30D158]' : 'text-[#FF453A]'}`}>
                      ₹{c.fcfCr.toLocaleString('en-IN')} Cr
                    </td>
                    <td className={`py-3 text-right ${c.debtToEquity <= 0.1 ? 'text-[#30D158]' : 'text-white'}`}>
                      {c.debtToEquity}x
                    </td>
                    <td className={`py-3 text-right font-bold ${c.roe >= 20 ? 'text-[#30D158]' : 'text-white'}`}>
                      {c.roe}%
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="8" className="py-8 text-center text-[#8E8E93] font-sans">
                    No constituent currently categorised in this specific capital pattern.
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
