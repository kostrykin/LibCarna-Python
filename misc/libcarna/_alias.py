import functools


def kwalias(keyword: str, *aliases: str):
    """
    Create an alias for a keyword.

    Arguments:
        keyword: The original keyword.
        *aliases: The aliases for the keyword.
    """
    if keyword in aliases:
        raise ValueError(f"Keyword and alias cannot be the same: '{keyword}'.")

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            used_aliases = list()
            for alias in [keyword] + list(aliases):
                if alias in kwargs:
                    used_aliases.append(alias)
                    if len(used_aliases) > 1:
                        raise ValueError(f"Both '{used_aliases[0]}' and '{used_aliases[1]}' provided.")
                    kwargs[keyword] = kwargs.pop(alias)
            return func(*args, **kwargs)
        
        return wrapper

    return decorator
