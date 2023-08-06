#ifndef PYTAPS_ERRORS_H
#define PYTAPS_ERRORS_H

#define ERR_ENT_OR_ENTARR     "entity or entity array expected"
#define ERR_ENT_OR_ENTSET     "entity or entity set expected"
#define ERR_ANY_ENT           "entity, entity array, or entity set expected"
#define ERR_ARR_SIZE          "unexpected array size"
#define ERR_ARR_DIMS          "1- or 2-dimensional array expected"
#define ERR_TYPE_CODE         "invalid type code"
#define ERR_ADJ_LIST          "unable to create adjacency list"
#define ERR_ISECT_LIST        "unable to create intersection list"
#define ERR_INVALID_BASIS     "invalid basis"
#define ERR_INFER_BASIS       "cannot infer basis"
#define ERR_ENT_TYPE          "invalid entity type"
#define ERR_ARR_TYPE          "invalid element type"
#define ERR_ARR_INSTANCE      "members of array must have same base instance"
#define ERR_ARR_BASE          "unable to retrieve array base"
#define ERR_EXP_INSTANCE      "expected instance"
#define ERR_WRONG_INSTANCE    "instances don't match"
#define ERR_MESH_SET_CTOR     "cannot take instance and iMesh.EntitySet"
#define ERR_MESH_TAG_CTOR     "cannot take instance and iMesh.Tag"
#define ERR_GEOM_SET_CTOR     "cannot take instance and iGeom.EntitySet"
#define ERR_GEOM_TAG_CTOR     "cannot take instance and iGeom.Tag"
#define ERR_UNKNOWN_INST      "unknown iBase instance"
#define ERR_NO_SRC_DST        "must supply src and/or dest"
#define ERR_INVALID_STG       "invalid storage order"
#define ERR_INVALID_TYPE      "invalid type"
#define ERR_INVALID_TOPO      "invalid topology"
#define ERR_INVALID_RELTYPE   "invalid relation type"
#define ERR_INVALID_RELSTATUS "invalid relation status"
#define ERR_INVALID_OUT       "unable to parse 'out' argument"

#define WARN_TAG_GET          "tag.getData(entities) is deprecated. Use " \
                              "tag[entities] instead."
#define WARN_TAG_SET          "tag.setData(entities, value) is deprecated. " \
                              "Use tag[entities] = value instead."
#define WARN_TAG_REMOVE       "tag.remove(entities) is deprecated. Use del " \
                              "tag[entities] instead."
#define WARN_OUT_UNUSED       "output buffer ignored"

#endif
