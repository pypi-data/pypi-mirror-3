1694 /*OBJECT_API
1695   To File
1696 */
1697 static int
1698 PyArray_ToFile(PyArrayObject *self, FILE *fp, char *sep, char *format)
1699 {
1700     intp size;
1701     intp n, n2;
1702     size_t n3, n4;
1703     PyArrayIterObject *it;
1704     PyObject *obj, *strobj, *tupobj;
1705 
1706     n3 = (sep ? strlen((const char *)sep) : 0);
1707     if (n3 == 0) { /* binary data */
1708         if (PyDataType_FLAGCHK(self->descr, NPY_LIST_PICKLE)) {
1709             PyErr_SetString(PyExc_ValueError, "cannot write " \
1710                             "object arrays to a file in "   \
1711                             "binary mode");
1712             return -1;
1713         }
1714 
1715         if (PyArray_ISCONTIGUOUS(self)) {
1716             size = PyArray_SIZE(self);
1717             NPY_BEGIN_ALLOW_THREADS
1718                 n=fwrite((const void *)self->data,
1719                          (size_t) self->descr->elsize,
1720                          (size_t) size, fp);
1721             NPY_END_ALLOW_THREADS
1722                 if (n < size) {
1723                     PyErr_Format(PyExc_ValueError,
1724                                  "%ld requested and %ld written",
1725                                  (long) size, (long) n);
1726                     return -1;
1727                 }
1728         }
1729         else {
1730             NPY_BEGIN_THREADS_DEF
1731 
1732                 it=(PyArrayIterObject *)                        \
1733                 PyArray_IterNew((PyObject *)self);
1734             NPY_BEGIN_THREADS
1735                 while(it->index < it->size) {
1736                     if (fwrite((const void *)it->dataptr,
1737                                (size_t) self->descr->elsize,
1738                                1, fp) < 1) {
1739                         NPY_END_THREADS
1740                             PyErr_Format(PyExc_IOError,
1741                                          "problem writing element"\
1742                                          " %d to file",
1743                                          (int)it->index);
1744                         Py_DECREF(it);
1745                         return -1;
1746                     }
1747                     PyArray_ITER_NEXT(it);
1748                 }
1749             NPY_END_THREADS
1750                 Py_DECREF(it);
1751         }
1752     }
1753     else {  /* text data */
1754 
1755         it=(PyArrayIterObject *)                                \
1756             PyArray_IterNew((PyObject *)self);
1757         n4 = (format ? strlen((const char *)format) : 0);
1758         while(it->index < it->size) {
1759             obj = self->descr->f->getitem(it->dataptr, self);
1760             if (obj == NULL) {Py_DECREF(it); return -1;}
1761             if (n4 == 0) { /* standard writing */
1762                 strobj = PyObject_Str(obj);
1763                 Py_DECREF(obj);
1764                 if (strobj == NULL) {Py_DECREF(it); return -1;}
1765             }
1766             else { /* use format string */
1767                 tupobj = PyTuple_New(1);
1768                 if (tupobj == NULL) {Py_DECREF(it); return -1;}
1769                 PyTuple_SET_ITEM(tupobj,0,obj);
1770                 obj = PyString_FromString((const char *)format);
1771                 if (obj == NULL) {Py_DECREF(tupobj);
1772                     Py_DECREF(it); return -1;}
1773                 strobj = PyString_Format(obj, tupobj);
1774                 Py_DECREF(obj);
1775                 Py_DECREF(tupobj);
1776                 if (strobj == NULL) {Py_DECREF(it); return -1;}
1777             }
1778             NPY_BEGIN_ALLOW_THREADS
1779                 n=fwrite(PyString_AS_STRING(strobj), 1,
1780                          n2=PyString_GET_SIZE(strobj), fp);
1781             NPY_END_ALLOW_THREADS
1782                 if (n < n2) {
1783                     PyErr_Format(PyExc_IOError,
1784                                  "problem writing element %d"\
1785                                  " to file",
1786                                  (int) it->index);
1787                     Py_DECREF(strobj);
1788                     Py_DECREF(it);
1789                     return -1;
1790                 }
1791             /* write separator for all but last one */
1792             if (it->index != it->size-1)
1793                 if (fwrite(sep, 1, n3, fp) < n3) {
1794                     PyErr_Format(PyExc_IOError,
1795                                  "problem writing "\
1796                                  "separator to file");
1797                     Py_DECREF(strobj);
1798                     Py_DECREF(it);
1799                     return -1;
1800                 }
1801             Py_DECREF(strobj);
1802             PyArray_ITER_NEXT(it);
1803         }
1804         Py_DECREF(it);
1805     }
1806     return 0;
1807 }
