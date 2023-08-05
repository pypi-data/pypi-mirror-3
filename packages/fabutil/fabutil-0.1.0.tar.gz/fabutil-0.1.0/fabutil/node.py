from fabric.tasks import task
from fabric.api import run, cd, sudo
from fabric.contrib import files

@task
def install_npm():
    # TODO: depend on curl
    # TODO: do error checking
    sudo("curl http://npmjs.org/install.sh | sh")

@task
def install_nave():
    if files.exists("~/.nave"):
        return
    run("mkdir ~/.nave")
    with cd("~/.nave"):
        run("wget http://github.com/isaacs/nave/raw/master/nave.sh")
        run("chmod 755 nave.sh")

@task
def nave(cmd):
    # TODO: check if nave is installed
    run("~/.nave/nave.sh %s" % cmd)

@task
def install_node():
    # TODO: depend on build-essentials and openssl
    #nave("install stable")
    #nave("usemain stable")

    # for squeeze:
    sudo("echo deb http://ftp.us.debian.org/debian/ sid main > /etc/apt/sources.list.d/sid.list")
    sudo("apt-get update")
    sudo("apt-get -y install nodejs nodejs-dev")
