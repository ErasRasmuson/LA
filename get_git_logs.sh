#!/usr/bin/env bash

set -e

git log --format="%ad %s" > All_versions.log
git log --format="%ad %s" LogAna/ > LogAna_versions.log
git log --format="%ad %s" LogCom/ > LogCom_versions.log
git log --format="%ad %s" LogDig/ > LogDig_versions.log
git log --format="%ad %s" LogGen/ > LogGen_versions.log
git log --format="%ad %s" LogPrep/ > LogPrep_versions.log
git log --format="%ad %s" LogTestGen/ > LogTestGen_versions.log
git log --format="%ad %s" SSDPrep/ > SSDPrep_versions.log
