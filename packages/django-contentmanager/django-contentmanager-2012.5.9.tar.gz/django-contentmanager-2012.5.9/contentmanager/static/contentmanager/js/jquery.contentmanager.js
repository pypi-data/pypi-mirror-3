// closure
(function($) {

    // private vars (within the closure)

    // opts contains the callbacks for close, submit and load
    var opts;

    // The id of the block for which the content is (being) updated
    var targetBlock = null;

    //
    // plugin definition
    //
    $.fn.contentmanager = function(options){
        // build main options before element iteration
        opts = $.extend({}, $.fn.contentmanager.defaults, options);
        // iterate and reformat each matched element
        return this.each(function(){
            $('.cmsblockcontrols').fadeTo('fast', '.3');
            $('.cmsblock').hover(
                function(){
                    $(this).children('.cmsblockcontrols').fadeTo('fast', '1');
                },
                function(){
                    $(this).children('.cmsblockcontrols').fadeTo('fast','.3');
                });
            if($('#cmsdialog').length===0){
                var markup = '<div id="cmsdialog" title="Content Manager"></div>';
                $(document.body).append(markup);
                $('#cmsdialog').dialog({
                    modal: true,
                    close: function(e, o){
                        close();
                    },
                    position: ['',30],
                    width: opts.dialogwidth,
                    height: opts.dialogheight, 
                    resizable: true, 
                    autoOpen: false
                });
                load();
            }
        });
    };

    // Default width and height for the editor
    $.fn.contentmanager.defaults = {
	onload: [],
	onsubmit: [],
	onclose: [],
        dialogwidth: "80%",
        dialogheight: $(window).height()*0.9
    };

    $.fn.contentmanager.registerCallback = function(event, callback){
	//opts['on'+event].push(callback);
	switch(event){
	case 'load':
	opts['onload'].push(callback);
	break;
	case 'close':
	opts['onclose'].push(callback);
	break;
	case 'submit':
	opts['onsubmit'].push(callback);
	break;
	}
    }

    //
    // private function for debugging
    //
    function debug(msg) {
        if(window.console && window.console.log){
            window.console.log(msg);
        }
    };
    
    // This is called before the dialog is closed and will call any
    // callbacks that are passed via options
    function close(){
        //debug('close called');
        if(opts.onclose){
            for(c in opts.onclose){
                opts.onclose[c]();
            }
        }
    };

    // This is called before a form (other than the listblocks-form)
    // is submitted
    function submit(){
        //debug('submit called');
        if(opts.onsubmit){
            for(c in opts.onsubmit){
                opts.onsubmit[c]();
            }
        }
    }

    function load(data, status){
        //debug('load called');
        if(status==='error'){
            $('#cmsdialog').html(data);
            return false;
        }
        installHooks();
        if(opts.onload){
            for(c in opts.onload){
                opts.onload[c]();
            }
        }
    }

    function installHooks(){
        $('.move-down, .move-up').siblings('a')
            .unbind('click')
            .click(function(ev){
                $(ev.target).siblings('input:image').click();
                return false;
                });
        $('a.cmurl').unbind('click').click(function(ev){
            targetBlock =  $(this).parents('.cmsblock').attr('id');
            if(ev.target.nodeName.toLowerCase()=='img'){
                var url = $(ev.target).parent()[0].href;
            } else {
                var url = ev.target.href;
            }
            $('#cmsdialog').load(url, null, load).dialog('open');
            return false;
        });
        $('#cmsdialog a.cmcancel').unbind('click').click(function(ev){
            $('#cmsdialog').dialog('close').html('');
            return false;
        });
        
        // HTTP POST's
        $('#cmsdialog .cmedit').submit(function(ev){
            submit();
        }).ajaxForm({
            error: function(xhr, textStatus, errorThrown){
                //debug('error');
                $('#cmsdialog').html(xhr.responseText);
            },
            complete: function(xhr, status){
                close();
                // The form has errors
                if(xhr.getResponseHeader('X-Contentmanager') === 'showpluginform'){
                    $('#cmsdialog').html(xhr.responseText);
                    load();
                    // Show the form again...
                    $('#cmsdialog').show();
                } else {
                    // An empty responseText means a succesful
                    // INSERT => refresh the page...
                    if(xhr.responseText===''){
                        document.location.reload(true);
                    } else {
                        // An UPDATE: Show the updated html
                        $('#'+targetBlock).html(xhr.responseText);
                        $('#cmsdialog').html('');
                        $('#cmsdialog').dialog('close');
                        load();
                    }
                }
            }
        });
    };
})(jQuery);
