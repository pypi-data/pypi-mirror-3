
export PKGNAME=rhaptos2.repo
export BUILD_TAG=t1
export WORKSPACE=/tmp/cnx

export bamboo_code_root=/home/pbrian/cnx/$PKGNAME
export bamboo_stage_root=$WORKSPACE/stage/$PKGNAME
export bamboo_archive_root=$WORKSPACE/archive
export bamboo_venvpath=$WORKSPACE/venv/$BUILD_TAG
export bamboo_xunitfilepath=$WORKSPACE/nosetests.xml

export bamboo_remote_build_root=/home/deployagent/
export bamboo_deployagent_keypath=/home/pbrian/.ssh/deployagent
export bamboo_deployagent=deployagent
export bamboo_www_server_root=/usr/share/www/nginx/www
export bamboo_logserverfqdn=log.frozone.mikadosoftware.com
export bamboo_logserverport=5147

export bamboo_modusdir=/home/pbrian/cnx/bamboo.recipies/recipies/
export bamboo_install_to=www.frozone.mikadosoftware.com::www.frozone.mikadosoftware.com
export bamboo_confdir=/tmp/confdir

export rhaptos2_repodir=/tmp/repo

export rhaptos2_statsd_host=log.frozone.mikadosoftware.com
export rhaptos2_statsd_port=8125
export rhaptos2_www_server_name=www.frozone.mikadosoftware.com
export rhaptos2_cdn_server_name=www.frozone.mikadosoftware.com

export rhaptos2_use_logging=Y
export rhaptos2_loglevel=DEBUG


#bamboo_runonjenkins=N (only relevant uif Y - so below only needed if y.
#bamboo_jenkinsurl=jenkins.frozone.mikadosoftware.com:8080
#bamboo_jenkinsjob=
#bamboo_artifactstoredir=


