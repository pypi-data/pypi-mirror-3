# Present value of a cash flow
def pv(cash_flow, period, cost_of_capital):
    """
    Input: cash_flow, year, cost_of_capital
    Output: present value of cash_flow
    """
    return cash_flow / (1.0 + cost_of_capital) ** period

# Discounted cash flow of a cash flow generating (losing) entity
def dcf(cash_flows, cost_of_capital):
    """
    Input: a dictionary or list of cash flows, cost_of_capital
    If given a list, year corresponds to index. All values must be numbers.
    If given a dictionary, expects year:cash_flow format. All values must be numbers.
    Output: value of cash flow generating entity/business
    """
    
    def dcf_list(cash_flow_iterable, cost_of_capital):
        return reduce(lambda x, y: x + y, 
                [pv(val, period, cost_of_capital=cost_of_capital) for period, val in enumerate(cash_flows)])
    
    def dcf_dict(cash_flow_iterable, cost_of_capital):
        return reduce(lambda x, y: x + y, 
                [pv(val, period, cost_of_capital=cost_of_capital) for period, val in cash_flows.items()])
    
    dispatch = {list:dcf_list, dict:dcf_dict}
    
    try:
        return dispatch[type(cash_flows)](cash_flows, cost_of_capital=cost_of_capital)
    except KeyError:
        print("error: dcf only supports type list or dict for cash_flows")
