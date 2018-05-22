import java.text.SimpleDateFormat
import groovy.time.TimeCategory

Calendar cal = Calendar.getInstance()
cal.add(Calendar.DATE, -1)
def sdf = new SimpleDateFormat("yyyy-MM-dd")
def dateString = sdf.format(cal.getTime())
sdf = new SimpleDateFormat("HH_mm_ss")
def timeString = sdf.format(cal.getTime())

def reportWs = "/proj/mtk06979/temp"
def outDirPattern = "outDir"
def outDir = "${reportWs}/${outDirPattern}"
def outHtmlPattern = "out-html"
def outHtmlDir = "${outDir}/${outHtmlPattern}"
def gerritStats = "/proj/mtk06979/gerritstats"
def afterDate = params.AfterDate
def afterDate4Gerrit = params.AfterDateForGerrit
def anaJson = "wits_new_my_todo.json"
def anaFilteredJson = "wits_new_my_todo_f.json"
def logCleanInterval = params.CleanInterval

node("mtksdals15"){
    stage("clean_outdate_artifact"){
        def dir = new File("/var/www/my_todo_statistic")
        dir.listFiles().each { f ->
            try{
                echo f.name
                def temp = TimeCategory.minus(new Date(), Date.parse("yyyy-MM-dd", f.name))
                if ( temp.days >= logCleanInterval.toInteger() ){
                    println "${f}: ${temp}"
                    sh "rm -rf ${f.path}"
                }
            } catch(Exception e){
                println e
            }
        
        }
    }
    
}


node("mytodo_report_slave"){
    ws(reportWs){
            
        stage("update codebase"){
            git branch: 'dev', url: 'ssh://mtksgt04:29419/wits/new_my_todo'
        }

        withEnv(['PATH+ENVS=/mtkoss/jdk/1.8.0_25/bin/:/mtkoss/python/odb/nodejs/v8.9.0-linux-x64/bin/:/mtkoss/python/odb/venv_mytodo_ubuntu1404-3.6.2_ssl_x64/bin/']) {
            stage("clean_build"){
                sh "rm -rf ${outDir} "
            }
            
            stage("update_gerrit_data"){
                sh "${gerritStats}/gerrit_downloader.sh --after-date ${afterDate4Gerrit} --server mtksgt04 --project wits/new_my_todo --output-dir ${outDir}"
                
                sh "python report/report_filter.py ${outDir}/${anaJson} ${outDir}/${anaFilteredJson}"
            }
            
            stage("analyze_data"){
                sh "mkdir -p ${outHtmlDir} && ${gerritStats}/gerrit_stats.sh -f ${outDir}/${anaFilteredJson} --branches dev -o ${outHtmlDir}"
            }
        }

        stage("counting_loc"){
            withEnv(['PATH+ENVS=/mtkoss/python/odb/virtual_runtime_ubuntu1204_x86/bin']) {
                sh "mkdir -p ${outHtmlDir} && gitinspector --timeline -m -x json -x lib -F html --grading --since ${afterDate} -H >${outHtmlDir}/loc.html"
            }
        }
        
        stage("archieve"){
            sh "mv ${outHtmlDir}/index.html ${outHtmlDir}/changes.html"

            archiveArtifacts artifacts: "${outDirPattern}/${outHtmlPattern}/**/*", fingerprint: true
        }
    }

}



node("mtksdals15"){
    
    def targetPath = "/proj/srv_rdscadm/cash/mytodo_report/${dateString}/${timeString}"
    sh "mkdir -p ${targetPath}"
    
    step([$class: 'CopyArtifact', fingerprintArtifacts: true, 
        projectName: "${env.JOB_NAME}", selector: [$class: 'SpecificBuildSelector', 
        buildNumber: "${currentBuild.number}"], 
        target: "${targetPath}"])
}