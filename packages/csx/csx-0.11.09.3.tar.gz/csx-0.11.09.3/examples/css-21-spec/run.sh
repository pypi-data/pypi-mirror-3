#!/bin/bash

# CSX example - CSS 2.1 spec stylesheet

set -e

NAME="css-21-spec"

cd $(dirname ${0})

dir="examples/${NAME}"
cwd2="$(basename $(dirname $(pwd)))/$(basename $(pwd))"

if [[ ${dir} != ${cwd2} ]]
then
    echo >&2 "${0}: must be run from ${dir}"
    exit 2
else
    echo "removing existing output files"
    rm -rf split csx compact bare pretty
    mkdir split csx compact bare pretty

    echo "splitting original/default.css into print and all-media stylesheets"
    sed '/^@media print {$/,$d' original/default.css > split/all.css
    sed '1,/^@media print {$/d;$d' original/default.css > split/print.css

    cd ../..
    export PATH=".:${PATH}"

    for name in all print
    do
        echo "converting ${name}.css to CSX"
        csx --aggressive ${dir}/split/${name}.css > ${dir}/csx/${name}.csx
        for style in bare compact pretty
        do
            echo "converting ${name}.csx to ${style} CSS"
            csx --${style} ${dir}/csx/${name}.csx > ${dir}/${style}/${name}.css
        done
    done
fi

