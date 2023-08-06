/*
PyGDChart

Copyright (c) 2003, Nullcube Pty Ltd
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

*   Redistributions of source code must retain the above copyright notice, this
    list of conditions and the following disclaimer.
*   Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation
    and/or other materials provided with the distribution.
*   Neither the name of Nullcube Pty Ltd nor the names of its contributors may
    be used to endorse or promote products derived from this software without
    specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#include <stdio.h>
#include <string.h>
#include <assert.h>

#include "Python.h"
#include "gdchart.h"
#include "gdcpie.h"
#include "gdc.h"

#ifndef HAVE_JPEG
#define GDC_JPEG 1
#endif

static PyObject *PGError;

typedef enum {
    GRAPH,
    PIE
} charttype;

typedef enum {
    OPT_BOOL,         /* CHAR */
    OPT_BOOL_A,       /* CHAR */
    OPT_COLOR,
    OPT_COLOR_A,
    OPT_CHAR,
    OPT_FLOAT,     
    OPT_DOUBLE,
    OPT_FONTSIZE,         /* INT  */
    OPT_INT,       
    OPT_INT_A,     
    OPT_LONG,      
    OPT_PERCENT,       /* Unsigned char */
    OPT_SHORT,     
    OPT_STRING,    
    OPT_USHORT,    
    OPT_UCHAR
} options;

typedef struct Option Option;
struct Option {
    char            *keyword;
    int             type;
    void            *var;
    int             size;
}; 

Option GraphOptions[] = {
    { "annotation_font_size",   OPT_FONTSIZE,   &GDC_annotation_font_size,	0},
    { "bar_width",              OPT_PERCENT,    &GDC_bar_width,		        0},
    { "bg_color",               OPT_COLOR,      &GDC_BGColor,		        0},
    { "bg_image",               OPT_STRING,     &GDC_BGImage,		        0},
    { "bg_transparent",         OPT_BOOL,       &GDC_transparent_bg,		0},
    { "border",                 OPT_INT,        &GDC_border,		        0},
    { "ext_color",              OPT_COLOR_A,    &GDC_ExtColor,		        0}, /* numsets * numpoints */
    { "ext_vol_color",          OPT_COLOR_A,    &GDC_ExtVolColor,		    0}, /* numpoints */
    { "generate_img",           OPT_BOOL,       &GDC_generate_img,		    0},
    { "grid",                   OPT_INT,        &GDC_grid,		            0},
    { "grid_color",             OPT_COLOR,      &GDC_GridColor,		        0},
    { "hard_graphheight",       OPT_INT,        &GDC_hard_grapheight,		0},
    { "hard_graphwidth",        OPT_INT,        &GDC_hard_graphwidth,		0},
    { "hard_size",              OPT_BOOL,       &GDC_hard_size,		        0},
    { "hard_xorig",             OPT_INT,        &GDC_hard_xorig,		    0},
    { "hard_yorig",             OPT_INT,        &GDC_hard_yorig,		    0},
    { "hlc_cap_width",          OPT_PERCENT,    &GDC_HLC_cap_width,		    0},
    { "hlc_style",              OPT_INT,        &GDC_HLC_style,		        0},
    { "hold_img",               OPT_INT,        &GDC_hold_img,		        0},
    { "interpolations",         OPT_BOOL,       &GDC_interpolations,		0},
    { "image_type",             OPT_INT,        &GDC_image_type,		    0},
    { "jpeg_quality",           OPT_INT,        &GDC_jpeg_quality,		    0},
    { "line_color",             OPT_COLOR,      &GDC_LineColor,		        0},
    { "plot_color",             OPT_COLOR,      &GDC_PlotColor,		        0},
    { "requested_yinterval",    OPT_FLOAT,      &GDC_requested_yinterval,	0},
    { "requested_ymax",         OPT_FLOAT,      &GDC_requested_ymax,		0},
    { "requested_ymin",         OPT_FLOAT,      &GDC_requested_ymin,		0},
    { "set_color",              OPT_COLOR_A,    &GDC_SetColor,		        0}, /* numsets */
    { "stack_type",             OPT_INT,        &GDC_stack_type,		    0},
    /* Python names cannot start with digits - so we rename these options slightly:*/
    { "threeD_angle",           OPT_UCHAR,      &GDC_3d_angle,		        0},
    { "threeD_depth",           OPT_FLOAT,      &GDC_3d_depth,		        0},
    { "thumblabel",             OPT_STRING,     &GDC_thumblabel,		    0},
    { "thumbnail",              OPT_BOOL,       &GDC_thumbnail,		        0},
    { "thumbval",               OPT_FLOAT,      &GDC_thumbval,		        0},
    { "ticks",                  OPT_INT,        &GDC_ticks,		            0},
    { "title",                  OPT_STRING,     &GDC_title,		            0},
    { "title_color",            OPT_COLOR,      &GDC_TitleColor,            0},
    { "title_font_size",        OPT_FONTSIZE,   &GDC_title_size,            0},
    { "vol_color",              OPT_COLOR,      &GDC_VolColor,		        0},
    { "xaxis",                  OPT_BOOL,       &GDC_xaxis,		            0},
    { "xaxis_angle",            OPT_DOUBLE,     &GDC_xaxis_angle,		    0},
    { "xaxis_font_size",        OPT_FONTSIZE,   &GDC_xaxisfont_size,		0},
    { "xlabel_color",           OPT_COLOR,      &GDC_XLabelColor,		    0},
    { "xlabel_spacing",         OPT_SHORT,      &GDC_xlabel_spacing,		0},
    { "xlabel_ctl",             OPT_BOOL_A,     &GDC_xlabel_ctl,		    0}, /* numpoints */
    { "xtitle",                 OPT_STRING,     &GDC_xtitle,                0},
    { "xtitle_color",           OPT_COLOR,      &GDC_XTitleColor,           0},
    { "xtitle_font_size",       OPT_FONTSIZE,   &GDC_xtitle_size,           0},
    { "yaxis",                  OPT_BOOL,       &GDC_yaxis,		            0},
    { "yaxis2",                 OPT_BOOL,       &GDC_yaxis2,		        0},
    { "yaxis_font_size",        OPT_FONTSIZE,   &GDC_yaxisfont_size,		0},
    { "ylabel_color",           OPT_COLOR,      &GDC_YLabelColor,		    0},
    { "ylabel_density",         OPT_PERCENT,    &GDC_ylabel_density,		0},
    { "ylabel_fmt",             OPT_STRING,     &GDC_ylabel_fmt,            0},
    { "ylabel2_color",          OPT_COLOR,      &GDC_YLabel2Color,          0},
    { "ylabel2_fmt",            OPT_STRING,     &GDC_ylabel2_fmt,           0},
    { "ytitle",                 OPT_STRING,     &GDC_ytitle,                0},
    { "ytitle_color",           OPT_COLOR,      &GDC_YTitleColor,           0},
    { "ytitle_font_size",       OPT_FONTSIZE,   &GDC_ytitle_size,           0},
    { "ytitle2",                OPT_STRING,     &GDC_ytitle2,               0},
    { "ytitle2_color",          OPT_COLOR,      &GDC_YTitle2Color,          0},
    { "yval_style",             OPT_BOOL,       &GDC_yval_style,            0},
    { "zeroshelf",              OPT_BOOL,       &GDC_0Shelf,		        0},
#ifdef HAVE_LIBFREETYPE
    { "annotation_font",        OPT_STRING,     &GDC_annotation_font,		0},
    { "annotation_ptsize",      OPT_DOUBLE,     &GDC_annotation_ptsize,		0},
    { "title_font",             OPT_STRING,     &GDC_title_font,            0},
    { "title_ptsize",           OPT_DOUBLE,     &GDC_title_ptsize,          0},
    { "xaxis_font",             OPT_STRING,     &GDC_xaxis_font,		    0},
    { "xaxis_ptsize",           OPT_DOUBLE,     &GDC_xaxis_ptsize,		    0},
    { "xtitle_font",            OPT_STRING,     &GDC_xtitle_font,           0},
    { "xtitle_ptsize",          OPT_DOUBLE,     &GDC_xtitle_ptsize,         0},
    { "yaxis_font",             OPT_STRING,     &GDC_yaxis_font,		    0},
    { "yaxis_ptsize",           OPT_DOUBLE,     &GDC_yaxis_ptsize,		    0},
    { "ytitle_font",            OPT_STRING,     &GDC_ytitle_font,           0},
    { "ytitle_ptsize",          OPT_DOUBLE,     &GDC_ytitle_ptsize,         0},
#endif 
    { NULL }
};

Option PieOptions[] = {
    { "bg_color",               OPT_COLOR,      &GDCPIE_BGColor,            0},
    { "bg_image",               OPT_STRING,     &GDC_BGImage,               0},
    { "edge_color",             OPT_COLOR,      &GDCPIE_EdgeColor,          0},
    { "explode",                OPT_INT_A,      &GDCPIE_explode,            0},  /* numpoints */
    { "generate_img",           OPT_BOOL,       &GDC_generate_img,          0},
    { "image_type",             OPT_INT,        &GDC_image_type,            0},
    { "jpeg_quality",           OPT_INT,        &GDC_jpeg_quality,          0},
    { "label_dist",             OPT_INT,        &GDCPIE_label_dist,         0},
    { "label_font_size",        OPT_FONTSIZE,   &GDCPIE_label_size,         0},
    { "label_line",             OPT_BOOL,       &GDCPIE_label_line,         0},
    { "line_color",             OPT_COLOR,      &GDCPIE_LineColor,          0},
    { "missing",                OPT_BOOL_A,     &GDCPIE_missing,            0}, /* numpoints */
    { "other_threshold",        OPT_CHAR,       &GDCPIE_other_threshold,	0},
    { "percent_format",         OPT_STRING,     &GDCPIE_percent_fmt,		0},
    { "percent_labels",         OPT_INT,        &GDCPIE_percent_labels,		0},
    { "perspective",            OPT_USHORT,     &GDCPIE_perspective,		0},
    { "color",                  OPT_COLOR_A,    &GDCPIE_Color,		        0}, /* numpoints */
    { "plot_color",             OPT_COLOR,      &GDCPIE_PlotColor,		    0},
    { "threeD_angle",           OPT_USHORT,     &GDCPIE_3d_angle,           0},
    { "threeD_depth",           OPT_USHORT,     &GDCPIE_3d_depth,           0},
    { "title",                  OPT_STRING,     &GDCPIE_title,		        0},
    { "title_font_size",        OPT_FONTSIZE,   &GDCPIE_title_size,		    0},
#ifdef HAVE_LIBFREETYPE
    { "label_font",             OPT_STRING,     &GDCPIE_label_font,         0},
    { "label_ptsize",           OPT_FLOAT,      &GDCPIE_label_ptsize,       0},
    { "title_font",             OPT_STRING,     &GDCPIE_title_font,		    0},
    { "title_ptsize",           OPT_FLOAT,      &GDCPIE_title_ptsize,		0},
#endif
    { NULL }
};

#define MEMPOOLSIZE 256
void *mempool[MEMPOOLSIZE];     /* The global memory pool array. */
int mempool_final = -1;         /* The greatest filled array index. */

/* Add a float constant to a module. Same as PyModule_AddIntConstant. */
int AddFloatConstant(PyObject *m, char *name, double value){
    return PyModule_AddObject(m, name, PyFloat_FromDouble(value));
}

/* Frees all memory in mempool. */
void clearMempool(void){
    int i;
    for (i = 0; i < mempool_final; i++){
        if (mempool[i]){
            free(mempool[i]);
            mempool[i] = NULL;
        }
    }
}

/* 
 * Add a piece of allocated memory to the mempool. As arguments, it takes the
 * new pointer, and the old pointer. If the old pointer is found in the
 * mempool, it is free()d, and replaced with the new pointer. Otherwise, the
 * new pointer is placed in an empty slot.
 * The new pointer can be NULL.
 * The function returns the new pointer.  */
void addMempool(void *new, void *old){
    int i;
    for (i = 0; i < MEMPOOLSIZE; i++) {
        if (mempool[i] == NULL){
            if (new == NULL){
                    return;
            }
            mempool[i] = new;
            mempool_final = i;
            return;
        } else if (mempool[i] == old){
            free(old);
            if (new == NULL){
                mempool[i] = mempool[mempool_final];
                mempool[mempool_final] = NULL;
                --mempool_final;
            } else
                mempool[i] = new;
            return;
        }
    }
    /* FIXME: Error here... */
    fprintf(stderr, "Mempool is full. This should never happen - please contact software authors.\n");
}


PyObject *getInt(Option opt){
    return PyInt_FromLong((long)*(int*)opt.var);
}

PyObject *getShort(Option opt){
    return PyInt_FromLong((long)*(short*)opt.var);
}

PyObject *getUshort(Option opt){
    return PyInt_FromLong((long)(*(unsigned short*)opt.var));
}

PyObject *getUchar(Option opt){
    return PyInt_FromLong((long)(*((unsigned char*)opt.var)));
}

PyObject *getChar(Option opt){
    return PyInt_FromLong((long)(*(char *)opt.var));
}

PyObject *getDouble(Option opt){
    return PyFloat_FromDouble(*(double *)opt.var);
}

PyObject *getFloat(Option opt){
    return PyFloat_FromDouble((double)(*(float *)opt.var));
}

PyObject *getString(Option opt){
    if (!(*(char**)opt.var)){
        Py_INCREF(Py_None);
        return Py_None;
    }
    return PyString_FromString(*(char**)opt.var);
}

PyObject *getIntA(Option opt){
    int i;
    PyObject *pint;
    PyObject *list = PyList_New(0);
    if (!list)
        return NULL;
    if (!(*(int**)opt.var)){
        Py_INCREF(Py_None);
        return Py_None;
    }
    for (i = 0; i < opt.size; i++){
        pint = PyInt_FromLong((long)(*(int **)opt.var)[i]);
        if (!pint || PyList_Append(list, pint) < 0)
            goto cleanup;
        Py_DECREF(pint);
    }
    return list;
    cleanup:
        Py_DECREF(list);
    return NULL;
}

PyObject *getBoolA(Option opt){
    int i;
    PyObject *pint;
    PyObject *list = PyList_New(0);
    if (!list)
        return NULL;
    if (!(*(char**)opt.var)){
        Py_INCREF(Py_None);
        return Py_None;
    }
    for (i = 0; i < opt.size; i++){
        pint = PyInt_FromLong((long)(*(char**)opt.var)[i]);
        if (!pint || PyList_Append(list, pint) < 0)
            goto cleanup;
        Py_DECREF(pint);
    }
    return list;
    cleanup:
        Py_DECREF(list);
    return NULL;
}

PyObject *getColorA(Option opt){
    int i;
    PyObject *pint;
    PyObject *list = PyList_New(0);
    if (!list)
        return NULL;
    if (!(*(char**)opt.var)){
        Py_INCREF(Py_None);
        return Py_None;
    }
    for (i = 0; i < opt.size; i++){
        pint = PyInt_FromLong((*(long**)opt.var)[i]);
        if (!pint || PyList_Append(list, pint) < 0)
                goto cleanup;
        Py_DECREF(pint);
    }
    return list;
    cleanup:
        Py_DECREF(list);
    return NULL;
}


/* Construct a dictionary of the following format:
 *          option: (index, type, value) */
PyObject *makeOptionDict(Option *opts){
    PyObject *(*funcptr)(Option); 
    PyObject *ret;
    int optIndex = 0;

    PyObject *tup;
    PyObject *dict = PyDict_New();
    while (opts[optIndex].keyword != NULL) {
        tup = PyTuple_New(3);
        PyTuple_SET_ITEM(tup, 0, PyInt_FromLong((long)optIndex));
        PyTuple_SET_ITEM(tup, 1, PyInt_FromLong((long)opts[optIndex].type));  

        switch (opts[optIndex].type){
            case OPT_INT:
            case OPT_LONG:
            case OPT_COLOR:
                funcptr = getInt;
                break;

            case OPT_SHORT:
                funcptr = getShort;
                break;

            case OPT_USHORT:
                funcptr = getUshort;
                break;

            case OPT_PERCENT:
            case OPT_BOOL:
            case OPT_FONTSIZE:
            case OPT_UCHAR:
                funcptr = getUchar;
                break;

            case OPT_CHAR:
                funcptr = getChar;
                break;

            case OPT_STRING:
                funcptr = getString;
                break;

            case OPT_FLOAT:
                funcptr = getFloat;
                break;

            case OPT_DOUBLE:
                funcptr = getDouble;
                break;
                
            case OPT_INT_A:
                funcptr = getIntA;
                break;

            case OPT_BOOL_A:
                funcptr = getBoolA;
                break;

            case OPT_COLOR_A:
                funcptr = getColorA;
                break;

            default:
                PyErr_SetString(PyExc_ValueError, "Argument is not a valid option type.");
                goto clean;
        }
        if (funcptr && opts[optIndex].var){
            ret = funcptr(opts[optIndex]);
            if (!ret)
                goto clean;
            PyTuple_SET_ITEM(tup, 2, ret);
        } else {
            PyTuple_SET_ITEM(tup, 2, Py_None);
        }
        if (PyDict_SetItemString(dict, opts[optIndex].keyword, tup) < 0) 
            goto clean;
        optIndex ++;
    }
    return dict;

clean:
    Py_DECREF(dict);
    return NULL;
}

/*
 * Retrieve current values of the specified chart options. Returns a
 * dictionary.
 */
PyObject *getOptions(PyObject *self, PyObject *args){
    int type;
    if (!PyArg_ParseTuple(args, "i", &type))
        return NULL;
    if (type == GRAPH)
        return makeOptionDict(GraphOptions);
    else if (type == PIE)
        return makeOptionDict(PieOptions);
    else{
        PyErr_SetString(PyExc_ValueError, "Argument is neither PIE nor GRAPH.");
        return NULL;
    }
}

/*
 *   Set an option. 
 */
PyObject *setOption(PyObject *self, PyObject *args){
    int type, optIndex;
    PyObject *val, *tmp;
    long ival;
    double dval;
    char *sval, *mstr;
    Option *table;
    if (!PyArg_ParseTuple(args, "iiO", &type, &optIndex, &val)){
        return NULL;
    }
    if (type == GRAPH)
        table = GraphOptions;
    else if (type == PIE)
        table = PieOptions;
    else{
        PyErr_SetString(PyExc_ValueError, "Argument is neither PIE nor GRAPH.");
        return NULL;
    }

    switch (table[optIndex].type){
        case OPT_INT:
        case OPT_COLOR:
        case OPT_SHORT:
        case OPT_USHORT:
        case OPT_UCHAR: 
        case OPT_BOOL: 
        case OPT_FONTSIZE: 
        case OPT_PERCENT: 
        case OPT_CHAR: 
        case OPT_LONG: 
            /* FIXME: Check return value... */
            tmp = PyNumber_Int(val);
            if (PyErr_Occurred())
                return NULL;
            ival = PyInt_AsLong(tmp);
            Py_DECREF(tmp);
            if (PyErr_Occurred())
                return NULL;
            switch (table[optIndex].type){
                case OPT_INT:
                    *(int*)table[optIndex].var = ival;
                    break;
                case OPT_SHORT:
                    *(short*)table[optIndex].var = ival;
                    break;
                case OPT_USHORT:
                    *(unsigned short*)table[optIndex].var = ival;
                    break;
                case OPT_UCHAR:
                case OPT_PERCENT:
                    *(unsigned char*)table[optIndex].var = ival;
                    break;
                case OPT_BOOL:
                    *(char*)table[optIndex].var = ival;
                    break;
                case OPT_FONTSIZE:
                    *(int*)table[optIndex].var = ival;
                    break;
                case OPT_CHAR:
                    *(char*)table[optIndex].var = ival;
                    break;
                case OPT_LONG:
                case OPT_COLOR:
                    *(long*)table[optIndex].var = ival;
                    break;
            }
            break;

        case OPT_FLOAT:
        case OPT_DOUBLE:
            tmp = PyNumber_Float(val);
            if (PyErr_Occurred())
                return NULL;
            dval = PyFloat_AsDouble(tmp);
            Py_DECREF(tmp);
            if (PyErr_Occurred())
                return NULL;
            if (table[optIndex].type == OPT_FLOAT) 
                *(float*)table[optIndex].var = dval;
            else
                *(double*)table[optIndex].var = dval;
            break;

        case OPT_STRING:
            if (val == Py_None){
                addMempool(NULL, *(char**)table[optIndex].var);
                *(char**)table[optIndex].var = NULL;
            } else {
                tmp = PyObject_Str(val);
                if (!tmp)
                    return NULL;
                sval = PyString_AsString(tmp);
                Py_DECREF(tmp);
                if (!sval)
                    return NULL;
                mstr = malloc(strlen(sval) + 1);
                if (!mstr){
                    PyErr_NoMemory();
                    return NULL;
                }
                addMempool(mstr, *(char**)table[optIndex].var);
                strcpy(mstr, sval);
                *(char**)table[optIndex].var = mstr;
            }
            break;

        case OPT_INT_A:
            if (val == Py_None){
                addMempool(NULL, *(int**)table[optIndex].var);
                *(int**)table[optIndex].var = NULL;
            } else {
                int i, len;
                int *arr;
                PyObject *aval;

                len = PyObject_Length(val);
                if (len < 0){
                    PyErr_SetString(PyExc_ValueError, "Cannot retrieve length of item.");
                    return NULL;
                }
                arr = calloc((size_t)len, sizeof(int));
                if (!arr){
                    PyErr_NoMemory();
                    return NULL;
                }
                for (i = 0; i < len; i++){
                    aval = PySequence_GetItem(val, i);
                    if (aval == NULL){
                        free(arr);
                        PyErr_SetString(PyExc_ValueError, "Cannot access list item.");
                        return NULL;
                    };
                    arr[i] = (int)PyInt_AsLong(aval);
                    Py_DECREF(aval);
                    if (PyErr_Occurred()){
                        free(arr);
                        return NULL;
                    }
                }
                addMempool(arr, *(int**)table[optIndex].var);
                *(int**)table[optIndex].var = arr;
                table[optIndex].size = len;
            }
            break;

        case OPT_BOOL_A:
            if (val == Py_None){
                addMempool(NULL, *(char**)table[optIndex].var);
                *(char**)table[optIndex].var = NULL;
            } else {
                int i, len;
                char *arr;
                PyObject *aval;

                len = PyObject_Length(val);
                if (len < 0){
                    PyErr_SetString(PyExc_ValueError, "Cannot retrieve length of item.");
                    return NULL;
                }
                arr = calloc((size_t)len, sizeof(char));
                if (!arr){
                    PyErr_NoMemory();
                    return NULL;
                }
                for (i = 0; i < len; i++){
                    aval = PySequence_GetItem(val, i);
                    if (aval == NULL){
                        free(arr);
                        PyErr_SetString(PyExc_ValueError, "Cannot access list item.");
                        return NULL;
                    };
                    arr[i] = (char)PyInt_AsLong(aval);
                    Py_DECREF(aval);
                    if (PyErr_Occurred()){
                        free(arr);
                        return NULL;
                    }
                }
                addMempool(arr, *(char**)table[optIndex].var);
                *(char**)table[optIndex].var = arr;
                table[optIndex].size = len;
            }
            break;

        case OPT_COLOR_A:
            if (val == Py_None){
                addMempool(NULL, *(long**)table[optIndex].var);
                *(long**)table[optIndex].var = NULL;
            } else {
                int i, len;
                long *arr;
                PyObject *aval;

                len = PyObject_Length(val);
                if (len < 0){
                    PyErr_SetString(PyExc_ValueError, "Cannot retrieve length of item.");
                    return NULL;
                }
                arr = calloc((size_t)len, sizeof(long));
                if (!arr){
                    PyErr_NoMemory();
                    return NULL;
                }
                for (i = 0; i < len; i++){
                    aval = PySequence_GetItem(val, i);
                    if (aval == NULL){
                        free(arr);
                        PyErr_SetString(PyExc_ValueError, "Cannot access list item.");
                        return NULL;
                    };
                    arr[i] = PyInt_AsLong(aval);
                    Py_DECREF(aval);
                    if (PyErr_Occurred()){
                        free(arr);
                        return NULL;
                    }
                }
                addMempool(arr, *(long**)table[optIndex].var);
                *(long**)table[optIndex].var = arr;
                table[optIndex].size = len;
            }
            break;

        default:
            PyErr_SetString(PyExc_ValueError, "Option type unknown.");
            return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

/*
 * The argument should be a list containing only strings.
 * The function returns an array of C strings. Both the 
 * array and the strings should be freed after use.
 * Returns NULL on error. 
 */
char **getStringsFromSequence(PyObject *lst){
    int i, j, slen;
    size_t len;
    char **strings;
    char *mem;
    PyObject *pobj, *pstr;

    len = PyObject_Length(lst);
    if (len < 0)
        return NULL;
    strings = calloc((size_t)len, sizeof(char*));
    if (!strings){
        PyErr_NoMemory();
        return NULL;
    }
    for (i = 0; i < len; i++){
        pobj = PySequence_GetItem(lst, i);
        pstr = PyObject_Str(pobj);
        Py_DECREF(pobj);
        if (pstr == NULL)
            goto cleanup;
        slen = PyString_Size(pstr);
        if (slen == NULL)
            goto cleanup;
        mem = malloc((size_t)slen+1);
        if (mem == NULL){
            PyErr_NoMemory();
            goto cleanup;
        }
        strcpy(mem, PyString_AsString(pstr));
        Py_DECREF(pstr);
        strings[i] = mem;
    }
    return strings;

cleanup:
    for (j = 0; j < len; j++){
        if (strings[j])
            free(strings[j]);
        else 
            break;
    }
    free(strings);
    PyErr_SetString(PyExc_ValueError, "Label cannot be converted to string.");
    return NULL;
}

/*
 * The argument should be a list containing only floats, ints and None objects.
 * The function returns a list of C floats. Note that the caller should free
 * this list after use. 
 *
 * Returns NULL on error. 
 */
float *getFloatsFromSequence(PyObject *lst){
    int i, len;
    float *floats;
    PyObject *pnum;

    len = PyObject_Length(lst);
    floats = malloc(len * sizeof(float));
    if (floats == NULL){
        PyErr_NoMemory();
        return NULL;
    }
    for (i = 0; i < len; i++){
        pnum = PySequence_GetItem(lst, i);
        if (pnum == Py_None){
          floats[i] = GDC_NOVALUE;
        } else {
            if ((!pnum) || (!PyNumber_Check(pnum))){
                PyMem_Free(floats);
                return NULL;
            }
            floats[i] = (float)PyFloat_AsDouble(pnum);
        }
        Py_DECREF(pnum);
    }
    return floats;
}

PyObject *pygd_out_pie(PyObject *self, PyObject *args){
    int width, height, graphtype, numpoints;
    int i;
    PyObject *pfile; 
    PyObject *labels = NULL; 
    PyObject *data = NULL;
    PyObject *ret = NULL;
    char **labels_strings = NULL;
    float *data_floats = NULL;
    FILE *fp;

    if (!PyArg_ParseTuple(args, "iiO!iiOO", &width, &height, &PyFile_Type, &pfile, 
                                                &graphtype, &numpoints, &labels, &data)){
        return NULL;
    }

    if (!PySequence_Check(data)){
        PyErr_SetString(PyExc_TypeError, "Argument data should be a list.");
        goto cleanup;
    }

    if (PyObject_IsTrue(labels)){
        if (!PySequence_Check(labels)){
            PyErr_SetString(PyExc_TypeError, "Argument labels should be a list.");
            goto cleanup;
        }
        if (!PyObject_Length(labels) == numpoints){
            PyErr_SetString(PyExc_TypeError, "Number of labels should equal numpoints.");
            goto cleanup;
        }
        labels_strings = getStringsFromSequence(labels);
        if (labels_strings == NULL){
            PyErr_SetString(PyExc_TypeError, "Could not convert labels arguments to strings.");
            goto cleanup;
        }
    } 

    if (!PyObject_Length(data) == numpoints){
        PyErr_SetString(PyExc_TypeError, "Number of data points should equal numpoints.");
        goto cleanup;
    }
    data_floats = getFloatsFromSequence(data);
    if (data_floats == NULL){
        PyErr_SetString(PyExc_TypeError, "Could not convert data arguments to floats.");
        goto cleanup;
    }

    fp = PyFile_AsFile(pfile);
    /* Why doesn't this function have a return value? */
    GDC_out_pie( width, height, fp, graphtype, numpoints, labels_strings,  data_floats);

    Py_INCREF(Py_None);
    ret = Py_None;

cleanup:
    if (labels_strings){
        for (i = 0; i < numpoints; i++)
            free(labels_strings[i]);
        free(labels_strings);
    }
    if (data_floats)
        free(data_floats);
    return ret;
}

PyObject *pygd_out_graph(PyObject *self, PyObject *args){
    int width, height, graphtype, numpoints, numsets, retval;
    int i;
    PyObject *pfile, *labels, *data, *combodata;
    PyObject *ret = NULL;
    char **labels_strings = NULL;
    float *data_floats = NULL;
    float *combodata_floats = NULL;
    FILE *fp;

    if (!PyArg_ParseTuple(args, "iiO!iiOiOO", &width, &height, &PyFile_Type, &pfile, 
                                                &graphtype, &numpoints, &labels, &numsets, 
                                                    &data, &combodata)){
        return NULL;
    }

    if (!PySequence_Check(data)){
        PyErr_SetString(PyExc_TypeError, "Argument data should be a list.");
        goto cleanup;
    }

    if (PyObject_IsTrue(labels)){
        if (!PySequence_Check(labels)){
            PyErr_SetString(PyExc_TypeError, "Argument labels should be a list.");
            goto cleanup;
        }
        if (!PyObject_Length(labels) == numpoints){
            PyErr_SetString(PyExc_TypeError, "Number of labels should equal numpoints.");
            goto cleanup;
        }
        labels_strings = getStringsFromSequence(labels);
        if (labels_strings == NULL){
            PyErr_SetString(PyExc_TypeError, "Could not convert labels arguments to strings.");
            goto cleanup;
        }
    } 

    if (PyObject_IsTrue(combodata)){
        if (!PySequence_Check(combodata)){
            PyErr_SetString(PyExc_TypeError, "Argument combodata should be a list.");
            goto cleanup;
        }
        if (!PyObject_Length(combodata) == numpoints){
            PyErr_SetString(PyExc_TypeError, "Number of combo data points should equal numpoints.");
            goto cleanup;
        }
        combodata_floats = getFloatsFromSequence(combodata);
        if (combodata_floats == NULL){
            PyErr_SetString(PyExc_TypeError, "Could not convert combodata arguments to floats.");
            goto cleanup;
        }
    } 

    if (!PyObject_Length(data) == numpoints){
        PyErr_SetString(PyExc_TypeError, "Number of data points should equal numpoints.");
        goto cleanup;
    }
    data_floats = getFloatsFromSequence(data);
    if (data_floats == NULL){
        PyErr_SetString(PyExc_TypeError, "Could not convert data arguments to floats.");
        goto cleanup;
    }

    fp = PyFile_AsFile(pfile);
    retval = GDC_out_graph( width, height, fp, graphtype, 
                            numpoints, labels_strings, numsets, 
                            data_floats, combodata_floats);
    if (retval){
        PyErr_SetString(PGError, "Generic error: could not draw graph.");
        ret =  NULL;
    } else {
        Py_INCREF(Py_None);
        ret = Py_None;
    }

cleanup:
    if (labels_strings){
        for (i = 0; i < numpoints; i++)
            free(labels_strings[i]);
        free(labels_strings);
    }
    if (combodata_floats)
        free(combodata_floats);
    if (data_floats)
        free(data_floats);
    return ret;
}

PyObject *pygd_set_scatter(PyObject *self, PyObject *args){
    int i, len;
    GDC_SCATTER_T *scatters;
    PyObject *scatList, *s, *attr, *aval;
    if (!PyArg_ParseTuple(args, "O", &scatList)){
        return NULL;
    }
    if (scatList == Py_None){
        addMempool(NULL, GDC_scatter);
        GDC_scatter = NULL;
        GDC_num_scatter_pts = 0;
        Py_INCREF(Py_None);
        return Py_None;
    }

    /* TODO: If scatlist is None, we clear the scatter points. */
    if (!PySequence_Check(scatList)){
        PyErr_SetString(PyExc_TypeError, "Argument data should be a list.");
        return NULL;
    }

    len = PyObject_Length(scatList);
    scatters = malloc(len * sizeof(GDC_SCATTER_T));
    for (i = 0; i < len; i++){
        s = PySequence_GetItem(scatList, i);
        attr = PyObject_GetAttrString(s, "point");
        if (attr == NULL)
            goto cleanup;
        aval = PyNumber_Float(attr);
        Py_DECREF(attr);
        if (aval == NULL){
            PyErr_SetString(PyExc_TypeError, "Point value must be representable as a float.");
            goto free;
        }
        scatters[i].point = (float)PyFloat_AsDouble(aval);
        Py_DECREF(aval);
            
        attr = PyObject_GetAttrString(s, "val");
        if (attr == NULL)
            goto cleanup;
        aval = PyNumber_Float(attr);
        Py_DECREF(attr);
        if (aval == NULL){
            PyErr_SetString(PyExc_TypeError, "Value must be representable as a float.");
            goto free;
        }
        scatters[i].val = (float)PyFloat_AsDouble(aval);
        Py_DECREF(aval);

        attr = PyObject_GetAttrString(s, "width");
        if (attr == NULL)
            goto cleanup;
        aval = PyNumber_Int(attr);
        Py_DECREF(attr);
        if (aval == NULL){
            PyErr_SetString(PyExc_TypeError, "Width must be representable as an int.");
            goto free;
        }
        scatters[i].width = (int)PyInt_AsLong(aval);
        Py_DECREF(aval);

        attr = PyObject_GetAttrString(s, "color");
        if (attr == NULL)
            goto cleanup;
        aval = PyNumber_Int(attr);
        Py_DECREF(attr);
        if (aval == NULL){
            PyErr_SetString(PyExc_TypeError, "Color must be representable as an int.");
            goto free;
        }
        scatters[i].color = (unsigned long)PyInt_AsLong(aval);
        Py_DECREF(aval);

        attr = PyObject_GetAttrString(s, "_type");
        if (attr == NULL)
            goto cleanup;
        aval = PyNumber_Int(attr);
        Py_DECREF(aval);
        if (aval == NULL){
            PyErr_SetString(PyExc_TypeError, "Type must be representable as an int.");
            goto free;
        }
        scatters[i].ind = (int)PyInt_AsLong(aval);
        Py_DECREF(aval);

        Py_DECREF(s);
    }
    addMempool(scatters, GDC_scatter);
    GDC_scatter = scatters;
    GDC_num_scatter_pts = len;
    Py_INCREF(Py_None);
    return Py_None;

cleanup:
        PyErr_SetString(PyExc_TypeError, "Object does not seem to be a scatter point object.");
free:
        free(scatters);
        return NULL;
}


PyObject *pygd_annotate(PyObject *self, PyObject *args){
    PyObject *anno, *attr, *aval;
    GDC_ANNOTATION_T *canno;

    if (!PyArg_ParseTuple(args, "O", &anno)){
        return NULL;
    }
    if (anno == Py_None){
        if (GDC_annotation)
            free(GDC_annotation);
        GDC_annotation = NULL;
    } else { 
        canno = malloc(sizeof(GDC_ANNOTATION_T));
        if (canno == NULL){
            PyErr_NoMemory();
            return NULL;
        }
        attr = PyObject_GetAttrString(anno, "point");
        if (attr == NULL)
            goto cleanup;
        aval = PyNumber_Float(attr);
        Py_DECREF(attr);
        if (aval == NULL){
            PyErr_SetString(PyExc_TypeError, "Point value must be representable as a float.");
            goto free;
        }
        canno->point = (float)PyFloat_AsDouble(aval);
        Py_DECREF(aval);

        attr = PyObject_GetAttrString(anno, "color");
        if (attr == NULL)
            goto cleanup;
        aval = PyNumber_Int(attr);
        Py_DECREF(attr);
        if (aval == NULL){
            PyErr_SetString(PyExc_TypeError, "Color value must be representable as a long.");
            goto free;
        }
        canno->color = PyInt_AsLong(aval);
        Py_DECREF(aval);

        attr = PyObject_GetAttrString(anno, "note");
        if (attr == NULL)
            goto cleanup;
        aval = PyObject_Str(attr);
        Py_DECREF(attr);
        if (aval == NULL){
            PyErr_SetString(PyExc_TypeError, "Note must be representable as a str.");
            goto free;
        }
        strncpy(canno->note, PyString_AsString(aval), MAX_NOTE_LEN+1);
        Py_DECREF(aval);

        if (GDC_annotation)
            free(GDC_annotation);
        GDC_annotation = canno;
    }
    Py_INCREF(Py_None);
    return Py_None;

cleanup:
        PyErr_SetString(PyExc_TypeError, "Object does not seem to be an annotation object.");
free:
        free(canno);
        return NULL;
}


static PyMethodDef methods[] = {
    {"out_graph",       pygd_out_graph,         METH_VARARGS,       "Output a graph."                   },
    {"out_pie",         pygd_out_pie,           METH_VARARGS,       "Output a pie."                     },
    {"getOptions",      getOptions,             METH_VARARGS,       "Retrieve all chart options."       },
    {"setOption",       setOption,              METH_VARARGS,       "Set an option."                    },
    {"setScatter",      pygd_set_scatter,       METH_VARARGS,       "Set scatter points."               },
    {"annotate",        pygd_annotate,          METH_VARARGS,       "Set an annotation point."          },
    { NULL,			                                                NULL                                }
};

void init_gdchartc(void){
    PyObject *module; 

    Py_AtExit(clearMempool);
    module = Py_InitModule4("_gdchartc", methods, NULL, NULL, PYTHON_API_VERSION);
    PGError = PyErr_NewException("_gdchartc.PGError", NULL, NULL);
    PyModule_AddObject(module, "PGError", PGError);

    /* Expose our option type identifiers. */
    PyModule_AddIntConstant(module, "OPT_BOOL",     (long) OPT_BOOL);     
    PyModule_AddIntConstant(module, "OPT_BOOL_A",   (long) OPT_BOOL_A);   
    PyModule_AddIntConstant(module, "OPT_COLOR",    (long) OPT_COLOR);     
    PyModule_AddIntConstant(module, "OPT_COLOR_A",  (long) OPT_COLOR_A);     
    PyModule_AddIntConstant(module, "OPT_FLOAT",    (long) OPT_FLOAT);    
    PyModule_AddIntConstant(module, "OPT_FONTSIZE", (long) OPT_FONTSIZE);     
    PyModule_AddIntConstant(module, "OPT_INT",      (long) OPT_INT);      
    PyModule_AddIntConstant(module, "OPT_INT_A",    (long) OPT_INT_A);    
    PyModule_AddIntConstant(module, "OPT_LONG",     (long) OPT_LONG);     
    PyModule_AddIntConstant(module, "OPT_SHORT",    (long) OPT_SHORT);    
    PyModule_AddIntConstant(module, "OPT_USHORT",   (long) OPT_USHORT);   
    PyModule_AddIntConstant(module, "OPT_PERCENT",  (long) OPT_PERCENT);  
    PyModule_AddIntConstant(module, "OPT_STRING",   (long) OPT_STRING);    
    PyModule_AddIntConstant(module, "OPT_UCHAR",    (long) OPT_UCHAR);     
    PyModule_AddIntConstant(module, "OPT_CHAR",     (long) OPT_CHAR);      

    /* Expose the chart type identifiers */
    PyModule_AddIntConstant(module, "GRAPH", (long) GRAPH);      
    PyModule_AddIntConstant(module, "PIE",   (long) PIE);      

    /*
         ************************
                  gdc.h
         ************************
     */
    /* Max annotation length: */
    PyModule_AddIntConstant(module, "MAX_NOTE_LEN",  (long)  MAX_NOTE_LEN);
    /* Image formats: */
    PyModule_AddIntConstant(module, "GDC_GIF",  (long)  GDC_GIF);
    PyModule_AddIntConstant(module, "GDC_JPEG", (long)  GDC_JPEG);
    PyModule_AddIntConstant(module, "GDC_PNG",  (long)  GDC_PNG);
    PyModule_AddIntConstant(module, "GDC_WBMP", (long)  GDC_WBMP);
    /* Font sizes: */
    PyModule_AddIntConstant(module, "GDC_TINY",     (long) GDC_TINY);
    PyModule_AddIntConstant(module, "GDC_SMALL",    (long) GDC_SMALL);
    PyModule_AddIntConstant(module, "GDC_MEDBOLD",  (long) GDC_MEDBOLD);
    PyModule_AddIntConstant(module, "GDC_LARGE",    (long) GDC_LARGE);
    PyModule_AddIntConstant(module, "GDC_GIANT",    (long) GDC_GIANT);
    /* Chart styles */
    PyModule_AddIntConstant(module, "GDC_LINE",             (long) GDC_LINE);
    PyModule_AddIntConstant(module, "GDC_AREA",             (long) GDC_AREA);
    PyModule_AddIntConstant(module, "GDC_BAR",              (long) GDC_BAR);
    PyModule_AddIntConstant(module, "GDC_FLOATINGBAR",      (long) GDC_FLOATINGBAR);
    PyModule_AddIntConstant(module, "GDC_HILOCLOSE",        (long) GDC_HILOCLOSE);
    PyModule_AddIntConstant(module, "GDC_COMBO_LINE_BAR",   (long) GDC_COMBO_LINE_BAR);
    PyModule_AddIntConstant(module, "GDC_COMBO_HLC_BAR",    (long) GDC_COMBO_HLC_BAR);
    PyModule_AddIntConstant(module, "GDC_COMBO_LINE_AREA",  (long) GDC_COMBO_LINE_AREA);
    PyModule_AddIntConstant(module, "GDC_COMBO_LINE_LINE",  (long) GDC_COMBO_LINE_LINE);
    PyModule_AddIntConstant(module, "GDC_COMBO_HLC_AREA",   (long) GDC_COMBO_HLC_AREA);
    PyModule_AddIntConstant(module, "GDC_3DHILOCLOSE",      (long) GDC_3DHILOCLOSE);
    PyModule_AddIntConstant(module, "GDC_3DCOMBO_LINE_BAR", (long) GDC_3DCOMBO_LINE_BAR);
    PyModule_AddIntConstant(module, "GDC_3DCOMBO_LINE_AREA",(long) GDC_3DCOMBO_LINE_AREA);
    PyModule_AddIntConstant(module, "GDC_3DCOMBO_LINE_LINE",(long) GDC_3DCOMBO_LINE_LINE);
    PyModule_AddIntConstant(module, "GDC_3DCOMBO_HLC_BAR",  (long) GDC_3DCOMBO_HLC_BAR);
    PyModule_AddIntConstant(module, "GDC_3DCOMBO_HLC_AREA", (long) GDC_3DCOMBO_HLC_AREA);
    PyModule_AddIntConstant(module, "GDC_3DBAR",            (long) GDC_3DBAR);
    PyModule_AddIntConstant(module, "GDC_3DFLOATINGBAR",    (long) GDC_3DFLOATINGBAR);
    PyModule_AddIntConstant(module, "GDC_3DAREA",           (long) GDC_3DAREA);
    PyModule_AddIntConstant(module, "GDC_3DLINE",           (long) GDC_3DLINE);
    /* Pie styles */
    PyModule_AddIntConstant(module, "GDC_3DPIE",            (long) GDC_3DPIE);
    PyModule_AddIntConstant(module, "GDC_2DPIE",            (long) GDC_2DPIE);

    /* TODO: Justification, font type, font size */
    /*   ************************
                  gdchart.h
         ************************
    */
    /*  Stack options: */
    PyModule_AddIntConstant(module, "GDC_STACK_DEPTH",          (long)  GDC_STACK_DEPTH);
    PyModule_AddIntConstant(module, "GDC_STACK_SUM",            (long)  GDC_STACK_SUM);
    PyModule_AddIntConstant(module, "GDC_STACK_BESIDE",         (long)  GDC_STACK_BESIDE);
    PyModule_AddIntConstant(module, "GDC_STACK_LAYER",          (long)  GDC_STACK_LAYER);
    /* Hi-lo-close styles: */
    PyModule_AddIntConstant(module, "GDC_HLC_DIAMOND",          (long)  GDC_HLC_DIAMOND);
    PyModule_AddIntConstant(module, "GDC_HLC_CLOSE_CONNECTED",  (long)  GDC_HLC_CLOSE_CONNECTED);
    PyModule_AddIntConstant(module, "GDC_HLC_CONNECTING",       (long)  GDC_HLC_CONNECTING);
    PyModule_AddIntConstant(module, "GDC_HLC_I_CAP",            (long)  GDC_HLC_I_CAP);
    /* Scatter point styles: */
    PyModule_AddIntConstant(module, "GDC_SCATTER_TRIANGLE_DOWN",    (long) GDC_SCATTER_TRIANGLE_DOWN);
    PyModule_AddIntConstant(module, "GDC_SCATTER_TRIANGLE_UP",      (long) GDC_SCATTER_TRIANGLE_UP);
    PyModule_AddIntConstant(module, "GDC_SCATTER_CIRCLE",           (long) GDC_SCATTER_CIRCLE);
    /* Tick styles: */
    PyModule_AddIntConstant(module, "GDC_TICK_LABELS",  (long) GDC_TICK_LABELS);
    PyModule_AddIntConstant(module, "GDC_TICK_POINTS",  (long) GDC_TICK_POINTS);
    PyModule_AddIntConstant(module, "GDC_TICK_NONE",    (long) GDC_TICK_NONE);
    /* Border styles: */
    PyModule_AddIntConstant(module, "GDC_BORDER_NONE",  (long) GDC_BORDER_NONE);
    PyModule_AddIntConstant(module, "GDC_BORDER_ALL",   (long) GDC_BORDER_ALL);
    PyModule_AddIntConstant(module, "GDC_BORDER_X",     (long) GDC_BORDER_X);
    PyModule_AddIntConstant(module, "GDC_BORDER_Y",     (long) GDC_BORDER_Y);
    PyModule_AddIntConstant(module, "GDC_BORDER_Y2",    (long) GDC_BORDER_Y2);
    PyModule_AddIntConstant(module, "GDC_BORDER_TOP",   (long) GDC_BORDER_TOP);
    /* Other magic: */
    AddFloatConstant(module, "GDC_INTERP_VALUE",        (double) GDC_INTERP_VALUE);

    /* ************************
                gdcpie.h
       ************************
    */
    /* Percent placement (pie charts): */
    PyModule_AddIntConstant(module, "GDCPIE_PCT_NONE",  (long) GDCPIE_PCT_NONE);
    PyModule_AddIntConstant(module, "GDCPIE_PCT_ABOVE", (long) GDCPIE_PCT_ABOVE);
    PyModule_AddIntConstant(module, "GDCPIE_PCT_BELOW", (long) GDCPIE_PCT_BELOW);
    PyModule_AddIntConstant(module, "GDCPIE_PCT_RIGHT", (long) GDCPIE_PCT_RIGHT);
    PyModule_AddIntConstant(module, "GDCPIE_PCT_LEFT",  (long) GDCPIE_PCT_LEFT);
}
