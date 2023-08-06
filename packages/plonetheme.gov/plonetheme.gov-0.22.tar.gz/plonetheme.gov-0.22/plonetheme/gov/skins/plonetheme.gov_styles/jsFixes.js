GovJSFixes = {};

GovJSFixes.fixCaptions = function ()
{
	var leadimage = jq(".newsImageContainer a img");
	var width = leadimage.width();
	jq(".newsImageContainer p").css({'max-width' : width});
};

GovJSFixes.runFixes = function ()
{
	//Add new fixes to this list to activate them
	GovJSFixes.fixCaptions();
};


GovJSFixes.runSpecialFixes = function ()
{
	//Add new fixes to this list to activate them and ONLY RUN WHEN THE FULL PAGE IS LOADED
};

//run all the fixes when the DOM is completely loaded and the special ones when everything is loaded;
jq(window).load(function () {GovJSFixes.runSpecialFixes();});
jq(document).ready(function () {GovJSFixes.runFixes();}); 
