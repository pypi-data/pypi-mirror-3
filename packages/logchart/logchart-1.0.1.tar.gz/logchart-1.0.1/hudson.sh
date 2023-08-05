#!/bin/bash -x
# Husdon job to build logchart monitoring on different jobs
HERE=$(cd $(dirname $0); pwd -P)
JOBS=${JOBS:-""}
FORCE=${FORCE:-}
LOGCHART_OPTS=${LOGCHART_OPTS:-}

for job in $JOBS; do
    cd $HERE/../../../$job/builds || continue
    for build in `find . -type d -maxdepth 1 -mindepth 1`; do
        [ -z $FORCE ] && [ -e $build/archive/trunk/monitor ] && continue
        [ ! -e $build/archive/trunk/tomcat/log ] && [ ! -e $build/archive/trunk/jboss/log ] && [ ! -e $build/archive/trunk/jetty/log ] && continue
        mkdir $build/archive/trunk/monitor
        [ -e $build/archive/trunk/tomcat/log ] && $HERE/logchart/logchart.py $LOGCHART_OPTS $build/archive/trunk/tomcat/log/ $build/archive/trunk/monitor/
        [ -e $build/archive/trunk/jboss/log ] && $HERE/logchart/logchart.py $LOGCHART_OPTS $build/archive/trunk/jboss/log/ $build/archive/trunk/monitor/
        [ -e $build/archive/trunk/jetty/log ] && $HERE/logchart/logchart.py $LOGCHART_OPTS $build/archive/trunk/jetty/log/ $build/archive/trunk/monitor/ --device='sda '
	[ -e $build/archive/trunk/report/bench-results-*.xml ] && ( 
	    benchbase import --rmdatabase -d /tmp/bb/bb.db -j $build/archive/trunk/report/bench-results-*.xml &&
	    benchbase addsar -d /tmp/bb/bb.db --host chipolata  1  $build/archive/trunk/tomcat/log/sysstat-sar.log.gz &&
	    benchbase report -d /tmp/bb/bb.db 1 -o $build/archive/trunk/report/benchbase)
        index=$build/archive/report-index.html
        reports=`(cd $build/archive;  find . -mindepth 2 -name '*.html' -or -name '*.txt')`
        cat > $index <<EOF
<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head><title>Report index</title><link rel="stylesheet" href="http://funkload.nuxeo.org/funkload.css" type="text/css" /></head>
<body><div class="section"><h1>Report index $job build $build</h1>
<ul>
EOF
        for report in $reports; do
            echo "<li><a href="$report">$report</a></li>" >> $index
        done
        echo "</ul></body></html>" >> $index
	find $build/archive/ -name 'funkload.xml' -exec gzip -f {} \;
	find $build/archive/ -name '*.log' -exec gzip -f {} \;
    done
done
