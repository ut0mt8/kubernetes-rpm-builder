#debuginfo not supported with Go
%global debug_package	%{nil}
%global provider	github
%global provider_tld	com
%global project		GoogleCloudPlatform
%global repo		kubernetes
%global import_path	%{provider}.%{provider_tld}/%{project}/%{repo}
%global commit          5a0a696437ad35c133c0c8493f7e9d22b0f9b81b
%global shortcommit	%(c=%{commit}; echo ${c:0:7})

#I really need this, otherwise "version_ldflags=$(kube::version_ldflags)"
# does not work
%global _buildshell	/bin/bash
%global _checkshell	/bin/bash

Name:		kubernetes
Version:        1.4.5
Release:	1%{?dist}
Summary:	Container cluster management
License:	ASL 2.0
URL:		https://github.com/kubernetes/kubernetes/
ExclusiveArch:	x86_64
Source0:	https://github.com/kubernetes/kubernetes/archive/%{commit}/kubernetes-%{shortcommit}.tar.gz

# cadvisor is integrated into kubelet
Obsoletes:      cadvisor

Requires(pre):	shadow-utils

BuildRequires:	systemd
BuildRequires:	etcd >= 2.0.8
BuildRequires:	hostname
BuildRequires:	rsync

%description
%{summary}

%prep
%autosetup -n %{name}-%{commit} -p1

%build
export KUBE_GIT_TREE_STATE="clean"
export KUBE_GIT_COMMIT=%{commit}
export KUBE_GIT_VERSION=1.4.5

make all

%check

%install
. hack/lib/init.sh
kube::golang::setup_env

mkdir -p $RPM_BUILD_ROOT/var/run/kubernetes
output_path="${KUBE_OUTPUT_BINPATH}/$(kube::golang::current_platform)"

binaries=(kube-apiserver kube-controller-manager kube-scheduler kube-proxy kubelet kubectl)
install -m 755 -d %{buildroot}%{_bindir}
for bin in "${binaries[@]}"; do
  echo "+++ INSTALLING ${bin}"
  install -p -m 755 -t %{buildroot}%{_bindir} ${output_path}/${bin}
done

# install config files
install -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}
install -m 644 -t %{buildroot}%{_sysconfdir}/%{name} contrib/init/systemd/environ/*

# install service files
install -d -m 0755 %{buildroot}%{_unitdir}
install -m 0644 -t %{buildroot}%{_unitdir} contrib/init/systemd/*.service

# install manpages
install -d %{buildroot}%{_mandir}/man1
install -p -m 644 docs/man/man1/* %{buildroot}%{_mandir}/man1

# install the place the kubelet defaults to put volumes
install -d %{buildroot}/var/lib/kubelet

# place contrib/init/systemd/tmpfiles.d/kubernetes.conf to /usr/lib/tmpfiles.d/kubernetes.conf
install -d -m 0755 %{buildroot}%{_tmpfilesdir}
install -p -m 0644 -t %{buildroot}/%{_tmpfilesdir} contrib/init/systemd/tmpfiles.d/kubernetes.conf

%package master
Summary: %{summary} master parts
%description master
%{summary} master parts

%files master
%doc README.md LICENSE CONTRIB.md CONTRIBUTING.md DESIGN.md
%{_mandir}/man1/*
%{_bindir}/kube-apiserver
%{_bindir}/kubectl
%{_bindir}/kube-controller-manager
%{_bindir}/kubelet
%{_bindir}/kube-proxy
%{_bindir}/kube-scheduler
%{_unitdir}/kube-apiserver.service
%{_unitdir}/kubelet.service
%{_unitdir}/kube-scheduler.service
%{_unitdir}/kube-controller-manager.service
%{_unitdir}/kube-proxy.service
%dir %{_sysconfdir}/%{name}
%dir /var/lib/kubelet
%config(noreplace) %{_sysconfdir}/%{name}/config
%config(noreplace) %{_sysconfdir}/%{name}/apiserver
%config(noreplace) %{_sysconfdir}/%{name}/controller-manager
%config(noreplace) %{_sysconfdir}/%{name}/proxy
%config(noreplace) %{_sysconfdir}/%{name}/kubelet
%config(noreplace) %{_sysconfdir}/%{name}/scheduler
%{_tmpfilesdir}/kubernetes.conf

%dir /var/run/kubernetes
%attr(755,kube,kube) /var/run/kubernetes

%pre master
getent group kube >/dev/null || groupadd -r kube
getent passwd kube >/dev/null || useradd -r -g kube -d / -s /sbin/nologin \
        -c "Kubernetes user" kube
%post master
%systemd_post kube-apiserver kube-scheduler kube-controller-manager kubelet kube-proxy

%preun master
%systemd_preun kube-apiserver kube-scheduler kube-controller-manager kubelet kube-proxy

%postun master
%systemd_postun 
/master


%package node
Summary: %{summary} node parts
%description node 
%{summary} node parts

%files node 

%doc README.md LICENSE CONTRIB.md CONTRIBUTING.md DESIGN.md
%{_mandir}/man1/*
%{_bindir}/kubectl
%{_bindir}/kubelet
%{_bindir}/kube-proxy
%{_unitdir}/kubelet.service
%{_unitdir}/kube-proxy.service
%dir %{_sysconfdir}/%{name}
%dir /var/lib/kubelet
%config(noreplace) %{_sysconfdir}/%{name}/config
%config(noreplace) %{_sysconfdir}/%{name}/proxy
%config(noreplace) %{_sysconfdir}/%{name}/kubelet
%{_tmpfilesdir}/kubernetes.conf

%dir /var/run/kubernetes
%attr(755,kube,kube) /var/run/kubernetes

%dir /var/run/kubernetes
%attr(755,kube,kube) /var/run/kubernetes

%pre node
getent group kube >/dev/null || groupadd -r kube
getent passwd kube >/dev/null || useradd -r -g kube -d / -s /sbin/nologin \
        -c "Kubernetes user" kube
%post node
%systemd_post kubelet kube-proxy

%preun node
%systemd_preun kubelet kube-proxy

%postun node
%systemd_postun
/node

