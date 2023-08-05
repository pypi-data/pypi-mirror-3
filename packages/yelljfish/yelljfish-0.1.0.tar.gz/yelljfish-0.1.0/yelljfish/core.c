/* yelljfish: a pixel-based, potentially pseudo-random image generator
 * Copyright (C) 2011 Niels Serup

 * This file is part of yelljfish.
 *
 * yelljfish is free software: you can redistribute it and/or modify it under the
 * terms of the GNU Affero General Public License as published by the Free
 * Software Foundation, either version 3 of the License, or (at your option) any
 * later version.
 *
 * yelljfish is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
 * PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
 * details.
 *
 * You should have received a copy of the GNU Affero General Public License along
 * with yelljfish.  If not, see <http://www.gnu.org/licenses/>.

 * PNG portions are based on the program at
 * <http://zarb.org/~gc/html/libpng.html>, copyright 2002-2010 Guillaume
 * Cottenceau, redistributable under the terms of the X11 license.
 */

#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdarg.h>

#define PNG_DEBUG 3
#include <png.h>

#include "core.h"

void yelljpointlist_init(YelljPointList** list) {
    *list = (YelljPointList*) malloc(sizeof(YelljPointList));
    if (*list == NULL) exit(EXIT_FAILURE);
}

void yelljstartpointlist_init(YelljStartPointList** list) {
    *list = (YelljStartPointList*) malloc(sizeof(YelljStartPointList));
    if (*list == NULL) exit(EXIT_FAILURE);
}

void yelljimage_init(YelljImage** image) {
    *image = (YelljImage*) malloc(sizeof(YelljImage));
    if (*image == NULL) exit(EXIT_FAILURE);
}

void yelljimage_fillzeros(YelljImage* image) {
    uint32_t i, j;
    image->rows = (uint32_t**) malloc(sizeof(uint32_t) * image->height);
    if (image->rows == NULL) exit(EXIT_FAILURE);
    for (i = 0; i < image->height; i++) {
        image->rows[i] = (uint32_t*) malloc(sizeof(uint32_t) * image->width);
        if (image->rows[i] == NULL) exit(EXIT_FAILURE);
        for (j = 0; j < image->width; j++)
            image->rows[i][j] = 0;
    }
}

uint32_t yellj_get_pixel(YelljImage* image, YelljPoint* p) {
    return image->rows[p->y][p->x];
}

void yellj_set_pixel(YelljImage* image, YelljPoint* p, uint32_t value) {
    image->rows[p->y][p->x] = value;
}

void yellj_perform_run(YelljImage* image, YelljPointList* points) {
    uint32_t i, j, p1v, p2v, pcv, temp_i;
    YelljPoint p1, p2, pc;

    temp_i = points->length;
    for (i = 0; i < points->length; i++) {
        for (j = i + 1; j < points->length; j++) {
            p1 = points->elems[i];
            p1v = yellj_get_pixel(image, &p1);
            p2 = points->elems[j];
            p2v = yellj_get_pixel(image, &p2);
            
            pcv = (p1v + p2v) / 2; // overflow possible, but doesn't really matter
            if (pcv == 0)
                pcv = 1;
            if (p2.x > p1.x)
                pc.x = p1.x + (p2.x - p1.x) / 2;
            else
                pc.x = p2.x + (p1.x - p2.x) / 2;
            if (p2.y > p1.y)
                pc.y = p1.y + (p2.y - p1.y) / 2;
            else
                pc.y = p2.y + (p1.y - p2.y) / 2;
            if (yellj_get_pixel(image, &pc) == 0) {
                points->elems[temp_i].x = pc.x;
                points->elems[temp_i].y = pc.y;
                yellj_set_pixel(image, &pc, pcv);
                temp_i++;
            }
            
        }
    }
    points->length = temp_i;
}

YelljImage* yellj_generate_image(uint32_t width, uint32_t height,
                                 uint32_t runs,
                                 YelljStartPointList* start_points) {
    YelljImage *image;
    YelljPointList *points;
    YelljPoint temp_point;
    uint32_t i;

    yelljimage_init(&image);
    image->width = width;
    image->height = height;
    image->size = width * height;
    yelljimage_fillzeros(image);

    yelljpointlist_init(&points);
    points->length = start_points->length;
    points->elems = (YelljPoint*) malloc(sizeof(YelljPoint) * image->size);
    for (i = 0; i < start_points->length; i++) {
        points->elems[i].x = start_points->elems[i].x;
        points->elems[i].y = start_points->elems[i].y;
        temp_point.x = points->elems[i].x;
        temp_point.y = points->elems[i].y;
        yellj_set_pixel(image, &temp_point, start_points->elems[i].value);
    }
    runs++;
    for (i = 1; i < runs; i++) {
        yellj_perform_run(image, points);
        printf("Run %u completed.\n", i);
    }
    
    return image;
}

void yellj_generate_and_save_image(uint32_t width, uint32_t height,
                                   uint32_t runs,
                                   YelljStartPointList* start_points,
                                   char* outfile) {
    YelljImage *image = yellj_generate_image(width, height, runs, start_points);
    yellj_to_png(image, outfile);
}

static void png_abort(const char* s, ...) {
    va_list args;
    va_start(args, s);
    vfprintf(stderr, s, args);
    fprintf(stderr, "\n");
    va_end(args);
    abort();
}

void yellj_to_png(YelljImage* image, char* file_name) {
    png_structp png_ptr;
    png_infop info_ptr;
    png_bytep* row_pointers;
    unsigned int i;

    /* Convert (we don't care about color order, any color is fine as long as
       the system for conversion is consistent) */
    row_pointers = (png_bytep*) image->rows;
    
    
    /* create file */
    FILE *fp = fopen(file_name, "wb");
    if (!fp)
        png_abort("[write_png_file] File %s could not be opened for writing", file_name);


    /* initialize stuff */
    png_ptr = png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);

    if (!png_ptr)
        png_abort("[write_png_file] png_create_write_struct failed");

    info_ptr = png_create_info_struct(png_ptr);
    if (!info_ptr)
        png_abort("[write_png_file] png_create_info_struct failed");

    if (setjmp(png_jmpbuf(png_ptr)))
        png_abort("[write_png_file] Error during init_io");

    png_init_io(png_ptr, fp);

    
    /* write header */
    if (setjmp(png_jmpbuf(png_ptr)))
        png_abort("[write_png_file] Error during writing header");

    png_set_IHDR(png_ptr, info_ptr, image->width, image->height,
                 (png_byte) 8, PNG_COLOR_TYPE_RGB_ALPHA, PNG_INTERLACE_NONE,
                 PNG_COMPRESSION_TYPE_BASE, PNG_FILTER_TYPE_BASE);

    png_write_info(png_ptr, info_ptr);


    /* write bytes */
    if (setjmp(png_jmpbuf(png_ptr)))
        png_abort("[write_png_file] Error during writing bytes");
    
    png_write_image(png_ptr, row_pointers);
    

    /* end write */
    if (setjmp(png_jmpbuf(png_ptr)))
        png_abort("[write_png_file] Error during end of write");

    png_write_end(png_ptr, NULL);

    /* cleanup heap allocation */
    for (i = 0; i < image->height; i++)
        free(row_pointers[i]);
    free(row_pointers);

    fclose(fp);
}

