package com.omniclaim.app;

import android.os.Handler;
import android.os.Looper;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class ApiClient {
    public static String BASE_URL = "https://omniclaim-ai.onrender.com";
    private static final ExecutorService executor = Executors.newSingleThreadExecutor();
    private static final Handler mainHandler = new Handler(Looper.getMainLooper());

    public interface ApiCallback {
        void onSuccess(String responseJson);
        void onError(String errorMessage);
    }

    public static void setCustomBaseUrl(String url) {
        if (url != null && !url.trim().isEmpty()) {
            BASE_URL = url.trim();
        }
    }

    public static void uploadDocument(final String rawText, final String filename, final ApiCallback callback) {
        executor.execute(new Runnable() {
            @Override
            public void run() {
                try {
                    URL url = new URL(BASE_URL + "/api/pipeline/upload-document");
                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setRequestMethod("POST");
                    conn.setRequestProperty("Content-Type", "application/json");
                    conn.setDoOutput(true);
                    conn.setConnectTimeout(6000);

                    JSONObject body = new JSONObject();
                    body.put("raw_ocr_text", rawText);
                    body.put("filename", filename);

                    OutputStream os = conn.getOutputStream();
                    os.write(body.toString().getBytes("UTF-8"));
                    os.close();

                    int responseCode = conn.getResponseCode();
                    if (responseCode == 200) {
                        BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                        StringBuilder response = new StringBuilder();
                        String inputLine;
                        while ((inputLine = in.readLine()) != null) {
                            response.append(inputLine);
                        }
                        in.close();

                        final String result = response.toString();
                        mainHandler.post(() -> callback.onSuccess(result));
                    } else {
                        mainHandler.post(() -> callback.onError("Server returned code: " + responseCode));
                    }
                } catch (final Exception e) {
                    mainHandler.post(() -> callback.onError("Network error: " + e.getMessage()));
                }
            }
        });
    }

    public static void fetchHistoricalFlightScenarios(final ApiCallback callback) {
        executor.execute(new Runnable() {
            @Override
            public void run() {
                try {
                    URL url = new URL(BASE_URL + "/api/pipeline/eligible-flights");
                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setRequestMethod("GET");
                    conn.setConnectTimeout(6000);

                    int responseCode = conn.getResponseCode();
                    if (responseCode == 200) {
                        BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                        StringBuilder response = new StringBuilder();
                        String inputLine;
                        while ((inputLine = in.readLine()) != null) {
                            response.append(inputLine);
                        }
                        in.close();
                        final String result = response.toString();
                        mainHandler.post(() -> callback.onSuccess(result));
                    } else {
                        mainHandler.post(() -> callback.onError("HTTP " + responseCode));
                    }
                } catch (Exception e) {
                    mainHandler.post(() -> callback.onError(e.getMessage()));
                }
            }
        });
    }
}
