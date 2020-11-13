import random
import string

def generate_random_value(value_type: str, seed=None):
    """Given a name of a type, return random data in that type

    The value_type is the name of the type as a string. The type will
    will be checked and the appropriate value will be generated.
    The seed is optional but will be used to set the random seed for tests.
    """
    if seed is not None:
        random.seed(seed)

    if value_type == "str":
        value = ""
        # Get the maximum length that the ascii_letters has for use to index it later
        max_length = len(string.ascii_letters) - 1
        # Repeat for a random amount of characters in a reasonable range
        for character in range(random.randint(10, 30)):
            # Also adds the seed if its defined, the random seed resets after use
            # this sets up the seed for each iteration
            if seed is not None:
                random.seed(seed)
            # Get a random character from string.ascii_letters (a string of all ascii letters) and
            # add the char to the value, the final string
            value += string.ascii_letters[random.randint(0, max_length)]
        return value

    elif value_type == "int":
        return random.randint(0, 100)

    elif value_type == "float":
        return round(random.uniform(0, 100), 4)

    elif value_type == "bool":
        # Cast randint to bool
        return bool(random.randint(0, 1))
