Name:           med
Version:        3.3.1
Release:        2%{?dist}
Summary:        Library to exchange meshed data

License:        LGPLv3+
URL:            http://www.salome-platform.org/user-section/about/med
Source0:        http://files.salome-platform.org/Salome/other/%{name}-%{version}.tar.gz

# Chars are unsigned on arm, but the tests do not appear to expect this
# Patch generated via
#    find . -type f -print0 | xargs -0 sed -i "s|-e 's/H5T_STD_I8LE//g'|-e 's/H5T_STD_I8LE//g' -e 's/H5T_STD_U8LE//g'|g"
Patch0:         med-3.0.7_tests.patch
# - Install headers in %%_includedir/med
# - Comment out missing test
# - Set library version
# - Use LIB_SUFFIX
# - Install cmake config files to %%_libdir/cmake
Patch1:         med-3.3.1_cmake.patch

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-gfortran
BuildRequires:  hdf5-devel
BuildRequires:  make
BuildRequires:  python2-devel
BuildRequires:  python3-devel
BuildRequires:  swig
BuildRequires:  zlib-devel

# For autoreconf
BuildRequires: autoconf automake libtool


%description
MED-fichier (Modélisation et Echanges de Données, in English Modelisation
and Data Exchange) is a library to store and exchange meshed data or
computation results. It uses the HDF5 file format to store the data.


%package -n     python2-%{name}
Summary:        Python2 bindings for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Obsoletes:      python-%{name} < 3.1.0-1
Provides:       python-%{name} = %{version}

%description -n python2-%{name}
The python2-%{name} package contains python2 bindings for %{name}.


%package -n     python3-%{name}
Summary:        Python3 bindings for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description -n python3-%{name}
The python3-%{name} package contains python3 bindings for %{name}.


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
Requires:       cmake-filesystem

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%package        doc
Summary:        Documentation for %{name}
BuildArch:      noarch

%description    doc
The %{name}-doc package contains the documentation for %{name}.


%prep
%autosetup -p1 -n %{name}-%{version}_SRC

# Fix file not utf8
iconv --from=ISO-8859-1 --to=UTF-8 ChangeLog > ChangeLog.new && \
touch -r ChangeLog ChangeLog.new && \
mv ChangeLog.new ChangeLog


%build
# https://autotools.io/libtool/version.html
# -> On linux, current:revision:age translates to lib version (current-age).age.revision
libmedCRA=`grep -E "libmed_la_LDFLAGS.*version-info\s+([0-9]+:[0-9]+:[0-9]+)" src/Makefile.am | grep -Eo "[0-9]+:[0-9]+:[0-9]+"`
libmedSOVER=`echo $libmedCRA | awk -F':' '{print $1-$3}'`
libmedLIBVER=`echo $libmedCRA | awk -F':' '{print $1-$3"."$3"."$2}'`
libmedcCRA=`grep -E "libmedC_la_LDFLAGS.*version-info\s+([0-9]+:[0-9]+:[0-9]+)" src/Makefile.am | grep -Eo "[0-9]+:[0-9]+:[0-9]+"`
libmedcSOVER=`echo $libmedcCRA | awk -F':' '{print $1-$3}'`
libmedcLIBVER=`echo $libmedcCRA | awk -F':' '{print $1-$3"."$3"."$2}'`
libmedimportCRA=`grep -E "libmedimport_la_LDFLAGS.*version-info\s+([0-9]+:[0-9]+:[0-9]+)" tools/medimport/Makefile.am | grep -Eo "[0-9]+:[0-9]+:[0-9]+"`
libmedimportSOVER=`echo $libmedimportCRA | awk -F':' '{print $1-$3}'`
libmedimportLIBVER=`echo $libmedimportCRA | awk -F':' '{print $1-$3"."$3"."$2}'`

mkdir build_py2
pushd build_py2
%cmake -DMEDFILE_BUILD_PYTHON=1 \
    -DPYTHON_EXECUTABLE=%{__python2} \
    -DPYTHON_INCLUDE_DIR=%{_includedir}/python%{python2_version}/ \
    -DPYTHON_LIBRARY=%{_libdir}/libpython%{python2_version}.so \
    -DLIBMED_SOVER=$libmedSOVER -DLIBMED_LIBVER=$libmedLIBVER \
    -DLIBMEDC_SOVER=$libmedcSOVER -DLIBMEDC_LIBVER=$libmedcLIBVER \
    -DLIBMEDIMPORT_SOVER=$libmedimportSOVER -DLIBMEDIMPORT_LIBVER=$libmedimportLIBVER ..
%make_build
popd

mkdir build_py3
pushd build_py3
%cmake -DMEDFILE_BUILD_PYTHON=1 \
    -DPYTHON_EXECUTABLE=%{__python3} \
    -DPYTHON_INCLUDE_DIR=%{_includedir}/python%{python3_version}m/ \
    -DPYTHON_LIBRARY=%{_libdir}/libpython%{python3_version}m.so \
    -DLIBMED_SOVER=$libmedSOVER -DLIBMED_LIBVER=$libmedLIBVER \
    -DLIBMEDC_SOVER=$libmedcSOVER -DLIBMEDC_LIBVER=$libmedcLIBVER \
    -DLIBMEDIMPORT_SOVER=$libmedimportSOVER -DLIBMEDIMPORT_LIBVER=$libmedimportLIBVER ..
%make_build
popd


%install
%make_install -C build_py2
%make_install -C build_py3

# Install docs through %%doc
mkdir installed_docs
mv %{buildroot}%{_docdir}/* installed_docs

# Remove test-suite files
rm -rf %{buildroot}%{_bindir}/testc
rm -rf %{buildroot}%{_bindir}/testf
rm -rf %{buildroot}%{_bindir}/testpy


%check
make check -C build_py2 || :
make check -C build_py3 || :


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%doc AUTHORS ChangeLog  README
%license COPYING.LESSER
%{_libdir}/libmed.so.1*
%{_libdir}/libmedC.so.1*
%{_libdir}/libmedimport.so.0*

%files -n python2-%{name}
%{python2_sitearch}/%{name}/

%files -n python3-%{name}
%{python3_sitearch}/%{name}/

%files tools
%{_bindir}/*mdump*
%{_bindir}/medconforme
%{_bindir}/medimport

%files devel
%{_libdir}/*.so
%{_libdir}/libmedfwrap.a
%{_libdir}/cmake/MEDFile/
%{_includedir}/%{name}/

%files doc
%doc installed_docs/*
%license COPYING.LESSER


%changelog
* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com> - 3.3.1-2
- Rebuilt for Python 3.7

* Fri Mar 09 2018 Sandro Mani <manisandro@gmail.com> - 3.3.1-1
- Update to 3.3.1

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.2.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Mon Feb 05 2018 Jitka Plesnikova <jplesnik@redhat.com> - 3.2.1-4
- Rebuild for new gfortran

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.2.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat May 06 2017 Sandro Mani <manisandro@gmail.com> - 3.2.1-1
- Update to 3.2.1

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.2.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Feb 01 2017 Sandro Mani <manisandro@gmail.com> - 3.2.0-2
- Rebuild (gfortran)

* Mon Oct 03 2016 Sandro Mani <manisandro@gmail.com> - 3.2.0-1
- Update to 3.2.0

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.0-2
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Sat Feb 06 2016 Sandro Mani <manisandro@gmail.com> - 3.1.0-1
- Update to 3.1.0

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.8-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jan 21 2016 Orion Poplawski <orion@cora.nwra.com> - 3.0.8-5
- Rebuild for hdf5 1.8.16

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.8-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sun May 17 2015 Orion Poplawski <orion@cora.nwra.com> - 3.0.8-3
- Rebuild for hdf5 1.8.15

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
