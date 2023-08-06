================
 Why Use PyTAPS
================

Programmers already familiar with using the ITAPS interfaces in C or Fortran may
be wondering why they should use PyTAPS instead. Well, for the same reason that
one would want to use Python for any kind of scientific computing: it's easier!

An Example
==========

For a motivating example, let's consider an extremely simple program. We want to
load in a VTK mesh containing several quadrilateral faces, and then print out
the coordinates of each point on each quad, like so::

  0.0, 0.0, 0.0
  0.0, 1.0, 0.0
  1.0, 1.0, 0.0
  1.0, 0.0, 0.0

  0.0, 0.0, 1.0
  0.0, 1.0, 1.0
  1.0, 1.0, 1.0
  1.0, 0.0, 1.0

  0.0, 0.0, 2.0
  0.0, 1.0, 2.0
  1.0, 1.0, 2.0
  1.0, 0.0, 2.0

C Version
---------

We'll start by writing this in C, using iMesh.

.. code-block:: c

   #include <iBase.h>
   #include <iMesh.h>
   #include <stdio.h>
   #include <stdlib.h>

   void handleError(iMesh_Instance mesh)
   {
       int err;
       char error[120];
       iMesh_getDescription(mesh, error, &err, sizeof(error));
       printf("Error: %s\n", error);
       exit(1);
   }

   int main()
   {
       iMesh_Instance mesh;
       int err;

       iMesh_newMesh("", &mesh, &err, 0);
       if(err != 0)
           handleError(mesh);

       iMesh_load(mesh, NULL, "mesh.vtk", "", &err, 8, 0);
       if(err != 0)
           handleError(mesh);

       iBase_EntityHandle *faces = NULL;
       int faces_allocated = 0;
       int faces_size;

       iMesh_getEntities(mesh, NULL, iBase_FACE, iMesh_ALL_TOPOLOGIES,
                         &faces, &faces_allocated, &faces_size, &err);
       if(err != 0)
           handleError(mesh);

       iBase_EntityHandle *adj_ents = NULL;
       int adj_allocated = 0;
       int adj_size;
       int *offsets = NULL;
       int offsets_allocated = 0;
       int offsets_size;

       iMesh_getEntArrAdj(mesh, faces, faces_size, iBase_VERTEX,
                          &adj_ents, &adj_allocated, &adj_size,
                          &offsets, &offsets_allocated, &offsets_size,
                          &err);
       if(err != 0)
           handleError(mesh);

       int i,j;
       for(i=0; i<faces_size; i++)
       {
           for(j=offsets[i]; j<offsets[i+1]; j++)
           {
               double x, y, z;
               iMesh_getVtxCoord(mesh, adj_ents[j], &x, &y, &z, &err);
               if(err != 0)
                   handleError(mesh);
               printf("%f, %f, %f\n", x, y, z);
           }
           printf("\n");
       }

       free(adj_ents);
       free(offsets);
       free(faces);

       iMesh_dtor(mesh, &err);
       if(err != 0)
           handleError(mesh);
       
       return 0;
   }

Python Version
--------------

Now, let's try the same thing in Python, using PyTAPS.

.. code-block:: python

   from itaps import iBase, iMesh

   mesh = iMesh.Mesh()
   mesh.load("mesh.vtk")

   faces = mesh.getEntities(iBase.Type.face)
   adj = mesh.getEntAdj(faces, iBase.Type.vertex)

   for i in adj:
       for j in i:
           x, y, z = mesh.getVtxCoords(j)
           print "%f, %f, %f" % (x, y, z)
       print

Conclusions
-----------

It turns out that the source code for the C version of this program is over 5
times the size (in bytes) of that of the Python version! Because of the sheer
amount of code necessary to work with ITAPS in C, we end up spending much more
time typing and much less time getting to the interesting bits. Besides that,
having more code just leaves you with more places for bugs to hide! In fact,
the C version already has a bug waiting to bite us: if an error occurs midway
through the program, we don't remember to ``free()`` the already-allocated
arrays. In this case, we're lucky because the operating system will reclaim
that memory when we call ``exit(1)``, but imagine if this were part of a
program that loaded many large meshes and tried to continue if one failed!
