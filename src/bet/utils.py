import logging


logger = logging.getLogger(__name__)
def calculate_arb(koef1, koef2):
    logger.debug(f"Calculate arbs koefs {koef1} {koef2}")
    arb = 1 - ((1 / float(koef1)) + (1 / float(koef2)))
    logger.debug(f"Actual arb {arb}")
    return arb


def calculate_value(koef1, koef2):
    value = (1 / float(koef1)) * 100 - (1 / float(koef2)) * 100
    logger.debug(f"Actual value {value}")
    return value


