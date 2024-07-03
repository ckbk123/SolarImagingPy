from os.path import join as opj
import mmcv
import cv2
import numpy as np
from mmseg.apis import init_model, inference_model, show_result_pyplot
from sky_detection.src.crop_around_disk import estimate_radius, crop_around_disk

data_dir = "./DebugData"
pprad_path = opj(data_dir, "pprad.yml")
img_cropped_path = opj(data_dir, "img_cropped.jpg")
output_path = opj(data_dir, "output.jpg")

config_path = opj("./sky_detection/src/unet-s5-d16_fcn_4xb4-160k_cityscapes-512x1024.py")
checkpoint_path = opj("./sky_detection/src/model.pth")


def inference(calibration_path, img_path):
    """
    Args:
    - calibration_path: path of output of fisheye_to_equirectangular_v3/import_camera_intrinsic_function.py
    - img_path: path of the input image
    Returns:
    - a torch tensor of shape (1, H, W)
    """
    
    # Initiate the model
    model = init_model(config_path, checkpoint_path, 'cpu')

    # Crop the image
    estimate_radius(calibration_path)
    img = mmcv.imread(img_path)
    img_cropped, cropped_section = crop_around_disk(pprad_path, img)
    mmcv.image.imwrite(img_cropped, img_cropped_path)
    print(cropped_section)

    # Run inference
    result = inference_model(model, img_cropped_path)
    result = result.pred_sem_seg.data[0].numpy()

    # Create a visual representation and save it
    image_to_convert = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    im_height, im_width = image_to_convert.shape

    # the work is done on a cropped image... => so we need to plot the mask back onto the fullscale image
    full_size_mask = np.zeros((im_height, im_width), dtype=np.uint8)
    full_size_mask[cropped_section[2]:cropped_section[3]+1,cropped_section[0]:cropped_section[1]+1] = result

    return full_size_mask
