#!/bin/bash

version=1.4.5
specfile=kubernetes.spec

# clean up and clone
rm -rf ./kubernetes/ && git clone https://github.com/kubernetes/kubernetes.git

# cp init script
cp -pr init/ kubernetes/contrib/

# Find the latest tagged stable release in the master branch,
cd kubernetes; git checkout master &> /dev/null; git reset --hard &> /dev/null; git pull &> /dev/null;

kubernetes_commit="`git rev-list v${version}  | head -n 1`"
short_commit=`echo $kubernetes_commit | cut -c1-7`
cd ..;

# update the rpm spec file with the latest stable version and commit
sed -i "s/^Version:.*/Version:        ${version}/" rpmbuild/SPECS/${specfile}
sed -i "s/^%global commit.*/%global commit          ${kubernetes_commit}/" rpmbuild/SPECS/${specfile}
sed -i "s/^export KUBE_GIT_VERSION=.*/export KUBE_GIT_VERSION=${version}/" rpmbuild/SPECS/${specfile}

# clean up any old builds. tar up the latest stable commit, and throw it into rpmbuild/SOURCES, and prepare for the build
cd kubernetes; git checkout $kubernetes_commit ; cd ..;
mkdir -p rpmbuild/SOURCES
rm -rf rpmbuild/BUILD rpmbuild/BUILDROOT rpmbuild/RPMS rpmbuild/SRPMS rpmbuild/SOURCES/*
tar -c kubernetes --transform s/kubernetes/kubernetes-$kubernetes_commit/ | gzip -9 &> "rpmbuild/SOURCES/kubernetes-${short_commit}.tar.gz"

# start compiling kubernetes
echo -e "Starting the compilation of kubernetes version: $version \n\n"
rpmbuild -ba --define "_topdir `pwd`/rpmbuild" rpmbuild/SPECS/${specfile}

if [ $? -eq 0 ]
then
  rpm_file=`ls rpmbuild/RPMS/*/kubernetes*`
  echo -e "\n\n\nFinished compiling kubernetes version: $latest_stable_kubernetes_version \nThe file is located here: ./$rpm_file"
else
  echo -e "\n\n\nKubernetes compilation failed.\n" 
fi
