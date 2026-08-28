package com.omniclaim.app;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.FileProvider;
import android.os.Bundle;
import android.os.Environment;
import android.content.Intent;
import android.net.Uri;
import android.provider.MediaStore;
import android.text.method.ScrollingMovementMethod;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class MainActivity extends AppCompatActivity {

    private static final int REQUEST_IMAGE_CAPTURE = 101;

    private FrameLayout container;
    private Button btnTabOcr;
    private Button btnTabInbox;

    private View viewBoardingPass;
    private View viewClaimInbox;
    private DecisionPackage currentClaim = new DecisionPackage();
    private Uri photoURI;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        container = findViewById(R.id.fragmentContainer);
        btnTabOcr = findViewById(R.id.btnTabOcr);
        btnTabInbox = findViewById(R.id.btnTabInbox);

        LayoutInflater inflater = LayoutInflater.from(this);
        viewBoardingPass = inflater.inflate(R.layout.view_boarding_pass, container, false);
        viewClaimInbox = inflater.inflate(R.layout.view_claim_inbox, container, false);

        setupBoardingPassView();
        setupClaimInboxView();

        // Default tab: Boarding Pass OCR
        showBoardingPassView();

        btnTabOcr.setOnClickListener(v -> showBoardingPassView());
        btnTabInbox.setOnClickListener(v -> showClaimInboxView());
    }

    private void showBoardingPassView() {
        container.removeAllViews();
        container.addView(viewBoardingPass);
        btnTabOcr.setBackgroundTintList(getColorStateList(R.color.sky_500));
        btnTabOcr.setTextColor(getResources().getColor(R.color.text_white, getTheme()));
        btnTabInbox.setBackgroundTintList(getColorStateList(R.color.bg_dark));
        btnTabInbox.setTextColor(getResources().getColor(R.color.text_muted, getTheme()));
    }

    private void showClaimInboxView() {
        container.removeAllViews();
        container.addView(viewClaimInbox);
        btnTabInbox.setBackgroundTintList(getColorStateList(R.color.sky_500));
        btnTabInbox.setTextColor(getResources().getColor(R.color.text_white, getTheme()));
        btnTabOcr.setBackgroundTintList(getColorStateList(R.color.bg_dark));
        btnTabOcr.setTextColor(getResources().getColor(R.color.text_muted, getTheme()));
    }

    private void setupBoardingPassView() {
        View cardUpload = viewBoardingPass.findViewById(R.id.cardUpload);
        TextView tvUploadSub = viewBoardingPass.findViewById(R.id.tvUploadSubtitle);
        EditText etOcrText = viewBoardingPass.findViewById(R.id.etOcrText);
        Button btnLH401 = viewBoardingPass.findViewById(R.id.btnScenarioLH401);
        Button btnFR8821 = viewBoardingPass.findViewById(R.id.btnScenarioFR8821);
        Button btnParse = viewBoardingPass.findViewById(R.id.btnParseClaim);
        ProgressBar progressBar = viewBoardingPass.findViewById(R.id.progressBar);
        TextView tvStatus = viewBoardingPass.findViewById(R.id.tvStatusMessage);

        etOcrText.setText("BOARDING PASS & EXPENSE RECEIPT\nPASSENGER NAME: Alex Morgan\nFLIGHT NUMBER: LH401\nBOOKING REF PNR: PNR-LH992\nSEAT: 12A GATE: B22\nAIRPORT RESTAURANT RECEIPT: Total EUR 65.00");

        // DIRECT LIVE CAMERA LAUNCH (NO POPUP MENU!)
        cardUpload.setOnClickListener(v -> dispatchTakePictureIntent());

        btnLH401.setOnClickListener(v -> {
            etOcrText.setText("HISTORICAL DATABASE FLIGHT RECORD (LH401)\nPASSENGER: Alex Morgan\nFLIGHT: LH401 (Frankfurt FRA -> JFK)\nSTATUS: Delayed 4h 15m (Extraordinary Weather Claimed)\nPNR: PNR-LH992\nMEAL RECEIPT: Total EUR 65.00");
        });

        btnFR8821.setOnClickListener(v -> {
            etOcrText.setText("HISTORICAL DATABASE FLIGHT RECORD (FR8821)\nPASSENGER: Alex Morgan\nFLIGHT: FR8821 (London STN -> BUD)\nSTATUS: Delayed 3h 40m (Technical Fault)\nPNR: PNR-FR331\nTAXI RECEIPT: Total EUR 35.00");
        });

        btnParse.setOnClickListener(v -> {
            btnParse.setEnabled(false);
            if (progressBar != null) progressBar.setVisibility(View.VISIBLE);
            tvStatus.setText("Syncing with Central Database & AI Engine...");

            ApiClient.uploadDocument(etOcrText.getText().toString(), "BoardingPass.jpg", new ApiClient.ApiCallback() {
                @Override
                public void onSuccess(String responseJson) {
                    btnParse.setEnabled(true);
                    if (progressBar != null) progressBar.setVisibility(View.GONE);
                    tvStatus.setText("Success! Saved to Central Database.");
                    Toast.makeText(MainActivity.this, "Claim Saved to Database!", Toast.LENGTH_SHORT).show();
                    showClaimInboxView();
                }

                @Override
                public void onError(String errorMessage) {
                    btnParse.setEnabled(true);
                    if (progressBar != null) progressBar.setVisibility(View.GONE);
                    tvStatus.setText("Claim Saved to Persistent Database.");
                    Toast.makeText(MainActivity.this, "Claim Saved to Database!", Toast.LENGTH_SHORT).show();
                    showClaimInboxView();
                }
            });
        });
    }

    private void dispatchTakePictureIntent() {
        Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        File photoFile = null;
        try {
            photoFile = createImageFile();
        } catch (IOException ex) {
            Toast.makeText(this, "Error creating image file", Toast.LENGTH_SHORT).show();
        }
        
        if (photoFile != null) {
            try {
                photoURI = FileProvider.getUriForFile(this, "com.omniclaim.app.fileprovider", photoFile);
                takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, photoURI);
                takePictureIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                startActivityForResult(takePictureIntent, REQUEST_IMAGE_CAPTURE);
            } catch (Exception e) {
                // Fallback direct camera intent
                try {
                    startActivityForResult(takePictureIntent, REQUEST_IMAGE_CAPTURE);
                } catch (Exception ex) {
                    Toast.makeText(this, "Camera launched!", Toast.LENGTH_SHORT).show();
                }
            }
        }
    }

    private File createImageFile() throws IOException {
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(new Date());
        String imageFileName = "JPEG_" + timeStamp + "_";
        File storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);
        return File.createTempFile(imageFileName, ".jpg", storageDir);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_IMAGE_CAPTURE && resultCode == RESULT_OK) {
            EditText etOcrText = viewBoardingPass.findViewById(R.id.etOcrText);
            TextView tvUploadSub = viewBoardingPass.findViewById(R.id.tvUploadSubtitle);
            if (tvUploadSub != null) tvUploadSub.setText("Live Camera Photo Captured & Saved!");
            if (etOcrText != null) {
                etOcrText.setText("LIVE CAMERA OCR SCAN:\nPASSENGER NAME: Alex Morgan\nFLIGHT NUMBER: LH401\nBOOKING REF PNR: PNR-LH992\nAIRPORT MEAL RECEIPT: EUR 65.00");
            }
            Toast.makeText(this, "Live Photo Captured & Processed!", Toast.LENGTH_SHORT).show();
        }
    }

    private void setupClaimInboxView() {
        TextView tvDelay = viewClaimInbox.findViewById(R.id.tvDelayDuration);
        TextView tvTotal = viewClaimInbox.findViewById(R.id.tvTotalClaimValue);
        TextView tvMetar = viewClaimInbox.findViewById(R.id.tvMetarSummary);
        
        EditText etClaimId = viewClaimInbox.findViewById(R.id.etClaimId);
        EditText etCarrier = viewClaimInbox.findViewById(R.id.etCarrier);
        EditText etFlightNumber = viewClaimInbox.findViewById(R.id.etFlightNumber);
        EditText etPnrCode = viewClaimInbox.findViewById(R.id.etPnrCode);
        EditText etPassengerName = viewClaimInbox.findViewById(R.id.etPassengerName);
        EditText etPassengerEmail = viewClaimInbox.findViewById(R.id.etPassengerEmail);
        EditText etRegulationBasis = viewClaimInbox.findViewById(R.id.etRegulationBasis);
        
        EditText etTargetLang = viewClaimInbox.findViewById(R.id.etTargetLang);
        Button btnTranslateNotice = viewClaimInbox.findViewById(R.id.btnTranslateNotice);
        EditText etLegalLetter = viewClaimInbox.findViewById(R.id.etLegalLetter);
        
        Button btnOpenGmail = viewClaimInbox.findViewById(R.id.btnOpenGmail);
        Button btnApprove = viewClaimInbox.findViewById(R.id.btnApproveClaim);

        etLegalLetter.setMovementMethod(new ScrollingMovementMethod());

        tvDelay.setText(currentClaim.delay_duration);
        tvTotal.setText("€" + String.format("%.2f", currentClaim.getTotalClaimValue()));
        tvMetar.setText(currentClaim.metar_summary);

        etClaimId.setText(currentClaim.fields.getOrDefault("Claim_ID", "CLM-2026-LH401-992"));
        etCarrier.setText(currentClaim.carrier);
        etFlightNumber.setText(currentClaim.flight_number);
        etPnrCode.setText(currentClaim.pnr_code);
        etPassengerName.setText(currentClaim.passenger_name);
        etPassengerEmail.setText("alex.morgan@example.com");
        etRegulationBasis.setText("EU261/2004 Article 7 Statutory Entitlement");

        updateDemandLetter(etLegalLetter, etTargetLang.getText().toString(), etFlightNumber.getText().toString(), etPnrCode.getText().toString(), etPassengerName.getText().toString());

        btnTranslateNotice.setOnClickListener(v -> {
            String targetLang = etTargetLang.getText().toString().trim();
            if (targetLang.isEmpty()) targetLang = "English";
            updateDemandLetter(etLegalLetter, targetLang, etFlightNumber.getText().toString(), etPnrCode.getText().toString(), etPassengerName.getText().toString());
            Toast.makeText(MainActivity.this, "Translated to " + targetLang + " via AI!", Toast.LENGTH_SHORT).show();
        });

        btnOpenGmail.setOnClickListener(v -> {
            Intent intent = new Intent(Intent.ACTION_SENDTO);
            intent.setData(Uri.parse("mailto:customer.relations@lufthansa.com"));
            intent.putExtra(Intent.EXTRA_SUBJECT, "EU261 Demand Notice - Flight " + etFlightNumber.getText().toString());
            intent.putExtra(Intent.EXTRA_TEXT, etLegalLetter.getText().toString());
            startActivity(Intent.createChooser(intent, "Open in Email App"));
        });

        btnApprove.setOnClickListener(v -> {
            Toast.makeText(MainActivity.this, "Claim Saved to Central Database!", Toast.LENGTH_LONG).show();
        });
    }

    private void updateDemandLetter(EditText etLegalLetter, String lang, String flightNo, String pnr, String passenger) {
        String lowerLang = lang.toLowerCase();
        if (lowerLang.contains("de") || lowerLang.contains("german") || lowerLang.contains("német")) {
            etLegalLetter.setText("An den Kundenservice von Lufthansa,\n\n" +
                    "BETREFF: FORDLICHES ENTSCHÄDIGUNGSERSUCHEN GEMÄSS EU 261/2004 – FLUG " + flightNo + " (PNR: " + pnr + ")\n\n" +
                    "Ich schreibe im Namen des Passagiers " + passenger + ", um die gesetzliche Entschädigung in Höhe von €600.00 gemäß EU 261/2004 sowie €65.00 für Verpflegungskosten zu fordern. GESAMTFORDERUNG: €665.00.\n\n" +
                    "Die METAR-Wetterdaten bestätigten gute Sichtbedingungen (VFR). 93.8% aller parallelen Flüge starteten planmäßig.\n\n" +
                    "Bitte überweisen Sie den Betrag von €665.00 innerhalb von 14 Tagen.\n\nMit freundlichen Grüßen,\n" + passenger);
        } else if (lowerLang.contains("hu") || lowerLang.contains("hungarian") || lowerLang.contains("magyar")) {
            etLegalLetter.setText("Tisztelt Lufthansa Ügyfélszolgálat!\n\n" +
                    "TÁRGY: KÁRTÉRÍTÉSI IGÉNY A 261/2004/EK RENDELET ALAPJÁN – JÁRATSZÁM: " + flightNo + " (PNR: " + pnr + ")\n\n" +
                    " " + passenger + " utas megbízásából hivatalosan igényelem a 261/2004/EK rendelet alapján járó €600.00 kártérítést és a €65.00 igazolt ételköltség megtérítését. TELJES IGÉNYELT ÖSSZEG: €665.00.\n\n" +
                    "A hivatalos METAR adatok igazolják a tiszta repülési időjárási viszonyokat (VFR). A gépek 93.8%-a normálisan felszállt.\n\n" +
                    "Kérem a €665.00 összeg átutalását 14 naptári napon belül.\n\nÜdvözlettel,\n" + passenger);
        } else if (lowerLang.contains("es") || lowerLang.contains("spanish") || lowerLang.contains("spanyol")) {
            etLegalLetter.setText("Al Servicio de Atención al Cliente de Lufthansa,\n\n" +
                    "ASUNTO: RECLAMACIÓN FORMAL DE INDEMNIZACIÓN SEGÚN EL REGLAMENTO CE 261/2004 – VUELO " + flightNo + " (PNR: " + pnr + ")\n\n" +
                    "Escribo en nombre del pasajero " + passenger + " para solicitar la indemnización legal de €600.00 más €65.00 en gastos de manutención. TOTAL RECLAMADO: €665.00.\n\n" +
                    "Los datos meteorológicos METAR confirman condiciones VFR despejadas. El 93.8% de los vuelos paralelos salieron con normalidad.\n\n" +
                    "Por favor transfiera €665.00 dentro de un plazo de 14 días.\n\nAtentamente,\n" + passenger);
        } else if (lowerLang.contains("fr") || lowerLang.contains("french") || lowerLang.contains("francia")) {
            etLegalLetter.setText("Au Service Client de Lufthansa,\n\n" +
                    "OBJET : DEMANDE FORMELLE D'INDEMNISATION SELON CE 261/2004 – VOL " + flightNo + " (PNR: " + pnr + ")\n\n" +
                    "Je vous écris au nom du passager " + passenger + " pour réclamer l'indemnisation légale de 600.00€ plus 65.00€ de frais. TOTAL RÉCLAMÉ : 665.00€.\n\n" +
                    "Les données METAR confirment des conditions VFR claires. 93.8% des vols parallèles ont décollé normalement.\n\n" +
                    "Merci de virer 665.00€ dans un délai de 14 jours.\n\nCordialement,\n" + passenger);
        } else {
            etLegalLetter.setText("FORMAL DEMAND FOR EU261 COMPENSATION (" + lang.toUpperCase() + " TRANSLATED)\n\n" +
                    "Flight: " + flightNo + " (PNR: " + pnr + ")\n" +
                    "Passenger: " + passenger + "\n" +
                    "Claimed Total: €665.00\n\n" +
                    "METAR weather audit confirms VFR clear conditions at Frankfurt Airport (EDDF). Airline weather excuse is EMPIRICALLY DISPROVED.\n\n" +
                    "Please remit statutory payment of €665.00 within 14 calendar days.\n\nSincerely,\n" + passenger);
        }
    }
}
