    
// const setting
def proxy = "http://172.23.29.23:3128"
def userHome = "/proj/mtk06979"

def greenLabel = 'my_todo_green_deploy_label'
def blueLabel = 'my_todo_blue_deploy_label'
def staticLabel = 'my_todo_static_deploy_label'
def haLabel = 'my_todo_ha_deploy_label'

def haInstance = [
    "${greenLabel}": ["${userHome}/my_todo_ap_green_deploy", "${userHome}/my_todo_ap_green_deploy_backup"],
    "${blueLabel}": ["${userHome}/my_todo_ap_blue_deploy", "${userHome}/my_todo_ap_blue_deploy_backup"]
]

def haDeploy = "${userHome}/my_todo_ha_deploy"
def staticDeploy = "${userHome}/my_todo_static_deploy"

def pythonBin = '/mtkoss/python/odb/venv_mytodo_ubuntu1404-3.6.2_ssl_x64/bin'
def CI_DAEMON = "JENKINS_NODE_COOKIE=leaveMeAloneFuckOff" 

// parameters 
def djangoEnv = ((params.IsProd)? "my_to_do.settings_prod" : "my_to_do.settings_dev")
def deployType = params.deployType
def isBlueGreen = params.isBlueGreen
def upstreamJob = params.UpstreamJob
def upstreamBuildNumber = params.UpstreamBuildNumber
def upstreamBranch = params.upstreamBranch
def totalNodes = []
def mode = ((params.IsProd)? "prod":"dev")

timestamps{

    def labels = []

    if (deployType == "WEBAP") {
        // stat -f -L -c %T remotedir
        labels = (isBlueGreen)? [greenLabel] : [greenLabel, blueLabel]
        stage("system_info"){
            echo getSysInfo(labels)
        }
        for (label in labels){
            
            def backupPath = haInstance.get("${label}")[1]
            def apPath = haInstance.get("${label}")[0]

            def subNodes = getNdoes("${label}")

            node(label){
                stage("fetching_artifact"){
                    def backupResult = sh returnStatus: true, script: """#!/bin/bash
                rm -rf ${backupPath} && mkdir -p ${apPath} &&  mv ${apPath} ${backupPath} && mkdir -p ${apPath}"""                
                    if (backupResult){
                        echo "Fail to backup application..."
                    }
                    step([$class: 'CopyArtifact', fingerprintArtifacts: true, projectName: "${upstreamJob}/${upstreamBranch}", 
                        selector: [$class: 'SpecificBuildSelector', buildNumber: "${upstreamBuildNumber}"], target: "${apPath}"])
                }
            }

            for (todoNodes in subNodes){
                node(todoNodes){
                    def machine = sh returnStdout: true, script: "hostname"
                    def fullPath = "${apPath}_${machine}"
                    withEnv(["PATH+PYENV=${pythonBin}", "DJANGO_SETTINGS_MODULE=${djangoEnv}"]) {
                        ws(fullPath){
                            stage("stop_ap_${machine}"){
                                echo "stop AP on ${machine}"
                                def fabExists = fileExists './fabfile.py'
                                if (fabExists){
                                        echo "Stop applicatoin on ${machine}"
                                        sh "fab stop_gunicorn"
                                    
                                } else {
                                    echo "Can't detect the fabfile existence, maybe the first deployment."
                                }
                            }

                            stage("deploy_ap_${machine}"){
                                echo "Deploy source on ${machine}"
                                cleanWs()
                                sh "cp -r ${apPath}/* ./"
                            }

                            stage("start_ap_${machine}"){
                                echo "Start applicatoin on ${machine}"
                                sh "${CI_DAEMON} fab start_gunicorn "
                            }
                        
                        }
                    }

                }
            }
        }

        // if (totalNodes.size()){
        //     def msg = "Fail to deploy on : "
        //     for (n in totalNodes){
        //         msg += "${n}, "
        //     }
        //     echo msg
        // }

    } else if (deployType == "HAPROXY") {
        def containerName = "my_todo_haproxy_${(params.IsProd)? "prod":"dev"}"
        node(haLabel){
            ws(haDeploy){                
                stage("ha_proxy_stop"){
                    def result = sh script: "docker stop ${containerName} && docker rm ${containerName}", returnStatus: true
                    if (result){
                        echo "fail to close ${containerName}, maybe because it doesn't exist."
                    }
                }
                stage("ha_proxy_start"){
                    sh "${CI_DAEMON} docker run -d --name ${containerName}  -p 80:80 -p 5566:5566 -p 5678:5678 -v /dev/log:/dev/log mytodo${mode}_haproxy1"
                }
            }
        }
        
    } else if (deployType == "STATIC_SERVER"){
        labels = [staticLabel]
        stage("system_info"){
            echo getSysInfo(labels)
        }
        def containerName = "my_todo_${mode}_nginx"
        stage("static_start"){
            for (label in labels){
                def nodes = getNdoes(label)
                for (n in nodes){
                    node(n){
                        ws(staticDeploy){
                            echo "stop frontend server on ${env.NODE_NAME}"
                            def result = sh script: "docker stop ${containerName} && docker rm ${containerName}", returnStatus: true
                            if (result){
                                echo "fail to close ${containerName}, maybe because it doesn't exist."
                            }

                            echo "start frontend server on ${env.NODE_NAME}"
                            sh "${CI_DAEMON} docker run -d --name ${containerName}  -p 8888:8888 -v /dev/log:/dev/log -v /tmp:/var/log/nginx mytodo${mode}_nginx1"
                        }
                    }
                }
            }
        }

    } else {
        print "unsupported deploy type!"
    }

}

@NonCPS
def getSysInfo(labels){
    msg = "Plan to deploy to following slaves: "
    for (label in labels){
        def nodes = getNdoes("${label}")
        for (singleNode in nodes){
            msg += "${singleNode}, "
        }
    }
    return msg
}

@NonCPS
def getNdoes(label){
    def labelObj = Jenkins.instance.getLabel("${label}")
    return labelObj.nodes.collect { node -> node.name }
}

