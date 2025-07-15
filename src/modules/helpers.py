# Misc Helper Functions

def tag(value):
    """
    Function to apply tag to folder name consistently based on value passed to function.
    """
    if value:
        return f" ({value})"
