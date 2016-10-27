Script for building kubernetes RPM binaries

Based on the work of https://github.com/JohnTheodore/kubernetes-rpm-builder

Instructions :

1. clone the repo
2. have a recent golang installed / git / some compilatons tools
3. install go-bindata
4. edit build.sh to choose the proper version
5. ./build.sh
6. pray

Known to work at least on centos 7 for kubernetes v1.4.4.

