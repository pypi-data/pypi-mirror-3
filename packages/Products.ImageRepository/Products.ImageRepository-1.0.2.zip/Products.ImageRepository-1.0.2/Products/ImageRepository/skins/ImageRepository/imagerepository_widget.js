var ImageRepositoryWidget = function() {

function CustomImageLibraryDrawer(tool, xsluri, libsuri, searchuri, baseelement, selecturi) {
    this.drawertitle = "Select Image";
    this.drawertype = "link";

    if (tool) {
        this.init(tool, xsluri, libsuri, searchuri, baseelement, selecturi);
    }

    this.createContent = function() {
        ImageLibraryDrawer.prototype.createContent.call(this);
    };

    // called by onLoad within document sent by server
    this.finishUpload = function(url) {
    };

    this.save = function() {
        this.editor.resumeEditing();
        /* create an image in the iframe according to collected data
           from the drawer */
        var selxpath = '//resource[@selected]';
        var selnode = this.xmldata.selectSingleNode(selxpath);

        if (selnode) {
            console.log(selnode);
            var uid = selnode.attributes.getNamedItem('id').nodeValue;
            var preview = this.xmldata.selectSingleNode(selxpath+'/preview');
            console.log(preview);
            if (preview) {
                preview = preview.textContent;
            }
            ImageRepositoryWidget.setImage(this.fieldName, uid, preview);
        }
        this.drawertool.closeDrawer();
    };

    this.setPosition = function(elem){
        var drawernode = document.getElementById('kupu-librarydrawer');

        var elem_top=0, elem_left=0;
        var parent = elem;
        while (parent) {
            if (parent.offsetTop)
                elem_top += parent.offsetTop;
            if (parent.offsetLeft)
                elem_left += parent.offsetLeft;
            parent = parent.offsetParent;
        }
        drawernode.style.left = '' + elem_left + 'px';
        drawernode.style.top = '' + elem_top + 'px';
    };
};
CustomImageLibraryDrawer.prototype = new ImageLibraryDrawer;
CustomImageLibraryDrawer.prototype.shared = {}; // Shared data

return {
    fakeEditor: function() {
        this.getBrowserName = function() {
            if (_SARISSA_IS_MOZ) {
                return "Mozilla";
            } else if (_SARISSA_IS_IE) {
                return "IE";
            } else {
                throw "Browser not supported!";
            }
        };
        this.suspendEditing = function () {};
        this.resumeEditing = function () {};
        this.getSelection = function() {};
        this.getSelectedNode = function() {};
        this.getNearestParentOfType = function() {};
        this.busy = function() {}
        this.notbusy = function() {}
    },

    clearImage: function(fieldname) {
        var field = document.getElementById(fieldname);
        if (!field.value) return
        
        field.value = '';
        
        // Hide the original image and preview
        var imageDiv = document.getElementById(fieldname + '_image');
        var preview = document.getElementById(fieldname + '_preview');
        imageDiv.style.display = 'none';
        preview.style.display = 'none';
        // switch 'Clear' and 'Keep' buttons
        var keepbutton = document.getElementById(fieldname + '_keepbutton');
        var clearbutton = document.getElementById(fieldname + '_clearbutton');
        var field_orig = document.getElementById(fieldname + '_orig');
        if (field_orig.value)
            keepbutton.style.display = 'inline';
        clearbutton.style.display = 'none';
    },
    
    keepImage: function(fieldname) {
        var field = document.getElementById(fieldname);
        var field_orig = document.getElementById(fieldname + '_orig');
        if (!field_orig.value) return;
        
        field.value = field_orig.value;
        // Show the original image, hide the preview
        var imageDiv = document.getElementById(fieldname + '_image');
        var preview = document.getElementById(fieldname + '_preview');
        imageDiv.style.display = 'block';
        preview.style.display = 'none';
        // switch 'Clear' and 'Keep' buttons
        var keepbutton = document.getElementById(fieldname + '_keepbutton');
        var clearbutton = document.getElementById(fieldname + '_clearbutton');
        keepbutton.style.display = 'none';
        clearbutton.style.display = 'inline';        
    },
    
    setImage: function(fieldname, uid, previewurl) {
        var field = document.getElementById(fieldname);
        field.value = uid;
        
        // enable 'Clear' and 'Keep' buttons
        var origfield = document.getElementById(fieldname + '_orig');
        if (origfield.value) {
            var keepbutton = document.getElementById(fieldname + '_keepbutton');
            keepbutton.style.display = 'inline';
        }
        var clearbutton = document.getElementById(fieldname + '_clearbutton');
        if (clearbutton)
            clearbutton.style.display = 'inline';
        
        // Set the preview image
        var imageDiv = document.getElementById(fieldname + '_image');
        imageDiv.style.display = 'none'
        var preview = document.getElementById(fieldname + '_preview');
        if (previewurl) {
            preview.src = previewurl;
        } else {
            preview.src = portal_url + '/reference_catalog/lookupObject?uuid=' + field.value;
        }
        preview.style.display = 'block'
    },

    openPicker: function(elem, fieldName, portal_url) {
        // window.open(portal_url + '/imagerepositorywidget_popup?fieldName=' + 
        //                          escape(fieldName),
        //             'imagerepository_popup',
        //             'toolbar=no,location=no,status=no,menubar=no,' +
        //             'scrollbars=yes,resizable=yes,width=500,height=550');
        var drawertool = ImageRepositoryWidget.drawertool;
        if (drawertool.current_drawer) {
            drawertool.closeDrawer();
        };
        var drawer = drawertool.drawers['imagelibdrawer'];
        drawer.createContent();
        drawer.setPosition(elem);
        drawer.fieldName = fieldName;
        drawertool.current_drawer = drawer;
    },
    
    init: function() {
        var editor = new ImageRepositoryWidget.fakeEditor();
        var drawertool = new DrawerTool();
        drawertool.initialize(editor);
        var conf = loadDictFromXML(document, 'imagerepositorywidgetconfig');
        var imagetool = new ImageTool();
        var imagelibdrawer = new CustomImageLibraryDrawer(imagetool,
                                                    conf.xsl_uri,
                                                    conf.lib_prefix,
                                                    conf.search_prefix);
        drawertool.registerDrawer('imagelibdrawer', imagelibdrawer);
        ImageRepositoryWidget.drawertool = drawertool;
    }
}}();

registerPloneFunction(ImageRepositoryWidget.init);