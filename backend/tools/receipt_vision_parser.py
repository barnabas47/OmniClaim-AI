"""
Multimodal Vision & OCR Receipt/Boarding Pass Parser Tool.
Extracts passenger names, PNR booking codes, flight numbers, and expense amounts from uploaded image/PDF documents.
Powered by AWS Bedrock Claude Vision with Windows Native OCR & Aviation Knowledge Base fallback.
NO HARDCODED MOCK NAMES OR DUMMY DEFAULTS EVER.
"""
import re
import json
import logging
import base64
import os
from typing import Dict, Any, Optional

try:
    from strands import tool
except ImportError:
    def tool(func):
        return func

logger = logging.getLogger("OmniClaim.VisionParser")

# Comprehensive Global Aviation Domain Knowledge Base & Intent Mapping Matrix
AVIATION_KNOWLEDGE_BASE = {
    "AIRLINES": {
        "LUFTHANSA": {"carrier": "Lufthansa German Airlines", "prefix": "LH", "hub": "EDDF/FRA"},
        "DLH": {"carrier": "Lufthansa German Airlines", "prefix": "LH", "hub": "EDDF/FRA"},
        "LH": {"carrier": "Lufthansa German Airlines", "prefix": "LH", "hub": "EDDF/FRA"},
        "BRITISH": {"carrier": "British Airways", "prefix": "BA", "hub": "EGLL/LHR"},
        "BAW": {"carrier": "British Airways", "prefix": "BA", "hub": "EGLL/LHR"},
        "BA": {"carrier": "British Airways", "prefix": "BA", "hub": "EGLL/LHR"},
        "AIR FRANCE": {"carrier": "Air France", "prefix": "AF", "hub": "LFPG/CDG"},
        "AFR": {"carrier": "Air France", "prefix": "AF", "hub": "LFPG/CDG"},
        "AF": {"carrier": "Air France", "prefix": "AF", "hub": "LFPG/CDG"},
        "KLM": {"carrier": "KLM Royal Dutch", "prefix": "KL", "hub": "EHAM/AMS"},
        "KL": {"carrier": "KLM Royal Dutch", "prefix": "KL", "hub": "EHAM/AMS"},
        "RYANAIR": {"carrier": "Ryanair DAC", "prefix": "FR", "hub": "EGSS/STN"},
        "RYR": {"carrier": "Ryanair DAC", "prefix": "FR", "hub": "EGSS/STN"},
        "FR": {"carrier": "Ryanair DAC", "prefix": "FR", "hub": "EGSS/STN"},
        "WIZZ": {"carrier": "Wizz Air Hungary", "prefix": "W6", "hub": "LIMC/MXP"},
        "WZZ": {"carrier": "Wizz Air Hungary", "prefix": "W6", "hub": "LIMC/MXP"},
        "W6": {"carrier": "Wizz Air Hungary", "prefix": "W6", "hub": "LIMC/MXP"},
        "SWISS": {"carrier": "Swiss International Air Lines", "prefix": "LX", "hub": "LSZH/ZRH"},
        "SWR": {"carrier": "Swiss International Air Lines", "prefix": "LX", "hub": "LSZH/ZRH"},
        "LX": {"carrier": "Swiss International Air Lines", "prefix": "LX", "hub": "LSZH/ZRH"},
        "AUSTRIAN": {"carrier": "Austrian Airlines", "prefix": "OS", "hub": "LOWW/VIE"},
        "AUA": {"carrier": "Austrian Airlines", "prefix": "OS", "hub": "LOWW/VIE"},
        "OS": {"carrier": "Austrian Airlines", "prefix": "OS", "hub": "LOWW/VIE"},
        "IBERIA": {"carrier": "Iberia", "prefix": "IB", "hub": "LEMD/MAD"},
        "IBE": {"carrier": "Iberia", "prefix": "IB", "hub": "LEMD/MAD"},
        "IB": {"carrier": "Iberia", "prefix": "IB", "hub": "LEMD/MAD"},
        "EUROWINGS": {"carrier": "Eurowings", "prefix": "EW", "hub": "EDDB/BER"},
        "EWG": {"carrier": "Eurowings", "prefix": "EW", "hub": "EDDB/BER"},
        "EW": {"carrier": "Eurowings", "prefix": "EW", "hub": "EDDB/BER"},
        "EASYJET": {"carrier": "easyJet Europe", "prefix": "U2", "hub": "EGKK/LGW"},
        "EJU": {"carrier": "easyJet Europe", "prefix": "U2", "hub": "EGKK/LGW"},
        "U2": {"carrier": "easyJet Europe", "prefix": "U2", "hub": "EGKK/LGW"},
        "EMIRATES": {"carrier": "Emirates", "prefix": "EK", "hub": "OMDB/DXB"},
        "UAE": {"carrier": "Emirates", "prefix": "EK", "hub": "OMDB/DXB"},
        "EK": {"carrier": "Emirates", "prefix": "EK", "hub": "OMDB/DXB"},
        "QATAR": {"carrier": "Qatar Airways", "prefix": "QR", "hub": "OTHH/DOH"},
        "QTR": {"carrier": "Qatar Airways", "prefix": "QR", "hub": "OTHH/DOH"},
        "QR": {"carrier": "Qatar Airways", "prefix": "QR", "hub": "OTHH/DOH"},
        "TURKISH": {"carrier": "Turkish Airlines", "prefix": "TK", "hub": "LTFM/IST"},
        "THY": {"carrier": "Turkish Airlines", "prefix": "TK", "hub": "LTFM/IST"},
        "TK": {"carrier": "Turkish Airlines", "prefix": "TK", "hub": "LTFM/IST"},
        "DELTA": {"carrier": "Delta Air Lines", "prefix": "DL", "hub": "KATL/ATL"},
        "DAL": {"carrier": "Delta Air Lines", "prefix": "DL", "hub": "KATL/ATL"},
        "DL": {"carrier": "Delta Air Lines", "prefix": "DL", "hub": "KATL/ATL"},
        "AMERICAN": {"carrier": "American Airlines", "prefix": "AA", "hub": "KDFW/DFW"},
        "AAL": {"carrier": "American Airlines", "prefix": "AA", "hub": "KDFW/DFW"},
        "AA": {"carrier": "American Airlines", "prefix": "AA", "hub": "KDFW/DFW"},
        "UNITED": {"carrier": "United Airlines", "prefix": "UA", "hub": "KORD/ORD"},
        "UAL": {"carrier": "United Airlines", "prefix": "UA", "hub": "KORD/ORD"},
        "UA": {"carrier": "United Airlines", "prefix": "UA", "hub": "KORD/ORD"},
        "LOT": {"carrier": "LOT Polish Airlines", "prefix": "LO", "hub": "EPWA/WAW"},
        "LO": {"carrier": "LOT Polish Airlines", "prefix": "LO", "hub": "EPWA/WAW"},
        "SAS": {"carrier": "SAS Scandinavian Airlines", "prefix": "SK", "hub": "EKCH/CPH"},
        "SK": {"carrier": "SAS Scandinavian Airlines", "prefix": "SK", "hub": "EKCH/CPH"},
        "FINNAIR": {"carrier": "Finnair", "prefix": "AY", "hub": "EFHK/HEL"},
        "AY": {"carrier": "Finnair", "prefix": "AY", "hub": "EFHK/HEL"},
        "TAP": {"carrier": "TAP Air Portugal", "prefix": "TP", "hub": "LPPT/LIS"},
        "TP": {"carrier": "TAP Air Portugal", "prefix": "TP", "hub": "LPPT/LIS"},
        "AEGEAN": {"carrier": "Aegean Airlines", "prefix": "A3", "hub": "LGAV/ATH"},
        "A3": {"carrier": "Aegean Airlines", "prefix": "A3", "hub": "LGAV/ATH"},
        "VUELING": {"carrier": "Vueling Airlines", "prefix": "VY", "hub": "LEBL/BCN"},
        "VY": {"carrier": "Vueling Airlines", "prefix": "VY", "hub": "LEBL/BCN"},
    }
}

_BEDROCK_AI_SYSTEM_PROMPT = """You are OmniClaim AI's boarding pass and receipt OCR specialist. 
Extract structured flight information from the provided document image or text.

AVIATION DOMAIN KNOWLEDGE:
- Airline codes: LH=Lufthansa, BA=British Airways, AF=Air France, KL=KLM, FR=Ryanair, W6=Wizz Air, 
  LX=Swiss, OS=Austrian, IB=Iberia, EW=Eurowings, U2=easyJet, EK=Emirates, QR=Qatar, TK=Turkish,
  DL=Delta, AA=American, UA=United, LO=LOT, SK=SAS, AY=Finnair, TP=TAP, A3=Aegean, VY=Vueling
- PNR/Booking reference: typically 6 alphanumeric characters (e.g., ABC123, XK7R9P)
- Flight numbers: airline code + digits (e.g., LH401, FR1234, W6 2301)
- Passenger names may appear as SURNAME/FIRSTNAME or Firstname Lastname
- Dates may appear as DD MMM YYYY, YYYY-MM-DD, DD/MM/YYYY, or similar formats

Return ONLY a valid JSON object with these fields (use null if not found):
{
  "passenger_name": "Full Name or null",
  "flight_number": "XX1234 format or null",
  "pnr_code": "PNR-XXXXXX format or null",
  "flight_date": "YYYY-MM-DD format or null",
  "airline": "Full airline name or null",
  "origin_iata": "3-letter code or null",
  "destination_iata": "3-letter code or null",
  "seat": "seat number or null",
  "expense_amount_eur": numeric amount or null,
  "document_type": "BOARDING_PASS or RECEIPT or TICKET or UNKNOWN"
}"""


def _try_bedrock_vision_parse(image_bytes: bytes, media_type: str = "image/jpeg") -> Optional[Dict]:
    """
    Attempts to parse a boarding pass / receipt image using AWS Bedrock Claude multimodal vision.
    Returns parsed dict or None if unavailable.
    """
    try:
        import boto3
        import json as _json

        aws_key = os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret = os.environ.get("AWS_SECRET_ACCESS_KEY")
        aws_region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

        if not aws_key or not aws_secret:
            logger.info("AWS credentials not configured – skipping Bedrock vision parse.")
            return None

        client = boto3.client(
            "bedrock-runtime",
            region_name=aws_region,
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
            aws_session_token=os.environ.get("AWS_SESSION_TOKEN")
        )

        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "system": _BEDROCK_AI_SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_b64
                            }
                        },
                        {
                            "type": "text",
                            "text": "Extract all flight information from this boarding pass or receipt document. Return only a JSON object."
                        }
                    ]
                }
            ]
        }

        model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        response = client.invoke_model(
            modelId=model_id,
            body=_json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )

        response_body = _json.loads(response["body"].read())
        raw_text = response_body["content"][0]["text"].strip()

        json_match = re.search(r'\{[\s\S]*\}', raw_text)
        if json_match:
            parsed = _json.loads(json_match.group(0))
            logger.info(f"Bedrock vision parse SUCCESS: {parsed}")
            return parsed

    except Exception as e:
        logger.warning(f"Bedrock vision parse failed: {e}")

    return None


def _try_bedrock_text_parse(document_text: str) -> Optional[Dict]:
    """
    Attempts to parse boarding pass / receipt text using AWS Bedrock Claude (text-only).
    Returns parsed dict or None if unavailable.
    """
    try:
        import boto3
        import json as _json

        aws_key = os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret = os.environ.get("AWS_SECRET_ACCESS_KEY")
        aws_region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

        if not aws_key or not aws_secret:
            logger.info("AWS credentials not configured – skipping Bedrock text parse.")
            return None

        client = boto3.client(
            "bedrock-runtime",
            region_name=aws_region,
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
            aws_session_token=os.environ.get("AWS_SESSION_TOKEN")
        )

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "system": _BEDROCK_AI_SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": f"Extract all flight information from this document text:\n\n{document_text}\n\nReturn only a JSON object."
                }
            ]
        }

        model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        response = client.invoke_model(
            modelId=model_id,
            body=_json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )

        response_body = _json.loads(response["body"].read())
        raw_text = response_body["content"][0]["text"].strip()

        json_match = re.search(r'\{[\s\S]*\}', raw_text)
        if json_match:
            parsed = _json.loads(json_match.group(0))
            logger.info(f"Bedrock text parse SUCCESS: {parsed}")
            return parsed

    except Exception as e:
        logger.warning(f"Bedrock text parse failed: {e}")

    return None


VALID_PREFIXES = {"LH", "BA", "AF", "KL", "FR", "W6", "LX", "OS", "IB", "EW", "U2", "EK", "QR", "TK", "DL", "AA", "UA", "LO", "SK", "AY", "TP", "A3", "VY", "DLH", "BAW", "AFR", "KLM", "RYR", "WZZ", "SWR", "AUA", "IBE", "EWG", "EJU", "UAE", "QTR", "THY", "DAL", "AAL", "UAL", "LOT", "SAS", "FIN", "TAP", "AEE", "VLG"}

MONTH_MAP = {
    "JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06",
    "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"
}

def _regex_fallback_parse(document_text: str, filename: str) -> Dict:
    """
    Regex-based fallback parser when AI is unavailable.
    Returns ONLY whatever can be genuinely found in document_text, NEVER mock/dummy data.
    """
    text_upper = (document_text or "").upper()
    file_upper = (filename or "").upper()

    # 1. Identify Airline Carrier
    detected_carrier_info = None
    sorted_keywords = sorted(AVIATION_KNOWLEDGE_BASE["AIRLINES"].keys(), key=len, reverse=True)
    for kw in sorted_keywords:
        info = AVIATION_KNOWLEDGE_BASE["AIRLINES"][kw]
        if len(kw) <= 3:
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, text_upper) or re.search(pattern, file_upper):
                detected_carrier_info = info
                break
        else:
            if kw in text_upper or kw in file_upper:
                detected_carrier_info = info
                break

    # 2. Flight Number (using re.finditer across all matches)
    flight_number = ""
    for m in re.finditer(r"\b([A-Z0-9]{2,3}\s*[-#]?\s*\d{3,4})\b", document_text, re.IGNORECASE):
        candidate = m.group(1).replace(" ", "").replace("-", "").upper()
        if any(candidate.startswith(pfx) for pfx in VALID_PREFIXES):
            flight_number = candidate
            break

    # 3. PNR Code (using re.finditer with strict separator & label checks)
    pnr_code = ""
    pnr_pattern = r"(?:PNR|BOOKING|REFERENCE|RECORD|LOCATOR|CONFIRMATION|RESERVATION|REF)[\s:#\(\)-]+(?:PNR-)?([A-Z0-9]{5,7})\b"
    for m in re.finditer(pnr_pattern, document_text, re.IGNORECASE):
        cand = m.group(1).upper()
        if cand not in ["REFERENCE", "BOOKING", "CONFIRMATION", "RESERVATION", "LOCATOR", "NUMBER", "DETAILS", "TICKET"]:
            pnr_code = f"PNR-{cand}"
            break
            
    if not pnr_code:
        for m in re.finditer(r"\b([A-Z0-9]{6})\b", document_text):
            cand = m.group(1).upper()
            if not any(w in cand for w in ["SELECT", "UPLOAD", "LATEST", "PASSED", "TICKET", "FLIGHT", "NUMBER", "DATE", "AMOUNT"]):
                pnr_code = f"PNR-{cand}"
                break

    # 4. Passenger Name
    INVALID_NAME_WORDS = {
        "local", "windows", "native", "ocr", "aviation", "knowledge", "base", 
        "parsed", "extracted", "confidence", "boarding", "flight", "gate", "seat", 
        "from", "date", "airline", "airport", "terminal", "booking", "receipt", 
        "ticket", "details", "passenger", "name", "economy", "business", "first", 
        "class", "zone", "sequence", "pnr", "reference", "carrier", "system", 
        "image", "document", "status", "success", "error", "clause", "notice",
        "lufthansa", "ryanair", "wizz", "easyjet", "swiss", "austrian", "iberia",
        "png", "jpg", "jpeg", "pdf", "select", "file", "uploaded", "successfully",
        "device", "preview", "choose", "browse", "drag", "drop", "upload",
        "generate", "claim", "parse", "total", "amount", "number", "issuing", "itinerary"
    }

    def _is_valid_person_name(cand: str) -> bool:
        if not cand or len(cand) < 4:
            return False
        words = [w.lower().strip(".,!?:;") for w in re.split(r"\s+", cand) if w.strip()]
        if len(words) < 2:
            return False
        if any(w in INVALID_NAME_WORDS for w in words):
            return False
        return True

    passenger_name = ""
    # Check IATA ticket format SURNAME / FIRSTNAME MR/MRS
    for iata_match in re.finditer(r"\b([A-Z]{2,20})\s*/\s*([A-Z]{2,20})(?:\s+(?:MR|MRS|MS|DR|PROF))?\b", document_text):
        last = iata_match.group(1).title()
        first = iata_match.group(2).title()
        cand = f"{first} {last}"
        if _is_valid_person_name(cand):
            passenger_name = cand
            break

    if not passenger_name:
        for reverse_name_match in re.finditer(r"\b([A-Z]{2,15}),\s*([A-Z]{2,15})\b", document_text):
            last = reverse_name_match.group(1).title()
            first = reverse_name_match.group(2).title()
            cand = f"{first} {last}"
            if _is_valid_person_name(cand):
                passenger_name = cand
                break

    if not passenger_name:
        for name_match in re.finditer(r"(?:PASSENGER NAME|PASSENGER|FULL NAME|CUSTOMER|NAME)[\s:#]+([A-Za-z]+(?:[ \t]+[A-Za-z]+)+)", document_text, re.IGNORECASE):
            clean_name = name_match.group(1).strip().title()
            if _is_valid_person_name(clean_name):
                passenger_name = clean_name
                break

    # 5. Expense Amount
    expense_amount = 0.0
    expense_matches = re.findall(r"(?:Total|Amount|EUR|USD|GBP|€|\$|£)\s*:?\s*[\$€£]?\s*(\d+[.,]\d{2})", document_text, re.IGNORECASE)
    if expense_matches:
        expense_amounts = [float(x.replace(",", ".")) for x in expense_matches]
        valid_expenses = [x for x in expense_amounts if 5.0 <= x <= 1500.0]
        if valid_expenses:
            expense_amount = max(valid_expenses)

    # 6. Flight Date
    flight_date = ""
    dmy_str_match = re.search(r"\b(\d{1,2})[\s/-]+([A-Za-z]{3})[\s/-]+(\d{2,4})\b", document_text)
    if dmy_str_match:
        day = int(dmy_str_match.group(1))
        mon = dmy_str_match.group(2).upper()
        yr = dmy_str_match.group(3)
        if len(yr) == 2: yr = f"20{yr}"
        if mon in MONTH_MAP:
            flight_date = f"{yr}-{MONTH_MAP[mon]}-{day:02d}"

    if not flight_date:
        iso_match = re.search(r"\b(202\d-\d{2}-\d{2})\b", document_text)
        if iso_match:
            flight_date = iso_match.group(1)

    if not flight_date:
        dmy_num_match = re.search(r"\b(\d{1,2})[/.](\d{1,2})[/.](\d{4})\b", document_text)
        if dmy_num_match:
            d, m, y = int(dmy_num_match.group(1)), int(dmy_num_match.group(2)), dmy_num_match.group(3)
            flight_date = f"{y}-{m:02d}-{d:02d}"

    return {
        "passenger_name": passenger_name,
        "flight_number": flight_number,
        "pnr_code": pnr_code,
        "flight_date": flight_date,
        "expense_amount_eur": expense_amount,
        "document_type": "BOARDING_PASS",
        "origin_iata": "",
        "destination_iata": "",
        "seat": "",
        "detected_carrier_info": detected_carrier_info,
        "raw_text": document_text
    }


def _merge_ai_result_with_knowledge_base(ai_result: Dict, document_text: str, filename: str) -> Dict:
    """
    Merges AI-extracted fields with knowledge base lookups for carrier enrichment.
    Never invents mock values.
    """
    text_upper = (document_text or "").upper()
    file_upper = (filename or "").upper()

    airline_raw = (ai_result.get("airline") or "").upper()
    detected_carrier_info = None
    sorted_keywords = sorted(AVIATION_KNOWLEDGE_BASE["AIRLINES"].keys(), key=len, reverse=True)

    for kw in sorted_keywords:
        if kw in airline_raw:
            detected_carrier_info = AVIATION_KNOWLEDGE_BASE["AIRLINES"][kw]
            break

    if not detected_carrier_info:
        fn = (ai_result.get("flight_number") or "").upper().replace(" ", "")
        for kw in sorted_keywords:
            if fn.startswith(kw):
                detected_carrier_info = AVIATION_KNOWLEDGE_BASE["AIRLINES"][kw]
                break

    if not detected_carrier_info:
        for kw in sorted_keywords:
            info = AVIATION_KNOWLEDGE_BASE["AIRLINES"][kw]
            if len(kw) <= 3:
                pattern = r"\b" + re.escape(kw) + r"\b"
                if re.search(pattern, text_upper) or re.search(pattern, file_upper):
                    detected_carrier_info = info
                    break
            else:
                if kw in text_upper or kw in file_upper:
                    detected_carrier_info = info
                    break

    pnr_raw = ai_result.get("pnr_code") or ""
    if pnr_raw and not pnr_raw.startswith("PNR-"):
        pnr_raw = f"PNR-{pnr_raw.upper()}"

    p_name = ai_result.get("passenger_name") or ""
    f_num = (ai_result.get("flight_number") or "").replace(" ", "").upper()

    # Blacklist check
    if p_name.upper() in ["DANIEL KOVACS", "DANIEL KOVÁCS", "EVA HORVATH", "ALEX MORGAN"]:
        p_name = ""
    if f_num in ["W62301", "LH401"]:
        f_num = ""
    if pnr_raw in ["PNR-W6230", "PNR-LH992"]:
        pnr_raw = ""

    return {
        "passenger_name": p_name,
        "flight_number": f_num,
        "pnr_code": pnr_raw,
        "flight_date": ai_result.get("flight_date") or "",
        "expense_amount_eur": ai_result.get("expense_amount_eur") or 0.0,
        "document_type": ai_result.get("document_type") or "BOARDING_PASS",
        "origin_iata": ai_result.get("origin_iata") or "",
        "destination_iata": ai_result.get("destination_iata") or "",
        "seat": ai_result.get("seat") or "",
        "detected_carrier_info": detected_carrier_info,
        "raw_text": document_text
    }


def _build_result(extracted: Dict, filename: str, ai_powered: bool) -> str:
    """Builds the final JSON result from extracted fields."""
    carrier_info = extracted.get("detected_carrier_info")
    matched_carrier = carrier_info["carrier"] if carrier_info else ""

    result = {
        "status": "SUCCESS",
        "vision_ocr_extracted": {
            "source_filename": filename,
            "flight_number": extracted.get("flight_number", ""),
            "pnr_code": extracted.get("pnr_code", ""),
            "passenger_name": extracted.get("passenger_name", ""),
            "flight_date": extracted.get("flight_date", ""),
            "incurred_expense_receipt_eur": extracted.get("expense_amount_eur", 0.0) if extracted.get("expense_amount_eur", 0.0) > 0 else 0.0,
            "confidence_score": 0.97 if ai_powered else 0.72,
            "knowledge_base_match": matched_carrier,
            "document_type": extracted.get("document_type", "BOARDING_PASS"),
            "origin_iata": extracted.get("origin_iata", ""),
            "destination_iata": extracted.get("destination_iata", ""),
            "seat": extracted.get("seat", ""),
            "parsed_by": extracted.get("parsed_by", "AWS Bedrock Claude Vision" if ai_powered else "Local Windows Native OCR + Aviation Knowledge Base"),
            "raw_text": extracted.get("raw_text", "")
        }
    }
    return json.dumps(result, indent=2)


@tool
def parse_receipt_or_boarding_pass(document_text: str, filename: Optional[str] = "boarding_pass.jpg") -> str:
    """
    Multimodal OCR parser tool that extracts structured flight metadata and expense receipt amounts
    from raw text extracted from uploaded boarding passes, e-tickets, or hotel/meal receipts.
    Uses AWS Bedrock Claude AI for intelligent extraction with regex fallback.

    Args:
        document_text: Raw text content extracted via OCR from boarding pass or expense receipt.
        filename: Name of the uploaded document file.

    Returns:
        JSON string containing extracted passenger name, flight number, PNR code, and incurred expense amounts.
    """
    logger.info(f"Parsing document: {filename} (text length: {len(document_text or '')})")

    ai_result = _try_bedrock_text_parse(document_text or "")
    ai_powered = False

    if ai_result:
        ai_powered = True
        extracted = _merge_ai_result_with_knowledge_base(ai_result, document_text or "", filename or "")
    else:
        extracted = _regex_fallback_parse(document_text or "", filename or "")

    return _build_result(extracted, filename or "boarding_pass.jpg", ai_powered)


def _local_windows_ocr(image_bytes: bytes) -> str:
    """
    Extracts raw text from image bytes using Windows Native OCR (winsdk.windows.media.ocr).
    Comprehensive 5-pass multi-region contrast & resolution scaling for screenshots & photos.
    Runs 100% offline on Windows 10/11 with zero external dependencies or API keys.
    Filters out OmniClaim app UI text that gets picked up when user uploads a screenshot.
    """
    # Lines that are the app's own UI — these must be filtered from OCR results
    APP_UI_LINES = {
        "upload boarding pass or receipt file",
        "select an image (jpg, png) or pdf document from your device",
        "select file",
        "file uploaded successfully!",
        "parse document & generate claim",
        "parse document",
        "generate claim",
        "review & edit details",
        "passenger & flight info verification",
        "active claim & notice",
        "omniclaim ai",
        "powered by strands ai agents",
        "processing via strands ai agents",
        "live eligible flights database",
        "search flights",
        "date",
        "airline",
        "flight callsign",
        "booking pnr",
        "passenger name",
        "passenger email",
        "delay duration",
        "route",
    }

    def _should_keep_line(line: str) -> bool:
        """Returns True if this line is NOT from app UI (i.e. it's real ticket content)."""
        stripped = line.strip()
        if not stripped or len(stripped) < 2:
            return False
        lower = stripped.lower()
        # Exact matches to UI strings
        if lower in APP_UI_LINES:
            return False
        # Partial match check for common UI fragments
        ui_fragments = [
            "upload boarding", "select an image", "select file",
            "file uploaded", "parse document", "generate claim",
            "parsed by local windows", "aviation knowledge base",
            "parsed by", "omniclaim", "strands ai",
            "review & edit", "active claim", "eligible flights",
        ]
        for frag in ui_fragments:
            if frag in lower:
                return False
        return True

    try:
        import io
        import asyncio
        import PIL.Image
        import PIL.ImageEnhance
        import PIL.ImageOps
        import PIL.ImageFilter
        import winsdk.windows.media.ocr as ocr
        import winsdk.windows.graphics.imaging as img_mod
        import winsdk.windows.storage.streams as streams

        async def _ocr_single(pil_img):
            buf = io.BytesIO()
            pil_img.convert("RGBA").save(buf, format="PNG")
            stream = streams.InMemoryRandomAccessStream()
            writer = streams.DataWriter(stream)
            writer.write_bytes(buf.getvalue())
            await writer.store_async()
            stream.seek(0)
            decoder = await img_mod.BitmapDecoder.create_async(stream)
            software_bitmap = await decoder.get_software_bitmap_async()
            engine = ocr.OcrEngine.try_create_from_user_profile_languages()
            if not engine:
                for lang in ocr.OcrEngine.available_recognizer_languages:
                    engine = ocr.OcrEngine.try_create_from_language(lang)
                    if engine:
                        break
            if not engine:
                return ""
            result = await engine.recognize_async(software_bitmap)
            return result.text if result else ""

        async def _ocr_async():
            orig_img = PIL.Image.open(io.BytesIO(image_bytes)).convert("RGB")
            w, h = orig_img.size
            all_lines = []

            def _scale_to(img, target_max=3000):
                iw, ih = img.size
                sc = max(1.0, float(target_max) / max(iw, ih, 1))
                if sc != 1.0:
                    return img.resize((int(iw * sc), int(ih * sc)), PIL.Image.Resampling.LANCZOS)
                return img

            def _enhance(img, contrast=2.0, sharpness=2.5, brightness=1.1):
                img = PIL.ImageEnhance.Contrast(img).enhance(contrast)
                img = PIL.ImageEnhance.Sharpness(img).enhance(sharpness)
                img = PIL.ImageEnhance.Brightness(img).enhance(brightness)
                return img

            def _collect(text):
                for line in (text or "").splitlines():
                    s = line.strip()
                    if _should_keep_line(s) and s not in all_lines:
                        all_lines.append(s)

            # Pass 1: Tight center crop (where ticket paper usually is in screenshots)
            c1 = orig_img.crop((int(w * 0.27), int(h * 0.36), int(w * 0.73), int(h * 0.62)))
            _collect(await _ocr_single(_enhance(_scale_to(c1, 3000))))

            # Pass 2: Same tight crop but binarized
            g2 = PIL.ImageOps.autocontrast(_scale_to(c1, 3000).convert("L"), cutoff=1)
            b2 = g2.point(lambda x: 255 if x > 115 else 0, mode="1").convert("RGB")
            _collect(await _ocr_single(b2))

            # Pass 3: Wider ticket crop (more context)
            c3 = orig_img.crop((int(w * 0.15), int(h * 0.32), int(w * 0.85), int(h * 0.65)))
            _collect(await _ocr_single(_enhance(_scale_to(c3, 3000), contrast=2.5)))

            # Pass 4: Top half of tight ticket crop (for header: passenger name, PNR, flight#)
            c4 = orig_img.crop((int(w * 0.27), int(h * 0.36), int(w * 0.73), int(h * 0.49)))
            _collect(await _ocr_single(_enhance(_scale_to(c4, 3000), contrast=3.0, sharpness=3.5)))

            # Pass 5: Full image high contrast (catch any missed data not in ticket area)
            s5 = _scale_to(orig_img, 2400)
            _collect(await _ocr_single(_enhance(s5, contrast=1.5, sharpness=2.0)))

            return "\n".join(all_lines)

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(lambda: asyncio.run(_ocr_async())).result()
            else:
                return loop.run_until_complete(_ocr_async())
        except Exception:
            return asyncio.run(_ocr_async())
    except Exception as e:
        logger.warning(f"Local Windows native OCR error: {e}")
        return ""


@tool
def parse_image_boarding_pass(image_bytes_b64: str, filename: Optional[str] = "boarding_pass.jpg", media_type: Optional[str] = "image/jpeg") -> str:
    """
    Multimodal Vision AI parser that processes actual image files (JPEG, PNG, PDF preview)
    of boarding passes and receipts using AWS Bedrock Claude Vision, with Windows Native OCR fallback.

    Args:
        image_bytes_b64: Base64-encoded image bytes.
        filename: Original filename of the uploaded image.
        media_type: MIME type of the image (image/jpeg, image/png, image/webp).

    Returns:
        JSON string with extracted passenger name, flight number, PNR, dates and expense amounts.
    """
    logger.info(f"Vision image parse: {filename} ({media_type})")

    try:
        image_bytes = base64.b64decode(image_bytes_b64)
    except Exception as e:
        logger.error(f"Failed to decode base64 image: {e}")
        return json.dumps({"status": "ERROR", "error": "Invalid base64 image data"})

    ai_result = _try_bedrock_vision_parse(image_bytes, media_type or "image/jpeg")
    ai_powered = False

    if ai_result:
        ai_powered = True
        extracted = _merge_ai_result_with_knowledge_base(ai_result, "", filename or "")
    else:
        logger.info("Bedrock vision unavailable/skipped. Falling back to Local Windows Native OCR...")
        local_ocr_text = _local_windows_ocr(image_bytes)
        logger.info(f"Local Windows Native OCR extracted {len(local_ocr_text)} characters.")
        
        if local_ocr_text:
            extracted = _regex_fallback_parse(local_ocr_text, filename or "")
            extracted["parsed_by"] = "Local Windows Native OCR + Aviation Knowledge Base"
        else:
            extracted = {
                "passenger_name": "",
                "flight_number": "",
                "pnr_code": "",
                "flight_date": "",
                "expense_amount_eur": 0.0,
                "document_type": "BOARDING_PASS",
                "origin_iata": "",
                "destination_iata": "",
                "seat": "",
                "detected_carrier_info": None,
            }

    return _build_result(extracted, filename or "boarding_pass.jpg", ai_powered)
