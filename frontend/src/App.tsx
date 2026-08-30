import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Plane, 
  Scan, 
  Mail, 
  CloudRain, 
  CheckCircle2, 
  FileText,
  Database,
  Search,
  Sparkles,
  Clock,
  ArrowRight
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
  const [activeTab, setActiveTab] = useState<'database' | 'claim' | 'ocr'>('database');
  const [searchQuery, setSearchQuery] = useState("");
  const [targetLang, setTargetLang] = useState("German");

  const [eligibleFlights, setEligibleFlights] = useState<EligibleFlight[]>([
    { id: 1, flight_number: "LH401", carrier: "Lufthansa", route: "Frankfurt (FRA) ➔ New York (JFK)", delay_duration: "4h 15m", delay_reason: "Eligible (Weather Bluff Disproved)", statutory_amount_eur: 600.0, metar_verdict: "Good Weather", parallel_departure_rate: "93.8%", flight_date: "2026-08-28" },
    { id: 2, flight_number: "FR8821", carrier: "Ryanair", route: "London (STN) ➔ Budapest (BUD)", delay_duration: "3h 40m", delay_reason: "Eligible (Technical Defect)", statutory_amount_eur: 400.0, metar_verdict: "Normal", parallel_departure_rate: "100.0%", flight_date: "2026-08-28" },
    { id: 3, flight_number: "W62301", carrier: "Wizz Air", route: "Milan (MXP) ➔ Budapest (BUD)", delay_duration: "5h 10m", delay_reason: "Eligible (Crew Duty Timeout)", statutory_amount_eur: 250.0, metar_verdict: "Normal", parallel_departure_rate: "100.0%", flight_date: "2026-08-27" },
    { id: 4, flight_number: "BA117", carrier: "British Airways", route: "London (LHR) ➔ New York (JFK)", delay_duration: "4h 50m", delay_reason: "Eligible (ATC Bluff Disproved)", statutory_amount_eur: 600.0, metar_verdict: "Clear Radar", parallel_departure_rate: "95.0%", flight_date: "2026-08-26" },
    { id: 5, flight_number: "KL1973", carrier: "KLM", route: "Amsterdam (AMS) ➔ Budapest (BUD)", delay_duration: "3h 15m", delay_reason: "Eligible (Aircraft Rotation)", statutory_amount_eur: 400.0, metar_verdict: "Normal", parallel_departure_rate: "98.2%", flight_date: "2026-08-25" }
  ]);

  const [ocrText, setOcrText] = useState(
    "PASSENGER: Alex Morgan\nFLIGHT: LH401\nPNR: PNR-LH992\nRECEIPT: EUR 65.00"
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
  });

  const [legalNotice, setLegalNotice] = useState(
    "FORMAL DEMAND FOR EU261 COMPENSATION\n\nFlight: LH401 (PNR: PNR-LH992)\nPassenger: Alex Morgan\nTotal Entitlement: €665.00\n\nPlease remit statutory payment of €665.00 within 14 calendar days."
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
    });

    setLegalNotice(
      `FORMAL DEMAND FOR EU261 COMPENSATION\n\nFlight: ${fl.flight_number} (PNR: PNR-LH992)\nCarrier: ${fl.carrier}\nPassenger: Alex Morgan\nTotal Entitlement: €${(fl.statutory_amount_eur + 65.0).toFixed(2)}\n\nPlease remit statutory payment within 14 calendar days.`
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
    <div style={{ minHeight: '100vh', backgroundColor: '#090D16', color: '#F9FAFB', fontFamily: 'Inter, system-ui, -apple-system, sans-serif' }}>
      
      {/* High Contrast Crystal Clear Header */}
      <header style={{ position: 'sticky', top: 0, zIndex: 50, backgroundColor: '#0F172A', borderBottom: '1px solid #1E293B', padding: '16px 40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{ width: '42px', height: '42px', borderRadius: '12px', backgroundColor: '#0EA5E9', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Plane size={24} color="#FFFFFF" />
          </div>
          <div>
            <h1 style={{ fontSize: '22px', fontWeight: '800', margin: 0, color: '#FFFFFF', letterSpacing: '-0.01em' }}>
              OmniClaim <span style={{ fontSize: '12px', padding: '2px 8px', borderRadius: '6px', backgroundColor: '#0284C7', color: '#FFFFFF', marginLeft: '6px', fontWeight: '700' }}>AI</span>
            </h1>
            <p style={{ fontSize: '12px', color: '#94A3B8', margin: 0 }}>Automated Flight Compensation Advocate</p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', backgroundColor: '#1E293B', padding: '6px 14px', borderRadius: '20px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#10B981' }}></span>
          <span style={{ fontSize: '12px', fontWeight: '600', color: '#10B981' }}>Active</span>
        </div>
      </header>

      {/* Main Workspace */}
      <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '32px 24px' }}>
        
        {/* Minimal Navigation Tabs */}
        <div style={{ display: 'flex', gap: '8px', backgroundColor: '#0F172A', padding: '6px', borderRadius: '16px', border: '1px solid #1E293B', marginBottom: '32px' }}>
          {[
            { id: 'database', label: 'Eligible Delayed Flights', icon: Database, count: eligibleFlights.length },
            { id: 'claim', label: 'Active Claim Details', icon: FileText },
            { id: 'ocr', label: 'Scan Boarding Pass', icon: Scan }
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                style={{
                  flex: 1,
                  padding: '12px 18px',
                  borderRadius: '12px',
                  border: 'none',
                  backgroundColor: isActive ? '#0EA5E9' : 'transparent',
                  color: isActive ? '#FFFFFF' : '#94A3B8',
                  fontSize: '14px',
                  fontWeight: '700',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  transition: 'all 0.2s'
                }}
              >
                <Icon size={18} color={isActive ? '#FFFFFF' : '#94A3B8'} />
                <span>{tab.label}</span>
                {tab.count !== undefined && (
                  <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '10px', backgroundColor: isActive ? 'rgba(255, 255, 255, 0.25)' : '#1E293B', color: '#FFFFFF' }}>
                    {tab.count}
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
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              {/* Filter Input */}
              <div style={{ position: 'relative', marginBottom: '24px' }}>
                <Search size={18} color="#94A3B8" style={{ position: 'absolute', left: '16px', top: '16px' }} />
                <input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Filter flights by number, airline, or destination..."
                  style={{ width: '100%', backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '14px', padding: '14px 16px 14px 46px', color: '#FFFFFF', fontSize: '14px', outline: 'none', boxSizing: 'border-box' }}
                />
              </div>

              {/* Clean Cards Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
                {filteredFlights.map((fl) => (
                  <div
                    key={fl.id}
                    style={{ backgroundColor: '#0F172A', padding: '24px', borderRadius: '20px', border: '1px solid #1E293B', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}
                  >
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                          <span style={{ backgroundColor: '#0EA5E9', padding: '6px 12px', borderRadius: '8px', fontSize: '15px', fontWeight: '800', color: '#FFFFFF' }}>
                            {fl.flight_number}
                          </span>
                          <span style={{ fontSize: '14px', fontWeight: '600', color: '#94A3B8' }}>{fl.carrier}</span>
                        </div>
                        <span style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.4)', padding: '6px 14px', borderRadius: '10px', fontSize: '16px', fontWeight: '800', color: '#34D399' }}>
                          €{fl.statutory_amount_eur.toFixed(2)}
                        </span>
                      </div>

                      <h3 style={{ fontSize: '17px', fontWeight: '700', color: '#FFFFFF', margin: '0 0 10px 0' }}>
                        {fl.route}
                      </h3>

                      <div style={{ fontSize: '13px', color: '#94A3B8', marginBottom: '16px' }}>
                        ⏱️ Delay: <strong style={{ color: '#FBBF24' }}>{fl.delay_duration}</strong> | Date: {fl.flight_date}
                      </div>
                    </div>

                    <button
                      onClick={() => handleSelectFlight(fl)}
                      style={{ width: '100%', padding: '14px', borderRadius: '12px', border: 'none', backgroundColor: '#0EA5E9', color: '#FFFFFF', fontWeight: '700', fontSize: '14px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
                    >
                      <Sparkles size={16} /> File Claim (€{fl.statutory_amount_eur.toFixed(0)})
                    </button>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* TAB 2: ACTIVE CLAIM WORKSPACE */}
          {activeTab === 'claim' && (
            <motion.div
              key="claim"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              {/* Summary Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
                <div style={{ backgroundColor: '#0F172A', padding: '20px', borderRadius: '16px', border: '1px solid #1E293B' }}>
                  <span style={{ fontSize: '11px', fontWeight: '700', color: '#94A3B8', textTransform: 'uppercase' }}>Selected Flight</span>
                  <h3 style={{ fontSize: '22px', fontWeight: '800', color: '#FBBF24', margin: '4px 0 0 0' }}>{claimData.flightNumber}</h3>
                  <span style={{ fontSize: '12px', color: '#94A3B8' }}>{claimData.carrier} ({claimData.delayDuration} delay)</span>
                </div>

                <div style={{ backgroundColor: '#0F172A', padding: '20px', borderRadius: '16px', border: '1px solid #1E293B' }}>
                  <span style={{ fontSize: '11px', fontWeight: '700', color: '#94A3B8', textTransform: 'uppercase' }}>Statutory Entitlement</span>
                  <h3 style={{ fontSize: '22px', fontWeight: '800', color: '#34D399', margin: '4px 0 0 0' }}>€{claimData.statutoryEur.toFixed(2)}</h3>
                  <span style={{ fontSize: '12px', color: '#94A3B8' }}>EU261 Rights Verified</span>
                </div>

                <div style={{ backgroundColor: '#0F172A', padding: '20px', borderRadius: '16px', border: '1px solid #1E293B' }}>
                  <span style={{ fontSize: '11px', fontWeight: '700', color: '#94A3B8', textTransform: 'uppercase' }}>Total Payout Claim</span>
                  <h3 style={{ fontSize: '24px', fontWeight: '800', color: '#FFFFFF', margin: '4px 0 0 0' }}>€{totalValue.toFixed(2)}</h3>
                  <span style={{ fontSize: '12px', color: '#38BDF8' }}>Includes €65 Expense</span>
                </div>
              </div>

              {/* Form & Demand Notice Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                
                {/* Left: Patient Details */}
                <div style={{ backgroundColor: '#0F172A', padding: '24px', borderRadius: '20px', border: '1px solid #1E293B' }}>
                  <h3 style={{ fontSize: '15px', fontWeight: '700', color: '#FFFFFF', margin: '0 0 16px 0' }}>Passenger &amp; Flight Info</h3>
                  
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                    <div>
                      <label style={{ fontSize: '11px', color: '#94A3B8', display: 'block', marginBottom: '4px' }}>AIRLINE</label>
                      <input value={claimData.carrier} onChange={(e) => setClaimData({...claimData, carrier: e.target.value})} style={{ width: '100%', backgroundColor: '#1E293B', border: 'none', borderRadius: '10px', padding: '10px', color: '#38BDF8', fontSize: '13px', boxSizing: 'border-box' }} />
                    </div>

                    <div>
                      <label style={{ fontSize: '11px', color: '#94A3B8', display: 'block', marginBottom: '4px' }}>FLIGHT #</label>
                      <input value={claimData.flightNumber} onChange={(e) => setClaimData({...claimData, flightNumber: e.target.value})} style={{ width: '100%', backgroundColor: '#1E293B', border: 'none', borderRadius: '10px', padding: '10px', color: '#38BDF8', fontSize: '13px', boxSizing: 'border-box' }} />
                    </div>

                    <div>
                      <label style={{ fontSize: '11px', color: '#94A3B8', display: 'block', marginBottom: '4px' }}>BOOKING PNR</label>
                      <input value={claimData.pnr} onChange={(e) => setClaimData({...claimData, pnr: e.target.value})} style={{ width: '100%', backgroundColor: '#1E293B', border: 'none', borderRadius: '10px', padding: '10px', color: '#38BDF8', fontSize: '13px', boxSizing: 'border-box' }} />
                    </div>

                    <div>
                      <label style={{ fontSize: '11px', color: '#94A3B8', display: 'block', marginBottom: '4px' }}>PASSENGER NAME</label>
                      <input value={claimData.passengerName} onChange={(e) => setClaimData({...claimData, passengerName: e.target.value})} style={{ width: '100%', backgroundColor: '#1E293B', border: 'none', borderRadius: '10px', padding: '10px', color: '#38BDF8', fontSize: '13px', boxSizing: 'border-box' }} />
                    </div>
                  </div>
                </div>

                {/* Right: Legal Notice */}
                <div style={{ backgroundColor: '#0F172A', padding: '24px', borderRadius: '20px', border: '1px solid #1E293B', display: 'flex', flexDirection: 'column' }}>
                  <h3 style={{ fontSize: '15px', fontWeight: '700', color: '#FFFFFF', margin: '0 0 12px 0' }}>Demand Notice</h3>
                  <textarea
                    value={legalNotice}
                    onChange={(e) => setLegalNotice(e.target.value)}
                    rows={8}
                    style={{ width: '100%', backgroundColor: '#1E293B', border: 'none', borderRadius: '12px', padding: '14px', color: '#F8FAFC', fontFamily: 'monospace', fontSize: '12px', lineHeight: 1.5, flex: 1, boxSizing: 'border-box', resize: 'none' }}
                  />

                  <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
                    <a
                      href={`mailto:customer.relations@lufthansa.com?subject=EU261 Demand Notice - Flight ${claimData.flightNumber}&body=${encodeURIComponent(legalNotice)}`}
                      style={{ flex: 1, padding: '14px', borderRadius: '12px', backgroundColor: '#E11D48', color: '#FFFFFF', textDecoration: 'none', fontWeight: '700', textAlign: 'center', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', fontSize: '13px' }}
                    >
                      <Mail size={16} /> Open Gmail
                    </a>
                    <button
                      onClick={handleApprove}
                      style={{ flex: 1, padding: '14px', borderRadius: '12px', border: 'none', backgroundColor: '#10B981', color: '#090D16', fontWeight: '800', fontSize: '14px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
                    >
                      <CheckCircle2 size={16} /> Approve &amp; Send
                    </button>
                  </div>
                </div>

              </div>
            </motion.div>
          )}

          {/* TAB 3: SCAN BOARDING PASS */}
          {activeTab === 'ocr' && (
            <motion.div
              key="ocr"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              style={{ maxWidth: '650px', margin: '0 auto' }}
            >
              <div style={{ backgroundColor: '#0F172A', borderRadius: '20px', padding: '32px', border: '1px solid #1E293B', textAlign: 'center', marginBottom: '24px' }}>
                <Scan size={48} color="#0EA5E9" style={{ margin: '0 auto 12px auto' }} />
                <h2 style={{ fontSize: '18px', fontWeight: '700', margin: '0 0 6px 0', color: '#FFFFFF' }}>Scan Boarding Pass or Receipt</h2>
                <p style={{ fontSize: '13px', color: '#94A3B8', margin: 0 }}>Paste text or scan document</p>
              </div>

              <textarea
                value={ocrText}
                onChange={(e) => setOcrText(e.target.value)}
                rows={5}
                style={{ width: '100%', backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '14px', padding: '16px', color: '#38BDF8', fontFamily: 'monospace', fontSize: '13px', outline: 'none', boxSizing: 'border-box', marginBottom: '20px' }}
              />

              <button
                onClick={() => setActiveTab('claim')}
                style={{ width: '100%', padding: '16px', borderRadius: '12px', border: 'none', backgroundColor: '#0EA5E9', color: '#FFFFFF', fontSize: '15px', fontWeight: '700', cursor: 'pointer' }}
              >
                Parse Document &amp; Generate Claim
              </button>
            </motion.div>
          )}

        </AnimatePresence>

      </div>
    </div>
  );
}
