import java.text.SimpleDateFormat
import java.util.TimeZone

def codebase = '/proj/srv_rdscadm/cash/my_to_do_ws'
def pythonBin = '/mtkoss/python/odb/venv_mytodo_ubuntu1404-3.6.2_ssl_x64/bin'
def nodeBin = '/mtkoss/python/odb/nodejs/v8.9.0-linux-x64/bin'

def proxy = "http://172.23.29.23:3128"
def constLatest = "latest"


// use timestamp no more
/*
SimpleDateFormat sdf = new SimpleDateFormat("yyyy_MM_dd_HH_mm_ss")
sdf.setTimeZone(TimeZone.getTimeZone("GMT+08:00"))
def currentTime = sdf.format(new Date())
*/
// update for every release, like maven
def tagName = "20180402-rc2"
def currentBranch = "master"
def vscServer = "ssh://mtk06979@mtksgt04:29419/wits/new_my_todo"

// mbj registry
def registry = "172.27.16.100:5000/" 

properties([
            [$class: 'RebuildSettings', autoRebuild: false, rebuildDisabled: false], 
            buildDiscarder(logRotator(artifactDaysToKeepStr: '20', artifactNumToKeepStr: '20', daysToKeepStr: '20', numToKeepStr: '20')),
            parameters([
                booleanParam(defaultValue: false, description: 'Clean full codebase', name: 'CleanWS'),
                // booleanParam(defaultValue: false, description: 'Clean intermediate files while building', name: 'CleanUntracked'),
                booleanParam(defaultValue: false, description: "Clean historical static files. (Warnning: Don't clean this if the production is version-mixing)", name: 'CleanStatic'),
                booleanParam(defaultValue: true, description: 'Build for production', name: 'IsProd'),
                booleanParam(defaultValue: false, description: 'Check to force building docker images', name: 'BuildDocker'),
                booleanParam(defaultValue: false, description: 'Check to force building frontend', name: 'BuildFrontend'),
                booleanParam(defaultValue: false, description: 'Check to force building HAProxy', name: 'BuildHAProxy'),
                booleanParam(defaultValue: false, description: 'Check to force building backend', name: 'BuildBackend'),
                booleanParam(defaultValue: false, description: 'Check to force backend Testing', name: 'TestBackend'),
                stringParam(defaultValue: "${tagName}", description: 'Speficy the docker tag', name: 'TagName'),
                stringParam(defaultValue: "${currentBranch}", description: 'Speficy the remote branch', name: 'VCSBranch'),
                stringParam(defaultValue: "${vscServer}", description: 'Speficy the remote server', name: 'VCSServer')
            ]), 
            pipelineTriggers([])
])

def djangoEnv = ((params.IsProd)? "my_to_do.settings_prod" : "my_to_do.settings_dev")

def buildFrontend = params.BuildFrontend || params.CleanWS || params.CleanStatic
def packageFrontend = buildFrontend 
def buildBackend = params.BuildBackend
def buildHa = params.BuildHAProxy
def buildDocker = params.BuildDocker || buildFrontend || buildBackend || buildHa
def packageBackend = buildBackend
def testBackend = params.TestBackend || buildBackend
def testResult = "test_result_${BUILD_NUMBER}.xml"
 
node('my_to_do_internet_label'){
    ws(codebase){

        stage('clean_artifact'){
            // if (params.CleanUntracked) {
            //         sh 'git clean -f -d -X '
            // }
            if (params.CleanStatic){
                sh 'rm -rf ./config/nginx/static'    
            }
            if (params.CleanWS){
                cleanWs()
            } else {
            	sh 'git status ' 
            }
        }

        stage('sync_source'){
            git branch: "${currentBranch}", url: "${vscServer}"
            // sh 'git config remote.origin.url http://mtk06979@mtksgt04:8080/gerrit/a/wits/mytodo'
            // sh 'git fetch --tags --progress http://mtk06979@mtksgt04:8080/gerrit/a/wits/mytodo +refs/heads/*:refs/remotes/origin/*'
            // sh 'git checkout -B dev origin/dev'
        }

        stage('check_change'){
            buildFrontend = buildFrontend || isBuildFrontend()
            echo "we are going to ${(buildFrontend)? "build frontend " : " skip building frontend"}"
            
            packageFrontend = buildFrontend
            echo "we are going to ${(packageFrontend)? "pack frontend" : " skip packing frontend"}"

            buildBackend = buildBackend || isBuildBackend()
            echo "we are going to ${(buildBackend)? "build backend " : " skip building backend"}"
            
            packageBackend = buildBackend
            echo "we are going to ${(packageBackend)? "pack backend" : " skip packing backend"}"
            
            buildHa = buildHa || isBuildHaProxyDockerImage()
            echo "we are going to ${(buildHa)? "build HAProxy" : " skip building HA"}"

            buildDocker = buildDocker || buildHa || buildBackend || buildFrontend || isBuildNginxDockerImage()
            echo "we are going to ${(buildDocker)? "build docker " : " skip building docker"}"
            
            testBackend = testBackend || buildBackend
            echo "we are going to ${(testBackend)? "test backend" : " skip backend testing"}"
        }
    }
}

node('python_admin_label'){
    withEnv(["PATH+PYENV=${pythonBin}"]) {
        stage('prepare_python_env'){
            sh "which pip && pip --proxy ${proxy} install -r ${codebase}/requirements.txt"
        }
    }
}

node('my_to_do_internet_label'){
    ws(codebase){
        withEnv(["PATH+PYENV=${pythonBin}", "PATH+NODEENV=${nodeBin}"]) {
            stage('install_frontend') {
                if (buildFrontend){   
                    sh 'which npm && fab install_frontend'
                } else {
                    echo "no frontend related changed, skip install..."
                }
            }
        }
    }
}

node('my_to_do_bulid_label') {
    
    withEnv(["PATH+PYENV=${pythonBin}", "PATH+NODEENV=${nodeBin}", 
    		"DJANGO_SETTINGS_MODULE=${djangoEnv}", 
    		"ORACLE_HOME=/proj/srv_rdscadm/cash/instantclient_12_2",
    		"LD_LIBRARY_PATH=/proj/srv_rdscadm/cash/instantclient_12_2:${LD_LIBRARY_PATH}"]) {
        ws(codebase){
            stage('build_frontend') {
                if (buildFrontend){
                    sh 'fab build_frontend'
                } else {
                    echo "no frontend related changed, skip build..."
                }
            }

            stage('collect_django_rc') {
            	if (packageFrontend){ 
                	sh 'fab run_django_collect_static'
                } else {
                	echo "skip collecting static" 
                }
            }

            stage('archive'){
                if (packageBackend || packageFrontend){
                	archiveArtifacts allowEmptyArchive: true, 
                                artifacts: '**/*.py, config/**/*, requirements.txt, Jenkinsfile, docker-compose.yml, **/Dockerfile, .dockerignore, .gitignore', 
                                excludes: '**/node_modules/,**/__pycache__/,**/*.pyc', 
                                fingerprint: true, onlyIfSuccessful: true
                } else {
                	echo "skip archive becuase no changes" 
                }
                
            }
        }
    }

}

stage('build_docker_iamge'){
    if (buildDocker){
        //nodes = getNdoes('my_to_do_prod_label')
        //for (n in nodes){
            //node(n){
        node('my_to_do_prod_label'){ 
            echo "build docker images on to ${env.NODE_NAME}" 
            def projName = "mytodo${((params.IsProd)? "prod":"dev")}"              
            withEnv(["PATH+PYENV=${pythonBin}", "DJANGO_SETTINGS_MODULE=${djangoEnv}"]) {
                sh "cd ${codebase} && pwd && docker-compose -p ${projName}  build "

                if ( buildFrontend || isBuildNginxDockerImage() ){
                    sh "docker tag ${projName}_nginx1:${constLatest} ${registry}${projName}_nginx1:${tagName}"
                    sh "docker push ${registry}${projName}_nginx1:${tagName}"
                }

                if (buildBackend){
                    sh "docker tag ${projName}_app1:${constLatest} ${registry}${projName}_app1:${tagName}"
                    sh "docker push ${registry}${projName}_app1:${tagName}"
                }

                if (buildHa){
                    sh "docker tag ${projName}_haproxy1:${constLatest} ${registry}${projName}_haproxy1:${tagName}"
                    sh "docker push ${registry}${projName}_haproxy1:${tagName}"
                }
            }
        }
//            }
//        }
                    
    } else {
        echo "no Docker related changed, skip build..."
    }
}



node('my_to_do_prod_label'){
    def test_ws = "/tmp/my_todo_test"
    // test ap in docker image
    ws(test_ws){
        def testoutput = ""
        if (testBackend){
	        stage('run_backend_testing') {
	        	sh "rm -rf *" // link the jenkins workspace with docker's : -v test_report:/mytodo/test_report
	            //
	            // test in other jobs for testlink report generation which didn't support pipeline yet
	            // 
	            def testJob = build job: 'GenTestLinkReport', parameters: [string(name: 'tagName', value: "${tagName}"), string(name: 'registry', value: "${registry}")], quietPeriod: 0, propagate: false
	            def jobResult = testJob.getResult()
	            if (testJob.result != 'SUCCESS'){
	            	echo "fail on tests, please check the report: ${testJob.absoluteUrl}" 
	            }
	            // aggregate the report to current pipeline test interface
	            copyArtifacts filter: '*.xml', fingerprintArtifacts: true, projectName: 'GenTestLinkReport', selector: specific("${testJob.number}")
	            // // --boxed is only for linux client which is the production env.
	            // sh  script: "docker run -v ${test_ws}:/mytodo/test_report --rm ${registry}mytodoprod_app1:${tagName} fab run_django_test:boxed='True'", returnStatus: true
	            
	        }
	
	        stage('gen_test_report'){
	            try{
	                junit allowEmptyResults: true, keepLongStdio: true, testResults: "**/*.xml"
	            } catch(Exception e){
	                echo e
	            }
	        }
	
	        stage('archieve_report'){
	            archiveArtifacts artifacts: '**/*', fingerprint: true
	        }
        }
    }
}



def isBuildFrontend(){
    return checkChange(['frontend/', "my_to_do/templates"], 'frontend-related')
}

def isBuildNginxDockerImage(){
    return checkChange(['config/nginx'], 'static file related')
}

def isBuildHaProxyDockerImage(){
    return checkChange(['config/haproxy'], 'ha proxy related')
}

def isBuildBackend(){
    return checkChange(['.py', "my_to_do/templates", 'requirements.txt'], 'backend related')
}

def checkChange(dataArray, msg) {
    def dockerPrefix = ['config/nginx', 'config/haproxy']
    for (changesets in currentBuild.changeSets){// usually only one loop
        for (changeset in changesets){ // loop the list
            for (p in changeset.getPaths()){
                for (prefix in dataArray){
                    if (p.getPath().contains(prefix)){
                        echo "${changeset.getCommitId()}: detect ${p.getPath()} with ${msg} pattern[${prefix}]"
                        return true
                    }
                }
            }
        }
    }
    return false
}

@NonCPS
def getNdoes(label){
    def labelObj = Jenkins.instance.getLabel("${label}")
    return labelObj.nodes.collect { node -> node.name }
}
