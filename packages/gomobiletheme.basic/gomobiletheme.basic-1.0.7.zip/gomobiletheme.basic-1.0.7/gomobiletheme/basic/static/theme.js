/**
 * Mobile theme specific Javascript which is run on 
 */

// Declare namespace so that other JS files can override functions
mobiletheme = {};

/**
 * Load upscaled action icon images if we detect high enough screen resolution.
 * 
 * We could scale these icons at the server end, but doing pixel size scales
 * without orignal vector source yields to very bad results.
 * 
 */
mobiletheme.fixMobileImages = function() {
	
	var multiplier;
	if(window.devicePixelRatio) {
		// iPhone 4
		
		multiplier = window.devicePixelRatio;
	} else {
		multiplier = 1;
	}

        if(multiplier == 2) {
	
	    // Compensate iPhone 4's 2x reported scale with 0.5x zoom
	    // jQuery seemed to have issue manipulating meta tags
	    document.getElementById("viewport").setAttribute("content", "width=device-width; initial-scale=0.5; minimum-scale=0.5; maximum-scale=0.5; user-scalable=no;");
		
	    // Load our special stylesheet having text size fixes for iPhone 4
	    jQuery("head").append("<link>");
	    css = jQuery("head").children(":last");
	    css.attr({
	      rel:  "stylesheet",
	      type: "text/css",
	      href: "++resource++gomobiletheme.basic/iphone4.css"
	    });
	}

        var width = jQuery(window).width() * multiplier;

	if(width > 480) {
	       // Assume smartphone with resolution in 640 x 480 range
	       
	       // Bump size to 24x24 -> 48x48
	       jQuery("img").each( function() {
	       	       var src = jQuery(this).attr("src");
		       src = src.replace("++resource++gomobiletheme.basic/24/", "++resource++gomobiletheme.basic/48/");		     
	       	       jQuery(this).attr("src", src);
	       });
	}
}


/**
 * Make search box blur and focus work cool
 */
mobiletheme.prepareSearchBox = function() {
	
	var elem = $(this);
	
	var searchLabel = gomobiletheme_basic_i18n.search_field_default_text;
	
	// Use hint text only if Javascript is enabled
	elem.attr("value", searchLabel);
	
	elem.blur(function() {            	
    	elem.toggleClass("blackText");
        if (this.value == '') {
            this.value = searchLabel;
        }
    });
	
    elem.focus(function(){
        elem.toggleClass("blackText");
        if (this.value == searchLabel) {
            this.value = '';
        }
    });
    
    return elem;
};

/**
 * Pimp up all search boxes on the page
 */
mobiletheme.installSearchBox = function() {

	var searchBoxIds = []
	
	// Top search appearing effect
	$('li.action-search').click(function (e) {
        e.preventDefault();
        $("#search-box-top").slideToggle("fast");
        $("li.action-search").toggleClass("action-search-selected");
    });
    
	// Manipulate controls on enter and exit
	$("input#searchboxbottom, input#searchboxtop").each(mobiletheme.prepareSearchBox);
	
};


jQuery(document).ready(function() {
	
		if(mobiletheme.fixMobileImages()) {	
			mobiletheme.fixMobileImages();
		}

		if(mobiletheme.installSearchBox()) {	
			mobiletheme.installSearchBox();
		}
})
