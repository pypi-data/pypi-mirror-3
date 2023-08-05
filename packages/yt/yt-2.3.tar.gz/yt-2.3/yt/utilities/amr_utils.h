#ifndef __PYX_HAVE__yt__utilities__amr_utils
#define __PYX_HAVE__yt__utilities__amr_utils

struct mem_encode;

/* "/home/mturk/yt/yt-dist/yt/utilities/_amr_utils/png_writer.pyx":223
 * # http://stackoverflow.com/questions/1821806/how-to-encode-png-to-buffer-using-libpng
 * 
 * cdef public struct mem_encode:             # <<<<<<<<<<<<<<
 *     char *buffer
 *     size_t size
 */
struct mem_encode {
  char *buffer;
  size_t size;
};

#ifndef __PYX_HAVE_API__yt__utilities__amr_utils

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

__PYX_EXTERN_C DL_IMPORT(void) my_png_write_data(png_structp, png_bytep, size_t);
__PYX_EXTERN_C DL_IMPORT(void) my_png_flush(png_structp);

#endif /* !__PYX_HAVE_API__yt__utilities__amr_utils */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initamr_utils(void);
#else
PyMODINIT_FUNC PyInit_amr_utils(void);
#endif

#endif /* !__PYX_HAVE__yt__utilities__amr_utils */
