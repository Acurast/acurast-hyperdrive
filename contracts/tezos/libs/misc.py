latest_var_id = 0
def generate_var(postfix=None):
    """
    Generate a unique variable name

    Necessary because of smartpy code inlining
    """
    global latest_var_id

    id = "utils_%s%s" % (latest_var_id, ("_" + postfix if postfix is not None else ""))
    latest_var_id += 1

    return id
