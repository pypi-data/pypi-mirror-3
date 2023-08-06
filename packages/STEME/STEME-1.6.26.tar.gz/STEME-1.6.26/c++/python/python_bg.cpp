/** Copyright John Reid 2011
 *
 * \file Exposes background parts of STEME algorithm to python.
 */

#include "steme_python_defs.h"

#include <steme/background_model.h>
#include <steme/data.h>

#include <myrrh/python/boost_range.h>

#include <boost/preprocessor/repetition/repeat_from_to.hpp>

namespace py = boost::python;
using namespace steme;
using namespace steme::python;

typedef data< EXPOSED_STEME_SPEC > data_t;



double
get_freq( const zero_order_frequencies & freqs, size_t base ) {
	if( base >= freqs.dist.size() ) {
		throw std::out_of_range( "Index into frequencies out of range." );
	}
	return freqs.dist[ base ];
}


zero_order_frequencies::ptr
zero_order_from_seq( py::object py_seq )
{
    if( 4 != boost::python::len( py_seq ) ) {
        throw std::logic_error( "Wrong number of elements in sequence." );
    }
    return zero_order_frequencies::ptr(
        new zero_order_frequencies(
            myrrh::python::make_extract_iterator< double >( myrrh::python::py_seq_iterator( py_seq, 0 ) ),
            myrrh::python::make_extract_iterator< double >( myrrh::python::py_seq_iterator( py_seq, 4 ) )
        )
    );
}




bg_model::ptr
create_bg_model_from_0_order(
    size_t W,
    data_t & data,
    const zero_order_frequencies & freqs
)
{
    bg_model::ptr result( new bg_model( W, freqs) );
    markov_0_order_likelihoods_calculator( data, freqs, result->wmer_LLs );
    return result;
}




bg_model::ptr
create_bg_model_from_base_likelihoods(
    size_t W,
    data_t & data,
    const likelihoods_vec_vec_t * base_likelihoods,
    const zero_order_frequencies & freqs
)
{
    bg_model::ptr result( new bg_model( W, freqs, base_likelihoods ) );
    base_to_wmer_likelihoods_calculator( data, *result->base_LLs, result->wmer_LLs );
    return result;
}



template< size_t Order >
bg_model::ptr
create_bg_model_from_Markov_model(
    size_t W,
    data_t & data,
    const complete_markov_model< Order, 4, double > & model,
    const zero_order_frequencies & freqs
)
{
    bg_model::ptr result( new bg_model( W, freqs ) );
    markov_wmer_likelihoods_calculator< complete_markov_model< Order, 4, double > >( data, model, result->wmer_LLs );
    return result;
}


/// Registers a create background from Markov model of given order
#define REGISTER_CREATE_BG_FROM_MARKOV_MODEL_OF_ORDER( z, Order, text ) \
    py::def( \
        MYRRH_MAKE_STRING( "create_bg_model_from_Markov_model_" << Order ).c_str(), \
        create_bg_model_from_Markov_model< Order >, \
        ( \
            py::arg( "W" ), \
            py::arg( "data" ), \
            py::arg( "model" ), \
            py::arg( "freqs" ) \
        ), \
        "Creates a background model from the Markov model." \
    );




void
expose_bg() {

#ifdef STEME_USE_OLD_BG_MODEL
	py::scope().attr("_using_old_bg_model") = true;
	std::cout << "WARNING: Using old background model. If you did not intend this then check your configuration!" << std::endl;
#else //STEME_USE_OLD_BG_MODEL
	py::scope().attr("_using_old_bg_model") = false;
#endif //STEME_USE_OLD_BG_MODEL


	//
	// zero_order_frequencies
	//
	py::class_< zero_order_frequencies, zero_order_frequencies::ptr > zero_order_freqs_class(
		"ZeroOrderFrequencies",
		"0-order frequencies.",
		py::no_init
    );
	zero_order_freqs_class.def( "__init__", make_constructor( zero_order_from_seq ), "Constructs from the 0-order occurrences in the sequence." );
	zero_order_freqs_class.def( "add_pseudo_counts", &zero_order_frequencies::add_pseudo_counts, "Add pseudo-counts and return a new 0-order frequencies object." );
	zero_order_freqs_class.def( "freq", get_freq, "Get the frequency of the base." );
	zero_order_freqs_class.def_readonly( "total_counts", &zero_order_frequencies::total_counts, "Total counts used to make this frequencies object." );




    //
    // Background model
    //
    py::class_<
        bg_model,
        boost::noncopyable,
        bg_model::ptr
    > bg_model_class(
        "BgModel",
        "Likelihoods of W-mers and 0-order frequencies.",
        py::no_init
    );
    bg_model_class.def_readonly( "freqs", &bg_model::freqs, "The background frequencies." );




    py::def(
        "create_bg_model_from_0_order",
        create_bg_model_from_0_order,
        (
            py::arg( "W" ),
            py::arg( "data" ),
            py::arg( "freqs" )
        ),
        "Creates a background model from 0-order frequencies."
    );



    py::def(
        "create_bg_model_from_base_likelihoods",
        create_bg_model_from_base_likelihoods,
        (
            py::arg( "W" ),
            py::arg( "data" ),
            py::arg( "base_LLs" ),
            py::arg( "freqs" )
        ),
        "Creates a background model from likelihoods given per-base."
        // following line does not work has runtime error: TypeError: cannot create weak reference to 'int' object
        // py::with_custodian_and_ward< 1, 4 >() // don't let base_LLs be destroyed before the background model
    );

    // define create from Markov model functions.
    BOOST_PP_REPEAT_FROM_TO( 0, STEME_MAX_MARKOV_MODEL_ORDER, REGISTER_CREATE_BG_FROM_MARKOV_MODEL_OF_ORDER, )
}
