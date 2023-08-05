VER=$1

. ./clean.sh
. ./build.sh

zip -r ../testman4trac.$VER.zip bin
tar cvzf ../testmanager.$VER.tar.gz bin

. ./clean.sh

mkdir testman4trac.$VER

cp *.sh testman4trac.$VER
cp *.txt testman4trac.$VER
cp *.cmd testman4trac.$VER
cp -R sqlexecutor testman4trac.$VER
cp -R testman4trac testman4trac.$VER
cp -R tracgenericclass testman4trac.$VER
cp -R tracgenericworkflow testman4trac.$VER

cd testman4trac.$VER

. ./clean.sh
find . -type d -name .svn -print -exec rm -rf {} \;
find . -type d -name .hg -print -exec rm -rf {} \;
find . -type f -name "*.bak" -print -exec rm -f {} \;

cd ..

zip -r ../testman4trac.$VER.src.zip testman4trac.$VER
tar cvzf ../testmanager.$VER.src.tar.gz testman4trac.$VER

svn co https://testman4trac.svn.sourceforge.net/svnroot/testman4trac testman4trac.$VER.SVN
cd testman4trac.$VER.SVN
cp -R ../testman4trac.$VER/* .
svn status
svn add
svn commit

cd ..

hg clone https://seccanj@bitbucket.org/olemis/testman4trac testman4trac.$VER.BITBKT
cd testman4trac.$VER.BITBKT
cp -R ../testman4trac.$VER/* .
hg status
hg add
hg commit
hg push

cd ..
#rm -rf testman4trac.$VER testman4trac.$VER.SVN testman4trac.$VER.BITBKT


