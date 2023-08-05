# Some project vars and functions

DEPLOY_DIR={{ deploy_dir }}
SOURCE_DIR={{ source_dir }}
STATIC_DIR={{ static_dir }}
SERVICE_DIR={{ service_dir }}

SITE_USER={{ site_user }}
SITE_GROUP={{ site_group }}

MODE={{ mode }}
TEMPLATE={{ template }}
DOMAIN={{ domain }}
PORT={{ port }}
PROJECT={{ project }}
BRANCH={{ branch }}
SRC={{ src }}


check_program () {
    program=$1
    shift
    message=$@
    which $program 1>/dev/null || {
        echo "Error: Command '$program' not found!" 1>&2
        echo "$message" 1>&2
        exit 127
    }
}

cmd () {
    CMD=$1
    echo "Run: $CMD"
    eval "$CMD"
    return "$?"
}

cmd_or_die () {
    CMD=$1
    cmd "$CMD" || exit 1
}
