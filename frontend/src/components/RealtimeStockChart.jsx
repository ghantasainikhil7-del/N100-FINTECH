import React, { useState, useEffect, useMemo, useRef } from 'react';

// Generates realistic market trend datasets for each timeframe
function generateTimeframeData(timeframe) {
  switch (timeframe) {
    case '1D': {
      // Intraday from 09:15 AM to 03:30 PM (IST)
      const times = [
        '09:15', '09:30', '09:45', '10:00', '10:15', '10:30', '10:45', '11:00',
        '11:15', '11:30', '11:45', '12:00', '12:15', '12:30', '12:45', '13:00',
        '13:15', '13:30', '13:45', '14:00', '14:15', '14:30', '14:45', '15:00',
        '15:15', '15:30'
      ];
      let p = 25034.25;
      const base = 25034.25;
      const points = [];
      const deltas = [
        18, 24, -12, 35, 15, -8, 22, 19, -14, 30, 25, -10,
        14, -5, 18, 22, 12, -16, 28, 34, 15, -10, 25, 20, 15, 8
      ];
      times.forEach((t, i) => {
        p += deltas[i] || 10;
        points.push({ time: t, price: Math.round(p * 100) / 100, base });
      });
      // Normalize last to ~25,318.40
      const diff = 25318.40 - points[points.length - 1].price;
      points.forEach((pt, i) => {
        pt.price = Math.round((pt.price + (diff * (i / (points.length - 1)))) * 100) / 100;
      });
      return points;
    }
    case '1W': {
      const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
      const points = [];
      let p = 24850.00;
      const base = 24850.00;
      days.forEach((d, dIdx) => {
        ['10:00', '12:00', '14:00', '15:30'].forEach((t, tIdx) => {
          const step = (dIdx * 4) + tIdx;
          p += (Math.sin(step * 0.7) * 45) + 32;
          points.push({ time: `${d} ${t}`, price: Math.round(p * 100) / 100, base });
        });
      });
      const diff = 25318.40 - points[points.length - 1].price;
      points.forEach((pt, i) => {
        pt.price = Math.round((pt.price + (diff * (i / (points.length - 1)))) * 100) / 100;
      });
      return points;
    }
    case '1M': {
      const points = [];
      let p = 24180.00;
      const base = 24180.00;
      for (let day = 1; day <= 24; day++) {
        p += (Math.sin(day * 0.5) * 65) + 52;
        points.push({ time: `Day ${day}`, price: Math.round(p * 100) / 100, base });
      }
      const diff = 25318.40 - points[points.length - 1].price;
      points.forEach((pt, i) => {
        pt.price = Math.round((pt.price + (diff * (i / (points.length - 1)))) * 100) / 100;
      });
      return points;
    }
    case '1Y': {
      const months = ['Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'];
      const points = [];
      let p = 21340.00;
      const base = 21340.00;
      months.forEach((m, mIdx) => {
        [1, 2, 3, 4].forEach(w => {
          const step = (mIdx * 4) + w;
          p += (Math.cos(step * 0.4) * 80) + 115;
          points.push({ time: `${m} W${w}`, price: Math.round(p * 100) / 100, base });
        });
      });
      const diff = 25318.40 - points[points.length - 1].price;
      points.forEach((pt, i) => {
        pt.price = Math.round((pt.price + (diff * (i / (points.length - 1)))) * 100) / 100;
      });
      return points;
    }
    case '5Y': {
      const years = ['2020', '2021', '2022', '2023', '2024'];
      const points = [];
      let p = 11200.00;
      const base = 11200.00;
      years.forEach((yr, yIdx) => {
        ['Q1', 'Q2', 'Q3', 'Q4'].forEach((q, qIdx) => {
          const step = (yIdx * 4) + qIdx;
          p += (Math.sin(step * 0.3) * 350) + 780;
          points.push({ time: `${yr} ${q}`, price: Math.round(p * 100) / 100, base });
        });
      });
      const diff = 25318.40 - points[points.length - 1].price;
      points.forEach((pt, i) => {
        pt.price = Math.round((pt.price + (diff * (i / (points.length - 1)))) * 100) / 100;
      });
      return points;
    }
    case 'ALL':
    default: {
      const years = ['2018', '2019', '2020', '2021', '2022', '2023', '2024'];
      const points = [];
      let p = 6800.00;
      const base = 6800.00;
      years.forEach((yr, yIdx) => {
        ['H1', 'H2'].forEach((h, hIdx) => {
          const step = (yIdx * 2) + hIdx;
          p += (Math.cos(step * 0.4) * 450) + 1420;
          points.push({ time: `${yr} ${h}`, price: Math.round(p * 100) / 100, base });
        });
      });
      const diff = 25318.40 - points[points.length - 1].price;
      points.forEach((pt, i) => {
        pt.price = Math.round((pt.price + (diff * (i / (points.length - 1)))) * 100) / 100;
      });
      return points;
    }
  }
}

// Converts array of points to smooth SVG cubic Bézier curves
function getCurvedPath(coords) {
  if (coords.length === 0) return '';
  if (coords.length === 1) return `M ${coords[0].x},${coords[0].y}`;

  let path = `M ${coords[0].x},${coords[0].y}`;
  for (let i = 0; i < coords.length - 1; i++) {
    const p0 = coords[i === 0 ? 0 : i - 1];
    const p1 = coords[i];
    const p2 = coords[i + 1];
    const p3 = coords[i + 2 < coords.length ? i + 2 : i + 1];

    const cp1x = p1.x + (p2.x - p0.x) / 6;
    const cp1y = p1.y + (p2.y - p0.y) / 6;

    const cp2x = p2.x - (p3.x - p1.x) / 6;
    const cp2y = p2.y - (p3.y - p1.y) / 6;

    path += ` C ${cp1x.toFixed(1)},${cp1y.toFixed(1)} ${cp2x.toFixed(1)},${cp2y.toFixed(1)} ${p2.x.toFixed(1)},${p2.y.toFixed(1)}`;
  }
  return path;
}

export default function RealtimeStockChart({ timeframe, onUpdatePrice }) {
  const [data, setData] = useState(() => generateTimeframeData(timeframe));
  const [hoverIndex, setHoverIndex] = useState(null);
  const [liveOffset, setLiveOffset] = useState(0);
  const [isTickUp, setIsTickUp] = useState(true);
  const svgRef = useRef(null);

  // Re-generate dataset whenever timeframe changes
  useEffect(() => {
    const newData = generateTimeframeData(timeframe);
    setData(newData);
    setHoverIndex(null);
  }, [timeframe]);

  // Real-time live market ticker animation (every 1.6s)
  useEffect(() => {
    const timer = setInterval(() => {
      setData(prev => {
        if (!prev || prev.length === 0) return prev;
        const lastIdx = prev.length - 1;
        const lastPoint = prev[lastIdx];
        
        // Random micro tick delta (-4.5 to +6.5) with slight upward market bias
        const delta = (Math.random() * 11 - 4.5);
        const newPrice = Math.round((lastPoint.price + delta) * 100) / 100;
        setIsTickUp(delta >= 0);
        setLiveOffset(delta);

        const updated = [...prev];
        updated[lastIdx] = { ...lastPoint, price: newPrice };
        return updated;
      });
    }, 1600);

    return () => clearInterval(timer);
  }, []);

  // Sync active price to parent header banner
  useEffect(() => {
    if (!data || data.length === 0) return;
    const activePoint = hoverIndex !== null ? data[hoverIndex] : data[data.length - 1];
    const basePrice = data[0].base || data[0].price;
    const changeAmount = Math.round((activePoint.price - basePrice) * 100) / 100;
    const changePct = Math.round(((changeAmount / basePrice) * 100) * 100) / 100;

    if (onUpdatePrice) {
      onUpdatePrice({
        price: activePoint.price,
        change: changeAmount,
        changePct: changePct,
        isPositive: changeAmount >= 0,
        time: activePoint.time,
        isHovered: hoverIndex !== null
      });
    }
  }, [data, hoverIndex, onUpdatePrice]);

  // Dimensions & bounds
  const width = 1000;
  const height = 180;
  const paddingX = 12;
  const paddingTop = 16;
  const paddingBottom = 24;

  const { coords, linePath, areaPath, minPrice, maxPrice } = useMemo(() => {
    if (!data || data.length === 0) return { coords: [], linePath: '', areaPath: '', minPrice: 0, maxPrice: 0 };

    const prices = data.map(d => d.price);
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const range = (max - min) || 1;

    // Buffer range by 5%
    const bufferedMin = min - (range * 0.05);
    const bufferedMax = max + (range * 0.05);
    const bufferedRange = bufferedMax - bufferedMin;

    const plotWidth = width - (paddingX * 2);
    const plotHeight = height - paddingTop - paddingBottom;

    const points = data.map((d, i) => {
      const x = paddingX + (i / (data.length - 1)) * plotWidth;
      const y = paddingTop + plotHeight - ((d.price - bufferedMin) / bufferedRange) * plotHeight;
      return { x, y, price: d.price, time: d.time };
    });

    const curvedLine = getCurvedPath(points);
    const area = `${curvedLine} L ${points[points.length - 1].x},${height - paddingBottom + 6} L ${points[0].x},${height - paddingBottom + 6} Z`;

    return {
      coords: points,
      linePath: curvedLine,
      areaPath: area,
      minPrice: Math.round(min),
      maxPrice: Math.round(max)
    };
  }, [data]);

  // Handle pointer scrub
  const handlePointerMove = (e) => {
    if (!svgRef.current || coords.length === 0) return;
    const rect = svgRef.current.getBoundingClientRect();
    const clientX = e.clientX ?? (e.touches && e.touches[0] ? e.touches[0].clientX : null);
    if (clientX === null) return;

    const relX = clientX - rect.left;
    const ratio = Math.max(0, Math.min(1, relX / rect.width));
    const targetIdx = Math.round(ratio * (coords.length - 1));
    setHoverIndex(targetIdx);
  };

  const handlePointerLeave = () => {
    setHoverIndex(null);
  };

  const activeCoord = hoverIndex !== null ? coords[hoverIndex] : coords[coords.length - 1];
  const lastCoord = coords[coords.length - 1];

  return (
    <div 
      className="relative w-full select-none"
      onPointerMove={handlePointerMove}
      onPointerLeave={handlePointerLeave}
      onTouchMove={handlePointerMove}
      onTouchEnd={handlePointerLeave}
    >
      <svg
        ref={svgRef}
        viewBox={`0 0 ${width} ${height}`}
        className="w-full h-36 md:h-44 overflow-visible cursor-crosshair"
        preserveAspectRatio="none"
      >
        <defs>
          {/* Signal Green Gradient */}
          <linearGradient id="appleGreenGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#30D158" stopOpacity="0.32" />
            <stop offset="60%" stopColor="#30D158" stopOpacity="0.08" />
            <stop offset="100%" stopColor="#30D158" stopOpacity="0.00" />
          </linearGradient>

          {/* Line Glow Filter */}
          <filter id="neonGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Subtle Horizontal Grid Reference Lines */}
        <line 
          x1={paddingX} 
          y1={paddingTop} 
          x2={width - paddingX} 
          y2={paddingTop} 
          stroke="rgba(255,255,255,0.06)" 
          strokeDasharray="4 4" 
        />
        <line 
          x1={paddingX} 
          y1={paddingTop + (height - paddingTop - paddingBottom) / 2} 
          x2={width - paddingX} 
          y2={paddingTop + (height - paddingTop - paddingBottom) / 2} 
          stroke="rgba(255,255,255,0.04)" 
          strokeDasharray="4 4" 
        />
        <line 
          x1={paddingX} 
          y1={height - paddingBottom} 
          x2={width - paddingX} 
          y2={height - paddingBottom} 
          stroke="rgba(255,255,255,0.06)" 
        />

        {/* Shaded Area Fill */}
        <path
          d={areaPath}
          fill="url(#appleGreenGradient)"
          className="transition-all duration-300 ease-out"
        />

        {/* Main Curved Trend Line */}
        <path
          d={linePath}
          fill="none"
          stroke="#30D158"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          filter="url(#neonGlow)"
          className="transition-all duration-150 ease-out"
        />

        {/* Hover Scrubbing Crosshair Guide Line */}
        {hoverIndex !== null && activeCoord && (
          <g>
            <line
              x1={activeCoord.x}
              y1={paddingTop}
              x2={activeCoord.x}
              y2={height - paddingBottom}
              stroke="rgba(255,255,255,0.35)"
              strokeWidth="1.2"
              strokeDasharray="3 3"
            />
            <circle
              cx={activeCoord.x}
              cy={activeCoord.y}
              r="6"
              fill="#30D158"
              stroke="#FFFFFF"
              strokeWidth="2.5"
              className="drop-shadow-[0_0_8px_rgba(48,209,88,0.9)]"
            />
          </g>
        )}

        {/* Real-time Leading Live Pulse Dot (when not scrubbing) */}
        {hoverIndex === null && lastCoord && (
          <g>
            {/* Pulsing Ripple Effect */}
            <circle
              cx={lastCoord.x}
              cy={lastCoord.y}
              r="8"
              fill="#30D158"
              opacity="0.35"
              className="animate-ping"
              style={{ transformOrigin: `${lastCoord.x}px ${lastCoord.y}px` }}
            />
            {/* Solid Center Dot */}
            <circle
              cx={lastCoord.x}
              cy={lastCoord.y}
              r="4.5"
              fill="#30D158"
              stroke="#FFFFFF"
              strokeWidth="1.8"
              className="drop-shadow-[0_0_6px_#30D158]"
            />
          </g>
        )}
      </svg>

      {/* Floating Scrub Tooltip Badge */}
      {hoverIndex !== null && activeCoord && (
        <div
          className="absolute pointer-events-none transform -translate-x-1/2 -top-3 z-30 transition-transform duration-75"
          style={{ left: `${(activeCoord.x / width) * 100}%` }}
        >
          <div className="bg-[#1C1C1E]/95 backdrop-blur-md border border-[rgba(255,255,255,0.18)] px-2.5 py-1 rounded-lg shadow-xl text-center">
            <div className="text-[10px] font-mono font-bold text-white">
              ₹{activeCoord.price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </div>
            <div className="text-[9px] font-mono text-[#8E8E93]">
              {activeCoord.time}
            </div>
          </div>
        </div>
      )}

      {/* Horizontal Axis Min / Max Markers */}
      <div className="flex items-center justify-between text-[10px] font-mono text-[#636366] px-3 pt-1">
        <span>Low: ₹{minPrice.toLocaleString()}</span>
        <span className="flex items-center gap-1.5 text-[#30D158] font-semibold">
          <span className="w-1.5 h-1.5 rounded-full bg-[#30D158] animate-pulse" />
          Live Tick Updates
        </span>
        <span>High: ₹{maxPrice.toLocaleString()}</span>
      </div>
    </div>
  );
}
