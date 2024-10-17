%ifarch s390 s390x
  # No OpenMPI support on these arches
  %bcond_with openmpi
%else
  %bcond_without openmpi
%endif

Summary: Basic Linear Algebra Communication Subprograms
Name: blacs
Version: 1.1
Release: 53%{?dist}
License: Public Domain

URL: https://www.netlib.org/blacs
Source0: http://www.netlib.org/blacs/mpiblacs.tgz
Source1: Bmake.inc
Source2: http://www.netlib.org/blacs/mpi_prop.ps
Source3: http://www.netlib.org/blacs/blacs_install.ps
Source4: http://www.netlib.org/blacs/mpiblacs_issues.ps
Source5: http://www.netlib.org/blacs/f77blacsqref.ps
Source6: http://www.netlib.org/blacs/cblacsqref.ps
Source7: http://www.netlib.org/blacs/lawn94.ps
Source8: %{name}.rpmlintrc
BuildRequires: gcc-gfortran
%if %{with openmpi}
# Required for openmpi tests
BuildRequires: openssh-clients
%endif
# For tests
BuildRequires: lapack-devel
# Use gendiff blacs/BLACS .fedora
Patch0: blacs-fedora.patch


%description
The BLACS (Basic Linear Algebra Communication Subprograms) project is 
an ongoing investigation whose purpose is to create a linear algebra 
oriented message passing interface that may be implemented efficiently 
and uniformly across a large range of distributed memory platforms.

The length of time required to implement efficient distributed memory 
algorithms makes it impractical to rewrite programs for every new 
parallel machine. The BLACS exist in order to make linear algebra 
applications both easier to program and more portable. 

%package common
Summary: Common files for blacs


%description common
The BLACS (Basic Linear Algebra Communication Subprograms) project is
an ongoing investigation whose purpose is to create a linear algebra
oriented message passing interface that may be implemented efficiently
and uniformly across a large range of distributed memory platforms.

The length of time required to implement efficient distributed memory
algorithms makes it impractical to rewrite programs for every new
parallel machine. The BLACS exist in order to make linear algebra
applications both easier to program and more portable.

This file contains common files which are not specific to any MPI
implementation.

%package mpich
Summary: BLACS libraries compiled against mpich

BuildRequires: mpich-devel-static
Requires: %{name}-common = %{version}-%{release}
Requires: environment-modules
Provides: %{name}-mpich2 = %{version}-%{release}
Obsoletes: %{name}-mpich2 < 1.1-50

%description mpich
The BLACS (Basic Linear Algebra Communication Subprograms) project is
an ongoing investigation whose purpose is to create a linear algebra
oriented message passing interface that may be implemented efficiently
and uniformly across a large range of distributed memory platforms.

The length of time required to implement efficient distributed memory
algorithms makes it impractical to rewrite programs for every new
parallel machine. The BLACS exist in order to make linear algebra
applications both easier to program and more portable.

This package contains BLACS libraries compiled with mpich.

%package mpich-devel
Summary: Development libraries for blacs (mpich)

Requires: %{name}-mpich = %{version}-%{release}
Provides: %{name}-mpich2-devel = %{version}-%{release}
Obsoletes: %{name}-mpich2-devel < 1.1-50

%description mpich-devel
This package contains development libraries for blacs, compiled
against mpich.

%package mpich-static
Summary: Static libraries for blacs (mpich)

Provides: %{name}-mpich2-static = %{version}-%{release}
Obsoletes: %{name}-mpich2-static < 1.1-50

%description mpich-static
This package contains static libraries for blacs, compiled against mpich.

%if %{with openmpi}
%package openmpi
Summary: BLACS libraries compiled against openmpi

Requires: %{name}-common = %{version}-%{release}
Requires: environment-modules

%description openmpi
The BLACS (Basic Linear Algebra Communication Subprograms) project is
an ongoing investigation whose purpose is to create a linear algebra
oriented message passing interface that may be implemented efficiently
and uniformly across a large range of distributed memory platforms.

The length of time required to implement efficient distributed memory
algorithms makes it impractical to rewrite programs for every new
parallel machine. The BLACS exist in order to make linear algebra
applications both easier to program and more portable.

This package contains BLACS libraries compiled with openmpi.

%package openmpi-devel
Summary: Development libraries for blacs (openmpi)

BuildRequires: openmpi-devel
Requires: %{name}-openmpi = %{version}-%{release}

%description openmpi-devel
This package contains development libraries for blacs, compiled
against openmpi.

%package openmpi-static
Summary: Static libraries for blacs (openmpi)


%description openmpi-static
This package contains static libraries for blacs, compiled against
openmpi.
%endif

%prep
%setup -q -c -n %{name}
%patch0 -p1 -b .fedora
for i in mpich %{?with_openmpi:openmpi}
do
	cp -ap BLACS BLACS-$i
	cp -fp %{SOURCE1} BLACS-$i/
	sed -i "s|FOO|$i|g" BLACS-$i/Bmake.inc
done

%if %{with openmpi}
# openmpi doesn't use TRANSCOMM = -DUseMpich
sed -i "s|-DUseMpich|-DUseMpi2|g" BLACS-openmpi/Bmake.inc
%endif

# copy in docs:
cp -p %{SOURCE2} mpi_prop.ps
cp -p %{SOURCE3} blacs_install.ps
cp -p %{SOURCE4} mpiblacs_issues.ps
cp -p %{SOURCE5} f77blacsqref.ps
cp -p %{SOURCE6} cblacsqref.ps
cp -p %{SOURCE7} lawn94.ps

%build
export RPM_BUILD_DIR=%{_builddir}
# CFLAGS=`echo $RPM_OPT_FLAGS | sed -e 's/-fstack-protector//g'`
# RPM_OPT_FLAGS=`echo $CFLAGS`

# To avoid replicated code define a build macro
%define dobuild() \
cd BLACS-$MPI_COMPILER_NAME; \
make mpi ; \
cd TESTING; \
make; \
cd ../..

# Build mpich version
export MPI_COMPILER_NAME=mpich
%{_mpich_load}
RPM_OPT_FLAGS=`echo $CFLAGS`
%dobuild
%{_mpich_unload}

%if %{with openmpi}
# Build OpenMPI version
export MPI_COMPILER_NAME=openmpi
%{_openmpi_load}
RPM_OPT_FLAGS=`echo $CFLAGS`
%dobuild
%{_openmpi_unload}
%endif

%install
# mkdir -p ${RPM_BUILD_ROOT}%{_bindir}

for i in mpich %{?with_openmpi:openmpi}
do 
  mkdir -p %{buildroot}%{_libdir}/$i/lib/
  mkdir -p %{buildroot}%{_includedir}/$i-%{_arch}/
  mkdir -p %{buildroot}%{_includedir}/blacs/
  pushd BLACS-$i/LIB
  for f in *.a *.so*; do
    cp -f $f %{buildroot}%{_libdir}/$i/lib/$f
  done
  popd
  # This file is independent of the MPI compiler used, but it is poorly named
  # So we'll put it in %{_includedir}/blacs/
  install -p BLACS-$i/SRC/MPI/Bdef.h %{buildroot}%{_includedir}/blacs/
  pushd %{buildroot}%{_libdir}/$i/lib/
  for l in libmpiblacs libmpiblacsF77init libmpiblacsCinit; do
    ln -fs $l.so.1.0.0 $l.so.1
    ln -s $l.so.1.0.0 $l.so
  done
  popd
done

# cd ../TESTING/EXE
# cp -f x*test_MPI-LINUX-0 ${RPM_BUILD_ROOT}%{_bindir}
%check
%{_mpich_load}
cd BLACS-mpich/TESTING/EXE
mpirun -host localhost -np 4 ./xCbtest_MPI-LINUX-0 || rc=$?
# Test exits using MPI_ABORT - test for return code
[ $rc != 255 ] && exit 1
mpirun -host localhost -np 4 ./xFbtest_MPI-LINUX-0 || rc=$?
# Test exits using MPI_ABORT - test for return code
[ $rc != 255 ] && exit 1
cd -
%{_mpich_unload}

%if %{with openmpi}
%{_openmpi_load}
cd BLACS-openmpi/TESTING/EXE
mpirun -np 4 ./xCbtest_MPI-LINUX-0 || rc=$?
# Test exits using MPI_ABORT - test for return code
[ $rc != 255 ] && exit 1
mpirun -np 4 ./xFbtest_MPI-LINUX-0 || rc=$?
# Test exits using MPI_ABORT - test for return code
[ $rc != 255 ] && exit 1
cd -
%{_openmpi_unload}
%endif

%files common
%doc mpi_prop.ps blacs_install.ps mpiblacs_issues.ps f77blacsqref.ps cblacsqref.ps lawn94.ps
%{_includedir}/blacs/
# %{_bindir}/x*test_MPI-LINUX-0

%files mpich
%{_libdir}/mpich/lib/*.so.*

%files mpich-devel
%{_includedir}/mpich-%{_arch}/
%{_libdir}/mpich/lib/*.so

%files mpich-static
%{_libdir}/mpich/lib/*.a

%if %{with openmpi}
%files openmpi
%{_libdir}/openmpi/lib/*.so.*

%files openmpi-devel
%{_includedir}/openmpi-%{_arch}/
%{_libdir}/openmpi/lib/*.so

%files openmpi-static
%{_libdir}/openmpi/lib/*.a
%endif
