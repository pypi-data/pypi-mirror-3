This plugin for Trac uses JavaScript to modify the user interface for
reordering enumerable ticket fields, such as Priorities and Resolutions in the
Trac admin web interface.

The new UI allows rows in the value listing table to be drag-and-dropped,
rather than have to specify the order for each value in a drop down list.

This plugin is also compatible with the very useful `CustomFieldAdminPlugin`_
so that it also supports an easier UI for reordering ticket fields.

This plugin makes use of the `TableDnD`_ plugin for jQuery, which is (c) Denis
Howlett <denish@isocra.com> under an MIT license.

.. _CustomFieldAdminPlugin: http://trac-hacks.org/wiki/CustomFieldAdminPlugin
.. _TableDnD: https://github.com/isocra/TableDnD/
