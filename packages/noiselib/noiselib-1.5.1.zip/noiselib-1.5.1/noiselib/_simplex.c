// Copyright (c) 2011, Chandler Armstrong (omni dot armstrong at gmail dot com)
// see LICENSE.txt for details



#include "Python.h"
#include <math.h>



// 2D simplex skew factors
#define F2 0.3660254037844386f  // 0.5 * (sqrt(3.0) - 1.0)
#define G2 0.21132486540518713f // (3.0 - sqrt(3.0)) / 6.0


// 3D simplex skew factors
#define F3 (1.0f / 3.0f)
#define G3 (1.0f / 6.0f)


// lambdas
#define LENOF(x) (sizeof (x) / sizeof (*(x)))
#define POWOFTWO(x) (x & (x - 1)) == 0


// gradient indices?
const float GRAD3[][3] = {
  {1,1,0},{-1,1,0},{1,-1,0},{-1,-1,0}, 
  {1,0,1},{-1,0,1},{1,0,-1},{-1,0,-1}, 
  {0,1,1},{0,-1,1},{0,1,-1},{0,-1,-1}
};


int *PERM; // permutation table
int N = 0; // size


// utility functions
float
dot(float *a, float *b) {
  int i;
  int n = LENOF(a);
  float total = 0.0;
  for (i = 0; i < n; i++) {
    total += a[i] * b[i];
  }
  return total;
}


// main functions
float
noise2(float x, float y) {
  // arguments (x, y) in a simplex-tiled space
  // skew (x, y) such that simplex tiles align with grid
  // in skewed (grid) space, find corners of simplex tile containing (x, y)
  // ???
  int c;            // for loop index
  int I_1, J_1;     // increments (0 or 1) to unknown (second) skewed corner
  float X[3], Y[3]; // coordinates of corners in unskewed (simplex) space
  int G[3];
  float noise[3] = {0.0f, 0.0f, 0.0f};
  // find first corner (i, j) in skewed (grid) space
  float s = (x + y) * F2;      // skew factor
  int i = (int) floorf(x + s); // first corner in skewed space
  int j = (int) floorf(y + s);
  // find first corner (x, y) in unskewed space
  float t = (i + j) * G2;      // unskew factor
  X[0] = x - (i - t);          // first corner in unskewed space
  Y[0] = y - (j - t);
  // find increments unknown corner
  // if first corner x > y, the input (x, y) is in lower triangle
  // else in upper triangle
  if (X[0] > Y[0]) { I_1 = 1; J_1 = 0; }
  else { I_1 = 0; J_1 = 1; }
  // find remaining corners in unskewed space
  X[1] = X[0] - I_1 + G2;
  Y[1] = Y[0] - J_1 + G2;
  X[2] = X[0] - 1.0f + (2.0f * G2);
  Y[2] = Y[0] - 1.0f + (2.0f * G2);

  i = i & (N - 1); // wrap coords to perm table size
  j = j & (N - 1);
  G[0] = PERM[i + PERM[j]] % 12;
  G[1] = PERM[i + I_1 + PERM[j + J_1]] % 12;
  G[2] = PERM[i + 1 + PERM[j + 1]] % 12;

  for (c = 0; c < 3; c++) {
    float a = 0.5f - X[c]*X[c] - Y[c]*Y[c];
    float C[2] = {X[c], Y[c]};
    if (a > 0) { noise[c] = a*a*a*a * dot(C, GRAD3[G[c]]); }
  }

  return (noise[0] + noise[1] + noise[2]) * 70.0f;
}


float
noise3(float x, float y, float z) {
  int c;
  int I_1, J_1, K_1, I_2, J_2, K_2;
  float X[4], Y[4], Z[4];
  int G[4];
  float noise[4] = {0.0f, 0.0f, 0.0f, 0.0f};

  float s = (x + y + z) * F3;
  int i = (int) floorf(x + s);
  int j = (int) floorf(y + s);
  int k = (int) floorf(z + s);

  float t = (i + j + k) * G3;
  X[0] = x - (i - t);
  Y[0] = y - (j - t);
  Z[0] = z - (k - t);

  if (X[0] >= Y[0]) {
    if (Y[0] >= Z[0]) {
      I_1 = 1; J_1 = 0; K_1 = 0;
      I_2 = 1; J_2 = 1; K_2 = 0;
    } else if (X[0] >= Z[0]) {
      I_1 = 1; J_1 = 0; K_1 = 0;
      I_2 = 1; J_2 = 0; K_2 = 1;
    } else {
      I_1 = 0; J_1 = 0; K_1 = 1;
      I_2 = 1; J_2 = 0; K_2 = 1;
    }
  } else {
    if (Y[0] < Z[0]) {
      I_1 = 0; J_1 = 0; K_1 = 1;
      I_2 = 0; J_2 = 1; K_2 = 1;
    } else if (X[0] < Z[0]) {
      I_1 = 0; J_1 = 1; K_1 = 0;
      I_2 = 0; J_2 = 1; K_2 = 1;
    } else {
      I_1 = 0; J_1 = 1; K_1 = 0;
      I_2 = 1; J_2 = 1; K_2 = 0;
    }
  }

  X[1] = X[0] - I_1 + G3;
  Y[1] = Y[0] - J_1 + G3;
  Z[1] = Z[0] - K_1 + G3;
  X[2] = X[0] - I_2 + (2.0f * G3);
  Y[2] = Y[0] - J_2 + (2.0f * G3);
  Z[2] = Z[0] - K_2 + (2.0f * G3);
  X[3] = X[0] - 1.0f + (3.0f * G3);
  Y[3] = Y[0] - 1.0f + (3.0f * G3);
  Z[3] = Z[0] - 1.0f + (3.0f * G3);

  i = i & (N - 1);
  j = j & (N - 1);
  k = k & (N - 1);
  G[0] = PERM[i + PERM[j + PERM[k]]] % 12;
  G[1] = PERM[i + I_1 + PERM[j + J_1 + PERM[k + K_1]]] % 12;
  G[2] = PERM[i + I_2 + PERM[j + J_2 + PERM[k + K_2]]] % 12;
  G[3] = PERM[i + 1 + PERM[j + 1 + PERM[k + 1]]] % 12; 

  for (c = 0; c < 4; c++) {
    float a = 0.6f - X[c]*X[c] - Y[c]*Y[c] - Z[c]*Z[c];
    float C[3] = {X[c], Y[c], Z[c]};
    if (a > 0) { noise[c] = a*a*a*a * dot(C, GRAD3[G[c]]); }
  }

  return (noise[0] + noise[1] + noise[2] + noise[3]) * 32.0f;
}


static PyObject *
py_set_perm(PyObject *self, PyObject *args) {
  int i;
  PyObject *seq;

  if (!PyArg_ParseTuple(args, "O:set_perm", &seq)) { return NULL; }
  seq = PySequence_Fast(seq, "argument must be iterable");
  if (!seq) { return NULL; }

  N = PySequence_Fast_GET_SIZE(seq);
  if (!(POWOFTWO(N))) {
      PyErr_SetString(PyExc_ValueError,
		      "permutation table length must be a "
		      "power of two");
      Py_DECREF(seq);
      return NULL;
    }

  PERM = malloc(N * sizeof(int));
  if (!PERM) {
    Py_DECREF(seq);
    return PyErr_NoMemory();
  }

  for(i = 0; i < N; i++) {
    PyObject *int_item;
    PyObject *item = PySequence_Fast_GET_ITEM(seq, i);

    if(!item) {
      Py_DECREF(seq);
      free(PERM);
      return NULL;
    }

    int_item = PyNumber_Int(item);
    if(!int_item) {
      Py_DECREF(seq);
      free(PERM);
      PyErr_SetString(PyExc_TypeError, "all items must be numbers");
      return NULL;
    }

    PERM[i] = PyInt_AS_LONG(int_item);
    Py_DECREF(int_item);
  }

  N /= 2; // permuation table is doubled only for indexing purposes

  Py_DECREF(seq);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject *
py_noise2(PyObject *self, PyObject *args) {
  float x, y;

  if (!N) {
    PyErr_SetString(PyExc_ValueError,
		    "permutation table must initialized first.  call "
		    "noiselib.init(p), where p is the period or "
		    "permutation table");
    return NULL;
  }

  if (!PyArg_ParseTuple(args, "(ff):noise2", &x, &y))
    return NULL;
  return (PyObject *) PyFloat_FromDouble((double) noise2(x, y));
}


static PyObject *
py_noise3(PyObject *self, PyObject *args) {
  float x, y, z;

  if (!N) {
    PyErr_SetString(PyExc_ValueError,
		    "permutation table must initialized first.  call "
		    "noiselib.init(p), where p is the period or "
		    "permutation table");
    return NULL;
  }

  if (!PyArg_ParseTuple(args, "(fff):noise3", &x, &y, &z))
    return NULL;
  return (PyObject *) PyFloat_FromDouble((double) noise3(x, y, z));
}


static PyMethodDef simplex_functions[] = {
  {"set_perm", py_set_perm, METH_VARARGS,
   "set_perm(n) set permuation table of length n\n\n"},
  {"noise2", py_noise2, METH_VARARGS, 
   "noise2(x, y) return simplex noise value for specified coordinate.\n\n"},
  {"noise3", py_noise3, METH_VARARGS, 
   "noise3(x, y, z) return simplex noise value for specified coordinate\n\n"},
  {NULL}
};


PyMODINIT_FUNC
init_simplex(void) {
  PyObject *m;
  m = Py_InitModule3("_simplex", simplex_functions, "Native-code simplex noise functions");
}
