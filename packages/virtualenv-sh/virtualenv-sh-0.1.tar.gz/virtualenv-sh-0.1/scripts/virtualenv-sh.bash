_virtualenv_sh_complete_cdvirtualenv()
{
    
    local cur="$2"
    COMPREPLY=( $(cdvirtualenv && compgen -d -- "${cur}" ) )
}


_virtualenv_sh_complete_sitepackages()
{
    
    local cur="$2"
    COMPREPLY=( $(cdsitepackages && compgen -d -- "${cur}" ) )
}


_virtualenv_sh_complete_virtualenvs()
{
    
    local cur="${COMP_WORDS[COMP_CWORD]}"
    COMPREPLY=( $(compgen -W "`virtualenv-sh-virtualenvs`" -- ${cur}) )
}


autoworkon()
{
    
    virtualenv_sh_verify_workon_home || return 1
    
    
    # Never override a manually set virtualenv.
    if [ -n "${VIRTUAL_ENV:-}" ] && [ ! "${VIRTUAL_ENV:-}" = "${_virtualenv_sh_auto_virtualenv:-}" ]; then
        return 0
    fi
    
    
    # Look for a .workon file in our path. This should contain the name of a
    # virtualenv in $WORKON_HOME.
    _dot_workon=$(find_in_parents .workon)
    
    if [ -r "${_dot_workon}" ]; then
        read _new_virtualenv < "${_dot_workon}"
    fi
    
    
    # Update the virtualenv, if warranted.
    if [ -n "${_new_virtualenv:-}" ]; then
        if [ ! "${_new_virtualenv}" = "${VIRTUAL_ENV##*/}" ]; then
            workon "${_new_virtualenv}"
            _virtualenv_sh_auto_virtualenv="${VIRTUAL_ENV:-}"
        fi
    else
        if [ -n "${_virtualenv_sh_auto_virtualenv:-}" ]; then
            deactivate
        fi
    fi
    
    
    unset _dot_workon
    unset _new_virtualenv
}


cdsitepackages()
{
    
    virtualenv_sh_verify_workon_home || return 1
    virtualenv_sh_verify_active_virtualenv || return 1
    
    cd "$(virtualenv_sh_site_packages_path)"/"$1"
}


cdvirtualenv()
{
    
    virtualenv_sh_verify_workon_home || return 1
    virtualenv_sh_verify_active_virtualenv || return 1
    
    cd "$VIRTUAL_ENV"/"$1"
}


find_in_parents()
{
    
    # Bonus function: searches the current directly and all parents for a
    # filesystem item with a name matching any argument.
    #
    # e.g. find_in_parents .git .hg .svn
    
    if [ -n "${ZSH_VERSION:-}" ]; then
        local chpwd chpwd_functions # zsh: disable chpwd hooks during this function
    fi
    
    if [ ! -d "${PWD}" ]; then
        return 2
    fi
    
    _pwd_save="$PWD"
    _found_in_parents=
    
    while [ -z "${_found_in_parents}" ]; do
        for target in "$@"; do
            if [ -e "./$target" ]; then
                echo "${PWD}/${target}"
                _found_in_parents=1
            fi
        done
    
        if [ "${PWD}" = "/" ]; then
            _found_in_parents=0
        else
            cd ..
        fi
    done
    
    cd "${_pwd_save}"
    
    unset _pwd_save
    
    [ ${_found_in_parents} -eq 1 ]
}


lssitepackages()
{
    
    virtualenv_sh_verify_workon_home || return 1
    virtualenv_sh_verify_active_virtualenv || return 1
    
    ls "$@" "$(virtualenv_sh_site_packages_path)"
}


lsvirtualenvs()
{
    
    virtualenv_sh_virtualenvs
}


mkvirtualenv()
{
    
    virtualenv_sh_verify_workon_home || return 1
    
    eval "_mkvirtualenv_env_name=\$$#"
    
    # If the last argument is an option, assume we're not actually making a
    # virtualenv.
    if [ ${_mkvirtualenv_env_name#-} != ${_mkvirtualenv_env_name} ]; then
        _mkvirtualenv_env_name=
    fi
    
    
    if [ -n "${_mkvirtualenv_env_name}" ]; then
        virtualenv_sh_run_hook "premkvirtualenv" "${_mkvirtualenv_env_name}"
    fi
    
    ( cd ${WORKON_HOME}
      virtualenv "$@" 
    ) || return 1
    
    if [ -n "${_mkvirtualenv_env_name}" ]; then
        virtualenv_sh_run_hook "postmkvirtualenv" "${_mkvirtualenv_env_name}"
    
        workon ${_mkvirtualenv_env_name}
    fi
    
    unset _mkvirtualenv_env_name
}


rmvirtualenv()
{
    
    virtualenv_sh_verify_workon_home || return 1
    
    
    if [ -z "${1:-}" ]; then
        echo "Please specify an enviroment." >&2
        return 1
    else
        _rmvirtualenv_env_name="$1"
    fi
    
    _rmvirtualenv_env_dir="${WORKON_HOME}/${_rmvirtualenv_env_name}"
    
    if [ "${VIRTUAL_ENV}" = "$_rmvirtualenv_env_dir" ] && ! deactivate; then
        echo "ERROR: unable to deactivate ${_rmvirtualenv_env_name}"
        return 1
    fi
    
    virtualenv_sh_run_hook "prermvirtualenv" "${_rmvirtualenv_env_name}"
    
    rm -rf "${_rmvirtualenv_env_dir}"
    
    virtualenv_sh_run_hook "postrmvirtualenv" "${_rmvirtualenv_env_name}"
    
    
    unset _rmvirtualenv_env_name
    unset _rmvirtualenv_env_dir
}


virtualenv_sh_add_hook()
{
    
    # Adds a function to be executed for a particular hook. If it's already in the
    # list, this has no effect.
    #
    # $1 is the hook name
    # $2 is the function name
    
    for item in ${_virtualenv_sh_hook_functions:-}; do
        if [ "$item" = "$1/$2" ]; then
            return 0
        fi
    done
    
    _virtualenv_sh_hook_functions="${_virtualenv_sh_hook_functions:-} $1/$2"
}


virtualenv_sh_init()
{
    
    if [ -z "${WORKON_HOME}" ]; then
        WORKON_HOME="${HOME}/.virtualenvs"
    fi
    
    if [ -e "${WORKON_HOME}" ] && [ ! -d "${WORKON_HOME}" ]; then
        echo "ERROR: ${WORKON_HOME} exists but is not a directory."
        return 1
    fi
    
    _virtualenv_sh_hook_functions=
    
    if [ ! -e "${WORKON_HOME}" ]; then
        echo "Creating ${WORKON_HOME}" >&2
        mkdir "${WORKON_HOME}" || return 2
    
        for hook in initialize \
                    premkvirtualenv postmkvirtualenv \
                    prermvirtualenv postrmvirtualenv \
                    preactivate postactivate \
                    predeactivate postdeactivate; do
            echo "#!/bin/sh" > "${WORKON_HOME}"/${hook}    
        done
    
        #for hook in preactivate postactivate predeactivate postdeactivate; do
        #    echo "echo \"echo local \\\"\\\$@\\\"\" > \${WORKON_HOME}/\$2/bin/$hook" >> "${WORKON_HOME}"/postmkvirtualenv
        #done
    fi
    
    virtualenv_sh_init_features
    
    virtualenv_sh_run_hook "initialize"
}


virtualenv_sh_init_features()
{
    
    complete -o default -o nospace -F _virtualenv_sh_complete_virtualenvs workon
    complete -o default -o nospace -F _virtualenv_sh_complete_virtualenvs rmvirtualenv
    complete -o nospace -F _virtualenv_sh_complete_cdvirtualenv -S/ cdvirtualenv
    complete -o nospace -F _virtualenv_sh_complete_sitepackages -S/ cdsitepackages
}


virtualenv_sh_remove_hook()
{
    
    # The inverse of virtualenv_sh_add_hook: removes all occurances of a given hook
    # function from our list (there should be at most one).
    #
    # $1 is the hook name
    # $2 is the function name
    
    _virtualenv_sh_hook_functions=$(
        for item in ${_virtualenv_sh_hook_functions:-}; do
            if [ ! "$item" = "$1/$2" ]; then
                printf " %s" "$item"
            fi
        done
    )
}


virtualenv_sh_restore_options()
{
    
    if [ -r /tmp/virtualenv_sh_saved_options ]; then
        . /tmp/virtualenv_sh_saved_options 2>/dev/null
        rm /tmp/virtualenv_sh_saved_options
    fi
}


virtualenv_sh_run_global_hook()
{
    
    # $1 is the hook name
    
    if [ -n "${WORKON_HOME}" ] && [ -r "${WORKON_HOME}/$1" ]; then
        . "${WORKON_HOME}/$1"
    fi
}


virtualenv_sh_run_hook()
{
    
    # $1 is the hook name
    # $2 (optional) is the environment name
    
    if [ ${2:-} ]; then
        _run_hook_env_name=$2
    elif [ ${VIRTUAL_ENV:-} ]; then
        _run_hook_env_name="${VIRTUAL_ENV##*/}"
    else
        _run_hook_env_name=
    fi
    
    
    # Internal hook implementations
    case $1 in
        postdeactivate) unset _virtualenv_sh_auto_virtualenv;;
    esac
    
    
    # External hook scripts
    case $1 in
        initialize|premkvirtualenv|postmkvirtualenv|prermvirtualenv|postrmvirtualenv)
            virtualenv_sh_run_global_hook $1 ${_run_hook_env_name};;
    
        preactivate|postactivate)
            virtualenv_sh_run_global_hook $1 ${_run_hook_env_name}
            virtualenv_sh_run_local_hook $1 ${_run_hook_env_name};;
    
        predeactivate|postdeactivate)
            virtualenv_sh_run_local_hook $1 ${_run_hook_env_name}
            virtualenv_sh_run_global_hook $1 ${_run_hook_env_name};;
    esac
    
    
    # Registered hook functions
    virtualenv_sh_run_hook_functions $1 ${_run_hook_env_name}
    
    
    unset _run_hook_env_name
}


virtualenv_sh_run_hook_functions()
{
    
    # Runs all registered hook functions for a given hook name.
    
    for item in ${_virtualenv_sh_hook_functions:-}; do
        if [ "${item%%/*}" = "$1" ]; then
            eval "${item#*/}"
        fi
    done
}


virtualenv_sh_run_local_hook()
{
    
    # $1 is the hook name
    # $2 is the env name
    
    _run_local_hook_env_path="${WORKON_HOME}/$2"
    
    if [ -n "$_run_local_hook_env_path" ] && [ -r "$_run_local_hook_env_path/bin/$1" ]; then
        . "$_run_local_hook_env_path/bin/$1"
    fi
    
    
    unset _run_local_hook_env_path
}


virtualenv_sh_save_options()
{
    
    set +o >| /tmp/virtualenv_sh_saved_options
}


virtualenv_sh_site_packages_path()
{
    
    virtualenv_sh_verify_active_virtualenv || return 1
    
    # There should only be one directory in lib, named after the python version.
    for p in "$VIRTUAL_ENV"/lib/*/site-packages; do
        echo $p
        break
    done
}


virtualenv_sh_verify_active_virtualenv()
{
    
    if [ -z "${VIRTUAL_ENV}" ] || [ ! -d "${VIRTUAL_ENV}" ]; then
        echo "ERROR: no virtualenv active, or active virtualenv is missing" >&2
        return 1
    fi
}


virtualenv_sh_verify_workon_home()
{
    
    if [ -z "$WORKON_HOME" ] || [ ! -d "$WORKON_HOME" ]; then
        echo "ERROR: WORKON_HOME not set or does not exist" >&2
        return 1
    fi
}


virtualenv_sh_virtualenvs()
{
    
    for item in ${WORKON_HOME}/*; do
        if [ -r "${item}/bin/activate" ]; then
            echo ${item##*/}
        fi
    done
}


workon()
{
    
    virtualenv_sh_verify_workon_home || return 1
    
    if [ -z "${1:-}" ]; then
        lsvirtualenvs
        return 1
    fi
    
    _activate="$WORKON_HOME/$1/bin/activate"
    if [ ! -f "$_activate" ]; then
        echo "ERROR: '$WORKON_HOME/$1' is not a virtualenv." >&2
        return 1
    fi
    
    if type deactivate >/dev/null 2>&1; then
        deactivate
    fi
    
    virtualenv_sh_run_hook "preactivate" "$1"
    
    # virtualenv's scripts choke on nounset
    virtualenv_sh_save_options && set +o nounset
    . "$_activate"
    virtualenv_sh_restore_options
    
    # Save the deactivate function from virtualenv under a different name
    _virtualenv_sh_original_deactivate=`typeset -f deactivate | sed 's/deactivate/virtualenv_deactivate/g'`
    eval "$_virtualenv_sh_original_deactivate"
    unset -f deactivate >/dev/null 2>&1
    
    # Replace the deactivate() function with a wrapper.
    eval 'deactivate () {
        old_env=${VIRTUAL_ENV##*/}
        
        # Call the local hook before the global so we can undo
        # any settings made by the local postactivate first.
        virtualenv_sh_run_hook "predeactivate" "${old_env}"
        
        # Call the original function.
        virtualenv_sh_save_options && set +o nounset
        virtualenv_deactivate "$@"
        virtualenv_sh_restore_options
    
        virtualenv_sh_run_hook "postdeactivate" "${old_env}"
    
        if [ ! "${1:-}" = "nondestructive" ]; then
            # Remove this function
            unset -f virtualenv_deactivate >/dev/null 2>&1
            unset -f deactivate >/dev/null 2>&1
        fi
    }'
    
    virtualenv_sh_run_hook "postactivate"
}


virtualenv_sh_init
