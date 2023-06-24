import pint
from pint.errors import UndefinedUnitError


class UnitConvertor:
    @staticmethod
    def convert(value, from_unit, to_unit):
        ureg = pint.UnitRegistry()
        Q_ = ureg.Quantity
        return Q_(value, from_unit).to(to_unit).magnitude

    @staticmethod
    def convert_MMSCFD_to_kg_per_h(value, MW):
        converted_value = (
            UnitConvertor.convert(value * 1e6, "ft**3/day", "m**3/h") / 1.057 / 22.414 * MW
        )
        return converted_value
