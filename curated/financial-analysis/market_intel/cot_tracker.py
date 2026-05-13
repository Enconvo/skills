import pandas as pd
import requests
import zipfile
import io
import json
import argparse
from datetime import datetime

# Target assets mapping
FIN_ASSETS = {
    "Bitcoin": "BITCOIN - CHICAGO MERCANTILE EXCHANGE",
    "S&P 500": "E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE",
    "Nasdaq 100": "NASDAQ-100 Consolidated - CHICAGO MERCANTILE EXCHANGE",
    "10Y Treasury": "10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE",
    "Euro FX": "EURO FX - CHICAGO MERCANTILE EXCHANGE",
}

DISAGG_ASSETS = {
    "Gold": "GOLD - COMMODITY EXCHANGE INC.",
    "Crude Oil": "CRUDE OIL, LIGHT SWEET-WTI - ICE FUTURES EUROPE",
    "Copper": "COPPER-GRADE #1 - COMMODITY EXCHANGE INC."
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

def get_cftc_df(url):
    #print(f"Fetching {url}...")
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(response.content))
    csv_file = z.namelist()[0]
    with z.open(csv_file) as f:
        df = pd.read_csv(f, low_memory=False)
        # Parse date
        if 'Report_Date_as_MM_DD_YYYY' in df.columns:
             df['Report_Date_as_YYYY-MM-DD'] = pd.to_datetime(df['Report_Date_as_MM_DD_YYYY'])
        else:
             df['Report_Date_as_YYYY-MM-DD'] = pd.to_datetime(df['Report_Date_as_YYYY-MM-DD'])
        
        df = df.sort_values('Report_Date_as_YYYY-MM-DD', ascending=False)
        return df

def get_combined_history(years=[2024, 2025, 2026]):
    # Fetch Fin and Disagg for all requested years
    dfs_fin = []
    dfs_disagg = []
    
    current_year = datetime.now().year
    
    for y in years:
        if y > current_year: continue
        
        fin_url = f"https://www.cftc.gov/files/dea/history/fut_fin_txt_{y}.zip"
        try:
            dfs_fin.append(get_cftc_df(fin_url))
        except Exception as e:
            # print(f"Skipping Fin {y}: {e}")
            pass

        disagg_url = f"https://www.cftc.gov/files/dea/history/fut_disagg_txt_{y}.zip"
        try:
            dfs_disagg.append(get_cftc_df(disagg_url))
        except Exception as e:
            # print(f"Skipping Disagg {y}: {e}")
            pass
            
    if not dfs_fin or not dfs_disagg:
        raise ValueError("Could not fetch data")
        
    full_fin = pd.concat(dfs_fin).sort_values('Report_Date_as_YYYY-MM-DD', ascending=False)
    full_disagg = pd.concat(dfs_disagg).sort_values('Report_Date_as_YYYY-MM-DD', ascending=False)
    
    return full_fin, full_disagg

def process_asset_history(df, market_name, category="Financial"):
    # Filter for asset
    sub = df[df['Market_and_Exchange_Names'] == market_name].copy()
    if sub.empty:
        return []
        
    history = []
    
    # Sort descending date (newest first)
    sub = sub.sort_values('Report_Date_as_YYYY-MM-DD', ascending=False)
    
    for _, row in sub.iterrows():
        date_str = row['Report_Date_as_YYYY-MM-DD'].strftime('%Y-%m-%d')
        open_interest = row.get('Open_Interest_All', 0)
        
        entry = {
            "date": date_str,
            "open_interest": int(open_interest),
            "category": category
        }
        
        if category == "Financial":
            # Lev Money (Hedge Funds)
            lev_long = row.get('Lev_Money_Positions_Long_All', 0)
            lev_short = row.get('Lev_Money_Positions_Short_All', 0)
            entry['hedge_fund_net'] = int(lev_long - lev_short)
            entry['hedge_fund_long'] = int(lev_long)
            entry['hedge_fund_short'] = int(lev_short)
            
            # Asset Manager (Real Money)
            am_long = row.get('Asset_Mgr_Positions_Long_All', 0)
            am_short = row.get('Asset_Mgr_Positions_Short_All', 0)
            entry['asset_mgr_net'] = int(am_long - am_short)
            
        else: # Commodity
            # Managed Money (Hedge Funds)
            mm_long = row.get('M_Money_Positions_Long_All', 0)
            mm_short = row.get('M_Money_Positions_Short_All', 0)
            entry['hedge_fund_net'] = int(mm_long - mm_short)
            entry['hedge_fund_long'] = int(mm_long)
            entry['hedge_fund_short'] = int(mm_short)
            
            # Producer/Merchant (Commercials)
            prod_long = row.get('Prod_Merc_Positions_Long_All', 0)
            prod_short = row.get('Prod_Merc_Positions_Short_All', 0)
            entry['commercial_net'] = int(prod_long - prod_short)
            
        history.append(entry)
        
    return history

def analyze_fin(df):
    results = {}
    for asset_name, market_name in FIN_ASSETS.items():
        sub = df[df['Market_and_Exchange_Names'] == market_name]
        if sub.empty:
            continue
        
        # Get latest and previous weeks for change calculation
        latest = sub.iloc[0]
        prev = sub.iloc[1] if len(sub) > 1 else None
        
        # Leveraged Funds (Hedge Funds / Speculators)
        long_pos = latest['Lev_Money_Positions_Long_All']
        short_pos = latest['Lev_Money_Positions_Short_All']
        net_pos = long_pos - short_pos
        
        prev_net = (prev['Lev_Money_Positions_Long_All'] - prev['Lev_Money_Positions_Short_All']) if prev is not None else 0
        wow_change = net_pos - prev_net
        
        # Asset Managers (Institutional)
        am_long = latest['Asset_Mgr_Positions_Long_All']
        am_short = latest['Asset_Mgr_Positions_Short_All']
        am_net = am_long - am_short
        
        results[asset_name] = {
            "date": latest['Report_Date_as_YYYY-MM-DD'].strftime('%Y-%m-%d'),
            "category": "Financial",
            "hedge_fund_net": int(net_pos),
            "hedge_fund_wow": int(wow_change),
            "asset_mgr_net": int(am_net),
            "bias": "Bullish" if net_pos > 0 else "Bearish"
        }
    return results

def analyze_disagg(df):
    results = {}
    for asset_name, market_name in DISAGG_ASSETS.items():
        sub = df[df['Market_and_Exchange_Names'] == market_name]
        if sub.empty:
            continue
            
        latest = sub.iloc[0]
        prev = sub.iloc[1] if len(sub) > 1 else None
        
        # Managed Money (Hedge Funds / CTAs)
        long_pos = latest['M_Money_Positions_Long_All']
        short_pos = latest['M_Money_Positions_Short_All']
        net_pos = long_pos - short_pos
        
        prev_net = (prev['M_Money_Positions_Long_All'] - prev['M_Money_Positions_Short_All']) if prev is not None else 0
        wow_change = net_pos - prev_net
        
        results[asset_name] = {
            "date": latest['Report_Date_as_YYYY-MM-DD'].strftime('%Y-%m-%d'),
            "category": "Commodity",
            "hedge_fund_net": int(net_pos),
            "hedge_fund_wow": int(wow_change),
            "bias": "Bullish" if net_pos > 0 else "Bearish"
        }
    return results

def compute_analytics(history_list):
    """Compute percentile, streak, flip, extreme from weekly history.
    
    history_list: list of dicts sorted newest-first, each with 'hedge_fund_net' and 'date'.
    Returns analytics dict for the latest week.
    """
    if not history_list or len(history_list) < 4:
        return {}
    
    nets = [w["hedge_fund_net"] for w in history_list if w.get("hedge_fund_net") is not None]
    if not nets:
        return {}
    
    latest_net = nets[0]
    
    # Percentile (0-100): what % of historical readings are below current
    below = sum(1 for n in nets if n < latest_net)
    percentile = round(below / len(nets) * 100, 1)
    
    # Streak: consecutive weeks net moved in same direction
    streak = 0
    if len(nets) >= 2:
        direction = 1 if nets[0] > nets[1] else -1
        for i in range(1, len(nets)):
            if i + 1 >= len(nets):
                break
            weekly_dir = 1 if nets[i] > nets[i + 1] else -1
            if weekly_dir == direction:
                streak += 1
            else:
                break
        streak = streak * direction  # positive = consecutive increases, negative = consecutive decreases
    
    # Flip: did net position change sign this week vs last?
    flip = False
    if len(nets) >= 2:
        flip = (nets[0] > 0 and nets[1] <= 0) or (nets[0] <= 0 and nets[1] > 0)
    
    # Extreme: >90th or <10th percentile
    extreme = None
    if percentile >= 90:
        extreme = "EXTREME_LONG"
    elif percentile <= 10:
        extreme = "EXTREME_SHORT"
    
    # 2-year range
    min_net = min(nets)
    max_net = max(nets)
    
    # WoW change
    wow = nets[0] - nets[1] if len(nets) >= 2 else 0
    
    return {
        "percentile_2y": percentile,
        "streak_weeks": streak,
        "flip_signal": flip,
        "extreme": extreme,
        "range_2y_min": min_net,
        "range_2y_max": max_net,
        "weeks_of_data": len(nets),
        "wow_change": wow,
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch and analyze CFTC COT data")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--history", action="store_true", help="Fetch full history (2024-Present)")
    parser.add_argument("--analytics", action="store_true", help="Include historical analytics (percentile, streak, flip, extreme)")
    args = parser.parse_args()
    
    current_year = datetime.now().year

    if args.history:
        # Full history mode
        try:
            fin_df, disagg_df = get_combined_history([2024, 2025, 2026])
            
            output = {}
            
            for name, market in FIN_ASSETS.items():
                output[name] = process_asset_history(fin_df, market, "Financial")
                
            for name, market in DISAGG_ASSETS.items():
                output[name] = process_asset_history(disagg_df, market, "Commodity")
                
            if args.json:
                print(json.dumps(output, indent=2))
            
        except Exception as e:
            if args.json:
                print(json.dumps({"error": str(e)}))
            else:
                print(f"Error: {e}")
        return

    # Default mode (latest snapshot)
    fin_url = f"https://www.cftc.gov/files/dea/history/fut_fin_txt_{current_year}.zip"
    disagg_url = f"https://www.cftc.gov/files/dea/history/fut_disagg_txt_{current_year}.zip"
    
    if not args.json:
        print(f"Fetching CFTC COT Reports for {current_year}...")
        
    try:
        df_fin = get_cftc_df(fin_url)
        fin_results = analyze_fin(df_fin)
        
        df_disagg = get_cftc_df(disagg_url)
        disagg_results = analyze_disagg(df_disagg)
        
        combined = {**fin_results, **disagg_results}
        
        # Add historical analytics if requested
        if args.analytics:
            try:
                fin_df_hist, disagg_df_hist = get_combined_history([2024, 2025, 2026])
                all_history = {}
                for name, market in FIN_ASSETS.items():
                    all_history[name] = process_asset_history(fin_df_hist, market, "Financial")
                for name, market in DISAGG_ASSETS.items():
                    all_history[name] = process_asset_history(disagg_df_hist, market, "Commodity")
                
                for asset_name in combined:
                    if asset_name.startswith("_"):
                        continue
                    hist = all_history.get(asset_name, [])
                    analytics = compute_analytics(hist)
                    if analytics:
                        combined[asset_name]["analytics"] = analytics
            except Exception as e:
                combined["_analytics_error"] = str(e)
        
        # Add staleness metadata
        all_dates = [v["date"] for v in combined.values() if "date" in v]
        latest_data_date = max(all_dates) if all_dates else None
        if latest_data_date:
            data_dt = datetime.strptime(latest_data_date, "%Y-%m-%d")
            days_old = (datetime.now() - data_dt).days
            # Next CFTC release: Friday 3:30 PM ET (Sat 3:30 AM SGT)
            # Data is always for Tuesday positions
            from datetime import timedelta
            today = datetime.now()
            days_until_friday = (4 - today.weekday()) % 7
            if days_until_friday == 0 and today.hour >= 16:  # past release time
                days_until_friday = 7
            next_release = (today + timedelta(days=days_until_friday)).strftime("%Y-%m-%d")
            combined["_meta"] = {
                "data_as_of": latest_data_date,
                "days_old": days_old,
                "next_release": f"{next_release} (Fri 3:30PM ET / Sat 3:30AM SGT)",
            }
        
        if args.json:
            print(json.dumps(combined, indent=2))
        else:
            print("\n" + "="*60)
            print(f"  SMART MONEY POSITIONING (CFTC COT REPORT) ")
            print("="*60)
            
            for asset, data in combined.items():
                print(f"  {asset:<15} | Date: {data['date']}")
                
                net = data['hedge_fund_net']
                wow = data['hedge_fund_wow']
                sign = "+" if net > 0 else ""
                w_sign = "+" if wow > 0 else ""
                trend = "🟢 Buying" if wow > 0 else "🔴 Selling"
                
                print(f"     Hedge Fund Net : {sign}{net:,} contracts")
                print(f"     WoW Change     : {w_sign}{wow:,} ({trend})")
                
                if 'asset_mgr_net' in data:
                    am_net = data['asset_mgr_net']
                    am_sign = "+" if am_net > 0 else ""
                    print(f"     Asset Mgr Net  : {am_sign}{am_net:,} contracts")
                print("-" * 60)
                
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Failed to fetch or parse CFTC data: {e}")

if __name__ == "__main__":
    main()
