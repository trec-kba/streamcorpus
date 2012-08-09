

all: clean
	tar cf kba_corpus.tar  --exclude ".git"  kba_corpus.py argparse.py kba_thrift thrift
	# trec-kba-rsa.secret-key is NOT part of this git repo, and
	# anyone who has it has signed agreements with NIST promising
	# to protect it from dissemination
	tar rf kba_corpus.tar  ../trec-kba-rsa.secret-key
	gzip kba_corpus.tar

clean:
	rm -f kba_corpus.tar.gz
