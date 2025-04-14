#!/usr/bin/python3
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

def parse_jackpot_string(jackpot_str):
    try:
        print(f"Raw jackpot string: {jackpot_str}")
        amount = jackpot_str.replace('$', '').replace(',', '').strip().lower()
        return float(amount)
    except Exception as e:
        print(f"Parse error: {e}")
        return None

def scrape_jackpot(url):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        elem = soup.select_one("p.bigText")
        if elem:
            return parse_jackpot_string(elem.text.strip())
        else:
            print(f"Jackpot element not found at {url}")
            return None
    except Exception as e:
        print(f"Scrape error for {url}: {e}")
        return None

def estimate_draws(current_jackpot, historical_avg_draws=38, start_jackpot=82_000_000, target_jackpot=1_000_000_000):
    """
    Estimates the number of Powerball draws to reach $1 billion.
    """
    if not isinstance(current_jackpot, (int, float)) or current_jackpot <= 0:
        return None
    if not isinstance(historical_avg_draws, int) or historical_avg_draws <= 0:
        return None
    if current_jackpot >= target_jackpot:
        return 0
    remaining_amount = target_jackpot - current_jackpot
    total_growth_needed_hist = target_jackpot - start_jackpot
    if total_growth_needed_hist <= 0:
        return historical_avg_draws
    proportion_remaining = remaining_amount / total_growth_needed_hist
    estimated_draws = historical_avg_draws * proportion_remaining
    return round(estimated_draws)

def estimate_date_to_billion(current_jackpot, historical_avg_draws=38):
    """
    Estimates the approximate date when the Powerball jackpot might reach $1 billion.
    """
    if not isinstance(current_jackpot, (int, float)) or current_jackpot <= 0:
        return None
    if not isinstance(historical_avg_draws, int) or historical_avg_draws <= 0:
        return None
    if current_jackpot >= 1_000_000_000:
        return datetime.now().strftime("%Y-%m-%d")

    estimated_draws = estimate_draws(current_jackpot, historical_avg_draws)
    if estimated_draws is None:
        return None

    today = datetime.now()
    days_to_add = (estimated_draws // 3) * 7  # Full weeks
    remaining_draws = estimated_draws % 3

    estimated_date = today + timedelta(days=days_to_add)

    # Account for the remaining draws in the current/next week
    if remaining_draws == 1:
        days_to_add = 0
        if today.weekday() == 0: # Monday
            days_to_add = 0
        elif today.weekday() == 1: # Tuesday
            days_to_add = 6
        elif today.weekday() == 2: # Wednesday
            days_to_add = 4
        elif today.weekday() == 3: # Thursday
            days_to_add = 3
        elif today.weekday() == 4: # Friday
            days_to_add = 2
        elif today.weekday() == 5: # Saturday
            days_to_add = 1
        elif today.weekday() == 6: # Sunday
            days_to_add = 0 + 1 # To Monday
        estimated_date += timedelta(days=days_to_add)
    elif remaining_draws == 2:
        days_to_add = 0
        if today.weekday() == 0: # Monday
            days_to_add = 2 # To Wednesday
        elif today.weekday() == 1: # Tuesday
            days_to_add = 1 # To Wednesday
        elif today.weekday() == 2: # Wednesday
            days_to_add = 7 # To next Wednesday
        elif today.weekday() == 3: # Thursday
            days_to_add = 6
        elif today.weekday() == 4: # Friday
            days_to_add = 5
        elif today.weekday() == 5: # Saturday
            days_to_add = 4
        elif today.weekday() == 6: # Sunday
            days_to_add = 3 # To Wednesday
        estimated_date += timedelta(days=days_to_add)

    return estimated_date.strftime("%Y-%m-%d")

def generate_html(pb_data, mm_data):
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lottery Jackpot Estimates</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 10px; /* Reduced overall margin for mobile */
            background-color: #f0f8ff;
            color: #333;
        }}
        .container {{
            display: flex;
            flex-direction: column; /* Stack items vertically on smaller screens */
            gap: 20px;
            align-items: center; /* Center items horizontally */
            margin-top: 20px;
        }}
        .jackpot-card {{
            background-color: #fff;
            padding: 20px; /* Reduced padding for mobile */
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
            width: 95%; /* Make cards take up most of the screen width */
            max-width: 400px; /* Limit maximum width */
            text-align: center;
            border: 1px solid #e0e0e0;
        }}
        h2 {{
            color: #2e8b57;
            margin-top: 0;
            margin-bottom: 15px; /* Reduced bottom margin */
            font-size: 1.8em; /* Slightly smaller heading */
        }}
        p {{
            color: #555;
            margin-bottom: 10px; /* Reduced bottom margin */
            font-size: 1em;
        }}
        .jackpot-amount {{
            font-size: 1.6em; /* Slightly smaller jackpot amount */
            color: #ff8c00;
            font-weight: bold;
        }}
        .after-tax {{
            color: #888;
            font-size: 0.8em;
            font-style: italic;
        }}
        .error {{
            color: #dc143c;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <h1>Current Lottery Jackpot Estimates</h1>
    <div class="container">
        <div class="jackpot-card">
            <h2>Powerball</h2>
            {''.join([f'<p>{key}: <span class="{key.lower().replace(" ", "-")}">{value}</span></p>' for key, value in pb_data.items()])}
        </div>
        <div class="jackpot-card">
            <h2>Mega Millions</h2>
            {''.join([f'<p>{key}: <span class="{key.lower().replace(" ", "-")}">{value}</span></p>' for key, value in mm_data.items()])}
        </div>
    </div>
</body>
</html>"""
    return html_content

def main():
    print("Fetching current jackpots...\n")

    powerball_url = "https://www.lottonumbers.com/powerball"
    megamillions_url = "https://www.lottonumbers.com/mega-millions"

    pb_jackpot = scrape_jackpot(powerball_url)
    mm_jackpot = scrape_jackpot(megamillions_url)

    tax_rate = 0.73  # 73% tax rate
    pb_data = {}
    mm_data = {}

    if pb_jackpot:
        pb_draws = estimate_draws(pb_jackpot)
        pb_est_date = estimate_date_to_billion(pb_jackpot)
        pb_jackpot_after_tax = pb_jackpot * (1 - tax_rate)
        pb_data = {
            "Jackpot": f"<span class='jackpot-amount'>${int(pb_jackpot):,}</span>",
            "Cash option after taxes (est. 27%)": f"<span class='after-tax'>${int(pb_jackpot_after_tax):,}</span>",
            "Estimated Draws to $1B": pb_draws if pb_draws is not None else "N/A",
            "Estimated Date to $1B": pb_est_date if pb_est_date else "N/A"
        }
    else:
        pb_data = {"Error": "<span class='error'>Powerball jackpot could not be retrieved.</span>"}

    if mm_jackpot:
        mm_draws = estimate_draws(mm_jackpot) # Using the same historical average for MM as a rough guess
        mm_est_date = estimate_date_to_billion(mm_jackpot) # Using the same logic
        mm_jackpot_after_tax = mm_jackpot * (1 - tax_rate)
        mm_data = {
            "Jackpot": f"<span class='jackpot-amount'>${int(mm_jackpot):,}</span>",
            "Cash Option after taxes (est. 27%)": f"<span class='after-tax'>${int(mm_jackpot_after_tax):,}</span>",
            "Estimated Draws to $1B": mm_draws if mm_draws is not None else "N/A",
            "Estimated Date to $1B": mm_est_date if mm_est_date else "N/A"
        }
    else:
        mm_data = {"Error": "<span class='error'>Mega Millions jackpot could not be retrieved.</span>"}

    html_output = generate_html(pb_data, mm_data)

    with open("/var/www/html/lottery/index.html", "w") as f:
        f.write(html_output)

    print("\nLottery jackpot estimates saved to lottery_estimates.html")

if __name__ == "__main__":
    main()
