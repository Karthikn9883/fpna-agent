from agent.intents import classify

def test_intent_classify():
    assert classify('What was June 2025 revenue vs budget?') == 'revenue_vs_budget'
    assert classify('Show gross margin % trend for the last 3 months') == 'gm_trend'
    assert classify('Break down Opex by category for June') == 'opex_breakdown'
    assert classify('What is our cash runway right now?') == 'cash_runway'
