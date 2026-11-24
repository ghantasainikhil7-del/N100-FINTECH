import React, { useState, useMemo } from 'react';
import { 
  TrendingUp, 
  DollarSign, 
  ShieldCheck, 
  Layers, 
  Sparkles, 
  BarChart2, 
  ArrowRight 
} from 'lucide-react';
import { useBluestockData } from '../context/useBluestockData';
import { RAW_SECTORS_DATA } from '../data/bluestockExtendedData';
import RealtimeStockChart from '../components/RealtimeStockChart';

export default function HomeOverview({ onSelectCompany }) {
  const { companies } = useBluestockData();
  const [timeframe, setTimeframe] = useState('1Y');
  const [marketStatus, setMarketStatus] = useState({
    price: 25318.40,
    change: 284.15,
    changePct: 1.12,
    isPositive: true,
    time: '',
    isHovered: false
  });

  // Compute aggregate stats across all 92 companies
  const stats = useMemo(() => {
    const totalCompanies = companies.length;
    const debtFreeCount = companies.filter(c => c.debtToEquity <= 0.05).length;
    const compoundersCount = companies.filter(c => c.roe >= 20 && c.fcfCr > 0).length;
    
    // Sort ROEs for median
    const sortedRoes = [...companies].map(c => c.roe).sort((a, b) => a - b);
    const medianRoe = sortedRoes[Math.floor(sortedRoes.length / 2)] || 18.2;

    const sortedPes = [...companies].map(c => c.pe).filter(p => p > 0 && p < 150).sort((a, b) => a - b);
    const medianPe = sortedPes[Math.floor(sortedPes.length / 2)] || 24.5;

    return {
      totalCompanies,
      debtFreeCount,
      compoundersCount,
      medianRoe,
      medianPe,
    };
  }, [companies]);

  // Aggregate Sectors
  const sectorList = useMemo(() => {
    const map = {};
    companies.forEach(c => {
      const s = c.sector;
      if (!map[s]) map[s] = { name: s, count: 0, weight: 0, roeSum: 0 };
      map[s].count += 1;
      map[s].weight += (c.indexWeight || 1.0);
      map[s].roeSum += (c.roe || 0);
    });

    return Object.values(map)
      .map(s => ({
        ...s,
        weight: Math.round(s.weight * 10) / 10,
        avgRoe: Math.round((s.roeSum / s.count) * 10) / 10
      }))
      .sort((a, b) => b.weight - a.weight)
      .slice(0, 7);
  }, [companies]);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto w-full">
      {/* 1. Hero Market Banner (Pure Apple OLED Squircle) */}
      <div className="rounded-2xl bg-[#1C1C1E] border border-[rgba(255,255,255,0.08)] p-6 shadow-2xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-[11px] font-bold text-[#30D158] bg-[#30D158]/15 border border-[#30D158]/30 px-2.5 py-0.5 rounded-full flex items-center gap-1.5">
                <span className="pulse-green-dot" /> NIFTY 100 REAL-TIME CONSTITUENTS
              </span>
              <span className="text-xs text-[#636366] font-mono">BSE / NSE AUDITED</span>
            </div>
            <div className="text-3xl font-extrabold text-white tracking-tight flex items-baseline gap-2.5">
              <span>{marketStatus.price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
              <span className={`text-lg font-semibold ${marketStatus.isPositive ? 'text-[#30D158]' : 'text-[#FF453A]'}`}>
                {marketStatus.isPositive ? '+' : ''}{marketStatus.change >= 0 ? marketStatus.change.toFixed(2) : marketStatus.change.toFixed(2)} ({marketStatus.isPositive ? '+' : ''}{marketStatus.changePct}%)
              </span>
              {marketStatus.isHovered && (
                <span className="text-xs text-[#8E8E93] font-mono font-medium">
                  · {marketStatus.time}
                </span>
              )}
            </div>
            <p className="text-xs text-[#8E8E93] max-w-xl mt-1 leading-relaxed">
              Consolidated fundamental intelligence and institutional surveillance across India's premier 92 bluechip corporations.
            </p>
          </div>

          {/* Timeframe Pill Switcher (Classic Apple iOS Segmented Control) */}
          <div className="bg-[#2C2C2E] p-1 rounded-2xl flex items-center gap-1 self-start md:self-auto border border-[rgba(255,255,255,0.06)]">
            {['1D', '1W', '1M', '1Y', '5Y', 'ALL'].map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-3 py-1.5 text-xs font-bold rounded-xl transition-all duration-150 ${
                  timeframe === tf
                    ? 'bg-white text-black shadow-md'
                    : 'text-[#8E8E93] hover:text-white'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>

        {/* Real-Time Interactive Animated Stock Chart */}
        <div className="mt-5 pt-3 border-t border-[rgba(255,255,255,0.06)]">
          <RealtimeStockChart timeframe={timeframe} onUpdatePrice={setMarketStatus} />
        </div>
      </div>

      {/* 2. Six Institutional KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
        {[
          { label: 'Total Index Mcap', value: '₹248.6T', sub: `${stats.totalCompanies} Audited Cos`, icon: DollarSign, badge: '+12.4% YoY' },
          { label: 'Median ROE', value: `${stats.medianRoe}%`, sub: 'Top Quartile 24.2%', icon: TrendingUp, badge: 'Robust' },
          { label: 'Debt Free Leaders', value: `${stats.debtFreeCount} Cos`, sub: 'D/E ≤ 0.05x', icon: ShieldCheck, badge: 'Pristine B/S' },
          { label: 'Quality Compounders', value: `${stats.compoundersCount} Cos`, sub: 'ROE>20% + FCF>0', icon: Sparkles, badge: 'High Moat' },
          { label: 'Average Median P/E', value: `${stats.medianPe}x`, sub: 'Historical 22.4x', icon: BarChart2, badge: 'Fair Value' },
          { label: 'Index Dividend Yield', value: '1.38%', sub: '₹48,200 Cr Dist.', icon: Layers, badge: '+8.5% YoY' },
        ].map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div key={idx} className="ios-card p-4 flex flex-col justify-between">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-bold text-[#8E8E93] uppercase tracking-wider">{kpi.label}</span>
                <div className="w-6 h-6 rounded-lg bg-[#2C2C2E] flex items-center justify-center text-[#8E8E93]">
                  <Icon className="w-3.5 h-3.5" />
                </div>
              </div>
              <div>
                <div className="text-xl font-extrabold text-white tracking-tight">{kpi.value}</div>
                <div className="text-[10px] text-[#8E8E93] mt-0.5">{kpi.sub}</div>
              </div>
              <div className="mt-3 pt-2 border-t border-[rgba(255,255,255,0.06)] flex items-center justify-between">
                <span className="text-[9.5px] font-bold px-1.5 py-0.5 rounded bg-[#30D158]/15 text-[#30D158]">
                  {kpi.badge}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* 3. Constituent Performance List & Sector Allocation */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Table of all 92 companies */}
        <div className="lg:col-span-2 ios-card p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-white tracking-tight">Active Bluechip Constituents</h3>
              <p className="text-xs text-[#8E8E93]">Live trading prices, fundamental multiples, and capital efficiency.</p>
            </div>
            <span className="text-xs text-[#8E8E93] font-mono">{companies.length} Records</span>
          </div>

          <div className="overflow-x-auto max-h-[520px]">
            <table className="w-full text-left text-xs">
              <thead className="sticky top-0 bg-[#1C1C1E] z-10">
                <tr className="border-b border-[rgba(255,255,255,0.08)] text-[10px] font-bold text-[#8E8E93] uppercase tracking-wider">
                  <th className="pb-2.5 font-semibold">Ticker & Company</th>
                  <th className="pb-2.5 font-semibold">Sector</th>
                  <th className="pb-2.5 font-semibold text-right">LTP (₹)</th>
                  <th className="pb-2.5 font-semibold text-right">Change</th>
                  <th className="pb-2.5 font-semibold text-right">P/E</th>
                  <th className="pb-2.5 font-semibold text-right">ROE %</th>
                  <th className="pb-2.5 font-semibold text-center">Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[rgba(255,255,255,0.04)] font-mono">
                {companies.map((co) => (
                  <tr 
                    key={co.id} 
                    onClick={() => onSelectCompany(co.id)}
                    className="hover:bg-white/[0.04] cursor-pointer transition-colors group"
                  >
                    <td className="py-2.5 font-sans">
                      <div className="font-bold text-white group-hover:text-[#0A84FF] transition-colors">{co.id}</div>
                      <div className="text-[10px] text-[#8E8E93] truncate max-w-[150px]">{co.name}</div>
                    </td>
                    <td className="py-2.5 text-[#8E8E93] text-[11px] font-sans">{co.sector}</td>
                    <td className="py-2.5 text-right font-semibold text-white">
                      ₹{co.price.toLocaleString('en-IN')}
                    </td>
                    <td className="py-2.5 text-right font-bold">
                      <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10.5px] ${
                        co.isPositive ? 'bg-[#30D158]/15 text-[#30D158]' : 'bg-[#FF453A]/15 text-[#FF453A]'
                      }`}>
                        {co.change}
                      </span>
                    </td>
                    <td className="py-2.5 text-right text-[#8E8E93]">{co.pe}x</td>
                    <td className="py-2.5 text-right text-[#30D158] font-bold">{co.roe}%</td>
                    <td className="py-2.5 text-center font-sans">
                      <span 
                        className="text-[10px] font-bold px-2 py-0.5 rounded font-mono"
                        style={{ 
                          backgroundColor: `${co.healthScore?.color || '#30D158'}20`, 
                          color: co.healthScore?.color || '#30D158',
                          border: `1px solid ${co.healthScore?.color || '#30D158'}40`
                        }}
                      >
                        {co.score} · {co.healthBand}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Sector Allocation Breakdown */}
        <div className="ios-card p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-white tracking-tight">Sector Weights</h3>
                <p className="text-xs text-[#8E8E93]">Macro constituent distribution</p>
              </div>
              <span className="text-[10.5px] font-bold text-[#30D158] bg-[#30D158]/15 px-2 py-0.5 rounded">
                11 GICS Sectors
              </span>
            </div>

            <div className="space-y-3">
              {sectorList.map((s) => (
                <div key={s.name} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-white">{s.name}</span>
                    <span className="font-mono text-[#8E8E93]">{s.weight}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-[#2C2C2E] rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-[#30D158] rounded-full"
                      style={{ width: `${Math.min(100, s.weight * 2.5)}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-[10px] text-[#636366]">
                    <span>{s.count} Bluechips</span>
                    <span className="text-[#30D158] font-semibold">Avg ROE {s.avgRoe}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-3 bg-[#2C2C2E] rounded-2xl mt-4 border border-[rgba(255,255,255,0.06)]">
            <div className="text-[10px] text-[#8E8E93] font-semibold uppercase tracking-wider mb-1">
              PORTFOLIO SURVEILLANCE
            </div>
            <div className="text-xs text-white font-medium">
              Financials and IT command ~49% of aggregate index weight with superior free cash conversion.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
