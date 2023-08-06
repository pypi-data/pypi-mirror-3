#ifndef PYTAPS_IGEOM_DOC_H
#define PYTAPS_IGEOM_DOC_H

/***** iGeom.Geom *****/

#define IGEOMDOC_iGeom \
"Return a new :class:`Geom` object with any implementation-specific options\n" \
"defined in *options*.\n\n"                                                    \
":param options: Implementation-specific options string"

#define IGEOMDOC_iGeom_rootSet \
"Return the handle of the root set for this instance. The entire\n"            \
"geometry in this instance can be accessed from this set."

#define IGEOMDOC_iGeom_boundBox \
"Return the bounding box of the entire model."

#define IGEOMDOC_iGeom_topoLevel \
"Return the topology level of the geometry as an integer, where 0 =\n"         \
"basic entities only, 1 = manifold entities, 2 = non-manifold entities."

#define IGEOMDOC_iGeom_parametric \
"Return True if the interface has information about parameterization,\n"       \
"False otherwise."

#define IGEOMDOC_iGeom_tolerance \
"Return a tuple representing the tolerance at the modeler level. The\n"        \
"first value is an integer representing the type of the tolerance, where\n"    \
"0 = no tolerance information, 1 = modeler-level tolerance, 2 =\n"             \
"entity-level tolerances. If this value is 1, the second value returns\n"      \
"the modeler-level tolerance. If this value is 2, use\n"                       \
":meth:`getEntTolerance` to query the tolerance on a per-entity basis."

#define IGEOMDOC_iGeom_load \
"Load a geometry from a file.\n\n"                                             \
":param filename: File name from which the geometry is to be loaded\n"         \
":param options: Implementation-specific options string"

#define IGEOMDOC_iGeom_save \
"Save the geometry to a file.\n\n"                                             \
":param filename: File name to which the geometry is to be saved\n"            \
":param options: Implementation-specific options string"

#define IGEOMDOC_iGeom_createSphere \
"Create a sphere with the specified *radius*.\n\n"                             \
":param radius: The radius of the sphere\n"                                    \
":return: The created entity"

#define IGEOMDOC_iGeom_createBrick \
"Create a sphere with the x, y, and z dimensions specified in\n"               \
"*dimensions*. You may also call this method with\n"                           \
"``createBrick(x, y, z)``.\n\n"                                                \
":param dimensions: The dimensions of the brick\n"                             \
":return: The created entity"

#define IGEOMDOC_iGeom_createCylinder \
"Create a cylinder with the specified *height*, *major_rad*, and\n"            \
"*minor_rad*.\n\n"                                                             \
":param height: The height of the cylinder\n"                                  \
":param major_rad: The cylinder's major radius\n"                              \
":param minor_rad: The cylinder's minor radius\n"                              \
":return: The created entity"

#define IGEOMDOC_iGeom_createPrism \
"Create a prism with the specified *height*, *sides*, *major_rad*, and\n"      \
"*minor_rad*.\n\n"                                                             \
":param height: The height of the prism\n"                                     \
":param sides: The number of sides of the prism\n"                             \
":param major_rad: The prism's major radius\n"                                 \
":param minor_rad: The prism's minor radius\n"                                 \
":return: The created entity"

#define IGEOMDOC_iGeom_createCone \
"Create a cylinder with the specified *height*, *major_rad*,\n"                \
"*minor_rad*, and *top_rad*.\n\n"                                              \
":param height: The height of the cone\n"                                      \
":param major_rad: The cone's major radius\n"                                  \
":param minor_rad: The cone's minor radius\n"                                  \
":param minor_rad: The cone's top radius\n"                                    \
":return: The created entity"

#define IGEOMDOC_iGeom_createTorus \
"Create a torus with the specified *major_rad* and *minor_rad*.\n\n"           \
":param major_rad: The torus's major radius\n"                                 \
":param minor_rad: The torus's minor radius\n"                                 \
":return: The created entity"

#define IGEOMDOC_iGeom_deleteAll \
"Delete all entities in the model."

#define IGEOMDOC_iGeom_deleteEnt \
"Delete the specified entity.\n\n"                                             \
":param entity: An entity to delete"

#define IGEOMDOC_iGeom_getVtxCoords \
"Get the coordinates of the vertices specified in *src*.\n\n"                  \
"If *dest* is supplied, return parameterized coordinates relative to the\n"    \
"entity or entities specified in *dest*. *dest* may either be an entity\n"     \
"(or array of entities) or a tuple of the entities and the basis of the\n"     \
"parameterized coordinates. If the basis is not specified, it is\n"            \
"inferred from the first entity in *dest*.\n\n"                                \
"With *dest* supplied, if *src* is a single :class:`~itaps.iBase.Entity`\n"    \
"or an array with one element, return the coordinates of that entity\n"        \
"relative to each entity in *dest*. Likewise, if *dest* is a single\n"         \
"entity,return the coordinates of each of *src* relative to that entity.\n\n"  \
":param src: Vertex or array of vertices being queried\n"                      \
":param dest: Either 1) an entity or array of entities, or 2) a tuple\n"       \
"             containing (1) followed by the expected basis of the\n"          \
"             coordinates.\n"                                                  \
":param storage_order: Storage order of vertices to be returned\n"             \
":return: If *entities* and *dest* (if specified) are both single\n"           \
"         :class:`Entities <itaps.iBase.Entity>`, the coordinates of\n"        \
"         *src* Otherwise, an array of coordinates."

#define IGEOMDOC_iGeom_getEntCoords \
"Transform the supplied *coords* relative to the bases in *src* and\n"         \
"*dest*.\n\n"                                                                  \
"*src* and *dest*, if supplied, represent the parameterization of the\n"       \
"input and output coordinates, respectively. Both may either be an\n"          \
"entity (or array of entities) or a tuple of the entities and the basis\n"     \
"of the parameterized coordinates. If the basis is not specified, it is\n"     \
"inferredfrom the first entity in *src* or *dest*.\n\n"                        \
"If *src* is supplied, *coords* should be parameterized relative to the\n"     \
"entities in *src*.  If *src* is a single :class:`~itaps.iBase.Entity`\n"      \
"or an array with one element, transform the coordinates of each element\n"    \
"in *coords* relative to that element. Likewise, if *coords* is a single\n"    \
"vector, transform the its coordinates relative to that each entity in\n"      \
"*src*.\n\n"                                                                   \
"If *dest* is supplied, the resulting coordinates will be parameterized\n"     \
"relative to the entities in *dest*. A similar relation between arrays\n"      \
"and single elements of *dest* exists as with *src*.\n\n"                      \
":param coords: Coordinate(s) being queried\n"                                 \
":param src: Either 1) an entity or array of entities, or 2) a tuple\n"        \
"            containing (1) followed by the expected basis of the\n"           \
"            coordinates.\n"                                                   \
":param dest: Either 1) an entity or array of entities, or 2) a tuple\n"       \
"             containing (1) followed by the expected basis of the\n"          \
"             coordinates.\n"                                                  \
":param storage_order: Storage order of the coordinates supplied and\n"        \
"                      returned\n"                                             \
":return: If *source* is a single vector, and *src* and *dest* (if\n"          \
"         specified) are both single\n"                                        \
"         :class:`Entities <itaps.iBase.Entity>`, then a single\n"             \
"         transformed coordinates. Otherwise, an array of coordinates."

#define IGEOMDOC_iGeom_measure \
"Return the measure (length, area, or volume, as applicable) of the\n"         \
"specified *entities*.\n\n"                                                    \
":param entities: Entity or array of entities being queried\n"                 \
":return: If *entities* is a single :class:`~itaps.iBase.Entity`, the\n"       \
"         measure of that entity. Otherwise, an array of measures."

#define IGEOMDOC_iGeom_getEntType \
"Get the entity type for the specified entities.\n\n"                          \
":param entities: Entity or array of entities being queried\n"                 \
":return: If *entities* is a single :class:`~itaps.iBase.Entity`, the\n"       \
"         type of the entity. Otherwise, an array of the entity types."

#define IGEOMDOC_iGeom_getFaceType \
"Return an implementation-defined string describing the type of the\n"         \
"specified face.\n\n"                                                          \
":param entity: The entity to query\n"                                         \
":return: A string describing the face's type"

#define IGEOMDOC_iGeom_isEntParametric \
"Return whether the specified *entities* have parameterization.\n\n"           \
":param entities: Entity or array of entities being queried\n"                 \
":return: If *entities* is a single :class:`~itaps.iBase.Entity`, a\n"         \
"         boolean representing whether the entity has parameterization.\n"     \
"         Otherwise, an array of booleans."

#define IGEOMDOC_iGeom_isEntPeriodic \
"Return whether the specified *entities* are periodic.\n\n"                    \
":param entities: Entity or array of entities being queried\n"                 \
":return: If *entities* is a single :class:`~itaps.iBase.Entity`, a\n"         \
"         boolean representing whether the entity is periodic.\n"              \
"         Otherwise, an array of booleans."

#define IGEOMDOC_iGeom_isFcDegenerate \
"Return whether the specified faces are degenerate.\n\n"                       \
":param entities: Entity or array of entities being queried\n"                 \
":return: If *entities* is a single :class:`~itaps.iBase.Entity`, a\n"         \
"         boolean representing whether the face is degenerate.\n"              \
"         Otherwise, an array of booleans."

#define IGEOMDOC_iGeom_getEntBoundBox \
"Return the bounding box for the specified entities.\n\n"                      \
":param entities: Entity or array of entities being queried\n"                 \
":param storage_order: Storage order of vertices to be returned\n"             \
":return: If *entities* is a single :class:`~itaps.iBase.Entity`, the\n"       \
"         coordinates of the bounding box. Otherwise, an array of\n"           \
"         coordinates."

#define IGEOMDOC_iGeom_getEntRange \
"Return the parametric range of the specified *entities*. If *basis* is\n"     \
"specified, assume that the parameterization of *entities* is in that\n"       \
"basis. Otherwise, infer the basis from the first element of *entities*.\n\n"  \
":param entities: Entity or array of entities being queried\n"                 \
":param basis: The :class:`Basis` of the supplied coordinates\n"               \
":param storage_order: Storage order of the vectors returned\n"                \
":return: If *entities* is a single :class:`~itaps.iBase.Entity`, a pair\n"    \
"         of vectors representing the parametric range. Otherwise, A\n"        \
"         pair of arrays of vectors."

#define IGEOMDOC_iGeom_getEntTolerance \
"Return the tolerance for the specified *entities*.\n\n"                       \
":param entities: Entity or array of entities being queried\n"                 \
":return: If *entities* is a single :class:`~itaps.iBase.Entity`, the\n"       \
"         tolerance (as a :class:`float`). Otherwise, an array of\n"           \
"         tolerances."

#define IGEOMDOC_iGeom_getEntAdj \
"Get entities of the specified type adjacent to elements of *entities*.\n"     \
"If *entities* is a single :class:`~itaps.iBase.Entity`, returns an\n"         \
"array of adjacent entities. If *entities* is an array of entities,\n"         \
"return an :class:`~itaps.helpers.OffsetListSingle` instance.\n\n"             \
":param entities: Entity or array of entities being queried\n"                 \
":param type: Type of adjacent entities being requested\n"                     \
":return: If *entities* is a single :class:`~itaps.iBase.Entity`, an\n"        \
"         array of adjacent entities. Otherwise, an\n"                         \
"         :class:`~itaps.helpers.OffsetListSingle` instance."

#define IGEOMDOC_iGeom_getEnt2ndAdj \
"Get \"2nd order\" adjacencies to an array of entities, that is, from each \n" \
"entity, through other entities of a specified \"bridge\" dimension, to\n"     \
"other entities of another specified \"to\" dimension. If *entities* is a\n"   \
"single :class:`~itaps.iBase.Entity`, returns an array of adjacent\n"          \
"entities. If *entities* is an array of entities, return an\n"                 \
":class:`~itaps.helpers.OffsetListSingle` instance.\n\n"                       \
":param entities: Entity or array of entities being queried\n"                 \
":param bridge_type: Type of bridge entity for 2nd order adjacencies\n"        \
":param type: Type of adjacent entities being requested\n"                     \
":return: If *entities* is a single :class:`~itaps.iBase.Entity`, an\n"        \
"         array of adjacent entities. Otherwise, an\n"                         \
"         :class:`~itaps.helpers.OffsetListSingle` instance."

#define IGEOMDOC_iGeom_isEntAdj \
"Return an array indicating whether the entities in the array\n"               \
"*entities1* are pairwise adjacent to those in *entities2*. If\n"              \
"*entities1* is a single :class:`~itaps.iBase.Entity` or an array with\n"      \
"one element, then return an array indicating that entity's adjacency\n"       \
"with each entity in *entities2* (likewise when *entities2* is a single\n"     \
"entity).\n\n"                                                                 \
":param entities1: Entity or array of entities being queried\n"                \
":param entities2: Entity or array of entities being queried\n"                \
":return: If *entities1* and *entities2* are both single\n"                    \
"         :class:`Entities <itaps.iBase.Entity>`, a boolean indicating\n"      \
"         whether they are adjacent. Otherwise, an array of booleans."

#define IGEOMDOC_iGeom_getEntClosestPt \
"Return the pairwise closest points on *entities* to the points\n"             \
"specified in *coords*. If *entities* is a single\n"                           \
":class:`~itaps.iBase.Entity` or an array with one element, return the\n"      \
"closest points on that entity to the points in *coords*. Likewise, if\n"      \
"*coords* is a single point, return the closest points on each of\n"           \
"*entities* to that point.\n\n"                                                \
":param entities: Entity or array of entities being queried\n"                 \
":param coords: XYZ coordinate(s) being queried\n"                             \
":param storage_order: Storage order of the vertices supplied and\n"           \
"                      returned\n"                                             \
":return: If *entities* is a single :class:`~itaps.iBase.Entity`, and\n"       \
"         *coords* is a vector, return a vector representing the closest \n"   \
"         point. Otherwise, return an array of vectors."

#define IGEOMDOC_iGeom_getEntNormal \
"Return the pairwise normals on *entities* at the points specified in\n"       \
"*coords*. If *entities* is a single :class:`~itaps.iBase.Entity` or an\n"     \
"array with one element, return the normals on that entity at the points\n"    \
"in *coords*. Likewise, if *coords* is a single point, return the\n"           \
"normals on each of *entities* at that point.\n\n"                             \
":param entities: Entity or array of entities being queried\n"                 \
":param coords: Coordinate(s) being queried\n"                                 \
":param basis: The :class:`Basis` of the supplied coordinates\n"               \
":param storage_order: Storage order of the vertices supplied and\n"           \
"                      returned\n"                                             \
":return: If *entities* is a single :class:`~itaps.iBase.Entity`, and\n"       \
"         *coords* is a vector, return a vector representing the normal.\n"    \
"         Otherwise, return an array of vectors."

#define IGEOMDOC_iGeom_getEntNormalPl \
"Return the pairwise closest points and normals on *entities* to/at the\n"     \
"points specified in *coords*. If *entities* is a single\n"                    \
":class:`~itaps.iBase.Entity` or an array with one element, return the\n"      \
"closest points/normals on that entity at the points in *coords*.\n"           \
"Likewise, if *coords* is a single point, return the closest\n"                \
"points/normalson each of *entities* at that point.\n\n"                       \
":param entities: Entity or array of entities being queried\n"                 \
":param coords: XYZ coordinate(s) being queried\n"                             \
":param storage_order: Storage order of the vertices supplied and\n"           \
"                      returned\n"                                             \
":return: If *entities* is a single :class:`~itaps.iBase.Entity`, and\n"       \
"         *coords* is a vector, return a tuple of the closest point and\n"     \
"         the normal. Otherwise, return a tuple of arrays of the closest\n"    \
"         points and normals."

#define IGEOMDOC_iGeom_getEntTangent \
"Return the pairwise tangents on *entities* at the points specified in\n"      \
"*coords*. If *entities* is a single :class:`~itaps.iBase.Entity` or an\n"     \
"array with one element, return the tangents on that entity at the\n"          \
"points in *coords*. Likewise, if *coords* is a single point, return the\n"    \
"tangents on each of *entities* at that point.\n\n"                            \
":param entities: Entity or array of entities being queried\n"                 \
":param coords: Coordinate(s) being queried\n"                                 \
":param basis: The :class:`Basis` of the supplied coordinates\n"               \
":param storage_order: Storage order of the vertices supplied and\n"           \
"                      returned\n"                                             \
":return: If *entities* is a single :class:`~itaps.iBase.Entity`, and\n"       \
"         *coords* is a vector, return a vector representing the\n"            \
"         tangent. Otherwise, return an array of vectors."

#define IGEOMDOC_iGeom_getEntCurvature \
"Return the pairwise curvatures on *entities* at the points specified in\n"    \
"*coords*. If *entities* is a single :class:`~itaps.iBase.Entity` or an\n"     \
"array with one element, return the curvatures on that entity at the\n"        \
"points in *coords*. Likewise, if *coords* is a single point, return the\n"    \
"curvatures on each of *entities* at that point.\n\n"                          \
"If *type* is specified, this method assumes that the elements of\n"           \
"*entities* are of that type. Otherwise, the type is inferred from the\n"      \
"first element of *entities*.\n\n"                                             \
":param entities: Entity or array of entities being queried\n"                 \
":param coords: Coordinate(s) being queried\n"                                 \
":param basis: The :class:`Basis` of the supplied coordinates\n"               \
":param type: The :class:`~itaps.iBase.Type` of the supplied entities\n"       \
":param storage_order: Storage order of the vertices supplied and\n"           \
"                      returned\n"                                             \
":return: If *entities* or *coords* are arrays, a pair of arrays of\n"         \
"         vectors representing the two curvatures of each entity.\n"           \
"         Otherwise, either 1) a single curvature vector when *entities*\n"    \
"         is a single :data:`~itaps.iBase.Type.edge`, a vector, or 2) a\n"     \
"         pair of curvature vectors when *entities* is a single\n"             \
"         :data:`~itaps.iBase.Type.face`.\n\n"                                 \
".. note::\n"                                                                  \
"   If *entities* or *coords* are arrays, this method will always return\n"    \
"   pairs of curvatures, even for edges. Only the first curvature is\n"        \
"   valid, however."

#define IGEOMDOC_iGeom_getEntEval \
"Return pairwise data about *entities* at the points specified in\n"           \
"*coords*. If *entities* is a single :class:`~itaps.iBase.Entity` or an\n"     \
"array with one element, return the data for that entity at the points\n"      \
"in *coords*. Likewise, if *coords* is a single point, return the data\n"      \
"for each of *entities* at that point.\n\n"                                    \
"The data returned depends on the type of the entities. If *type* is\n"        \
":data:`~itaps.iBase.Type.edge`, return the closest point, tangent, and\n"     \
"curvature of *entities* at *coords*. If *type* is\n"                          \
":data:`~itaps.iBase.Type.face`, return the closest point, normal, and\n"      \
"bothcurvatures of *entities* at *coords*. If *type* is unspecified, it\n"     \
"is inferred from the first element of *entities*.\n\n"                        \
":param entities: Entity or array of entities being queried\n"                 \
":param coords: Coordinate(s) being queried\n"                                 \
":param type: The :class:`~itaps.iBase.Type` of the supplied entities\n"       \
":param storage_order: Storage order of the vertices supplied and\n"           \
"                      returned\n"                                             \
":return: If *entities* or *coords* are arrays, a tuple of arrays of\n"        \
"         vectors representing the data for each entity. Otherwise, a\n"       \
"         tuple of vectors."

#define IGEOMDOC_iGeom_getEnt1stDerivative \
"Return pairwise data about the 1st deriviative of the specified\n"            \
"*entities* at *coords* as an :class:`~itaps.helpers.OffsetListTuple`\n"       \
"instance with fields named *u* and *v*.\n\n"                                  \
":param entities: Entity or array of entities being queried\n"                 \
":param coords: Coordinate(s) being queried\n"                                 \
":param storage_order: Storage order of the vertices supplied and\n"           \
"                      returned\n"                                             \
":return: If *entities* is a single :class:`~itaps.iBase.Entity`, a pair\n"    \
"         of vectors representing the 1st derivative. Otherwise, an\n"         \
"         :class:`~itaps.helpers.OffsetListTuple` instance with fields\n"      \
"         named *u* and *v*."

#define IGEOMDOC_iGeom_getEnt2ndDerivative \
"Return pairwise data about the 2nd deriviative of the specified\n"            \
"*entities* at *coords* as an :class:`~itaps.helpers.OffsetListTuple`\n"       \
"instance with fields named *uu*, *vv*, and *uv*.\n\n"                         \
":param entities: Entity or array of entities being queried\n"                 \
":param coords: Coordinate(s) being queried\n"                                 \
":param storage_order: Storage order of the vertices supplied and\n"           \
"                      returned\n"                                             \
":return: If *entities* is a single :class:`~itaps.iBase.Entity`, a\n"         \
"         triple of vectors representing the 2nd derivative. Otherwise,\n"     \
"         an :class:`~itaps.helpers.OffsetListTuple` instance with\n"          \
"         fields named *uu*, *vv*, and *uv*."

#define IGEOMDOC_iGeom_getPtRayIntersect \
"Intersect a ray or rays with the model and return the entities\n"             \
"intersected, the coordinates of intersection, and the distances along\n"      \
"the ray(s) at which the intersection occurred. If *points* and\n"             \
"*vectors* are single vectors, return a tuple containing the above data.\n"    \
"If both arearrays of vectors, return an\n"                                    \
":class:`~itaps.helpers.OffsetListTuple` instance with fields named\n"         \
"*entities*, *isect*, and *param*.\n\n"                                        \
":param points: Vector or array of vectors for the sources of the rays\n"      \
":param vectors: Vector or array of vectors for the direction of the\n"        \
"                rays\n"                                                       \
":param storage_order: Storage order of the vectors returned\n"                \
":return: If *points* and *vectors* are single vectors, a tuple of\n"          \
"         intersection data. If both are arrays of vectors, an\n"              \
"         :class:`~itaps.helpers.OffsetListTuple` instance with fields\n"      \
"         named *entities*, *isect*, and *param*."

#define IGEOMDOC_iGeom_getPtClass \
"Return the entity (or entities) on which a point (or points) lies.\n\n"       \
":param points: Point or array of points to query\n"                           \
":param storage_order: Storage order of the points supplied\n"                 \
":return: If *points* is a single point, the entity on which it lies.\n"       \
"         Otherwise, an array of entities."

#define IGEOMDOC_iGeom_getEntNormalSense \
"Return the pairwise sense of a face or array of faces with respect to a\n"    \
"region or array of regions. The sense is returned as -1, 0, or 1,\n"          \
"representing \"reversed\", \"both\", or \"forward\". A sense value of "       \
    "\"both\"\n"                                                               \
"indicates that face bounds the region once with each sense.\n\n"              \
"If *faces* is a single :class:`~itaps.iBase.Entity` or an array with\n"       \
"one element, return the sense of that entity with respect to each\n"          \
"entity in *regions*. Likewise, if *regions* is a single\n"                    \
":class:`~itaps.iBase.Entity`, return the sense of each of *faces* with\n"     \
"respect to that region.\n\n"                                                  \
":param faces: The face or array of faces to query\n"                          \
":param regions: The region or array of regions to query\n"                    \
":return: If *faces* and *regions* are both single\n"                          \
"         :class:`Entities <itaps.iBase.Entity>`, return the sense (as\n"      \
"         an integer). Otherwise, return an array of senses."

#define IGEOMDOC_iGeom_getEgFcSense \
"Return the pairwise sense of an edge or array of edges with respect to\n"     \
"a face or array of faces. The sense is returned as -1, 0, or 1,\n"            \
"representing \"reversed\", \"both\", or \"forward\". A sense value of "       \
    "\"both\"\n"                                                               \
"indicates that edge bounds the face once with each sense.\n\n"                \
"If *edges* is a single :class:`~itaps.iBase.Entity` or an array with\n"       \
"one element, return the sense of that entity with respect to each\n"          \
"entity in *faces*. Likewise, if *faces* is a single\n"                        \
":class:`~itaps.iBase.Entity`, return the sense of each of *edges* with\n"     \
"respect to that face.\n\n"                                                    \
":param edges: The edge or array of edges to query\n"                          \
":param faces: The face or array of faces to query\n"                          \
":return: If *edges* and *faces* are both single\n"                            \
"         :class:`Entities <itaps.iBase.Entity>`, return the sense (as\n"      \
"         an integer). Otherwise, return an array of senses."

#define IGEOMDOC_iGeom_getEgVtxSense \
"Return the pairwise sense of a pair of vertices or pair of array of\n"        \
"vertices with respect to an edge or array of edges. The sense is\n"           \
"returned as -1, 0, or 1, representing \"reversed\", \"both\", or "            \
    "\"forward\".\n"                                                           \
"A sense value of \"both\" indicates that the vertices bound the edge once\n"  \
"with each sense.\n\n"                                                         \
"If *vertices1* and *vertices2* are both single\n"                             \
":class:`Entities <itaps.iBase.Entity>` or arrays with one element each,\n"    \
"return the sense of those vertices with respect to each entity in\n"          \
"*edges*. Likewise, if *edges* is a single :class:`~itaps.iBase.Entity`,\n"    \
"return the sense of each of *vertices1* and *vertices2* with respect to\n"    \
"that edge.\n\n"                                                               \
":param edges: The edge or array of edges to query\n"                          \
":param vertices1: The first vertex or array of vertices to query\n"           \
":param vertices2: The second vertex or array of vertices to query\n"          \
":return: If *edges*, *vertices1*, and *vertices2* are alll single\n"          \
"         :class:`Entities <itaps.iBase.Entity>`, return the sense (as\n"      \
"         an integer). Otherwise, return an array of senses."

#define IGEOMDOC_iGeom_copyEnt \
"Copy the specified *entity* and return the duplicate.\n\n"                    \
":param entity: The entity to copy\n"                                          \
":return: The created entity"

#define IGEOMDOC_iGeom_moveEnt \
"Translate an entity in a particular direction.\n\n"                           \
":param entity: The entity to translate\n"                                     \
":param direction: A vector representing the displacement"

#define IGEOMDOC_iGeom_rotateEnt \
"Rotate an entity about an axis.\n\n"                                          \
":param entity: The entity to rotate\n"                                        \
":param angle: The angle (in degrees) to rotate the entity\n"                  \
":param axis: The axis about which to rotate the entity"

#define IGEOMDOC_iGeom_reflectEnt \
"Reflect an entity about an axis.\n\n"                                         \
":param entity: The entity to reflect\n"                                       \
":param axis: The axis about which to reflect the entity"

#define IGEOMDOC_iGeom_scaleEnt \
"Scale an entity in the x, y, and z directions.\n\n"                           \
":param entity: The entity to scale\n"                                         \
":param scale: A vector of the x, y, and z scaling factors"

#define IGEOMDOC_iGeom_sweepEntAboutAxis \
"Sweep (extrude) the specified *entity* about an axis.\n\n"                    \
":param entity: The entity to entity\n"                                        \
":param angle: The angle (in degrees) to sweep the entity\n"                   \
":param axis: The axis about which to sweep the entity\n"                      \
":return: The created entity"

#define IGEOMDOC_iGeom_uniteEnts \
"Geometrically unite the specified *entities* and return the result.\n"        \
"This method may also be called with ``uniteEnts(ent1, ent2, ent3)``.\n\n"     \
":param entities: The entities to unite\n"                                     \
":return: The resulting entity"

#define IGEOMDOC_iGeom_subtractEnts \
"Geometrically subtract *entity2* from *entity1* and return the result.\n\n"   \
":param entity1: The entity to be subtracted from\n"                           \
":param entity2: The entity to subtract\n"                                     \
":return: The resulting entity"

#define IGEOMDOC_iGeom_intersectEnts \
"Geometrically intersect *entity1* and *entity2* and return the result.\n\n"   \
":param entity1: An entity to intersect\n"                                     \
":param entity2: An entity to intersect\n"                                     \
":return: The resulting entity"

#define IGEOMDOC_iGeom_sectionEnt \
"Section an entity along a plane and return the result.\n\n"                   \
":param entity: The entity to section\n"                                       \
":param normal: The normal of the plane\n"                                     \
":param offset: The plane's offset from the origin\n"                          \
":param reverse: True is the resulting entity should be reversed, false\n"     \
"                otherwise.\n"                                                 \
":return: The resulting entity"

#define IGEOMDOC_iGeom_imprintEnts \
"Imprint the specified entities.\n\n"                                          \
":param entities: The entities to be imprinted"

#define IGEOMDOC_iGeom_mergeEnts \
"Merge the specified *entities* if they are within the specified\n"            \
"*tolerance*.\n\n"                                                             \
":param entities: The entities to merge\n"                                     \
":param tolerance: Tolerance for determining if entities should be\n"          \
"                  merged"

#define IGEOMDOC_iGeom_createEntSet \
"Create an :class:`EntitySet`, either ordered or unordered. Unordered\n"       \
"entity sets can contain a given entity or set only once.\n\n"                 \
":param ordered: True if the list should be ordered, false otherwise\n"        \
":return: The newly-created :class:`EntitySet`"

#define IGEOMDOC_iGeom_destroyEntSet \
"Destroy an entity set.\n\n"                                                   \
":param set: Entity set to be destroyed"

#define IGEOMDOC_iGeom_createTag \
"Create a :class:`Tag` with specified *name*, *size*, and *type*. The\n"       \
"tag's *size* is the number of values of type *type* that can be held.\n"      \
"*type* can be a NumPy dtype (or an object convertible to one;\n"              \
":class:`int` and :class:`~itaps.iBase.Entity` are special-cased), or a\n"     \
"single character:\n\n" \
"============================ =============== ================\n"              \
"Type object                  Type char       Result\n"                        \
"============================ =============== ================\n"              \
":class:`numpy.int32`         ``'i'``         Integer\n"                       \
":class:`numpy.float64`       ``'d'``         Double\n"                        \
":class:`~itaps.iBase.Entity` ``'E'``         Entity handle\n"                 \
":class:`numpy.byte`          ``'b'``         Binary data\n"                   \
"============================ =============== ================\n\n"            \
":param name: Tag name\n"                                                      \
":param size: Size of tag in number of values\n"                               \
":param type: Type object or character representing the tag's type\n"          \
":return: The created :class:`Tag`"

#define IGEOMDOC_iGeom_destroyTag \
"Destroy a :class:`Tag`. If *force* is true and entities still have\n"         \
"values set for this tag, the tag is deleted anyway and those values\n"        \
"disappear. Otherwise the tag is not deleted if entities still have\n"         \
"values set for it.\n\n"                                                       \
":param tag: :class:`Tag` to delete\n"                                         \
":param force: True if the tag should be deleted even if there are\n"          \
"              values set for it"

#define IGEOMDOC_iGeom_getTagHandle \
"Get the handle of an existing tag with the specified *name*.\n\n"             \
":param name: The name of the tag to find\n"                                   \
":return: The :class:`Tag` with the specified name"

#define IGEOMDOC_iGeom_getAllTags \
"Get all the tags associated with a specified entity or entity set.\n\n"       \
":param entities: Entity or entity set being queried\n"                        \

/***** iGeom.EntitySet *****/

#define IGEOMDOC_iGeomEntSet \
"Return a new set referring to the handled contained in  *set*. If *set* is\n" \
"an :class:`itaps.iBase.EntitySet` instance, *instance* must also be\n"        \
"specified."

#define IGEOMDOC_iGeomEntSet_instance \
"Return the :class:`Geom` instance from which this entity set was\n"           \
"created."

#define IGEOMDOC_iGeomEntSet_isList \
"Return whether this entity set is ordered."

#define IGEOMDOC_iGeomEntSet_getNumOfType \
"Get the number of entities with the specified type in this entity set.\n\n"   \
":param type: Type of entity requested\n"                                      \
":return: The number of entities in this entity set of the requested\n"        \
"         type"

#define IGEOMDOC_iGeomEntSet_getEntities \
"Get entities of a specific type in this entity set. All entities of a\n"      \
"given type are requested by specifying :attr:`itaps.iBase.Type.all`.\n\n"     \
":param type: Type of entities being requested\n"                              \
":return: Array of entity handles from this entity set meeting the\n"          \
"         requirements of *type*"

#define IGEOMDOC_iGeomEntSet_getNumEntSets \
"Get the number of sets contained in this entity set. If this entity set\n"    \
"is not the root set, *hops* indicates the maximum number of contained\n"      \
"sets from this set to one of the contained sets, inclusive of this set.\n\n"  \
":param hops: Maximum number of contained sets from this set to a\n"           \
"             contained set, not including itself\n"                           \
":return: Number of entity sets found"

#define IGEOMDOC_iGeomEntSet_getEntSets \
"Get the sets contained in this entity set. If this entity set is not\n"       \
"the root set, *hops* indicates the maximum number of contained sets\n"        \
"from this set to one of the contained sets, inclusive of this set.\n\n"       \
":param hops: Maximum number of contained sets from this set to a\n"           \
"             contained set, not including itself\n"                           \
":return: Array of entity sets found"

#define IGEOMDOC_iGeomEntSet_add \
"Add an entity, entity set, or array of entities to this entity set.\n\n"      \
":param entities: The entity, entity set, or array of entities to add"

#define IGEOMDOC_iGeomEntSet_remove \
"Remove an entity, entity set, or array of entities from this entity\n"        \
"set.\n\n"                                                                     \
":param entities: The entity, entity set, or array of entities to remove"

#define IGEOMDOC_iGeomEntSet_contains \
"Return whether an entity, entity set, or array of entities is contained\n"    \
"in this entity set.\n\n"                                                      \
":param entities: The entity, entity set, or array of entities to query\n"     \
":return: If *entities* is an array of entities, an array of booleans\n"       \
"         corresponding to each element of *entities*. Otherwise, a\n"         \
"         single boolean."

#define IGEOMDOC_iGeomEntSet_addChild \
"Add *set* as a child to this entity set.\n\n"                                 \
":param set: The entity set to add"

#define IGEOMDOC_iGeomEntSet_removeChild \
"Remove *set* as a child from this entity set.\n\n"                            \
":param set: The entity set to remove"

#define IGEOMDOC_iGeomEntSet_isChild \
"Return whether an entity set is a child of this entity set.\n\n"              \
":param set: The entity set to query:\n"                                       \
":return: True if *set* is a child of this entity set, false otherwise"

#define IGEOMDOC_iGeomEntSet_getNumChildren \
"Get the number of child sets linked from this entity set. If *hops*\n"        \
"is non-zero, this represents the maximum hops from this entity set to\n"      \
"any child in the count.\n\n"                                                  \
":param hops: Maximum hops from this entity set to a child set,\n"             \
"             not inclusive of the child set\n"                                \
":return: Number of children"

#define IGEOMDOC_iGeomEntSet_getNumParents \
"Get the number of parent sets linked from this entity set. If *hops*\n"       \
"is non-zero, this represents the maximum hops from this entity set to\n"      \
"any parents in the count.\n\n"                                                \
":param hops: Maximum hops from this entity set to a parent set,\n"            \
"             not inclusive of the parent set\n"                               \
":return: Number of parents"

#define IGEOMDOC_iGeomEntSet_getChildren \
"Get the child sets linked from this entity set. If *hops* is\n"               \
"non-zero, this represents the maximum hops from this entity set to any\n"     \
"child in the result.\n\n"                                                     \
":param hops: Maximum hops from this entity set to a child set,\n"             \
"             not inclusive of the child set\n"                                \
":return: Array of children"

#define IGEOMDOC_iGeomEntSet_getParents \
"Get the parents sets linked from this entity set. If *hops* is\n"             \
"non-zero, this represents the maximum hops from this entity set to any\n"     \
"parent in the result.\n\n"                                                    \
":param hops: Maximum hops from this entity set to a parent set,\n"            \
"             not inclusive of the parent set\n"                               \
":return: Array of parents"

#define IGEOMDOC_iGeomEntSet_iterate \
"Initialize an :class:`Iterator` over the specified entity type for this\n"    \
"entity set. If *count* is greater than 1, each step of the iteration\n"       \
"returns an array of *count* entities. Equivalent to::\n\n"                    \
"  itaps.iGeom.Iterator(self, type, count)\n\n"                                \
":param type: Type of entities being requested\n"                              \
":param count: Number of entities to return on each step of iteration\n"       \
":return: An :class:`Iterator` instance"

#define IGEOMDOC_iGeomEntSet_difference \
"Subtract contents of an entity set from this set. Equivalent to\n"            \
"``self - set``.\n\n"                                                          \
":param set: Entity set to subtract\n"                                         \
":return: Resulting entity set"

#define IGEOMDOC_iGeomEntSet_intersection \
"Intersect contents of an entity set with this set. Equivalent to\n"           \
"``self & set``.\n\n"                                                          \
":param set: Entity set to intersect\n"                                        \
":return: Resulting entity set"

#define IGEOMDOC_iGeomEntSet_union \
"Unite contents of an entity set with this set. Equivalent to\n"               \
"``self | set``.\n\n"                                                          \
":param set: Entity set to unite\n"                                            \

/***** iGeom.Iterator *****/

#define IGEOMDOC_iGeomIter \
"Return a new iterator on the entity set *set* to iterate over entities of\n"  \
"the specified *type*. If *count* is greater than 1, each step of the\n"       \
"iteration will return an array of *count* entities. All entities of a given\n"\
"type are requested by specifying :attr:`itaps.iBase.Type.all`.\n\n"           \
":param set: Entity set to iterate over\n"                                     \
":param type: Type of entities being requested\n"                              \
":param count: Number of entities to return on each step of iteration"

#define IGEOMDOC_iGeomIter_instance \
"Return the :class:*Geom* instance from which this iterator was created."

#define IGEOMDOC_iGeomIter_reset \
"Resets the iterator to the beginning."

/***** iGeom.Tag *****/

#define IGEOMDOC_iGeomTag \
"Return a new tag referring to the handled contained in *tag*. If *tag* is\n"  \
"an :class:`itaps.iBase.Tag` instance, *instance* must also be specified."

#define IGEOMDOC_iGeomTag_instance \
"Return the :class:`Geom` instance from which this tag was created."

#define IGEOMDOC_iGeomTag_name \
"Get the name for this tag."

#define IGEOMDOC_iGeomTag_sizeValues \
"Get the size in number of values for this tag."

#define IGEOMDOC_iGeomTag_sizeBytes \
"Get the size in bytes for this tag."

#define IGEOMDOC_iGeomTag_type \
"Get the data type for this tag as a character code (see above)."

#define IGEOMDOC_iGeomTag_get \
"Get the tag data for an entity, entity set, or array of entities. This\n"     \
"method is equivalent to `tag[entities]``.\n\n"                                \
":param entities: Entity, entity set, or array of entities to get\n"           \
":return: The tag data for *entities*"

#define IGEOMDOC_iGeomTag_getData \
"Get the tag data for an entity, entity set, or array of entities. This\n"     \
"method is deprecated in favor of ``tag[entities]``."

#define IGEOMDOC_iGeomTag_setData \
"Set the tag data for an entity, entity set, or array of entities to\n"        \
"*data*. This method is deprecated in favor of ``tag[entities] = data``."

#define IGEOMDOC_iGeomTag_remove \
"Remove the tag data for an entity, entity set, or array of entities.\n"       \
"This method is deprecated in favor of ``del tag[entities]``."

#endif
