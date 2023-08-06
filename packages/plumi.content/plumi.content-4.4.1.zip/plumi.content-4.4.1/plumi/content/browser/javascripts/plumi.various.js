jq(document).ready(function(){
  jq('#plumivideo-base-edit').submit(function(){            
    jq('form#plumivideo-base-edit').find('#video_file_file').each(function() {
        if (!jq('#video_file_nochange').is(":checked")) {
            var loading_html = '<p>Please be patient while your file is uploading. It may take a long time. Thanks.</p> <img src="ajax-loader.gif"/>';
            jq('#video_file_file').after(loading_html);
            alert("You are about to start uploading. Please be patient, as this may take some time. Don't close your browser or click 'Save' again. Thanks!");
        }
        
    });
  });
        
  jq('#toggleBookmarks').click(function() {
    if (jq('#toggledBookmarks').is(":hidden"))
   {
                jq('#toggledBookmarks').fadeIn("slow");
    } else {
           jq('#toggledBookmarks').fadeOut("slow");
   }
  });

});
