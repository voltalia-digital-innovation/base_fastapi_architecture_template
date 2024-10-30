from datetime import datetime
from modules.core.services.utils.methods import is_a_valid_month


class BaseValidator:
    """
    This class implements core validations to the application
    Author: Matheus Henrique (m.araujo)

    Date: 07th October 2024
    """

    def check_month_and_year_filter_parameters(
            self, year: str = None, month: str = None, optional: bool = True):
        """
        Will check if all parameters are valid

        Checks:
            - Year must be <= current year
            - Month must be <= current month

        Args:
            year (str): the desired year
            month (str): the desired month

        Author: Matheus Henrique (m.araujo)

        Date: 07th October 2024

        Returns:
            is_valid: bool
            messages: str
        """
        is_valid = True
        messages = []
        today = datetime.now()

        if optional == False and (year is None or month is None):
            is_valid = False
            messages.append('The year and month are required!')

        valid_year_condition = (year and str(year).isdigit()
                                and int(year) <= today.year)
        valid_month_condition = (month and is_a_valid_month(month))

        if year and not valid_year_condition:
            # Year must be <= current year
            is_valid = False
            messages.append('The year is not valid')
        if month and not valid_month_condition:
            # Month must be >= 1 or <= 12
            is_valid = False
            messages.append('The month is not valid')
        return is_valid, messages
