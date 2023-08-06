==========
 Tutorial
==========

PyTAPS is a set of Python bindings to the `ITAPS <http://www.tstt-scidac.org/>`_
(Interoperable Technologies for Advanced Petascale Simulations) interfaces, a
set of standardized interfaces for use in simulation code written in C, C++, or
Fortran (users already familiar with ITAPS may wish to consult :doc:`from-c`
first). Specifically, ITAPS includes:

* `iBase`: Common definitions used by all other ITAPS interfaces
* `iMesh`: Creation, querying, and manipulation of discrete polygonal/polyhedral
  meshes
* `iGeom`: Creation, querying, and manipulation of continuous geometry (e.g.
  CAD)
* `iRel`: Relations between pairs of other ITAPS interface instances 

ITAPS strives to remain implementation-independent, allowing people to write
generic simulation code that can be used on any system that implements the
appropriate ITAPS interfaces. There are several software packages that
implement these interfaces, including
`MOAB <http://trac.mcs.anl.gov/projects/ITAPS/wiki/MOAB/>`_,
`GRUMMP <http://tetra.mech.ubc.ca/GRUMMP/>`_,
`FMDB <http://www.scorec.rpi.edu/FMDB/>`_,
`NWGrid <http://www.emsl.pnl.gov:2080/nwgrid/>`_,
`Frontier <http://frontier.ams.sunysb.edu/news/news.php>`_,
`CGM <http://trac.mcs.anl.gov/projects/ITAPS/wiki/CGM/>`_, and
`Lasso <http://trac.mcs.anl.gov/projects/ITAPS/wiki/Lasso/>`_.
PyTAPS wraps all of this up and makes it available to Python.

In ITAPS, there are three basic data types: `entities`, `entity sets`, and
`tags`. `Entities` refer to individual geometric objects, such as vertices or
hexahedra. `Entity sets` are collections of entities or other entity sets; they
can also contain parent-child relationships with other sets. `Tags` are
(sparse) mappings of entities or entity sets to arbitrary data. These data types
are combined to do everything that can be done in ITAPS (and correspondingly in
PyTAPS).

.. toctree::
   :maxdepth: 2

   why-use
   imesh
   igeom
   sets-tags
   irel
   example
   from-c
