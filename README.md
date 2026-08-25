# Elara X NRLMSIS 2.0 Native Compatibility

A separately packaged first-class NRLMSIS 2.0 compatibility implementation from the accepted Elara X atmospheric-model programme. It uses the accepted native NRLMSIS 2.1 scientific core with nitric oxide disabled and excluded from aggregate mass density, in a separate Python state namespace.

## Accepted scientific result

The frozen M18 comparison covered 200 official cases and 2,200 scalar outputs (`D(1:9)`, `TEX`, `TN`) through the official IEEE-754 binary32 GTD8D boundary. There were zero bitwise differences and zero frozen-tolerance mismatches. The accepted scientific identity is `c720f852e4966c1fd3519618c46858d6494a0a40f702ff0eb8271abcb567d14e`.

## Resource and source boundary

No official NRLMSIS 2.0 Fortran, parameter file, test input, reference output, or oracle binary is included. Model parameter resources remain external and are verified by the packaged resolver. The full Elara X application is not included.

## Release state

This repository is `0.1.0.dev0`. No final Git tag or release is created until the complete atmospheric-model/paper freeze.
