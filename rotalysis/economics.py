import numpy as np
import numpy_financial as npf
import pandas as pd

from .definitions import EconomicsVariables


class Economics:
    @staticmethod
    def create_cashflow_df(capex, project_life):
        project_life = int(project_life) + 1
        dfcashflow = pd.DataFrame(
            data={
                EconomicsVariables.FUEL_COST: 0.0,
                EconomicsVariables.OPEX: 0.0,
                EconomicsVariables.CASH_FLOW: 0.0,
            },
            index=range(0, project_life),
        )
        dfcashflow = dfcashflow.rename_axis("year")
        dfcashflow.loc[0, EconomicsVariables.CASH_FLOW] = -capex
        return dfcashflow

    @staticmethod
    def inflation_adjusted_opex(opex, inflation_rate, years):
        adjusted_opex = [
            opex * ((1 + inflation_rate) ** (year - min(years))) for year in years
        ]
        return adjusted_opex

    @staticmethod
    def annualized_spending(NPV, discount_rate, project_life):
        annualized_spending = -NPV * (
            discount_rate / (1 - (1 + discount_rate) ** (-project_life))
        )
        return round(annualized_spending, 2)

    @staticmethod
    def GHG_reduction_cost(annualized_spending, GHG_reduction):
        if GHG_reduction == 0:
            return 0
        else:
            GHG_reduction_cost = annualized_spending / GHG_reduction
            return round(GHG_reduction_cost, 2)

    @staticmethod
    def calculate_payback_period(cash_flows):
        cumulative_cash_flow = 0
        payback_period = None

        for year, cash_flow in enumerate(cash_flows, start=0):
            cumulative_cash_flow += cash_flow

            if cumulative_cash_flow >= 0:
                payback_period = year
                break

        return (
            int(payback_period) if isinstance(payback_period, (int, float)) else "Never"
        )
