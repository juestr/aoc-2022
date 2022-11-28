#!/usr/bin/env bash

if [ -z "$SESSION" ] ; then
  echo "export SESSION= missing"
  exit 1
fi
if [ -z "$1" ] ; then
  echo "Provide a number"
  exit 1
fi

fn=`printf 'aoc%02d_example.txt' $1`
echo "Touching $fn"
touch $fn

fn=`printf 'aoc%02d_input.txt' $1`
echo "Downloading input for day <$1> to $fn"

curl --cookie session=${SESSION} "https://adventofcode.com/2022/day/$1/input" | tee $fn || ( echo "something failed" && exit 1 )
