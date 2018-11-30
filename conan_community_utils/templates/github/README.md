{% set travis = recipe.get_travis_status(branch=branch) %}
{% set appveyor = recipe.get_appveyor_status(branch=branch) %}

{% if travis %}[![Build Status]({{ travis.image_url }})]({{ travis.url }}){% endif %}
{% if appveyor %}[![Build Status]({{ appveyor.image_url }})]({{ appveyor.url }}){% endif %}


# {{ recipe.id }}

{% set pck_version = recipe.get_bintray_package_version(branch=branch) %}
{% if pck_version %}
[Conan]({{ pck_version.url }}) package for {{ recipe.id }} library.


## Basic setup

    $ conan install {{ pck_version }}
    
## Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*
    
    [requires]
    {{ pck_version }}

    [options]
    
    [generators]
    cmake

Complete the installation of requirements for your project running:

    conan install . 

Project setup installs the library (and all his dependencies) and generates the files *conanbuildinfo.cmake* with all the 
paths and variables that you need to link with your dependencies.

{% endif %}