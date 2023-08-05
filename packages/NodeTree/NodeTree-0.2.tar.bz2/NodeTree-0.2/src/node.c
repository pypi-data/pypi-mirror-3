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


/* Create a new NodeTree node object

    This creates a new Python object to wrap a given XML node based on its type
*/
PyObject*
nodetree_node_Create (xmlNode* node) {
    switch (node->type) {
        case XML_ELEMENT_NODE :
            return (PyObject*) nodetree_Element_Create(node);

        case XML_TEXT_NODE :
            return PyUnicode_FromString(node->content);

        case XML_COMMENT_NODE :
            return nodetree_Comment_Create(node);

        default :
            Py_RETURN_NONE;
    }
}


/* Copy a node used by a Python object

    Whenever a linked (has a parent/siblings) node is added to a new parent a
    copy of the XML node needs to be made and the node list updated.

    This can be used on any NodeTree Python Object which can be added to a
    parent node, not just Element, as these all use the same object struct.
*/
void
nodetree_node_Copy (void* py_node) {
    nodetree_Element_Object* element = (nodetree_Element_Object*) py_node;
    nodetree_node* next;

    // Allocate and populate a new Node struct
    // We're prepending node list so we can use the new primary node next
    next = PyMem_Malloc(sizeof(nodetree_node));
    next->node = element->node;
    next->next = (nodetree_node*) element->next;

    // Copy current primary node as new primary node, store new node struct
    element->node = xmlCopyNode(element->node, 1);
    element->next = next;
}


/* PyObject to XML

    This function takes a Python object and returns an xmlNode for it based
    on its type.
*/
xmlNode*
nodetree_node_Py2XML (PyObject* item) {
    xmlNode* ret = NULL;

    // First step processing for unicode items
    if (PyUnicode_Check(item)) {
        // Encode unicode string as UTF-8 bytes object
        item = PyUnicode_AsUTF8String(item);
    } else if (PyBytes_Check(item)) {
        // If string/bytes was originally passed in, incref for decref below
        Py_INCREF(item);
    }

    // Handle text nodes
    if (PyBytes_Check(item)) {
        ret = xmlNewTextLen(PyBytes_AsString(item), PyBytes_Size(item));
        Py_DECREF(item);  // We're done with this

        if (!ret) {
            PyErr_SetString(PyExc_ValueError, "error creating text node");
            return NULL;
        }
    }

    // Handle element nodes
    else if (nodetree_Element_Check(item)) {
        // Check to see if Element's primary node is in use
        if (((nodetree_Element_Object*) item)->node->parent) {
            // It is, so make a copy of it which becomes the new primary node
            nodetree_node_Copy((nodetree_Element_Object*) item);
        }

        // Use the child's primary node
        ret = ((nodetree_Element_Object*) item)->node;
    }

    // Handle comment nodes
    else if (nodetree_Comment_Check(item)) {
        // Check to see if Element's primary node is in use
        if (((nodetree_Comment_Object*) item)->node->parent) {
            // It is, so make a copy of it which becomes the new primary node
            nodetree_node_Copy((nodetree_Comment_Object*) item);
        }

        // Use the child's primary node
        ret = ((nodetree_Comment_Object*) item)->node;
    }

    // Unrecognized type
    else
        PyErr_SetString(PyExc_TypeError, "Unsupported XML type");

    // Return node
    return ret;
}


/* Prune an XML branch

    This function frees a node and all of its children which do not have Python
    objects holding them.  If a Python object does hold the child node and its
    the only one its unlinked from its parent and kept for data storage, if a
    child node is held by a Python object but is redundant its removed from the
    Python object's list of nodes and freed along with its children.
*/
void
nodetree_node_Prune (xmlNode* node) {
    nodetree_Element_Object* self;
    nodetree_node* next;
    nodetree_node* after;
    xmlNode* child = NULL;

    // If the node is held by a Python object
    if (node->_private) {
        // This works for all Python nodes, not just Element
        self = (nodetree_Element_Object*) node->_private;

        // This three-part conditional removes the specified node from the
        // Python object's list of nodes.  Copies of the node held by other
        // Python objects will be maintained.

        // If this is the primary node
        if (node == self->node) {
            // If there's more, bump the next into the primary slot and free it
            if (self->next) {
                next = self->next;
                self->node = next->node;
                self->next = next->next;
                free(next);
            }
        }

        // If this is the secondary node
        else if (node == self->next->node) {
            // Bump 2nd non-primary into first non-primary slot, free it
            next = self->next;
            self->next = next->next;
            free(next);
        }

        // Else this needs to be searched for in the self->next node chain
        else {
            next = self->next;
            while (next->next) {
                // We're actually looking at "after"
                after = next->next;

                // When we find it, bump what's after it forward and free
                if (node == after->node) {
                    next->next = after->next;
                    free(after);
                    break;
                }

                // Not found, continue to next in chain
                next = after;
            }
        }

        // Unlink the specified node from its parents and siblings
        xmlUnlinkNode(node);

        // If there's a copy of the node, free it
        if (node != self->node) {
            // Walk through the children, unlinking those with Python objects
            child = node->children;
            while (child) {
                nodetree_node_Prune(child);
                child = child->next;
            }

            // We can now safely free this node
            xmlFreeNode(node);
        }
    }

    // This node is not held by a Python object, recursively unlink/free it
    else {
        // Unlink the specified node from its parents and siblings
        xmlUnlinkNode(node);

        // Walk through children, unlinking those with Python objects
        child = node->children;
        while (child) {
            nodetree_node_Prune(child);
            child = child->next;
        }

        // Now free this node
        xmlFreeNode(node);
    }
}


/* Count child nodes

    This returns the number of children a specified node contains.
*/
int
nodetree_node_Child_Count (xmlNode* node) {
    int length = 0;
    xmlNode* child = node->children;  // Get first child node

    // Walk node list to determine its length
    while (child) {
        child = child->next;
        length++;
    }

    return length;
}


/* Get child node by index

    This function walks through the children of a node and either returns a
    PyObject* for that node or NULL if it couldn't be found.
*/
PyObject*
nodetree_node_Child_Get (xmlNode* node, int index) {
    int i = 0;
    xmlNode* child;
    PyObject* ret = NULL;

    // Get first child
    child = node->children;

    // Iterate over list of children, breaking if an index match is found
    while (child) {
        // Check against index
        if (i == index)
            // This will cause child != NULL below
            break;
        child = child->next;
        i++;
    }

    // If the index was in range
    if (child) {
        if (child->_private) {
            // Use an existing Python object if available
            ret = child->_private;
            Py_INCREF(ret);
        }
        else {
            // Create a new PyObject based on the type of node to return
            ret = nodetree_node_Create(child);
        }
    }
    else {
        // Set exception if index wasn't found
        PyErr_SetString(PyExc_IndexError, "Child index out of range");
    }

    // Return Python object or NULL
    return ret;
}


int
nodetree_node_Child_Set(xmlNode* node, int index, PyObject* value) {
    int i = 0;
    xmlNode* child;
    xmlNode* newchild;

    // Get first child
    child = node->children;

    // Iterate over list of children, breaking if an index match is found
    while (child) {
        // Check against index
        if (i == index)
            // This will cause child != NULL below
            break;
        child = child->next;
        i++;
    }

    // Ensure index was found
    if (!child) {
        // Raise exception
        PyErr_SetString(PyExc_IndexError, "Child index out of range");
        return -1;
    }

    if (value) {
        // Get new child node from value
        newchild = nodetree_node_Py2XML(value);

        // Raise exception if NULL was returned from nodetree_node_Py2XML
        if (!newchild)
            return -1;

        // Replace old node with new one, prune old node
        xmlReplaceNode(child, newchild);
        nodetree_node_Prune(child);
    }
    else {
        // Handle del(node[index]) calls
        nodetree_node_Prune(child);
    }

    // Success
    return 0;
}
