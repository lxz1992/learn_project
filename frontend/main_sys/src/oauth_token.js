import '../../node_modules/bootstrap/dist/css/bootstrap.min.css';
import '../../lib/font-awesome-4.7.0/css/font-awesome.min.css';
import 'jquery';
import 'bootstrap';

import cmnUtils from './util/index';
import Consts, {OAUTH_CLIENT_ID, OAUTH_REDIRECT_URI} from './constants';

const jq = jQuery.noConflict();

console.log('loading...');

jq(document).ready(function () {
    console.log('on ready...');
    let code = cmnUtils.getQueryParams('code');
    let auth = jq('#auth-code').text();
    let formBody = `code=${code}&grant_type=authorization_code&redirect_uri=${OAUTH_REDIRECT_URI}&client_id=${OAUTH_CLIENT_ID}`;

    fetch(Consts.URL_STORE.OAUTH_TOKEN, {
            method: "POST",
            body: formBody,
            headers: new Headers({
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                "Authorization": "Basic " + auth
            })
        })
        .then(cmnUtils.handleResult)
        .then((tokenInfo) => {
            console.log("successfully got token!");
            cmnUtils.setOauthToken(JSON.stringify(tokenInfo));
            window.close();
        })
        .catch((reason) => {
            alert(reason);
        });
});