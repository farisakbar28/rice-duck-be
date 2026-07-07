import requests
import json

# Start by checking if server is running
try:
    response = requests.get('http://127.0.0.1:8000/health', timeout=2)
    print('Server is running')
except Exception as e:
    print('ERROR: Server is not running. Please start with: uvicorn app.main:app --reload')
    print(f'Error: {e}')
    exit(1)

# SoT example payload
payload = {
    'land_area_are': 10,
    'duck_count': 50,
    'rice_variety': 'sertani',
    'planting_system': 'jajar_legowo',
    'planting_date': '2026-01-01',
    'duck_age_days': 14
}

response = requests.post('http://127.0.0.1:8000/api/v1/dss/simulate', json=payload)

if response.status_code == 200:
    data = response.json()
    
    # Extract key values
    cost_labor_total = data.get('Cost_labor_total')
    cost_total_cash = data.get('Cost_total_cash')
    profit_net_cash = data.get('Profit_net_cash')
    valuation_weed_eco = data.get('Valuation_weed_eco')
    profit_net_full = data.get('Profit_net_full')
    
    # Check if Cost_labor_tending exists in response (it should NOT)
    has_tending = 'Cost_labor_tending' in data
    
    print('=== SoT Example Verification ===')
    print(f'Cost_labor_total: {cost_labor_total} (expected: 540955.0 ±0.5)')
    print(f'Cost_total_cash: {cost_total_cash} (expected: 2561008.0)')
    print(f'Profit_net_cash: {profit_net_cash} (expected: 1053392.0)')
    print(f'Valuation_weed_eco: {valuation_weed_eco} (expected: 101422.0)')
    print(f'Profit_net_full: {profit_net_full} (expected: 1154814.0)')
    print(f'Cost_labor_tending in response: {has_tending} (expected: False)')
    
    # Verify values
    tolerance = 0.5
    all_ok = True
    
    if cost_labor_total is None or abs(cost_labor_total - 540955.0) > tolerance:
        print(f'FAIL: Cost_labor_total mismatch')
        all_ok = False
    if cost_total_cash is None or abs(cost_total_cash - 2561008.0) > tolerance:
        print(f'FAIL: Cost_total_cash mismatch')
        all_ok = False
    if profit_net_cash is None or abs(profit_net_cash - 1053392.0) > tolerance:
        print(f'FAIL: Profit_net_cash mismatch')
        all_ok = False
    if valuation_weed_eco is None or abs(valuation_weed_eco - 101422.0) > tolerance:
        print(f'FAIL: Valuation_weed_eco mismatch')
        all_ok = False
    if profit_net_full is None or abs(profit_net_full - 1154814.0) > tolerance:
        print(f'FAIL: Profit_net_full mismatch')
        all_ok = False
    if has_tending:
        print(f'FAIL: Cost_labor_tending should NOT be in response')
        all_ok = False
    
    if all_ok:
        print('\n✓ ALL VERIFICATIONS PASSED')
    else:
        print('\n✗ SOME VERIFICATIONS FAILED')
        print('\nFull response:')
        print(json.dumps(data, indent=2))
else:
    print(f'ERROR: API returned status {response.status_code}')
    print(response.text)
