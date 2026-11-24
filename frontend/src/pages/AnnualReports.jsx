import React, { useState, useMemo } from 'react';
import { Download, ExternalLink, FileText, CheckCircle2, Building2, Globe2, Layers, Search } from 'lucide-react';
import { useBluestockData } from '../context/useBluestockData';
import { RAW_DOCUMENTS_DATA } from '../data/bluestockDatasets';

const SECTORS_LIST = [
  "Financials", "Energy", "Information Technology", "Consumer Discretionary", 
  "Consumer Staples", "Healthcare", "Materials", "Industrials", 
  "Communication Services", "Real Estate", "Conglomerates"
];

export default function AnnualReports() {
  const { companies, setSelectedTicker } = useBluestockData();
  const [activeTab, setActiveTab] = useState('suite');
  const [reportSearch, setReportSearch] = useState('');
  const [selectedYear, setSelectedYear] = useState('All');

  // Filter BSE Regulatory Documents
  const filteredDocs = useMemo(() => {
    let list = RAW_DOCUMENTS_DATA.filter(r => r.Annual_Report && r.Annual_Report !== 'Null');
    if (selectedYear !== 'All') {
      list = list.filter(r => String(r.Year) === selectedYear);
    }
    if (reportSearch) {
      const q = reportSearch.toLowerCase().trim();
      list = list.filter(r => r.company_id.toLowerCase().includes(q));
    }
    return list.slice(0, 100);
  }, [reportSearch, selectedYear]);

  // Download publication-grade 2-page PDF Tearsheet
  const handleDownloadTearsheet = (ticker) => {
    const url = `/reports/tearsheets/${ticker}_tearsheet.pdf`;
    const link = document.createElement('a');
    link.href = url;
    link.download = `${ticker}_tearsheet.pdf`;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Download publication-grade Sector Intelligence PDF Report
  const handleDownloadSectorReport = (sector) => {
    const sectorMap = {
      "Information Technology": "Information_Technology_report.pdf",
      "Financials": "Financials_report.pdf",
      "Energy": "Energy_report.pdf",
      "Healthcare": "Healthcare_report.pdf",
      "Materials": "Materials_report.pdf",
      "Consumer Discretionary": "Consumer_Discretionary_report.pdf",
      "Automobiles": "Consumer_Discretionary_report.pdf",
      "Consumer Staples": "Consumer_Staples_report.pdf",
      "Fast Moving Consumer Goods": "Consumer_Staples_report.pdf",
      "FMCG": "Consumer_Staples_report.pdf",
      "Industrials": "Industrials_report.pdf",
      "Communication Services": "Communication_Services_report.pdf",
      "Telecommunication": "Communication_Services_report.pdf",
      "Real Estate": "Real_Estate_report.pdf",
      "Conglomerates": "Energy_report.pdf",
    };
    const targetFile = sectorMap[sector] || `${sector.replace(/[^\w\-]/g, '_')}_report.pdf`;
    const url = `/reports/sector/${targetFile}`;
    const link = document.createElement('a');
    link.href = url;
    link.download = targetFile;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Full Universe Excel/CSV Export
  const exportFullUniverse = () => {
    const headers = [
      "Ticker", "Company Legal Name", "GICS Broad Sector", "Sub Sector", 
      "Index Weight (%)", "Price (INR)", "Market Cap (Cr)", "Financial Health Score", 
      "Health Band", "ROE (%)", "ROCE (%)", "P/E", "P/B", "EV/EBITDA", "D/E Ratio", 
      "Interest Coverage", "Free Cash Flow (Cr)", "Cash from Operations (Cr)", "CapEx (Cr)", 
      "Dividend Yield (%)", "Capital Allocation Strategy"
    ];
    const rows = companies.map(c => [
      c.id,
      `"${c.name}"`,
      `"${c.sector}"`,
      `"${c.subSector}"`,
      c.indexWeight,
      c.price,
      c.mcapCr,
      c.score,
      c.healthBand,
      c.roe,
      c.roce,
      c.pe,
      c.pb,
      c.evEbitda,
      c.debtToEquity,
      c.interestCoverage,
      c.fcfCr,
      c.cfoCr,
      c.capexCr,
      c.divYield,
      `"${c.capitalAllocation.label}"`
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `nifty100_full_universe_report_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto w-full">
      {/* 1. Header Card */}
      <div className="ios-card p-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className="text-[10px] font-bold text-[#8E8E93] bg-[#2C2C2E] border border-white/[0.08] px-2.5 py-0.5 rounded-full uppercase tracking-wider font-mono">
                92 COMPANY TEARSHEETS + 11 SECTOR REPORTS
              </span>
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">Executive Reports & Regulatory Filings Repository</h2>
            <p className="text-xs text-[#8E8E93] mt-0.5">
              Automated 2-page company tearsheets, 11 sector macro digests, and direct links to 1,585 statutory BSE India filings.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={exportFullUniverse}
              className="px-4 py-2 bg-white text-black font-bold text-xs rounded-xl shadow-lg hover:bg-[#30D158] transition-all flex items-center gap-2"
            >
              <Download className="w-3.5 h-3.5" />
              Download Full Universe Data (CSV)
            </button>
          </div>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center gap-2 bg-[#2C2C2E] p-1 rounded-2xl border border-white/[0.06] w-fit">
          <button
            onClick={() => setActiveTab('suite')}
            className={`px-4 py-1.5 text-xs font-semibold rounded-xl transition-all ${
              activeTab === 'suite'
                ? 'bg-white text-black font-bold shadow-md'
                : 'text-[#8E8E93] hover:text-white'
            }`}
          >
            103 Report Suite (Tearsheets & Sectors)
          </button>
          <button
            onClick={() => setActiveTab('filings')}
            className={`px-4 py-1.5 text-xs font-semibold rounded-xl transition-all ${
              activeTab === 'filings'
                ? 'bg-white text-black font-bold shadow-md'
                : 'text-[#8E8E93] hover:text-white'
            }`}
          >
            BSE Statutory Archives (1,585 Filings)
          </button>
        </div>
      </div>

      {/* 2. Tab Content */}
      {activeTab === 'suite' ? (
        <div className="space-y-6">
          {/* 11 Sector Macro Reports */}
          <div className="ios-card p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                  <Globe2 className="w-4 h-4 text-[#0A84FF]" />
                  11 Sector Macro PDF Reports
                </h3>
                <p className="text-xs text-[#8E8E93]">Consolidated industry landscape, median multiples, and constituent rankings</p>
              </div>
              <span className="text-xs font-mono text-[#0A84FF]">11 Broad Sectors</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {SECTORS_LIST.map((sec) => (
                <div key={sec} className="p-3.5 bg-[#2C2C2E]/60 rounded-xl border border-white/[0.06] flex items-center justify-between">
                  <div>
                    <div className="text-xs font-bold text-white">{sec}</div>
                    <div className="text-[10px] text-[#8E8E93] mt-0.5">Macro Landscape Digest</div>
                  </div>
                  <button
                    onClick={() => handleDownloadSectorReport(sec)}
                    className="p-1.5 rounded-lg bg-[#1C1C1E] border border-white/[0.1] text-[#0A84FF] hover:bg-[#0A84FF] hover:text-white transition-all text-xs font-semibold"
                    title={`Download ${sec} Sector PDF Report`}
                  >
                    PDF
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* 92 Company Executive Tearsheets */}
          <div className="ios-card p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
              <div>
                <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                  <FileText className="w-4 h-4 text-[#30D158]" />
                  92 Company Executive Tearsheets (2-Page Reports)
                </h3>
                <p className="text-xs text-[#8E8E93]">KPI tiles, 10Y financial trajectories, Balance Sheet stack, and Cash Flow breakdown</p>
              </div>
              <span className="text-xs font-mono text-[#30D158]">92 Companies Available</span>
            </div>

            <div className="overflow-x-auto max-h-[500px]">
              <table className="w-full text-left text-xs">
                <thead className="sticky top-0 bg-[#1C1C1E] z-10">
                  <tr className="border-b border-white/[0.08] text-[10px] font-bold text-[#8E8E93] uppercase">
                    <th className="pb-3">Ticker</th>
                    <th className="pb-3">Company Legal Name</th>
                    <th className="pb-3">Sector</th>
                    <th className="pb-3 text-center">Health Score</th>
                    <th className="pb-3 text-right">Market Cap</th>
                    <th className="pb-3 text-right">Tearsheet Export</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/[0.04] font-mono">
                  {companies.map((c) => (
                    <tr key={c.id} className="hover:bg-white/[0.04] transition-colors">
                      <td className="py-2.5 font-bold text-white">{c.id}</td>
                      <td className="py-2.5 font-sans font-medium text-white">{c.name}</td>
                      <td className="py-2.5 font-sans text-[#8E8E93] text-[11px]">{c.sector}</td>
                      <td className="py-2.5 text-center font-sans">
                        <span 
                          className="text-[10px] font-bold px-2 py-0.5 rounded font-mono"
                          style={{ backgroundColor: `${c.healthScore?.color || '#30D158'}20`, color: c.healthScore?.color || '#30D158' }}
                        >
                          {c.score} · {c.healthBand}
                        </span>
                      </td>
                      <td className="py-2.5 text-right text-white font-semibold">₹{c.mcap} Cr</td>
                      <td className="py-2.5 text-right font-sans">
                        <button
                          onClick={() => handleDownloadTearsheet(c.id)}
                          className="inline-flex items-center gap-1.5 px-3 py-1 bg-[#2C2C2E] border border-white/[0.1] rounded-lg text-xs font-semibold text-[#0A84FF] hover:bg-[#0A84FF] hover:text-white transition-all cursor-pointer shadow-sm active:scale-95"
                          title={`Download 2-Page Tearsheet PDF for ${c.id}`}
                        >
                          Download Tearsheet <Download className="w-3 h-3 stroke-[2.5]" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : (
        /* BSE Regulatory Filings Archive */
        <div className="ios-card p-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
            <div>
              <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                <FileText className="w-4 h-4 text-[#0A84FF]" />
                BSE India Annual Regulatory Filings (1,585 Documents)
              </h3>
              <p className="text-xs text-[#8E8E93]">Direct authenticated links to BSE regulatory annual disclosures</p>
            </div>

            {/* Filter controls */}
            <div className="flex items-center gap-2">
              <input
                type="text"
                placeholder="Search ticker..."
                value={reportSearch}
                onChange={(e) => setReportSearch(e.target.value)}
                className="bg-[#2C2C2E] border border-white/[0.1] rounded-xl px-3 py-1.5 text-xs text-white outline-none focus:border-[#0A84FF] w-36"
              />
              <select
                value={selectedYear}
                onChange={(e) => setSelectedYear(e.target.value)}
                className="bg-[#2C2C2E] border border-white/[0.1] rounded-xl px-3 py-1.5 text-xs text-white outline-none focus:border-[#0A84FF] cursor-pointer"
              >
                <option value="All">All Years</option>
                {['2024', '2023', '2022', '2021', '2020', '2019', '2018', '2017'].map(yr => (
                  <option key={yr} value={yr} className="bg-black">{yr}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="overflow-x-auto max-h-[500px]">
            <table className="w-full text-left text-xs">
              <thead className="sticky top-0 bg-[#1C1C1E] z-10">
                <tr className="border-b border-white/[0.08] text-[10px] font-bold text-[#8E8E93] uppercase">
                  <th className="pb-2.5">Company Code</th>
                  <th className="pb-2.5">Filing Year</th>
                  <th className="pb-2.5">Document Archive</th>
                  <th className="pb-2.5 text-right">Regulatory PDF Link</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filteredDocs.map((doc, idx) => (
                  <tr key={idx} className="hover:bg-white/[0.04] transition-colors">
                    <td className="py-2.5 font-bold text-white font-mono">{doc.company_id}</td>
                    <td className="py-2.5 text-[#8E8E93] font-mono">{doc.Year}</td>
                    <td className="py-2.5 text-white flex items-center gap-2">
                      <FileText className="w-3.5 h-3.5 text-[#0A84FF]" />
                      <span>Annual Statutory Disclosures ({doc.Year})</span>
                    </td>
                    <td className="py-2.5 text-right">
                      <a
                        href={doc.Annual_Report}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1.5 px-3 py-1 bg-[#2C2C2E] border border-white/[0.1] rounded-lg text-xs font-semibold text-[#0A84FF] hover:bg-[#0A84FF] hover:text-white transition-all cursor-pointer"
                      >
                        BSE PDF <ExternalLink className="w-3 h-3" />
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
