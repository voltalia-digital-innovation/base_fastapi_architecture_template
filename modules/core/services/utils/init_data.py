from sqlalchemy.orm import Session
from modules.core.database import get_db
from modules.basic_entries.models.Formula import Formula
from modules.basic_entries.models.Indicator import Indicator


def __generate_formula_and_indicator(db: Session):
    """
    Varieties:
        - Fixed cell (contract price, pld, etc...)
        - Basic expressions (+, -, *, /)
        - Consider last month (Annual)
        - Consider whole year till now (Quadrennial)
        - Conditional
        - AVG whole year till now (PLD)
        - MAX
    """
    print('\nBefore indicators\n')
    indicators = [
        {
            'name': 'generation_accumulated',
            'description': 'Year generation accumulated. The data is accumulated from the DB, there is no formula for that.',
            'formula': '',
            'human_readable_formula': 'SUM(generation_mwh)',
        },
        {
            'name': 'contract_accumulated',
            'description': 'Contract year generation accumulated. The data is accumulated from the contract registered on DB, there is no formula for that.',
            'formula': '',
            'human_readable_formula': 'SUM(contract_generation_mwh)',
        },
        {
            'name': 'delta_accumulated_perc',
            'description': 'The delta between generation_accumulated and contract_accumulated',
            'formula': 'lambda generation_accumulated,contract_accumulated: generation_accumulated / contract_accumulated',
            'human_readable_formula': 'generation_accumulated / contract_accumulated',
        },
        {
            'name': 'delta_accumulated_mwh',
            'description': 'The difference between generation_mwh and contract_generation',
            'formula': 'lambda generation_mwh,contract_generation: generation_mwh - contract_generation',
            'human_readable_formula': 'generation_mwh - contract_generation',
        },
        {
            'name': 'accrual_without_adjustment_and_price_effect ',
            'description': 'The multiplication between delta_accumulated_mwh and contract_price',
            'formula': 'lambda delta_accumulated_mwh,contract_price: delta_accumulated_mwh * contract_price',
            'human_readable_formula': 'delta_accumulated_mwh * contract_price',
        },
        {
            'name': 'accrual_quadrennial_mwh',
            'description': 'The quadrennial accrual in MWh',
            'formula': 'lambda delta_accumulated_mwh,delta_accumulated_perc,contract_accumulated: delta_accumulated_mwh if delta_accumulated_perc>=0.9 else contract_accumulated-contract_accumulated * 0.9',
            'human_readable_formula': '=IF(delta_accumulated_perc>=90%;delta_accumulated_mwh;(contract_accumulated-contract_accumulated*90%))',
        },
        {
            'name': 'accrual_annual_mwh',
            'description': '',
            'formula': 'lambda delta_accumulated_mwh,accrual_quadrennial_mwh: delta_accumulated_mwh - accrual_quadrennial_mwh',
            'human_readable_formula': 'delta_accumulated_mwh - accrual_quadrennial_mwh',
        },
        {
            'name': 'pld_avg_annual',
            'description': 'Year average pld. The data is accumulated from the DB, there is no formula for that.',
            'formula': '',
            'human_readable_formula': 'AVG(pld)',
        },
        {
            'name': 'pld_avg_quadrennial',
            'description': 'Quadrennial average pld. The data is accumulated from the DB, there is no formula for that.',
            'formula': '',
            'human_readable_formula': 'AVG(pld)',
        },
        {
            'name': 'accrual_price_annual',
            'description': 'Total Accrual Price Annual',
            'formula': 'lambda pld_avg_annual,contract_price: pld_avg_annual*1.15 if pld_avg_annual*1.15 > contract_price*1.15 else contract_price*1.15',
            'human_readable_formula': 'MAX(pld_avg_annual:contract_price) * 1.15',
        },
        {
            'name': 'accrual_price_quadrennial',
            'description': 'Total Accrual Price Quadrennial',
            'formula': 'lambda contract_price,accrual_quadrennial_mwh,pld_avg_quadrennial: contract_price if accrual_quadrennial_mwh > 0 else (pld_avg_quadrennial if pld_avg_quadrennial>contract_price else contract_price)',
            'human_readable_formula': '=IF(accrual_quadrennial_mwh>0;contract_price;MAX(pld_avg_quadrennial:contract_price;1))',
        },
        {
            'name': 'accrual_accumulated_quadrennial',
            'description': 'Total Accrual Quadrennial',
            'formula': 'lambda accrual_quadrennial_mwh,accrual_price_quadrennial: accrual_quadrennial_mwh * accrual_price_quadrennial',
            'human_readable_formula': 'accrual_quadrennial_mwh * accrual_price_quadrennial',
        },
        {
            'name': 'accrual_accumulated_annual',
            'description': 'Total Accrual Annual',
            'formula': 'lambda accrual_price_annual,accrual_annual_mwh: accrual_price_annual * accrual_annual_mwh',
            'human_readable_formula': 'accrual_price_annual * accrual_annual_mwh',
        },
        {
            'name': 'accrual_total',
            'description': 'Total Accrual',
            'formula': 'lambda accrual_accumulated_annual,accrual_quadrennial_mwh: accrual_accumulated_annual + accrual_quadrennial_mwh',
            'human_readable_formula': 'accrual_accumulated_annual + accrual_quadrennial_mwh',
        },
        {
            'name': 'accrual_total_generation_effect',
            'description': '',
            'formula': 'lambda: accrual_without_adjustment_and_price_effect: accrual_without_adjustment_and_price_effect',
            'human_readable_formula': 'accrual_without_adjustment_and_price_effect',
        },
        {
            'name': 'accrual_total_price_effect',
            'description': '',
            'formula': 'lambda accrual_total,accrual_total_generation_effect: accrual_total - accrual_total_generation_effect',
            'human_readable_formula': 'accrual_total - accrual_total_generation_effect',
        },

    ]
    print('\nAfter indicators\n')

    for index, indicator in enumerate(indicators):
        print(f'\nStarting object creation: {index}\n')
        formula = Formula(**{
            'string_formula': indicator['formula'],
            'description': indicator['description'],
            'human_readable_formula': indicator['human_readable_formula']
        })
        db.add(formula)
        db.flush()

        data = {
            'name': indicator['name'],
            'description': indicator['description'],
            'formula': formula,
        }
        db.add(Indicator(**data))
    print('\nIs about to commit...\n')
    db.commit()


def init_data():
    # Generating Formula and Indicators
    db: Session = next(get_db())
    print("Started Generating Formula and Indicators...\n")
    __generate_formula_and_indicator(db=db)
    print("Formula and Indicators were created successfully!\n\n")

    print("Init Data method has finished!")
