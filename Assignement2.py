# Part 1: Clean CSV using only base Python
def clean_csv_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    headers = lines[0].strip().split(',')
    data = []

    for line in lines[1:]:
        values = line.strip().split(',')

        if len(values) != len(headers):
            continue  # skip malformed rows

        row = dict(zip(headers, values))

        # Clean fields: strip extra spaces, handle nulls, invalids
        cleaned_row = {}
        for key, value in row.items():
            value = value.strip()
            if value == '' or value.lower() in ['na', 'null', 'none']:
                cleaned_row[key] = None
            else:
                cleaned_row[key] = value
        data.append(cleaned_row)

    return headers, data
    
# Part 2: Decision based on city-wise claim analysis
def analyze_city_shutdown(data):
    target_cities = ["pune", "kolkata", "ranchi", "guwahati"]
    city_stats = {}

    for row in data:
        city = row.get("CITY")
        if city:
            city = city.strip().lower()  # normalize city name

        claim_amt = row.get("CLAIM_AMOUNT")
        claim_status = row.get("CLAIM_STATUS")

        if city in target_cities:
            if city not in city_stats:
                city_stats[city] = {
                    "total_claims": 0,
                    "total_paid": 0.0,
                    "paid_count": 0,
                    "rejected_count": 0
                }

            city_stats[city]["total_claims"] += 1

            if claim_status and claim_status.lower() == "paid":
                try:
                    amt = float(claim_amt)
                    city_stats[city]["total_paid"] += amt
                    city_stats[city]["paid_count"] += 1
                except:
                    pass
            elif claim_status and claim_status.lower() == "rejected":
                city_stats[city]["rejected_count"] += 1

    if not city_stats:
        print("No matching cities found in data. Check 'CITY' column values.")
        return None, {}

    shutdown_city = min(city_stats.items(), key=lambda x: x[1]["total_paid"])[0]
    return shutdown_city, city_stats


# Corrected handle_error
def handle_error(error_message):
    print(f"Error: {error_message}")
    return "Error"

# Corrected contains_rejection_reason
def contains_rejection_reason(rejection_text, reason):
    try:
        if rejection_text and isinstance(rejection_text, str):
            return reason.lower() in rejection_text.lower()
    except Exception as e:
        handle_error(f"Error in contains_rejection_reason: {str(e)}")
    return False

# Corrected map_rejection_reason
REJECTION_REASONS_MAP = {
    "Fake_document": "Fake_document",
    "Not_Covered": "Not_Covered",
    "Policy_expired": "Policy_expired"
}

def map_rejection_reason(rejection_text):
    try:
        if rejection_text and isinstance(rejection_text, str):
            for reason, rejection_class in REJECTION_REASONS_MAP.items():
                if contains_rejection_reason(rejection_text, reason):
                    return rejection_class
            return "Unknown"
        else:
            return "NoRemark"
    except Exception as e:
        handle_error(f"Error in map_rejection_reason: {str(e)}")
        return "Error"

# Corrected complex_rejection_classifier
def complex_rejection_classifier(remark_text):
    try:
        if not remark_text or not isinstance(remark_text, str) or len(remark_text.strip()) == 0:
            return "Invalid Remark"

        if contains_rejection_reason(remark_text, "Fake_document"):
            return "Fake_document"
        elif contains_rejection_reason(remark_text, "Not_Covered"):
            return "Not_Covered"
        elif contains_rejection_reason(remark_text, "Policy_expired"):
            return "Policy_expired"
        else:
            return map_rejection_reason(remark_text)
    except Exception as e:
        handle_error(f"Error in complex_rejection_classifier: {str(e)}")
        return "Error"


headers, cleaned_data = clean_csv_data(r"C:\Users\shiva\OneDrive\Desktop\Insurance_auto_data.csv")

# City analysis

#city_to_close, city_summary = analyze_city_shutdown(cleaned_data)
#print("City recommended for shutdown:", city_to_close)
#print("City summary:", city_summary)

city_to_shutdown, summary = analyze_city_shutdown(cleaned_data)
print("Recommended city for shutdown:", city_to_shutdown)
print("Full summary:")
for city, stats in summary.items():
    print(city, stats)


# Apply classifier to sample data
for row in cleaned_data:
    remark = row.get("REJECTION_REMARKS")
    row["REJECTION_CLASS"] = complex_rejection_classifier(remark)
