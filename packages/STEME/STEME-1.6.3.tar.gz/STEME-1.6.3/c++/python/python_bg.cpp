/** Copyright John Reid 2011
 *
 * \file Exposes background parts of STEME algorithm to python.
 */

#include "steme_python_defs.h"

#include <steme/background_model.h>
#include <steme/data.h>

#include <myrrh/python/boost_range.h>

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
	// MarkovBackgroundModel - not used unless STEME_USE_OLD_BG_MODEL is defined
	//
	py::class_<
		Markov0OrderBackgroundModel,
		boost::noncopyable,
		Markov0OrderBackgroundModel::ptr
	> markov_bg_model_class(
		"Markov0OrderBackgroundModel",
		"A 0-order Markov background model.",
		py::init<
			data_t &,
			const zero_order_frequencies &,
			size_t
		>(
			(
				py::arg( "data" ),
				py::arg( "zero_order_freqs" ),
				py::arg( "W" )
			),
			"Construct a Markov0OrderBackgroundModel object."
		)
    );
	markov_bg_model_class.def_readonly( "freqs", &Markov0OrderBackgroundModel::freqs, "The background frequencies." );


	//
	// BackgroundModelFromLikelihoods
	//
	py::class_<
		BackgroundModelFromLikelihoods,
		boost::noncopyable,
		BackgroundModelFromLikelihoods::ptr
	> likelihoods_bg_model_class(
		"BackgroundModelFromLikelihoods",
		"A background model created from likelihoods.",
		py::init<
			data_t &,
			const likelihoods_vec_vec_t &,
			const zero_order_frequencies &,
			size_t
		>(
			(
				py::arg( "data" ),
				py::arg( "likelihoods" ),
				py::arg( "zero_order_freqs" ),
				py::arg( "W" )
			),
			"Construct a BackgroundModelFromLikelihoods object."
		)
    );
    likelihoods_bg_model_class.def_readonly( "freqs", &BackgroundModelFromLikelihoods::freqs, "The background frequencies." );
    likelihoods_bg_model_class.def(
        "w_mer_log_likelihood",
        &BackgroundModelFromLikelihoods::w_mer_log_likelihood,
        (
            py::arg( "seq" ),
            py::arg( "offset" )
        ),
        "The likelihood of the given W-mer." );


}
