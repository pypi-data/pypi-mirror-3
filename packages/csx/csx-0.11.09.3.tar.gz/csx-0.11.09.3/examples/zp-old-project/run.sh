#!/bin/bash

# CSX example - CSS 2.1 spec stylesheet

set -e

NAME="zp-old-project"

cd $(dirname ${0})

dir="examples/${NAME}"
cwd2="$(basename $(dirname $(pwd)))/$(basename $(pwd))"

if [[ ${dir} != ${cwd2} ]]
then
    echo >&2 "${0}: must be run from ${dir}"
    exit 2
else
    echo "removing existing output files"
    rm -rf csx compact bare pretty
    mkdir csx compact bare pretty

    cd ../..
    export PATH=".:${PATH}"

    for name in l m s x
    do
        echo "converting ${name}.css to CSX"
        csx --aggressive ${dir}/original/${name}/*.css > ${dir}/csx/${name}.csx
        for style in bare compact pretty
        do
            echo "converting ${name}.csx to ${style} CSS"
            csx --${style} ${dir}/csx/${name}.csx > ${dir}/${style}/${name}.css
        done
    done
fi

