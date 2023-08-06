// Copyright 2012 Luis Pedro Coelho <luis@luispedro.org>
// License: MIT (see COPYING.MIT file)

#ifndef LPC_NUMPY_H_INCLUDE_GUARD_WED_FEB__1_16_34_50_WET_2012
#define LPC_NUMPY_H_INCLUDE_GUARD_WED_FEB__1_16_34_50_WET_2012
#include <memory>
#include "base.h"

extern "C" {
    #include <Python.h>
    #include <numpy/ndarrayobject.h>
}

class NumpyImage : public Image {
    public:
        NumpyImage(PyArrayObject* array = 0)
            :array_(array)
            { }

        ~NumpyImage() {
            Py_XDECREF(array_);
        }

        PyArrayObject* release() {
            PyArrayObject* r = array_;
            array_ = 0;
            return r;
        }

        PyObject* releasePyObject() {
            this->finalize();
            return reinterpret_cast<PyObject*>(this->release());
        }


        virtual int ndims() const {
            if (!array_) throw ProgrammingError();
            return PyArray_NDIM(array_);
        }
        virtual int dim(int d) const {
            if (!array_ || d >= this->ndims()) throw ProgrammingError();
            return PyArray_DIM(array_, d);
        }

        virtual void* rowp(int r) {
            if (!array_) throw ProgrammingError();
            if (r >= PyArray_DIM(array_, 0)) throw ProgrammingError();
            return PyArray_GETPTR1(array_, r);
        }
        void finalize();
        PyArrayObject* array_;
};

class NumpyFactory : public ImageFactory {
    protected:
        std::auto_ptr<Image> create(int nbits, int h, int w, int d) {
            npy_intp dims[3];
            dims[0] = h;
            dims[1] = w;
            dims[2] = d;
            const npy_intp nd = 2 + (d != -1);
            int dtype = -1;
            switch (nbits) {
                case 1: dtype = NPY_BOOL; break;
                case 8: dtype = NPY_UINT8; break;
                case 16: dtype = NPY_UINT16; break;
                case 32: dtype = NPY_UINT32; break;
                default:
                    throw ProgrammingError("Cannot handle this number of bits");
            }

            PyArrayObject* array = reinterpret_cast<PyArrayObject*>(PyArray_SimpleNew(nd, dims, dtype));
            if (!array) throw std::bad_alloc();
            try {
                return std::auto_ptr<Image>(new NumpyImage(array));
            } catch(...) {
                Py_DECREF(array);
                throw;
            }
        }
};

#endif // LPC_NUMPY_H_INCLUDE_GUARD_WED_FEB__1_16_34_50_WET_2012
