#!/bin/bash

# Util script to merge multiple branches as listed in a file into a new branch
# Used for dev.openlibrary.org "deploys"
# See make-integration-branch-sample.txt for a sample of the file format.

BRANCHES_FILE=$1
NEW_BRANCH=$2

git checkout master
git pull origin master

# First clean up the file of any branches that are already in master
while read line; do
    if [[ $line == "https://"* || $line == "#https://"* || $line == '**https://'* ]] ; then
        branch=${line/#/}
        branch=${branch/\*\*/}

        git checkout master > /dev/null 2>&1
        git branch -D $NEW_BRANCH > /dev/null 2>&1
        git checkout -b $NEW_BRANCH > /dev/null 2>&1
        pull_resp=$(git pull $branch 2>&1)
        git diff --quiet master
        # branch deleted
        if [[ $? -eq 0 || pull_resp == *"Couldn't find remote ref"* ]] ; then
            echo "Remove old line: $line"
        else
            echo $line >> "_tmp_$BRANCHES_FILE"
        fi
    else
        echo $line >> "_tmp_$BRANCHES_FILE"
    fi
done <"$BRANCHES_FILE"

mv "_tmp_$BRANCHES_FILE" "$BRANCHES_FILE"
ONLY_STARRED=$(grep '^\*\*' $BRANCHES_FILE | sed 's/\*\*//g' )
git branch -D $NEW_BRANCH
git checkout -b $NEW_BRANCH

while read line; do
    branch=${line/\*\*/}
    branch=$(echo $branch | grep -o -E '^[^#]+')
    if [[ -z $line || $line == "#"* ]] ; then
        :
    elif [[ ! -z $ONLY_STARRED && $line != "**"* ]] ; then
        :
    elif [[ $branch == "https://github.com/internetarchive/openlibrary/pull/"*".patch" ]] ; then
        echo -e "---\n$line"
        curl -L $branch | git am -3
    elif [[ $branch == "https://"* || $branch == "origin pull/"* ]] ; then
        echo -e "---\n$line"
        git pull $branch
        # If the merge didn't succeed automatically, abort it
        [[ $(git ls-files -u) ]] && git merge --abort
    else
        echo -e "---\n$line"
        git merge $branch
        # If the merge didn't succeed automatically, abort it
        [[ $(git ls-files -u) ]] && git merge --abort
    fi
done <"$BRANCHES_FILE"

echo "---"
echo "Complete; dev-merged created (SHA: $(git rev-parse --short HEAD))"
