#ifndef PYTAPS_IMESH_DOC_H
#define PYTAPS_IMESH_DOC_H

/***** iMesh.Mesh *****/

#define IMESHDOC_iMesh \
"Return a new :class:`Mesh` object with any implementation-specific\n"         \
"optionsdefined in *options*.\n\n"                                             \
":param options: Implementation-specific options string"

#define IMESHDOC_iMesh_rootSet \
"Return the handle of the root set for this instance. The entire mesh\n"       \
"in this instance can be accessed from this set."

#define IMESHDOC_iMesh_geometricDimension \
"Get/set the geometric dimension of mesh represented in this\n"                \
"instance. When setting the dimension, an application should not\n"            \
"expect this function to succeed unless the mesh database is empty\n"          \
"(no vertices created, no files read, etc.)"

#define IMESHDOC_iMesh_defaultStorage \
"Return the default storage order used by this implementation."

#define IMESHDOC_iMesh_adjTable \
"Return the adjacency table for this implementation.  This table is\n"         \
"a 4x4 matrix, where *adjTable[i][j]* represents the relative cost of\n"       \
"retrieving adjacencies between entities of dimension *i* to entities\n"       \
"of dimension *j*."

#define IMESHDOC_iMesh_optimize \
"Request that the mesh optimize the storage of its entities, possibly\n"       \
"rearranging the entities and invalidating extisting handles.\n\n"             \
":return: True if entity handles have changed"

#define IMESHDOC_iMesh_createVtx \
"Create a vertex or array of vertices with the specified\n"                    \
"coordinates.\n\n"                                                             \
":param coords: Coordinates of new vertices to create\n"                       \
":param storage_order: Storage order of coordinates"

#define IMESHDOC_iMesh_createEnt \
"Create a new entity with the specified lower-order topology.\n\n"             \
":param topo: Topology of the entity to be created\n"                          \
":param entities: Array of lower order entity handles used to\n"               \
"                 construct the new entity\n"                                  \
":return: Tuple containing the created entity and its creation\n"              \
"         status"

#define IMESHDOC_iMesh_createEntArr \
"Create an array of new entities with the specified lower-oder\n"              \
"topology.\n\n"                                                                \
":param topo: Topology of the entities to be created\n"                        \
":param entities: Array of lower order entity handles used to\n"               \
"                 construct the new entities\n"                                \
":return: Tuple containing the created entities and their creation\n"          \
"         statuses"

#define IMESHDOC_iMesh_deleteEnt \
"Delete the specified entity or array of entities.\n\n"                        \
":param entities: An entity or array of entities to delete"

#define IMESHDOC_iMesh_getVtxCoords \
"Get coordinates of specified vertices.\n\n"                                   \
":param entities: Entity or array of entities being queried\n"                 \
":param storage_order: Storage order of vertices to be returned\n"             \
":return: If *entities* is a single :class:`~itaps.iBase.Entity`,\n"           \
"         the coordinates of the vertex. Otherwise, an array of\n"             \
"         coordinates."

#define IMESHDOC_iMesh_setVtxCoords \
"Set the coordinates for the specified vertex or array of vertices.\n\n"       \
":param entities: Vertex handle or array of vertex handles being set\n"        \
":param coords: New coordinates to assign to vertices\n"                       \
":param storage_order: Storage order of coordinates to be assigned"

#define IMESHDOC_iMesh_getEntType \
"Get the entity type for the specified entities.\n\n"                          \
":param entities: Entity or array of entities being queried\n"                 \
":return: If *entities* is a single :class:`~itaps.iBase.Entity`,\n"           \
"         the type of the entity. Otherwise, an array of the entity\n"         \
"         types."

#define IMESHDOC_iMesh_getEntTopo \
"Get the entity topology for the specified entities.\n\n"                      \
":param entities: Entity or array of entities being queried\n"                 \
":return: If *entities* is a single :class:`~itaps.iBase.Entity`,\n"           \
"         the topology of the entity. Otherwise, an array of the\n"            \
"         entity topologies."

#define IMESHDOC_iMesh_getEntAdj \
"Get entities of the specified type adjacent to elements of\n"                 \
"*entities*. If *entities* is a single :class:`~itaps.iBase.Entity`,\n"        \
"returns an array of adjacent entities. If *entities* is an array of\n"        \
"entities, return an :class:`~itaps.helpers.OffsetListSingle`\n"               \
"instance.\n\n"                                                                \
":param entities: Entity or array of entities being queried\n"                 \
":param type: Type of adjacent entities being requested\n"                     \
":return: If *entities* is a single :class:`~itaps.iBase.Entity` an\n"         \
"         array of adjacent entities. Otherwise, an\n"                         \
"         :class:`~itaps.helpers.OffsetListSingle` instance."

#define IMESHDOC_iMesh_getEnt2ndAdj \
"Get \"2nd order\" adjacencies to an array of entities, that is, from\n"       \
"each entity, through other entities of a specified bridge\n"                  \
"dimension, to other entities of another specified target dimension.\n"        \
"If *entities* is a single :class:`~itaps.iBase.Entity`, returns an\n"         \
"array of adjacent entities. If *entities* is an array of entities,\n"         \
"return an :class:`~itaps.helpers.OffsetListSingle` instance.\n\n"             \
":param entities: Entity or array of entities being queried\n"                 \
":param bridge_type: Type of bridge entity for 2nd order adjacencies\n"        \
":param type: Type of adjacent entities being requested\n"                     \
":return: If *entities* is a single :class:`~itaps.iBase.Entity`, an\n"        \
"         array of adjacent entities. Otherwise, an\n"                         \
"         :class:`~itaps.helpers.OffsetListSingle` instance."

#define IMESHDOC_iMesh_createEntSet \
"Create an :class:`EntitySet`, either ordered or unordered.\n"                 \
"Unordered entity sets can contain a given entity or set only once.\n\n"       \
":param ordered: True if the list should be ordered, false otherwise\n"        \
":return: The newly-created :class:`EntitySet`"

#define IMESHDOC_iMesh_destroyEntSet \
"Destroy an entity set.\n\n"                                                   \
":param set: Entity set to be destroyed"

#define IMESHDOC_iMesh_createTag \
"Create a :class:`Tag` with specified *name*, *size*, and *type*.\n"           \
"The tag's *size* is the number of values of type *type* that can be\n"        \
"held. *type* can be a NumPy dtype (or an object convertible to one;\n"        \
":class:`int` and :class:`~itaps.iBase.Entity` are special-cased),\n"          \
"or a single character:\n\n"                                                   \
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

#define IMESHDOC_iMesh_destroyTag \
"Destroy a :class:`Tag`. If *force* is true and entities still have\n"         \
"values set for this tag, the tag is deleted anyway and those values\n"        \
"disappear. Otherwise the tag is not deleted if entities still have\n"         \
"values set for it.\n\n"                                                       \
":param tag: :class:`Tag` to delete\n"                                         \
":param forced: True if the tag should be deleted even if there are\n"         \
"               values set for it"

#define IMESHDOC_iMesh_getTagHandle \
"Get the handle of an existing tag with the specified *name*.\n\n"             \
":param name: The name of the tag to find\n"                                   \
":return: The :class:`Tag` with the specified name"

#define IMESHDOC_iMesh_getAllTags \
"Get all the tags associated with a specified entity or entity set.\n\n"       \
":param entities: Entity or entity set being queried\n"                        \
":return: Array of :class:`Tag`\\ s associated with *entities*"

/***** iMesh.EntitySet *****/

#define IMESHDOC_iMeshEntSet \
"Return a new set referring to the handled contained in *set*. If *set*\n"     \
"is an :class:`itaps.iBase.EntitySet` instance, *instance* must also be\n"     \
"specified."

#define IMESHDOC_iMeshEntSet_instance \
"Return the :class:`Mesh` instance from which this entity set was\n"           \
"created."

#define IMESHDOC_iMeshEntSet_isList \
"Return whether this entity set is ordered."

#define IMESHDOC_iMeshEntSet_load \
"Load a mesh from a file, adding it to this entity set.\n\n"                   \
":param filename: File name from which the mesh is to be loaded\n"             \
":param options: Implementation-specific options string"

#define IMESHDOC_iMeshEntSet_save \
"Save the subset of the mesh contained in this entity set to a file.\n\n"      \
":param filename: File name to which the mesh is to be saved\n"                \
":param options: Implementation-specific options string"

#define IMESHDOC_iMeshEntSet_getNumOfType \
"Get the number of entities with the specified type in this entity\n"          \
"set.\n\n"                                                                     \
":param type: Type of entity requested\n"                                      \
":return: The number of entities in entity set of the requested type"

#define IMESHDOC_iMeshEntSet_getNumOfTopo \
"Get the number of entities with the specified topology in this\n"             \
"entity set.\n\n"                                                              \
":param topo: Topology of entity requested\n"                                  \
":return: The number of entities in the entity set of the requested\n"         \
"         topology"

#define IMESHDOC_iMeshEntSet_getEntities \
"Get entities of a specific type and/or topology in this entity set.\n"        \
"All entities of a given type or topology are requested by\n"                  \
"specifying :attr:`itaps.iBase.Type.all` or \n"                                \
":attr:`itaps.iMesh.Topology.all`, respectively.\n\n"                          \
":param type: Type of entities being requested\n"                              \
":param topo: Topology of entities being requested\n"                          \
":return: Array of entity handles from this entity set meeting the\n"          \
"         requirements of *type* and *topo*"

#define IMESHDOC_iMeshEntSet_getAdjEntIndices \
"Given an entity set and optionally a type or topology, return a\n"            \
"tuple containing the entities in the set of type *type* and\n"                \
"topology *topo*, and an :class:`~itaps.helpers.IndexedList`\n"                \
"containing the adjacent entities of type *adj_type*.\n\n"                     \
":param type: Type of entities being requested\n"                              \
":param topo: Topology of entities being requested\n"                          \
":param adjType: Type of adjacent entities being requested\n"                  \
":return: A tuple containing the requested entities and the adjacent\n"        \
"         entities"

#define IMESHDOC_iMeshEntSet_getNumEntSets \
"Get the number of sets contained in this entity set. If this entity\n"        \
"set is not the root set, *hops* indicates the maximum number of\n"            \
"contained sets from this set to one of the contained sets,\n"                 \
"inclusive of this set.\n\n"                                                   \
":param hops: Maximum number of contained sets from this set to a\n"           \
"             contained set, not including itself\n"                           \
":return: Number of entity sets found"

#define IMESHDOC_iMeshEntSet_getEntSets \
"Get the sets contained in this entity set. If this entity set is\n"           \
"not the root set, *hops* indicates the maximum number of contained\n"         \
"sets from this set to one of the contained sets, inclusive of this\n"         \
"set.\n\n"                                                                     \
":param hops: Maximum number of contained sets from this set to a\n"           \
"             contained set, not including itself\n"                           \
":return: Array of entity sets found"

#define IMESHDOC_iMeshEntSet_add \
"Add an entity, entity set, or array of entities to this entity set.\n\n"      \
":param entities: The entity, entity set, or array of entities to\n"           \
"                 add"

#define IMESHDOC_iMeshEntSet_remove \
"Remove an entity, entity set, or array of entities from this entity\n"        \
"set.\n\n"                                                                     \
":param entities: The entity, entity set, or array of entities to\n"           \
"                 remove"

#define IMESHDOC_iMeshEntSet_contains \
"Return whether an entity, entity set, or array of entities is\n"              \
"contained in this entity set.\n\n"                                            \
":param entities: The entity, entity set, or array of entities to\n"           \
"                 query\n"                                                     \
":return: If *entities* is an array of entities, an array of\n"                \
"         booleans corresponding to each element of *entities*.\n"             \
"         Otherwise, a single boolean."

#define IMESHDOC_iMeshEntSet_isChild \
"Return whether an entity set is a child of this entity set.\n\n"              \
":param set: The entity set to query\n"                                        \
":return: True if *set* is a child of this entity set, false\n"                \
"         otherwise"

#define IMESHDOC_iMeshEntSet_getNumChildren \
"Get the number of child sets linked from this entity set. If *hops*\n"        \
"is non-zero, this represents the maximum hops from this entity set\n"         \
"to any child in the count.\n\n"                                               \
":param hops: Maximum hops from this entity set to a child set,\n"             \
"             not inclusive of the child set\n"                                \
":return: Number of children"

#define IMESHDOC_iMeshEntSet_getNumParents \
"Get the number of parent sets linked from this entity set. If\n"              \
"*hops* is non-zero, this represents the maximum hops from this\n"             \
"entity set to any parents in the count.\n\n"                                  \
":param hops: Maximum hops from this entity set to a parent set,\n"            \
"             not inclusive of the parent set\n"                               \
":return: Number of parents"

#define IMESHDOC_iMeshEntSet_getChildren \
"Get the child sets linked from this entity set. If *hops* is\n"               \
"non-zero, this represents the maximum hops from this entity set to\n"         \
"any child in the result.\n\n"                                                 \
":param hops: Maximum hops from this entity set to a child set,\n"             \
"             not inclusive of the child set\n"                                \
":return: Array of children"

#define IMESHDOC_iMeshEntSet_getParents \
"Get the parents sets linked from this entity set. If *hops* is\n"             \
"non-zero, this represents the maximum hops from this entity set to\n"         \
"any parent in the result.\n\n"                                                \
":param hops: Maximum hops from this entity set to a parent set,\n"            \
"             not inclusive of the parent set\n"                               \
":return: Array of parents"

#define IMESHDOC_iMeshEntSet_addChild \
"Add *set* as a child to this entity set.\n\n"                                 \
":param set: The entity set to add"

#define IMESHDOC_iMeshEntSet_removeChild \
"Remove *set* as a child from this entity set.\n\n"                            \
":param set: The entity set to remove"

#define IMESHDOC_iMeshEntSet_iterate \
"Initialize an :class:`Iterator` over the specified entity type and\n"         \
"topology for this entity set. If *count* is greater than 1, each\n"           \
"step of the iteration returns an array of *count* entities.\n"                \
"Equivalent to::\n\n"                                                          \
"  itaps.iMesh.Iterator(self, type, topo, count)\n\n"                          \
":param type: Type of entities being requested\n"                              \
":param topo: Topology of entities being requested\n"                          \
":param count: Number of entities to return on each step of\n"                 \
"              iteration\n"                                                    \
":return: An :class:`Iterator` instance"

#define IMESHDOC_iMeshEntSet_difference \
"Subtract contents of an entity set from this set. Equivalent to\n"            \
"``self - set``.\n\n"                                                          \
":param set: Entity set to subtract\n"                                         \
":return: Resulting entity set"

#define IMESHDOC_iMeshEntSet_intersection \
"Intersect contents of an entity set with this set. Equivalent to\n"           \
"``self & set``.\n\n"                                                          \
":param set: Entity set to intersect\n"                                        \
":return: Resulting entity set"

#define IMESHDOC_iMeshEntSet_union \
"Unite contents of an entity set with this set. Equivalent to\n"               \
"``self | set``.\n\n"                                                          \
":param set: Entity set to unite\n"                                            \
":return: Resulting entity set"

/***** iMesh.Iterator *****/

#define IMESHDOC_iMeshIter \
"Return a new iterator on the entity set *set* to iterate over entities\n"     \
"of the specified *type* and *topo*. If *size* is greater than 1, each\n"      \
"step of the iteration will return an array of *size* entities. All\n"         \
"entities of a given type or topology are requested by specifying\n"           \
":attr:`itaps.iBase.Type.all` or :attr:`itaps.iMesh.Topology.all`,\n"          \
"respectively.\n\n"                                                            \
":param set: Entity set to iterate over\n"                                     \
":param type: Type of entities being requested\n"                              \
":param topo: Topology of entities being requested\n"                          \
":param count: Number of entities to return on each step of iteration"

#define IMESHDOC_iMeshIter_instance \
"Return the :class:`Mesh` instance from which this iterator was\n"             \
"created."

#define IMESHDOC_iMeshIter_reset \
"Resets the iterator to the beginning."

/***** iMesh.Tag *****/

#define IMESHDOC_iMeshTag \
"Return a new tag referring to the handled contained in *tag*. If *tag*\n"     \
"is an :class:`itaps.iBase.Tag` instance, *instance* must also be\n"           \
"specified."

#define IMESHDOC_iMeshTag_instance \
"Return the :class:`Mesh` instance from which this tag was created."

#define IMESHDOC_iMeshTag_name \
"Get the name for this tag."

#define IMESHDOC_iMeshTag_sizeValues \
"Get the size in number of values for this tag."

#define IMESHDOC_iMeshTag_sizeBytes \
"Get the size in bytes for this tag."

#define IMESHDOC_iMeshTag_type \
"Get the data type for this tag as a character code (see above)."

#define IMESHDOC_iMeshTag_get \
"Get the tag data for an entity, entity set, or array of entities.\n"          \
"This method is equivalent to `tag[entities]``.\n\n"                           \
":param entities: Entity, entity set, or array of entities to get\n"           \
":return: The tag data for *entities*"

#define IMESHDOC_iMeshTag_getData \
"Get the tag data for an entity, entity set, or array of entities.\n"          \
"This method is deprecated in favor of ``tag[entities]``."

#define IMESHDOC_iMeshTag_setData \
"Set the tag data for an entity, entity set, or array of entities to\n"        \
"*data*. This method is deprecated in favor of\n"                              \
"``tag[entities] = data``."

#define IMESHDOC_iMeshTag_remove \
"Remove the tag data for an entity, entity set, or array of\n"                 \
"entities. This method is deprecated in favor of\n"                            \
"``del tag[entities]``."

#endif
