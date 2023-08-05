cdef extern from "stdlib.h":
  void free(void *)

cdef extern from "H5Zlzo.h":
  int register_lzo(char **, char **)

def register_():
  cdef char *version, *date

  if not register_lzo(&version, &date):
    return None

  compinfo = (version, date)
  free(version)
  free(date)
  return compinfo
