function tagging_add_tag(btn, tagging_url, target_id) {
    jQuery.post(tagging_url+'/add',
                jQuery(btn).parents('.tagging_tags_block').find('.tagging_add_tag_form form').serialize(),
                function() {jQuery(btn).parents('.tagging_tags_block').load(tagging_url+'/tags/'+target_id)}
    );
    return false;
}

function tagging_delete_tag(btn, tagging_url, target_id, tag_name) {
    if (confirm('Do you really want to delete this tag?')) {
        jQuery.post(tagging_url+'/remove',
                    {target_id:target_id, tags:tag_name},
                    function() {jQuery(btn).parents('.tagging_tags_block').load(tagging_url+'/tags/'+target_id)}
        );
    }
    return false;
} 
