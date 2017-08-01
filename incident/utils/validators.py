from datetime import datetime
from incident.circuits import STATES_BY_CIRCUIT


def validate_choices(values, choices):
    """Ensure that the values given are valid choices for this field"""
    result = []
    options = [choice[0] for choice in choices]
    for value in values:
        if value in options:
            result.append(value)
    return result


def validate_date(date):
    try:
        valid_date = datetime.strptime(date, '%Y-%m-%d')
    except (ValueError, TypeError):
        return None
    return valid_date.date()


def validate_integer_list(lst):
    """Generate a list of integers from a list of string integers

    Note: strings that cannot be converted into integers are removed
    from the output.
    E.g. ['1', '2', 'a', '3'] --> [1, 2, 3]

    """
    result = []
    for e in lst:
        try:
            result.append(int(e))
        except ValueError:
            continue
    return result


def validate_bool(string):
    if string.title() in ('True', 'False'):
        return string.title()

    return None


def validate_circuits(circuits):
    validated_circuits = []
    for circuit in circuits:
        if circuit in STATES_BY_CIRCUIT.keys():
            validated_circuits.append(circuit)
    return validated_circuits
