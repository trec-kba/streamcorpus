
clean:
	rm -rf classes
	rm -rf streamcorpus.jar

build: clean
	mkdir classes
	javac -cp ../scala/lib/libthrift-1.0.0.jar:lib/slf4j-api-1.7.2.jar  -d classes src/streamcorpus/*
	cd classes && jar cvf ../streamcorpus.jar .

