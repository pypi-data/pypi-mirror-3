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


static int
root_setter (nodetree_Document_Object* self, PyObject* value, void* closure);


static char
tp_doc[] = "NodeTree Document\n"
"\n"
"    Documents are XML streams which contain exactly one root element and may\n"
"    contain comments, processing instructions, and other types of XML nodes.\n"
"\n"
"    As with Element, Document children are accessed as items.  While there\n"
"    may be only one root element in a document, the root element is not\n"
"    guarenteed to be the first item (and will often not be).\n"
"\n"
"    The .name property holds the Document's name, filename, or URI.\n"
"    The .root property is a shortcut to the Document's root element.\n"
"    The .version property is the XML version used (currently '1.0' only)\n"
"\n";


static PyObject*
tp_new (PyTypeObject* type, PyObject* args, PyObject* kwds) {
    nodetree_Document_Object* self;

    // Inherit base type
    self = (nodetree_Document_Object*) PyType_GenericNew(type, args, kwds);
    if (!self)
      return NULL;

    // Create new XML document
    self->node = xmlNewDoc("1.0");

    // Link new XML document to this object
    self->node->_private = self;

    // Return self
    return (PyObject*) self;
}


static void
tp_dealloc (nodetree_Document_Object* self) {
    // Free the XML document
    xmlFreeDoc(self->node);

    // Dealloc base type
    PyObject_Del((PyObject*) self);
}


static PyObject*
tp_repr (nodetree_Document_Object* self) {
    xmlChar* string;
    int string_size;
    PyObject* ret;

    // Dump XML for entire document to a string
    xmlDocDumpFormatMemory(self->node, &string, &string_size, 1);

    // Convert the returned XML string to a Python return string
    ret = PyUnicode_FromStringAndSize((char*) string, string_size);

    // Free XML string and return the Python string
    xmlFree(string);
    return ret;
}


static PyObject*
tp_str (nodetree_Document_Object* self) {
    xmlChar* string;
    int string_size;
    PyObject* ret;

    // Dump XML for entire document to a string
    xmlDocDumpMemory(self->node, &string, &string_size);

    // Convert the returned XML string to a Python return string
    ret = PyUnicode_FromStringAndSize((char*) string, string_size);

    // Free XML string and return the Python string
    xmlFree(string);
    return ret;
}


/////////////////////////////////////////////////////////////////////////////
// Sequence Methods

static Py_ssize_t
sq_length (nodetree_Document_Object* self) {
    // Use child node counter
    return (Py_ssize_t) nodetree_node_Child_Count((xmlNode*) self->node);
}


static PyObject*
sq_item (nodetree_Document_Object* self, Py_ssize_t index) {
    // Use child node getter
    return nodetree_node_Child_Get((xmlNode*) self->node, (int) index);
}


static int
sq_ass_item (nodetree_Document_Object* self, Py_ssize_t index,
             PyObject* value) {
    int i = 0;
    xmlNode* child;
    xmlNode* oldroot;

    /* Element node handling

        We need to handle Element children specially because only one is
        permitted in a Document (the root node), though comments and other
        types of nodes may also be in a Document.

        libxml also has special handling of root nodes so we get this out of
        the way before handling any other kind of node.

        Note that we must check that value != NULL for del() operations.
    */

    if (value && nodetree_Element_Check(value)) {
        /* Check current root vs new element

            We want to ensure that if there's already a root element, the new
            one will only replace it if its being set to the same position.
            Ie, the behavior is identical to using the Document.root property.

            To not allow this may make some functions more complex than they
            need to be.  Code complexity is better here to keep the API simple.
        */

        if (oldroot = xmlDocGetRootElement(self->node)) {
            // Get first child
            child = self->node->children;

            // Search for oldroot's index in the children list
            while (child) {
                if (child == oldroot)
                    break;
                i++;
                child = child->next;
            }

            // Ensure the new root and old root are at the same index
            if (i != index) {
                PyErr_SetString(PyExc_ValueError,
                                "Can only replace root node in-place.\n"
                                "Use Document.root property to replace the "
                                "root node or delete it first.");
                return -1;
            }
        }

        /* Same position

            The new root node is destined for the same position as the old root
            so its safe to let this fall through and be processed normally.
        */
    }

    /* Filter disallowed node types

        Besides only permitting one root element, certain types of nodes are
        strictly not permitted in a document root.  These need to raise an
        exception instead of being processed as they would being added to an
        Element node.

        After this any remaining node can be processed by nodetree_node_Py2XML.

        Note that we must check that value != NULL for del() operations.
    */

    // Ensure value is not a bytes/string or unicode type (aka text node)
    if (value && (PyUnicode_Check(value) || PyBytes_Check(value))) {
        PyErr_SetString(PyExc_TypeError,
                        "Text nodes can only be added to an Element node.");
        return -1;
    }

    // Use child node setter
    return nodetree_node_Child_Set((xmlNode*) self->node, (int) index, value);
}


static int
sq_contains (nodetree_Document_Object* self, PyObject* value) {
    xmlNode* child;
    nodetree_node* next;

    // Documents only have one root Element, so this is easy to check
    if (nodetree_Element_Check(value)) {
        child = xmlDocGetRootElement(self->node);

        // Check first node
        if (child = ((nodetree_Element_Object*) value)->node)
            return 1;

        // Then search node list for a match
        next = ((nodetree_Element_Object*) value)->next;
        while (next) {
            if (child = next->node)
                return 1;
            next = (nodetree_node*) next->next;
        }

        // Element was not found
        return 0;
    }

    // TODO Check for other types of nodes

    // Unrecognized value types are never contained in a NodeTree Document
    return 0;
}


/////////////////////////////////////////////////////////////////////////////
// General Methods

static char
append_doc[] = "NodeTree Document.append method\n"
"\n"
"    This method can be used to add a child node to the document.  While an\n"
"    XML document may only have one root Element, other types of nodes can\n"
"    be added, in any order, such as comments and processing instructions.\n"
"\n"
"    If a root Element is added to a Document which already has one, the old\n"
"    root Element will be detached and will also be freed from memory if no\n"
"    reference to it is held by Python.\n"
"\n";


static PyObject*
append (nodetree_Document_Object* self, PyObject* args) {
    PyObject* item;
    xmlNode* child;

    // Parse argument tuple for single item
    if (!PyArg_ParseTuple(args, "O", &item)) {
        return NULL;
    }

    /* Element node handling

        We need to handle Element children specially because only one is
        permitted in a Document (the root node), though comments and other
        types of nodes may also be in a Document.

        libxml also has special handling of root nodes so we get this out of
        the way before handling any other kind of node.
    */

    if (nodetree_Element_Check(item)) {
        /* Root node replacement not allowed with Document.append

            We do not allow appending an element when there's already a root
            node in a document because doing so would "magically" remove the
            old root from its location changing the ordering in a non-intuitive
            manner.  Ie, appending should always increase the length of a
            sequence, and allowing this would make that not the case.

            "Explicit is better than implicit."

            The Document.root property is provided for this reason.
        */

        if (xmlDocGetRootElement(self->node)) {
            PyErr_SetString(PyExc_ValueError, "Cannot add second root node.\n"
                            "Use Document.root property to replace the root "
                            "node or delete it first.");
            return NULL;
        }

        // If there is not already a root node, this behaves exactly like using
        // the Document.root property, so we just call that code directly.
        if (root_setter(self, item, NULL) == -1) {
            // Exception set by root_setter already
            return NULL;
        }

        // Returns None on success
        Py_RETURN_NONE;
    }

    /* Filter disallowed node types

        Besides only permitting one root element, certain types of nodes are
        strictly not permitted in a document root.  These need to raise an
        exception instead of being processed as they would being added to an
        Element node.

        After this any remaining node can be processed by nodetree_node_Py2XML.
    */

    // Ensure value is not a bytes/string or unicode type (aka text node)
    if (PyUnicode_Check(item) || PyBytes_Check(item)) {
        PyErr_SetString(PyExc_TypeError,
                        "Text nodes can only be added to an Element node.");
        return NULL;
    }

    // Get new child node
    child = nodetree_node_Py2XML(item);

    // Return exception NULL was returned by nodetree_node_Py2XML
    if (!child)
        return NULL;

    // Add child to end of children list
    child = xmlAddChild((xmlNode*) self->node, child);

    // Raise exception if this fails for some reason
    if (!child) {
        PyErr_SetString(PyExc_ValueError, "error appending child");
        return NULL;
    }

    // Returns None on success
    Py_RETURN_NONE;
}


/////////////////////////////////////////////////////////////////////////////
// Properties

static PyObject*
root_getter (nodetree_Document_Object* self, void* closure) {
    xmlNode* root;

    // Get root element from libxml2
    root = xmlDocGetRootElement(self->node);

    // Return None if there isn't one
    if (!root)
        Py_RETURN_NONE;

    if (root->_private)
        // Incref existing Element object if there is one
        Py_INCREF((PyObject*) root->_private);
    else
        // Create a new Element object to wrap the node for Python
        nodetree_Element_Create(root);

    return (PyObject*) root->_private;
}


static int
root_setter (nodetree_Document_Object* self, PyObject* value, void* closure) {
    nodetree_Element_Object* element;
    xmlNode* oldroot;
    xmlNode* newroot;

    // Handle del(document.root) and document.root = None calls
    if (!value || value == Py_None) {
        oldroot = xmlDocGetRootElement(self->node);

        // Do nothing if there is no root element
        if (oldroot) {
            // Prune node from tree
            nodetree_node_Prune(oldroot);
        }

        // Always succeeds
        return 0;
    }

    // Ensure value is an Element
    if (!nodetree_Element_Check(value)) {
        PyErr_SetString(PyExc_TypeError,
                        "root attribute must be an Element node");
        return -1;
    }

    // This is just for code simplicity
    element = (nodetree_Element_Object*) value;

    // Check to see if Element's primary node is in use
    if (element->node->parent)
        nodetree_node_Copy(element);

    // This function returns the old root element (or NULL)
    oldroot = xmlDocSetRootElement(self->node,
                                   ((nodetree_Element_Object*) value)->node);

    // Clean up old root if necessary
    if (oldroot)
        nodetree_node_Prune(oldroot);

    // Return success
    return 0;
}


/////////////////////////////////////////////////////////////////////////////
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
    {"append",                                             // ml_name
     (PyCFunction) append,                                 // ml_meth
     METH_VARARGS,                                         // ml_flags
     append_doc},                                          // ml_doc
    {NULL},                                                // sentinel
};


static PyGetSetDef tp_getset[] = {
    {"root",
     (getter) root_getter,
     (setter) root_setter,
     "Document's root element - there can be only one.",
     NULL},
    {NULL},                                                // sentinel
};


PyTypeObject nodetree_Document_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "nodetree.Document",                                   // tp_name
    sizeof(nodetree_Document_Object),                      // tp_basicsize
    0,                                                     // tp_itemsize
    (destructor) tp_dealloc,                               // tp_dealloc
    0,                                                     // RESERVED
    (getattrfunc) 0,                                       // tp_getattr
    (setattrfunc) 0,                                       // tp_setattr
    0,                                                     // RESERVED
    (reprfunc) tp_repr,                                    // tp_repr
    0,                                                     // tp_as_number
    &tp_as_sequence,                                       // tp_as_sequence
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
    tp_new,                                                // tp_new
    0,                                                     // tp_free
    0,                                                     // tp_is_gc
};

