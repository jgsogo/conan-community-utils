#!/bin/sh

commit_website_files() {
  cd ../web
  git add .
  git commit --message "Travis build: $TRAVIS_BUILD_NUMBER"
}

upload_files() {
  git push --quiet
}

commit_website_files
upload_files
