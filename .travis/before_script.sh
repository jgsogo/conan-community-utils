#!/bin/sh

setup_git() {
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI"
}

checkout_web() {
  git clone https://${GH_TOKEN}@github.com/jgsogo/conan-community-web.git ../web > /dev/null 2>&1
}

setup_git
checkout_web
