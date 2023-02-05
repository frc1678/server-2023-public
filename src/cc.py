import numpy as np
import numpy.linalg as nl
from typing import List, TypedDict


class CCEvent(TypedDict):
    """
    Data structure to hold a calculated contribution event information.
    """

    parties: List[str]  # List of parties involved in the event
    value: float  # The value of the event


def cc(data: List[CCEvent], precision: int = 2) -> dict:
    """
    Calculates the contribution of each party to a set of events.

    Parameters
    ----------
    data : List[CCEvent]
        A list of `CCEvent` objects, representing each event.
    precision : int, optional
        The precision to round the calculated contribution to. Default is 2.

    Returns
    -------
    dict
        A dictionary mapping party names to their calculated contribution.
    """
    # Create a set to store the unique parties involved in the events
    parties = set()

    # Iterate through each event to add each involved party to the set
    for event in data:
        for party in event["parties"]:
            parties.add(party)

    # Sort the parties and create a matrix to store the parties' involvement in each event
    parties = sorted(parties)
    party_matrix = np.zeros((len(parties), len(data)))

    # Create a matrix to store the values of each event
    value_matrix = np.zeros((1, len(data)))

    # Iterate through each event to fill the party matrix and value matrix
    for event_index, event in enumerate(data):
        for team in event["parties"]:
            party_matrix[parties.index(team), event_index] = 1
        value_matrix[0, event_index] = event["value"]

    # Transpose the party matrix to prepare it for matrix multiplication
    transposed_party_matrix = np.transpose(party_matrix)

    # Multiply the party matrix with its transpose to get the left side of the equation
    left_side = np.matmul(party_matrix, transposed_party_matrix)

    # Multiply the value matrix with the transposed party matrix to get the right side of the equation
    right_side = np.matmul(value_matrix, transposed_party_matrix)

    # Solve the equation to get the calculated contribution of each party
    solved = nl.lstsq(left_side, right_side.transpose(), rcond=None)[0]

    # Return the calculated contribution rounded to the specified precision
    return {parties[i]: round(cc[0], precision) for i, cc in enumerate(solved)}
