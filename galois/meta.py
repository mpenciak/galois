"""
A module that defines Meta which is a base class for GroupMeta, RingMeta, and FieldMeta.
"""
import numpy as np

from .meta_func import Func
from .meta_ufunc import Ufunc

# pylint: disable=abstract-method


class Meta(Ufunc, Func):
    """
    A base class for :obj:`GroupMeta`, :obj:`RingMeta`, and :obj:`FieldMeta`.
    """
    # pylint: disable=no-value-for-parameter,comparison-with-callable,too-many-public-methods

    def __new__(cls, name, bases, namespace, **kwargs):  # pylint: disable=unused-argument
        return super().__new__(cls, name, bases, namespace)

    def __init__(cls, name, bases, namespace, **kwargs):
        super().__init__(name, bases, namespace, **kwargs)
        cls._order_str = None

        cls._ufunc_mode = None
        cls._ufunc_target = None

    def __str__(cls):
        return f"<class 'numpy.ndarray over {cls.name}'>"

    def __repr__(cls):
        return f"<class 'numpy.ndarray over {cls.name}'>"

    ###############################################################################
    # Methods
    ###############################################################################

    def compile(cls, mode, target="cpu"):
        """
        Recompile the just-in-time compiled numba ufuncs with a new calculation mode or target.

        Parameters
        ----------
        mode : str
            The method of field computation, either `"jit-lookup"`, `"jit-calculate"`, `"python-calculate"`. The "jit-lookup" mode will
            use Zech log, log, and anti-log lookup tables for speed. The "jit-calculate" mode will not store any lookup tables, but perform field
            arithmetic on the fly. The "jit-calculate" mode is designed for large fields that cannot store lookup tables in RAM.
            Generally, "jit-calculate" is slower than "jit-lookup". The "python-calculate" mode is reserved for extremely large fields. In
            this mode the ufuncs are not JIT-compiled, but are pur python functions operating on python ints. The list of valid
            modes for this field is in :obj:`galois.GFMeta.ufunc_modes`.
        target : str, optional
            The `target` keyword argument from :obj:`numba.vectorize`, either `"cpu"`, `"parallel"`, or `"cuda"`. The default
            is `"cpu"`. For extremely large fields the only supported target is `"cpu"` (which doesn't use numba it uses pure python to
            calculate the field arithmetic). The list of valid targets for this field is in :obj:`galois.GFMeta.ufunc_targets`.
        """
        mode = cls.default_ufunc_mode if mode == "auto" else mode
        if mode not in cls.ufunc_modes:
            raise ValueError(f"Argument `mode` must be in {cls.ufunc_modes} for {cls.name}, not {mode}.")
        if target not in cls.ufunc_targets:
            raise ValueError(f"Argument `target` must be in {cls.ufunc_targets} for {cls.name}, not {target}.")

        if mode == cls.ufunc_mode and target == cls.ufunc_target:
            # Don't need to rebuild these ufuncs
            return

        cls._ufunc_mode = mode
        cls._ufunc_target = target
        cls._compile_ufuncs(target)
        cls._compile_funcs(target)

    ###############################################################################
    # Array display methods
    ###############################################################################

    def _formatter(cls, array):  # pylint: disable=no-self-use,unused-argument
        return {}

    ###############################################################################
    # Class attributes
    ###############################################################################

    @property
    def structure(cls):
        raise NotImplementedError

    @property
    def short_name(cls):
        raise NotImplementedError

    @property
    def name(cls):
        raise NotImplementedError

    @property
    def order(cls):
        raise NotImplementedError

    @property
    def dtypes(cls):
        raise NotImplementedError

    @property
    def ufunc_mode(cls):
        """
        str: The mode for ufunc compilation, either `"jit-lookup"`, `"jit-calculate"`, `"python-calculate"`.

        Examples
        --------
        .. ipython:: python

            galois.GF(2).ufunc_mode
            galois.GF(2**8).ufunc_mode
            galois.GF(31).ufunc_mode
            # galois.GF(7**5).ufunc_mode
        """
        return cls._ufunc_mode

    @property
    def ufunc_modes(cls):
        """
        list: All supported ufunc modes for this Galois field array class.

        Examples
        --------
        .. ipython:: python

            galois.GF(2).ufunc_modes
            galois.GF(2**8).ufunc_modes
            galois.GF(31).ufunc_modes
            galois.GF(2**100).ufunc_modes
        """
        if cls.dtypes == [np.object_]:
            return ["python-calculate"]
        else:
            return ["jit-lookup", "jit-calculate"]

    @property
    def default_ufunc_mode(cls):
        """
        str: The default ufunc arithmetic mode for this Galois field.

        Examples
        --------
        .. ipython:: python

            galois.GF(2).default_ufunc_mode
            galois.GF(2**8).default_ufunc_mode
            galois.GF(31).default_ufunc_mode
            galois.GF(2**100).default_ufunc_mode
        """
        if cls.dtypes == [np.object_]:
            return "python-calculate"
        elif cls.order <= 2**20:
            return "jit-lookup"
        else:
            return "jit-calculate"

    @property
    def ufunc_target(cls):
        """
        str: The numba target for the JIT-compiled ufuncs, either `"cpu"`, `"parallel"`, or `"cuda"`.

        Examples
        --------
        .. ipython:: python

            galois.GF(2).ufunc_target
            galois.GF(2**8).ufunc_target
            galois.GF(31).ufunc_target
            # galois.GF(7**5).ufunc_target
        """
        return cls._ufunc_target

    @property
    def ufunc_targets(cls):
        """
        list: All supported ufunc targets for this Galois field array class.

        Examples
        --------
        .. ipython:: python

            galois.GF(2).ufunc_targets
            galois.GF(2**8).ufunc_targets
            galois.GF(31).ufunc_targets
            galois.GF(2**100).ufunc_targets
        """
        if cls.dtypes == [np.object_]:
            return ["cpu"]
        else:
            return ["cpu", "parallel", "cuda"]

    @property
    def properties(cls):
        raise NotImplementedError


class GroupMetaBase(Meta):
    """
    A base class for the GroupMeta class. Included here so other functions can easily
    check whether a class is a finite group or other algebraic structure.
    """


class RingMetaBase(Meta):
    """
    A base class for the RingMeta class. Included here so other functions can easily
    check whether a class is a finite group or other algebraic structure.
    """


class FieldMetaBase(Meta):
    """
    A base class for the FieldMeta class. Included here so other functions can easily
    check whether a class is a finite field or other algebraic structure.
    """