import numpy as np

# this function calculate the homogeneous coordinates of the sun in the camera's frame of reference
# phi = zenith
# theta = azimuth
# omega = inclination
# psi = orientation
# PLEASE provide them in DEGREES
# astropy_coords = [phi, theta]
def astropy_to_camera_extrinsic (astropy_coords, psi, omega):
    # convert to radians
    theta = astropy_coords[0]*np.pi/180
    phi = astropy_coords[1] * np.pi / 180
    psi = psi*np.pi/180
    omega = omega*np.pi/180

    # first convert to spherical ground basis
    theta_ground = 3*np.pi/2 - theta
    phi_ground = phi

    # spherical in ground basis to rectangular in ground basis
    x = np.sin(phi_ground)*np.cos(theta_ground)/np.cos(phi_ground)
    y = np.sin(phi_ground)*np.sin(theta_ground)/np.cos(phi_ground)

    # ground basis to (x',y',z')
    x_prime = np.cos(psi)*x + np.sin(psi)*y
    y_prime = -np.sin(psi)*x + np.cos(psi)*y

    # (x',y',z') basis to camera basis, but we add 1 to the mix
    x_c = x_prime/(np.sin(omega)*y_prime + np.cos(omega))
    y_c = (np.cos(omega)*y_prime - np.sin(omega))/(np.sin(omega)*y_prime + np.cos(omega))

    return np.array([x_c,y_c]).T.tolist()

# this function transform a set of x,y ground homogenous coordinates to camera extrinsic coordinate
def ground_homogenous_to_camera_extrinsic (ground_coords, psi, omega):
    psi = psi * np.pi / 180
    omega = omega * np.pi / 180

    x = ground_coords[0]
    y = ground_coords[1]

    # ground basis to (x',y',z')
    x_prime = np.cos(psi) * x + np.sin(psi) * y
    y_prime = -np.sin(psi) * x + np.cos(psi) * y

    # (x',y',z') basis to camera basis, but we add 1 to the mix
    x_c = x_prime / (np.sin(omega) * y_prime + np.cos(omega))
    y_c = (np.cos(omega) * y_prime - np.sin(omega)) / (np.sin(omega) * y_prime + np.cos(omega))

    return np.array([x_c, y_c]).T.tolist()
