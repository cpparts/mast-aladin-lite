from astropy.coordinates import SkyCoord, Angle
import astropy.units as u
from astropy.tests.helper import assert_quantity_allclose


def assert_coordinate_close(coord1, coord2, atol=1 * u.arcsec):
    # check that two coordinates are within some separation tolerance
    separation = coord1.separation(coord2)
    assert_quantity_allclose(separation, desired=0*u.arcsec, atol=atol)


def assert_angle_close(angle1, angle2, atol=1 * u.arcsec):
    # check that two angles are within some separation tolerance
    difference = abs(angle1 - angle2)
    assert_quantity_allclose(difference, desired=0*u.arcsec, atol=atol)


def test_mast_aladin_has_aid(MastAladin_app):
    assert callable(getattr(MastAladin_app, 'set_viewport', None))


def test_mast_aladin_aid_set_viewport(MastAladin_app):
    # check that the default center coordinate is (0, 0) deg, the default
    # fov is 60 deg, and the default rotation angle is 0 deg before
    # we test the setter. Set fov_xy to be able to check manipulations:
    initial_fov_xy = {
        'x': Angle(60, unit='deg'),
        'y': Angle(40, unit='deg'),
    }
    MastAladin_app._fov_xy = {
        'x': 60,
        'y': 40,
    }
    default_center = SkyCoord(0, 0, unit='deg')
    default_rotation = Angle(0, unit='deg')
    assert_coordinate_close(MastAladin_app.target, default_center)
    assert_angle_close(MastAladin_app.rotation, default_rotation)
    assert_angle_close(MastAladin_app.fov, initial_fov_xy["x"])

    # test the setter for center and rotation
    target_coords = SkyCoord(45, 45, unit='deg')
    target_rotation = Angle(45, unit='deg')
    target_fov = {
        'x': Angle(45, unit='deg'),
        'y': Angle(30, unit='deg'),
    }
    MastAladin_app.set_viewport(
        center=target_coords,
        fov=target_fov["y"],
        rotation=target_rotation,
    )

    assert_coordinate_close(MastAladin_app.target, target_coords)
    assert_angle_close(MastAladin_app.rotation, target_rotation)
    assert_angle_close(MastAladin_app.fov, target_fov["x"])


"""
def test_mast_aladin_aid_get_viewport(MastAladin_app):
    # check that the default center coordinate is (0, 0) deg,
    # the default fov is 60.0 deg, and the image_label is None
    default_center = SkyCoord(0, 0, unit='deg')
    default_viewport = MastAladin_app.get_viewport()
    assert_coordinate_close(default_viewport["center"], default_center)
    assert_angle_close(Angle(60, u.deg), default_viewport["fov"])
    assert default_viewport["image_label"] is None


def test_mast_aladin_aid_get_and_set_viewport_roundtrip(MastAladin_app):
    # check that performing a round trip of getting and setting the
    # viewport results in the original state

    # get default settings
    default_viewport = MastAladin_app.get_viewport()

    # change viewport settings
    target_coords = SkyCoord(45, 45, unit='deg')
    target_rotation = Angle(45, unit='deg')
    MastAladin_app.set_viewport(center=target_coords, rotation=target_rotation)

    # check new viewport settings
    midpoint_viewport = MastAladin_app.get_viewport()
    assert_coordinate_close(midpoint_viewport["center"], target_coords)
    assert_angle_close(midpoint_viewport["rotation"], target_rotation)
    assert_angle_close(midpoint_viewport["fov"], Angle(60, u.deg))
    assert midpoint_viewport["image_label"] is None

    # change viewport settings back to default
    MastAladin_app.set_viewport(
        center=default_viewport["center"],
        rotation=default_viewport["rotation"]
    )

    # check final viewport settings
    final_viewport = MastAladin_app.get_viewport()
    assert_coordinate_close(final_viewport["center"], default_viewport["center"])
    assert_angle_close(final_viewport["rotation"], default_viewport["rotation"])
    assert_angle_close(final_viewport["fov"], default_viewport["fov"])
    assert final_viewport["image_label"] is None
"""
