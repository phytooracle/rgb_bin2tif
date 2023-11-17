#!/usr/bin/env python3
"""
Author : Emmanuel Gonzalez, Jeffrey Demieville
References: AgPipeline, TERRA-REF
Date   : 2020-09-11
Purpose: Convert raw BIN files to geoTIFFs
"""

import argparse
import os
import sys
import json
import numpy as np
from terrautils.spatial import scanalyzer_to_latlon
from terrautils.formats import create_geotiff
from osgeo import gdal, osr
from scipy.ndimage.filters import convolve


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='BIN to geoTIFF',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('bin',
                        metavar='BIN file',
                        help='Raw BIN file to process')

    parser.add_argument('-o',
                        '--outdir',
                        help='Output directory',
                        metavar='outdir',
                        type=str,
                        default='bin2tif_out')

    parser.add_argument('-m',
                        '--metadata',
                        help='Metadata file associated with bin file',
                        metavar='metadata',
                        type=str,
                        required=True)

    parser.add_argument('-z',
                        '--zoffset',
                        help='Z-axis offset',
                        metavar='z-offset',
                        type=float,
                        required=True)

    return parser.parse_args()


# --------------------------------------------------
def demosaic(im):
    """Demosaic the BayerGR8 image.
    Arguments:
      im (numpy array): BayerGR8 image with shape (height, width)
    Returns:
      (numpy array): RGB image with shape (height, width)
    """

    # Assuming GBRG ordering.
    B = np.zeros_like(im)
    R = np.zeros_like(im)
    G = np.zeros_like(im)
    R[0::2, 1::2] = im[0::2, 1::2]
    B[1::2, 0::2] = im[1::2, 0::2]
    G[0::2, 0::2] = im[0::2, 0::2]
    G[1::2, 1::2] = im[1::2, 1::2]

    fG = np.asarray(
            [[0, 1, 0],
             [1, 4, 1],
             [0, 1, 0]]) / 4.0
    fRB = np.asarray(
            [[1, 2, 1],
             [2, 4, 2],
             [1, 2, 1]]) / 4.0

    im_color = np.zeros(im.shape+(3,), dtype='uint8') #RGB
    im_color[:, :, 0] = convolve(R, fRB)
    im_color[:, :, 1] = convolve(G, fG)
    im_color[:, :, 2] = convolve(B, fRB)

    return im_color


# --------------------------------------------------
def get_boundingbox(metadata, z_offset):

    with open(metadata) as f:
        meta = json.load(f)['lemnatec_measurement_metadata']

    loc_gantry_x = float(meta['sensor_fixed_metadata']['location in camera box x [m]'])
    loc_gantry_y = float(meta['sensor_fixed_metadata']['location in camera box y [m]'])
    loc_gantry_z = float(meta['sensor_fixed_metadata']['location in camera box z [m]'])

    gantry_x = float(meta['gantry_system_variable_metadata']['position x [m]']) + loc_gantry_x
    gantry_y = float(meta['gantry_system_variable_metadata']['position y [m]']) + loc_gantry_y
    gantry_z = float(meta['gantry_system_variable_metadata']['position z [m]']) + z_offset + loc_gantry_z#offset in m

    fov_2m = meta['sensor_fixed_metadata']['field of view at 2m in X- Y- direction [m]']
    fov_x, fov_y = fov_2m.strip('[ ]').split(' ')

    img_height = int(meta['sensor_variable_metadata']['height left image [pixel]'])
    img_width = int(meta['sensor_variable_metadata']['width left image [pixel]'])

    B = gantry_z
    A_x = np.arctan((0.5*float(fov_x))/2)
    A_y = np.arctan((0.5*float(fov_y))/2)
    L_x = 2*B*np.tan(A_x)
    L_y = 2*B*np.tan(A_y)

    x_n = gantry_x + (L_x/2)
    x_s = gantry_x - (L_x/2)
    y_w = gantry_y + (L_y/2)
    y_e = gantry_y - (L_y/2)

    bbox_nw_latlon = scanalyzer_to_latlon(x_n, y_w)
    bbox_se_latlon = scanalyzer_to_latlon(x_s, y_e)

    # TERRA-REF
    lon_shift = 0.000020308287

    # Drone
    lat_shift = 0.000018292 #0.000015258894
    b_box =  ( bbox_se_latlon[0] - lat_shift,
                bbox_nw_latlon[0] - lat_shift,
                bbox_nw_latlon[1] + lon_shift,
                bbox_se_latlon[1] + lon_shift )

    return b_box, img_height, img_width


# --------------------------------------------------
def main():
    """Convert bin files to geoTIFFs here"""

    args = get_args()

    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)

    b_box, img_height, img_width = get_boundingbox(args.metadata, args.zoffset)

    shape = (img_width, img_height)
    im = np.fromfile(args.bin, dtype='uint8').reshape(shape[::-1])
    im_color = demosaic(im)
    im_color = (np.rot90(im_color))

    basename = os.path.basename(args.bin).replace('.bin', '.tif')
    out_file = os.path.join(args.outdir, basename)

    extractor_info = None
    create_geotiff(im_color, b_box, out_file, None,
                False, extractor_info, None, compress=True)


# --------------------------------------------------
if __name__ == '__main__':
    main()
