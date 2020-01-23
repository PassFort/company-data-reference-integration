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
    curl -Ssf -u "${CIRCLE_TOKEN}:" "${CIRCLE_API}${url}"
  else
    curl -Ssf -u "${CIRCLE_TOKEN}:" -X "POST" --header "Content-Type: application/json" -d "${data}" "${CIRCLE_API}${url}"
  fi
}

QUERY_PARAM="branch=${PARENT_BRANCH}"
LAST_COMPLETED_BUILD_SHA=""

# Loop through a page of results at a time
while [[ -z "$LAST_COMPLETED_BUILD_SHA" && -n "$QUERY_PARAM" ]]
do
  PIPELINE_JSON=`circle_ci "/v2/project/${PROJECT_SLUG}/pipeline?${QUERY_PARAM}"`
  QUERY_PARAM=`echo "$PIPELINE_JSON" | jq -r '"page-token=\(.next_page_token | select(.))"'`

  # Returns a line for each API-triggered pipeline, containing space-separated "id" "revision"
  RECENT_PIPELINES=`echo "$PIPELINE_JSON" | jq -r '.items | map(select(.trigger.type == "api") | [.id, .vcs.revision, .created_at] | @tsv) | join("\n")'`

  # Find a pipeline where the commit hash is an ancestor, and where all the workflows succeeded.
  while read pipeline_id revision created_at
  do
    BUILD_DATE=`date -d "$created_at" "+%Y-%m-%d %H:%M:%S"`
    echo -n "Checking revision [${revision:0:7}] (built ${BUILD_DATE} by pipeline ${pipeline_id})... "
    if git merge-base --is-ancestor $revision HEAD; then
      LATEST_WORKFLOWS=`circle_ci "/v2/pipeline/${pipeline_id}/workflow" | jq '.items | group_by(.name) | map(max_by(.created_at))'`
      if echo "$LATEST_WORKFLOWS" | jq -e 'all(.status == "success")' > /dev/null; then
        LAST_WORKFLOWS=`echo "$LATEST_WORKFLOWS" | jq -r 'map([.name, .id] | @tsv) | join("\n")'`
        LAST_COMPLETED_BUILD_SHA="$revision"
        echo -e "\e[92mOK!\e[0m"
        break
      else
        echo -e "\e[31mNot successful.\e[0m"
      fi
    else
      echo -e "\e[31mNot an ancestor.\e[0m"
    fi
  done <<< "$RECENT_PIPELINES"
done

############################################
## 1.1. Find triggering workflow
############################################

if [[ -n "$LAST_COMPLETED_BUILD_SHA" ]]; then
  QUERY_PARAM="branch=${PARENT_BRANCH}"
  TRIGGER_BUILD_NUM=""

  # Loop through a page of results at a time
  while [[ -z "$TRIGGER_BUILD_NUM" && -n "$QUERY_PARAM" ]]
  do
    PIPELINE_JSON=`circle_ci "/v2/project/${PROJECT_SLUG}/pipeline?${QUERY_PARAM}"`
    QUERY_PARAM=`echo "$PIPELINE_JSON" | jq -r '"page-token=\(.next_page_token | select(.))"'`

    # Returns a line for each API-triggered pipeline, containing space-separated "id" "revision"
    RECENT_PIPELINES=`echo "$PIPELINE_JSON" | jq -r '.items | map(select(.trigger.type != "api") | [.id, .vcs.revision] | @tsv) | join("\n")'`

    # Find a pipeline where the commit hash is an ancestor, and where all the workflows succeeded.
    while read pipeline_id revision
    do
      if [[ "$revision" == "$LAST_COMPLETED_BUILD_SHA" ]]; then
        TRIGGER_WORKFLOW_ID=`circle_ci "/v2/pipeline/${pipeline_id}/workflow" | jq -r '.items | max_by(.created_at) | .id'`
        TRIGGER_BUILD_NUM=`circle_ci "/v2/workflow/${TRIGGER_WORKFLOW_ID}/job" | jq -r '.items | max_by(.started_at) | .job_number'`
        COVERAGE_ARTIFACTS=`circle_ci "/v2/project/${PROJECT_SLUG}/${TRIGGER_BUILD_NUM}/artifacts" | jq -r '.items | map(select(.path | startswith("coverage/")) | [.path, .url] | @tsv) | join("\n")'`
        break
      fi
    done <<< "$RECENT_PIPELINES"
  done

  echo
  echo "Triggered by build ${TRIGGER_BUILD_NUM} in workflow ${TRIGGER_WORKFLOW_ID}."

  while read workflow_name workflow_id
  do
    LAST_BUILDS=`circle_ci "/v2/workflow/${workflow_id}/job" | jq -r '.items | map([.name, .job_number] | @tsv) | join("\n")'`
    while read build_name build_num
    do
      ARTIFACT_URL=`circle_ci "/v2/project/${PROJECT_SLUG}/${build_num}/artifacts" | jq -r '.items | map(select(.path == "coverage.xml")) | first | .url | select(.)'`
      if [[ -n "$ARTIFACT_URL" ]]; then
        ARTIFACT_PATH="coverage/${workflow_name}/${build_name}.xml"
        COVERAGE_ARTIFACTS="$COVERAGE_ARTIFACTS"$'\n'"$ARTIFACT_PATH"$'\t'"$ARTIFACT_URL"
      fi
    done <<< "$LAST_BUILDS"
  done <<< "$LAST_WORKFLOWS"

  echo "Previous artifacts:"
  echo "$COVERAGE_ARTIFACTS"
fi

echo

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

      # Remove coverage for packages we are going to rebuild
      COVERAGE_ARTIFACTS=`echo "$COVERAGE_ARTIFACTS" | sed "/^coverage\/$PACKAGE\//d"`
    fi
  fi
done

if [[ -n "$LAST_COMPLETED_BUILD_SHA" ]]; then
  mkdir coverage

  while read artifact_path artifact_url
  do
    if [[ -n "$artifact_url" ]]; then
      echo "Downloading previous coverage report: $artifact_url"
      curl "$artifact_url?circle-token=$CIRCLE_TOKEN" --create-dirs -o "$artifact_path"
    fi
  done <<< "$COVERAGE_ARTIFACTS"

  bash <(curl -s https://codecov.io/bash) -s coverage -f "*.xml"
fi

echo

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
