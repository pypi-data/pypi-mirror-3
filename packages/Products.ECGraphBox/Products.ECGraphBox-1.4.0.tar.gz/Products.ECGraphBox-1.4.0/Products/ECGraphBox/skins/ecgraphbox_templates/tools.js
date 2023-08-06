/**
 * 
 */


//#########################################################################
//Tools Begin
//#########################################################################	

//-------------------------------------------------------------------------
//Toolprototype Begin
//-------------------------------------------------------------------------
function Tool(){
	
	this.useOnClick = function(x, y, key){
	};	
	
	this.useOnDblClick = function(x, y, key){
	};	
	
	this.useOnMouseDown = function(x, y, key){
	};	
	
	this.useOnDrag = function(x, y, dx, dy, key){
	};
	
	this.useOnMouseUp = function(x, y, key){
	};
	
	this.useOnScrol = function(x, y, key){
	};

	this.useOnKeyDown = function(key){
	};
	
	this.useOnKeyUp = function(key){
	};
}

//-------------------------------------------------------------------------
//Toolprototype End
//-------------------------------------------------------------------------

//-------------------------------------------------------------------------
//DeleteTool Begin
//-------------------------------------------------------------------------
	DeleteTool = function(name){
		this.name = name;
	};
	DeleteTool.prototype = new Tool();
	DeleteTool.prototype.constructor = DeleteTool;
	
	DeleteTool.prototype.useOnKeyDown = function(key){
		if(key == 46 && !textFieldHasFocus){
			writeToProtocol();
			graph.removeKnotsBySelection();
			graph.removeEdgesBySelection();
		}
	};
//-------------------------------------------------------------------------
//DeleteTool End
//-------------------------------------------------------------------------

	
//-------------------------------------------------------------------------
//MultiTool Begin
//-------------------------------------------------------------------------
	MultiTool = function(name){
		this.name = name;
		var currentTool = SELECT;
	};
	MultiTool.prototype = new Tool();
	MultiTool.prototype.constructor = MultiTool;
	
	MultiTool.prototype.useOnDblClick = function(x, y, key){
		writeToProtocol();
		graph.addKnotByPosition(x, y);		
	};
	
	MultiTool.prototype.useOnMouseDown = function(x, y, key){	
		var knot = graph.getKnotIndexByPoint(x, y);
		if(knot == -1){
			switch(key){
				case -1: 
					currentTool = SELECT;
					toolBundle.tools[SELECT].useOnMouseDown(x, y, key);	
					break;
				case 16: 
					currentTool = SELECT_PLUS;
					toolBundle.tools[SELECT_PLUS].useOnMouseDown(x, y, key);		
					break;
				case 17: 
					currentTool = SELECT_MINUS;
					toolBundle.tools[SELECT_MINUS].useOnMouseDown(x, y, key);	
					break;
			} 
		} else{
			switch(key){
				case -1: 
					currentTool = DRAG;
					toolBundle.tools[DRAG].useOnMouseDown(x, y, key);	
					break;
				case 13: 
					break;
				case 16: 
					currentTool = MOVE;
					toolBundle.tools[MOVE].useOnMouseDown(x, y, key);	
					break;
				case 17: 
					currentTool = ADD_EDGE;
					toolBundle.tools[ADD_EDGE].useOnMouseDown(x, y, key);
					break;
			} 
		}
	};
	
	MultiTool.prototype.useOnDrag = function(x, y, dx, dy, key){
		toolBundle.tools[currentTool].useOnDrag(x, y, dx, dy, key);	
	};
	
	MultiTool.prototype.useOnMouseUp = function(x, y, key){
		toolBundle.tools[currentTool].useOnMouseUp(x, y, key);
	};
//-------------------------------------------------------------------------
//MultiTool End
//-------------------------------------------------------------------------



//-------------------------------------------------------------------------
//DragTool Begin
//-------------------------------------------------------------------------
	DragTool = function(name){
		this.name = name;
		var hasMoved = false;
	};
	DragTool.prototype = new Tool();
	DragTool.prototype.constructor = DragTool;
	
	DragTool.prototype.useOnMouseDown = function(x, y, key){
		graph.deselectAll();	
		
		if(!dragSelected && graph.selectKnotByPoint(x, y) > -1){
			textfield_knotName.value = graph.getKnotIndexByPoint(x,y);
			dragSelected = true;
		}			
		
		switch(key){
			case 16:  // shift key pressed
				graph.selectEdgeByPoint(x, y);
				graph.selectKnotByPoint(x, y);
				break;
			case 17:  // ctrl key pressed
				graph.deselectEdgeByPoint(x, y);
				graph.deselectKnotByPoint(x, y);
				break;
		}
		
		graph.selectKnotByPoint(x, y);
		graph.selectEdgeByPoint(x, y);	
	};
	
	DragTool.prototype.useOnDrag = function(x, y, dx, dy, key){
		if(!hasMoved){
			writeToProtocol(); 
			hasMoved = true;
		}
		graph.translateKnotsBySelection(dx, dy);
	};
	
	DragTool.prototype.useOnMouseUp = function(x, y, key){
		dragSelected = false;
		hasMoved = false;
	};
//-------------------------------------------------------------------------
//DragTool End
//-------------------------------------------------------------------------


//-------------------------------------------------------------------------
//MoveTool Begin
//-------------------------------------------------------------------------
	MoveTool = function(name){
		this.name = name;
	};
	MoveTool.prototype = new Tool();
	MoveTool.prototype.constructor = MoveTool;
	
	MoveTool.prototype.useOnMouseDown = function(x, y, key){
		graph.selectEdgeByPoint(x, y);
		graph.selectKnotByPoint(x, y);		
	};
	
	MoveTool.prototype.useOnDrag = function(x, y, dx, dy, key){
		graph.translateKnotsBySelection(dx, dy);		
	};
	
	MoveTool.prototype.useOnMouseUp = function(x, y, key){
		writeToProtocol(); 
	};
//-------------------------------------------------------------------------
//MoveTool End
//-------------------------------------------------------------------------



//-------------------------------------------------------------------------
//SelectTools Begin
//-------------------------------------------------------------------------
	SelectTool = function(name){
		this.name = name;
	};
	SelectTool.prototype = new Tool();
	SelectTool.prototype.constructor = SelectTool;
	
	SelectTool.prototype.useOnMouseDown = function(x, y, key){
		selectRect.xs = x + 0.5;
		selectRect.ys = y + 0.5; 
		selectRect.xe = x + 0.5;
		selectRect.ye = y + 0.5;
		selectRect.isActiv = true;	
		
		graph.deselectAll();			
		//graph.selectEdgeByPoint(x, y);		
	};
	
	SelectTool.prototype.useOnDrag = function(x, y, dx, dy, key){
		selectRect.xe += dx;
		selectRect.ye += dy;
	};
	
	SelectTool.prototype.useOnMouseUp = function(x, y, key){
		selectRect.isActiv = false;
		graph.deselectAll();
		graph.selectKnotByPoint(x, y);
		graph.selectKnotByRect(selectRect.xs, selectRect.xe, selectRect.ys, selectRect.ye);
		graph.selectEdgeByRect(selectRect.xs, selectRect.xe, selectRect.ys, selectRect.ye);
		graph.selectEdgeByPoint(x, y);
	};
//-------------------------------------------------------------------------
//SelectTools End
//-------------------------------------------------------------------------



//-------------------------------------------------------------------------
//SelectPlusTool Begin
//-------------------------------------------------------------------------
	SelectPlusTool = function(name){
		this.name = name;
	};
	SelectPlusTool.prototype = new Tool();
	SelectPlusTool.prototype.constructor = SelectPlusTool;
	
	SelectPlusTool.prototype.useOnMouseDown = function(x, y, key){	
		selectRect.xs = x + 0.5;
		selectRect.ys = y + 0.5; 
		selectRect.xe = x + 0.5;
		selectRect.ye = y + 0.5;
		selectRect.isActiv = true;

		graph.selectKnotByPoint(x, y);	
		graph.selectEdgeByPoint(x, y);	
	};
	
	SelectPlusTool.prototype.useOnDrag = function(x, y, dx, dy, key){
		selectRect.xe += dx;
		selectRect.ye += dy;
	};
	
	SelectPlusTool.prototype.useOnMouseUp = function(x, y, key){
		selectRect.isActiv = false;
		graph.selectEdgeByPoint(x, y);	
		graph.selectKnotByRect(selectRect.xs, selectRect.xe, selectRect.ys, selectRect.ye);	
	};
//-------------------------------------------------------------------------
//SelectPlusTool End
//-------------------------------------------------------------------------



//-------------------------------------------------------------------------
//SelectMinusTool Begin
//-------------------------------------------------------------------------
	SelectMinusTool = function(name){
		this.name = name;
	};
	SelectMinusTool.prototype = new Tool();
	SelectMinusTool.prototype.constructor = SelectMinusTool;
	
	SelectMinusTool.prototype.useOnMouseDown = function(x, y, key){	
		selectRect.xs = x + 0.5;
		selectRect.ys = y + 0.5; 
		selectRect.xe = x + 0.5;
		selectRect.ye = y + 0.5;
		selectRect.isActiv = true;

		graph.deselectKnotByPoint(x, y);	
		graph.deselectEdgeByPoint(x, y);
	};
	
	SelectMinusTool.prototype.useOnDrag = function(x, y, dx, dy, key){
		selectRect.xe += dx;
		selectRect.ye += dy;
	};
	
	SelectMinusTool.prototype.useOnMouseUp = function(x, y, key){
		selectRect.isActiv = false;
		graph.deselectKnotByRect(selectRect.xs, selectRect.xe, selectRect.ys, selectRect.ye);	
	};
//-------------------------------------------------------------------------
//SelectPlusTool End
//-------------------------------------------------------------------------



//-------------------------------------------------------------------------
//AddKnotTool Begin
//-------------------------------------------------------------------------
	AddKnotTool = function(name){
		this.name = name;
	};
	AddKnotTool.prototype = new Tool();
	AddKnotTool.prototype.constructor = AddKnotTool;
	
	AddKnotTool.prototype.useOnMouseDown = function(x, y, key){	
		writeToProtocol();
		graph.addKnotByPosition(x, y);	
	};
//-------------------------------------------------------------------------
//AddKnotTool End
//-------------------------------------------------------------------------


//-------------------------------------------------------------------------
//AddEdgeTool Begin
//-------------------------------------------------------------------------
	AddEdgeTool = function(name){
		this.name = name;
	};
	AddEdgeTool.prototype = new Tool();
	AddEdgeTool.prototype.constructor = AddEdgeTool;
	
	AddEdgeTool.prototype.useOnMouseDown = function(x, y, key){	
		if(!graph.isEmpty()){
			graph.deselectAllKnots();
			
			edgeDragger.startKnot.name = graph.getKnotIndexByPoint(x, y); 
			if(edgeDragger.startKnot.name > -1){
				var startKnot = graph.getKnotByIndex(edgeDragger.startKnot.name);
				edgeDragger.setStart(startKnot.x, startKnot.y);
				edgeDragger.setEnd(startKnot.x, startKnot.y);
				edgeDragger.isActiv = true;
			} 
		}
	};
	
	AddEdgeTool.prototype.useOnDrag = function(x, y, dx, dy, key){
		if(edgeDragger.isActiv){
			edgeDragger.setEnd(x,y);
			edgeDragger.endKnot.name = graph.getKnotIndexByPoint(x, y);
				
			if(edgeDragger.hasValidTarget() == 1){
				edgeDragger.setTarget(graph.getKnotByIndex(edgeDragger.endKnot.name));					
			} 
		}
	};
	
	AddEdgeTool.prototype.useOnMouseUp = function(x, y, key){	
		if(edgeDragger.endKnot.name > -1 && edgeDragger.startKnot.name > -1){
			writeToProtocol();
			graph.addEdgeByToIndices(edgeDragger.startKnot.name, edgeDragger.endKnot.name);
			
		}
		edgeDragger.isActiv = false;
		edgeDragger.startKnot.name = -1;
		edgeDragger.endKnot.name = -1;
	};
//-------------------------------------------------------------------------
//AddEdgeTool End
//-------------------------------------------------------------------------

	
// writeToProtocol pushs the GraphML-representation of the current graph to the protocol-stack
function writeToProtocol(){
	protocolPred.push(graph.toString());
	protocolSucc = new Array;
	protocolpresent = true;
}

// protPred makes the last changes undone 
// changes that are made undone are saved on the succesor-stack 
function protPred(){	
	if(protocolPred.length > 0){
		var gxml = protocolPred.pop();
		var gxmlDoc;		
		gxmlDoc = loadXMLString(gxml);
		
		protocolSucc.push(graph.toString()); // memorys the steps that allready done, that is to be undone
		makeGraph(gxmlDoc);
		graph.setDirected(graphIsDirected);
		graph.setWeighted(graphIsWeighted);
		update();
	}	
}

// protSucc redos a already done change that was undone
// the current state of the graph is saved on the predessor-stack
function protSucc(){
	if(protocolSucc.length > 0){
		var gxml = protocolSucc.pop();
		var gxmlDoc;
		gxmlDoc = loadXMLString(gxml);
		
		protocolPred.push(graph.toString());	
		makeGraph(gxmlDoc);
		graph.setDirected(graphIsDirected);
		graph.setWeighted(graphIsWeighted);
		update();
	}	
}

// remove removes all selectet elements of the graph
function remove(){
	update();
}

// change the graphs attribute "directed" 
function changeDirected(){
	graph.setDirected(!graph.isDirected());
	update();
}

//change the graphs attribute "weighted" 
function changeWeighted(){
	graph.setWeighted(!graph.isWeighted());
	update();
}

//#########################################################################
//Tools End
//#########################################################################	

//#########################################################################
//Toolhandling Begin
//#########################################################################	

//changeTool changes the tool interactive by pressing ctr, shift and depending on the the mouses position (on a knot or edge or on plane areas)
function changeTool(x, y){
	if(!locked){
		var knot = graph.getKnotIndexByPoint(x, y);
		if(knot == -1){
			changeToolByName(2, false);
		} else{
			switch(key){
				case -1: 
					changeToolByName(4, false);
					break;
				case 13: 
					writeToProtocol();
					graph.changeKnotNameBySelection(textfield.value);
					break;
				case 16: 
					changeToolByName(MOVE, false);
					break;
				case 17: 
					changeToolByName(1, false);
					break;
			} 
		}
	}
}

// changeToolByName changes the current tool
function changeToolByName(t, lock){
	locked = lock;
	switch (t){
		case 0:
			tool = t;
			break;
			
		case 1:
			tool = t;
			graph.deselectAll();
			break;
			
		case 2:
			tool = t;
			break;
			
		case 3:
			tool = t;
			break;
			
		case 4:
			tool = t;
			break;
			
		case 6:
			tool = t;
			break;
			
		case 7:
			tool = t;
			writeToProtocol();
			graph.changeKnotNameBySelection(textfield.value);
			break;
			
		case 9:
			tool = t;
			break;
			
		case 10:
			tool = t;
			break;
		case 11:
			tool = t;
			break;
	}
	update();	
}
//#########################################################################
//Toolhandling end
//#########################################################################	
