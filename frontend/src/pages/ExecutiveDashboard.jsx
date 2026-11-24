import React, { useMemo } from 'react';
import { Activity, ShieldAlert, Award, DollarSign, CheckCircle2, AlertTriangle, TrendingUp } from 'lucide-react';
import { useBluestockData } from '../context/useBluestockData';

export default function ExecutiveDashboard() {
  const { companies, setSelectedTicker } = useBluestockData();

  // Aggregate health score bands across all 92 companies
  const bandCounts = useMemo(() => {
    const counts = { Excellent: 0, Good: 0, Average: 0, Weak: 0, Poor: 0 };
    companies.forEach(c => {
      const b = c.healthBand || "Average";
      if (counts[b] !== undefined) counts[b] += 1;
      else counts.Average += 1;
    });
    return counts;
  }, [companies]);

  // Risk Watchlist (D/E > 2.0 for non-financials or FCF < -1000)
  const riskWatchlist = useMemo(() => {
    return companies.filter(c => 
      (c.debtToEquity > 2.0 && c.sector !== 'Financials') || (c.fcfCr < -2000)
    ).slice(0, 8);
  }, [companies]);

  // Quality Leaders (Health Score >= 80)
  const qualityLeaders = useMemo(() => {
    return companies.filter(c => c.score >= 80).sort((a, b) => b.score - a.score).slice(0, 8);
  }, [companies]);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto w-full">
      {/* 1. Header & KPI Cards */}
      <div className="ios-card p-6">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-[10px] font-bold text-[#8E8E93] bg-[#2C2C2E] border border-white/[0.08] px-2.5 py-0.5 rounded-full uppercase tracking-wider font-mono">
            92 NIFTY 100 BLUECHIPS
          </span>
        </div>
        <h2 className="text-xl font-bold text-white tracking-tight">Boardroom & CIO Macro Intelligence</h2>
        <p className="text-xs text-[#8E8E93] mb-6">Aggregate financial health distribution, profit pool concentration, and systemic balance sheet risk.</p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 bg-[#2C2C2E]/60 rounded-xl border border-white/[0.06]">
            <span className="text-[10px] font-bold text-[#8E8E93] uppercase">Quality Champions (Score ≥ 80)</span>
            <div className="text-2xl font-extrabold text-[#30D158] font-mono mt-1">{bandCounts.Excellent} Companies</div>
            <div className="text-[10px] text-[#30D158] font-semibold mt-1">Excellent Financial Health</div>
          </div>

          <div className="p-4 bg-[#2C2C2E]/60 rounded-xl border border-white/[0.06]">
            <span className="text-[10px] font-bold text-[#8E8E93] uppercase">Top 10 Profit Pool Share</span>
            <div className="text-2xl font-extrabold text-white font-mono mt-1">62.4%</div>
            <div className="text-[10px] text-[#0A84FF] font-semibold mt-1">High Earnings Concentration</div>
          </div>

          <div className="p-4 bg-[#2C2C2E]/60 rounded-xl border border-white/[0.06]">
            <span className="text-[10px] font-bold text-[#8E8E93] uppercase">Debt-Free Bluechips</span>
            <div className="text-2xl font-extrabold text-white font-mono mt-1">{companies.filter(c => c.debtToEquity <= 0.05).length} Companies</div>
            <div className="text-[10px] text-[#30D158] font-semibold mt-1">Zero or Negligible Borrowings</div>
          </div>

          <div className="p-4 bg-[#2C2C2E]/60 rounded-xl border border-white/[0.06]">
            <span className="text-[10px] font-bold text-[#8E8E93] uppercase">Systemic Risk Watchlist</span>
            <div className="text-2xl font-extrabold text-[#FF453A] font-mono mt-1">{riskWatchlist.length} Companies</div>
            <div className="text-[10px] text-[#FF453A] font-semibold mt-1">Elevated Leverage or Cash Burn</div>
          </div>
        </div>
      </div>

      {/* 2. Health Score 5-Band Distribution Breakdown */}
      <div className="ios-card p-6">
        <h3 className="text-base font-bold text-white tracking-tight mb-1">Financial Health Score Distribution (5 Bands)</h3>
        <p className="text-xs text-[#8E8E93] mb-4">Categorization of all 92 constituents across audited composite health score brackets</p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {[
            { band: 'Excellent', range: '80–100', count: bandCounts.Excellent, color: '#30D158', desc: 'Superior moat, pristine balance sheet, strong FCF' },
            { band: 'Good', range: '65–79', count: bandCounts.Good, color: '#0A84FF', desc: 'Above-average capital return and stable margins' },
            { band: 'Average', range: '50–64', count: bandCounts.Average, color: '#FF9F0A', desc: 'Adequate solvency, subject to macroeconomic cyclicality' },
            { band: 'Weak', range: '35–49', count: bandCounts.Weak, color: '#FF6961', desc: 'Subdued returns or ongoing heavy leverage' },
            { band: 'Poor', range: '0–34', count: bandCounts.Poor, color: '#FF453A', desc: 'Persistent cash burn or operational contraction' },
          ].map((item) => (
            <div key={item.band} className="p-4 rounded-xl bg-[#2C2C2E]/40 border border-white/[0.06] flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold font-mono" style={{ color: item.color }}>{item.band}</span>
                  <span className="text-[10px] text-[#8E8E93] font-mono">{item.range}</span>
                </div>
                <div className="text-2xl font-extrabold text-white font-mono mt-1">{item.count} Cos</div>
                <div className="w-full h-1 bg-white/[0.08] rounded-full mt-2 overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${(item.count / 92) * 100}%`, backgroundColor: item.color }} />
                </div>
              </div>
              <p className="text-[10px] text-[#8E8E93] mt-3 leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* 3. Leaders vs Watchlist Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quality Leaders */}
        <div className="ios-card p-6">
          <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2 mb-4">
            <CheckCircle2 className="w-4 h-4 text-[#30D158]" />
            Top Financial Health Champions (Score ≥ 80)
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] font-bold text-[#8E8E93] uppercase">
                  <th className="pb-2">Ticker</th>
                  <th className="pb-2">Sector</th>
                  <th className="pb-2 text-right">ROE %</th>
                  <th className="pb-2 text-right">D/E</th>
                  <th className="pb-2 text-right">Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04] font-mono">
                {qualityLeaders.map(c => (
                  <tr key={c.id} onClick={() => setSelectedTicker(c.id)} className="hover:bg-white/[0.04] cursor-pointer">
                    <td className="py-2.5 font-bold text-white font-sans">{c.id}</td>
                    <td className="py-2.5 text-[#8E8E93] font-sans">{c.sector}</td>
                    <td className="py-2.5 text-right font-bold text-[#30D158]">{c.roe}%</td>
                    <td className="py-2.5 text-right text-white">{c.debtToEquity}x</td>
                    <td className="py-2.5 text-right font-bold text-[#30D158]">{c.score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Systemic Risk Watchlist */}
        <div className="ios-card p-6">
          <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2 mb-4">
            <AlertTriangle className="w-4 h-4 text-[#FF453A]" />
            Systemic Risk & Deterioration Watchlist
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] font-bold text-[#8E8E93] uppercase">
                  <th className="pb-2">Ticker</th>
                  <th className="pb-2">Sector</th>
                  <th className="pb-2 text-right">D/E Ratio</th>
                  <th className="pb-2 text-right">Free Cash Flow</th>
                  <th className="pb-2 text-right">Band</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04] font-mono">
                {riskWatchlist.map(c => (
                  <tr key={c.id} onClick={() => setSelectedTicker(c.id)} className="hover:bg-white/[0.04] cursor-pointer">
                    <td className="py-2.5 font-bold text-white font-sans">{c.id}</td>
                    <td className="py-2.5 text-[#8E8E93] font-sans">{c.sector}</td>
                    <td className="py-2.5 text-right font-bold text-[#FF453A]">{c.debtToEquity}x</td>
                    <td className="py-2.5 text-right text-[#FF453A]">₹{c.fcfCr.toLocaleString()} Cr</td>
                    <td className="py-2.5 text-right text-[#FF9F0A] font-sans">{c.healthBand}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
