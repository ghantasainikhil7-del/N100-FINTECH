import React, { useState, useMemo } from 'react';
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, Tooltip } from 'recharts';
import { useBluestockData } from '../context/useBluestockData';
import { RAW_PEER_GROUPS_DATA } from '../data/bluestockExtendedData';
import { Award, TrendingUp, BarChart3, ArrowRight } from 'lucide-react';

const PEER_GROUPS = [
  { name: "Private Banks", benchmark: "HDFCBANK" },
  { name: "Public Sector Banks", benchmark: "SBIN" },
  { name: "IT Services", benchmark: "TCS" },
  { name: "Pharmaceuticals", benchmark: "SUNPHARMA" },
  { name: "Automobiles", benchmark: "MARUTI" },
  { name: "Life Insurance", benchmark: "LICI" },
  { name: "Oil & Gas", benchmark: "RELIANCE" },
  { name: "Power & Utilities", benchmark: "NTPC" },
  { name: "Steel", benchmark: "TATASTEEL" },
  { name: "FMCG", benchmark: "HINDUNILVR" },
  { name: "Consumer Finance", benchmark: "BAJFINANCE" },
];

export default function PeerComparison() {
  const { companies } = useBluestockData();
  const [selectedGroup, setSelectedGroup] = useState("IT Services");

  const currentGroupMeta = PEER_GROUPS.find(g => g.name === selectedGroup) || PEER_GROUPS[2];
  
  // Cohort members
  const cohortMembers = useMemo(() => {
    const memberEntries = RAW_PEER_GROUPS_DATA.filter(p => p.peer_group_name === selectedGroup);
    return memberEntries.map(m => {
      const comp = companies.find(c => c.id === m.company_id) || {
        id: m.company_id,
        name: m.company_id,
        roe: 18,
        roce: 20,
        pe: 25,
        pb: 3.5,
        debtToEquity: 0.1,
        fcfCr: 1500,
        divYield: 1.2
      };
      return {
        ...comp,
        isBenchmark: m.is_benchmark
      };
    });
  }, [selectedGroup, companies]);

  // Selected companies for duel (default benchmark vs second member)
  const [compAId, setCompAId] = useState(currentGroupMeta.benchmark);
  const [compBId, setCompBId] = useState(cohortMembers.find(c => !c.isBenchmark)?.id || cohortMembers[0]?.id || "INFY");

  // Synchronize duel tickers when peer group changes
  React.useEffect(() => {
    setCompAId(currentGroupMeta.benchmark);
    const nonBench = cohortMembers.find(c => !c.isBenchmark);
    setCompBId(nonBench ? nonBench.id : cohortMembers[0]?.id || "INFY");
  }, [selectedGroup]);

  const compA = companies.find(c => c.id === compAId) || cohortMembers[0];
  const compB = companies.find(c => c.id === compBId) || cohortMembers[1] || cohortMembers[0];

  const radarData = [
    { subject: 'ROE %', [compA?.id || 'A']: compA?.roe || 15, [compB?.id || 'B']: compB?.roe || 15 },
    { subject: 'ROCE %', [compA?.id || 'A']: compA?.roce || 18, [compB?.id || 'B']: compB?.roce || 18 },
    { subject: 'P/E multiple', [compA?.id || 'A']: Math.min(compA?.pe || 25, 60), [compB?.id || 'B']: Math.min(compB?.pe || 25, 60) },
    { subject: 'P/B multiple', [compA?.id || 'A']: (compA?.pb || 3) * 5, [compB?.id || 'B']: (compB?.pb || 3) * 5 },
    { subject: 'Div Yield %', [compA?.id || 'A']: (compA?.divYield || 1) * 10, [compB?.id || 'B']: (compB?.divYield || 1) * 10 },
    { subject: 'Capital Health', [compA?.id || 'A']: Math.max(0, 50 - (compA?.debtToEquity || 0) * 20), [compB?.id || 'B']: Math.max(0, 50 - (compB?.debtToEquity || 0) * 20) },
  ];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto w-full">
      {/* 1. Header Card & Peer Group Switcher */}
      <div className="ios-card p-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-5">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-bold text-[#8E8E93] bg-[#2C2C2E] border border-white/[0.08] px-2.5 py-0.5 rounded-full uppercase tracking-wider font-mono">
                11 DESIGNATED SECTOR COHORTS
              </span>
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">Competitive Industry Benchmarking</h2>
            <p className="text-xs text-[#8E8E93] mt-0.5">
              Multi-axis polar radar duels and relative percentile ranking against designated sector benchmarks.
            </p>
          </div>

          {/* Group Selector */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-[#8E8E93]">Select Peer Cohort:</span>
            <select
              value={selectedGroup}
              onChange={(e) => setSelectedGroup(e.target.value)}
              className="bg-[#2C2C2E] border border-white/[0.12] rounded-xl px-3 py-1.5 text-xs text-white font-semibold outline-none focus:border-[#0A84FF] cursor-pointer"
            >
              {PEER_GROUPS.map(g => (
                <option key={g.name} value={g.name} className="bg-black">
                  {g.name} (Benchmark: {g.benchmark})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* 11 Cohort Quick Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-2 scrollbar-none">
          {PEER_GROUPS.map((g) => {
            const isActive = selectedGroup === g.name;
            return (
              <button
                key={g.name}
                onClick={() => setSelectedGroup(g.name)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-white text-black font-bold shadow-md'
                    : 'bg-[#2C2C2E]/60 text-[#8E8E93] hover:text-white hover:bg-[#2C2C2E]'
                }`}
              >
                {g.name}
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. Polar Radar Comparison Duel */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Radar Chart */}
        <div className="ios-card p-6 flex flex-col justify-between">
          <div>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
              <div>
                <h3 className="text-base font-bold text-white tracking-tight">6-Axis Polar Duel</h3>
                <p className="text-xs text-[#8E8E93]">Relative operational efficiency and multiple premium</p>
              </div>

              {/* Company Selectors */}
              <div className="flex items-center gap-2">
                <select
                  value={compAId}
                  onChange={(e) => setCompAId(e.target.value)}
                  className="bg-[#2C2C2E] border border-[#30D158]/50 text-[#30D158] text-xs font-bold rounded-lg px-2 py-1 outline-none cursor-pointer"
                >
                  {cohortMembers.map(c => (
                    <option key={c.id} value={c.id} className="bg-black text-white">{c.id} {c.isBenchmark ? '★' : ''}</option>
                  ))}
                </select>
                <span className="text-xs text-[#636366]">vs</span>
                <select
                  value={compBId}
                  onChange={(e) => setCompBId(e.target.value)}
                  className="bg-[#2C2C2E] border border-[#0A84FF]/50 text-[#0A84FF] text-xs font-bold rounded-lg px-2 py-1 outline-none cursor-pointer"
                >
                  {cohortMembers.map(c => (
                    <option key={c.id} value={c.id} className="bg-black text-white">{c.id} {c.isBenchmark ? '★' : ''}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid stroke="rgba(255,255,255,0.08)" />
                  <PolarAngleAxis dataKey="subject" stroke="#8E8E93" fontSize={11} />
                  <PolarRadiusAxis stroke="rgba(255,255,255,0.08)" fontSize={10} tick={false} />
                  <Radar name={compA?.id || 'A'} dataKey={compA?.id || 'A'} stroke="#30D158" fill="#30D158" fillOpacity={0.25} />
                  <Radar name={compB?.id || 'B'} dataKey={compB?.id || 'B'} stroke="#0A84FF" fill="#0A84FF" fillOpacity={0.25} />
                  <Tooltip contentStyle={{ background: '#1C1C1E', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px', fontSize: '11px', color: '#fff' }} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="p-3 bg-[#2C2C2E]/60 rounded-xl border border-white/[0.04] text-xs text-[#8E8E93] mt-2">
            <span className="text-white font-bold">{compA?.id}</span> maintains a {compA?.roe > (compB?.roe || 0) ? 'higher' : 'lower'} ROE of {compA?.roe}% compared to {compB?.id} ({compB?.roe}%), with a D/E ratio of {compA?.debtToEquity}x.
          </div>
        </div>

        {/* Head-to-Head Comparison Table */}
        <div className="ios-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-white tracking-tight">Direct Metric Comparison</h3>
            <span className="text-xs text-[#8E8E93]">Cohort Benchmark: <strong className="text-[#30D158]">{currentGroupMeta.benchmark}</strong></span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] font-bold text-[#8E8E93] uppercase">
                  <th className="pb-2 text-left">Metric</th>
                  <th className="pb-2 text-right text-[#30D158] font-bold">{compA?.id}</th>
                  <th className="pb-2 text-right text-[#0A84FF] font-bold">{compB?.id}</th>
                  <th className="pb-2 text-right text-[#8E8E93]">Variance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04] font-mono">
                {[
                  { label: "Return on Equity (ROE)", a: `${compA?.roe}%`, b: `${compB?.roe}%`, diff: (compA?.roe || 0) - (compB?.roe || 0), unit: '%' },
                  { label: "Return on Capital (ROCE)", a: `${compA?.roce}%`, b: `${compB?.roce}%`, diff: (compA?.roce || 0) - (compB?.roce || 0), unit: '%' },
                  { label: "P/E Multiple", a: `${compA?.pe}x`, b: `${compB?.pe}x`, diff: (compA?.pe || 0) - (compB?.pe || 0), unit: 'x' },
                  { label: "P/B Ratio", a: `${compA?.pb}x`, b: `${compB?.pb}x`, diff: (compA?.pb || 0) - (compB?.pb || 0), unit: 'x' },
                  { label: "Debt-to-Equity", a: `${compA?.debtToEquity}x`, b: `${compB?.debtToEquity}x`, diff: (compA?.debtToEquity || 0) - (compB?.debtToEquity || 0), unit: 'x', reverse: true },
                  { label: "Free Cash Flow (Cr)", a: `₹${compA?.fcfCr?.toLocaleString()} Cr`, b: `₹${compB?.fcfCr?.toLocaleString()} Cr`, diff: (compA?.fcfCr || 0) - (compB?.fcfCr || 0), unit: ' Cr' },
                  { label: "Dividend Yield", a: `${compA?.divYield}%`, b: `${compB?.divYield}%`, diff: (compA?.divYield || 0) - (compB?.divYield || 0), unit: '%' }
                ].map((row, i) => {
                  const isPositive = row.reverse ? row.diff < 0 : row.diff > 0;
                  return (
                    <tr key={i} className="hover:bg-white/[0.03]">
                      <td className="py-2.5 font-sans font-medium text-white">{row.label}</td>
                      <td className="py-2.5 text-right font-bold text-white">{row.a}</td>
                      <td className="py-2.5 text-right font-bold text-white">{row.b}</td>
                      <td className={`py-2.5 text-right font-bold ${isPositive ? 'text-[#30D158]' : 'text-[#FF453A]'}`}>
                        {row.diff > 0 ? `+${Math.round(row.diff * 10) / 10}` : Math.round(row.diff * 10) / 10}{row.unit}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* 3. Entire Cohort Benchmark Table (Section 6.5) */}
      <div className="ios-card p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <Award className="w-4 h-4 text-[#30D158]" />
              {selectedGroup} Cohort League Table
            </h3>
            <p className="text-xs text-[#8E8E93] mt-0.5">
              Constituents ranked within cohort. Designated benchmark highlighted in signal green.
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-white/[0.08] text-[10px] font-bold text-[#8E8E93] uppercase">
                <th className="pb-3">Constituent</th>
                <th className="pb-3">Sub-Sector</th>
                <th className="pb-3 text-right">LTP (₹)</th>
                <th className="pb-3 text-right">Market Cap</th>
                <th className="pb-3 text-right">ROE %</th>
                <th className="pb-3 text-right">ROCE %</th>
                <th className="pb-3 text-right">P/E</th>
                <th className="pb-3 text-right">P/B</th>
                <th className="pb-3 text-right">D/E</th>
                <th className="pb-3 text-center">Benchmark Role</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.04] font-mono">
              {cohortMembers.map((c) => (
                <tr key={c.id} className={`hover:bg-white/[0.04] transition-colors ${c.isBenchmark ? 'bg-[#30D158]/5' : ''}`}>
                  <td className="py-3 font-sans">
                    <div className="font-bold text-white flex items-center gap-1.5">
                      <span>{c.id}</span>
                      {c.isBenchmark && <span className="text-[#30D158] text-[10px]">★</span>}
                    </div>
                    <div className="text-[10px] text-[#8E8E93] font-normal">{c.name}</div>
                  </td>
                  <td className="py-3 font-sans text-[#8E8E93]">{c.subSector}</td>
                  <td className="py-3 text-right text-white font-semibold">₹{c.price.toLocaleString('en-IN')}</td>
                  <td className="py-3 text-right text-white">₹{c.mcap} Cr</td>
                  <td className={`py-3 text-right font-bold ${c.roe >= 20 ? 'text-[#30D158]' : 'text-white'}`}>{c.roe}%</td>
                  <td className="py-3 text-right text-[#0A84FF] font-semibold">{c.roce}%</td>
                  <td className="py-3 text-right text-white">{c.pe}x</td>
                  <td className="py-3 text-right text-[#8E8E93]">{c.pb}x</td>
                  <td className={`py-3 text-right ${c.debtToEquity <= 0.1 ? 'text-[#30D158]' : 'text-white'}`}>{c.debtToEquity}x</td>
                  <td className="py-3 text-center font-sans">
                    {c.isBenchmark ? (
                      <span className="text-[10px] font-bold text-[#30D158] bg-[#30D158]/15 border border-[#30D158]/30 px-2 py-0.5 rounded-full uppercase">
                        ★ Benchmark
                      </span>
                    ) : (
                      <span className="text-[10px] font-semibold text-[#8E8E93] bg-[#2C2C2E] px-2 py-0.5 rounded-full">
                        Peer Member
                      </span>
                    )}
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
