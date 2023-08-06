/** Copyright John Reid 2011
 *
 * \file
 * \brief Seqan types for STEME algorithm.
 *
 */

#ifndef STEME_JR_13AUG2011_SEQAN_TYPES_H_
#define STEME_JR_13AUG2011_SEQAN_TYPES_H_

#include <steme/defs.h>

namespace steme {



/// Meta-function to choose type.
template< typename Spec = default_spec >
struct alphabet_meta {
	typedef seqan::Dna5 type; ///< Stores one base.
};

/// Meta-function to choose type.
template< typename Spec = default_spec >
struct fasta_string_meta {
	typedef seqan::String<
		typename alphabet_meta< Spec >::type,
		seqan::FileReader< seqan::Fasta >
	> type; ///< Type of string read from fasta file.
};

/// Meta-function to choose type.
template< typename Spec = default_spec >
struct string_meta {
	typedef seqan::String< typename alphabet_meta< Spec >::type > type; ///< A string of seqan::Dna5.
};

/// Meta-function to choose type.
template< typename Spec = default_spec >
struct string_set_meta {
	typedef seqan::StringSet< typename string_meta< Spec >::type > type; ///< Our seqan::StringSet type.
};

/// Meta-function to choose type.
template< typename Spec = default_spec >
struct id_set_meta {
	typedef seqan::StringSet< seqan::CharString > type; ///< Holds IDs of strings.
};

/// Meta-function to choose type.
template< typename Spec = default_spec >
struct index_tag_meta {
	typedef seqan::IndexEsa<> type; ///< Selector for which seqan index implementation.
};

/// Meta-function to choose type.
template< typename Spec = default_spec >
struct index_meta {
	typedef seqan::Index<
		typename string_set_meta< Spec >::type,
		typename index_tag_meta< Spec >::type
	> type; ///< Our seqan index type over our string set.
};

/// Meta-function to choose type.
template< typename Spec = default_spec >
struct freq_dist_meta {
	typedef seqan::FrequencyDistribution< typename alphabet_meta< Spec >::type > type; ///< The type that holds frequency distributions.
};




#define STEME_TYPEDEF_SEQAN_TYPES( SPEC ) \
	typedef typename alphabet_meta< SPEC >::type                                                alphabet_t;            \
	typedef typename fasta_string_meta< SPEC >::type                                            fasta_file_string_t;   \
	typedef typename string_meta< SPEC >::type                                                  string_t;              \
	typedef typename seqan::Infix< string_t >::Type                                             infix_t;               \
	typedef typename string_set_meta< SPEC >::type                                              string_set_t;          \
	typedef boost::shared_ptr< string_set_t >                                                   string_set_ptr_t;      \
	typedef typename id_set_meta< SPEC >::type                                                  id_set_t;              \
	typedef typename index_tag_meta< SPEC >::type                                               index_tag_t;           \
	typedef typename index_meta< SPEC >::type                                                   index_t;               \
	typedef boost::shared_ptr< index_t >                                                        index_ptr_t;           \
	typedef typename seqan::SAValue< index_t >::Type                                            sa_value_t;            \
	typedef typename seqan::Fibre< index_t, seqan::EsaSA >::Type                                fibre_sa_t;            \
	typedef typename seqan::Infix< fibre_sa_t const >::Type                                     occurrences_t;         \
	typedef typename seqan::Fibre< index_t, seqan::EsaText >::Type                              esa_text_fibre_t;      \
	typedef typename seqan::Infix< esa_text_fibre_t const >::Type                               parent_edge_label_t;   \
	typedef typename seqan::Host< index_t >::Type                                               text_t;                \
	typedef typename seqan::Id< text_t >::Type                                                  id_t;                  \
	typedef boost::tuple< id_t, int >                                                           local_pos_t;           \
	typedef typename seqan::Fibre< index_t, seqan::EsaRawText >::Type                           raw_text_t;            \
	typedef typename seqan::StringSetLimits< text_t >::Type                                     string_set_limits_t;   \
	typedef boost::shared_ptr< string_set_limits_t >                                            string_set_limits_ptr; \
	typedef typename seqan::Iterator< index_t, seqan::TopDown<> >::Type                         top_down_it;           \
	typedef typename seqan::Iterator< index_t, seqan::TopDown< seqan::ParentLinks<> > >::Type   top_down_history_it;   \
	typedef typename seqan::Infix< text_t const >::Type                                         representative_t;      \
	typedef typename seqan::Prefix< representative_t >::Type                                    prefix_t;              \



template< typename Spec = default_spec >
struct steme_seqan_types {
	STEME_TYPEDEF_SEQAN_TYPES( Spec )
};



} // namespace steme

#endif /* STEME_JR_13AUG2011_SEQAN_TYPES_H_ */
