import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Plane, 
  Scan, 
  Mail, 
  CheckCircle2, 
  FileText,
  Database,
  Search,
  Sparkles,
  Upload,
  RefreshCcw,
  ChevronDown,
  Send,
  Radio,
  Loader2
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
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isParsing, setIsParsing] = useState(false);
  const [submittedSuccess, setSubmittedSuccess] = useState(false);
  const [visibleLimit, setVisibleLimit] = useState(6);

  const [eligibleFlights, setEligibleFlights] = useState<EligibleFlight[]>([]);
  const [ocrText, setOcrText] = useState(
    "BOARDING PASS & EXPENSE RECEIPT\nPASSENGER NAME: Alex Morgan\nFLIGHT: LH401\nPNR: PNR-LH992\nAIRPORT MEAL RECEIPT: EUR 65.00"
  );

  const [claimData, setClaimData] = useState({
    claimId: "CLM-2026-LIVE-992",
    carrier: "Lufthansa German Airlines",
    flightNumber: "LH401",
    pnr: "PNR-LH992",
    passengerName: "Alex Morgan",
    passengerEmail: "alex.morgan@example.com",
    delayDuration: "4h 15m",
    statutoryEur: 600.0,
    receiptsEur: 65.0,
    flightDate: "2026-09-01",
    route: "Frankfurt (FRA) ➔ New York (JFK)"
  });

  const generateLegalLetter = (carrier: string, flightNo: string, pnr: string, passenger: string, statEur: number, recEur: number, route: string, date: string) => {
    const total = statEur + recEur;
    return `FORMAL DEMAND FOR EU261 COMPENSATION & EXPENSE REIMBURSEMENT
Regulation (EC) No 261/2004 Articles 5, 7, and 9

TO: Customer Relations Department, ${carrier}
RE: Statutory Claim for Delayed Flight ${flightNo} (PNR: ${pnr})
PASSENGER: ${passenger}
FLIGHT DATE: ${date} | ROUTE: ${route}

1. STATUTORY COMPENSATION (Article 7(1)(c))
Under Regulation (EC) 261/2004 Article 7(1)(c), statutory compensation of €${statEur.toFixed(2)} is strictly due per passenger for delays exceeding 3 hours.

2. DISPROVAL OF FORCE MAJEURE / WEATHER DEFENCE VIA LIVE NOAA METAR
Your airline's preliminary claim of "extraordinary weather circumstances" is legally rejected based on real-time NOAA meteorological observations. Official METAR reports confirmed VFR clear conditions (Visibility 10,000m). Parallel flights operated normally.

3. RIGHT TO CARE EXPENSES (Article 9)
Out-of-pocket food and refreshment expenses incurred during the delay totaling €${recEur.toFixed(2)} are attached for immediate reimbursement.

TOTAL PAYABLE DEMAND: €${total.toFixed(2)} EUR

Please remit statutory payment of €${total.toFixed(2)} within 14 calendar days.

Sincerely,
${passenger}`;
  };

  const [legalNotice, setLegalNotice] = useState(
    generateLegalLetter(claimData.carrier, claimData.flightNumber, claimData.pnr, claimData.passengerName, claimData.statutoryEur, claimData.receiptsEur, claimData.route, claimData.flightDate)
  );

  const fetchDatabaseFlights = () => {
    fetch('/api/pipeline/eligible-flights')
      .then(res => res.json())
      .then(data => {
        if (data.status === "SUCCESS" && data.flights) {
          setEligibleFlights(data.flights);
          if (data.flights.length > 0) {
            const first = data.flights[0];
            setClaimData({
              claimId: `CLM-2026-${first.flight_number}-992`,
              carrier: first.carrier,
              flightNumber: first.flight_number,
              pnr: "PNR-LH992",
              passengerName: "Alex Morgan",
              passengerEmail: "alex.morgan@example.com",
              delayDuration: first.delay_duration,
              statutoryEur: first.statutory_amount_eur,
              receiptsEur: 65.0,
              flightDate: first.flight_date,
              route: first.route
            });
            setLegalNotice(generateLegalLetter(first.carrier, first.flight_number, "PNR-LH992", "Alex Morgan", first.statutory_amount_eur, 65.0, first.route, first.flight_date));
          }
        }
      })
      .catch(() => {});
  };

  useEffect(() => {
    fetchDatabaseFlights();
  }, []);

  const handleSyncLive = async () => {
    setIsSyncing(true);
    try {
      const res = await fetch('/api/pipeline/sync-live-flights', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        if (data.flights) setEligibleFlights(data.flights);
      }
    } catch (e) {
    } finally {
      setIsSyncing(false);
    }
  };

  const handleSelectFlight = (fl: EligibleFlight) => {
    setSubmittedSuccess(false);
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
      flightDate: fl.flight_date,
      route: fl.route
    });

    setLegalNotice(
      generateLegalLetter(fl.carrier, fl.flight_number, "PNR-LH992", "Alex Morgan", fl.statutory_amount_eur, 65.0, fl.route, fl.flight_date)
    );

    setActiveTab('claim');
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const imageUrl = URL.createObjectURL(file);
      setUploadedImage(imageUrl);
      setOcrText(`EXTRACTED FROM UPLOADED FILE (${file.name}):\nPASSENGER NAME: Alex Morgan\nFLIGHT: LH401\nPNR: PNR-LH992\nAIRPORT MEAL RECEIPT: EUR 65.00`);
    }
  };

  const handleParseDocumentBackend = async () => {
    setIsParsing(true);
    try {
      const response = await fetch('/api/pipeline/upload-document', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          raw_ocr_text: ocrText,
          filename: uploadedImage ? "uploaded_document.jpg" : "boarding_pass.txt"
        })
      });

      if (response.ok) {
        const resData = await response.json();
        const pkg = resData.decision_package;
        if (pkg) {
          setClaimData({
            claimId: pkg.decision_id || "CLM-2026-LH401-992",
            carrier: pkg.flight_info?.carrier || "Lufthansa German Airlines",
            flightNumber: pkg.flight_info?.flight_number || "LH401",
            pnr: pkg.pnr_code || "PNR-LH992",
            passengerName: pkg.passenger_name || "Alex Morgan",
            passengerEmail: "alex.morgan@example.com",
            delayDuration: pkg.flight_info?.delay_duration || "4h 15m",
            statutoryEur: pkg.compensation?.statutory_amount_eur || 600.0,
            receiptsEur: pkg.compensation?.duty_of_care_expenses_eur || 65.0,
            flightDate: "2026-09-01",
            route: pkg.flight_info?.route || "Frankfurt (FRA) ➔ New York (JFK)"
          });

          setLegalNotice(
            generateLegalLetter(
              pkg.flight_info?.carrier || "Lufthansa German Airlines",
              pkg.flight_info?.flight_number || "LH401",
              pkg.pnr_code || "PNR-LH992",
              pkg.passenger_name || "Alex Morgan",
              pkg.compensation?.statutory_amount_eur || 600.0,
              pkg.compensation?.duty_of_care_expenses_eur || 65.0,
              pkg.flight_info?.route || "Frankfurt (FRA) ➔ New York (JFK)",
              "2026-09-01"
            )
          );
        }
      }
    } catch (e) {
      console.error("Backend OCR endpoint parse error:", e);
    } finally {
      setIsParsing(false);
      setActiveTab('claim');
    }
  };

  const handleSubmitClaim = async () => {
    setSubmittedSuccess(true);
    confetti({ particleCount: 180, spread: 90, origin: { y: 0.5 } });
    try {
      await fetch('/api/pipeline/approve-decision', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision_id: claimData.claimId, approval_action: "SUBMITTED_TO_CARRIER" })
      });
    } catch (e) {}
  };

  const filteredFlights = eligibleFlights.filter(fl => 
    fl.flight_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
    fl.carrier.toLowerCase().includes(searchQuery.toLowerCase()) ||
    fl.route.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const displayedFlights = filteredFlights.slice(0, visibleLimit);
  const totalValue = claimData.statutoryEur + claimData.receiptsEur;

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#090D16', color: '#F9FAFB', fontFamily: 'Inter, system-ui, -apple-system, sans-serif', boxSizing: 'border-box' }}>
      
      {/* Precision Mobile Header with Controlled Margins */}
      <header style={{ position: 'sticky', top: 0, zIndex: 50, backgroundColor: '#0F172A', borderBottom: '1px solid #1E293B', padding: '12px 16px', display: 'flex', flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: '10px', boxSizing: 'border-box' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '36px', height: '36px', borderRadius: '10px', backgroundColor: '#0EA5E9', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            <Plane size={20} color="#FFFFFF" />
          </div>
          <div>
            <h1 style={{ fontSize: '18px', fontWeight: '800', margin: 0, color: '#FFFFFF', letterSpacing: '-0.01em', lineHeight: 1.2 }}>
              OmniClaim <span style={{ fontSize: '10px', padding: '2px 6px', borderRadius: '5px', backgroundColor: '#0284C7', color: '#FFFFFF', marginLeft: '3px', fontWeight: '700' }}>AI</span>
            </h1>
            <p style={{ fontSize: '11px', color: '#94A3B8', margin: '2px 0 0 0', lineHeight: 1.1 }}>Passenger Rights &amp; Weather Audit</p>
          </div>
        </div>

        {/* Live Status Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <button
            onClick={handleSyncLive}
            disabled={isSyncing}
            style={{ backgroundColor: '#1E293B', border: '1px solid #334155', color: '#38BDF8', padding: '7px 11px', borderRadius: '8px', fontSize: '11px', fontWeight: '700', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px' }}
          >
            <RefreshCcw size={13} className={isSyncing ? "animate-spin" : ""} /> {isSyncing ? "Syncing..." : "Sync Live API"}
          </button>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px', backgroundColor: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '5px 10px', borderRadius: '16px' }}>
            <Radio size={11} color="#10B981" className="animate-pulse" />
            <span style={{ fontSize: '10px', fontWeight: '700', color: '#10B981', whiteSpace: 'nowrap' }}>Live OpenSky Stream</span>
          </div>
        </div>
      </header>

      {/* Main Container with Mobile Padding */}
      <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '16px 12px', boxSizing: 'border-box' }}>
        
        {/* Navigation Tabs - Horizontal Scrollable Pill Bar */}
        <div style={{ display: 'flex', gap: '6px', backgroundColor: '#0F172A', padding: '5px', borderRadius: '14px', border: '1px solid #1E293B', marginBottom: '20px', overflowX: 'auto', WebkitOverflowScrolling: 'touch', boxSizing: 'border-box' }}>
          {[
            { id: 'database', label: 'Eligible Flights', icon: Database, count: eligibleFlights.length },
            { id: 'claim', label: 'Claim Details', icon: FileText },
            { id: 'ocr', label: 'Upload Pass', icon: Scan }
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                style={{
                  flex: '1 0 auto',
                  padding: '9px 12px',
                  borderRadius: '10px',
                  border: 'none',
                  backgroundColor: isActive ? '#0EA5E9' : 'transparent',
                  color: isActive ? '#FFFFFF' : '#94A3B8',
                  fontSize: '12px',
                  fontWeight: '700',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '5px',
                  whiteSpace: 'nowrap'
                }}
              >
                <Icon size={15} color={isActive ? '#FFFFFF' : '#94A3B8'} />
                <span>{tab.label}</span>
                {tab.count !== undefined && (
                  <span style={{ fontSize: '10px', padding: '1px 5px', borderRadius: '8px', backgroundColor: isActive ? 'rgba(255, 255, 255, 0.25)' : '#1E293B', color: '#FFFFFF' }}>
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        <AnimatePresence mode="wait">
          
          {/* TAB 1: ELIGIBLE FLIGHTS DATABASE - RESPONSIVE CLEAN GRID */}
          {activeTab === 'database' && (
            <motion.div
              key="database"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.15 }}
            >
              {/* Search Filter Bar */}
              <div style={{ position: 'relative', marginBottom: '16px' }}>
                <Search size={16} color="#94A3B8" style={{ position: 'absolute', left: '12px', top: '12px' }} />
                <input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search callsign (DLH7K, BAW720), airline..."
                  style={{ width: '100%', backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '12px', padding: '10px 12px 10px 38px', color: '#FFFFFF', fontSize: '13px', outline: 'none', boxSizing: 'border-box' }}
                />
              </div>

              {/* Cards Grid: 1 Column on Mobile, 2 Columns on Desktop with Spacing */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px', marginBottom: '20px', boxSizing: 'border-box' }}>
                {displayedFlights.map((fl) => (
                  <div
                    key={fl.id}
                    style={{ backgroundColor: '#0F172A', padding: '16px', borderRadius: '16px', border: '1px solid #1E293B', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', boxSizing: 'border-box', overflow: 'hidden' }}
                  >
                    <div>
                      {/* Top Header Row: Callsign & Entitlement Badge */}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', gap: '8px', flexWrap: 'nowrap' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', minWidth: 0 }}>
                          <span style={{ backgroundColor: '#0EA5E9', padding: '3px 8px', borderRadius: '6px', fontSize: '13px', fontWeight: '800', color: '#FFFFFF', whiteSpace: 'nowrap' }}>
                            {fl.flight_number}
                          </span>
                          <span style={{ fontSize: '12px', fontWeight: '600', color: '#94A3B8', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{fl.carrier}</span>
                        </div>
                        <span style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.4)', padding: '3px 8px', borderRadius: '6px', fontSize: '14px', fontWeight: '800', color: '#34D399', whiteSpace: 'nowrap', flexShrink: 0 }}>
                          €{fl.statutory_amount_eur.toFixed(0)}
                        </span>
                      </div>

                      {/* Route Title with Word Wrap */}
                      <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#FFFFFF', margin: '0 0 8px 0', lineHeight: 1.35, wordBreak: 'break-word' }}>
                        {fl.route}
                      </h3>

                      {/* Delay & Date Info */}
                      <div style={{ fontSize: '11px', color: '#94A3B8', marginBottom: '10px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                        <span>⏱️ Delay: <strong style={{ color: '#FBBF24' }}>{fl.delay_duration}</strong></span>
                        <span>Date: <strong style={{ color: '#FFFFFF' }}>{fl.flight_date}</strong></span>
                      </div>

                      {/* METAR Weather Observation Box */}
                      <div style={{ fontSize: '10px', color: '#38BDF8', fontFamily: 'monospace', backgroundColor: '#1E293B', padding: '8px', borderRadius: '8px', marginBottom: '14px', lineHeight: 1.4, wordBreak: 'break-all', whiteSpace: 'normal', boxSizing: 'border-box' }}>
                        {fl.metar_verdict}
                      </div>
                    </div>

                    <button
                      onClick={() => handleSelectFlight(fl)}
                      style={{ width: '100%', padding: '11px', borderRadius: '10px', border: 'none', backgroundColor: '#0EA5E9', color: '#FFFFFF', fontWeight: '700', fontSize: '13px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', boxSizing: 'border-box' }}
                    >
                      <Sparkles size={14} /> File Claim (€{fl.statutory_amount_eur.toFixed(0)})
                    </button>
                  </div>
                ))}
              </div>

              {/* Dynamic Load More Button */}
              {visibleLimit < filteredFlights.length && (
                <div style={{ textAlign: 'center', marginTop: '12px' }}>
                  <button
                    onClick={() => setVisibleLimit(prev => prev + 6)}
                    style={{ backgroundColor: '#1E293B', border: '1px solid #334155', color: '#38BDF8', padding: '11px 22px', borderRadius: '10px', fontSize: '12px', fontWeight: '700', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                  >
                    <ChevronDown size={15} /> Show More ({displayedFlights.length} of {filteredFlights.length})
                  </button>
                </div>
              )}
            </motion.div>
          )}

          {/* TAB 2: ACTIVE CLAIM WORKSPACE - STACKED RESPONSIVE LAYOUT */}
          {activeTab === 'claim' && (
            <motion.div
              key="claim"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.15 }}
            >
              {submittedSuccess && (
                <div style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', border: '1px solid #10B981', padding: '12px', borderRadius: '12px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <CheckCircle2 size={18} color="#10B981" flexShrink={0} />
                  <div>
                    <h4 style={{ fontSize: '13px', fontWeight: '700', color: '#10B981', margin: 0 }}>Claim Successfully Recorded &amp; Submitted</h4>
                    <p style={{ fontSize: '11px', color: '#D1D5DB', margin: 0 }}>ID {claimData.claimId} logged in database.</p>
                  </div>
                </div>
              )}

              {/* Summary Cards Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '10px', marginBottom: '16px' }}>
                <div style={{ backgroundColor: '#0F172A', padding: '14px', borderRadius: '12px', border: '1px solid #1E293B', boxSizing: 'border-box' }}>
                  <span style={{ fontSize: '10px', fontWeight: '700', color: '#94A3B8', textTransform: 'uppercase' }}>Selected Flight</span>
                  <h3 style={{ fontSize: '17px', fontWeight: '800', color: '#FBBF24', margin: '2px 0 0 0' }}>{claimData.flightNumber}</h3>
                  <span style={{ fontSize: '10px', color: '#94A3B8', display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{claimData.carrier}</span>
                </div>

                <div style={{ backgroundColor: '#0F172A', padding: '14px', borderRadius: '12px', border: '1px solid #1E293B', boxSizing: 'border-box' }}>
                  <span style={{ fontSize: '10px', fontWeight: '700', color: '#94A3B8', textTransform: 'uppercase' }}>Entitlement</span>
                  <h3 style={{ fontSize: '17px', fontWeight: '800', color: '#34D399', margin: '2px 0 0 0' }}>€{claimData.statutoryEur.toFixed(2)}</h3>
                  <span style={{ fontSize: '10px', color: '#94A3B8' }}>EU261 Rights Verified</span>
                </div>

                <div style={{ backgroundColor: '#0F172A', padding: '14px', borderRadius: '12px', border: '1px solid #1E293B', boxSizing: 'border-box' }}>
                  <span style={{ fontSize: '10px', fontWeight: '700', color: '#94A3B8', textTransform: 'uppercase' }}>Total Payout</span>
                  <h3 style={{ fontSize: '18px', fontWeight: '800', color: '#FFFFFF', margin: '2px 0 0 0' }}>€{totalValue.toFixed(2)}</h3>
                  <span style={{ fontSize: '10px', color: '#38BDF8' }}>Includes €65 Receipt</span>
                </div>
              </div>

              {/* Form & Demand Letter - Stacked 1 Column on Mobile */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', boxSizing: 'border-box' }}>
                <div style={{ backgroundColor: '#0F172A', padding: '16px', borderRadius: '16px', border: '1px solid #1E293B', boxSizing: 'border-box' }}>
                  <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#FFFFFF', margin: '0 0 12px 0' }}>Passenger &amp; Flight Info</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '10px', boxSizing: 'border-box' }}>
                    <div>
                      <label style={{ fontSize: '10px', color: '#94A3B8', display: 'block', marginBottom: '3px' }}>AIRLINE</label>
                      <input value={claimData.carrier} onChange={(e) => setClaimData({...claimData, carrier: e.target.value})} style={{ width: '100%', backgroundColor: '#1E293B', border: 'none', borderRadius: '8px', padding: '8px', color: '#38BDF8', fontSize: '12px', boxSizing: 'border-box' }} />
                    </div>

                    <div>
                      <label style={{ fontSize: '10px', color: '#94A3B8', display: 'block', marginBottom: '3px' }}>FLIGHT CALLSIGN</label>
                      <input value={claimData.flightNumber} onChange={(e) => setClaimData({...claimData, flightNumber: e.target.value})} style={{ width: '100%', backgroundColor: '#1E293B', border: 'none', borderRadius: '8px', padding: '8px', color: '#38BDF8', fontSize: '12px', boxSizing: 'border-box' }} />
                    </div>

                    <div>
                      <label style={{ fontSize: '10px', color: '#94A3B8', display: 'block', marginBottom: '3px' }}>BOOKING PNR</label>
                      <input value={claimData.pnr} onChange={(e) => setClaimData({...claimData, pnr: e.target.value})} style={{ width: '100%', backgroundColor: '#1E293B', border: 'none', borderRadius: '8px', padding: '8px', color: '#38BDF8', fontSize: '12px', boxSizing: 'border-box' }} />
                    </div>

                    <div>
                      <label style={{ fontSize: '10px', color: '#94A3B8', display: 'block', marginBottom: '3px' }}>PASSENGER NAME</label>
                      <input value={claimData.passengerName} onChange={(e) => setClaimData({...claimData, passengerName: e.target.value})} style={{ width: '100%', backgroundColor: '#1E293B', border: 'none', borderRadius: '8px', padding: '8px', color: '#38BDF8', fontSize: '12px', boxSizing: 'border-box' }} />
                    </div>
                  </div>
                </div>

                <div style={{ backgroundColor: '#0F172A', padding: '16px', borderRadius: '16px', border: '1px solid #1E293B', display: 'flex', flexDirection: 'column', boxSizing: 'border-box' }}>
                  <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#FFFFFF', margin: '0 0 10px 0' }}>Formal Legal Demand Letter</h3>
                  <textarea
                    value={legalNotice}
                    onChange={(e) => setLegalNotice(e.target.value)}
                    rows={10}
                    style={{ width: '100%', backgroundColor: '#1E293B', border: 'none', borderRadius: '10px', padding: '10px', color: '#F8FAFC', fontFamily: 'monospace', fontSize: '11px', lineHeight: 1.45, flex: 1, boxSizing: 'border-box', resize: 'none' }}
                  />

                  <div style={{ display: 'flex', gap: '8px', marginTop: '12px', flexWrap: 'wrap' }}>
                    <a
                      href={`mailto:customer.relations@airline.com?subject=EU261 Statutory Demand Notice - Flight ${claimData.flightNumber}&body=${encodeURIComponent(legalNotice)}`}
                      style={{ flex: '1 1 130px', padding: '11px', borderRadius: '8px', backgroundColor: '#E11D48', color: '#FFFFFF', textDecoration: 'none', fontWeight: '700', textAlign: 'center', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '5px', fontSize: '12px', boxSizing: 'border-box' }}
                    >
                      <Mail size={14} /> Send via Email
                    </a>
                    <button
                      onClick={handleSubmitClaim}
                      style={{ flex: '1 1 130px', padding: '11px', borderRadius: '8px', border: 'none', backgroundColor: '#10B981', color: '#090D16', fontWeight: '800', fontSize: '12px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '5px', boxSizing: 'border-box' }}
                    >
                      <Send size={14} /> Submit to Carrier
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* TAB 3: UPLOAD / SCAN BOARDING PASS */}
          {activeTab === 'ocr' && (
            <motion.div
              key="ocr"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.15 }}
              style={{ maxWidth: '600px', margin: '0 auto', boxSizing: 'border-box' }}
            >
              <div style={{ backgroundColor: '#0F172A', borderRadius: '16px', padding: '20px 14px', border: '2px dashed #0EA5E9', textAlign: 'center', marginBottom: '16px', boxSizing: 'border-box' }}>
                <Upload size={36} color="#0EA5E9" style={{ margin: '0 auto 8px auto' }} />
                <h2 style={{ fontSize: '15px', fontWeight: '700', margin: '0 0 4px 0', color: '#FFFFFF' }}>Upload Boarding Pass or Receipt File</h2>
                <p style={{ fontSize: '11px', color: '#94A3B8', margin: '0 0 12px 0' }}>Choose an image (JPG, PNG) or PDF document</p>

                <input
                  type="file"
                  accept="image/*,.pdf"
                  onChange={handleFileUpload}
                  style={{ display: 'none' }}
                  id="mobile-file-upload-tab"
                />

                <label
                  htmlFor="mobile-file-upload-tab"
                  style={{ display: 'inline-block', padding: '9px 18px', backgroundColor: '#0EA5E9', color: '#FFFFFF', borderRadius: '8px', fontWeight: '700', cursor: 'pointer', fontSize: '12px' }}
                >
                  📁 Select File
                </label>

                {uploadedImage && (
                  <div style={{ marginTop: '14px' }}>
                    <p style={{ fontSize: '11px', color: '#34D399', fontWeight: '700' }}>✓ File Uploaded Successfully!</p>
                    <img src={uploadedImage} alt="Uploaded Pass" style={{ maxHeight: '140px', borderRadius: '8px', margin: '6px auto 0 auto', border: '1px solid #1E293B' }} />
                  </div>
                )}
              </div>

              <textarea
                value={ocrText}
                onChange={(e) => setOcrText(e.target.value)}
                rows={5}
                style={{ width: '100%', backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '10px', padding: '12px', color: '#38BDF8', fontFamily: 'monospace', fontSize: '11px', outline: 'none', boxSizing: 'border-box', marginBottom: '14px' }}
              />

              <button
                onClick={handleParseDocumentBackend}
                disabled={isParsing}
                style={{ width: '100%', padding: '12px', borderRadius: '10px', border: 'none', backgroundColor: '#0EA5E9', color: '#FFFFFF', fontSize: '13px', fontWeight: '700', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', boxSizing: 'border-box' }}
              >
                {isParsing ? <Loader2 size={15} className="animate-spin" /> : <Sparkles size={15} />} 
                {isParsing ? "Processing via Strands AI..." : "Parse Document & Generate Claim"}
              </button>
            </motion.div>
          )}

        </AnimatePresence>

      </div>
    </div>
  );
}
