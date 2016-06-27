help:
	@python -c "lines = [l.strip().split(':', 1)[0] for l in open('Makefile') if l.strip() and not l.startswith('\t') and ' = ' not in l]; print '\n'.join(lines)";


notebook:
	jupyter notebook analysis.ipynb


pastebin:
	python corral_qai.py pastebin ||:


gist:
	python corral_qai.py gist ||:


activestate:
	python corral_qai.py activestate ||:


retrieve: pastebin gist activestate
	@echo done;


metrics:
	python metrics.py;


export:
	python -c 'import os; import corral_qai; from metrics import df; df.to_csv(os.path.join(corral_qai.DATA_PATH, "corral_qai.csv"), encoding="utf8")';
	sqlite3 data/corral_qai.db '.dump' > data/corral_qai.sql;


all: retrieve metrics export
	echo "done";
	#git commit -am "more data";
	#git push origin master;
