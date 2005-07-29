#
# Condtional build:
%bcond_without  kernel          # don't build kernel modules
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	smp		# without smp packages
%bcond_with	verbose		# verbose build (V=1)
#
%define	snap	20050729
%define _rel	0.%{snap}.1
Name:		kernel-cluster-gfs
Summary:	Shared-disk cluster file system
Version:	0.1
Release:	%{_rel}@%{_kernel_ver_str}
Epoch:		0
License:	GPL v2
Group:		Base/Kernel
Source0:	cluster-gfs-%{snap}.tar.gz
# Source0-md5:	7be8fb3998d0c5d1c2462e8cd61ddda9
URL:		http://sources.redhat.com/cluster/gfs/
BuildRequires:	perl-base
BuildRequires:	cman-devel
BuildRequires:	dlm-devel
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.7}
%endif
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

%package -n kernel-smp-cluster-gfs
Summary:	kernel-smp-cluster-gfs
Summary(pl):	Shared-disk cluster file system
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel-smp}

%description -n kernel-smp-cluster-gfs
GFS (Global File System) is a cluster file system. It allows a cluster
of computers to simultaneously use a block device that is shared
between them (with FC, iSCSI, NBD, etc...). GFS reads and writes to
the block device like a local filesystem, but also uses a lock module
to allow the computers coordinate their I/O so filesystem consistency
is maintained. One of the nifty features of GFS is perfect consistency
-- changes made to the filesystem on one machine show up immediately
on all other machines in the cluster.

%package -n gfs-devel
Summary:	Shared-disk cluster file system - headers
Release:	%{_rel}
Group:		Development/Libraries

%description -n gfs-devel
Shared-disk cluster file system - headers.

%prep
%setup -q -n cluster-gfs-%{snap}

%build
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
	    rm -rf include
	    install -d include/{linux,config}
	    ln -sf %{_kernelsrcdir}/config-$cfg .config
	    ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
	    ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
	    %if %{without dist_kernel}
	        [ ! -x %{_kernelsrcdir}/scripts/kallsyms ] || ln -sf %{_kernelsrcdir}/scripts
	    %endif
	    touch include/config/MARKER
	    %{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	    %{__make} -C %{_kernelsrcdir} modules \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		CC="%{__cc}" CPP="%{__cpp}" \
		M=$PWD O=$PWD \
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

%post -n kernel-smp-cluster-gfs
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-cluster-gfs
%depmod %{_kernel_ver}smp

%if %{with kernel}
%files
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/fs/*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-cluster-gfs
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/fs/*
%endif
%endif

%files -n gfs-devel
%defattr(644,root,root,755)
%{_includedir}/cluster
