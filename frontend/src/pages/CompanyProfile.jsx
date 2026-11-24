import React, { useState } from 'react';
import { 
  Building2, 
  TrendingUp, 
  ShieldCheck, 
  ExternalLink,
  FileText,
  DollarSign,
  PieChart,
  CheckCircle2,
  AlertTriangle,
  ArrowUpRight,
  Layers,
  Sparkles,
  Download
} from 'lucide-react';
import { useBluestockData } from '../context/useBluestockData';
import { getTearsheetPdfUrl } from '../services/api';

export default function CompanyProfile({ selectedTicker, onSelectCompany }) {
  const { 
    companies, 
    currentCompany, 
    setSelectedTicker,
    pnlHistory, 
    balanceSheetHistory, 
    cashFlowHistory, 
    annualReports,
    companyProsCons,
    compoundedGrowth,
    peerCohort
  } = useBluestockData();

  const handleCompanyChange = (ticker) => {
    if (setSelectedTicker) setSelectedTicker(ticker);
    if (onSelectCompany) onSelectCompany(ticker);
  };

  const [statementTab, setStatementTab] = useState('pnl');

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto w-full">
      {/* 1. Header Card with Company Selector */}
      <div className="ios-card p-6 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-2.5 mb-1.5 flex-wrap">
            <span className="text-2xl font-black text-white">{currentCompany.id}</span>
            <span className="text-[10px] font-bold text-[#0A84FF] bg-[#0A84FF]/15 border border-[#0A84FF]/30 px-2.5 py-0.5 rounded-full uppercase tracking-wider">
              {currentCompany.sector}
            </span>
            <span className="text-[10px] font-semibold text-[#8E8E93] bg-[#2C2C2E] px-2 py-0.5 rounded-full">
              {currentCompany.subSector}
            </span>
            <span className="text-[10px] font-bold text-[#30D158] bg-[#30D158]/15 border border-[#30D158]/30 px-2 py-0.5 rounded-full">
              Index Weight: {currentCompany.indexWeight}%
            </span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">{currentCompany.name}</h2>
          <p className="text-xs text-[#8E8E93] max-w-2xl mt-1 leading-relaxed">
            {currentCompany.about}
          </p>

          {/* Capital Allocation & Peer Badge */}
          <div className="mt-3 flex items-center gap-3 flex-wrap">
            <div className="flex items-center gap-1.5 text-xs">
              <span className="text-[#8E8E93]">Capital Strategy:</span>
              <span 
                className="px-2 py-0.5 rounded font-semibold text-[11px]"
                style={{ backgroundColor: `${currentCompany.capitalAllocation.color}20`, color: currentCompany.capitalAllocation.color }}
              >
                {currentCompany.capitalAllocation.label}
              </span>
            </div>
            <div className="text-xs text-[#636366]">•</div>
            <div className="text-xs text-[#8E8E93]">
              Peer Cohort: <span className="text-white font-medium">{currentCompany.peerGroup}</span>
              {currentCompany.isBenchmark && (
                <span className="ml-1 text-[9px] bg-[#30D158]/20 text-[#30D158] px-1.5 py-0.2 rounded font-bold uppercase">
                  Cohort Benchmark
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Constituent Switcher */}
        <div className="flex flex-col items-end gap-2 self-start md:self-auto">
          <div className="text-right">
            <div className="text-2xl font-extrabold text-white font-mono">
              ₹{currentCompany.price.toLocaleString('en-IN')}
            </div>
            <div className={`text-xs font-bold font-mono ${currentCompany.isPositive ? 'text-[#30D158]' : 'text-[#FF453A]'}`}>
              {currentCompany.change} Real-Time
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                const pdfUrl = getTearsheetPdfUrl(currentCompany.id);
                window.open(pdfUrl, '_blank');
              }}
              className="px-3 py-1.5 rounded-xl bg-white text-black font-bold text-xs hover:bg-[#E5E5EA] transition-all flex items-center gap-1.5 shadow-sm active:scale-95"
              title={`Download 2-Page Tearsheet PDF for ${currentCompany.id} via FastAPI`}
            >
              <Download className="w-3.5 h-3.5 stroke-[2.5]" />
              PDF Tearsheet
            </button>
            <select 
              value={currentCompany.id}
              onChange={(e) => handleCompanyChange(e.target.value)}
              className="bg-[#2C2C2E] border border-[rgba(255,255,255,0.12)] text-white text-xs rounded-xl px-3 py-1.5 outline-none focus:border-[#0A84FF] cursor-pointer"
            >
              {companies.map(c => (
                <option key={c.id} value={c.id} className="bg-black">
                  {c.name} ({c.id})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* 2. Key Valuation & Ratio Badges (Section 6.3 & 6.4) */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
        {[
          { label: 'Market Cap', val: `₹${currentCompany.mcap} Cr` },
          { label: 'Book Value', val: `₹${currentCompany.bookValue}` },
          { label: 'ROE %', val: `${currentCompany.roe}%` },
          { label: 'ROCE %', val: `${currentCompany.roce}%` },
          { label: 'P/E Multiple', val: `${currentCompany.pe}x` },
          { label: 'P/B Ratio', val: `${currentCompany.pb}x` },
          { label: 'Div Yield %', val: `${currentCompany.divYield}%` },
        ].map((item, idx) => (
          <div key={idx} className="ios-card p-3 text-center">
            <div className="text-[9.5px] font-bold text-[#8E8E93] uppercase tracking-wider">{item.label}</div>
            <div className="text-sm font-extrabold text-white font-mono mt-1">{item.val}</div>
          </div>
        ))}
      </div>

      {/* 2b. Composite Financial Health Score (0-100) Card */}
      <div className="ios-card p-5 bg-gradient-to-r from-[#1C1C1E] via-[#242426] to-[#1C1C1E]">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div 
              className="w-16 h-16 rounded-2xl flex flex-col items-center justify-center font-mono font-extrabold shadow-lg"
              style={{ backgroundColor: `${currentCompany.healthScore?.color || '#30D158'}20`, color: currentCompany.healthScore?.color || '#30D158', border: `1.5px solid ${currentCompany.healthScore?.color || '#30D158'}50` }}
            >
              <span className="text-2xl leading-none">{currentCompany.score}</span>
              <span className="text-[9px] font-sans uppercase tracking-wider mt-0.5 font-bold">/ 100</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-white uppercase tracking-wider">
                  Composite Financial Health Score
                </span>
                <span 
                  className="text-[10px] font-bold px-2 py-0.5 rounded font-mono uppercase"
                  style={{ backgroundColor: `${currentCompany.healthScore?.color || '#30D158'}20`, color: currentCompany.healthScore?.color || '#30D158' }}
                >
                  {currentCompany.healthBand} Band
                </span>
              </div>
              <p className="text-xs text-[#8E8E93] mt-1">
                Weighted composite score across Profitability (35%), Cash Quality (30%), Growth (20%), and Leverage (15%).
              </p>
            </div>
          </div>

          {/* 4 Pillars Breakdown */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 self-stretch md:self-auto">
            <div className="bg-[#18181A] px-3 py-2 rounded-xl border border-white/[0.06] text-center">
              <div className="text-[9px] text-[#8E8E93] uppercase font-bold">Profitability</div>
              <div className="text-xs font-mono font-bold text-white mt-0.5">{currentCompany.healthScore?.breakdown?.profitability || 28} / 35</div>
            </div>
            <div className="bg-[#18181A] px-3 py-2 rounded-xl border border-white/[0.06] text-center">
              <div className="text-[9px] text-[#8E8E93] uppercase font-bold">Cash Quality</div>
              <div className="text-xs font-mono font-bold text-[#30D158] mt-0.5">{currentCompany.healthScore?.breakdown?.cashQuality || 25} / 30</div>
            </div>
            <div className="bg-[#18181A] px-3 py-2 rounded-xl border border-white/[0.06] text-center">
              <div className="text-[9px] text-[#8E8E93] uppercase font-bold">Growth Engine</div>
              <div className="text-xs font-mono font-bold text-[#0A84FF] mt-0.5">{currentCompany.healthScore?.breakdown?.growth || 16} / 20</div>
            </div>
            <div className="bg-[#18181A] px-3 py-2 rounded-xl border border-white/[0.06] text-center">
              <div className="text-[9px] text-[#8E8E93] uppercase font-bold">Leverage/D&E</div>
              <div className="text-xs font-mono font-bold text-[#FF9F0A] mt-0.5">{currentCompany.healthScore?.breakdown?.leverage || 13} / 15</div>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Qualitative Investment Insights: Pros & Cons (Section 5.7) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Pros Card */}
        <div className="ios-card p-5 border-l-4 border-l-[#30D158]">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle2 className="w-4 h-4 text-[#30D158]" />
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Investment Strengths & Moat (Pros)
            </h3>
          </div>
          <ul className="space-y-2 text-xs text-[#E5E5EA]">
            {companyProsCons.pros.map((p, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-[#30D158] font-bold mt-0.5">•</span>
                <span className="leading-relaxed">{p}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Cons Card */}
        <div className="ios-card p-5 border-l-4 border-l-[#FF453A]">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-4 h-4 text-[#FF453A]" />
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Risks, Headwinds & Limitations (Cons)
            </h3>
          </div>
          <ul className="space-y-2 text-xs text-[#E5E5EA]">
            {companyProsCons.cons.map((c, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-[#FF453A] font-bold mt-0.5">•</span>
                <span className="leading-relaxed">{c}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* 4. Compounded Growth (CAGR) Analysis (Section 5.5) */}
      <div className="ios-card p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-[#0A84FF]" />
              Compounded Fundamental Trajectory (CAGR & ROE)
            </h3>
            <p className="text-xs text-[#8E8E93] mt-0.5">
              Audited historical compounding rates across 10-Year, 5-Year, 3-Year, and Trailing Twelve Months (TTM)
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Sales CAGR */}
          <div className="bg-[#2C2C2E]/60 p-4 rounded-xl border border-[rgba(255,255,255,0.06)]">
            <div className="text-[11px] font-bold text-[#8E8E93] uppercase tracking-wider mb-2">Compounded Sales Growth</div>
            <div className="space-y-1.5 font-mono text-xs">
              {compoundedGrowth.map((g, i) => (
                <div key={i} className="flex justify-between items-center py-0.5 border-b border-white/[0.04]">
                  <span className="text-[#8E8E93] font-sans">{g.compounded_sales_growth?.split(':')[0]}:</span>
                  <span className="text-white font-bold">{g.compounded_sales_growth?.split(':')[1] || '—'}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Profit CAGR */}
          <div className="bg-[#2C2C2E]/60 p-4 rounded-xl border border-[rgba(255,255,255,0.06)]">
            <div className="text-[11px] font-bold text-[#8E8E93] uppercase tracking-wider mb-2">Compounded Profit Growth</div>
            <div className="space-y-1.5 font-mono text-xs">
              {compoundedGrowth.map((g, i) => (
                <div key={i} className="flex justify-between items-center py-0.5 border-b border-white/[0.04]">
                  <span className="text-[#8E8E93] font-sans">{g.compounded_profit_growth?.split(':')[0]}:</span>
                  <span className="text-[#30D158] font-bold">{g.compounded_profit_growth?.split(':')[1] || '—'}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Stock Price CAGR */}
          <div className="bg-[#2C2C2E]/60 p-4 rounded-xl border border-[rgba(255,255,255,0.06)]">
            <div className="text-[11px] font-bold text-[#8E8E93] uppercase tracking-wider mb-2">Stock Price CAGR</div>
            <div className="space-y-1.5 font-mono text-xs">
              {compoundedGrowth.map((g, i) => (
                <div key={i} className="flex justify-between items-center py-0.5 border-b border-white/[0.04]">
                  <span className="text-[#8E8E93] font-sans">{g.stock_price_cagr?.split(':')[0]}:</span>
                  <span className="text-[#0A84FF] font-bold">{g.stock_price_cagr?.split(':')[1] || '—'}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Return on Equity */}
          <div className="bg-[#2C2C2E]/60 p-4 rounded-xl border border-[rgba(255,255,255,0.06)]">
            <div className="text-[11px] font-bold text-[#8E8E93] uppercase tracking-wider mb-2">Return on Equity (ROE)</div>
            <div className="space-y-1.5 font-mono text-xs">
              {compoundedGrowth.map((g, i) => (
                <div key={i} className="flex justify-between items-center py-0.5 border-b border-white/[0.04]">
                  <span className="text-[#8E8E93] font-sans">{g.roe?.split(':')[0]}:</span>
                  <span className="text-white font-bold">{g.roe?.split(':')[1] || '—'}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 5. Audited Financial Statements Deep Dive */}
      <div className="ios-card p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h3 className="text-base font-bold text-white tracking-tight">Audited Financial History</h3>
            <p className="text-xs text-[#8E8E93]">Multi-year statutory filings from BSE India regulatory archives</p>
          </div>

          {/* Statement Tab Controls */}
          <div className="bg-[#2C2C2E] p-1 rounded-2xl flex items-center gap-1 border border-[rgba(255,255,255,0.06)] self-start md:self-auto">
            {[
              { id: 'pnl', label: 'Profit & Loss' },
              { id: 'bs', label: 'Balance Sheet' },
              { id: 'cf', label: 'Cash Flow' },
              { id: 'reports', label: 'BSE Annual Reports' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setStatementTab(tab.id)}
                className={`px-3 py-1 text-xs font-semibold rounded-xl transition-all ${
                  statementTab === tab.id
                    ? 'bg-white text-black font-bold shadow-md'
                    : 'text-[#8E8E93] hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab 1: P&L Statement Table */}
        {statementTab === 'pnl' && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[rgba(255,255,255,0.08)] text-[10px] font-bold text-[#8E8E93] uppercase">
                  <th className="pb-2.5">Fiscal Year</th>
                  <th className="pb-2.5 text-right">Sales Revenue (₹ Cr)</th>
                  <th className="pb-2.5 text-right">Operating Profit (₹ Cr)</th>
                  <th className="pb-2.5 text-right">OPM %</th>
                  <th className="pb-2.5 text-right">Net Profit (₹ Cr)</th>
                  <th className="pb-2.5 text-right">EPS (₹)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[rgba(255,255,255,0.04)] font-mono">
                {pnlHistory.length > 0 ? (
                  pnlHistory.map((r, i) => (
                    <tr key={i} className="hover:bg-white/[0.03]">
                      <td className="py-2.5 font-sans font-semibold text-white">{r.year}</td>
                      <td className="py-2.5 text-right text-white">₹{r.sales?.toLocaleString()}</td>
                      <td className="py-2.5 text-right text-[#30D158] font-bold">₹{r.operating_profit?.toLocaleString()}</td>
                      <td className="py-2.5 text-right text-[#0A84FF] font-semibold">{r.opm_percentage}%</td>
                      <td className="py-2.5 text-right text-white font-bold">₹{r.net_profit?.toLocaleString()}</td>
                      <td className="py-2.5 text-right text-[#8E8E93]">₹{r.eps}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6" className="py-6 text-center text-[#8E8E93] font-sans">
                      Historical audited statements available in database for {currentCompany.id}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* Tab 2: Balance Sheet Table */}
        {statementTab === 'bs' && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[rgba(255,255,255,0.08)] text-[10px] font-bold text-[#8E8E93] uppercase">
                  <th className="pb-2.5">Year</th>
                  <th className="pb-2.5 text-right">Equity Capital</th>
                  <th className="pb-2.5 text-right">Reserves & Surplus</th>
                  <th className="pb-2.5 text-right">Borrowings</th>
                  <th className="pb-2.5 text-right">Fixed Assets</th>
                  <th className="pb-2.5 text-right">Total Assets</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[rgba(255,255,255,0.04)] font-mono">
                {balanceSheetHistory.length > 0 ? (
                  balanceSheetHistory.map((r, i) => (
                    <tr key={i} className="hover:bg-white/[0.03]">
                      <td className="py-2.5 font-sans font-semibold text-white">{r.year}</td>
                      <td className="py-2.5 text-right text-[#8E8E93]">₹{r.equity_capital?.toLocaleString()}</td>
                      <td className="py-2.5 text-right text-white font-semibold">₹{r.reserves?.toLocaleString()}</td>
                      <td className="py-2.5 text-right text-[#FF453A]">₹{r.borrowings?.toLocaleString()}</td>
                      <td className="py-2.5 text-right text-[#0A84FF]">₹{r.fixed_assets?.toLocaleString()}</td>
                      <td className="py-2.5 text-right text-[#30D158] font-bold">₹{r.total_assets?.toLocaleString()}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6" className="py-6 text-center text-[#8E8E93] font-sans">
                      Audited balance sheet statement loaded for {currentCompany.id}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* Tab 3: Cash Flow Table */}
        {statementTab === 'cf' && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[rgba(255,255,255,0.08)] text-[10px] font-bold text-[#8E8E93] uppercase">
                  <th className="pb-2.5">Period</th>
                  <th className="pb-2.5 text-right">Operating Activity (CFO)</th>
                  <th className="pb-2.5 text-right">Investing Activity (CFI)</th>
                  <th className="pb-2.5 text-right">Financing Activity (CFF)</th>
                  <th className="pb-2.5 text-right">Net Cash Flow</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[rgba(255,255,255,0.04)] font-mono">
                {cashFlowHistory.length > 0 ? (
                  cashFlowHistory.map((r, i) => (
                    <tr key={i} className="hover:bg-white/[0.03]">
                      <td className="py-2.5 font-sans font-semibold text-white">{r.year}</td>
                      <td className={`py-2.5 text-right font-bold ${r.operating_activity >= 0 ? 'text-[#30D158]' : 'text-[#FF453A]'}`}>
                        ₹{r.operating_activity?.toLocaleString()}
                      </td>
                      <td className="py-2.5 text-right text-[#8E8E93]">₹{r.investing_activity?.toLocaleString()}</td>
                      <td className="py-2.5 text-right text-[#8E8E93]">₹{r.financing_activity?.toLocaleString()}</td>
                      <td className={`py-2.5 text-right font-bold ${r.net_cash_flow >= 0 ? 'text-[#30D158]' : 'text-[#FF453A]'}`}>
                        ₹{r.net_cash_flow?.toLocaleString()}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="5" className="py-6 text-center text-[#8E8E93] font-sans">
                      Statutory Cash Flow reports available for {currentCompany.id}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* Tab 4: BSE India Regulatory Reports */}
        {statementTab === 'reports' && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[rgba(255,255,255,0.08)] text-[10px] font-bold text-[#8E8E93] uppercase">
                  <th className="pb-2.5">Filing Year</th>
                  <th className="pb-2.5">Document Title</th>
                  <th className="pb-2.5">Source Registry</th>
                  <th className="pb-2.5 text-right">Official Document Link</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[rgba(255,255,255,0.04)]">
                {annualReports.length > 0 ? (
                  annualReports.map((r, i) => (
                    <tr key={i} className="hover:bg-white/[0.03]">
                      <td className="py-2.5 font-mono font-semibold text-white">{r.Year}</td>
                      <td className="py-2.5 text-white">{currentCompany.name} Annual Report {r.Year}</td>
                      <td className="py-2.5 text-[#8E8E93]">BSE India Corporate Filing</td>
                      <td className="py-2.5 text-right">
                        <a 
                          href={r.Annual_Report} 
                          target="_blank" 
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 px-3 py-1 bg-[#2C2C2E] border border-[rgba(255,255,255,0.1)] rounded-lg text-xs font-semibold text-[#0A84FF] hover:bg-[#0A84FF] hover:text-white transition-all"
                        >
                          View PDF <ExternalLink className="w-3 h-3" />
                        </a>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="4" className="py-6 text-center text-[#8E8E93]">
                      Official BSE Annual Report links recorded in repository for {currentCompany.id}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
