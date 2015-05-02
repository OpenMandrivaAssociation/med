Name:           med
Version:        3.0.8
Release:        2%{?dist}
Summary:        Library to exchange meshed data

License:        LGPLv3+
URL:            http://www.code-aster.org/outils/med/
Source0:        http://files.salome-platform.org/Salome/other/%{name}-%{version}.tar.gz

# Chars are unsigned on arm, but the tests do not appear to expect this
# Patch generated via
#    find . -type f -print0 | xargs -0 sed -i "s|-e 's/H5T_STD_I8LE//g'|-e 's/H5T_STD_I8LE//g' -e 's/H5T_STD_U8LE//g'|g"
Patch0:   med-3.0.7_tests.patch
%if 0%{?el6}
# Automake in el6 does not understand serial-tests
Patch1:   med-3.0.7_serial-tests.patch
# Fix syntax in med_check_swig.m4
Patch2:   med-3.0.7_check-swig.patch
%endif

BuildRequires:  hdf5-devel
BuildRequires:  gcc-gfortran
BuildRequires:  swig
BuildRequires:  python2-devel
BuildRequires:  zlib-devel

# For autoreconf
BuildRequires: autoconf automake libtool


%description
MED-fichier (Modélisation et Echanges de Données, in English Modelisation
and Data Exchange) is a library to store and exchange meshed data or
computation results. It uses the HDF5 file format to store the data.


%package -n     python-%{name}
Summary:        Python bindings for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description -n python-%{name}
The python-%{name} package contains python bindings for %{name}.


%package        tools
Summary:        Runtime tools for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       tk

%description    tools
This package contains runtime tools for %{name}:
  - mdump: a tool to dump MED files
  - xmdump: graphical version of mdump.
  - medconforme: a tool to validate a MED file
  - medimport: a tool to convert a MED v2.1 or v2.2 file into a MED v2.3 file


%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%package        doc
Summary:        Documentation for %{name}
BuildArch:      noarch

%description    doc
The %{name}-doc package contains the documentation for %{name}.


%prep
%setup -q -n %{name}-%{version}_SRC
%patch0 -p1
%if 0%{?el6}
%patch1 -p1
%patch2 -p1
%endif

# Fix file not utf8
iconv --from=ISO-8859-1 --to=UTF-8 ChangeLog > ChangeLog.new && \
touch -r ChangeLog ChangeLog.new && \
mv ChangeLog.new ChangeLog


%build
# To remove rpath
autoreconf -ivf
%configure --disable-static
make %{?_smp_mflags}


%install
%make_install

find %{buildroot} -name '*.la' -exec rm -f {} ';'

# Install docs through %%doc
mkdir installed_docs
mv %{buildroot}%{_docdir}/* installed_docs

# Remove configuration summary file
rm -f %{buildroot}%{_libdir}/libmed3.settings

# Remove test-suite files
rm -rf %{buildroot}%{_bindir}/testc
rm -rf %{buildroot}%{_bindir}/usescases
rm -rf %{buildroot}%{_bindir}/unittests
rm -rf %{buildroot}%{_bindir}/testf
rm -rf %{buildroot}%{_bindir}/testpy

# Fix symlinks to point to correct path
ln -sf %{_bindir}/mdump3 %{buildroot}%{_bindir}/mdump
ln -sf %{_bindir}/xmdump3 %{buildroot}%{_bindir}/xmdump


%check
make check


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%doc AUTHORS ChangeLog  README
%license COPYING.LESSER
%{_libdir}/libmed.so.1*
%{_libdir}/libmedC.so.1*
%{_libdir}/libmedimport.so.0*

%files -n python-%{name}
%{python_sitearch}/%{name}/

%files tools
%{_bindir}/*

%files devel
%{_libdir}/*.so
%{_includedir}/*

%files doc
%doc installed_docs/*
%license COPYING.LESSER


%changelog
* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 3.0.8-2
- Rebuilt for GCC 5 C++11 ABI change

* Wed Mar 25 2015 Sandro Mani <manisandro@gmail.com> - 3.0.8-1
- Update to 3.0.8

* Wed Jan 07 2015 Orion Poplawski <orion@cora.nwra.com> - 3.0.7-7
- Rebuild for hdf5 1.8.14

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.7-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.7-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May 21 2014 Sandro Mani <manisandro@gmail.com> - 3.0.7-4
- Fix tests on arm

* Tue May 20 2014 Sandro Mani <manisandro@gmail.com> - 3.0.7-3
- Removed -Wl,--as-needed again
- Fixed license LGPLv3 -> LGPLv3+
- BR python2-devel instead of python-devel

* Sat May 17 2014 Sandro Mani <manisandro@gmail.com> - 3.0.7-2
- Added -Wl,--as-needed to LDFLAGS
- Run autoreconf to remove rpath
- Fixed ChangeLog encoding
- Removed dependency on main package for -doc subpackage

* Sat May 17 2014 Sandro Mani <manisandro@gmail.com> - 3.0.7-1
- Initial package
