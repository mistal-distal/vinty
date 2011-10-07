#!/usr/bin/make

HTTP_USER=www-data
PREFIX=

build: py-build-stamp
py-build-stamp:
	python setup.py build
	touch py-build-stamp

install: py-build-stamp py-install-stamp
py-install-stamp:
	python setup.py install --prefix=$(PREFIX)/usr $(py_setup_install_args) --install-layout=deb
	install -d -m 700 -o $(HTTP_USER) $(PREFIX)/var/lib/vinty
	install -d -m 755 $(PREFIX)/usr/share/vinty/htdocs
	install -d -m 755 $(PREFIX)/usr/share/vinty/scripts
	install -d -m 755 $(PREFIX)/etc/vinty
	install -m 755 -o root vinty.py $(PREFIX)/usr/sbin/vinty
	install -m 755 -o root vintypasswd.py $(PREFIX)/usr/bin/vintypasswd
	install -m 644 -o root config/*.* $(PREFIX)/etc/vinty
	install -m 755 -o root htdocs/*.cgi $(PREFIX)/usr/share/vinty/htdocs
	install -m 644 -o root htdocs/*.css $(PREFIX)/usr/share/vinty/htdocs
	install -m 755 -o root scripts/*.sh $(PREFIX)/usr/share/vinty/scripts
	touch py-install-stamp

clean:
	rm -f py-build-stamp
	rm -f py-install-stamp
	rm -rf build
