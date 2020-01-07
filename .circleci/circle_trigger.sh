#!/bin/bash
set -e

# The root directory of packages.
# Use `.` if your packages are located in root.
ROOT="." 
REPOSITORY_TYPE="github"
CIRCLE_API="https://circleci.com/api"
PROJECT_SLUG="${REPOSITORY_TYPE}/${CIRCLE_PROJECT_USERNAME}/${CIRCLE_PROJECT_REPONAME}"

############################################
## 1. Commit SHA of last CI build
############################################
if [[ ${CIRCLE_BRANCH} == "master" ]]; then
  PARENT_BRANCH=master
else
  PARENT_BRANCH=staging
fi

function circle_ci() {
  local url="$1"
  local data="$2"
  if [[ -z "$data" ]]; then
    >&2 echo "GET ${CIRCLE_API}${url}"
    curl -Ssf -u "${CIRCLE_TOKEN}:" "${CIRCLE_API}${url}"
  else
    >&2 echo "POST ${CIRCLE_API}${url}"
    curl -Ssf -u "${CIRCLE_TOKEN}:" -X "POST" --header "Content-Type: application/json" -d "${data}" "${CIRCLE_API}${url}"
  fi
}

# Returns a line for each API-triggered pipeline, containing space-separated "id" "revision"
RECENT_PIPELINES=`circle_ci "/v2/project/${PROJECT_SLUG}/pipeline?branch=${PARENT_BRANCH}" | jq -r '.items | map(select(.trigger.type == "api") | [.id, .vcs.revision] | @sh) | join("\n")'`

# Find a pipeline where the commit hash is an ancestor, and where all the workflows succeeded.
LAST_COMPLETED_BUILD_SHA=""
echo "$RECENT_PIPELINES" | while read pipeline_id revision
do
  if git merge-base --is-ancestor $revision HEAD; then
    if circle_ci "/v2/pipeline/${pipeline_id}/workflow" | jq -e '.items | all(.status == "success")' > /dev/null; then
      LAST_COMPLETED_BUILD_SHA="$revision"
      break
    fi
  fi
done

############################################
## 2. Changed packages
############################################
PACKAGES=$(ls ${ROOT} -l | grep ^d | awk '{print $9}' | grep -v '^base$')

if [[ -z "$LAST_COMPLETED_BUILD_SHA" ]]; then
  echo -e "\e[93mThere are no suitable completed CI builds in branch ${PARENT_BRANCH}.\e[0m"
else
  echo "Searching for changes since commit [${LAST_COMPLETED_BUILD_SHA:0:7}] ..."
fi

## The CircleCI API parameters object
PARAMETERS='"trigger":false'
COUNT=0
for PACKAGE in ${PACKAGES[@]}
do
  PACKAGE_PATH=${ROOT#.}/$PACKAGE
  if [[ -z "$LAST_COMPLETED_BUILD_SHA" ]]; then
    PARAMETERS+=", \"$PACKAGE\":true"
    COUNT=$((COUNT + 1))
    echo -e "\e[36m  [+] ${PACKAGE} \e[21m (changed in [${LATEST_COMMIT_SINCE_LAST_BUILD:0:7}])\e[0m"
  else
    LATEST_COMMIT_SINCE_LAST_BUILD=$(git log -1 $CIRCLE_SHA1 ^$LAST_COMPLETED_BUILD_SHA --format=format:%H --full-diff ${PACKAGE_PATH#/})

    if [[ -z "$LATEST_COMMIT_SINCE_LAST_BUILD" ]]; then
      echo -e "\e[90m  [-] $PACKAGE \e[0m"
    else
      PARAMETERS+=", \"$PACKAGE\":true"
      COUNT=$((COUNT + 1))
      echo -e "\e[36m  [+] ${PACKAGE} \e[21m (changed in [${LATEST_COMMIT_SINCE_LAST_BUILD:0:7}])\e[0m"
    fi
  fi
done

if [[ $COUNT -eq 0 ]]; then
  echo -e "\e[93mNo changes detected in packages. Skip triggering workflows.\e[0m"
  exit 0
fi

echo "Changes detected in ${COUNT} package(s)."

############################################
## 3. CicleCI REST API call
############################################
DATA="{ \"branch\": \"$CIRCLE_BRANCH\", \"parameters\": { $PARAMETERS } }"
echo "Triggering pipeline with data:"
echo -e "  $DATA"

circle_ci "/v2/project/${PROJECT_SLUG}/pipeline" "$DATA"
