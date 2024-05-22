import numpy as np
import cv2
from camera_coords_to_image_intrinsic import camera_coords_to_image_intrinsic
from astropy_to_camera_extrinsic import ground_homogenous_to_camera_extrinsic
from colorama import Fore, Style

# the reference frame of the "remapped" image is the camera coordinate basis
def compute_diffuse_shading_factor(image, poly_incident_angle_to_radius, principal_point, estimated_fov, im_height, im_width):
    print(f"{Fore.YELLOW}Computing global DIFFUSE shading factor...{Style.RESET_ALL}")

    ## create a photo
    azimuth_length = 1000
    zenith_length = 500
    estimated_fov = estimated_fov*np.pi/180     # convert to RADIANS

    ## so the created photo have around 500 corresponding to the estimated_fov
    ## so what would be the true length with we have 90 perfectly?
    true_90 = zenith_length/(1-np.cos(estimated_fov))

    # construct the array of index to iterate thru azimuth + zenith and the respective blank image
    horizontal_index = np.linspace(0, azimuth_length-1, azimuth_length, True, False, 'int')
    vertical_index = np.linspace(0, zenith_length-1, zenith_length, True, False, 'int')

    # each point on the conformal image has an equivalent azimuth and zenith
    azimuth_remapped = horizontal_index*2*np.pi/azimuth_length
    zenith_remapped = np.arccos(1-(vertical_index+1)/true_90)

    # create a meshgrid of coordinates. Note that the zenith section is in one mat zenith_mat and azimuth is in the other mat
    zenith_mat, azimuth_mat = np.meshgrid(zenith_remapped, azimuth_remapped, indexing='ij')

    # multiply those two mat to create the max of x_prime and y_prime
    x_prime = np.multiply(np.cos(azimuth_mat), np.tan(zenith_mat))
    y_prime = np.multiply(np.sin(azimuth_mat), np.tan(zenith_mat))

    # stack x_prime and y_prime to create a matrix of coordinate pairs. This could be used directly with intrinsic.camera_coords_to_image_intrinsic
    xy_coord_matrix = np.stack((x_prime,y_prime),axis=2)

    # this contains all the image coords of the remapped points
    equi_point = camera_coords_to_image_intrinsic(xy_coord_matrix.tolist(), poly_incident_angle_to_radius, principal_point)

    # create a blank canvas utilizing the azimuth_length and zenith_length values
    # the dtype=np.unit8 is important to make the imshow function understand how to plot the image.
    # this section is a bit confusing... OpenCV/Omnicalib convention is x to the right, y to the bottom, z into image
    # while accessing the image manually would have the first argument toward the bottom and second argument to the right
    # this means that the first component in the equi_point is actually the HORIZONTAL coordinates and the second component is the VERTICAL COORDINATES
    # so you need to check the [0] component with im_width and [1] with im_height
    # then the access is done as image[equi_point[ver][hor][1]][equi_point[ver][hor][0]]
    conformal_image = np.zeros((zenith_length, azimuth_length), dtype=np.uint8)

    for ver in vertical_index:
        for hor in horizontal_index:
            if equi_point[ver][hor][0] >= 0 and equi_point[ver][hor][0] < im_width and equi_point[ver][hor][1] >= 0 and equi_point[ver][hor][1] < im_height:
                    conformal_image[ver][hor] = image[equi_point[ver][hor][1]][equi_point[ver][hor][0]]

    # note that we use the true_90 instead of zenith length because this will maximize the shading factor
    diffuse_coeff = (azimuth_length*true_90 - cv2.sumElems(conformal_image)[0] / 255) / (azimuth_length*true_90)

    print(f'{Fore.GREEN}Diffuse shading factor is around ' + str(round(diffuse_coeff, 2)) + f'{Style.RESET_ALL}')
    return diffuse_coeff        # this essentially returns the diffuse component after compensated with shadings

def compute_diffuse_shading_factor_NASA(image, poly_incident_angle_to_radius, principal_point, estimated_fov, im_height, im_width, image_orientation, image_inclination, inclined_surface_orientation, inclined_surface_inclination):
    print(f"{Fore.YELLOW}Computing global DIFFUSE shading factor...{Style.RESET_ALL}")

    ## OK SO HERES THE PROBLEM: WE MUST ASSUME THAT THE USER TAKE THE PHOTO HORIZONTAL TO GROUND
    ## AND THE BOTTOM OF THE PHOTO POINTS SOUTH. SO EAST IS TO THE LEFT OF PHOTO

    # THIS SECTION TRANSFORM THE FISHEYE IMAGE INTO A CONFORMAL REMAPPED IMAGE
    ## create a photo
    azimuth_length = 1000
    zenith_length = 500
    estimated_fov = estimated_fov*np.pi/180     # convert to RADIANS

    ## so the created photo have around 500 corresponding to the estimated_fov
    ## so what would be the true length with we have 90 perfectly?
    true_90 = zenith_length/(1-np.cos(estimated_fov))

    # construct the array of index to iterate thru azimuth + zenith and the respective blank image
    horizontal_index = np.linspace(0, azimuth_length-1, azimuth_length, True, False, 'int')
    vertical_index = np.linspace(0, zenith_length-1, zenith_length, True, False, 'int')

    # each point on the conformal image has an equivalent azimuth and zenith
    azimuth_remapped = horizontal_index*2*np.pi/azimuth_length
    zenith_remapped = np.arccos(1-(vertical_index+1)/true_90)

    # create a meshgrid of coordinates. Note that the zenith section is in one mat zenith_mat and azimuth is in the other mat
    zenith_mat, azimuth_mat = np.meshgrid(zenith_remapped, azimuth_remapped, indexing='ij')

    # multiply those two mat to create the matrix of x_prime and y_prime
    x_prime = np.multiply(np.cos(azimuth_mat), np.tan(zenith_mat))
    y_prime = np.multiply(np.sin(azimuth_mat), np.tan(zenith_mat))

    # stack x_prime and y_prime to create a matrix of coordinate pairs. This could be used directly with intrinsic.camera_coords_to_image_intrinsic
    xy_coord_matrix = np.stack((x_prime,y_prime),axis=2)

    # this contains all the image coords of the remapped points
    equi_point = camera_coords_to_image_intrinsic(xy_coord_matrix.tolist(), poly_incident_angle_to_radius, principal_point)

    # create a blank canvas utilizing the azimuth_length and zenith_length values
    # the dtype=np.unit8 is important to make the imshow function understand how to plot the image.
    # this section is a bit confusing... OpenCV/Omnicalib convention is x to the right, y to the bottom, z into image
    # while accessing the image manually would have the first argument toward the bottom and second argument to the right
    # this means that the first component in the equi_point is actually the HORIZONTAL coordinates and the second component is the VERTICAL COORDINATES
    # so you need to check the [0] component with im_width and [1] with im_height
    # then the access is done as image[equi_point[ver][hor][1]][equi_point[ver][hor][0]]
    conformal_image = np.zeros((zenith_length, azimuth_length), dtype=np.uint8)

    for ver in vertical_index:
        for hor in horizontal_index:
            if equi_point[ver][hor][0] >= 0 and equi_point[ver][hor][0] < im_width and equi_point[ver][hor][1] >= 0 and equi_point[ver][hor][1] < im_height:
                    conformal_image[ver][hor] = image[equi_point[ver][hor][1]][equi_point[ver][hor][0]]

    cv2.imshow('conformal_image', conformal_image)
    # NOW EDIT THE CONFORMAL IMAGE VERSION TO REMOVE SECTION OF THE SKY THAT IS NOT VISIBLE BY THE SOLAR HARVESTING SURFACE
    # first step is to determine the normal vector N to the surface plane. This vector is described using the orientation and inclination of the solar harvesting surface
    conformal_image_plane_map = np.zeros((zenith_length, azimuth_length), dtype=np.uint8)

    # determine the x,y coordinate that describes the Cartesian normal vector of the solar harvesting plane in ground basis
    azimuth_panel = (inclined_surface_orientation) * np.pi / 180
    zenith_panel = (-inclined_surface_inclination) * np.pi / 180
    x_normal = np.sin(zenith_panel) * np.cos(azimuth_panel) / np.cos(zenith_panel)
    y_normal = np.sin(zenith_panel) * np.sin(azimuth_panel) / np.cos(zenith_panel)
    print(x_normal)
    print(y_normal)
    # then convert the set of x_normal, y_normal into the camera extrinsic coordiantes
    normal_coords_in_camera_extrinsic = ground_homogenous_to_camera_extrinsic([x_normal, y_normal], image_orientation, image_inclination)

    # we now obtain a Cartesian set of coords that describes the normal vector to the solar harvesting plane in camera coords
    x_normal_in_cam_coords = normal_coords_in_camera_extrinsic[0]
    y_normal_in_cam_coords = normal_coords_in_camera_extrinsic[1]
    print(x_normal_in_cam_coords)
    print(y_normal_in_cam_coords)

    # an explanation for this section
    # basically for a given normal vector [Nx, Ny, Nz] of a plane that points toward the "positive" side of that plane and a given point [X,Y,Z]
    # we could check if [X,Y,Z] belongs in this positive side by checking X*Nx + Y*Ny + Z*Nz > 0
    for ver in vertical_index:
        for hor in horizontal_index:
            # print(x_prime[ver][hor] * x_normal_in_cam_coords + y_prime[ver][hor] * y_normal_in_cam_coords + 1 * 1)
            if x_prime[ver][hor]*x_normal_in_cam_coords + y_prime[ver][hor]*y_normal_in_cam_coords + 1*1 > 0:
                conformal_image_plane_map[ver][hor] = 255

    cv2.imshow('conformal_image_2', conformal_image_plane_map)
    # by multiplying conformal image to conformal_image_plane_map, the pixels that are visible by the solar harvesting plane stays the same
    # while those that are not visible is set to 0
    # conformal_image = np.multiply(conformal_image, conformal_image_plane_map)

    # note that we use the true_90 instead of zenith length because this will maximize the shading factor
    diffuse_coeff = (azimuth_length*true_90 - cv2.sumElems(conformal_image)[0] / 255) / (azimuth_length*true_90)

    print(f'{Fore.GREEN}Diffuse shading factor is around ' + str(round(diffuse_coeff, 2)) + f'{Style.RESET_ALL}')
    return diffuse_coeff        # this essentially returns the diffuse component after compensated with shadings