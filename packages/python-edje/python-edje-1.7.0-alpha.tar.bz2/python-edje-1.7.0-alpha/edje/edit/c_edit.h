#ifndef __PYX_HAVE__edje__edit__c_edit
#define __PYX_HAVE__edje__edit__c_edit

struct PyEdjeEdit;

/* "edje/edit/c_edit.pxd":340
 * 
 * 
 * cdef public class EdjeEdit(edje.c_edje.Edje) [object PyEdjeEdit, type PyEdjeEdit_Type]:             # <<<<<<<<<<<<<<
 *     pass
 * #    cdef object _text_change_cb
 */
struct PyEdjeEdit {
  struct PyEdje __pyx_base;
};

#ifndef __PYX_HAVE_API__edje__edit__c_edit

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyEdjeEdit_Type;

#endif /* !__PYX_HAVE_API__edje__edit__c_edit */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initc_edit(void);
#else
PyMODINIT_FUNC PyInit_c_edit(void);
#endif

#endif /* !__PYX_HAVE__edje__edit__c_edit */
