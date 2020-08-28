UML := ${wildcard *.plant}

.PHONY: build
build: ${UML}
	plantuml ${UML}

clean:
	${RM} *.png
