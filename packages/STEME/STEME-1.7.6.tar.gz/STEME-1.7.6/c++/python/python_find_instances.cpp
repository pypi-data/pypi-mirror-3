/** Copyright John Reid 2011
 *
 * \file Exposes find instances part of STEME algorithm to python.
 */

#include "steme_python_defs.h"

#include <steme/find_instances.h>

namespace py = boost::python;
using namespace steme;
using namespace steme::python;


typedef find_instances< STEME_INDEX_MODULE_SPEC > find_instances_t;
typedef data< STEME_INDEX_MODULE_SPEC > data_t;
typedef model< STEME_INDEX_MODULE_SPEC > model_t;



find_instances_t::instances_vec_ptr
get_best_non_overlapping( find_instances_t::instances_vec & instances, int W, bool already_sorted_by_position ) {
    find_instances_t::instances_vec_ptr result( new find_instances_t::instances_vec );
    output_non_overlapping_instances(
        instances,
        W,
        std::back_inserter( *result ),
        already_sorted_by_position
    );
    return result;
}


void
expose_find_instances() {


    py::class_<
        find_instances_t,
        find_instances_t::ptr,
        boost::noncopyable
    > find_instances_class(
        "FindInstances",
        "Finds the instances of the model in the data (above a given Z threshold).",
        py::init<
            data_t &,
            model_t &,
            double
        >(
            (
                py::args( "data" ),
                py::args( "model" ),
                py::args( "Z_threshold" )
            ),
            "Constructor."
        )
    );
    find_instances_class.def( "__call__", &find_instances_t::descend_tree, "Find the best W-mers." );
    find_instances_class.def_readonly( "instances", &find_instances_t::instances, "Instances." );
    expose_tree_descender< find_instances_t >( find_instances_class );

    py::class_<
        find_instances_t::instances_vec,
        find_instances_t::instances_vec_ptr
    > instance_vec_class( "InstanceVec" );
    instance_vec_class.def(
        py::indexing::container_suite< find_instances_t::instances_vec >()
    );
    instance_vec_class.def( "sort_by_position", sort_instances_by_position< find_instances_t::instances_vec >, "Sort the instances by position." );
    instance_vec_class.def(
        "get_best_non_overlapping",
        get_best_non_overlapping,
        (
            py::arg( "instances" ),
            py::arg( "W" ),
            py::arg( "already_sorted_by_position" ) = false
        ),
        "Get the best instances that don't overlap."
    );
    instance_vec_class.def(
        "do_instances_overlap",
        do_instances_overlap< find_instances_t::instances_vec >,
        (
            py::arg( "instances" ),
            py::arg( "W" ),
            py::arg( "already_sorted_by_position" ) = false
        ),
        "Do the instances overlap?"
    );
}


