from datetime import datetime, timedelta

def calculate_user_streak(dates: list, current_date: datetime = None) -> int:
    if not dates:
        return 0
    
    # Sort descending
    clean_dates = sorted(list(set(d for d in dates if d)), reverse=True)
    if not clean_dates:
        return 0
    
    now_dt = current_date or datetime.now()
    today_str = now_dt.strftime("%Y-%m-%d")
    yesterday_str = (now_dt - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Check if the streak is active (practiced today or yesterday)
    if clean_dates[0] != today_str and clean_dates[0] != yesterday_str:
        return 0
    
    streak = 1
    for i in range(len(clean_dates) - 1):
        try:
            d1 = datetime.strptime(clean_dates[i], "%Y-%m-%d")
            d2 = datetime.strptime(clean_dates[i + 1], "%Y-%m-%d")
            diff = (d1 - d2).days
            if diff == 1:
                streak += 1
            else:
                break
        except Exception:
            break
            
    return streak

def run_tests():
    now = datetime(2026, 10, 7) # Wednesday
    
    # Case 1: Empty history
    assert calculate_user_streak([], now) == 0, "Test 1 failed"
    
    # Case 2: Practiced today only
    assert calculate_user_streak(["2026-10-07"], now) == 1, "Test 2 failed"
    
    # Case 3: Practiced today and yesterday
    assert calculate_user_streak(["2026-10-07", "2026-10-06"], now) == 2, "Test 3 failed"
    
    # Case 4: Practiced today, yesterday, and day before yesterday
    assert calculate_user_streak(["2026-10-07", "2026-10-06", "2026-10-05"], now) == 3, "Test 4 failed"
    
    # Case 5: Practiced yesterday and day before, but hasn't practiced yet today (streak active)
    assert calculate_user_streak(["2026-10-06", "2026-10-05"], now) == 2, "Test 5 failed"
    
    # Case 6: Practiced today and 2 days ago (missed yesterday) -> streak should be 1
    assert calculate_user_streak(["2026-10-07", "2026-10-05"], now) == 1, "Test 6 failed"
    
    # Case 7: Missed both yesterday and today (practiced 2 days ago and 3 days ago) -> streak broken (0)
    assert calculate_user_streak(["2026-10-05", "2026-10-04"], now) == 0, "Test 7 failed"
    
    # Case 8: Duplicate dates in history on same day
    assert calculate_user_streak(["2026-10-07", "2026-10-07", "2026-10-06", "2026-10-06"], now) == 2, "Test 8 failed"
    
    print("[SUCCESS] ALL 8 STREAK LOGIC TEST CASES PASSED!")

if __name__ == "__main__":
    run_tests()
