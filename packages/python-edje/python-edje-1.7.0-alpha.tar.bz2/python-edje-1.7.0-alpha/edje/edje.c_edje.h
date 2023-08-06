#ifndef __PYX_HAVE__edje__c_edje
#define __PYX_HAVE__edje__c_edje

struct PyEdje;

/* "edje/c_edje.pxd":446
 * 
 * 
 * cdef public class Edje(evas.c_evas.Object) [object PyEdje, type PyEdje_Type]:             # <<<<<<<<<<<<<<
 *     cdef object _text_change_cb
 *     cdef object _message_handler_cb
 */
struct PyEdje {
  struct PyEvasObject __pyx_base;
  PyObject *_text_change_cb;
  PyObject *_message_handler_cb;
  PyObject *_signal_callbacks;
};

#ifndef __PYX_HAVE_API__edje__c_edje

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEdje_Type;

#endif /* !__PYX_HAVE_API__edje__c_edje */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initc_edje(void);
#else
PyMODINIT_FUNC PyInit_c_edje(void);
#endif

#endif /* !__PYX_HAVE__edje__c_edje */
