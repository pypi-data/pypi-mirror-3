#include <stdio.h>
#include <Python.h>

#define MOD_ADLER 4294967291ULL

static PyObject* func_adler64(PyObject *self, PyObject *args)
{
  PyObject *retval = NULL;
  char *buffer = NULL;
  int bufsize;
  unsigned long long elem, a = 1, b = 0;
  int begin, end, i;

  if(!PyArg_ParseTuple(args, "t#ii|KK", &buffer, &bufsize, &begin, &end, &a, &b)) {
    PyErr_SetString(PyExc_SystemError, "Wrong arguments.");
    goto out;
  }
  for (i = begin; i < end; ++i) {
    elem = buffer[i];
    a = (elem + a) % MOD_ADLER;
    b = (b + a) % MOD_ADLER;
  }
  retval = Py_BuildValue("(KKK)", (b << 32) | a, a, b);
out:
  return retval;
}

static PyObject* func_adler64rol(PyObject *self, PyObject *args)
{
  unsigned long removed, new, blocksize = 4096;
  unsigned long long a, b;

  if (!PyArg_ParseTuple(args, "kkKK|k", &removed, &new, &a, &b, &blocksize)) {
    PyErr_SetString(PyExc_SystemError, "Wrong arguments.");
    return NULL;
  }
  a = (a - removed + new) % MOD_ADLER;
  b = (b - removed * blocksize - 1 + a) % MOD_ADLER;
  return Py_BuildValue("(KKK)", (b << 32) | a, a, b);
}

static PyObject* func_adler64search(PyObject *self, PyObject *args)
{
  PyObject *is_exists_func, *is_exists_dict;
  PyObject *retval = NULL;
  unsigned long long firstcks, checksum, a = 1, b = 0;
  int enew, eold, elem;
  int end, i, d = 0, blocksize = 4096;
  int bufsize = 0;
  char *dest = NULL;
  char *buffer = NULL;

  if (!PyArg_ParseTuple(args, "OOt#|i", &is_exists_dict, &is_exists_func, &buffer, &bufsize, &blocksize)) {
    PyErr_SetString(PyExc_SystemError, "Wrong arguments.");
    goto out;
  }
  if (bufsize < blocksize) {
    PyErr_SetString(PyExc_SystemError, "Buffer need to be larger then block size.");
    goto out;
  }
  dest = (char*) malloc (blocksize + 1);
  end = bufsize - blocksize;
  for (i = 0; i < blocksize; ++i) {
    elem = buffer[i];
    a = (elem + a) % MOD_ADLER;
    b = (b + a) % MOD_ADLER;
  }
  firstcks = checksum = (b <<  32) | a;
  for (i = 0; i < end; ++i) {
    PyObject *num = PyLong_FromUnsignedLongLong(checksum);
    if (PyMapping_HasKey(is_exists_dict, num)) {
      Py_XDECREF(num);
      retval = PyObject_CallFunction(is_exists_func, "s#iiK", buffer, bufsize, i, i + blocksize, checksum);
      if (retval == NULL) PyErr_Print();
      else if (retval == Py_True) {
	Py_XDECREF(retval);
	retval = Py_BuildValue("(Ois#KK)", Py_True, i, dest, d, firstcks, checksum);
	goto out;
      }
    } else {
      Py_XDECREF(num);
    }
    enew = buffer[i + blocksize];
    eold = buffer[i];
    dest[d++] = eold;
    a = (a - eold + enew) % MOD_ADLER;
    b = (b - eold * blocksize - 1 + a) % MOD_ADLER;
    checksum = (b << 32) | a;
  }
  retval = Py_BuildValue("(Ois#KK)", Py_False, end, dest, d, firstcks, 0ULL);
out:
  if (dest != NULL) free(dest);
  return retval;
}

static PyMethodDef adler64[] = {
  {"calculate", func_adler64, METH_VARARGS, "Calculate Adler-64 checksum."},
  {"roll", func_adler64rol, METH_VARARGS, "Calculate rolling Adler-64 checksum."},
  {"search", func_adler64search, METH_VARARGS, "Search data in buffer."},
  {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initadler64(void)
{
  (void) Py_InitModule("adler64", adler64);
}
