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

#include <Python.h>
#define YELLJFISH_MODULE

#include "wrapper.h"
#include "core.h"

PyMODINIT_FUNC PyInit__core(void);
static PyObject* yellj_py_generate_image(PyObject *self, PyObject *args);


static PyMethodDef YelljMethods[] = {
    {"generate_image", yellj_py_generate_image, METH_VARARGS,
     "generate_image(width, height, runs, starting_points[, outfile])\n\n"
     "Run the image generation algorithm <runs> times.\n"
     "If no outfile is given, the image data will be returned in a\n"
     "modiable array (not implemented yet)."
    },
    {NULL, NULL, 0, NULL} // Sentinel
};

static struct PyModuleDef yelljmodule = {
   PyModuleDef_HEAD_INIT,
   "_core",    /* name of module */
   NULL,      /* module documentation, may be NULL */
   -1,       /* size of per-interpreter state of the module,
                or -1 if the module keeps state in global variables. */
   YelljMethods
};

PyMODINIT_FUNC PyInit__core(void) {
    PyObject *m;

    m = PyModule_Create(&yelljmodule);
    if (m == NULL)
        return NULL;

    return m;
}

static PyObject* yellj_to_pyobject(YelljImage* image) {
    // TODO: return a YelljImage as a modifiable array of some kind
    return Py_None;
}

static PyObject* yellj_py_generate_image(PyObject* self, PyObject* args) {
    uint32_t width, height, runs, i;
    char *outfile;
    PyObject *pypoints, *temp, *pyimage;
    Py_ssize_t tsize;
    YelljStartPointList *points;


    if (PyArg_ParseTuple(args, "iiiO|z", &width, &height, &runs,
                         &pypoints, &outfile)) {
        tsize = PyTuple_Size(pypoints);
        yelljstartpointlist_init(&points);
        points->length = tsize;
        points->elems = (YelljStartPoint*) malloc(sizeof(YelljStartPoint)
                                                  * tsize);
        if (points->elems == NULL) exit(EXIT_FAILURE);
        for (i = 0; i < points->length; i++) {
            temp = PyTuple_GetItem(pypoints, i);
            points->elems[i].x = (uint32_t) PyLong_AsUnsignedLong(PyTuple_GetItem(temp, 0));
            points->elems[i].y = (uint32_t) PyLong_AsUnsignedLong(PyTuple_GetItem(temp, 1));
            points->elems[i].value = (uint32_t) PyLong_AsUnsignedLong(PyTuple_GetItem(temp, 2));
        }
        if (outfile == NULL) {
            pyimage = yellj_to_pyobject(yellj_generate_image(width, height,
                                                             runs, points));
            Py_INCREF(pyimage);
            return pyimage;
        }
        else {
            yellj_generate_and_save_image(width, height, runs, points, outfile);
            Py_INCREF(Py_None);
            return Py_None;
        }
    }
    return NULL;
}
