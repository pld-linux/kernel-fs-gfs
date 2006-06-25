#
# Condtional build:
%bcond_without	kernel		# don't build kernel modules
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	smp		# without smp packages
%bcond_with	verbose		# verbose build (V=1)
#
%define _rel	0.3
Summary:	Shared-disk cluster file system
Summary(pl):	System plików dla klastrów z wspó³dzielon± przestrzeni± dyskow±
Name:		kernel%{_alt_kernel}-fs-gfs
Version:	1.02.00
Release:	%{_rel}@%{_kernel_ver_str}
Epoch:		0
License:	GPL v2
Group:		Base/Kernel
Source0:	ftp://sources.redhat.com/pub/cluster/releases/cluster-%{version}.tar.gz
# Source0-md5:	131c34c8b66d8d7d74384839ed4091d0
Patch0:		kernel-fs-gfs-posix_test_lock.patch
Patch1:		kernel-fs-gfs-mutex.patch
Patch2:		kernel-fs-gfs-get_block.patch
URL:		http://sources.redhat.com/cluster/gfs/
BuildRequires:	kernel%{_alt_kernel}-cluster-cman-devel
BuildRequires:	kernel%{_alt_kernel}-cluster-dlm-devel
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.7}
%endif
BuildRequires:	perl-base
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel}
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

%description -l pl
GFS (Global File System - globalny system plików) to system plików dla
klastrów. Pozwala klastrowi komputerów jednocze¶nie u¿ywaæ urz±dzenia
blokowego wspó³dzielonego pomiêdzy nimi (poprzez FC, iSCSI, NBD itp.).
GFS odczytuje i zapisuje urz±dzenie blokowe podobnie do lokalnego
systemu plików, ale u¿ywa tak¿e modu³u do blokad, aby umo¿liwiæ
komputerom koordynowanie ich operacji wej¶cia/wyj¶cia tak, by utrzymaæ
spójno¶æ systemu plików. Jedn± z cech GFS-a jest doskona³a spójno¶æ -
zmiany wykonywane w systemie plików na jednej maszynie pokazuj± siê
natychmiast na wszystkich innych maszynach w klastrze.

%package -n kernel%{_alt_kernel}-smp-fs-gfs
Summary:	Shared-disk cluster file system
Summary(pl):	System plików dla klastrów z wspó³dzielon± przestrzeni± dyskow±
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel-smp}

%description -n kernel%{_alt_kernel}-smp-fs-gfs
GFS (Global File System) is a cluster file system. It allows a cluster
of computers to simultaneously use a block device that is shared
between them (with FC, iSCSI, NBD, etc...). GFS reads and writes to
the block device like a local filesystem, but also uses a lock module
to allow the computers coordinate their I/O so filesystem consistency
is maintained. One of the nifty features of GFS is perfect consistency
-- changes made to the filesystem on one machine show up immediately
on all other machines in the cluster.

%description -n kernel%{_alt_kernel}-smp-fs-gfs -l pl
GFS (Global File System - globalny system plików) to system plików dla
klastrów. Pozwala klastrowi komputerów jednocze¶nie u¿ywaæ urz±dzenia
blokowego wspó³dzielonego pomiêdzy nimi (poprzez FC, iSCSI, NBD itp.).
GFS odczytuje i zapisuje urz±dzenie blokowe podobnie do lokalnego
systemu plików, ale u¿ywa tak¿e modu³u do blokad, aby umo¿liwiæ
komputerom koordynowanie ich operacji wej¶cia/wyj¶cia tak, by utrzymaæ
spójno¶æ systemu plików. Jedn± z cech GFS-a jest doskona³a spójno¶æ -
zmiany wykonywane w systemie plików na jednej maszynie pokazuj± siê
natychmiast na wszystkich innych maszynach w klastrze.

%package -n kernel%{_alt_kernel}-fs-gfs-devel
Summary:	Shared-disk cluster file system - headers
Summary(pl):	System plików dla klastrów z wspó³dzielon± przestrzeni± dyskow± - pliki nag³ówkowe
Release:	%{_rel}
Group:		Development/Libraries

%description -n kernel%{_alt_kernel}-fs-gfs-devel
Shared-disk cluster file system - headers.

%description -n kernel%{_alt_kernel}-fs-gfs-devel -l pl
System plików dla klastrów z wspó³dzielon± przestrzeni± dyskow± -
pliki nag³ówkowe.

%prep
%setup -q -n cluster-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
cd gfs-kernel
./configure \
	--kernel_src=%{_kernelsrcdir}
%if %{with kernel}
cd src
ln -s . harness/linux

ln -s ../harness nolock/linux

ln -s ../harness dlm/linux
ln -s %{_includedir}/cluster dlm/cluster

ln -s ../harness gulm/linux

ln -s . gfs/linux
ln -s ../harness/lm_interface.h gfs/lm_interface.h

for dir in harness nolock dlm gulm gfs; do
    cd $dir
	for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	    if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	    fi
	    rm -rf o
	    install -d o/include/linux
	    ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	    ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
	    ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
%if %{with dist_kernel}
	%{__make} -C %{_kernelsrcdir} O=$PWD/o prepare scripts
%else
	install -d o/include/config
	touch o/include/config/MARKER
	ln -sf %{_kernelsrcdir}/scripts o/scripts
%endif
	    %{__make} -C %{_kernelsrcdir} clean \
		USING_KBUILD=yes \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	    %{__make} -C %{_kernelsrcdir} modules \
		USING_KBUILD=yes \
		CC="%{__cc}" CPP="%{__cpp}" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}

	    case "$dir" in
		harness|nolock|dlm|gulm)
			mv lock_${dir}.ko lock_${dir}-$cfg.ko
			;;
		gfs)
			mv gfs.ko gfs-$cfg.ko
			;;
		*)
			exit 1
			;;
	    esac
	done
	cd -
done
cd -
%endif

%install
rm -rf $RPM_BUILD_ROOT

cd gfs-kernel
%if %{with kernel}
# DLM
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/fs/gfs_locking/lock_dlm
install src/dlm/lock_dlm-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/fs/gfs_locking/lock_dlm/lock_dlm.ko
%if %{with smp} && %{with dist_kernel}
install src/dlm/lock_dlm-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/fs/gfs_locking/lock_dlm/lock_dlm.ko
%endif

# GFS
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/fs/gfs
install src/gfs/gfs-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/fs/gfs/gfs.ko
%if %{with smp} && %{with dist_kernel}
install src/gfs/gfs-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/fs/gfs/gfs.ko
%endif

# GULM
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/fs/gfs_locking/lock_gulm
install src/gulm/lock_gulm-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/fs/gfs_locking/lock_gulm/lock_gulm.ko
%if %{with smp} && %{with dist_kernel}
install src/gulm/lock_gulm-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/fs/gfs_locking/lock_gulm/lock_gulm.ko
%endif

# HARNESS
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/fs/gfs_locking/lock_harness
install src/harness/lock_harness-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/fs/gfs_locking/lock_harness/lock_harness.ko
%if %{with smp} && %{with dist_kernel}
install src/harness/lock_harness-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/fs/gfs_locking/lock_harness/lock_harness.ko
%endif

# NOLOCK
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/fs/gfs_locking/lock_nolock
install src/nolock/lock_nolock-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/fs/gfs_locking/lock_nolock/lock_nolock.ko
%if %{with smp} && %{with dist_kernel}
install src/nolock/lock_nolock-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/fs/gfs_locking/lock_nolock/lock_nolock.ko
%endif
%endif

install -d $RPM_BUILD_ROOT%{_includedir}/cluster
install src/gfs/gfs_ondisk.h src/gfs/gfs_ioctl.h \
	src/harness/lm_interface.h \
		$RPM_BUILD_ROOT%{_includedir}/cluster

%clean
rm -rf $RPM_BUILD_ROOT

%post
%depmod %{_kernel_ver}

%postun
%depmod %{_kernel_ver}

%post -n kernel%{_alt_kernel}-smp-fs-gfs
%depmod %{_kernel_ver}smp

%postun -n kernel%{_alt_kernel}-smp-fs-gfs
%depmod %{_kernel_ver}smp

%if %{with kernel}
%files
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/fs/*

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-fs-gfs
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/fs/*
%endif
%endif

%files -n kernel%{_alt_kernel}-fs-gfs-devel
%defattr(644,root,root,755)
%{_includedir}/cluster
