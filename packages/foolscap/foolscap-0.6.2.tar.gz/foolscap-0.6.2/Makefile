
.PHONY: build test debian-sid debian-dapper debian-feisty debian-sarge
.PHONY: debian-edgy debian-etch

build:
	python setup.py build

TRIAL=trial
TEST=foolscap
test:
	$(TRIAL) $(TEST)

test-poll:
	$(MAKE) test TRIAL="trial -r poll"

debian-sid:
	rm -f debian
	ln -s misc/sid/debian debian
	chmod a+x debian/rules
	debuild -uc -us

debian-etch:
	rm -f debian
	ln -s misc/etch/debian debian
	chmod a+x debian/rules
	debuild -uc -us

debian-dapper:
	rm -f debian
	ln -s misc/dapper/debian debian
	chmod a+x debian/rules
	debuild -uc -us

debian-edgy:
	rm -f debian
	ln -s misc/edgy/debian debian
	chmod a+x debian/rules
	debuild -uc -us

debian-feisty:
	rm -f debian
	ln -s misc/feisty/debian debian
	chmod a+x debian/rules
	debuild -uc -us

debian-gutsy:
	rm -f debian
	ln -s misc/gutsy/debian debian
	chmod a+x debian/rules
	debuild -uc -us

debian-hardy:
	rm -f debian
	ln -s misc/hardy/debian debian
	chmod a+x debian/rules
	debuild -uc -us

debian-sarge:
	rm -f debian
	ln -s misc/sarge/debian debian
	chmod a+x debian/rules
	debuild -uc -us

LORE=lore
DOC_TEMPLATE=doc/template.tpl
docs:
	$(LORE) -p --config template=$(DOC_TEMPLATE) --config ext=.html \
	--config baseurl='api/%s-class.html' \
	`find doc -name '*.xhtml'`
doc/%.html: doc/%.xhtml
	$(LORE) -p --config template=$(DOC_TEMPLATE) --config ext=.html \
	--config baseurl='api/%s-class.html' \
	$<

api-docs:
	rm -rf doc/api
	PYTHONPATH=. epydoc -v -o doc/api --html -n Foolscap -u http://foolscap.lothar.com --exclude foolscap.test foolscap

pyflakes:
	pyflakes bin foolscap |sort |uniq

find-trailing-spaces:
	find-trailing-spaces -r bin foolscap
