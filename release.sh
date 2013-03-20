#!/bin/bash
if [ -z $1 ] || [ -z `echo ${1} | grep -E "^[0-9]+_[0-9]+_[0-9]+" | awk '{print $1}'` ]; then
    echo "Please input {RELEASE_VERSION (YYYY_MM_patch)}.";
    exit
else
    publish_version=$1
    year=`echo ${1} | grep -E "^[0-9]+_[0-9]+_[0-9]+" | awk -F_ '{print $1}'`
    week=`echo ${1} | grep -E "^[0-9]+_[0-9]+_[0-9]+" | awk -F_ '{print $2}'`
    version=`echo ${1} | grep -E "^[0-9]+_[0-9]+_[0-9]+" | awk -F_ '{print $3}'`
fi

cd /opt/release_code/git/code/
git fetch -p origin

has_remote_branch=`git branch -r | grep "release-${publish_version}" | awk '{print $1}'`
if [ -z $has_remote_branch ]; then
    echo "No version named ${publish_version}"
    exit
fi

# make sure weather the first ga this week
if [ -z `git tag | grep -E "ga-${year}_${week}_[0-9]+" | awk '{ print $1 }'` ];then
    first=1
else
    first=0
fi


# find the next build version
CUR_BUILD=`git tag | grep -E "^ga-${publish_version}\+build\.[0-9]+" | awk -F. '{ print $2 }' | grep -o -E "^[0-9]+" | sort -n | tail -n 1`

if [ $CUR_BUILD ]; then
    NEXT_BUILD=`expr $CUR_BUILD + 1`
else
    NEXT_BUILD=1
fi

TAG="ga-${publish_version}+build.${NEXT_BUILD}"

# checkout to release
git checkout master
has_local_branch=`git branch | grep "release-${publish_version}" | awk '{print $1}'`
if [ -z $has_local_branch ]; then
    git checkout -b release-${publish_version} origin/release-${publish_version}
else 
    git checkout release-${publish_version}
    git pull origin release-${publish_version}
fi

# tag it and push to upstream
git tag ${TAG} -m "Release time: `date \"+%Y-%m-%d %H:%M:%S\"`"
git push origin ${TAG}


# delete tags created earlier this week
#for i in `git tag | grep -E "^ga-${year}_${week}_[0-9]+" | awk -F_ '{print $3}'`
#do
#   cur_ver=`echo $i | awk -F+ '{print $1}'`
#   cur_build=`echo $i | awk -F. '{print $2}'`
#   if [ $cur_ver -lt $version ] || ([ $cur_ver -eq $version ] && [ $cur_build -lt $NEXT_BUILD ]); then
#       git tag -d ga-${year}_${week}_${cur_ver}+build.${cur_build}
#       git push origin :ga-${year}_${week}_${cur_ver}+build.${cur_build}
#   fi
#done

# delete releases two weeks ago
if [ 1 = $first ];then
    for i in `git branch -r | grep -E "release-[0-9]+_[0-9]+_[0-9]+" | awk -F- '{print $2}'`
    do
        cur_year=`echo $i | awk -F_ '{print $1}'`
        cur_week=`echo $i | awk -F_ '{print $2}'`
        cur_ver=`echo $i | awk -F_ '{print $3}'`	

	if [ $cur_year -lt $year ];then
	    x=`expr 54 - ${cur_week} + $week`
        else
            x=`expr ${week} - ${cur_week}`
	fi
	
        if [ $x -ge '3' ]; then
            git push origin :release-${i}
        fi
    done
fi

dsh -c \
    -m app10-003.i.ajkdns.com \
    -m app10-005.i.ajkdns.com \
    -m app10-006.i.ajkdns.com \
    -m idx10-002.i.ajkdns.com \
    -m idx10-001.i.ajkdns.com \
    -m bjob10-001.i.ajkdns.com \
    -m xapp10-061.i.ajkdns.com \
    -m xapp10-062.i.ajkdns.com \
    -m xapp10-081.i.ajkdns.com \
    -m app10-080.i.ajkdns.com \
    -m app10-078.i.ajkdns.com \
    "/home/www/bin/release-version.sh" $1

#CUR_DIR=`pwd`
#$CUR_DIR/mail-log.sh $1
