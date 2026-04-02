#!/usr/bin/env bash

# Before releasing:
# In root directory
# Clear directory build/
# python setup.py develop
# mathics/
#   python test.py -o
#   python test.py -t
# mathics/doc/tex/
#   make latex
# Then run this file.

admin_dir=$(dirname ${BASH_SOURCE[0]})
cd $(dirname ${BASH_SOURCE[0]})
owd=$(pwd)
cd ..
version=`python -c "import mathics; print(mathics.__version__)"`
echo "Releasing Mathics3_Scanner $version"

rm -rf build/release
python setup.py build
mkdir build/release

zipfilename="mathics-scanner-$version.zip"
tgzfilename="mathics-scanner-$version.tgz"
releasedir="mathics-scanner-$version"
rm -f "build/$zipfilename"
rm -f "build/$tgzfilename"
cd build/
cp -r release/ $releasedir/
echo "Creating ZIP file $zipfilename"
zip -r $zipfilename $releasedir/
echo "Creating TGZ file $tgzfilename"
tar czf $tgzfilename $releasedir/
cd ..

mkdir -p Homepage/release
cp "build/$zipfilename" Homepage/release/

echo "Done"
