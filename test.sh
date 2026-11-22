oldpwd=$PWD
make clean && make picoPC
node test.js
cp Board.json sim/
cd sim
npm install .
NAME=InternalSD.img
truncate -s 64M $NAME
sudo mkfs.vfat $NAME
IMG=$NAME npm run mount
cp -a $oldpwd/SD0/. ./mnt_dir
npm run unmount
mv $NAME firmware/
NAME=ExternalSD.img
truncate -s 64M $NAME
sudo mkfs.vfat $NAME
IMG=$NAME npm run mount
mv $NAME firmware/
rm -a ./mnt_dir/*
cp -a $oldpwd/SD1/. ./mnt_dir
npm run unmount
IMG=firmware/firmfs.img npm run mount
cp -a $oldpwa/out/. ./mnt_dir
npm run unmount
npm run start
cd $oldpwd