import os.path
import numpy as np
import cv2
import argparse

GT_PATH = "/home/guy/workspace/doorky/ImagesGT"

from parse_annote_plans import prase_svg, read_file_to_var


def hangleArgs():
    """ Handle input flags """
    parser = argparse.ArgumentParser(add_help=True, description='Take an image and svg and create an image with the bounding boxes in blue')
    parser.add_argument('img_file', type=str,
                        help='path to the image')
    parser.add_argument('svg_file', type=str,
                        help='path to svg file')
    parser.add_argument('output_file', type=str,
                        help='path where to write the image')
    
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = hangleArgs()
    test_file = args.img_file
    test_file_annote = args.svg_file
    
    
    doors = prase_svg(test_file_annote)["doors"]
    image = cv2.imread(test_file)
    
    for door in doors:
        cv2.rectangle(image, (door[0], door[1]), (door[2], door[3]), (255,0,0), 2)
                      
    cv2.imwrite(args.output_file, image)
    
    