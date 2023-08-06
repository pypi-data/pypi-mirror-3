/**
 * Copyright John Reid 2011
 */

#include <seqan/index.h>
#include <seqan/sequence.h>

#include <boost/timer.hpp>

#include <string>
#include <iostream>

using namespace seqan;
using namespace std;

typedef String< Dna5 >                                                string_t;              /**< A string of Dna5. */
typedef seqan::StringSet< string_t >                                  string_set_t;          /**< StringSet type. */
typedef Index< string_set_t >                                         index_t;               /**< The index over our strings. */
typedef seqan::Iterator< index_t, seqan::TopDown<> >::Type            top_down_it;           /**< A iterator over the index type. */


/**
 * Visit a node in the suffix tree (array).
 */
void
visit( top_down_it it ) {
	if( goDown( it ) ) {
		visit( it );
		while( goRight( it ) ) {
			visit( it );
		}
	}
}


/**
 * Read a FASTA file into a string set.
 */
size_t
read_fasta( const char * filename, string_set_t & sequences )
{
	size_t num_bases = 0;
	::ifstream f( filename );
	if( ! f ) {
		cerr << "Could not open FASTA file: " << filename << "\n";
	} else {
		String< char > meta;
		string_t str;
		while( f ) {
			readMeta( f, meta, Fasta() );
			read( f, str, Fasta() );
			appendValue( sequences, str );
			num_bases += length( str );
		}
	}
	f.close();
	return num_bases;
}


void wait_for_return() {
	char input;
	cout << "Press <return> to continue...\n";
	do {
		input = cin.get();
	} while( '\n' != input );
}

#pragma GCC diagnostic ignored "-Wunused-result"

void
show_ps_info() {
	system( "ps -C seqan_sandbox_build_index -o pid,sz,vsz,rss,args" );
}

int
main( int argc, char * argv[] ) {

	if( argc < 2 ) {

		cerr << "USAGE: " << argv[0] << " <fasta file>\n";
		return -1;

	} else {

		show_ps_info();

		string_set_t sequences;
		boost::timer timer;

		timer.restart();
		const size_t num_bases = read_fasta( argv[1], sequences );
		cout << "\nRead " << num_bases << " bases from: " << argv[1] << " in " << timer.elapsed() << " seconds.\n";
		show_ps_info();

		timer.restart();
		index_t index( sequences );
		cout << "\nBuilt index in " << timer.elapsed() << " seconds.\n";
		show_ps_info();

		timer.restart();
		visit( top_down_it( index ) );
		cout << "\nVisited index in " << timer.elapsed() << " seconds.\n";
		show_ps_info();

		timer.restart();
		visit( top_down_it( index ) );
		cout << "\nVisited index in " << timer.elapsed() << " seconds.\n";
		show_ps_info();

		return 0;
	}
}
