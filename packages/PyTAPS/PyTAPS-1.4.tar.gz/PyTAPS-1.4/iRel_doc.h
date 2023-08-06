#ifndef PYTAPS_IREL_DOC_H
#define PYTAPS_IREL_DOC_H

/***** iRel.Rel *****/

#define IRELDOC_iRel \
"Return a new :class:`Rel` object with any implementation-specific\n"          \
"options defined in *options*.\n\n"                                            \
":param options: Implementation-specific options string"

#define IRELDOC_iRel_createPair \
"Create a new relation pair between two ITAPS interfaces.\n\n"                 \
":param left: The interface on the left half of the pair\n"                    \
":param left_type: The relation :class:`Type` for the first\n"                 \
"                  interface\n"                                                \
":param left_status: The relation :class:`Status` for the first\n"             \
"                    interface\n"                                              \
":param right: The interface on the right half of the pair\n"                  \
":param right_type: The relation :class:`Type` for the second\n"               \
"                   interface\n"                                               \
":param right_status: The relation :class:`Status` for the second\n"           \
"                     interface\n"                                             \
":return: The newly-created relation pair"

#define IRELDOC_iRel_destroyPair \
"Destroy a relation pair.\n\n"                                                 \
":param pair: The relation pair to be destroyed"

#define IRELDOC_iRel_findPairs \
"Find all relation pairs that contain the specified *interface*.\n\n"          \
":param interface: The interface to search for\n"                              \
":return: A list of relation pairs"

/***** iRel.Pair *****/

#define IRELDOC_iRelPair \
"An association between two ITAPS interfaces allowing their entities or\n"     \
"sets to be related to one another."

#define IRELDOC_iRelPair_instance \
"Return the :class:`Rel` instance from which this pair was created."

#define IRELDOC_iRelPair_left \
"Return the :class:`PairSide` corresponding to the left half of this\n"        \
"relation pair."

#define IRELDOC_iRelPair_right \
"Return the :class:`PairSide` corresponding to the right half of\n"            \
"this relation pair."

#define IRELDOC_iRelPair_changeType \
"Change the type of one or both sides of a relation pair. Only\n"              \
"changes that result in no lost information are allowed, e.g.\n"               \
"changing a type from *set* to *both* or vice versa.\n\n"                      \
":param left: The relation :class:`Type` for the first\n"                      \
"             interface\n"                                                     \
":param right: The relation :class:`Type` for the first\n"                     \
"              interface"

#define IRELDOC_iRelPair_changeStatus \
"Change the status of one or both sides of a relation pair.\n\n"               \
":param left: The relation :class:`Status` for the first\n"                    \
"             interface\n"                                                     \
":param right: The relation :class:`Status` for the first\n"                   \
"              interface"

#define IRELDOC_iRelPair_relate \
"Relate two elements (entities or sets) to one another. If *left*\n"           \
"and *right* are arrays, relate the elements pairwise.\n\n"                    \
":param left: :class:`~itaps.iBase.Entity` or\n"                               \
"             :class:`~itaps.iBase.EntitySet` from the left half of\n"         \
"             the relation pair\n"                                             \
":param right: :class:`~itaps.iBase.Entity` or\n"                              \
"              :class:`~itaps.iBase.EntitySet` from the right half\n"          \
"              of the relation pair"

#define IRELDOC_iRelPair_inferAllRelations \
"Infer the relations between elements (entities or sets) in the\n"             \
"interfaces defined by this relation pair. The criteria used to\n"             \
"infer these relations depends on the interfaces in the pair, the\n"           \
"iRel implementation, and the source of the data in those\n"                   \
"interfaces."

#define IRELDOC_iRelPairSide \
"One half of a :class:`Pair`, corresponding to a given side of the\n"          \
"relation pair."

#define IRELDOC_iRelPairSide_instance \
"Return the instance corresponding to the this side of the relation\n"         \
"pair."

#define IRELDOC_iRelPairSide_type \
"Return the relation :class:`Type` of the this side of the relation\n"         \
"pair."

#define IRELDOC_iRelPairSide_status \
"Return the relation :class:`Status` of the this side of the\n"                \
"relation pair."

#define IRELDOC_iRelPairSide_get \
"Get the entity/set related to the specified element. If the input\n"          \
"is an array of elements, this function returns pairwise relations.\n\n"       \
":param entities: :class:`~itaps.iBase.Entity` or\n"                           \
"                 :class:`~itaps.iBase.EntitySet` from the left half\n"        \
"                 of the relation pair\n"                                      \
":return: The related entity"

#define IRELDOC_iRelPairSide_inferRelations \
"Infer the relations corresponding to the supplied element(s)\n"               \
"(entities or sets) in the interfaces defined by this relation pair.\n"        \
"The criteria used to infer these relations depends on the\n"                  \
"interfaces in the pair, the iRel implementation, and the source of\n"         \
"the data in those interfaces.\n\n"                                            \
":param entities: :class:`~itaps.iBase.Entity` or\n"                           \
"                 :class:`~itaps.iBase.EntitySet` from the left half\n"        \
"                 of the relation pair"

#endif
