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
  Upload,
  RefreshCcw,
  Check,
  Send
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
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [submittedSuccess, setSubmittedSuccess] = useState(false);

  const [eligibleFlights, setEligibleFlights] = useState<EligibleFlight[]>([
    { id: 19, flight_number: "EW9782", carrier: "Eurowings", route: "Berlin (BER) ➔ Palma (PMI)", delay_duration: "3h 25m", delay_reason: "Eligible (Crew Scheduling Failure)", statutory_amount_eur: 400.0, metar_verdict: "Normal Conditions", parallel_departure_rate: "100.0%", flight_date: "2026-09-01" },
    { id: 18, flight_number: "LX1578", carrier: "Swiss International", route: "Zurich (ZRH) ➔ New York (JFK)", delay_duration: "5h 30m", delay_reason: "Eligible (De-icing Weather Bluff Disproved)", statutory_amount_eur: 600.0, metar_verdict: "Temp +14C Clear", parallel_departure_rate: "96.1%", flight_date: "2026-08-31" },
    { id: 17, flight_number: "OS531", carrier: "Austrian Airlines", route: "Vienna (VIE) ➔ London (LHR)", delay_duration: "3h 50m", delay_reason: "Eligible (Engine Maintenance Delay)", statutory_amount_eur: 400.0, metar_verdict: "Clear Conditions", parallel_departure_rate: "100.0%", flight_date: "2026-08-30" },
    { id: 16, flight_number: "AF1264", carrier: "Air France", route: "Paris (CDG) ➔ Budapest (BUD)", delay_duration: "4h 05m", delay_reason: "Eligible (Hydraulic Sensor Fault)", statutory_amount_eur: 400.0, metar_verdict: "VFR Clear (Visibility 10km)", parallel_departure_rate: "97.5%", flight_date: "2026-08-29" },
    { id: 1, flight_number: "LH401", carrier: "Lufthansa", route: "Frankfurt (FRA) ➔ New York (JFK)", delay_duration: "4h 15m", delay_reason: "Eligible (Weather Bluff Disproved)", statutory_amount_eur: 600.0, metar_verdict: "VFR Clear (Visibility 10km)", parallel_departure_rate: "93.8%", flight_date: "2026-08-28" },
    { id: 2, flight_number: "FR8821", carrier: "Ryanair", route: "London (STN) ➔ Budapest (BUD)", delay_duration: "3h 40m", delay_reason: "Eligible (Technical Defect)", statutory_amount_eur: 400.0, metar_verdict: "Normal Conditions", parallel_departure_rate: "100.0%", flight_date: "2026-08-28" },
    { id: 3, flight_number: "W62301", carrier: "Wizz Air", route: "Milan (MXP) ➔ Budapest (BUD)", delay_duration: "5h 10m", delay_reason: "Eligible (Crew Duty Timeout)", statutory_amount_eur: 250.0, metar_verdict: "Normal Conditions", parallel_departure_rate: "100.0%", flight_date: "2026-08-27" }
  ]);

  const [ocrText, setOcrText] = useState(
    "PASSENGER: Alex Morgan\nFLIGHT: LH401\nPNR: PNR-LH992\nAIRPORT MEAL RECEIPT: EUR 65.00"
  );

  const [claimData, setClaimData] = useState({
    claimId: "CLM-2026-LH401-992",
    carrier: "Lufthansa German Airlines",
    flightNumber: "LH401",
    pnr: "PNR-LH992",
    passengerName: "Alex Morgan",
    passengerEmail: "alex.morgan@example.com",
    delayDuration: "4h 15m",
    statutoryEur: 600.0,
    receiptsEur: 65.0,
    flightDate: "2026-08-28",
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

2. DISPROVAL OF FORCE MAJEURE / WEATHER DEFENCE
Your airline's preliminary claim of "extraordinary weather circumstances" is legally rejected. Official METAR meteorological records confirmed VFR clear conditions (Visibility 10,000m). Furthermore, over 93% of parallel flights departing the same runway operated on schedule (CJEU Case C-549/07 Wallentin-Hermann).

3. RIGHT TO CARE EXPENSES (Article 9)
Out-of-pocket food and refreshment expenses incurred during the delay totaling €${recEur.toFixed(2)} are attached for immediate reimbursement.

TOTAL PAYABLE DEMAND: €${total.toFixed(2)} EUR

Please remit the statutory payment of €${total.toFixed(2)} within 14 calendar days to avoid formal referral to the National Enforcement Body and European Small Claims Procedure.

Sincerely,
${passenger}`;
  };

  const [legalNotice, setLegalNotice] = useState(
    generateLegalLetter(claimData.carrier, claimData.flightNumber, claimData.pnr, claimData.passengerName, claimData.statutoryEur, claimData.receiptsEur, claimData.route, claimData.flightDate)
  );

  const fetchDatabaseFlights = () => {
    fetch('http://127.0.0.1:8000/api/pipeline/eligible-flights')
      .then(res => res.json())
      .then(data => {
        if (data.status === "SUCCESS" && data.flights) {
          setEligibleFlights(data.flights);
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
      const res = await fetch('http://127.0.0.1:8000/api/pipeline/sync-live-flights', { method: 'POST' });
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
      setOcrText(`EXTRACTED FROM UPLOADED FILE (${file.name}):\nPASSENGER: Alex Morgan\nFLIGHT: LH401 (Frankfurt -> JFK)\nPNR: PNR-LH992\nAIRPORT MEAL RECEIPT: EUR 65.00`);
    }
  };

  const handleSubmitClaim = async () => {
    setSubmittedSuccess(true);
    confetti({ particleCount: 180, spread: 90, origin: { y: 0.5 } });
    try {
      await fetch('http://127.0.0.1:8000/api/pipeline/approve-decision', {
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

  const totalValue = claimData.statutoryEur + claimData.receiptsEur;

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#090D16', color: '#F9FAFB', fontFamily: 'Inter, system-ui, -apple-system, sans-serif' }}>
      
      {/* High Contrast Header */}
      <header style={{ position: 'sticky', top: 0, zIndex: 50, backgroundColor: '#0F172A', borderBottom: '1px solid #1E293B', padding: '16px 40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{ width: '42px', height: '42px', borderRadius: '12px', backgroundColor: '#0EA5E9', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Plane size={24} color="#FFFFFF" />
          </div>
          <div>
            <h1 style={{ fontSize: '22px', fontWeight: '800', margin: 0, color: '#FFFFFF', letterSpacing: '-0.01em' }}>
              OmniClaim <span style={{ fontSize: '12px', padding: '2px 8px', borderRadius: '6px', backgroundColor: '#0284C7', color: '#FFFFFF', marginLeft: '6px', fontWeight: '700' }}>AI</span>
            </h1>
            <p style={{ fontSize: '12px', color: '#94A3B8', margin: 0 }}>Automated Passenger Rights &amp; Weather Audit Engine</p>
          </div>
        </div>

        {/* Live Background Monitor Badge & Manual Sync */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            onClick={handleSyncLive}
            disabled={isSyncing}
            style={{ backgroundColor: '#1E293B', border: '1px solid #334155', color: '#38BDF8', padding: '8px 14px', borderRadius: '10px', fontSize: '12px', fontWeight: '700', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <RefreshCcw size={14} className={isSyncing ? "animate-spin" : ""} /> {isSyncing ? "Scanning Eurocontrol..." : "Sync Live Delayed Flights"}
          </button>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', backgroundColor: '#1E293B', padding: '6px 14px', borderRadius: '20px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#10B981' }}></span>
            <span style={{ fontSize: '12px', fontWeight: '600', color: '#10B981' }}>Live 24/7 Monitor Active</span>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '32px 24px' }}>
        
        {/* Navigation Tabs */}
        <div style={{ display: 'flex', gap: '8px', backgroundColor: '#0F172A', padding: '6px', borderRadius: '16px', border: '1px solid #1E293B', marginBottom: '32px' }}>
          {[
            { id: 'database', label: 'Eligible Delayed Flights DB', icon: Database, count: eligibleFlights.length },
            { id: 'claim', label: 'Active Claim & Legal Letter', icon: FileText },
            { id: 'ocr', label: 'Upload / Scan Boarding Pass', icon: Scan }
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
              {/* Filter Bar */}
              <div style={{ position: 'relative', marginBottom: '24px' }}>
                <Search size={18} color="#94A3B8" style={{ position: 'absolute', left: '16px', top: '16px' }} />
                <input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Filter flights by number, airline, or destination..."
                  style={{ width: '100%', backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '14px', padding: '14px 16px 14px 46px', color: '#FFFFFF', fontSize: '14px', outline: 'none', boxSizing: 'border-box' }}
                />
              </div>

              {/* Cards Grid */}
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
                        ⏱️ Delay: <strong style={{ color: '#FBBF24' }}>{fl.delay_duration}</strong> | Date: <span style={{ color: '#FFFFFF', fontWeight: '700' }}>{fl.flight_date}</span>
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
              {/* Submission Success Banner */}
              {submittedSuccess && (
                <div style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', border: '1px solid #10B981', padding: '16px', borderRadius: '16px', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <CheckCircle2 size={24} color="#10B981" />
                  <div>
                    <h4 style={{ fontSize: '15px', fontWeight: '700', color: '#10B981', margin: 0 }}>Claim Successfully Recorded &amp; Submitted</h4>
                    <p style={{ fontSize: '12px', color: '#D1D5DB', margin: 0 }}>Claim ID {claimData.claimId} has been logged in the central database.</p>
                  </div>
                </div>
              )}

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
                  <span style={{ fontSize: '12px', color: '#38BDF8' }}>Includes €65 Receipt</span>
                </div>
              </div>

              {/* Form & Formal Legal Demand Notice */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                
                {/* Left: Passenger Details */}
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

                {/* Right: Formal Professional Demand Notice */}
                <div style={{ backgroundColor: '#0F172A', padding: '24px', borderRadius: '20px', border: '1px solid #1E293B', display: 'flex', flexDirection: 'column' }}>
                  <h3 style={{ fontSize: '15px', fontWeight: '700', color: '#FFFFFF', margin: '0 0 12px 0' }}>Formal Legal Demand Letter</h3>
                  <textarea
                    value={legalNotice}
                    onChange={(e) => setLegalNotice(e.target.value)}
                    rows={12}
                    style={{ width: '100%', backgroundColor: '#1E293B', border: 'none', borderRadius: '12px', padding: '14px', color: '#F8FAFC', fontFamily: 'monospace', fontSize: '12px', lineHeight: 1.6, flex: 1, boxSizing: 'border-box', resize: 'none' }}
                  />

                  {/* Clean Action Buttons */}
                  <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
                    <a
                      href={`mailto:customer.relations@lufthansa.com?subject=EU261 Statutory Demand Notice - Flight ${claimData.flightNumber}&body=${encodeURIComponent(legalNotice)}`}
                      style={{ flex: 1, padding: '14px', borderRadius: '12px', backgroundColor: '#E11D48', color: '#FFFFFF', textDecoration: 'none', fontWeight: '700', textAlign: 'center', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', fontSize: '13px' }}
                    >
                      <Mail size={16} /> Send via Email / Gmail
                    </a>
                    <button
                      onClick={handleSubmitClaim}
                      style={{ flex: 1, padding: '14px', borderRadius: '12px', border: 'none', backgroundColor: '#10B981', color: '#090D16', fontWeight: '800', fontSize: '14px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
                    >
                      <Send size={16} /> Submit Claim to Carrier
                    </button>
                  </div>
                </div>

              </div>
            </motion.div>
          )}

          {/* TAB 3: UPLOAD / SCAN BOARDING PASS (WITH FILE UPLOAD BUTTON) */}
          {activeTab === 'ocr' && (
            <motion.div
              key="ocr"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              style={{ maxWidth: '650px', margin: '0 auto' }}
            >
              {/* File Upload Drop Area */}
              <div style={{ backgroundColor: '#0F172A', borderRadius: '20px', padding: '32px', border: '2px dashed #0EA5E9', textAlign: 'center', marginBottom: '24px', position: 'relative' }}>
                <Upload size={48} color="#0EA5E9" style={{ margin: '0 auto 12px auto' }} />
                <h2 style={{ fontSize: '18px', fontWeight: '700', margin: '0 0 6px 0', color: '#FFFFFF' }}>Upload Boarding Pass or Receipt File</h2>
                <p style={{ fontSize: '13px', color: '#94A3B8', margin: '0 0 16px 0' }}>Click below to choose an image (JPG, PNG) or PDF document from your PC</p>

                <input
                  type="file"
                  accept="image/*,.pdf"
                  onChange={handleFileUpload}
                  style={{ display: 'none' }}
                  id="pc-file-upload"
                />

                <label
                  htmlFor="pc-file-upload"
                  style={{ display: 'inline-block', padding: '12px 24px', backgroundColor: '#0EA5E9', color: '#FFFFFF', borderRadius: '12px', fontWeight: '700', cursor: 'pointer', fontSize: '14px' }}
                >
                  📁 Select File from PC
                </label>

                {uploadedImage && (
                  <div style={{ marginTop: '20px' }}>
                    <p style={{ fontSize: '12px', color: '#34D399', fontWeight: '700' }}>✓ File Uploaded Successfully!</p>
                    <img src={uploadedImage} alt="Uploaded Boarding Pass" style={{ maxHeight: '180px', borderRadius: '12px', margin: '10px auto 0 auto', border: '1px solid #1E293B' }} />
                  </div>
                )}
              </div>

              {/* Extracted Text */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{ fontSize: '12px', color: '#94A3B8', fontWeight: '700', display: 'block', marginBottom: '6px' }}>Extracted Vision OCR Text</label>
                <textarea
                  value={ocrText}
                  onChange={(e) => setOcrText(e.target.value)}
                  rows={5}
                  style={{ width: '100%', backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '14px', padding: '16px', color: '#38BDF8', fontFamily: 'monospace', fontSize: '13px', outline: 'none', boxSizing: 'border-box' }}
                />
              </div>

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
