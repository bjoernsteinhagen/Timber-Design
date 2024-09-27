class Convert:
    """The project works exclusively with SI units. This class helps with conversions."""

    @staticmethod
    def _convert_units(values, input_unit, conversion_factors):
        """
        Helper method to convert values using provided conversion factors.
        Raises ValueError if the input unit is unsupported.
        """
        if input_unit not in conversion_factors:
            raise ValueError(f"Unsupported unit: {input_unit}")

        factor = conversion_factors[input_unit]

        if isinstance(values, (int, float)):
            return float(values * factor)
        elif len(values) == 1:
            return float(values[0] * factor)
        else:
            return [float(value * factor) for value in values]

    @staticmethod
    def pressure(*values, input_unit: str = 'N/mm²'):
        """Converts a list of pressure units to SI units (Pascals, N/m²)"""
        pressure_conversion_factors = {
            'N/mm²': 1e6, # MPa to Pa
            'N/cm²': 1e4, # N/cm² to Pa
            'N/m²' : 1, # Pa is the base unit
            'psi': 6894.76, # psi to Pa
            'psf': 47.8803 # psf to Pa
        }

        return Convert._convert_units(values, input_unit, pressure_conversion_factors)

    @staticmethod
    def force(*values, input_unit: str = 'kN'):
        """
        Converts a list of force units to SI units (Newtons, N)
        """
        force_conversion_factors = {
            'N': 1,  # Newton is the base unit
            'kN': 1e3,  # Kilonewtons to Newtons
            'MN': 1e6,  # Meganewtons to Newtons
            'lbf': 4.44822,  # Pound-force to Newtons
            'tonf': 8896.44,  # Ton-force to Newtons
            'kgf': 9.80665  # Kilogram-force to Newtons
        }

        return Convert._convert_units(values, input_unit, force_conversion_factors)

    @staticmethod
    def length(*values, input_unit: str = 'm'):
        """
        Converts a list of length units to SI units (meters, m)
        """
        length_conversion_factors = {
            'm': 1,  # Meter is the base unit
            'mm': 0.001,  # Millimeters to meters
            'cm': 0.01,  # Centimeters to meters
            'km': 1000,  # Kilometers to meters
            'in': 0.0254,  # Inches to meters
            'ft': 0.3048,  # Feet to meters
            'yd': 0.9144,  # Yards to meters
            'mile': 1609.34  # Miles to meters
        }

        return Convert._convert_units(values, input_unit, length_conversion_factors)

    @staticmethod
    def area(*values, input_unit: str = 'm'):
        """
        Converts a list of area units to SI units (meters, m²)
        """
        length_conversion_factors = {
            'm': 1,  # Meter is the base unit
            'mm': 0.001**2,  # Millimeters to meters
            'cm': 0.01**2,  # Centimeters to meters
            'km': 1000**2,  # Kilometers to meters
            'in': 0.0254**2,  # Inches to meters
            'ft': 0.3048**2,  # Feet to meters
            'yd': 0.9144**2,  # Yards to meters
            'mile': 1609.34**2  # Miles to meters
        }

        return Convert._convert_units(values, input_unit, length_conversion_factors)

    @staticmethod
    def moment_of_inertia(*values, input_unit: str = 'm'):
        """
        Converts a list of area units to SI units (meters, m²)
        """
        length_conversion_factors = {
            'm': 1,  # Meter is the base unit
            'mm': 0.001**4,  # Millimeters to meters
            'cm': 0.01**4,  # Centimeters to meters
            'km': 1000**4,  # Kilometers to meters
            'in': 0.0254**4,  # Inches to meters
            'ft': 0.3048**4,  # Feet to meters
            'yd': 0.9144**4,  # Yards to meters
            'mile': 1609.34**4  # Miles to meters
        }

        return Convert._convert_units(values, input_unit, length_conversion_factors)
