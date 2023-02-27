#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert an pixel image into a mosaic constructed by polygons
=======================================================================
Author: Johannes Beetz
Based on algorithm described in "Artificial Mosaics (2005)" by Di Blasi
"""

import time
import random
from . import edges, guides, tiles, convex, coloring, plotting

def generate_mosaic(parameters=None, output_images=None):
    # Load image
    t_start = time.time()
    random.seed(0)
    img0 = edges.load_image(parameters=parameters)

    output_images['original'] = img0

    h,w = img0.shape[0],img0.shape[1]
    A0 = (2*parameters['half_tile'])**2 # area of tile when placed along straight guideline
    print (f'Estimated number of tiles: {2*w*h/A0:.0f}') # factor 2 since tiles can be smaller than default size
    
    img1 = edges.calculate_edges(output_images['original'],
                                detection_type=parameters['EDGE_DETECTION'],
                                gauss=parameters['GAUSS'],
                                frame=parameters['WITH_FRAME'])
    output_images['edges'] = img1

    # place tiles along chains
    res = guides.chains_and_angles(img1, half_tile=parameters['half_tile'])
    res['polygons'] = tiles.place_tiles_along_chains(res['chains'], 
                                                    res['angles_0to180'], 
                                                    parameters['half_tile'], 
                                                    parameters['RAND_SIZE'], 
                                                    parameters['MAX_ANGLE'], 
                                                    A0)
    output_images['distances'] = res['distances']
    output_images['guidelines'] = res['guidelines']
    output_images['gradient'] = res['gradient']
    output_images['angles_0to180'] = res['angles_0to180']
    output_images['polygons_chains'] = {key: res[key] for key in ['polygons', 'chains']}



    # find gaps and put more tiles inside
    filler_chains = guides.chains_into_gaps(res['polygons'], 
                                                h, w, 
                                                parameters['half_tile'], 
                                                parameters['GAP_CHAIN_SPACING'])

    output_images['used_up_space'] = filler_chains['used_up_space']
    output_images['distance_to_tile'] = filler_chains['distance_to_tile']
    output_images['filler_guidelines'] = filler_chains['filler_guidelines']

    polygons_all = tiles.place_tiles_into_gaps(res['polygons'], 
                                                filler_chains['chains2'], 
                                                parameters['half_tile'], 
                                                A0)

    output_images['polygons_filler'] = {'polygons':polygons_all, 'chains':filler_chains['chains2']}

    # remove parts of tiles which reach outside of image frame
    polygons_all = tiles.cut_tiles_outside_frame(polygons_all,
                                                    parameters['half_tile'], 
                                                    img0.shape[0],
                                                    img0.shape[1])
    output_images['polygons_cut'] = polygons_all

    # convert concave polygons to convex (i.e. more realistic) ones
    polygons_convex = convex.make_convex(polygons_all, 
                                            parameters['half_tile'], 
                                            A0) if parameters['MAKE_CONVEX'] else polygons_all

    # make polygons smaller, remove or correct strange polygons, simplify and drop very small polygons
    polygons_post = tiles.irregular_shrink(polygons_convex, 
                                            parameters['half_tile'])
    polygons_post = tiles.repair_tiles(polygons_post) 
    polygons_post = tiles.reduce_edge_count(polygons_post, 
                                            parameters['half_tile'])
    polygons_post = tiles.drop_small_tiles(polygons_post, 
                                        A0)
    
    # copy colors from original image
    colors = coloring.colors_from_original(polygons_post, img0, method='average')

    t0 = time.time()
    # svg = plotting.draw_tiles(polygons_post, colors, h,w, background_brightness=0.2, return_svg=True, chains=None)
    output_images['final'] = {
                                'polygons_post': polygons_post,
                                'colors': colors,
                                'h': h,
                                'w': w,
                                'background_brightness': 0.2,
                                'return_svg': True,
                                'chains': None
                            }
    
    color_dict = coloring.load_colors()
    keys = color_dict.keys() if not parameters['COLOR_SCHEMA'] else parameters['COLOR_SCHEMA']
    for key in keys:
        new_colors = coloring.modify_colors(colors, 'source', color_dict[key])
        title = key if not parameters['COLOR_SCHEMA'] else ''

        
        output_images[f'final_recolored_{key}'] = {
                                'polygons_post': polygons_post,
                                'colors': new_colors,
                                'h': h,
                                'w': w,
                                'background_brightness': 0.2,
                                'return_svg': True,
                                'chains': None
                            }

    print (f'Total calculation time: {time.strftime("%M min %S s", time.gmtime((time.time()-t_start)))}' ) # sek->min:sek
    print ('Final number of tiles:', len(polygons_post))


















