#!/bin/sh

commit_website_files() {
  cd ../web
  pwd
  ls -la
  git add .
  git commit --message "Travis build: $TRAVIS_BUILD_NUMBER"
}

upload_files() {
  cd ../web
  pwd
  ls -la
  git push --quiet
}

commit_website_files
upload_files
