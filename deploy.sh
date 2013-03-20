#:w!/bin/bash
#显示帮助信息
show_help(){
echo "*************************************script help***************************************************"
echo "*                                                                                                 *"
echo "*                                                                                                 *"
echo "*  1. publish version: sh deploy.sh 2012_03(publish_version) a000001(SHA-1,optional)              *"
echo "*  2. update version: sh deploy.sh 2012_03_1(publish_version) a000001(SHA-1,optional)             *"
echo "*                                                                                                 *"
echo "*                                                                                                 *"
echo "******************************************end******************************************************"
}

if [ -z $1 ] || [ "$1" = "-help" ]; then
   echo "Use -help to show this help info again."
   show_help
   exit
fi

version=`echo $1 | grep '^[0-9]\{4\}_[0-9]\{1,2\}$'`
version1=`echo $1 | grep '^[0-9]\{4\}_[0-9]\{1,2\}_[0-9]\{1,3\}$'`

if [ -n "$version" ] ||  [ -n "$version1" ]; then
    if [ -n "$version" ]; then
        changeVersion=1
        echo "You are going to release a new version:${version}"
    fi
    if [ -n "$version1" ]; then
        changeVersion=0
        echo "You are going to update version:${version1}"
    fi
else
    echo "Unknown command:${1}"
    show_help
    exit
fi

RELEASE_ROOT="/opt/release_code/git/code/";
CODE_PATH='/opt/release_code/git/code/';
VERSION_PATH='/opt/release_code/git/version/'


df -m $CODE_PATH
ret=`df -m $CODE_PATH | awk '{if ($4 < 500) print -1; else print 1; }'`
ret2=`echo $ret | awk '{print $2}'`
if [ "$ret2" = "-1" ]; then
   echo "No enough space release code (less 500M) and exit.\n";
   exit
fi

#获取当前小版本号
get_num(){
   version_num=`ls "$VERSION_PATH" | grep "$1" | awk -F_ '{print $NF}' | sort -n -r | head -n 1`
   if [ -z $version_num ]; then
      version_num=1
   else
      version_num=`/usr/bin/expr $version_num + 1`
   fi

   return $version_num
}

if [ 1 = $changeVersion ]; then
    get_num $version
    #获取返回值
    NUM=$?
    publish_version="${version}_${NUM}"
else
    publish_version="${version1}"
fi

cd $RELEASE_ROOT

git fetch origin
#若该分支已存在，先删掉
has_remote_branch=`git branch -r | grep "release-${publish_version}" | awk '{print $1}'`
if [ ! -z $has_remote_branch ]; then
  git push origin :release-$publish_version
fi

git checkout master
has_local_branch=`git branch | grep "release-${publish_version}" | awk '{print $1}'`
if [ ! -z $has_local_branch ]; then
  git branch -D release-$publish_version
fi

#创建分支
if [ ! -z $2 ]; then
    git branch release-$publish_version $2
    git checkout release-$publish_version
else
    git checkout master
    git rebase origin/master
    git checkout -b release-$publish_version
fi
sleep 2
git push origin release-$publish_version

#rsync -avz --exclude-from="/home/www/release/ignore.haozu_git" $RELEASE_ROOT -e ssh evans@10.10.6.139:/home/rsync/code/$publish_version

rsync -avz --exclude-from="/home/www/release/ignore.haozu_git" $RELEASE_ROOT -e ssh evans@app10-003.i.ajkdns.com:/home/www/release/$publish_version

dsh -c \
    -m bjob10-001.i.ajkdns.com \
    -m idx10-001.i.ajkdns.com \
    -m idx10-002.i.ajkdns.com \
    -m app10-005.i.ajkdns.com \
    -m app10-006.i.ajkdns.com \
    -m xapp10-061.i.ajkdns.com \
    -m xapp10-062.i.ajkdns.com \
    -m xapp10-081.i.ajkdns.com \
    -m app10-080.i.ajkdns.com \
    -m app10-078.i.ajkdns.com \
    "/home/www/bin/release-rsync.sh" $publish_version

#更新pages
PAGES_PATH="/opt/release_code/git/pages/"
cd $PAGES_PATH
git pull origin master
rsync -av  --exclude-from="/home/www/release/ignore.haozu_git" $PAGES_PATH -e ssh evans@app10-003.i.ajkdns.com:/home/www/pages/

#最后更新vertion文件
if [ 1 = $changeVersion ]; then
    CURTIME=$(date +%Y/%m/%d_%T)
    str="created:${CURTIME}"
    echo $str >> $VERSION_PATH$publish_version
else
    CURTIME=$(date +%Y/%m/%d_%T)
    str="updated:${CURTIME}"
    echo $str >> $VERSION_PATH$publish_version
fi

#如果是更新版本，检查是否是线上版本
if [ 0 = $changeVersion ] && [ ! -z `git tag | grep -E "ga-${publish_version}" | awk '{ print $1 }'` ];then
    sh /opt/release_code/git/deploy/release.sh ${publish_version}
fi

echo "Version:${publish_version} complete."
exit

