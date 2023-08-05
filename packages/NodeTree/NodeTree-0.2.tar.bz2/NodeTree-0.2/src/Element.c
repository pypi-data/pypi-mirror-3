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
tp_doc[] = "NodeTree Element\n"
"\n"
"    Each Element represents an XML element containing zero or more child\n"
"    nodes.  A node may be another instance of nodetree.Element, a string,\n"
"    or any object which can produce a valid XML string.\n"
"\n"
"    You may pass an XML string containing one root element (and zero or\n"
"    more child nodes) to parse.  The new Element object will be populated\n"
"    with as much complete data as can be parsed, additional data may be fed\n"
"    to the Element object as it becomes available.  Any callbacks provided\n"
"    via a subclass will be triggered while parsing the initial string.\n"
"\n"
"    The .name property holds the Element's name.\n"
"    The .attributes member is a mapping of Element attributes.\n"
"\n"
"    I haven't determined how to handle namespaces yet.\n"
"\n";

nodetree_Element_Object*
nodetree_Element_Create (xmlNode* node) {
    nodetree_Element_Object* self;

    // Inherit base type
    self = (nodetree_Element_Object*) PyType_GenericNew(&nodetree_Element_Type,
                                                        NULL, NULL);
    if (!self)
      return NULL;

    // Link XML node to this object
    self->node = node;
    self->next = NULL;

    // Link new object to XML node
    self->node->_private = self;

    return self;
}

static nodetree_Element_Object*
tp_new (PyTypeObject* type, PyObject* args, PyObject* kwds) {
    char* name;
    xmlNode* node;
    nodetree_Element_Object* self;

    // Ensure no keywords were given
    if (!_PyArg_NoKeywords("nodetree.Element", kwds));

    // Parse just the name
    if (!PyArg_ParseTuple(args, "z", &name)) {
        return NULL;
    }

    // Create new XML node
    node = xmlNewNode(NULL, name);

    // Create new Python object, free node on failure
    self = nodetree_Element_Create(node);
    if (!self)
        xmlFreeNode(node);

    // Python will free name, just return self
    return self;
}


static void
tp_dealloc (nodetree_Element_Object* self) {
    nodetree_node* next;

    self->node->_private = NULL;

    // Prune primary node if orphan
    if (!self->node->parent)
        nodetree_node_Prune(self->node);

    while (self->next) {
        next = self->next;
        next->node->_private = NULL;

        // Prune node if orphan
        if (!next->node->parent)
            nodetree_node_Prune(next->node);

        self->next = next->next;
        free(next);
    }

    // Dealloc base type
    PyObject_Del((PyObject*) self);
}


static PyObject*
tp_repr (nodetree_Element_Object* self) {
    xmlBuffer* buffer;
    PyObject* ret;

    // Create new XML buffer
    buffer = xmlBufferCreate();

    // Dump XML for element to a string
    xmlNodeDump(buffer, NULL, self->node, 0, 1);

    // Convert the returned XML string to a Python return string
    ret = PyUnicode_FromStringAndSize(buffer->content, buffer->use);

    // Free buffer and return string
    xmlBufferFree(buffer);
    return ret;
}


static PyObject*
tp_str (nodetree_Element_Object* self) {
    xmlBuffer* buffer;
    PyObject* ret;

    // Create new XML buffer
    buffer = xmlBufferCreate();

    // Dump XML for element to a string
    xmlNodeDump(buffer, NULL, self->node, 0, 0);

    // Convert the returned XML string to a Python return string
    ret = PyUnicode_FromStringAndSize(buffer->content, buffer->use);

    // Free buffer and return string
    xmlBufferFree(buffer);
    return ret;
}


///////////////////////////////////////////////////////////////////////////////
// Sequence methods

static Py_ssize_t
sq_length (nodetree_Element_Object* self) {
    // Use child node counter
    return (Py_ssize_t) nodetree_node_Child_Count((xmlNode*) self->node);
}


static PyObject*
sq_item(nodetree_Element_Object* self, Py_ssize_t index) {
    // Use child node getter
    return nodetree_node_Child_Get(self->node, (int) index);
}


static int
sq_ass_item (nodetree_Element_Object* self, Py_ssize_t index,
             PyObject* value) {
    xmlNode* node = self->node;
    nodetree_node* next = self->next;

    // Add a copy of the child to every copy of our own node to keep in sync
    while (node) {
        /* Use child node setter.

            If this fails it should always fail on the first pass.
        */
        if (nodetree_node_Child_Set(node, (int) index, value) == -1)
            return -1;

        // Get next node
        if (next) {
            node = next->node;
            next = next->next;
        }
        else
            node = NULL;
    }
}


static int
sq_contains (nodetree_Element_Object* self, PyObject* value) {
    return 0;
}


///////////////////////////////////////////////////////////////////////////////
// Sequence methods

static PyObject*
append (nodetree_Element_Object* self, PyObject* args) {
    PyObject* item;
    xmlNode* child;
    xmlNode* node = self->node;
    nodetree_node* next = self->next;

    // Parse item as single argument
    if (!PyArg_ParseTuple(args, "O", &item)) {
        return NULL;
    }

    // Add a copy of the child to every copy of our own node to keep in sync
    while (node) {
        // Get new child node
        child = nodetree_node_Py2XML(item);

        // Return exception NULL was returned by nodetree_node_Py2XML
        if (!child)
            return NULL;

        // Add child to end of children list
        child = xmlAddChild(node, child);

        // Raise exception if this fails for some reason
        if (!child) {
            PyErr_SetString(PyExc_ValueError, "error appending child");
            return NULL;
        }

        // Get next node
        if (next) {
            node = next->node;
            next = next->next;
        }
        else
            node = NULL;
    }

    // Returns None on success
    Py_RETURN_NONE;
}


/////////////////////////////////////////////////////////////////////////////
// Properties

static PyObject*
nodetree_Element_attributes_getter (nodetree_Element_Object* self,
                                    void* closure) {
    return PyObject_CallMethod((PyObject*) self, "_Attributes", NULL);
}


static PyObject*
nodetree_Element_name_getter (nodetree_Element_Object* self, void* closure) {
    return PyUnicode_FromString(self->node->name);
}


static int
nodetree_Element_name_setter (nodetree_Element_Object* self,
                              PyObject* value, void* closure) {
    PyObject* bytes;
    xmlChar* string;
    xmlNode* node = self->node;
    nodetree_node* next = self->next;

    if (value == NULL) {
        PyErr_SetString(PyExc_AttributeError, "cannot delete name attribute");
        return -1;
    }

    // Require key to be either a bytes or unicode object
    if (PyBytes_Check(value)) {
        // Use a bytes string verbatim as UTF-8 name
        Py_INCREF(value);
        bytes = value;
    }
    else if (PyUnicode_Check(value)) {
        // Encode unicode string as UTF-8 bytes object
        bytes = PyUnicode_AsUTF8String(value);
    }
    else {
        // Raise exception
        PyErr_SetString(PyExc_TypeError, "name attribute must be a string");
        return -1;
    }

    /* Update name of each node

        Remember, Element nodes may belong to many parents and for each there's
        a copy of itself held in a linked list.  Each must be updated.
    */
    while (1) {
        // libxml2 will do the right thing
        xmlNodeSetName(node, PyBytes_AsString(bytes));

        // End loop if this is the last node
        if (!next)
            break;

        // Get next node
        node = next->node;
        next = next->next;
    }

    // Success
    return 0;
}


///////////////////////////////////////////////////////////////////////////////
// Type structs

static PySequenceMethods tp_as_sequence = {
    (lenfunc) sq_length,                                   // sq_length
    0,                                                     // sq_concat
    0,                                                     // sq_repeat
    (ssizeargfunc) sq_item,                                // sq_item
    0,                                                     // was_sq_slice
    (ssizeobjargproc) sq_ass_item,                         // sq_ass_item
    0,                                                     // was_sq_ass_slice
    (objobjproc) sq_contains,                              // sq_contains
    0,                                                     // sq_inplace_concat
    0,                                                     // sq_inplace_repeat
};


static PyMethodDef tp_methods[] = {
    {"_Attributes", // FIXME this doesn't belong here      // ml_name
     (PyCFunction) nodetree_Element_Attributes_Create,     // ml_meth
     METH_NOARGS,                                          // ml_flags
     "Type for .attributes"},                              // ml_doc
    {"append",                                             // ml_name
     (PyCFunction) append,                                 // ml_meth
     METH_VARARGS,                                         // ml_flags
     "append node to end"},                                // ml_doc
    {NULL},                                                // sentinel
};


static PyGetSetDef tp_getset[] = {
    {"attributes",
     (getter) nodetree_Element_attributes_getter,
     NULL,
     "Element attributes",
     NULL},
    {"name",
     (getter) nodetree_Element_name_getter,
     (setter) nodetree_Element_name_setter,
     "Element name",
     NULL},
    {NULL},                                                 // sentinel
};


PyTypeObject nodetree_Element_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "nodetree.Element",                                     // tp_name
    sizeof(nodetree_Element_Object),                        // tp_basicsize
    0,                                                      // tp_itemsize
    (destructor) tp_dealloc,                                // tp_dealloc
    0,                                                      // RESERVED
    (getattrfunc) 0,                                        // tp_getattr
    (setattrfunc) 0,                                        // tp_setattr
    0,                                                      // RESERVED
    (reprfunc) tp_repr,                                     // tp_repr
    0,                                                      // tp_as_number
    &tp_as_sequence,                                        // tp_as_sequence
    0,                                                      // tp_as_mapping
    0,                                                      // tp_hash
    0,                                                      // tp_call
    (reprfunc) tp_str,                                      // tp_str
    (getattrofunc) 0,                                       // tp_getattro
    (setattrofunc) 0,                                       // tp_setattro
    0,                                                      // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,               // tp_flags
    tp_doc,                                                 // tp_doc
    0,                                                      // tp_traverse
    0,                                                      // tp_clear
    0,                                                      // tp_richcompare
    0,                                                      // tp_weaklistoffset
    0,                                                      // tp_iter
    0,                                                      // tp_iternext
    tp_methods,                                             // tp_methods
    0,                                                      // tp_members
    tp_getset,                                              // tp_getset
    0,                                                      // tp_base
    0,                                                      // tp_dict
    0,                                                      // tp_descr_get
    0,                                                      // tp_descr_set
    0,                                                      // tp_dictoffset
    0,                                                      // tp_init
    0,                                                      // tp_alloc
    (newfunc) tp_new,                                       // tp_new
    0,                                                      // tp_free
    0,                                                      // tp_is_gc
};

