#!/usr/bin/env bash
main() {
  VERSION="2.1.3"
  # Use colors, but only if connected to a terminal, and that terminal
  # supports them.
  if which tput >/dev/null 2>&1; then
      ncolors=$(tput colors)
  fi
  if [ -t 1 ] && [ -n "$ncolors" ] && [ "$ncolors" -ge 8 ]; then
    RED="$(tput setaf 1)"
    GREEN="$(tput setaf 2)"
    YELLOW="$(tput setaf 3)"
    BLUE="$(tput setaf 4)"
    BOLD="$(tput bold)"
    NORMAL="$(tput sgr0)"
  else
    RED=""
    GREEN=""
    YELLOW=""
    BLUE=""
    BOLD=""
    NORMAL=""
  fi

  # Only enable exit-on-error after the non-critical colorization stuff,
  # which may fail on systems lacking tput or terminfo
  set -e

  if [ ! -n "$COBRA" ]; then
    COBRA=/usr/local/bin/cobra
  fi

  if [ -d "$COBRA" ]; then
    printf "${YELLOW}You already have Cobra installed.${NORMAL}\n"
    printf "You'll need to remove $COBRA if you want to re-install.\n"
    exit
  fi

  # Prevent the cloned repository from having insecure permissions. Failing to do
  # so causes compinit() calls to fail with "command not found: compdef" errors
  # for users with insecure umasks (e.g., "002", allowing group writability). Note
  # that this will be ignored under Cygwin by default, as Windows ACLs take
  # precedence over umasks except for filesystems mounted with option "noacl".
  umask g-w,o-w

  printf "${BLUE}Cloning Cobra...${NORMAL}\n"
  hash git >/dev/null 2>&1 || {
    echo "Error: git is not installed"
    exit 1
  }
  # The Windows (MSYS) Git is not compatible with normal use on cygwin
  if [ "$OSTYPE" = cygwin ]; then
    if git --version | grep msysgit > /dev/null; then
      echo "Error: Windows/MSYS Git is not supported on Cygwin"
      echo "Error: Make sure the Cygwin git package is installed and is first on the path"
      exit 1
    fi
  fi
  env git clone --depth=1 -b beta https://github.com/wufeifei/cobra.git $COBRA || {
    printf "Error: git clone of Cobra repo failed\n"
    exit 1
  }


  printf "${BLUE}Looking for an existing Cobra config...${NORMAL}\n"
  if [ -f ~/.cobrarc ] || [ -h ~/.cobrarc ]; then
    printf "${YELLOW}Found ~/.cobrarc.${NORMAL} ${GREEN}Backing up to ~/.cobrarc.backup${NORMAL}\n";
    mv ~/.cobrarc ~/.cobrarc.backup;
  fi

  printf "${BLUE}Using the Cobra template file and adding it to ~/.cobrarc${NORMAL}\n"
  cp $COBRA/cobrarc.template ~/.cobrarc
  # Set COBRA path
  sed "/^export COBRA=/ c\\
  export COBRA=$COBRA
  " ~/.cobrarc > ~/.cobrarc-temp
  mv -f ~/.cobrarc-temp ~/.cobrarc
  # Symbolic link
  ln -sf $COBRA/cobra.py /usr/loca/bin/cobra

  printf "${GREEN}"
  echo 'Successful installation! :-D'
  echo ',---.     |              '
  echo '|    ,---.|---.,---.,---.'
  echo '|    |   ||   ||    ,---|'
  echo '`---``---``---``    `---^  v'$VERSION
  echo ''
  echo ' Config file: ~/.cobrarc'
  echo ' GitHub Page: https://github.com/wufeifei/cobra'
  echo ' Documents  : https://cobra-docs.readthedocs.io'
  echo ' Usage      : cobra --help'
  printf "${NORMAL}"
}

main