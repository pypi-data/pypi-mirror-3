/*
# Copyright (c) 2011 Tigr <tigr42@centrum.cz>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

/***************************************************************************
 *  _uuencoder.c
 *  
 *  This extension module provides SubStation UUencoding functions.
 *  See Appendix B of the SSA format specification for details.
 *  Roughly 50-100x times faster than Python implementation.
 */

#define PY_SSIZE_T_CLEAN
#include "Python.h"


static PyObject* bin2ascii( PyObject* self, PyObject* args )
{
    unsigned char *input, *output, *in_ptr, *out_ptr;
    unsigned char a, b, c;
    Py_ssize_t len;
    int encoded_char_cnt;
    PyObject* output_str;
    
    if( !PyArg_ParseTuple( args, "y#", &input, &len ) )
        return NULL;
    
    output = (unsigned char*) malloc( 2 * len );
    if( !output )   
        return PyErr_NoMemory();
    
    /***************************************************************************
     *  encode first mod3 bytes
     */
    
    for( in_ptr = input, out_ptr = output, encoded_char_cnt = 0;
         in_ptr < input + len - (len % 3);
         encoded_char_cnt++ )
    {
        /*    
            input   AAAA AAAA  BBBB BBBB  CCCC CCCC  [  N/A  ]
            output  00AA AAAA  00AA BBBB  00BB BBCC  00CC CCCC
            byte #    12 3456    78 1234    56 7812    34 5678
        */
        
        a = *(in_ptr++);
        b = *(in_ptr++);
        c = *(in_ptr++);
        
        *(out_ptr++) = 33 + (a >> 2);
        *(out_ptr++) = 33 + (((a << 4) | (b >> 4)) & 0x3f);
        *(out_ptr++) = 33 + (((b << 2) | (c >> 6)) & 0x3f);
        *(out_ptr++) = 33 + (c & 0x3f);
        
        if( encoded_char_cnt % 20 == 19 )
            *(out_ptr++) = '\n';                
    }
    
    /***************************************************************************
     *  handle non-mod3 filelengths
     */
    
    if( len % 3 == 1 ) {
        /*
            input   AAAA AAAA  [  N/A  ]
            output  00AA AAAA  00AA 0000
            byte #    12 3456    78
        */
        
        a = *in_ptr;
        
        *(out_ptr++) = 33 + (a >> 2);
        *(out_ptr++) = 33 + ((a << 4) & 0x3f);        
    }
    else if( len % 3 == 2) {
        /*
            input   AAAA AAAA  BBBB BBBB  [  N/A  ]
            output  00AA AAAA  00AA BBBB  00BB BB00
            byte #    12 3456    78 1234    56 78
        */
        
        a = *(in_ptr++);
        b = *in_ptr;
        
        *(out_ptr++) = 33 + (a >> 2);
        *(out_ptr++) = 33 + (((a << 4) | (b >> 4)) & 0x3f);
        *(out_ptr++) = 33 + ((b << 2) & 0x3f);
    }
    
    /***************************************************************************
     *  save output
     */
    
    *out_ptr = '\0';
    output_str = PyUnicode_FromString( (char*)output );
    free( output );
    return output_str;
}


static PyObject* ascii2bin( PyObject* self, PyObject* args ) {
    unsigned char *input, *output, *in_ptr, *out_ptr;
    unsigned char w[4], tmp;
    int i;
    Py_ssize_t len;
    PyObject *unicode_input, *input_bytes, *output_bytes;
    
    if( !PyArg_ParseTuple( args, "U", &unicode_input ) )
        return NULL;
    
    input_bytes = PyUnicode_AsASCIIString( unicode_input );
    if( !input_bytes )
        return NULL;
    
    if( !PyBytes_AsStringAndSize( input_bytes, (char**)&input, &len ) == -1 ) {
        Py_DECREF( input_bytes );
        return NULL;
    }
    
    output = (unsigned char*) malloc( len );
    if( !output ) {
        Py_DECREF( input_bytes );
        return PyErr_NoMemory();
    }
    
    /***************************************************************************
     *  decode first mod4 bytes
     */
    
    in_ptr = input;
    out_ptr = output;
    i = 0;
    
    while( *in_ptr != '\0' ) {
        tmp = (*in_ptr++) - 33;
        if( tmp > 0x3f )
            continue;
        
        w[i++] = tmp;
        
        if( i == 4 ) {
            /*
                byte #    12 3456    78 1234    56 7812    34 5678
                input   00AA AAAA  00AA BBBB  00BB BBCC  00CC CCCC
                output  AAAA AAAA  BBBB BBBB  CCCC CCCC  [  N/A  ]
            */
            
            i = 0;
            
            *(out_ptr++) = (w[0] << 2) | (w[1] >> 4);
            *(out_ptr++) = (w[1] << 4) | (w[2] >> 2);
            *(out_ptr++) = (w[2] << 6) | w[3];                        
        }        
    }
    
    Py_DECREF( input_bytes );
    
    /***************************************************************************
     *  handle non-mod4 inputs
     */
    
    if( i == 1 ) {
        PyErr_SetString( PyExc_ValueError, "malformed data (1 extra byte)" );
        return NULL;
    }
    else if( i == 2 ) {
        /*
            byte #    12 3456    78
            input   00AA AAAA  00AA 0000
            output  AAAA AAAA  [  N/A  ]
        */
        
        *(out_ptr++) = (w[0] << 2) | (w[1] >> 4);
    }
    else if( i == 3 ) {
        /*
            byte #    12 3456    78 1234    56 78
            input   00AA AAAA  00AA BBBB  00BB BB00
            output  AAAA AAAA  BBBB BBBB  [  N/A  ]
        */
        
        *(out_ptr++) = (w[0] << 2) | (w[1] >> 4);
        *(out_ptr++) = (w[1] << 4) | (w[2] >> 2);
    }
    
    /***************************************************************************
     *  save output
     */
    
    output_bytes = PyBytes_FromStringAndSize( (char*)output, out_ptr - output );
    if( !output_bytes )
        return NULL;
    
    free( output );
    return output_bytes;
}


static PyMethodDef uuencoder_methods[] = {
     { "bin2ascii", bin2ascii, METH_VARARGS, "SSA's uuencoder." },
     { "ascii2bin", ascii2bin, METH_VARARGS, "SSA's uudecoder." },
     { NULL, NULL, 0, NULL }
};


static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_uuencoder",
    NULL,
    0, /* size of module state struct */
    uuencoder_methods,
    NULL,
    NULL, /*traverse*/
    NULL, /*clear*/
    NULL
};

 
PyObject* PyInit__uuencoder() {
    PyObject* module = PyModule_Create( &moduledef );
    
    if( module == NULL )
        return NULL;
    
    return module;
}
