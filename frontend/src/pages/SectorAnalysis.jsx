import React, { useState, useMemo } from 'react';
import { useBluestockData } from '../context/useBluestockData';
import { Globe2, Layers, Building2, TrendingUp, ArrowRight, PieChart } from 'lucide-react';

const SECTOR_BENCHMARKS = {
  "Financials": { roeRange: "12–22%", deRange: "> 5x (Normal)", opmRange: "25–45% NIM", peRange: "12–25x", note: "D/E structurally high — assess NIM + ROA" },
  "Energy": { roeRange: "10–18%", deRange: "0.5–2x", opmRange: "8–18%", peRange: "8–15x", note: "Capital intensive; commodity-linked margins" },
  "Information Technology": { roeRange: "25–50%", deRange: "0–0.3x", opmRange: "20–35%", peRange: "22–40x", note: "Asset-light; high ROE; pristine debt-free balance sheets" },
  "Consumer Discretionary": { roeRange: "10–25%", deRange: "0.3–1.5x", opmRange: "10–20%", peRange: "25–50x", note: "Auto OEMs & consumer retail have diverse margin profiles" },
  "Consumer Staples": { roeRange: "20–45%", deRange: "0–0.5x", opmRange: "15–28%", peRange: "40–70x", note: "Premium multiples, brand moat, resilient cash generation" },
  "Healthcare": { roeRange: "15–30%", deRange: "0–0.8x", opmRange: "15–25%", peRange: "25–45x", note: "R&D pipeline assets; export focus" },
  "Materials": { roeRange: "10–25%", deRange: "0.3–1x", opmRange: "12–22%", peRange: "8–18x", note: "Cyclical global commodity pricing" },
  "Industrials": { roeRange: "12–22%", deRange: "0.3–1.5x", opmRange: "10–20%", peRange: "20–35x", note: "Capex cycle driven; order book backlog sensitivity" },
  "Communication Services": { roeRange: "10–20%", deRange: "1.5–3x", opmRange: "35–50%", peRange: "25–45x", note: "High leverage due to 5G spectrum & towers" },
  "Real Estate": { roeRange: "6–15%", deRange: "0.3–1.2x", opmRange: "20–35%", peRange: "25–50x", note: "Presales momentum and inventory velocity" },
  "Conglomerates": { roeRange: "10–20%", deRange: "0.5–2x", opmRange: "12–25%", peRange: "15–30x", note: "Diversified capital allocation and holding discount" }
};

export default function SectorAnalysis() {
  const { companies, setSelectedTicker } = useBluestockData();
  const [activeSector, setActiveSector] = useState("Financials");

  // Aggregate stats per broad sector
  const sectorAggregates = useMemo(() => {
    const map = {};
    companies.forEach(c => {
      const s = c.sector;
      if (!map[s]) {
        map[s] = {
          name: s,
          companies: [],
          totalWeight: 0,
          roeSum: 0,
          peSum: 0
        };
      }
      map[s].companies.push(c);
      map[s].totalWeight += (c.indexWeight || 1.0);
      map[s].roeSum += (c.roe || 0);
      map[s].peSum += (c.pe || 0);
    });

    return Object.values(map).map(sec => {
      const count = sec.companies.length;
      return {
        ...sec,
        count: count,
        totalWeight: Math.round(sec.totalWeight * 10) / 10,
        avgRoe: Math.round((sec.roeSum / count) * 10) / 10,
        avgPe: Math.round((sec.peSum / count) * 10) / 10,
      };
    }).sort((a, b) => b.totalWeight - a.totalWeight);
  }, [companies]);

  const currentSectorData = sectorAggregates.find(s => s.name === activeSector) || sectorAggregates[0];
  const currentBenchmark = SECTOR_BENCHMARKS[activeSector] || { roeRange: "12–22%", deRange: "< 1.5x", opmRange: "15–25%", peRange: "15–30x", note: "Nifty 100 core constituent" };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto w-full">
      {/* 1. Header Card */}
      <div className="ios-card p-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-bold text-[#8E8E93] bg-[#2C2C2E] border border-white/[0.08] px-2.5 py-0.5 rounded-full uppercase tracking-wider font-mono">
                11 GICS BROAD SECTORS
              </span>
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">Macro Sector Allocation & Industry Weights</h2>
            <p className="text-xs text-[#8E8E93] mt-0.5">
              Constituent distribution, median valuation multiples, and structural return on equity across India's economic sectors.
            </p>
          </div>
        </div>

        {/* Sector Macro Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3.5">
          {sectorAggregates.map((s) => {
            const isSelected = activeSector === s.name;
            return (
              <div
                key={s.name}
                onClick={() => setActiveSector(s.name)}
                className={`p-4 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between ${
                  isSelected
                    ? 'bg-[#2C2C2E] border-[#0A84FF] shadow-lg'
                    : 'bg-[#1C1C1E] border-white/[0.08] hover:border-white/[0.16] hover:bg-white/[0.04]'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-white truncate max-w-[150px]">{s.name}</span>
                    <span className="text-[10px] font-mono text-[#30D158] font-bold bg-[#30D158]/10 px-2 py-0.5 rounded-full">
                      {s.count} Cos
                    </span>
                  </div>
                  <div className="text-2xl font-extrabold text-white font-mono mt-1">
                    {s.totalWeight}% <span className="text-[10px] text-[#8E8E93] font-sans font-normal">Index Wt</span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-[11px] text-[#8E8E93] mt-3 pt-2.5 border-t border-white/[0.06]">
                  <span>Median ROE: <strong className="text-white font-mono">{s.avgRoe}%</strong></span>
                  <span>Avg P/E: <strong className="text-white font-mono">{s.avgPe}x</strong></span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 2. Selected Sector Deep Dive */}
      <div className="ios-card p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-lg font-bold text-white">{activeSector}</span>
              <span className="text-xs text-[#8E8E93]">• {currentSectorData?.count} Constituent Bluechips</span>
            </div>
            <p className="text-xs text-[#8E8E93] max-w-2xl leading-relaxed">
              {currentBenchmark.note}
            </p>
          </div>

          {/* Benchmark Range Pills (Section 28) */}
          <div className="flex items-center gap-2 text-xs flex-wrap">
            <span className="px-2.5 py-1 rounded-xl bg-[#2C2C2E] text-[#8E8E93] border border-white/[0.06]">
              Target ROE: <strong className="text-white">{currentBenchmark.roeRange}</strong>
            </span>
            <span className="px-2.5 py-1 rounded-xl bg-[#2C2C2E] text-[#8E8E93] border border-white/[0.06]">
              Normal D/E: <strong className="text-white">{currentBenchmark.deRange}</strong>
            </span>
            <span className="px-2.5 py-1 rounded-xl bg-[#2C2C2E] text-[#8E8E93] border border-white/[0.06]">
              P/E Range: <strong className="text-white">{currentBenchmark.peRange}</strong>
            </span>
          </div>
        </div>

        {/* Sector Constituents Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-white/[0.08] text-[10px] font-bold text-[#8E8E93] uppercase">
                <th className="pb-3">Ticker</th>
                <th className="pb-3">Company Name</th>
                <th className="pb-3">Sub-Industry</th>
                <th className="pb-3 text-right">LTP (₹)</th>
                <th className="pb-3 text-right">Market Cap (Cr)</th>
                <th className="pb-3 text-right">ROE %</th>
                <th className="pb-3 text-right">P/E</th>
                <th className="pb-3 text-right">D/E</th>
                <th className="pb-3 text-center">Index Weight</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.04] font-mono">
              {currentSectorData?.companies?.map((c) => (
                <tr 
                  key={c.id} 
                  onClick={() => setSelectedTicker(c.id)}
                  className="hover:bg-white/[0.04] cursor-pointer transition-colors"
                >
                  <td className="py-3 font-bold text-white hover:text-[#0A84FF] transition-colors">
                    {c.id}
                  </td>
                  <td className="py-3 font-sans text-white font-medium">
                    {c.name}
                  </td>
                  <td className="py-3 font-sans text-[#8E8E93]">
                    {c.subSector}
                  </td>
                  <td className="py-3 text-right text-white font-semibold">
                    ₹{c.price.toLocaleString('en-IN')}
                  </td>
                  <td className="py-3 text-right text-white">
                    ₹{c.mcap} Cr
                  </td>
                  <td className={`py-3 text-right font-bold ${c.roe >= 20 ? 'text-[#30D158]' : 'text-white'}`}>
                    {c.roe}%
                  </td>
                  <td className="py-3 text-right text-white">
                    {c.pe}x
                  </td>
                  <td className={`py-3 text-right ${c.debtToEquity <= 0.1 ? 'text-[#30D158]' : 'text-white'}`}>
                    {c.debtToEquity}x
                  </td>
                  <td className="py-3 text-center text-[#0A84FF] font-semibold">
                    {c.indexWeight}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
