from sympy.vector.coordsysrect import CoordSysCartesian
from sympy.vector.dyadic import Dyadic
from sympy.vector.vector import Vector, BaseVector
from sympy.vector.scalar import BaseScalar
from sympy import sympify, diff, integrate, S, simplify


def express(expr, system, system2=None, variables=False):
    """
    Global function for 'express' functionality.

    Re-expresses a Vector, Dyadic or scalar(sympyfiable) in the given
    coordinate system.

    If 'variables' is True, then the coordinate variables (base scalars)
    of other coordinate systems present in the vector/scalar field or
    dyadic are also substituted in terms of the base scalars of the
    given system.

    Parameters
    ==========

    expr : Vector/Dyadic/scalar(sympyfiable)
        The expression to re-express in CoordSysCartesian 'system'

    system: CoordSysCartesian
        The coordinate system the expr is to be expressed in

    system2: CoordSysCartesian
        The other coordinate system required for re-expression
        (only for a Dyadic Expr)

    variables : boolean
        Specifies whether to substitute the coordinate variables present
        in expr, in terms of those of parameter system

    Examples
    ========

    >>> from sympy.vector import CoordSysCartesian
    >>> from sympy import Symbol, cos, sin
    >>> N = CoordSysCartesian('N')
    >>> q = Symbol('q')
    >>> B = N.orient_new_axis('B', q, N.k)
    >>> from sympy.vector import express
    >>> express(B.i, N)
    (cos(q))*N.i + (sin(q))*N.j
    >>> express(N.x, B, variables=True)
    -sin(q)*B.y + cos(q)*B.x
    >>> d = N.i.outer(N.i)
    >>> express(d, B, N) == (cos(q))*(B.i|N.i) + (-sin(q))*(B.j|N.i)
    True

    """

    if expr == 0 or expr == Vector.zero:
        return expr

    if not isinstance(system, CoordSysCartesian):
        raise TypeError("system should be a CoordSysCartesian \
                        instance")

    if isinstance(expr, Vector):
        if system2 is not None:
            raise ValueError("system2 should not be provided for \
                                Vectors")
        # Given expr is a Vector
        if variables:
            # If variables attribute is True, substitute
            # the coordinate variables in the Vector
            system_list = []
            for x in expr.atoms(BaseScalar, BaseVector):
                if x.system != system:
                    system_list.append(x.system)
            system_list = set(system_list)
            subs_dict = {}
            for f in system_list:
                subs_dict.update(f.scalar_map(system))
            expr = expr.subs(subs_dict)
        # Re-express in this coordinate system
        outvec = Vector.zero
        parts = expr.separate()
        for x in parts:
            if x != system:
                temp = system.rotation_matrix(x) * parts[x].to_matrix(x)
                outvec += matrix_to_vector(temp, system)
            else:
                outvec += parts[x]
        return outvec

    elif isinstance(expr, Dyadic):
        if system2 is None:
            system2 = system
        if not isinstance(system2, CoordSysCartesian):
            raise TypeError("system2 should be a CoordSysCartesian \
                            instance")
        outdyad = Dyadic.zero
        var = variables
        for k, v in expr.components.items():
            outdyad += (express(v, system, variables=var) *
                        (express(k.args[0], system, variables=var) |
                         express(k.args[1], system2, variables=var)))

        return outdyad

    else:
        if system2 is not None:
            raise ValueError("system2 should not be provided for \
                                Vectors")
        if variables:
            # Given expr is a scalar field
            system_set = set([])
            expr = sympify(expr)
            # Subsitute all the coordinate variables
            for x in expr.atoms(BaseScalar):
                if x.system != system:
                    system_set.add(x.system)
            subs_dict = {}
            for f in system_set:
                subs_dict.update(f.scalar_map(system))
            return expr.subs(subs_dict)
        return expr


def curl(vect, coord_sys):
    """
    Returns the curl of a vector field computed wrt the base scalars
    of the given coordinate system.

    Parameters
    ==========

    vect : Vector
        The vector operand

    coord_sys : CoordSysCartesian
        The coordinate system to calculate the curl in

    Examples
    ========

    >>> from sympy.vector import CoordSysCartesian, curl
    >>> R = CoordSysCartesian('R')
    >>> v1 = R.y*R.z*R.i + R.x*R.z*R.j + R.x*R.y*R.k
    >>> curl(v1, R)
    0
    >>> v2 = R.x*R.y*R.z*R.i
    >>> curl(v2, R)
    R.x*R.y*R.j + (-R.x*R.z)*R.k

    """

    return coord_sys.delop.cross(vect).doit()


def divergence(vect, coord_sys):
    """
    Returns the divergence of a vector field computed wrt the base
    scalars of the given coordinate system.

    Parameters
    ==========

    vect : Vector
        The vector operand

    coord_sys : CoordSysCartesian
        The cooordinate system to calculate the divergence in

    Examples
    ========

    >>> from sympy.vector import CoordSysCartesian, divergence
    >>> R = CoordSysCartesian('R')
    >>> v1 = R.x*R.y*R.z * (R.i+R.j+R.k)
    >>> divergence(v1, R)
    R.x*R.y + R.x*R.z + R.y*R.z
    >>> v2 = 2*R.y*R.z*R.j
    >>> divergence(v2, R)
    2*R.z

    """

    return coord_sys.delop.dot(vect).doit()


def gradient(scalar, coord_sys):
    """
    Returns the vector gradient of a scalar field computed wrt the
    base scalars of the given coordinate system.

    Parameters
    ==========

    scalar : SymPy Expr
        The scalar field to compute the gradient of

    coord_sys : CoordSysCartesian
        The coordinate system to calculate the gradient in

    Examples
    ========

    >>> from sympy.vector import CoordSysCartesian, gradient
    >>> R = CoordSysCartesian('R')
    >>> s1 = R.x*R.y*R.z
    >>> gradient(s1, R)
    R.y*R.z*R.i + R.x*R.z*R.j + R.x*R.y*R.k
    >>> s2 = 5*R.x**2*R.z
    >>> gradient(s2, R)
    10*R.x*R.z*R.i + 5*R.x**2*R.k

    """

    return coord_sys.delop(scalar).doit()

def directional_derivative(scalar, vect):
    """
    Returns the directional derivative of a scalar field computed along a given vector
    in given coordinate system.

    Parameters
    ==========

    scalar : SymPy Expr
        The scalar field to compute the gradient of

    vect : Vector
        The vector operand

    coord_sys : CoordSysCartesian
        The coordinate system to calculate the gradient in

    Examples
    ========

    >>> from sympy.vector import CoordSysCartesian, directional_derivative
    >>> R = CoordSysCartesian('R')
    >>> f1 = R.x*R.y*R.z
    >>> v1 = 3*R.i + 4*R.j + R.k
    >>> directional_derivative(f1, v1)
    R.x*R.y + 4*R.x*R.z + 3*R.y*R.z
    >>> f2 = 5*R.x**2*R.z
    >>> directional_derivative(f2, v1)
    5*R.x**2 + 30*R.x*R.z

    """
    coord_sys = vect._sys
    return gradient(scalar, coord_sys).dot(vect).doit()

def is_conservative(field):
    """
    Checks if a field is conservative.

    Paramaters
    ==========

    field : Vector
        The field to check for conservative property

    Examples
    ========

    >>> from sympy.vector import CoordSysCartesian
    >>> from sympy.vector import is_conservative
    >>> R = CoordSysCartesian('R')
    >>> is_conservative(R.y*R.z*R.i + R.x*R.z*R.j + R.x*R.y*R.k)
    True
    >>> is_conservative(R.z*R.j)
    False

    """

    # Field is conservative irrespective of system
    # Take the first coordinate system in the result of the
    # separate method of Vector
    if not isinstance(field, Vector):
        raise TypeError("field should be a Vector")
    if field == Vector.zero:
        return True
    coord_sys = list(field.separate())[0]
    return curl(field, coord_sys).simplify() == Vector.zero


def is_solenoidal(field):
    """
    Checks if a field is solenoidal.

    Paramaters
    ==========

    field : Vector
        The field to check for solenoidal property

    Examples
    ========

    >>> from sympy.vector import CoordSysCartesian
    >>> from sympy.vector import is_solenoidal
    >>> R = CoordSysCartesian('R')
    >>> is_solenoidal(R.y*R.z*R.i + R.x*R.z*R.j + R.x*R.y*R.k)
    True
    >>> is_solenoidal(R.y * R.j)
    False

    """

    # Field is solenoidal irrespective of system
    # Take the first coordinate system in the result of the
    # separate method in Vector
    if not isinstance(field, Vector):
        raise TypeError("field should be a Vector")
    if field == Vector.zero:
        return True
    coord_sys = list(field.separate())[0]
    return divergence(field, coord_sys).simplify() == S(0)


def scalar_potential(field, coord_sys):
    """
    Returns the scalar potential function of a field in a given
    coordinate system (without the added integration constant).

    Parameters
    ==========

    field : Vector
        The vector field whose scalar potential function is to be
        calculated

    coord_sys : CoordSysCartesian
        The coordinate system to do the calculation in

    Examples
    ========

    >>> from sympy.vector import CoordSysCartesian
    >>> from sympy.vector import scalar_potential, gradient
    >>> R = CoordSysCartesian('R')
    >>> scalar_potential(R.k, R) == R.z
    True
    >>> scalar_field = 2*R.x**2*R.y*R.z
    >>> grad_field = gradient(scalar_field, R)
    >>> scalar_potential(grad_field, R)
    2*R.x**2*R.y*R.z

    """

    # Check whether field is conservative
    if not is_conservative(field):
        raise ValueError("Field is not conservative")
    if field == Vector.zero:
        return S(0)
    # Express the field exntirely in coord_sys
    # Subsitute coordinate variables also
    if not isinstance(coord_sys, CoordSysCartesian):
        raise TypeError("coord_sys must be a CoordSysCartesian")
    field = express(field, coord_sys, variables=True)
    dimensions = coord_sys.base_vectors()
    scalars = coord_sys.base_scalars()
    # Calculate scalar potential function
    temp_function = integrate(field.dot(dimensions[0]), scalars[0])
    for i, dim in enumerate(dimensions[1:]):
        partial_diff = diff(temp_function, scalars[i + 1])
        partial_diff = field.dot(dim) - partial_diff
        temp_function += integrate(partial_diff, scalars[i + 1])
    return temp_function


def scalar_potential_difference(field, coord_sys, point1, point2):
    """
    Returns the scalar potential difference between two points in a
    certain coordinate system, wrt a given field.

    If a scalar field is provided, its values at the two points are
    considered. If a conservative vector field is provided, the values
    of its scalar potential function at the two points are used.

    Returns (potential at point2) - (potential at point1)

    The position vectors of the two Points are calculated wrt the
    origin of the coordinate system provided.

    Parameters
    ==========

    field : Vector/Expr
        The field to calculate wrt

    coord_sys : CoordSysCartesian
        The coordinate system to do the calculations in

    point1 : Point
        The initial Point in given coordinate system

    position2 : Point
        The second Point in the given coordinate system

    Examples
    ========

    >>> from sympy.vector import CoordSysCartesian, Point
    >>> from sympy.vector import scalar_potential_difference
    >>> R = CoordSysCartesian('R')
    >>> P = R.origin.locate_new('P', R.x*R.i + R.y*R.j + R.z*R.k)
    >>> vectfield = 4*R.x*R.y*R.i + 2*R.x**2*R.j
    >>> scalar_potential_difference(vectfield, R, R.origin, P)
    2*R.x**2*R.y
    >>> Q = R.origin.locate_new('O', 3*R.i + R.j + 2*R.k)
    >>> scalar_potential_difference(vectfield, R, P, Q)
    -2*R.x**2*R.y + 18

    """

    if not isinstance(coord_sys, CoordSysCartesian):
        raise TypeError("coord_sys must be a CoordSysCartesian")
    if isinstance(field, Vector):
        # Get the scalar potential function
        scalar_fn = scalar_potential(field, coord_sys)
    else:
        # Field is a scalar
        scalar_fn = field
    # Express positions in required coordinate system
    origin = coord_sys.origin
    position1 = express(point1.position_wrt(origin), coord_sys,
                        variables=True)
    position2 = express(point2.position_wrt(origin), coord_sys,
                        variables=True)
    # Get the two positions as substitution dicts for coordinate variables
    subs_dict1 = {}
    subs_dict2 = {}
    scalars = coord_sys.base_scalars()
    for i, x in enumerate(coord_sys.base_vectors()):
        subs_dict1[scalars[i]] = x.dot(position1)
        subs_dict2[scalars[i]] = x.dot(position2)
    return scalar_fn.subs(subs_dict2) - scalar_fn.subs(subs_dict1)


def matrix_to_vector(matrix, system):
    """
    Converts a vector in matrix form to a Vector instance.

    It is assumed that the elements of the Matrix represent the
    measure numbers of the components of the vector along basis
    vectors of 'system'.

    Parameters
    ==========

    matrix : SymPy Matrix, Dimensions: (3, 1)
        The matrix to be converted to a vector

    system : CoordSysCartesian
        The coordinate system the vector is to be defined in

    Examples
    ========

    >>> from sympy import ImmutableMatrix as Matrix
    >>> m = Matrix([1, 2, 3])
    >>> from sympy.vector import CoordSysCartesian, matrix_to_vector
    >>> C = CoordSysCartesian('C')
    >>> v = matrix_to_vector(m, C)
    >>> v
    C.i + 2*C.j + 3*C.k
    >>> v.to_matrix(C) == m
    True

    """

    outvec = Vector.zero
    vects = system.base_vectors()
    for i, x in enumerate(matrix):
        outvec += x * vects[i]
    return outvec


def _path(from_object, to_object):
    """
    Calculates the 'path' of objects starting from 'from_object'
    to 'to_object', along with the index of the first common
    ancestor in the tree.

    Returns (index, list) tuple.
    """

    if from_object._root != to_object._root:
        raise ValueError("No connecting path found between " +
                         str(from_object) + " and " + str(to_object))

    other_path = []
    obj = to_object
    while obj._parent is not None:
        other_path.append(obj)
        obj = obj._parent
    other_path.append(obj)
    object_set = set(other_path)
    from_path = []
    obj = from_object
    while obj not in object_set:
        from_path.append(obj)
        obj = obj._parent
    index = len(from_path)
    i = other_path.index(obj)
    while i >= 0:
        from_path.append(other_path[i])
        i -= 1
    return index, from_path


def orthogonalize(*vlist, **kwargs):
    """
    Takes a sequence of independent vectors and orthogonalizes them
    using the Gram - Schmidt process. Returns a list of
    orthogonal or orthonormal vectors.

    Parameters
    ==========

    vlist : sequence of independent vectors to be made orthogonal.

    orthonormal : Optional parameter
                  Set to True if the the vectors returned should be
                  orthonormal.
                  Default: False

    Examples
    ========

    >>> from sympy.vector.coordsysrect import CoordSysCartesian
    >>> from sympy.vector.vector import Vector, BaseVector
    >>> from sympy.vector.functions import orthogonalize
    >>> C = CoordSysCartesian('C')
    >>> i, j, k = C.base_vectors()
    >>> v1 = i + 2*j
    >>> v2 = 2*i + 3*j
    >>> orthogonalize(v1, v2)
    [C.i + 2*C.j, 2/5*C.i + (-1/5)*C.j]

    References
    ==========

    .. [1] https://en.wikipedia.org/wiki/Gram-Schmidt_process

    """
    orthonormal = kwargs.get('orthonormal', False)

    if not all(isinstance(vec, Vector) for vec in vlist):
        raise TypeError('Each element must be of Type Vector')

    ortho_vlist = []
    for i, term in enumerate(vlist):
        for j in range(i):
            term -= ortho_vlist[j].projection(vlist[i])
        # TODO : The following line introduces a performance issue
        # and needs to be changed once a good solution for issue #10279 is
        # found.
        if simplify(term).equals(Vector.zero):
            raise ValueError("Vector set not linearly independent")
        ortho_vlist.append(term)

    if orthonormal:
        ortho_vlist = [vec.normalize() for vec in ortho_vlist]

    return ortho_vlist
