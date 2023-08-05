/* Configuration substantially based on the configuration from Tiks:
 * http://svn.tiks.org/svn/repos/Tiks/trunk/src/tiks/widgets/fckeditor/browser/tiks_fckconfig.js
 * by Roger Ineichen (dev@projekt01.ch)
 */

FCKConfig.BasePath = '/@@/fckeditor/editor/';
FCKConfig.EditorAreaCSS = FCKConfig.BasePath + 'css/fck_editorarea.css' ;
FCKConfig.CustomConfigurationsPath = "/@@/zope_fckconfig.js";

FCKConfig.ToolbarSets["zope"] = [
  ['Source','DocProps'],
  ['Cut','Copy','Paste','PasteText','PasteWord','-'],
  ['SelectAll','RemoveFormat'],
  ['Bold','Italic','Underline','StrikeThrough','-','Subscript','Superscript'],
  ['OrderedList','UnorderedList','-','Outdent','Indent'],
  ['JustifyLeft','JustifyCenter','JustifyRight','JustifyFull'],
  ['Image','Link','Unlink','Anchor','Table','Rule'],
  '/',
  ['Style','FontFormat','FontName','FontSize'],
  ['TextColor','BGColor'],
  ['About']
  ];

// set faked table borders on table wth border="0"
FCKConfig.ShowBorders	= true ;

// The contextURL is set in the javescipt template and used in the explorer implementation
FCKConfig.contextURL = window.top.top.contextURL;

FCKConfig.LinkBrowser = false ;
FCKConfig.LinkBrowserURL = window.top.top.explorerURL;
FCKConfig.LinkBrowserWindowWidth	= 650 ;	// 40%
FCKConfig.LinkBrowserWindowHeight	= 440 ;	// 40%

FCKConfig.ImageBrowser = false ;
FCKConfig.ImageBrowserURL = window.top.top.explorerURL;
FCKConfig.ImageBrowserWindowWidth  = 650 ;	// 40% ;
FCKConfig.ImageBrowserWindowHeight = 440 ;	// 40% ;

// change this views if you need to load a different file explorer tree
// This way you can load different explorers for different widget since
// you can load different configuration scripts for each widget.
// See tiks.skintools.explorer for more info
FCKConfig.treeview = '@@explorer_tree';
FCKConfig.insertview = '@@explorer_insert';
