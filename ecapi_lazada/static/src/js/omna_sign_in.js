odoo.define('omna.SignIn', function (require) {
    "use strict";

    var session = require('web.session');

    var OmnaSingIn =  {
         start: function(){
               if(session.user_context.omna_get_access_token_code){
                 return $.ajax({
                            url: session.user_context.omna_get_access_token_url,
                            dataType: 'json',
                            type: 'POST',
                            data: JSON.stringify({'code': session.user_context.omna_get_access_token_code}),
                            contentType: 'application/json',
                            success: function(r){
                                $.ajax({
                                        url: '/omna/get_access_token',
                                        dataType: 'json',
                                        type: 'POST',
                                        data: JSON.stringify({'jsonrpc': "2.0", 'params': { 'default_tenant': r['data']}}),
                                        contentType: 'application/json',
                                        success: function(r){
                                            if(r.result){
                                                window.location.reload();
                                            }
                                        }
                              })
                            },
                            error: function(e){
                              $.ajax({
                                        url: '/omna/get_access_token',
                                        dataType: 'json',
                                        type: 'POST',
                                        data: JSON.stringify({'jsonrpc': "2.0", 'params': { }}),
                                        contentType: 'application/json',
                                        success: function(r){
                                            window.location.reload();
                                        }
                              })
                            }
                  })
              }else{
                    return false
              }
         }
    }

    OmnaSingIn.start();

    return {
        omna_sign_in: OmnaSingIn
    }

});
