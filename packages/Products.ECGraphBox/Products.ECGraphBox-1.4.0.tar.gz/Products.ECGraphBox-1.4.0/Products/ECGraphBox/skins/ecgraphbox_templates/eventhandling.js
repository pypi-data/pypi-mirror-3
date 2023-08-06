/**
 * 
 */
var originX = 0;
var originY = 0;
var focusX = 0;
var focusY = 0;
var scale = 1;
//#########################################################################
// Buttonevents Begin
//#########################################################################



//#########################################################################
// Buttonevents End
//#########################################################################


//#########################################################################
// Keyboardhandling Begin
//#########################################################################
var key = -1;
var isTyping = false;

function keyDown(e){
	key = e.keyCode;
	output = key; 

	toolBundle.tools[tool].useOnKeyDown(key);
	toolBundle.omnipresentToolsUseOnKeyDown(key);	
	
	//Copy and Paste in progress
	/*
	if(key == 67){
		var graphML = graph.selectionToString();
		clipBoard.save(graphML);
	}
	if(key == 86){
		var graphML = clipBoard.getData();
		//output = graphML;
		graph.insert(graphML);
	}
	*/
	update();
}

function keyUp(e){
	key = -1;
	
	//output = key; //for debug

	toolBundle.tools[tool].useOnKeyUp(key);
	toolBundle.omnipresentToolsUseOnKeyUp(key);	
	update();
}
//#########################################################################
// Keyboardhandling End
//#########################################################################



//#########################################################################
// Mousehandling Begin
//#########################################################################

function onMouseDown(x, y){	
	focusX = x;
	focusY = y;
	toolBundle.tools[tool].useOnMouseDown(x, y, key);	
	toolBundle.omnipresentToolsUseOnMouseDown(x, y, key);	
	update();
}

function onDrag(x, y, dx, dy, e){
//	var zoom = 1 + 0.2 * dx/50;
//	if(e.ctrlKey && key == 32){
//		ctx.translate(0,0);
//		ctx.scale(zoom, zoom);	
//		scale = scale * zoom;
//		ctx.translate( -( focusX / scale - focusX / ( scale * zoom)), -( focusY / scale - focusY / ( scale * zoom)));
//		originX = (focusX / scale + originX - focusX / ( scale * zoom ));
//	    originY = ( focusY / scale + originY - focusY / ( scale * zoom ) );
//
//
//	} else if(key == 32){
//		
//	} else {
		toolBundle.tools[tool].useOnDrag(x, y, dx, dy, key);
		toolBundle.omnipresentToolsUseOnDrag(x, y, dx, dy, key);	
//	}
	update();	
}

function onDblClick(x, y){
	toolBundle.tools[tool].useOnDblClick(x, y, key);	
	toolBundle.omnipresentToolsUseOnClick(x, y, key);	
	update();
}

function onMouseMove(x, y, dx, dy){
	//alert("huhu");
}


function onMouseUp(x, y){
	toolBundle.tools[tool].useOnMouseUp(x, y, key);
	toolBundle.omnipresentToolsUseOnMouseUp(x, y, key);
	update();	
}

//#########################################################################
// Mousehandling End
//#########################################################################