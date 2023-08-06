#!/bin/bash

mkdir iwaters
cd iwaters
cp -r ../static/* .
find -name .svn -exec rm -rf {} \;
cd ..
zip -r iwaters.zip iwaters
rm -rf  iwaters/
