import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Plane, 
  Scan, 
  ShieldCheck, 
  Mail, 
  CloudRain, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw, 
  Send, 
  DollarSign, 
  FileText,
  Activity,
  Database,
  Search,
  Sparkles,
  ArrowRight,
  Zap,
  Globe,
  Clock
} from 'lucide-react';
import confetti from 'canvas-confetti';

interface EligibleFlight {
  id: number;
  flight_number: string;
  carrier: string;
  route: string;
  delay_duration: string;
  delay_reason: string;
  statutory_amount_eur: number;
  metar_verdict: string;
  parallel_departure_rate: string;
  flight_date: string;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'database' | 'claim' | 'ocr' | 'metar'>('database');
  const [searchQuery, setSearchQuery] = useState("");
  const [targetLang, setTargetLang] = useState("German");
  const [isProcessing, setIsProcessing] = useState(false);

  const [eligibleFlights, setEligibleFlights] = useState<EligibleFlight[]>([
    { id: 1, flight_number: "LH401", carrier: "Lufthansa", route: "FRA ➔ JFK", delay_duration: "4h 15m", delay_reason: "Weather Bluff Disproved", statutory_amount_eur: 600.0, metar_verdict: "VFR Clear (Visibility 10km)", parallel_departure_rate: "93.8%", flight_date: "2026-08-28" },
    { id: 2, flight_number: "FR8821", carrier: "Ryanair", route: "STN ➔ BUD", delay_duration: "3h 40m", delay_reason: "Technical Defect", statutory_amount_eur: 400.0, metar_verdict: "Normal Conditions", parallel_departure_rate: "100.0%", flight_date: "2026-08-28" },
    { id: 3, flight_number: "W62301", carrier: "Wizz Air", route: "MXP ➔ BUD", delay_duration: "5h 10m", delay_reason: "Crew Duty Timeout", statutory_amount_eur: 250.0, metar_verdict: "Normal Conditions", parallel_departure_rate: "100.0%", flight_date: "2026-08-27" },
    { id: 4, flight_number: "BA117", carrier: "British Airways", route: "LHR ➔ JFK", delay_duration: "4h 50m", delay_reason: "ATC Bluff Disproved", statutory_amount_eur: 600.0, metar_verdict: "Clear Radar", parallel_departure_rate: "95.0%", flight_date: "2026-08-26" },
    { id: 5, flight_number: "KL1973", carrier: "KLM", route: "AMS ➔ BUD", delay_duration: "3h 15m", delay_reason: "Aircraft Rotation", statutory_amount_eur: 400.0, metar_verdict: "Normal Conditions", parallel_departure_rate: "98.2%", flight_date: "2026-08-25" }
  ]);

  const [ocrText, setOcrText] = useState(
    "PASSENGER: Alex Morgan\nFLIGHT: LH401 (Frankfurt -> JFK)\nPNR: PNR-LH992\nAIRPORT EXPENSE RECEIPT: EUR 65.00"
  );

  const [claimData, setClaimData] = useState({
    claimId: "CLM-2026-LH401-992",
    carrier: "Lufthansa",
    flightNumber: "LH401",
    pnr: "PNR-LH992",
    passengerName: "Alex Morgan",
    passengerEmail: "alex.morgan@example.com",
    delayDuration: "4h 15m",
    statutoryEur: 600.0,
    receiptsEur: 65.0,
    metarSummary: "Official METAR weather at Frankfurt (EDDF) confirmed VFR Clear (Visibility 10km). 93.8% of parallel flights departed normally. Airline weather excuse is EMPIRICALLY DISPROVED."
  });

  const [legalNotice, setLegalNotice] = useState(
    "FORMAL DEMAND FOR EU261 COMPENSATION\n\nFlight: LH401 (PNR: PNR-LH992)\nPassenger: Alex Morgan\nClaimed Total: €665.00\n\nMETAR weather audit confirms VFR Clear at Frankfurt Airport. Airline weather excuse is REJECTED.\nPlease remit payment within 14 calendar days."
  );

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/pipeline/eligible-flights')
      .then(res => res.json())
      .then(data => {
        if (data.status === "SUCCESS" && data.flights) {
          setEligibleFlights(data.flights);
        }
      })
      .catch(() => {});
  }, []);

  const handleSelectFlight = (fl: EligibleFlight) => {
    setClaimData({
      claimId: `CLM-2026-${fl.flight_number}-992`,
      carrier: fl.carrier,
      flightNumber: fl.flight_number,
      pnr: "PNR-LH992",
      passengerName: "Alex Morgan",
      passengerEmail: "alex.morgan@example.com",
      delayDuration: fl.delay_duration,
      statutoryEur: fl.statutory_amount_eur,
      receiptsEur: 65.0,
      metarSummary: `METAR weather audit for ${fl.flight_number}: ${fl.metar_verdict}. ${fl.parallel_departure_rate} parallel flights departed on schedule. Reason: ${fl.delay_reason}.`
    });

    setLegalNotice(
      `FORMAL DEMAND FOR EU261 COMPENSATION\n\nFlight: ${fl.flight_number} (PNR: PNR-LH992)\nCarrier: ${fl.carrier}\nPassenger: Alex Morgan\nClaimed Total: €${(fl.statutory_amount_eur + 65.0).toFixed(2)}\n\nReason: ${fl.delay_reason}. METAR weather audit confirms ${fl.metar_verdict}.\n\nPlease remit statutory payment of €${(fl.statutory_amount_eur + 65.0).toFixed(2)} within 14 calendar days.`
    );

    setActiveTab('claim');
  };

  const handleApprove = () => {
    confetti({ particleCount: 180, spread: 90, origin: { y: 0.5 } });
  };

  const filteredFlights = eligibleFlights.filter(fl => 
    fl.flight_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
    fl.carrier.toLowerCase().includes(searchQuery.toLowerCase()) ||
    fl.route.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const totalValue = claimData.statutoryEur + claimData.receiptsEur;

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#030712', color: '#F9FAFB', fontFamily: 'Inter, system-ui, -apple-system, sans-serif', backgroundImage: 'radial-gradient(ellipse at 50% 0%, rgba(14, 165, 233, 0.15), transparent 70%)' }}>
      
      {/* Top Floating Glass Header */}
      <header style={{ position: 'sticky', top: 0, zIndex: 50, backdropFilter: 'blur(16px)', backgroundColor: 'rgba(3, 7, 18, 0.8)', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', padding: '16px 40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <motion.div 
            whileHover={{ scale: 1.05, rotate: 5 }}
            style={{ width: '42px', height: '42px', borderRadius: '14px', background: 'linear-gradient(135deg, #0EA5E9, #6366F1)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 24px rgba(14, 165, 233, 0.5)' }}
          >
            <Plane size={24} color="#FFFFFF" />
          </motion.div>
          <div>
            <h1 style={{ fontSize: '19px', fontWeight: '800', margin: 0, letterSpacing: '-0.02em', background: 'linear-gradient(to right, #FFFFFF, #93C5FD)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              OmniClaim <span style={{ fontSize: '12px', padding: '2px 8px', borderRadius: '20px', backgroundColor: 'rgba(14, 165, 233, 0.2)', border: '1px solid rgba(14, 165, 233, 0.4)', color: '#38BDF8', marginLeft: '6px', textFillColor: 'initial', WebkitTextFillColor: '#38BDF8' }}>AI ENGINE</span>
            </h1>
            <p style={{ fontSize: '11px', color: '#9CA3AF', margin: 0, fontWeight: 500 }}>Autonomous Passenger Advocate &amp; Weather Bluff Disprover</p>
          </div>
        </div>

        {/* Header Badges */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <motion.div 
            animate={{ scale: [1, 1.03, 1] }} 
            transition={{ repeat: Infinity, duration: 3 }}
            style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 16px', borderRadius: '20px', backgroundColor: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', color: '#34D399', fontSize: '12px', fontWeight: '600' }}
          >
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#34D399', boxShadow: '0 0 10px #34D399' }}></span>
            Cloud Neural Agent 24/7 Active
          </motion.div>
        </div>
      </header>

      {/* Main Container */}
      <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '32px 40px' }}>
        
        {/* Animated Modern Tab Switcher */}
        <div style={{ display: 'flex', gap: '10px', backgroundColor: 'rgba(15, 23, 42, 0.6)', padding: '6px', borderRadius: '20px', border: '1px solid rgba(255, 255, 255, 0.08)', marginBottom: '36px', backdropFilter: 'blur(12px)' }}>
          {[
            { id: 'database', label: 'Eligible Flights DB', icon: Database, badge: eligibleFlights.length },
            { id: 'claim', label: 'Claim Inspector & Filer', icon: FileText, badge: 'Active' },
            { id: 'ocr', label: 'Vision OCR Ingestion', icon: Scan },
            { id: 'metar', label: 'METAR Weather Audit', icon: CloudRain }
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                style={{
                  position: 'relative',
                  flex: 1,
                  padding: '14px 20px',
                  borderRadius: '14px',
                  border: 'none',
                  backgroundColor: isActive ? '#0EA5E9' : 'transparent',
                  color: isActive ? '#FFFFFF' : '#9CA3AF',
                  fontSize: '13px',
                  fontWeight: '700',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '10px',
                  transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
                  boxShadow: isActive ? '0 0 24px rgba(14, 165, 233, 0.4)' : 'none'
                }}
              >
                <Icon size={18} color={isActive ? '#FFFFFF' : '#9CA3AF'} />
                <span>{tab.label}</span>
                {tab.badge && (
                  <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '10px', backgroundColor: isActive ? 'rgba(255, 255, 255, 0.2)' : 'rgba(255, 255, 255, 0.08)', color: '#FFFFFF' }}>
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        <AnimatePresence mode="wait">
          
          {/* TAB 1: ELIGIBLE FLIGHTS DATABASE */}
          {activeTab === 'database' && (
            <motion.div
              key="database"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ type: 'spring', stiffness: 350, damping: 25 }}
            >
              {/* Minimal Search Bar */}
              <div style={{ position: 'relative', marginBottom: '28px' }}>
                <Search size={20} color="#9CA3AF" style={{ position: 'absolute', left: '20px', top: '18px' }} />
                <input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Filter pre-audited flights by flight #, carrier, or route..."
                  style={{ width: '100%', backgroundColor: 'rgba(15, 23, 42, 0.6)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '18px', padding: '16px 20px 16px 54px', color: '#FFFFFF', fontSize: '14px', outline: 'none', backdropFilter: 'blur(10px)', boxSizing: 'border-box' }}
                />
              </div>

              {/* Cards Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '24px' }}>
                {filteredFlights.map((fl, idx) => (
                  <motion.div
                    key={fl.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    whileHover={{ scale: 1.015, translateY: -3 }}
                    style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', padding: '28px', borderRadius: '24px', border: '1px solid rgba(255, 255, 255, 0.08)', backdropFilter: 'blur(12px)', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}
                  >
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <span style={{ background: 'linear-gradient(135deg, #0EA5E9, #3B82F6)', padding: '6px 14px', borderRadius: '12px', fontSize: '15px', fontWeight: '800', color: '#FFFFFF', boxShadow: '0 0 16px rgba(14, 165, 233, 0.4)' }}>
                            {fl.flight_number}
                          </span>
                          <span style={{ fontSize: '14px', fontWeight: '600', color: '#93C5FD' }}>{fl.carrier}</span>
                        </div>
                        <span style={{ background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.4)', padding: '6px 14px', borderRadius: '14px', fontSize: '15px', fontWeight: '800', color: '#34D399' }}>
                          €{fl.statutory_amount_eur.toFixed(2)}
                        </span>
                      </div>

                      <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#FFFFFF', margin: '0 0 12px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {fl.route}
                      </h3>

                      <div style={{ display: 'flex', gap: '16px', fontSize: '13px', color: '#9CA3AF', marginBottom: '16px' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <Clock size={14} color="#FBBF24" /> Delay: <strong style={{ color: '#FBBF24' }}>{fl.delay_duration}</strong>
                        </span>
                        <span>Date: {fl.flight_date}</span>
                      </div>

                      <div style={{ backgroundColor: 'rgba(30, 41, 59, 0.6)', padding: '12px 16px', borderRadius: '14px', marginBottom: '20px', fontSize: '12px', color: '#E2E8F0', border: '1px solid rgba(255, 255, 255, 0.05)', lineHeight: 1.5 }}>
                        <div style={{ fontWeight: '700', color: '#38BDF8', marginBottom: '2px' }}>⚖️ Audit Verdict: {fl.delay_reason}</div>
                        <div style={{ color: '#94A3B8' }}>🌤️ METAR: {fl.metar_verdict} (Parallel Flights: {fl.parallel_departure_rate})</div>
                      </div>
                    </div>

                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleSelectFlight(fl)}
                      style={{ width: '100%', padding: '16px', borderRadius: '16px', border: 'none', background: 'linear-gradient(135deg, #0EA5E9, #4F46E5)', color: '#FFFFFF', fontWeight: '800', fontSize: '14px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', boxShadow: '0 4px 20px rgba(14, 165, 233, 0.3)' }}
                    >
                      <Sparkles size={18} /> Select Flight &amp; Generate Demand Package
                    </motion.button>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {/* TAB 2: CLAIM INSPECTOR & FILER */}
          {activeTab === 'claim' && (
            <motion.div
              key="claim"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ type: 'spring', stiffness: 350, damping: 25 }}
            >
              {/* Minimal Metrics Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '32px' }}>
                {[
                  { label: 'FLIGHT DELAY', val: claimData.delayDuration, sub: `${claimData.flightNumber} (${claimData.carrier})`, color: '#FBBF24' },
                  { label: 'STATUTORY CLAIM', val: `€${claimData.statutoryEur.toFixed(2)}`, sub: 'EU261 Article 7', color: '#34D399' },
                  { label: 'DUTY OF CARE EXPENSE', val: `€${claimData.receiptsEur.toFixed(2)}`, sub: 'Verified Airport Receipt', color: '#38BDF8' },
                  { label: 'TOTAL CLAIM VALUE', val: `€${totalValue.toFixed(2)}`, sub: '1-Click Approval Ready', color: '#FFFFFF', glow: true }
                ].map((stat, i) => (
                  <motion.div
                    key={i}
                    whileHover={{ translateY: -2 }}
                    style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', padding: '24px', borderRadius: '20px', border: stat.glow ? '1px solid rgba(14, 165, 233, 0.4)' : '1px solid rgba(255, 255, 255, 0.08)', backdropFilter: 'blur(12px)', boxShadow: stat.glow ? '0 0 24px rgba(14, 165, 233, 0.2)' : 'none' }}
                  >
                    <span style={{ fontSize: '11px', fontWeight: '800', color: '#9CA3AF', letterSpacing: '0.05em' }}>{stat.label}</span>
                    <h3 style={{ fontSize: '28px', fontWeight: '800', color: stat.color, margin: '8px 0 2px 0', letterSpacing: '-0.02em' }}>{stat.val}</h3>
                    <span style={{ fontSize: '12px', color: '#9CA3AF' }}>{stat.sub}</span>
                  </motion.div>
                ))}
              </div>

              {/* Split Screen Workspace */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '28px' }}>
                
                {/* Left Side: METAR & Editable Details */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                  <div style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', padding: '24px', borderRadius: '20px', border: '1px solid rgba(255, 255, 255, 0.08)', backdropFilter: 'blur(12px)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                      <CloudRain size={22} color="#FBBF24" />
                      <h3 style={{ fontSize: '15px', fontWeight: '700', color: '#38BDF8', margin: 0 }}>METAR WEATHER BLUFF AUDIT</h3>
                    </div>
                    <p style={{ fontSize: '13px', color: '#E2E8F0', margin: 0, lineHeight: 1.6 }}>{claimData.metarSummary}</p>
                  </div>

                  <div style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', padding: '24px', borderRadius: '20px', border: '1px solid rgba(255, 255, 255, 0.08)', backdropFilter: 'blur(12px)' }}>
                    <h3 style={{ fontSize: '15px', fontWeight: '700', color: '#FFFFFF', margin: '0 0 18px 0' }}>CLAIM DETAILS &amp; PASSENGER INFO</h3>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                      <div>
                        <label style={{ fontSize: '11px', color: '#9CA3AF', display: 'block', marginBottom: '4px', fontWeight: '600' }}>CARRIER</label>
                        <input value={claimData.carrier} onChange={(e) => setClaimData({...claimData, carrier: e.target.value})} style={{ width: '100%', backgroundColor: 'rgba(30, 41, 59, 0.6)', border: 'none', borderRadius: '12px', padding: '12px', color: '#38BDF8', fontSize: '13px', boxSizing: 'border-box' }} />
                      </div>

                      <div>
                        <label style={{ fontSize: '11px', color: '#9CA3AF', display: 'block', marginBottom: '4px', fontWeight: '600' }}>FLIGHT NUMBER</label>
                        <input value={claimData.flightNumber} onChange={(e) => setClaimData({...claimData, flightNumber: e.target.value})} style={{ width: '100%', backgroundColor: 'rgba(30, 41, 59, 0.6)', border: 'none', borderRadius: '12px', padding: '12px', color: '#38BDF8', fontSize: '13px', boxSizing: 'border-box' }} />
                      </div>

                      <div>
                        <label style={{ fontSize: '11px', color: '#9CA3AF', display: 'block', marginBottom: '4px', fontWeight: '600' }}>BOOKING PNR</label>
                        <input value={claimData.pnr} onChange={(e) => setClaimData({...claimData, pnr: e.target.value})} style={{ width: '100%', backgroundColor: 'rgba(30, 41, 59, 0.6)', border: 'none', borderRadius: '12px', padding: '12px', color: '#38BDF8', fontSize: '13px', boxSizing: 'border-box' }} />
                      </div>

                      <div>
                        <label style={{ fontSize: '11px', color: '#9CA3AF', display: 'block', marginBottom: '4px', fontWeight: '600' }}>PASSENGER NAME</label>
                        <input value={claimData.passengerName} onChange={(e) => setClaimData({...claimData, passengerName: e.target.value})} style={{ width: '100%', backgroundColor: 'rgba(30, 41, 59, 0.6)', border: 'none', borderRadius: '12px', padding: '12px', color: '#38BDF8', fontSize: '13px', boxSizing: 'border-box' }} />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Right Side: AI Translation & Demand Notice */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                  
                  {/* AI Translation Selector */}
                  <div style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', padding: '20px', borderRadius: '20px', border: '1px solid rgba(255, 255, 255, 0.08)', backdropFilter: 'blur(12px)' }}>
                    <div style={{ display: 'flex', gap: '12px' }}>
                      <input
                        value={targetLang}
                        onChange={(e) => setTargetLang(e.target.value)}
                        placeholder="Target language (German, Hungarian, Spanish...)"
                        style={{ flex: 1, backgroundColor: 'rgba(30, 41, 59, 0.6)', border: 'none', borderRadius: '12px', padding: '12px 16px', color: '#FFFFFF', fontSize: '13px' }}
                      />
                      <button
                        style={{ backgroundColor: '#0EA5E9', border: 'none', borderRadius: '12px', padding: '12px 20px', color: '#FFFFFF', fontWeight: '700', fontSize: '13px', cursor: 'pointer' }}
                      >
                        AI Translate
                      </button>
                    </div>
                  </div>

                  {/* Demand Notice */}
                  <div style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', padding: '24px', borderRadius: '20px', border: '1px solid rgba(255, 255, 255, 0.08)', backdropFilter: 'blur(12px)', flex: 1, display: 'flex', flexDirection: 'column' }}>
                    <h3 style={{ fontSize: '15px', fontWeight: '700', color: '#FFFFFF', margin: '0 0 12px 0' }}>LEGAL DEMAND NOTICE</h3>
                    <textarea
                      value={legalNotice}
                      onChange={(e) => setLegalNotice(e.target.value)}
                      rows={9}
                      style={{ width: '100%', backgroundColor: 'rgba(30, 41, 59, 0.6)', border: 'none', borderRadius: '16px', padding: '16px', color: '#F8FAFC', fontFamily: 'monospace', fontSize: '12px', lineHeight: 1.6, flex: 1, boxSizing: 'border-box', resize: 'none' }}
                    />

                    {/* Actions */}
                    <div style={{ display: 'flex', gap: '16px', marginTop: '20px' }}>
                      <a
                        href={`mailto:customer.relations@lufthansa.com?subject=EU261 Demand Notice - Flight ${claimData.flightNumber}&body=${encodeURIComponent(legalNotice)}`}
                        style={{ flex: 1, padding: '16px', borderRadius: '16px', backgroundColor: '#FB7185', color: '#FFFFFF', textDecoration: 'none', fontWeight: '800', textAlign: 'center', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
                      >
                        <Mail size={18} /> Open in Gmail
                      </a>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={handleApprove}
                        style={{ flex: 1, padding: '16px', borderRadius: '16px', border: 'none', backgroundColor: '#34D399', color: '#030712', fontWeight: '800', fontSize: '15px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', boxShadow: '0 0 20px rgba(52, 211, 153, 0.4)' }}
                      >
                        <CheckCircle2 size={18} /> Approve &amp; File Claim
                      </motion.button>
                    </div>
                  </div>

                </div>

              </div>
            </motion.div>
          )}

          {/* TAB 3: VISION OCR INGESTION */}
          {activeTab === 'ocr' && (
            <motion.div
              key="ocr"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ type: 'spring', stiffness: 350, damping: 25 }}
              style={{ maxWidth: '750px', margin: '0 auto' }}
            >
              <div style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', borderRadius: '24px', padding: '36px', border: '1px solid rgba(255, 255, 255, 0.08)', backdropFilter: 'blur(12px)', textAlign: 'center', marginBottom: '28px' }}>
                <Scan size={52} color="#0EA5E9" style={{ margin: '0 auto 16px auto' }} />
                <h2 style={{ fontSize: '20px', fontWeight: '800', margin: '0 0 6px 0', color: '#FFFFFF' }}>Multimodal Vision OCR Engine</h2>
                <p style={{ fontSize: '13px', color: '#9CA3AF', margin: 0 }}>Extract boarding pass details and expense receipts automatically</p>
              </div>

              <div style={{ marginBottom: '28px' }}>
                <textarea
                  value={ocrText}
                  onChange={(e) => setOcrText(e.target.value)}
                  rows={6}
                  style={{ width: '100%', backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '18px', padding: '20px', color: '#38BDF8', fontFamily: 'monospace', fontSize: '13px', outline: 'none', boxSizing: 'border-box' }}
                />
              </div>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setActiveTab('claim')}
                style={{ width: '100%', padding: '18px', borderRadius: '18px', border: 'none', background: 'linear-gradient(135deg, #0EA5E9, #4F46E5)', color: '#FFFFFF', fontSize: '15px', fontWeight: '800', cursor: 'pointer', boxShadow: '0 4px 24px rgba(14, 165, 233, 0.4)' }}
              >
                Parse Document &amp; Generate Claim Package
              </motion.button>
            </motion.div>
          )}

          {/* TAB 4: METAR WEATHER AUDIT */}
          {activeTab === 'metar' && (
            <motion.div
              key="metar"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ type: 'spring', stiffness: 350, damping: 25 }}
              style={{ maxWidth: '800px', margin: '0 auto' }}
            >
              <div style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', borderRadius: '24px', padding: '36px', border: '1px solid rgba(255, 255, 255, 0.08)', backdropFilter: 'blur(12px)', marginBottom: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
                  <CloudRain size={40} color="#FBBF24" />
                  <div>
                    <h2 style={{ fontSize: '20px', fontWeight: '800', margin: 0, color: '#FFFFFF' }}>METAR Weather Audit Engine</h2>
                    <p style={{ fontSize: '13px', color: '#38BDF8', margin: 0 }}>Empirically Disproves Airline Extraordinary Circumstance Excuses</p>
                  </div>
                </div>
                <p style={{ fontSize: '14px', color: '#E2E8F0', lineHeight: 1.6, margin: 0 }}>{claimData.metarSummary}</p>
              </div>
            </motion.div>
          )}

        </AnimatePresence>

      </div>
    </div>
  );
}
