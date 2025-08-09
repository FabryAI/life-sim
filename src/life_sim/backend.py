def get_backend(backend_name: str):
    """
    Ritorna (xp, on_gpu) dove xp è numpy o cupy compatibile.
    Se 'cupy' non è installato, ricade su numpy.
    """
    if backend_name.lower() == "cupy":
        try:
            import cupy as xp
            return xp, True
        except Exception:
            import numpy as xp
            return xp, False
    else:
        import numpy as xp
        return xp, False
