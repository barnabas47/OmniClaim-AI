package com.omniclaim.app;

import java.io.Serializable;
import java.util.HashMap;
import java.util.Map;

public class DecisionPackage implements Serializable {
    public String decision_id;
    public String passenger_name;
    public String pnr_code;
    public String flight_number;
    public String carrier;
    public String route;
    public String delay_duration;
    public String airline_excuse;
    public String metar_verdict;
    public String parallel_success_rate;
    public String metar_summary;
    public double statutory_amount_eur;
    public double total_receipts_eur;
    public String approval_state; // PENDING_APPROVAL, APPROVED, REJECTED
    public Map<String, String> fields = new HashMap<>();

    public DecisionPackage() {
        this.decision_id = "CLM-LH401-2026";
        this.passenger_name = "Alex Morgan";
        this.pnr_code = "PNR-LH992";
        this.flight_number = "LH401";
        this.carrier = "Lufthansa German Airlines";
        this.route = "Frankfurt (FRA) -> New York JFK (JFK)";
        this.delay_duration = "4h 15m";
        this.airline_excuse = "Extraordinary Circumstances - Severe Weather";
        this.metar_verdict = "BLUFF_DISPROVED";
        this.parallel_success_rate = "93.8%";
        this.metar_summary = "Official METAR weather at Frankfurt Airport (EDDF) confirmed VFR conditions (Visibility 10000m). 15 of 16 parallel flights departed normally. Weather excuse is DISPROVED.";
        this.statutory_amount_eur = 600.0;
        this.total_receipts_eur = 65.0;
        this.approval_state = "PENDING_APPROVAL";

        fields.put("Claim_ID", "CLM-2026-LH401-992");
        fields.put("Carrier", "Lufthansa German Airlines");
        fields.put("Flight_Number", "LH401");
        fields.put("Booking_Reference_PNR", "PNR-LH992");
        fields.put("Passenger_Name", "Alex Morgan");
        fields.put("Claimed_Amount_EUR", "€665.00");
    }

    public double getTotalClaimValue() {
        return statutory_amount_eur + total_receipts_eur;
    }
}
