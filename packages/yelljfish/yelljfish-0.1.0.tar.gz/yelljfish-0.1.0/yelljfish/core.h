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
 */

#ifndef YELLJFISH_CORE_HEADER
#define YELLJFISH_CORE_HEADER

typedef struct {
    uint32_t width;
    uint32_t height;
    uint32_t size;
    uint32_t** rows;
} YelljImage;

typedef struct {
    uint32_t x;
    uint32_t y;
    uint32_t value;
} YelljStartPoint;

typedef struct {
    YelljStartPoint* elems;
    size_t length;
} YelljStartPointList;

typedef struct {
    uint32_t x;
    uint32_t y;
} YelljPoint;

typedef struct {
    YelljPoint* elems;
    size_t length;
} YelljPointList;

void yelljpointlist_init(YelljPointList**);

void yelljstartpointlist_init(YelljStartPointList**);

void yelljimage_init(YelljImage**);

void yelljimage_fillzeros(YelljImage*);

YelljImage* yellj_generate_image(uint32_t, uint32_t, uint32_t,
                                 YelljStartPointList*);

void yellj_perform_run(YelljImage*, YelljPointList*);

uint32_t yellj_get_pixel(YelljImage*, YelljPoint*);

void yellj_set_pixel(YelljImage*, YelljPoint*, uint32_t);

void yellj_generate_and_save_image(uint32_t, uint32_t, uint32_t,
                                   YelljStartPointList*, char*);

void yellj_to_png(YelljImage*, char*);


#endif

