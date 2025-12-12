# For now -- since C code (built with clang) and
# Fortran code (built with gfortran) are linked
# together, LTO object files don't work
%global _disable_lto 1

%define libmed		%mklibname %{name}
%define libmedlibC	%mklibname medlibC
%define libmedimport	%mklibname medlibimport
%define libmedfwrap	%mklibname medfwrap_major
%define devname		%mklibname %{name} -d

%define oldlibmed	%mklibname med 1
%define oldlibmedlibC	%mklibname medlibC 1
%define oldlibmedimport	%mklibname medlibimport 0

%global	med_major	1
%global	medC_major	1
%global	medimport_major	0
%global	medfwrap_major	11

%bcond doc	1
%bcond python	1
%bcond tests	1

Summary:	Library to exchange meshed data
Name:		med
Version:	5.0.0
Release:	2
Group:		System/Libraries
License:	LGPLv3.0+
URL:		https://www.salome-platform.org/
Source0:	https://files.salome-platform.org/Salome/medfile/%{name}-%{version}.tar.bz2
# - Install headers in %%_includedir/med
# - Install cmake config files to %%_libdir/cmake
# - Install doc to %%_pkgdocdir
Patch0:		med_cmake.patch
# Fix python3.13 build
Patch1:		med-py3.13.patch
# Fix compatibility with hdf-1.14
Patch2:		hdf5-1.14.patch
# Fix swig-4.3.0 compatibility
Patch3:		med-swig-4.3.0.patch

BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	gcc-gfortran
BuildRequires:	hdf5-devel
%if %{with python}
BuildRequires:	pkgconfig(python3)
%endif
BuildRequires:	pkgconfig(zlib)
BuildRequires:	swig

%description
MED-fichier (Modélisation et Echanges de Données, in English Modelisation
and Data Exchange) is a library to store and exchange meshed data or
computation results. It uses the HDF5 file format to store the data.

This package contains runtime tools for %{name}:
  · mdump: a tool to dump MED files
  · medconforme: a tool to validate a MED file
  · medimport: a tool to convert a MED v2.1 or v2.2 file into a MED v2.3 file
  · xmdump: graphical version of mdump.

%files
%license COPYING.LESSER
%doc AUTHORS ChangeLog README
%{_bindir}/mdump*
%{_bindir}/medconforme
%{_bindir}/medimport
%{_bindir}/xmdump*

#----------------------------------------------------------------------

%package -n %{libmed}
Summary:	Graph, mesh and hypergraph partitioning library
Group:		System/Libraries
Obsoletes:	%oldlibmed < %{EVRD}

%description -n %{libmed}
MED-fichier (Modélisation et Echanges de Données, in English Modelisation
and Data Exchange) is a library to store and exchange meshed data or
computation results. It uses the HDF5 file format to store the data.

%files -n %{libmed}
%{_libdir}/libmed.so.%{med_major}*
%{_libdir}/libmedfwrap.so.%{medfwrap_major}*

#-----------------------------------------------------------------------

%package -n %{libmedlibC}
Summary:	Data exchanges in multi-physics simulation work
Group:		Development/Other
Obsoletes:	%oldlibmedlibC < %{EVRD}

%description -n	%{libmedlibC}
MED-fichier (Modélisation et Echanges de Données, in English Modelisation
and Data Exchange) is a library to store and exchange meshed data or
computation results. It uses the HDF5 file format to store the data.

%files -n %{libmedlibC}
%{_libdir}/libmedC.so.%{medC_major}*

#-----------------------------------------------------------------------

%package -n %{libmedimport}
Summary:	Data exchanges in multi-physics simulation work
Group:		Development/Other
Obsoletes:	%oldlibmedimport < %{EVRD}

%description -n %{libmedimport}
MED-fichier (Modélisation et Echanges de Données, in English Modelisation
and Data Exchange) is a library to store and exchange meshed data or
computation results. It uses the HDF5 file format to store the data.

%files -n %{libmedimport}
%{_libdir}/libmedimport.so.%{medimport_major}*

#----------------------------------------------------------------------

%package -n python-%{name}
Summary:	Python bindings for %{name}
Group:		Development/Python
Requires:	%{libmed} = %{version}-%{release}

%description -n python-%{name}
MED-fichier (Modélisation et Echanges de Données, in English Modelisation
and Data Exchange) is a library to store and exchange meshed data or
computation results. It uses the HDF5 file format to store the data.

This package contains a python binding for %{name}.


%files -n python-%{name}
%{python_sitearch}/%{name}/

#----------------------------------------------------------------------

%package -n %{devname}
Summary:	Development files for %{name}
Group:		Development/Other
Requires:	cmake-filesystem
Requires:	%{libmed} = %{EVRD}
Requires:	%{libmedimport} = %{EVRD}
Requires:	%{libmedlibC} = %{EVRD}
Provides:	%{name}-devel

%description -n %{devname}
MED-fichier (Modélisation et Echanges de Données, in English Modelisation
and Data Exchange) is a library to store and exchange meshed data or
computation results. It uses the HDF5 file format to store the data.

This package contains libraries and header files for developing applications
that use %{name}.

%files -n %{devname}
%license COPYING.LESSER
%doc AUTHORS ChangeLog README
%{_libdir}/*.so
%{_libdir}/cmake/MEDFile/
%{_includedir}/%{name}/

#----------------------------------------------------------------------

%package doc
Summary:	Documentation for %{name}
BuildArch:	noarch

%description doc
MED-fichier (Modélisation et Echanges de Données, in English Modelisation
and Data Exchange) is a library to store and exchange meshed data or
computation results. It uses the HDF5 file format to store the data.

This package contains the documentation for %{name}.

%files doc
%license COPYING.LESSER
%doc AUTHORS ChangeLog README
%if %{with doc}
%doc %{_docdir}*
%endif

#----------------------------------------------------------------------

%prep
%autosetup -p1

# Delete files generated by swig
grep -l 'This file was automatically generated' python/* | xargs rm

%build
export FC=gfortran

%cmake -Wno-dev \
	-DMEDFILE_INSTALL_DOC:BOOL=%{?with_doc:ON}%{?!with_doc:OFF} \
	-DMEDFILE_BUILD_PYTHON:BOOL=%{?with_python:ON}%{?!with_python:OFF} \
	-DMEDFILE_BUILD_TESTS:BOOL=%{?with_tests:ON}%{?!with_tests:OFF} \
	-GNinja
%ninja_build


%install
%ninja_install -C build

# Remove test-suite files
rm -rf %{buildroot}%{_bindir}/testc
rm -rf %{buildroot}%{_bindir}/testf
rm -rf %{buildroot}%{_bindir}/testpy

%check
%if %{with tests}
pushd build
LD_LIBRARY_PATH=%{buildroot}%{_libdir} \
YTHONPATH=%{buildroot}/%{python_sitearch} \
ctest || :
popd 1>/dev/null
%endif

