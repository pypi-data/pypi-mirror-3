(function($) {

    $(function() {
        $("#image-reference-popup,#file-reference-popup")
            .css({'display':'none'});

        $("#image-reference-controls dt").click(function() {
            load_reference_popup("image-reference-popup",'../@@sa_reference_popup','Image');
            return false;
        });

        $("#file-reference-controls dt").click(function() {
            load_reference_popup("file-reference-popup",'../@@sa_reference_popup','File');
            return false;
        });

    });

    function load_reference_popup(node,url,type) {
        $("#kss-spinner").show();

        $("#" + node)
            .load(url + "?type=" + type + " #ajax-content",'',
                function(response,status,xmlhttprequest) {
                    if(status=='success') {
                        type_lower = type.toLowerCase();
                        $("#"+type_lower+"-reference-popup a").click(function() {
                            browse_url = $(this).attr('href');
                            load_reference_popup(node,browse_url+"/@@sa_reference_popup",type);
                            return false;
                        });
                        $(".referenceableLink a").click(function() {
                            $("#kss-spinner").show();
                            uid = $(this).attr('title');
                            jq.post('./@@sa_add_reference',{uid:uid,
                                                            dom_id:type_lower+'-controls',
                                                            viewlet_manager:'simpleattachment.'+type_lower+'controls',
                                                            viewlet_name:'simpleattachment.'+type_lower+'listing'},
                                    function(listing_code) {
                                        $("#"+type.toLowerCase()+"-controls").replaceWith(listing_code);
                                        $("#kss-spinner").hide();
                                    });
                            return false;
                        });
                    }
                })
            .show("slow");

        $("#kss-spinner").hide();
    }

})(jQuery);
