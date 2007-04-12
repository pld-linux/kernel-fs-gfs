#
# Condtional build:
%bcond_without	kernel		# don't build kernel modules
%bcond_without	dist_kernel	# without distribution kernel
%bcond_with	verbose		# verbose build (V=1)
#
%define _rel	0.3
Summary:	Shared-disk cluster file system
Summary(pl.UTF-8):	System plików dla klastrów z współdzieloną przestrzenią dyskową
Name:		kernel%{_alt_kernel}-fs-gfs
Version:	2.00.00
Release:	%{_rel}@%{_kernel_ver_str}
Epoch:		0
License:	GPL v2
Group:		Base/Kernel
Source0:	ftp://sources.redhat.com/pub/cluster/releases/cluster-%{version}.tar.gz
# Source0-md5:	2ef3f4ba9d3c87b50adfc9b406171085
URL:		http://sources.redhat.com/cluster/gfs/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2}
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
BuildRequires:	perl-base
%{?with_dist_kernel:%requires_releq_kernel}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel%{_alt_kernel}}
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
GFS (Global File System) is a cluster file system. It allows a cluster
of computers to simultaneously use a block device that is shared
between them (with FC, iSCSI, NBD, etc...). GFS reads and writes to
the block device like a local filesystem, but also uses a lock module
to allow the computers coordinate their I/O so filesystem consistency
is maintained. One of the nifty features of GFS is perfect consistency
-- changes made to the filesystem on one machine show up immediately
on all other machines in the cluster.

%description -l pl.UTF-8
GFS (Global File System - globalny system plików) to system plików dla
klastrów. Pozwala klastrowi komputerów jednocześnie używać urządzenia
blokowego współdzielonego pomiędzy nimi (poprzez FC, iSCSI, NBD itp.).
GFS odczytuje i zapisuje urządzenie blokowe podobnie do lokalnego
systemu plików, ale używa także modułu do blokad, aby umożliwić
komputerom koordynowanie ich operacji wejścia/wyjścia tak, by utrzymać
spójność systemu plików. Jedną z cech GFS-a jest doskonała spójność -
zmiany wykonywane w systemie plików na jednej maszynie pokazują się
natychmiast na wszystkich innych maszynach w klastrze.

%package -n kernel%{_alt_kernel}-fs-gfs-devel
Summary:	Shared-disk cluster file system - headers
Summary(pl.UTF-8):	System plików dla klastrów z współdzieloną przestrzenią dyskową - pliki nagłówkowe
Release:	%{_rel}
Group:		Development/Libraries

%description -n kernel%{_alt_kernel}-fs-gfs-devel
Shared-disk cluster file system - headers.

%description -n kernel%{_alt_kernel}-fs-gfs-devel -l pl.UTF-8
System plików dla klastrów z współdzieloną przestrzenią dyskową -
pliki nagłówkowe.

%prep
%setup -q -n cluster-%{version}

cat > gfs-kernel/src/gfs/Makefile << EOF
obj-m := gfs.o
gfs-objs := acl.o bits.o bmap.o daemon.o dio.o dir.o eaops.o eattr.o file.o \
	glock.o glops.o inode.o ioctl.o lm.o log.o lops.o lvb.o main.o \
	mount.o ondisk.o ops_address.o ops_dentry.o ops_export.o ops_file.o \
	ops_fstype.o ops_inode.o ops_super.o ops_vm.o page.o proc.o quota.o \
	recovery.o rgrp.o super.o sys.o trans.o unlinked.o util.o

%{?debug:CFLAGS += -DCONFIG_MODULE_NAME_DEBUG=1}
EOF

%build
cd gfs-kernel
./configure \
	--kernel_src=%{_kernelsrcdir}
%if %{with kernel}
%build_kernel_modules -C src/gfs -m gfs
%endif

%install
rm -rf $RPM_BUILD_ROOT

cd gfs-kernel
%if %{with kernel}
%install_kernel_modules -m src/gfs/gfs -d fs
%endif

install -d $RPM_BUILD_ROOT%{_includedir}/cluster
install src/gfs/gfs_ondisk.h src/gfs/gfs_ioctl.h \
	$RPM_BUILD_ROOT%{_includedir}/cluster

%clean
rm -rf $RPM_BUILD_ROOT

%post
%depmod %{_kernel_ver}

%postun
%depmod %{_kernel_ver}

%if %{with kernel}
%files
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/fs/*
%endif

%files -n kernel%{_alt_kernel}-fs-gfs-devel
%defattr(644,root,root,755)
%{_includedir}/cluster
