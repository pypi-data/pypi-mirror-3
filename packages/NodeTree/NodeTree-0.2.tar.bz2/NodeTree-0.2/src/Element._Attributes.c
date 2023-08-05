/*
    NodeTree - Pythonic XML Data Binding Package
    Copyright (C) 2010,2011 Arc Riley

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program; if not, see http://www.gnu.org/licenses
*/


#include "nodetree.h"


static char
tp_doc[] = "NodeTree Element._Attributes\n"
"\n"
"    This is a mapping of nodetree.Attribute to string value.\n"
"\n";

nodetree_Element_Attributes_Object*
nodetree_Element_Attributes_Create (nodetree_Element_Object* element) {
    nodetree_Element_Attributes_Object* self;

    // Inherit base type
    self = (nodetree_Element_Attributes_Object*)
           PyType_GenericNew(&nodetree_Element_Attributes_Type, NULL, NULL);

    if (!self)
      return NULL;

    // Store the element
    Py_INCREF(element);
    self->element = element;
    return self;
}


static nodetree_Element_Attributes_Object*
tp_new (PyTypeObject* type, PyObject* args, PyObject* kwds) {
    nodetree_Element_Attributes_Object* self;
    nodetree_Element_Object* element;

    // Ensure no keywords were given
    if (!_PyArg_NoKeywords("nodetree.Element._Attributes", kwds));

    // Parse just the name
    if (!PyArg_ParseTuple(args, "O!", &nodetree_Element_Type, &element)) {
        return NULL;
    }

    // Return self
    return nodetree_Element_Attributes_Create(element);
}


static void
tp_dealloc (nodetree_Element_Attributes_Object* self) {
    // Decref element
    Py_DECREF(self->element);

    // Dealloc base type
    PyObject_Del((PyObject*) self);
}


///////////////////////////////////////////////////////////////////////////////
// Sequence methods

static Py_ssize_t
sq_length (nodetree_Element_Attributes_Object* self) {
    Py_ssize_t length = 0;
    xmlAttribute* attr = ((xmlElement*) self->element->node)->attributes;

    // Walk attribute list to determine its length
    while (attr) {
        attr = (xmlAttribute*) attr->next;
        length++;
    }

    return length;
}


static int
sq_contains (nodetree_Element_Attributes_Object* self, PyObject* value) {
    PyObject* name;
    xmlAttr* attr;

    // Require value to be either a bytes or unicode object
    if (PyBytes_Check(value)) {
        // Use a bytes string verbatim as UTF-8 name
        Py_INCREF(value);
        name = value;
    }
    else if (PyUnicode_Check(value)) {
        // Encode unicode string as UTF-8 bytes object
        name = PyUnicode_AsUTF8String(value);
    }
    else {
        // Raise exception
        PyErr_SetString(PyExc_TypeError, "attribute must be a string");
        return -1;
    }

    // attr will be NULL if not found
    attr = xmlHasProp(self->element->node, PyBytes_AsString(name));

    Py_DECREF(name);
    return (attr != NULL);
}


///////////////////////////////////////////////////////////////////////////////
// Mapping methods

static PyObject*
mp_subscript (nodetree_Element_Attributes_Object* self, PyObject* key) {
    PyObject* name;
    PyObject* value;
    char* attr;

    // Require key to be either a bytes or unicode object
    if (PyBytes_Check(key)) {
        // Use a bytes string verbatim as UTF-8 name
        Py_INCREF(key);
        name = key;
    }
    else if (PyUnicode_Check(key)) {
        // Encode unicode string as UTF-8 bytes object
        name = PyUnicode_AsUTF8String(key);
    }
    else {
        // Raise exception
        PyErr_SetString(PyExc_TypeError, "attribute name must be a string");
        return NULL;
    }

    // attr will be NULL if not found
    attr = xmlGetProp(self->element->node, PyBytes_AsString(name));
    Py_DECREF(name);

    // Raise exception if not found
    if (!attr) {
        PyErr_SetString(PyExc_KeyError, "attribute not found");
        return NULL;
    }

    // Return value after freeing the return value from xmlGetProp
    value = PyUnicode_FromString(attr);
    xmlFree(attr);
    return value;
}


static int
mp_ass_subscript (nodetree_Element_Attributes_Object* self, PyObject* key,
                  PyObject* v) {
    PyObject* name;
    PyObject* value;
    xmlAttr* attr;
    xmlNode* node = self->element->node;
    nodetree_node* next = self->element->next;

    // Require key to be either a bytes or unicode object
    if (PyBytes_Check(key)) {
        // Use a bytes string verbatim as UTF-8 name
        Py_INCREF(key);
        name = key;
    }
    else if (PyUnicode_Check(key)) {
        // Encode unicode string as UTF-8 bytes object
        name = PyUnicode_AsUTF8String(key);
    }
    else {
        // Raise exception
        PyErr_SetString(PyExc_TypeError, "attribute name must be a string");
        return -1;
    }

    // If v == NULL then delete attribute
    if (!v) {
        /* Delete attribute from each of Element's nodes

            Element may have multiple copies of itself due to being added to
            multiple parents.  As a result, each copy will have its own
            attributes list, so we need to perform this deletion on each.
        */
        while (node) {
            // attr will be NULL if not found
            attr = xmlHasProp(node, PyBytes_AsString(name));

            // Ensure key exists
            if (!attr) {
                Py_DECREF(name);
                PyErr_SetString(PyExc_KeyError, "attribute not found");
                return -1;
            }

            // Try to remove it, return error if raised by libxml
            if (xmlRemoveProp(attr) == -1) {
                Py_DECREF(name);
                PyErr_SetString(PyExc_KeyError, "error deleting attribute");
                return -1;
            }

            // Get next node
            if (next) {
                node = next->node;
                next = next->next;
            }
            else
                node = NULL;
        }

        // Successfully deleted attribute
        Py_DECREF(name);
        return 0;
    }

    // Require value to be either a bytes or unicode object
    if (PyBytes_Check(v)) {
        // Use a bytes string verbatim as UTF-8 name
        Py_INCREF(v);
        value = v;
    }
    else if (PyUnicode_Check(v)) {
        // Encode unicode string as UTF-8 bytes object
        value = PyUnicode_AsUTF8String(v);
    }
    else {
        // Raise exception
        Py_DECREF(name);
        PyErr_SetString(PyExc_TypeError, "attribute value must be a string");
        return -1;
    }

    /* Change attribute from each of Element's nodes

        Element may have multiple copies of itself due to being added to
        multiple parents.  As a result, each copy will have its own
        attributes list, so we need to change each of their attributes.
    */
    while (node) {
        // Tell libxml to set the attribute
        attr = xmlSetProp(node, PyBytes_AsString(name),
                          PyBytes_AsString(value));

        // Return error if raised by libxml
        if (!attr) {
            Py_DECREF(name);
            Py_DECREF(value);
            PyErr_SetString(PyExc_ValueError, "invalid XML attribute");
            return -1;
        }

        // Get next node
        if (next) {
            node = next->node;
            next = next->next;
        }
        else
            node = NULL;
    }

    // Successfully assigned new value
    Py_DECREF(name);
    Py_DECREF(value);
    return 0;
}


///////////////////////////////////////////////////////////////////////////////
// Type structs

static PySequenceMethods tp_as_sequence = {
    (lenfunc) sq_length,                                   // sq_length
    0,                                                     // sq_concat
    0,                                                     // sq_repeat
    0,                                                     // sq_item
    0,                                                     // was_sq_slice
    0,                                                     // sq_ass_item
    0,                                                     // was_sq_ass_slice
    (objobjproc) sq_contains,                              // sq_contains
    0,                                                     // sq_inplace_concat
    0,                                                     // sq_inplace_repeat
};


static PyMappingMethods tp_as_mapping = {
    0,                                                     // mp_length
    (binaryfunc) mp_subscript,                             // mp_subscript
    (objobjargproc) mp_ass_subscript,                      // mp_ass_subscript
};


static PyMethodDef tp_methods[] = {
    {NULL},                                                // sentinel
};


static PyGetSetDef tp_getset[] = {
    {NULL},                                                // sentinel
};


PyTypeObject nodetree_Element_Attributes_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "nodetree.Element._Attributes",                        // tp_name
    sizeof(nodetree_Element_Attributes_Object),            // tp_basicsize
    0,                                                     // tp_itemsize
    (destructor) tp_dealloc,                               // tp_dealloc
    0,                                                     // RESERVED
    (getattrfunc) 0,                                       // tp_getattr
    (setattrfunc) 0,                                       // tp_setattr
    0,                                                     // RESERVED
    0,                                                     // tp_repr
    0,                                                     // tp_as_number
    &tp_as_sequence,                                       // tp_as_sequence
    &tp_as_mapping,                                        // tp_as_mapping
    0,                                                     // tp_hash
    0,                                                     // tp_call
    0,                                                     // tp_str
    (getattrofunc) 0,                                      // tp_getattro
    (setattrofunc) 0,                                      // tp_setattro
    0,                                                     // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,              // tp_flags
    tp_doc,                                                // tp_doc
    0,                                                     // tp_traverse
    0,                                                     // tp_clear
    0,                                                     // tp_richcompare
    0,                                                     // tp_weaklistoffset
    0,                                                     // tp_iter
    0,                                                     // tp_iternext
    tp_methods,                                            // tp_methods
    0,                                                     // tp_members
    tp_getset,                                             // tp_getset
    0,                                                     // tp_base
    0,                                                     // tp_dict
    0,                                                     // tp_descr_get
    0,                                                     // tp_descr_set
    0,                                                     // tp_dictoffset
    0,                                                     // tp_init
    0,                                                     // tp_alloc
    (newfunc) tp_new,                                      // tp_new
    0,                                                     // tp_free
    0,                                                     // tp_is_gc
};

