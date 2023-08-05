%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           python-minihallib
Version:        0.1.10
Release:        1%{?dist}
Summary:        Library to handle HAL devices and events

Group:          Development/Languages
License:        GPLv2+ or AFL
URL:            http://www.smile.org.ua/trac/minihallib
Source0:        http://pypi.python.org/packages/source/m/minihallib/minihallib-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel
%if 0%{?fedora} >= 8
BuildRequires:  python-setuptools-devel
%else
BuildRequires:  python-setuptools
%endif

Requires:       dbus-python >= 0.62
Requires:       dbus-glib >= 0.62
Requires:       hal >= 0.5.6


%description
Python threaded library to handle HAL devices and their events.

%prep
%setup -q -n minihallib-%{version}

# Don't push executable files into documentation
chmod a-x examples/*


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT 


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc README
%doc examples
%{python_sitelib}/*


%changelog
* Sun Nov 11 2007 Andy Shevchenko <andy@smile.org.ua> 0.1.10-1
- update to the last release

* Wed Oct 17 2007 Andy Shevchenko <andy@smile.org.ua> 0.1.8-2
- remove duplicates at the files section

* Tue Oct 16 2007 Andy Shevchenko <andy@smile.org.ua> 0.1.8-1
- update to the last release

* Tue Oct 16 2007 Andy Shevchenko <andy@smile.org.ua> 0.1.7-2
- don't use CFLAGS
- fix this file according to the Python Eggs Guidelines
  (http://fedoraproject.org/wiki/Packaging/Python/Eggs)

* Tue Oct 16 2007 Andy Shevchenko <andy@smile.org.ua> 0.1.7-1
- update to the last release
- add examples to the documentation

* Wed Oct 03 2007 Andy Shevchenko <andy@smile.org.ua> 0.1.6-1
- update to the last release
- fix Source tag

* Tue Oct 02 2007 Andy Shevchenko <andy@smile.org.ua>
- fix License tag according to last Fedora guidelines

* Mon Sep 10 2007 Andy Shevchenko <andy@smile.org.ua>
- initial build

