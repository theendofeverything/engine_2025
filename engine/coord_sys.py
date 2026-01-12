"""CoordinateSystem is a helper struct to organize Game attributes for the coordinate systems.

There are two coordinate systems:
    PCS: Pixel Coordinate System
    GCS: Game Coordinate System
"""
from __future__ import annotations
from dataclasses import dataclass, field
from .geometry_types import Vec2D, Point2D
from .geometry_operators import Matrix2DH
from .panning import Panning


@dataclass
class CoordinateSystemScalingFactors:
    """Private class to namespace scaled factors used by CoordinateSystem.

    Properties (read-only attributes calculated on-demand):
        gcs_to_pcs (float):
            Scaling factor to transform from units of GCS to PCS.
            The scale is based on the visible width of the GCS at this zoom level
        pcs_to_gcs (float):
            Scaling factor to transform from units of PCS to GCS.
            This is the inverse of scale_gcs_to_pcs.

    >>> coord_sys = CoordinateSystem(window_size=Vec2D(16, 9), panning=Panning())
    >>> coord_sys.scaling.gcs_to_pcs
    8.0
    >>> coord_sys.scaling.pcs_to_gcs
    0.125
    """
    coord_sys: CoordinateSystem

    @property
    def gcs_to_pcs(self) -> float:
        """Scaling factor to convert from units of GCS to PCS."""
        return self.coord_sys.window_size.x/self.coord_sys.gcs_width

    @property
    def pcs_to_gcs(self) -> float:
        """Scaling factor to convert from units of PCS to GCS."""
        return 1/(self.gcs_to_pcs)


@dataclass
class CoordinateSystemMatrices:
    """Namespace matrices used by CoordinateSystem.

    Properties (read-only attributes calculated on-demand):
        gcs_to_pcs (Matrix2DH):
            Matrix that transforms from GCS to PCS.
            Intended usage:
                mouse_p = coord_sys.xfm(
                            mouse_g,
                            coord_sys.matrix.gcs_to_pcs
                            )
        pcs_to_gcs (Matrix2DH):
            Matrix that transforms from GCS to PCS.
            Intended usage:
                mouse_g = coord_sys.xfm(
                            mouse_p.as_vec(),
                            coord_sys.matrix.pcs_to_gcs
                            )

    >>> coord_sys = CoordinateSystem(window_size=Vec2D(16, 9), panning=Panning())

    The matrix uses column vectors.
    The affine transformation matrix is the top-left 2x2.
    The 2x2 is augmented to a 3x3 for using homogeneous coordinates to perform translation.

    GCS to PCS
    >>> print(coord_sys.matrix.gcs_to_pcs)
    |    8.0       0      8.0|
    |      0    -8.0      4.5|
    |      0       0        1|

    PCS to GCS
    >>> print(coord_sys.matrix.pcs_to_gcs)
    |  0.125     0.0     -1.0|
    |    0.0   -0.125  0.5625|
    |      0       0        1|
    """
    coord_sys: CoordinateSystem

    @property
    def gcs_to_pcs(self) -> Matrix2DH:
        """Matrix that transforms from GCS to PCS."""
        k = self.coord_sys.scaling.gcs_to_pcs
        return Matrix2DH(m11=k, m12=0, m21=0, m22=-k, translation=self.coord_sys.translation)

    @property
    def pcs_to_gcs(self) -> Matrix2DH:
        """Matrix that transforms from PCS to GCS."""
        return self.gcs_to_pcs.inv


@dataclass
class CoordinateSystem:
    """Game attributes for the coordinate systems.

    >>> coord_sys = CoordinateSystem(window_size=Vec2D(20*16, 20*9), panning=Panning())
    >>> print(coord_sys)
    CoordinateSystem(window_size=Vec2D(x=320, y=180),
                     panning=Panning(start=Point2D(x=0, y=0),
                        end=Point2D(x=0, y=0),
                        is_active=False),
                     gcs_width=2,
                     pcs_origin=Point2D(x=160.0, y=90.0),
                     scaling=CoordinateSystemScalingFactors(coord_sys=...),
                     matrix=CoordinateSystemMatrices(coord_sys=...))

    API (TODO: finish writing this section)

    xfm(Vec2D, Matrix2DH) -> Vec2D:
        Transform vector between coordinate systems using a Matrix2DH from
        CoordinateSystemMatrices.
        >>> coord_sys = CoordinateSystem(window_size=Vec2D(20*16, 20*9), panning=Panning())
        >>> coord_sys.xfm(Vec2D(20*16, 20*9), coord_sys.matrix.pcs_to_gcs)
        Vec2D(x=1.0, y=-0.5625)

        See xfm() docstring for explanation and more examples.

    Attributes:
        window_size (Vec2D):
            The size of the OS window in pixels.
        panning (Panning):
            Track the panning state. See Panning.
        gcs_width (float):
            The visible width of the game in the game coordinate system.
        pcs_origin (Point2D):
            The game coordinate system origin in pixel coordinates.
            The pcs_origin is updated in:
                UI.handle_windowsizechanged_events() -- when user resizes the window
                UI._zoom() -- when user zooms in or out
                UI.handle_mousebutton_up_events() -- when user releases mouse button to stop panning


    >>> for name, attr in CoordinateSystem.__dict__.items():
    ...     if isinstance(attr, property):
    ...         print(f"{name}")
    window_center
    translation

    Properties (read-only attributes calculated on-demand):
        window_center (Point2D):
            Center of the window in pixel coordinates.
        translation (Vec2D):
            This is a vector in pixel coordinates from the topleft of the window to the game origin,
            i.e., this translation vector describes the origin offset.
            The name 'translation' refers to how it is used in the CoordinateTransform.
            Mouse panning is included in the origin offset when calculating 'translation'.
    """
    window_size: Vec2D                                  # Track window size
    panning:     Panning  # Track UI panning: in game __post_init__() do 'panning=self.ui.panning'
    gcs_width:   float = 2                              # Initial value GCS -1:1 fills screen width

    # Instance variables defined in __post_init__()
    pcs_origin:  Point2D = field(init=False)            # Game origin in PCS
    scaling:     CoordinateSystemScalingFactors = field(init=False)  # CS unit cell scaling factors
    matrix:      CoordinateSystemMatrices = field(init=False)  # CS xfm matrices

    def __post_init__(self) -> None:
        self.pcs_origin = self.window_center            # Origin is initially the window center
        self.scaling = CoordinateSystemScalingFactors(self)  # Coord sys unit cell scaling factors
        self.matrix = CoordinateSystemMatrices(self)    # Coord sys xfm matrices

    @property
    def window_center(self) -> Point2D:
        """The center of the window in pixel coordinates."""
        return Point2D(self.window_size.x/2, self.window_size.y/2)

    @property
    def translation(self) -> Vec2D:
        """The translation vector describing the origin offset relative to the window (0,0).

        Dependency chain showing how translation is used and how it is affected by panning:
            renderer <-- coord_sys.matrix.gcs_to_pcs <-- coord_sys.translation <-- panning.vector
            In the above dependency chain:
                - read "<--" as "thing-on-left uses thing-on-right"
                - panning.vector = panning.end - panning.start
        """
        return Vec2D(x=self.pcs_origin.x + self.panning.vector.x,
                     y=self.pcs_origin.y + self.panning.vector.y)

    @staticmethod
    def xfm(v: Vec2D, mat: Matrix2DH) -> Vec2D:
        """Xfm 'v' to a new coordinate system by matrix multiplication of 'v' and 'mat'.

        Multiply column-vector matrix 'mat' by column vector 'v' in homogeneous coordinates.

        v:
            |x|
            |y|

        v in homogeneous-coordinates:
            |x|
            |y|
            |1|

        mat:
            The xfm matrix is 2x2, augmented with a translation vector to become a 3x3:

                mat = |m11  m12  Tx|
                      |m21  m22  Ty|
                      |  0    0   1|

                where |Tx Ty| is the vector that translates the origin between coordinate systems

            Since we are working with column vectors, note that the unit vectors of the 2x2: (a,b)
            and (c,d), must be the columns (not the rows):

                mat = |a   c  Tx|
                      |b   d  Ty|
                      |0   0   1|

        Matrix multiplication:

            |a   c  Tx|   |x|   |ax + cy + Tx|   |m11*x + m12*y + Tx|
            |b   d  Ty| * |y| = |bx + dy + Ty| = |m21*x + m22*y + Ty|
            |0   0   1|   |1|   | 0 +  0 +  1| = |    0 +     0 +  1|

        We only needed homogeneous coordinates to include translation in the transform.
        Return just the 2D vector (discarding the third element, 1):

            |m11*x + m12*y + Tx|
            |m21*x + m22*y + Ty|

        Examples
        --------

        Transform this vector in the following examples:
        >>> v = Vec2D(x=1, y=1)
        >>> v
        Vec2D(x=1, y=1)

        Note: these examples move the origin after initializing the coordinate system.
        The default behavior (and the intended usage) is to put the origin at the center of the
        window. If I want to default to other behavior (or have some choice), I should add an
        optional instance attribute that sets the default origin (e.g., topleft, bottomleft, center,
        etc.)

        Example 1: Leave the origin where it is and just scale.
        >>> xfm = Matrix2DH(m11=5, m12=0, m21=0, m22=-5, translation=Vec2D(x=0, y=0))
        >>> print(xfm)
        |    5     0      0|
        |    0    -5      0|
        |    0     0      1|

        Dummy coordinate system:
        >>> coord_sys = CoordinateSystem(window_size=Vec2D(0, 0), panning=Panning())
        >>> coord_sys.xfm(v, xfm)
        Vec2D(x=5, y=-5)

        Example 1A: Redo example 1 using the GCS to PCS matrix calculated by CoordinateSystem.
        >>> coord_sys = CoordinateSystem(window_size=Vec2D(16, 9), panning=Panning())
        >>> coord_sys.pcs_origin = Point2D(0, 0) # Put origin at topleft to eliminate translation
        >>> print(coord_sys.matrix.gcs_to_pcs)
        |  8.0     0      0|
        |    0  -8.0      0|
        |    0     0      1|

        >>> coord_sys.xfm(v, coord_sys.matrix.gcs_to_pcs)
        Vec2D(x=8.0, y=-8.0)

        Example 2: Now just translate the origin and don't change anything else.
        >>> xfm = Matrix2DH(m11=1, m12=0, m21=0, m22=1, translation=Vec2D(x=2, y=3))
        >>> print(xfm)
        |    1     0      2|
        |    0     1      3|
        |    0     0      1|

        Dummy coordinate system
        >>> coord_sys = CoordinateSystem(window_size=Vec2D(0, 0), panning=Panning())
        >>> coord_sys.xfm(v, xfm)
        Vec2D(x=3, y=4)

        Example 2A: Redo example 2 using the GCS to PCS matrix calculated by CoordinateSystem.
        Note:
            I use a window size of 2x2 because this is the initial size of the GCS visible in the
            window: -1.0:1.0 in both the x and y dimensions. By matching the window size to the
            visible portion of the GCS, the scaling factor is 1.
        Note:
            The vector is different from Example 2 because matrix.gcs_to_pcs flips the y-axis
            direction.
        >>> coord_sys = CoordinateSystem(window_size=Vec2D(2, 2), panning=Panning())
        >>> coord_sys.pcs_origin = Point2D(2, 3) # Put origin at 2,3 to show translation
        >>> print(coord_sys.matrix.gcs_to_pcs)
        |  1.0     0      2|
        |    0  -1.0      3|
        |    0     0      1|
        >>> coord_sys.xfm(v, coord_sys.matrix.gcs_to_pcs)
        Vec2D(x=3.0, y=2.0)

        Example 3: Scale and translate.
        >>> xfm = Matrix2DH(m11=5, m12=0, m21=0, m22=-5, translation=Vec2D(x=2, y=3))
        >>> print(xfm)
        |    5     0      2|
        |    0    -5      3|
        |    0     0      1|

        Dummy coordinate system
        >>> coord_sys = CoordinateSystem(window_size=Vec2D(0, 0), panning=Panning())
        >>> coord_sys.xfm(v, xfm)
        Vec2D(x=7, y=-2)

        Example 3A: Redo example 3 using the GCS to PCS matrix calculated by CoordinateSystem.
        >>> coord_sys = CoordinateSystem(window_size=Vec2D(16, 9), panning=Panning())
        >>> print(coord_sys.matrix.gcs_to_pcs)
        |  8.0     0    8.0|
        |    0  -8.0    4.5|
        |    0     0      1|

        >>> coord_sys.xfm(v, coord_sys.matrix.gcs_to_pcs)
        Vec2D(x=16.0, y=-3.5)
        """
        # Matrix multiply 'mat' by 'v' using homogeneous coordinates.
        return mat.multiply_vec(v)
