#ifndef __PYX_HAVE__evas__c_evas
#define __PYX_HAVE__evas__c_evas

struct PyEvasRect;
struct PyEvasCanvas;
struct PyEvasObject;
struct PyEvasSmartObject;
struct PyEvasRectangle;
struct PyEvasLine;
struct PyEvasImage;
struct PyEvasFilledImage;
struct PyEvasPolygon;
struct PyEvasText;
struct PyEvasTextblock;
struct PyEvasClippedSmartObject;
struct PyEvasMap;
struct PyEvasBox;

/* "evas/c_evas.pxd":952
 * 
 * 
 * cdef public class Rect [object PyEvasRect, type PyEvasRect_Type]:             # <<<<<<<<<<<<<<
 *     cdef int x0, y0, x1, y1, cx, cy, _w, _h
 * 
 */
struct PyEvasRect {
  PyObject_HEAD
  int x0;
  int y0;
  int x1;
  int y1;
  int cx;
  int cy;
  int _w;
  int _h;
};

/* "evas/c_evas.pxd":1102
 * 
 * 
 * cdef public class Canvas [object PyEvasCanvas, type PyEvasCanvas_Type]:             # <<<<<<<<<<<<<<
 *     cdef Evas *obj
 *     cdef object _callbacks
 */
struct PyEvasCanvas {
  PyObject_HEAD
  struct __pyx_vtabstruct_4evas_6c_evas_Canvas *__pyx_vtab;
  Evas *obj;
  PyObject *_callbacks;
};

/* "evas/c_evas.pxd":1110
 * 
 * 
 * cdef public class Object [object PyEvasObject, type PyEvasObject_Type]:             # <<<<<<<<<<<<<<
 *     cdef Evas_Object *obj
 *     cdef readonly Canvas evas
 */
struct PyEvasObject {
  PyObject_HEAD
  struct __pyx_vtabstruct_4evas_6c_evas_Object *__pyx_vtab;
  Evas_Object *obj;
  struct PyEvasCanvas *evas;
  PyObject *data;
  PyObject *_callbacks;
};

/* "evas/c_evas.pxd":1120
 * 
 * 
 * cdef public class SmartObject(Object) [object PyEvasSmartObject,             # <<<<<<<<<<<<<<
 *                                        type PyEvasSmartObject_Type]:
 *     cdef object _smart_callbacks
 */
struct PyEvasSmartObject {
  struct PyEvasObject __pyx_base;
  PyObject *_smart_callbacks;
  PyObject *_m_delete;
  PyObject *_m_move;
  PyObject *_m_resize;
  PyObject *_m_show;
  PyObject *_m_hide;
  PyObject *_m_color_set;
  PyObject *_m_clip_set;
  PyObject *_m_clip_unset;
  PyObject *_m_calculate;
};

/* "evas/c_evas.pxd":1134
 * 
 * 
 * cdef public class Rectangle(Object) [object PyEvasRectangle,             # <<<<<<<<<<<<<<
 *                                      type PyEvasRectangle_Type]:
 *     pass
 */
struct PyEvasRectangle {
  struct PyEvasObject __pyx_base;
};

/* "evas/c_evas.pxd":1139
 * 
 * 
 * cdef public class Line(Object) [object PyEvasLine, type PyEvasLine_Type]:             # <<<<<<<<<<<<<<
 *     pass
 * 
 */
struct PyEvasLine {
  struct PyEvasObject __pyx_base;
};

/* "evas/c_evas.pxd":1143
 * 
 * 
 * cdef public class Image(Object) [object PyEvasImage, type PyEvasImage_Type]:             # <<<<<<<<<<<<<<
 *     pass
 * 
 */
struct PyEvasImage {
  struct PyEvasObject __pyx_base;
};

/* "evas/c_evas.pxd":1147
 * 
 * 
 * cdef public class FilledImage(Image) [object PyEvasFilledImage,             # <<<<<<<<<<<<<<
 *                                       type PyEvasFilledImage_Type]:
 *     pass
 */
struct PyEvasFilledImage {
  struct PyEvasImage __pyx_base;
};

/* "evas/c_evas.pxd":1152
 * 
 * 
 * cdef public class Polygon(Object) [object PyEvasPolygon,             # <<<<<<<<<<<<<<
 *                                    type PyEvasPolygon_Type]:
 *     pass
 */
struct PyEvasPolygon {
  struct PyEvasObject __pyx_base;
};

/* "evas/c_evas.pxd":1157
 * 
 * 
 * cdef public class Text(Object) [object PyEvasText, type PyEvasText_Type]:             # <<<<<<<<<<<<<<
 *     pass
 * 
 */
struct PyEvasText {
  struct PyEvasObject __pyx_base;
};

/* "evas/c_evas.pxd":1160
 *     pass
 * 
 * cdef public class Textblock(Object) [object PyEvasTextblock, type PyEvasTextblock_Type]:             # <<<<<<<<<<<<<<
 *     pass
 * 
 */
struct PyEvasTextblock {
  struct PyEvasObject __pyx_base;
};

/* "evas/c_evas.pxd":1164
 * 
 * 
 * cdef public class ClippedSmartObject(SmartObject) \             # <<<<<<<<<<<<<<
 *          [object PyEvasClippedSmartObject, type PyEvasClippedSmartObject_Type]:
 *     cdef readonly Rectangle clipper
 */
struct PyEvasClippedSmartObject {
  struct PyEvasSmartObject __pyx_base;
  struct PyEvasRectangle *clipper;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-evas/evas/evas.c_evas_map.pxi":22
 * 
 * 
 * cdef public class Map(object) [object PyEvasMap, type PyEvasMap_Type]:             # <<<<<<<<<<<<<<
 *     cdef Evas_Map *map
 * 
 */
struct PyEvasMap {
  PyObject_HEAD
  Evas_Map *map;
};
struct PyEvasBox {
  struct PyEvasObject __pyx_base;
};

#ifndef __PYX_HAVE_API__evas__c_evas

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasRect_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasCanvas_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasObject_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasSmartObject_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasRectangle_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasLine_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasImage_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasFilledImage_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasPolygon_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasText_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasTextblock_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasClippedSmartObject_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasMap_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEvasBox_Type;

#endif /* !__PYX_HAVE_API__evas__c_evas */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initc_evas(void);
#else
PyMODINIT_FUNC PyInit_c_evas(void);
#endif

#endif /* !__PYX_HAVE__evas__c_evas */
