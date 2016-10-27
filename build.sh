#!/bin/bash

latest_stable_kubernetes_version=1.4.4
specfile=kubernetes.spec

git clone https://github.com/kubernetes/kubernetes.git
cd kubernetes; git checkout master ; git reset --hard ; git pull ;

latest_stable_kubernetes_commit="`git rev-list v${latest_stable_kubernetes_version}  | head -n 1`"
short_commit=`echo $latest_stable_kubernetes_commit | cut -c1-7`
cd ..;

# update the rpm spec file with the latest stable version and commit
sed -i "s/^Version:.*/Version:        ${latest_stable_kubernetes_version}/" rpmbuild/SPECS/${specfile}
sed -i "s/^%global commit.*/%global commit          ${latest_stable_kubernetes_commit}/" rpmbuild/SPECS/${specfile}
sed -i "s/^export KUBE_GIT_VERSION=.*/KUBE_GIT_VERSION=${latest_stable_kubernetes_version-${short_commit}}/" rpmbuild/SPECS/${specfile}

# clean up any old builds. tar up the latest stable commit, and throw it into rpmbuild/SOURCES, and prepare for the build
cd kubernetes; git checkout $latest_stable_kubernetes_commit ; cd ..;
mkdir -p rpmbuild/SOURCES
rm -rf rpmbuild/BUILD rpmbuild/BUILDROOT rpmbuild/RPMS rpmbuild/SRPMS rpmbuild/SOURCES/kubernetes-*.tar.gz
tar -c kubernetes --transform s/kubernetes/kubernetes-$latest_stable_kubernetes_commit/ | gzip -9 &> "rpmbuild/SOURCES/kubernetes-${short_commit}.tar.gz"

# start compiling kubernetes
echo -e "Starting the compilation of kubernetes version: $latest_stable_kubernetes_version \n\n"
rpmbuild -ba --define "_topdir `pwd`/rpmbuild" rpmbuild/SPECS/${specfile}

if [ $? -eq 0 ]
then
  rpm_file=`ls rpmbuild/RPMS/*/kubernetes*`
  echo -e "\n\n\nFinished compiling kubernetes version: $latest_stable_kubernetes_version \nThe file is located here: ./$rpm_file"
else
  echo -e "\n\n\nKubernetes compilation failed.\n" 
fi
