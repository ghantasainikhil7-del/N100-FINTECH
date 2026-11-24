import React from 'react';
import { Search, Bell } from 'lucide-react';

export default function Header({ title, subtitle, badgeText = "NIFTY 100 CONSTITUENTS" }) {
  return (
    <header className="px-6 py-4 border-b border-[rgba(255,255,255,0.06)] bg-black/60 backdrop-blur-md sticky top-0 z-40 flex items-center justify-between">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-[10px] font-bold text-[#30D158] bg-[#30D158]/15 border border-[#30D158]/30 px-2.5 py-0.5 rounded-full uppercase tracking-wider flex items-center gap-1.5">
            <span className="pulse-green-dot" />
            {badgeText}
          </span>
          <span className="text-[#636366] text-xs">/</span>
          <span className="text-[#8E8E93] text-xs font-semibold">BLUESTOCK PRO</span>
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight">{title}</h1>
        {subtitle && <p className="text-xs text-[#8E8E93] mt-0.5">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-3">
        <button className="w-8 h-8 rounded-full bg-[#1C1C1E] border border-[rgba(255,255,255,0.08)] flex items-center justify-center text-[#8E8E93] hover:text-white transition-colors relative">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-[#FF453A]" />
        </button>

        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#0A84FF] to-[#0055B3] text-white font-bold text-xs flex items-center justify-center border border-white/20">
          GN
        </div>
      </div>
    </header>
  );
}
