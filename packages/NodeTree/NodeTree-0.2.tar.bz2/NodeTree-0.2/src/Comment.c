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
tp_doc[] = "NodeTree Comment\n"
"\n"
"    Comment nodes contain information useful to a human reading an XML\n"
"    document but are not generally intended for processing.\n"
"\n"
"    They have no methods or properties, their content is set on creation\n"
"    and can be retreived by str(comment) like any other node.  Note that\n"
"    their content is prefixed with \"<!--\" and affixed with \"-->\".\n"
"\n";


PyObject*
nodetree_Comment_Create (xmlNode* node) {
    nodetree_Comment_Object* self;

    // Inherit base type
    self = (nodetree_Comment_Object*) PyType_GenericNew(&nodetree_Comment_Type,
                                                        NULL, NULL);
    if (!self)
      return NULL;

    // Link XML node to this object
    self->node = node;
    self->next = NULL;

    // Link new object to XML node
    self->node->_private = self;

    return (PyObject*) self;
}


static PyObject*
tp_new (PyTypeObject* type, PyObject* args, PyObject* kwds) {
    PyObject* self;
    char* content;
    xmlNode* node;

    // Ensure no keywords were given
    if (!_PyArg_NoKeywords("nodetree.Comment", kwds));

    // Parse just the content
    if (!PyArg_ParseTuple(args, "z", &content)) {
        return NULL;
    }

    // Create new XML node
    node = xmlNewComment(content);

    // Create new Python object, free node on failure
    self = nodetree_Comment_Create(node);
    if (!self)
        xmlFreeNode(node);

    // Python will free name, just return self
    return self;
}


static void
tp_dealloc (nodetree_Comment_Object* self) {
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
tp_repr (nodetree_Comment_Object* self) {
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
tp_str (nodetree_Comment_Object* self) {
    xmlBuffer* buffer;
    PyObject* ret;

    // Create new XML buffer
    buffer = xmlBufferCreate();

    // Dump XML for Comment to a string
    xmlNodeDump(buffer, NULL, self->node, 0, 0);

    // Convert the returned XML string to a Python return string
    ret = PyUnicode_FromStringAndSize(buffer->content, buffer->use);

    // Free buffer and return string
    xmlBufferFree(buffer);
    return ret;
}


///////////////////////////////////////////////////////////////////////////////
// Type structs

PyTypeObject nodetree_Comment_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "nodetree.Comment",                                    // tp_name
    sizeof(nodetree_Comment_Object),                       // tp_basicsize
    0,                                                     // tp_itemsize
    (destructor) tp_dealloc,                               // tp_dealloc
    0,                                                     // RESERVED
    (getattrfunc) 0,                                       // tp_getattr
    (setattrfunc) 0,                                       // tp_setattr
    0,                                                     // RESERVED
    (reprfunc) tp_repr,                                    // tp_repr
    0,                                                     // tp_as_number
    0,                                                     // tp_as_sequence
    0,                                                     // tp_as_mapping
    0,                                                     // tp_hash
    0,                                                     // tp_call
    (reprfunc) tp_str,                                     // tp_str
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
    0,                                                     // tp_methods
    0,                                                     // tp_members
    0,                                                     // tp_getset
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
