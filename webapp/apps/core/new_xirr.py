from datetime import datetime


def sppv(i, n):
    """
    :param i:
    :param n:
    :return:
    """
    result=[]
    const = (1 + i/100)
    for j in list(n):
        result.append(const**(-j))
    return result

def npv(x, i):
    """
    :param x:
    :param i:
    :return:
    """
    npv = []
    pvs = []
    rhs = sppv(i, range(1,len(x)+1))
    for k in range(len(rhs)):
        pvs.append(x[k] * rhs[k])
    npv.append(sum(pvs))

    return npv

def new_xirr(cashflow):
    """
    :param cashflow:
    :return: The xirr for a given cashflow
    """
    cashflow.sort(key=lambda tup: tup[0])
    cashflow_adj=[cashflow[0][1]]
    for i in range(len(cashflow)-1):

        interval = (cashflow[i+1][0]-cashflow[i][0]).days
        #interval=(dates[i+1]-dates[i]).days
        cashflow_adj = cashflow_adj+[0]*(interval-1)+[cashflow[i+1][1]]

    left = -10
    right = 10
    epsilon = 1e-8
    while (abs(right-left) > 2*epsilon):
        midpoint = (right+left)/2
        lhs=npv(cashflow_adj, left)
        rhs=npv(cashflow_adj, midpoint)

        if (lhs[0]*rhs[0] > 0):
            left = midpoint
        else:
            right = midpoint

    irr = (right+left) / 2 / 100
    irr = irr * 365
    irr = (1 + irr / 365) ** 365 - 1
    return irr
