//@TODO knots -> nodes
//@TODO fix remove edges
//@TODO finish copy paste
//@performance anhencment: 

//constands 
const ADD_KNOTS = 0;
const ADD_EDGE = 1;
const SELECT = 2;
const MOVE = 3;
const DRAG = 4;
const TOOGLE_SELECTION = 6;
const RENAME_KNOT = 7;
const REWEIGHT_EDGE = 8;
const SELECT_PLUS = 9;
const SELECT_MINUS = 10;
const MULTI_TOOL = 11;
const DELETE = 12;

//global objects
var ctx;
var textfield;
var graph;
var selectRect;
var edgeDragger;
var clipBoard;

//helpvariables
var viewMode = false;
var zoom = 1;


//helpvariables for tools
var tool = 11; 
var dragSelected = false; // is already a Knot selected?
var locked = false; // hotkey and speed interaction
var textFieldHasFocus = false; // is true if any textfield has the focus
var key = -1;
var protocolStep = 0;			//holds the current protocolstep
var protocolpresent = false; 	// says wether the top of the protocol represents the present graph or not
var protocolPred = new Array; 	// holds previous steps
var protocolSucc = new Array; 	// holds undone steps
var graphIsDirected = false;
var graphIsWeighted = false;

//tools
var deleteTool;
var multiTool;
var addKnotTool;
var eddEdgeTool;
var dragTool;
var moveTool;
var selectTool;
var selectPlusTool;
var selectMinusTool;

var t1;
var t2;
var toolBundle;

//debug
var output = 0;


//function to initialize globals
function init(onlyView){
	viewMode = onlyView;
	
	ctx = canvas.getContext('2d');		
	graph = new Graph(graphIsDirected, graphIsWeighted, 20, ctx);
	selectRect = new SelectRect(ctx);
	edgeDragger = new EdgeDragger(ctx);
	edgeDragger.setStart(0,0);
	edgeDragger.setEnd(1,1);
	clipBoard = new ClipBoard();
	
	//tools initialize
	toolBundle = new ToolBundle('bundle1');

	deleteTool 		= new DeleteTool(DELETE);
	multiTool 		= new MultiTool(MULTI_TOOL);
	addKnotTool 	= new AddKnotTool(ADD_KNOTS);
	addEdgeTool 	= new AddEdgeTool(ADD_EDGE);
	dragTool 		= new DragTool(DRAG);
	moveTool 		= new MoveTool(MOVE);
	selectTool 		= new SelectTool(SELECT);
	selectPlusTool 	= new SelectPlusTool(SELECT_PLUS);
	selectMinusTool = new SelectMinusTool(SELECT_MINUS);

	toolBundle.addOmnipresentTool(deleteTool);
	
	toolBundle.addTool(multiTool);
	toolBundle.addTool(addKnotTool);
	toolBundle.addTool(addEdgeTool);
	toolBundle.addTool(dragTool);
	toolBundle.addTool(moveTool);
	toolBundle.addTool(selectTool);
	toolBundle.addTool(selectPlusTool);
	toolBundle.addTool(selectMinusTool);	
	update();
}

function update(){
	if(!viewMode){
		settingVisiblitiy();
	}
	render();
}

function settingVisiblitiy(){
	nodeSettings.style.visibility = 'hidden';
	edgeSettings.style.visibility = 'hidden';	
	var k = graph.getSelectedKnotsCount();
	var e = graph.getSelectedEdgesCount();
	if(k >= 1){
		nodeSettings.style.visibility = 'visible';		
	}
	if(e >= 1){
		edgeSettings.style.visibility = 'visible';			
	} 
}

// renders the graph and everything on the canvas
function render(){
	ctx.fillStyle = '#FFF';
	ctx.fillRect(0,0,canvas.width,canvas.height);

	graph.render();
	selectRect.render();
	edgeDragger.render();
	
	ctx.lineWidth = 1;	
	ctx.strokeStyle = '#000';

	debug();
}

function zoom(s){
	zoom = s;
}

function debug(){
	//output =  clipBoard.getData();
	
	ctx.textBaseline  = 'middle';
	ctx.textAlign = 'left'; 
	ctx.font = '6pt Arial';
	ctx.fillStyle = 'rgba(0,0,0,1)';
	ctx.fillText(output, 10, 140);	
	
	ctx.beginPath();	
	ctx.moveTo(40, 60);	
	ctx.lineTo(40, 60);		
	ctx.stroke();
}


//#########################################################################
//temporarly added start
//#########################################################################


function ClipBoard(){
	var self = this;
	var storage = 'leer';
	
	//saves the data to the storage
	this.save = function(data){
		storage = data;
	}

	//returns the data from the storage
	this.getData = function(data){
		return storage;
	}
}

//#########################################################################
//temporarly added begin
//#########################################################################


//#########################################################################
// Graph begin
//#########################################################################


//-------------------------------------------------------------------------
//Knots begin
//-------------------------------------------------------------------------
function Knot(x, y, r, name, ctx){
	var self = this;	
	
	var selected = false;	// holds wether the knot is selected or not	

	var ctx = ctx; // the rendercontext in which the knot will render itself
	
	var timeStamp = new Date();
	var id = timeStamp.getTime(); //an unique Id for every knot
	var type = 'normalKnot'; // later there may be more types of knots (UML, ER, ...)
	
	this.x = x; 			//position x
	this.y = y;				//position y
	this.r = r;				//radius r
	this.name = name; 		// name of the knot is displayed as label
	this.fillColor = 'rgba(255,255,255,1)'; // color is used for the knot rendering
	
	
	
	this.getId = function(){
		return id;
	}
	
	this.getType = function(){
		return type;
	}
	
	//sets the Id of the knot
	//Attention: this method is only indented for remake knots out of a saved graph
	this.setId = function(value){
		id = value;
	}
	
	this.render = function(){
		ctx.strokeStyle = 'rgba(0,0,0,1)';	
		ctx.fillStyle = this.fillColor;
		ctx.lineWidth = 1;
		
		ctx.beginPath();
		ctx.arc(this.x, this.y, this.r, 0, 180, false);
		ctx.fill();
		ctx.stroke();
		
		ctx.textBaseline  = 'middle';
		ctx.textAlign = 'center'; 
		
		var h = 2 * this.r / this.name.length;
		if(h <= 15){
			ctx.font = h + 'pt Arial';	
			
		} else {
			ctx.font = '15pt Arial';	
			
		}	
	
		ctx.fillStyle = 'rgba(0,0,0,1)';
		ctx.fillText(this.name, this.x, this.y);
		
		if(selected){
			ctx.strokeStyle = 'rgba(0,130,226,0.6)';	
			ctx.fillStyle = 'rgba(0,120,226,0.3)';		
			ctx.lineWidth = 3;
			
			ctx.beginPath();
			ctx.arc(this.x, this.y, this.r, 0, 180, false);
			ctx.fill();
			ctx.stroke();
		}
	}
	
	//setSelected sets the property to true or false
	this.setSelected = function(value){
		selected = value;
	}
	
	this.isSelected = function(){
		return selected;
	}
}
//-------------------------------------------------------------------------
//Knots end
//-------------------------------------------------------------------------


//-------------------------------------------------------------------------
//Edges begin
//-------------------------------------------------------------------------
//"Wer Knoten kennt, der kennt auch Kanten"  <----- http://www.youtube.com/watch?v=6Q3eOUZY9Rc

function Edge(s, e,sourceKnotRadius, targetKnotRadius, weight, ctx){
	var self = this;
	
	var edgeWeightPositioning = -3; // how far from the edge shall the weight of an edge be rendered	
	var selected = false; 			// holds wether the edge is selected or not
	var directed = false; 			// holds wether the edge is directed or not
	var weighted = false;			// holds wether the edge is weight or not
	var targetKnotRadius = targetKnotRadius; // holds the radius of the target Knot (importend for right rendering of the edge)
	var sourceKnotRadius = sourceKnotRadius; // holds the radius of the target Knot (importend for right rendering of the edge)
	
	var ctx = ctx; 					// the rendercontext in which the knot will render itself
	
	this.start = s;					// holds the start knot 	Attention: it doesn't holds the index of the knot in the array!
	this.end = e;					// holds the end knot 		Attention: it doesn't holds the index of the knot in the array!
	this.weight = weight;			// holds the weight of the edge
	this.color = 'rgba(0,0,0,1)';

	var timeStamp = new Date();
	var id = timeStamp.getTime(); 	// an unique Id for all edges
	var type = 'normalEdge'; 		// there may be more types of edges later	
	 

	
	//helpvariables to represent a normal equation // BEGIN
	var normal = new Vector(e.y - s.y, s.x - e.x);		// edge normal
	normal.normalize();									// normalized normal
	var c = normal.scalarProduct1v(s);					// used to determin if the edge was hit or not
	var direction = new Vector(e.x - s.x, e.y - s.y);	// holds direction and length of the edge (later the length of the visible part of the edge)

	var d = new Vector(direction.x, direction.y);		// helper variable to shorten the direction variable to the visible part of the edge
	d.normalize();
	d.scale(sourceKnotRadius + targetKnotRadius);		// parts not visible from the edge
	direction = direction.subtract(d);					// edge shortend to the right visible length 
	
	var visibleEdgeStart = new Vector(direction.x, direction.y); // TODO: What is that?
	//helpvariables to represent a normal equation // END
	
	
	
	this.getId = function(){
		return id;
	}
	
	this.getType = function(){
		return type;
	}

	//sets the Id of the edge
	//Attention: this method is only indented for remake edges out of a saved graph
	this.setId = function(value){
		id = value;
	}	
	
	//takes true or false
	this.setDirected = function(value){
		directed = value;
	}
	
	//takes true or false
	this.setWeighted = function(value){
		weighted = value;
	}

	//takes true or false
	this.setSelected = function(value){
		selected = value;
	}
	
	this.isDirected = function(){
		return directed;
	}
	
	this.isWeighted = function(){
		return weighted;
	}
	
	this.isSelected = function(){
		return selected;
	}
	

	this.render = function(){		
		ctx.beginPath();	
		if(selected){
			ctx.strokeStyle = 'rgba(100,150,255,1)';
			ctx.fillStyle = 'rgba(100,150,255,1)';
			
		} else {
			ctx.strokeStyle = this.color;
			ctx.fillStyle = this.color;
		}
			
		//draw mainline
		ctx.moveTo(this.start.x, this.start.y);	
		ctx.lineTo(this.end.x, this.end.y);		
			
		// this calculation is only of use when the edge is directed or weighted 
		if(directed || weighted){		
			this.update(); // update the normal and direction
			
			var n = new Vector(normal.x, normal.y);
			n.normalize();
			n.scale(5);
			
			var d = new Vector(direction.x, direction.y);
			d.normalize();
			d.scale(targetKnotRadius);
		}
		

			
		if(weighted){
			ctx.textBaseline  = 'bottom';
			ctx.textAlign = 'center'; 
			ctx.font = '15pt Arial';
			
			var dx = (this.end.x - this.start.x);
			var dy = (this.end.y - this.start.y);
			
			if(dx < 0){						
				edgeWeightPositioning = -3;
			} else {
				edgeWeightPositioning = 3;
			}
			
			if(directed){ // weight is rendered on the side of the arrow
				ctx.fillText(this.weight, this.end.x  + edgeWeightPositioning * n.x -  3 *d.x, this.end.y  + edgeWeightPositioning * n.y -  3 *d.y);				
			} else {	// weitht is rendered in the middle of the edge
				var p = new Vector((this.start.x + this.end.x) / 2, (this.start.y + this.end.y) / 2);
				ctx.fillText(this.weight, p.x + edgeWeightPositioning * n.x, p.y + edgeWeightPositioning * n.y);					
			}
			
		}
		
		ctx.stroke();
		
		if(directed){	
			// rendering the arrow
			n.normalize();			
			n.scale(4);
			ctx.beginPath();	
			ctx.moveTo(this.end.x + n.x - 2*d.x, this.end.y + n.y - 2*d.y);
			ctx.lineTo(this.end.x - d.x, this.end.y - d.y);	
			ctx.lineTo(this.end.x - n.x - 2*d.x, this.end.y - n.y - 2*d.y);
			ctx.fill();	
		} 
	}
		
	this.isHit = function(x, y, maxDist){	
		this.update();	
		dist = normal.scalarProduct2c(x, y) - c; // distance from clickpoint to edge
		if(Math.abs(dist) <= maxDist){
			d.normalize();
			d.scale(sourceKnotRadius);
			visibleEdgeStart = new Vector(this.start.x, this.start.y);
			visibleEdgeStart = visibleEdgeStart.add(d);
			
			var ds = Math.sqrt(Math.pow((this.start.x - x), 2) + Math.pow((this.start.y - y), 2));
			var de = Math.sqrt(Math.pow((this.end.x - x), 2) + Math.pow((this.end.y - y), 2));
			
			if(direction.x == 0){
				var l = (y - visibleEdgeStart.y) / direction.y;
				
			} else {
				var l = (x - visibleEdgeStart.x) / direction.x;
			}
			
			return ((0 <= l) && (l <= 1) && (ds >= sourceKnotRadius) && (de >= targetKnotRadius));
		} else {
			return false
		}
	}
	
	// for codecomments of the following function see constuctor of edge 
	this.update = function(){
		normal = new Vector(e.y - s.y, s.x - e.x);	
		normal.normalize();
		c = normal.scalarProduct1v(s);
		
		direction = new Vector(e.x - s.x, e.y - s.y);	
		
		d = new Vector(direction.x, direction.y);
		d.normalize();
		d.scale(sourceKnotRadius + targetKnotRadius);
		direction = direction.subtract(d);		
	}
}
//-------------------------------------------------------------------------
//Edges end
//-------------------------------------------------------------------------

function Graph(dir, wei , knotR, renderctx){
	var self = this; 		// to have acess to the public variables out of a protected method
	
	var directed = dir;		// holds if the graph is directed or not
	var weighted = wei;		// holds if the graph is weighted or not
	var knotRadius = knotR;	// holds an default radius for all knots 	
	var empty = true;		// just right after initialisation this value holds false
	var lastNodeName = 0;	// can be used for a iterativ knot nameing
	
	var ctx = renderctx;	// holds the rendercontext	
	var knots = new Array;	// holds the knots
	var edges = new Array; 	// holds the edges
	var selectedKnotsCount = 0; // holds how much knots are selected
	var selectedEdgesCount = 0; // holds how much edges are selected
	
//-------------------------------------------------------------------------
// Setter begin
//-------------------------------------------------------------------------
	
	this.setDirected = function(value){
		directed = value;		
		for(var i = 0; i < edges.length; i ++){
			edges[i].setDirected(value);
		}
	}

	this.setWeighted = function(value){
		weighted = value;
		for(var i = 0; i < edges.length; i ++){
			edges[i].setWeighted(value);
		}
	}	
	
//-------------------------------------------------------------------------
// Setter end
//-------------------------------------------------------------------------
	
	
//-------------------------------------------------------------------------
// Getter begin
//-------------------------------------------------------------------------
	
	//gets a copy of the knotarray
	this.getKnots = function(){
		result = new Array;
		for(var i = 0; i < knots.length; i++){
			result[i] = knots[i];
		}
		return result;
	}
	
	//gets a copy of the edgesarray
	this.getEdges = function(){
		result = new Array;
		for(var i = 0; i < edges.length; i++){
			result[i] = edges[i];
		}
		return result;
	}	
	
	//getKnotByIndex returns a knot by its index
	this.getKnotByIndex = function(i){
		return knots[i];
	}
	
	//getKnotByID returns a knot by its id
	this.getKnotByID = function(id){
		for(k in knots){
			if(k.getId() == id) return k;
		}
	}
	//getKnotIndexByPoint returns the index of a knot if it was hit 
	//returns: index if a knot was hit, -1 if no knot was hit
	this.getKnotIndexByPoint = function(x, y){
		if(knots.length > 0){
			for(var i = knots.length-1; i >= 0; i--){
				var d = Math.sqrt(Math.pow((knots[i].x - x), 2) + Math.pow((knots[i].y - y), 2));
				if(d < knots[i].r){
					return i;
				}
			}
			return -1;
		}		
	}	


	//TODO: test this method
	//getKnotIndexByKnot returns the index of a knot 
	//returns: index if a knot was hit, -1 if no knot was found
	this.getKnotIndex = function(knot){
		if(knots.length > 0){
			for(var i = 0; i < knots.length; i++){
				if(knot == knots[i]){
					return i;
				}
			}
			return -1;
		}		
	}	
	
	//TODO: test this method
	//getKnotIdByKnot returns the id of a knot 
	//returns: id if a knot was hit, -1 if no knot was found
	this.getKnotId = function(knot){
		if(knots.length > 0){
			for(var i = 0; i < knots.length; i++){
				if(knot == knots[i]){
					return knots[i].getId();
				}
			}
			return -1;
		}		
	}	
	
	//getSelectedKnotsCount returns the count of knots which are selected
	this.getSelectedKnotsCount = function(){
		return selectedKnotsCount;
	}
	
	//getSelectedEdgesCount returns the count of edges are selected
	this.getSelectedEdgesCount = function(){
		return selectedEdgesCount;
	}
	
	//isDirected returns wether the graph is a directed one or not
	this.isDirected = function(){
		return directed;
		
	}	
	
	//isweighted returns wether the graph is a weighted one or not
	this.isWeighted = function(){
		return weighted;
		
	}
	
//-------------------------------------------------------------------------
// Getter end
//-------------------------------------------------------------------------		
	
	
//-------------------------------------------------------------------------
// Adding and removing begin
//-------------------------------------------------------------------------	

	//adding a knot by giving all attributes an the Id
	//Attantion: this method is only intendet for remakeing saved graphs 
	this.addKnotWithId = function(x, y, r, id, name, color){
		knots[knots.length] = new Knot(x, y, r, name, ctx);
		knots[knots.length - 1].fillColor = color;
		knots[knots.length - 1].setId(id);
		
		empty = false;
	}
	
	
	//adding a knot by giving all attributes
	this.addKnot = function(x, y, r, name, color){
		knots[knots.length] = new Knot(x, y, r, name, ctx);
		knots[knots.length - 1].fillColor = color;
		empty = false;
	}
	
	
	//adding a knot by giving the destinated position 
	this.addKnotByPosition = function(x, y){
		knots[knots.length] = new Knot(x, y, knotRadius, lastNodeName, ctx);
		lastNodeName += 1;
		empty = false;
	}
	
	
	//adding a knot by giving the destinated position with own name
	this.addKnotByPositionAndName = function(x, y, name){
		knots[knots.length] = new Knot(x, y, knotRadius, name, ctx);
		empty = false;
	}
	

	//adding an edge by giving all attributes and the Id 
	//startKnot and endKnot are indizes in the arrays
	//Attantion: this method is only intendet to remake saved graphs 
	this.addEdgeWithId = function(startKnot, endKnot, id, weight, color, directed, weighted){
		edges[edges.length] = new Edge(knots[startKnot], knots[endKnot], knotRadius, knotRadius, weight, ctx);
		edges[edges.length - 1].color = color;
		edges[edges.length - 1].setDirected(directed);
		edges[edges.length - 1].setWeighted(weighted);
		edges[edges.length - 1].setId(id);
		return 1;
	}
	
	
	//addHalfEdgeWithId adds a halfedge via its id
	//Attention:recommendet to use only when rebuild an saved Graph
	//Attention:no conflicttests (if the edge exists allredy)
	this.addHalfEdgeWithId = function(startKnot, endKnot, id, brotherId, weight, color, directed, weighted){
		edges[edges.length] = new HalfEdge(knots[startKnot], knots[endKnot], knotRadius, knotRadius, 0, brotherId, ctx);
		edges[edges.length - 1].color = color;
		edges[edges.length - 1].setDirected(directed);
		edges[edges.length - 1].setWeighted(weighted);
		edges[edges.length - 1].setId(id);
	}


	//adding an edge by giving all attributes
	//returns 1 if edge was added, returns -1 if edge exists already
	this.addEdge = function(startKnot, endKnot, weight, color, directed, weighted){
		var existingEdges = -1; // -1 when no Edge was found, -2 if two edges where found, indize if one edge was found 
		for(e in edges){
			if(((edges[e].start.getId() == knots[startKnot].getId()) && (edges[e].end.getId() == knots[endKnot].getId())) || ((edges[e].end.getId() == knots[startKnot].getId()) && (edges[e].start.getId() == knots[endKnot].getId()))){
				if(existingEdges == -1){
					existingEdges = e;
				} else if(existingEdges >= 0){
					existingEdges = -2;
				}
			}			
		}		
		
		//alert(existingEdges >= 0 && directed);
		if(existingEdges == -1){
			edges[edges.length] = new Edge(knots[startKnot], knots[endKnot], knotRadius, knotRadius, weight, ctx);
			edges[edges.length - 1].color = color;
			edges[edges.length - 1].setDirected(directed);
			edges[edges.length - 1].setWeighted(weighted);
			return 1;
		} else if((existingEdges >= 0) && directed){
			if((edges[existingEdges].end.getId() == knots[startKnot].getId()) && (edges[existingEdges].start.getId() == knots[endKnot].getId())){
			
				//new edge
				edges[edges.length] = new HalfEdge(knots[startKnot], knots[endKnot], knotRadius, knotRadius, weight, edges[existingEdges].getId(), ctx);
				edges[edges.length - 1].color = color;
				edges[edges.length - 1].setDirected(directed);
				edges[edges.length - 1].setWeighted(weighted);
				
				//the old edge must become a halfEdge too
				var oldEdge = new HalfEdge(knots[endKnot], knots[startKnot], knotRadius, knotRadius, edges[existingEdges].weight, edges[edges.length - 1].getId(), ctx);
				oldEdge.setDirected(directed);
				oldEdge.setWeighted(weighted);
				oldEdge.setId(edges[existingEdges].getId());
				oldEdge.color = edges[existingEdges].color;	
				edges.splice(existingEdges, 1, oldEdge);
				return 1;
			}
		} else if((existingEdges >= 0) && !directed){
			
			//the new edge will take the place beside the existing edge
			edges[edges.length] = new HalfEdge(edges[existingEdges].end, edges[existingEdges].start, knotRadius, knotRadius, weight, edges[existingEdges].getId(), ctx);
			edges[edges.length - 1].color = color;
			edges[edges.length - 1].setDirected(directed);
			edges[edges.length - 1].setWeighted(weighted);
			
			//the old edge must become a halfEdge too
			var oldEdge = new HalfEdge(edges[existingEdges].start, edges[existingEdges].end, knotRadius, knotRadius, edges[existingEdges].weight, edges[edges.length - 1].getId(), ctx);
			oldEdge.setDirected(directed);
			oldEdge.setWeighted(weighted);
			oldEdge.setId(edges[existingEdges].getId());
			oldEdge.color = edges[existingEdges].color;	
			edges.splice(existingEdges, 1, oldEdge);
			return 1;
		}
		return -1;
	}
	
	
	//addEdgeByToIndices adds an edge by giving the two indices of the start and end knot
	//returns 1 if edge was added, returns -1 if edge exists already
	this.addEdgeByToIndices = function(startKnot, endKnot){
		var existingEdges = -1; // -1 when no Edge was found, -2 if two edges where found, indize if one edge was found 
		for(e in edges){
			if(((edges[e].start.getId() == knots[startKnot].getId()) && (edges[e].end.getId() == knots[endKnot].getId())) || ((edges[e].end.getId() == knots[startKnot].getId()) && (edges[e].start.getId() == knots[endKnot].getId()))){
				if(existingEdges == -1){
					existingEdges = e;
				} else if(existingEdges >= 0){
					existingEdges = -2;
				}
			}			
		}		
		
		//alert(existingEdges >= 0 && directed);
		if(existingEdges == -1){
			edges[edges.length] = new Edge(knots[startKnot], knots[endKnot], knotRadius, knotRadius, 0, ctx);
			edges[edges.length - 1].setDirected(directed);
			edges[edges.length - 1].setWeighted(weighted);
			return 1;
		} else if((existingEdges >= 0) && directed){
			if((edges[existingEdges].end.getId() == knots[startKnot].getId()) && (edges[existingEdges].start.getId() == knots[endKnot].getId())){
			
				//new edge
				edges[edges.length] = new HalfEdge(knots[startKnot], knots[endKnot], knotRadius, knotRadius, 0, edges[existingEdges].getId(), ctx);
				edges[edges.length - 1].setDirected(directed);
				edges[edges.length - 1].setWeighted(weighted);
				
				//the old edge must become a halfEdge too
				var oldEdge = new HalfEdge(knots[endKnot], knots[startKnot], knotRadius, knotRadius, edges[existingEdges].weight, edges[edges.length - 1].getId(), ctx);
				oldEdge.setDirected(directed);
				oldEdge.setWeighted(weighted);
				oldEdge.setId(edges[existingEdges].getId());
				oldEdge.color = edges[existingEdges].color;	
				edges.splice(existingEdges, 1, oldEdge);
				return 1;
			}
		} else if((existingEdges >= 0) && !directed){
			
			//the new edge will take the place beside the existing edge
			edges[edges.length] = new HalfEdge(edges[existingEdges].end, edges[existingEdges].start, knotRadius, knotRadius, 0, edges[existingEdges].getId(), ctx);
			edges[edges.length - 1].setDirected(directed);
			edges[edges.length - 1].setWeighted(weighted);
			
			//the old edge must become a halfEdge too
			var oldEdge = new HalfEdge(edges[existingEdges].start, edges[existingEdges].end, knotRadius, knotRadius, edges[existingEdges].weight, edges[edges.length - 1].getId(), ctx);
			oldEdge.setDirected(directed);
			oldEdge.setWeighted(weighted);
			oldEdge.setId(edges[existingEdges].getId());
			oldEdge.color = edges[existingEdges].color;	
			edges.splice(existingEdges, 1, oldEdge);
			return 1;
		}
		return -1;
	}

	
	//adding an edge by giving the two indices of the start and end knot and a weight
	//returns 1 if edge was added, returns -1 if edge exists already
	this.addEdgeByWeight = function(startKnot, endKnot, weight){
		var existingEdges = -1; // -1 when no Edge was found, -2 if two edges where found, indize if one edge was found 
		for(e in edges){
			if(((edges[e].start.getId() == knots[startKnot].getId()) && (edges[e].end.getId() == knots[endKnot].getId())) || ((edges[e].end.getId() == knots[startKnot].getId()) && (edges[e].start.getId() == knots[endKnot].getId()))){
				if(existingEdges == -1){
					existingEdges = e;
				} else if(existingEdges >= 0){
					existingEdges = -2;
				}
			}			
		}		
		
		//alert(existingEdges >= 0 && directed);
		if(existingEdges == -1){
			edges[edges.length] = new Edge(knots[startKnot], knots[endKnot], knotRadius, knotRadius, weight, ctx);
			edges[edges.length - 1].setDirected(directed);
			edges[edges.length - 1].setWeighted(weighted);
			return 1;
		} else if((existingEdges >= 0) && directed){
			if((edges[existingEdges].end.getId() == knots[startKnot].getId()) && (edges[existingEdges].start.getId() == knots[endKnot].getId())){
			
				//new edge
				edges[edges.length] = new HalfEdge(knots[startKnot], knots[endKnot], knotRadius, knotRadius, weight, edges[existingEdges].getId(), ctx);
				edges[edges.length - 1].setDirected(directed);
				edges[edges.length - 1].setWeighted(weighted);
				
				//the old edge must become a halfEdge too
				var oldEdge = new HalfEdge(knots[endKnot], knots[startKnot], knotRadius, knotRadius, edges[existingEdges].weight, edges[edges.length - 1].getId(), ctx);
				oldEdge.setDirected(directed);
				oldEdge.setWeighted(weighted);
				oldEdge.setId(edges[existingEdges].getId());
				oldEdge.color = edges[existingEdges].color;	
				edges.splice(existingEdges, 1, oldEdge);
				return 1;
			}
		} else if((existingEdges >= 0) && !directed){
			
			//the new edge will take the place beside the existing edge
			edges[edges.length] = new HalfEdge(edges[existingEdges].end, edges[existingEdges].start, knotRadius, knotRadius, weight, edges[existingEdges].getId(), ctx);
			edges[edges.length - 1].setDirected(directed);
			edges[edges.length - 1].setWeighted(weighted);
			
			//the old edge must become a halfEdge too
			var oldEdge = new HalfEdge(edges[existingEdges].start, edges[existingEdges].end, knotRadius, knotRadius, edges[existingEdges].weight, edges[edges.length - 1].getId(), ctx);
			oldEdge.setDirected(directed);
			oldEdge.setWeighted(weighted);
			oldEdge.setId(edges[existingEdges].getId());
			oldEdge.color = edges[existingEdges].color;	
			edges.splice(existingEdges, 1, oldEdge);
			return 1;
		}
		return -1;
	}
	
	
	//removes all selected knots and incident edges 
	this.removeKnotsBySelection = function(){
		if(knots.length > 0){
			var knotsToKeep = new Array;
			var knotsToRemove = new Array;
			var edgesToKeep = new Array;
			var newEdges = new Array;
			
			for(var i = 0; i < knots.length; i++){
				if(!knots[i].isSelected()){
					knotsToKeep[knotsToKeep.length] = knots[i];
				} else {		
					knotsToRemove[knotsToRemove.length] = knots[i];
				}					
			}
			
			for(var i = 0; i < knotsToRemove.length; i++){
				for(var j = 0; j < edges.length; j++){
					if(!(edges[j].start == knotsToRemove[i] || edges[j].end == knotsToRemove[i])){
						edgesToKeep[edgesToKeep.length] = edges[j];						
					}
				}
				edges = edgesToKeep;
				edgesToKeep = new Array;
			}
						
			knots = knotsToKeep;
		}
		selectedKnotsCount = 0;
	}
	
	
	//removes all selected edges 
	this.removeEdgesBySelection = function(){
		if(edges.length > 0){
			var edgesToKeep = new Array;
			var brotherIDs = new Array;
			for(e in edges){
				if(!edges[e].isSelected()){
					edgesToKeep[edgesToKeep.length] = edges[e];
				} else if(edges[e].getType() == 'halfEdge'){
					brotherIDs[brotherIDs.length] = edges[e].getBrotherId();
				}
			}		
			edges = edgesToKeep;

			for(e in edges){
				for(i in brotherIDs){
					if(edges[e].getId() == brotherIDs[i]){
						//the brother edge must become a normal edge again
						var botherEdge = new Edge(edges[e].start, edges[e].end, knotRadius, knotRadius, edges[e].weight, ctx);
						botherEdge.setDirected(directed);
						botherEdge.setWeighted(weighted);
						botherEdge.setId(edges[e].getId());
						botherEdge.color = edges[e].color;	
						botherEdge.setSelected(edges[e].isSelected());
						edges.splice(e, 1, botherEdge);
						brotherIDs.splice(i,1);
					}
				}
			}
		}
		selectedEdgesCount = 0;
	}
	
	
	//removes all knots and all edges
	this.removeAllKnots = function(){
		this.removeAllEdges();
		knots = new Array;		
		selectedKnotsCount = 0;
		selectedEdgesCount = 0;
	}

	
	//removes all edges
	this.removeAllEdges = function(){
		edges = new Array;	
		selectedEdgesCount = 0;	
	}
	
	
	//clears the graph from all knots and edges
	this.clear = function(){
		this.removeAllKnots();
		selectedKnotsCount = 0;
	}
	
	
	this.removeKnotByIndex = function(i){
		if(knots[i].isSelected()){
			selectedKnotsCount -= 1;
		}
		knots.splice(i,1);
		
		var edgesToKeep = new Array;
		var newEdges = new Array;
		
		for(var j = 0; j < edges.length; j++){
			if(!(edges[j].start == knots[i] || edges[j].end == knots[i])){
				edgesToKeep[edgesToKeep.length] = j;
			}
		}
		for(var j = 0; j < edgesToKeep.length; j++){
			newEdges[newEdges.length] = edges[j];
		}
		edges = newEdges;
	}
	
	
	//adds an edge between the both first selected knots in the array
	this.addEdgeQuick = function(){
		if(knots.length > 0){
		var hits = 0;
		var s;
		var e;
		var i = 0;
			while((hits < 2) && (i < knots.length)){
				if(knots[i].isSelected() && hits == 0){
					s = i;
					knots[s].setSelected(false);
					hits += 1;
				} else {
					if(knots[i].isSelected() && hits == 1){
						e = i;
						knots[e].selected(false);
						hits += 1; 
					}
				}
				 i += 1;
			}
			if(s != null && e != null){
				edges[edges.length] = new Edge(knots[s], knots[e], knotRadius, knotRadius, 0, ctx);
			}
		}	
	}
	
//-------------------------------------------------------------------------
// Adding and removing end
//-------------------------------------------------------------------------		


//-------------------------------------------------------------------------
// Selection begin
//-------------------------------------------------------------------------
	
	//selectKnotByPoint selects a knot if it was hit 
	//Attention: no matter if it was selected befor or not
	//returns: id if a knot was hit, -1 if no knot was hit
	this.selectKnotByPoint = function(x, y){
		if(knots.length > 0){
			for(var i = knots.length-1; i >= 0; i = i-1){
				var d = Math.sqrt(Math.pow((knots[i].x - x), 2) + Math.pow((knots[i].y - y), 2));
				if(d < knots[i].r){
					if(!knots[i].isSelected()){
						selectedKnotsCount += 1;
					}
					knots[i].setSelected(true);
					return i;
				}
			}
			return -1;
		}		
	}	

	//selectKnotByRect selects all knots if they are in the selection rectangle 
	//Attention: no matter if it was selected befor or not
	this.selectKnotByRect = function(xst, xen, yst, yen){
		if(knots.length > 0){
			var xs = Math.min(xst, xen);
			var xe = Math.max(xst, xen);
			var ys = Math.min(yst, yen);
			var ye = Math.max(yst, yen);
			
			for(var i = 0; i < knots.length; i++){
				if(knots[i].x < xe && knots[i].x > xs && knots[i].y < ye && knots[i].y > ys){
					if(!knots[i].isSelected()){
						selectedKnotsCount += 1;
					}
					knots[i].setSelected(true);
				}
			}
		}		
	}		
	
	//selectKnotByIndex selects the knot with index
	this.selectKnotByIndex = function(i){
		if(!knots[i].isSelected()){
			selectedKnotsCount += 1;
		}
		knots[i].setSelected(true);
	}

	
	//selectEdgeByPoint selects an edge if it was hit 
	//Attention: no matter if it was selected befor or not
	//returns: id if a edge was hit, -1 if no edge was hit
	this.selectEdgeByPoint = function(x, y){
		if(edges.length > 0){
			for(var i = edges.length-1; i >= 0; i = i-1){	
				if(edges[i].isHit(x,y,8)){
					if(!edges[i].isSelected()){
						selectedEdgesCount += 1;
					}
					edges[i].setSelected(true);
					return i;
				}
			}
			return -1;
		}		
	}	
	
	//selectEdgeByRect selects all Edges if both of their knots are in the selection rectangle 
	//Attention: no matter if it was selected befor or not
	this.selectEdgeByRect = function(xst, xen, yst, yen){
		if(knots.length > 0){
			var xs = Math.min(xst, xen);
			var xe = Math.max(xst, xen);
			var ys = Math.min(yst, yen);
			var ye = Math.max(yst, yen);
			
			for(var i = 0; i < edges.length; i++){
				var startKnotIsInRect = edges[i].start.x < xe && edges[i].start.x > xs && edges[i].start.y < ye && edges[i].start.y > ys;
				var endKnotIsInRect = edges[i].end.x < xe && edges[i].end.x > xs && edges[i].end.y < ye && edges[i].end.y > ys;
				if(startKnotIsInRect && endKnotIsInRect){
					selectedEdgesCount += 1;
					edges[i].setSelected(true);
				}
			}
		}		
	}	
	
	//deselectKnotByPoint deselects a knot if it was hit 
	//Attention: no matter if it was selected befor or not
	//returns: id if a knot was hit, -1 if no knot was hit
	this.deselectKnotByPoint = function(x, y){
		if(knots.length > 0){
			for(var i = knots.length-1; i >= 0; i = i-1){
				var d = Math.sqrt(Math.pow((knots[i].x - x), 2) + Math.pow((knots[i].y - y), 2));
				if(d < knots[i].r){
					if(knots[i].isSelected()){
						selectedKnotsCount -= 1;
					}
					knots[i].setSelected(false);
					return i;
				}
			}
			return -1;
		}		
	}	
	

	//deselectKnotByRect deselects all knots if they are in the selection rectangle 
	//Attention: no matter if it was selected befor or not
	this.deselectKnotByRect = function(xst, xen, yst, yen){
		if(knots.length > 0){
			var xs = Math.min(xst, xen);
			var xe = Math.max(xst, xen);
			var ys = Math.min(yst, yen);
			var ye = Math.max(yst, yen);
			
			for(var i = 0; i < knots.length; i++){
				if(knots[i].x < xe && knots[i].x > xs && knots[i].y < ye && knots[i].y > ys){
					if(knots[i].isSelected()){
						selectedKnotsCount -= 1;
					}
					knots[i].setSelected(false);
				}
			}
		}		
	}	

	//deselectKnotByIndex deselects the knot with given index
	this.deselectKnotByIndex = function(i){
		if(knots[i].isSelected()){
			selectedKnotsCount -= 1;
		}
		knots[i].setSelected(false);
	}
	
	
	//deselectEdgeByPoint deselects a edge if it was hit 
	//Attention: no matter if it was selected befor or not
	//returns: id if a edge was hit, -1 if no edge was hit
	this.deselectEdgeByPoint = function(x, y){
		if(edges.length > 0){
			for(var i = edges.length-1; i >= 0; i = i-1){	
				if(edges[i].isHit(x,y,8)){
					if(edges[i].isSelected()){
						selectedEdgesCount -= 1;
					}
					edges[i].setSelected(false);
					return i;
				}
			}
			return -1;
		}
	}
	
	//toggleSelectKnotByPoint toggles the selection of an knot if it was hit
	//returns: -2 when no knot was hit, -1 when a knot was deselected, i >= 0 when a knot was selectet
	//were i is the index of the knot in the knots array
	this.toggleSelectKnotByPoint = function(x, y){
		if(knots.length > 0){
			for(var i = knots.length-1; i >= 0; i = i-1){
				var d = Math.sqrt(Math.pow((knots[i].x - x), 2) + Math.pow((knots[i].y - y), 2));
				if(d < knots[i].r){
					if(knots[i].selected){
						knots[i].setSelected(false);
						return -1;
					} else {
						knots[i].setSelected(true);
						return i;
					}
				}
			}
			return -2;
		}		
	}

	//toggleSelectKnotByPoint toggles the selection of an knot if it was hit
	this.toggleSelectKnotByRect = function(xst, xen, yst, yen){
		if(knots.length > 0){
			var xs = Math.min(xst, xen);
			var xe = Math.max(xst, xen);
			var ys = Math.min(yst, yen);
			var ye = Math.max(yst, yen);
			
			for(var i = 0; i < knots.length; i++){
				if(knots[i].x < xe && knots[i].x > xs && knots[i].y < ye && knots[i].y > ys){	
					knots[i].setSelected(!knots[i].isSelected());
				}
			}
		}		
	}
	
	//toggleSelectKnotByIndex toggles the selection of a knot given by the index
	this.toggleSelectKnotByIndex = function(i){
		knots[i].setSelected(!knots[i].isSelected());
	}

	// deselects all knots and all edges
	this.deselectAll = function(){
		deselectKnots();
		deselectEdges();
	}
	
	//deselects all knots 
	this.deselectAllKnots = function(){
		deselectKnots();
	}

	//deselects all edges 
	this.deselectAllEdges = function(){
		deselectEdges();
	}
	
	// deselects all knots
	function deselectKnots(){
		if(knots.length > 0){
			for(var i = 0; i < knots.length; i++){
				knots[i].setSelected(false);
			}		
			selectedKnotsCount = 0;	
		}		
	}
	
	// deselects all edges
	function deselectEdges(){
		if(edges.length > 0){
			for(var i = 0; i < edges.length; i++){
				edges[i].setSelected(false);
			}
			selectedEdgesCount = 0;	
		}		
	}
	
//-------------------------------------------------------------------------
// Selection end
//-------------------------------------------------------------------------

	
//-------------------------------------------------------------------------
// Manipulation begin
//-------------------------------------------------------------------------

	// translateKnotsBySelection moves all selectet knots relativ to there positions by dx and dy
	// returns 0 if no collision with a canvas edge was detectet
	// return 1 if a collision with the left canvas edge was detectet (knot shouldn't be moved out of the canvas)
	// return 2 if collision with top canvas edge
	// return 3 if collision with right canvas edge
	// return 4 if collision with bottom canvas edge
	this.translateKnotsBySelection = function(dx, dy){
		var collisionEdge = 0;
		if(knots.length > 0){
			for(var i = 0; i < knots.length; i++){
				if(knots[i].isSelected()){
					newX = knots[i].x + dx;
					newY = knots[i].y + dy;
					if(newX <= 0){
						if(dx >= 0){
							knots[i].x = newX;								
						}
						collisionEdge = 1;
					} else if(newX >= canvas.width){
						if(dx <= 0){
							knots[i].x = newX;								
						}
						collisionEdge = 3;
					} else{
						knots[i].x = newX;						
					}

					if(newY <= 0){
						if(dy >= 0){
							knots[i].y = newY;								
						}
						collisionEdge = 2;
					} else if(newY >= canvas.height){
						if(dy <= 0){
							knots[i].y = newY;								
						}
						collisionEdge = 4;
					} else{
						knots[i].y = newY;						
					}
				}
			}
			return collisionEdge;
		}				
	}
	
	//changeKnotNameByIndex changes the name of a knot via his ID
	this.changeKnotNameByIndex = function(name, i){
		if(knots.length > 0){
			knots[i].name = name;
		}	
	}
		
	//changeKnotNameBySelection changes the name of all selectet knots
	this.changeKnotNameBySelection = function(name){
		if(knots.length > 0){
			for(var i = 0; i < knots.length; i++){
				if(knots[i].isSelected()){
					knots[i].name = name;
				}
			}
		}				
	}
	
	//changeKnotColorBySelection changes the colo of all selectet knots
	this.changeKnotColorBySelection = function(c){
		if(c.charAt(0) != '#'){
			c = '#' + c;
		}
		if(knots.length > 0){
			for(var i = 0; i < knots.length; i++){
				if(knots[i].isSelected()){
					knots[i].fillColor = c;
				}
			}
		}	
	}

	//changeKnotRadiusBySelection changes the radius of all selectet knots
	this.changeKnotRadiusBySelection = function(r){			
		if(knots.length > 0){
			for(var i = 0; i < knots.length; i++){
				if(knots[i].isSelected()){
					knots[i].r = r;
				}
			}
		}			
	}	
	
	//changeEdgeWeightBySelection changes the weight of all selectet edges
	this.changeEdgeWeightBySelection = function(weight){
		if(edges.length > 0){
			for(var i = 0; i < edges.length; i++){
				if(edges[i].isSelected()){
					edges[i].weight = weight;
				}
			}
		}				
	}
	
	//changeEdgeColorBySelection changes the color of all selectet edges
	this.changeEdgeColorBySelection = function(c){
		if(c.charAt(0) != '#'){
			c = '#' + c;
		}
		if(edges.length > 0){
			for(var i = 0; i < edges.length; i++){
				if(edges[i].isSelected()){
					edges[i].color = c;
				}
			}
		}				
	}
		
//-------------------------------------------------------------------------
// Manipulation end
//-------------------------------------------------------------------------
	
	
//-------------------------------------------------------------------------
// Render begin
//-------------------------------------------------------------------------
	
	//renderEdges renders the Edges
	function renderEdges(){		
		if(edges.length > 0){
			for(var i = 0; i < edges.length; i ++){	
				edges[i].render();
			}
		}
	}
	
	//renderKnots renders the Knots
	function renderKnots(){
		if(knots.length > 0){
			for(var i = 0; i < knots.length; i ++){		
				knots[i].render();
			}
		}
	}	
	
	//render renders the graph
	this.render = function(){
		renderEdges();
		renderKnots();
	}
		
//-------------------------------------------------------------------------
// Render end
//-------------------------------------------------------------------------
	

//-------------------------------------------------------------------------
// Conversion begin
//-------------------------------------------------------------------------
	
	//toString writes it self as a GraphML to a string 
	this.toString = function(){		
		var str = '<?xml version="1.0" encoding="UTF-8"?><graphml>';	
		str = str + '<key id="d0" for="node" attr.name="type" attr.type="string"/>';
		str = str + '<key id="d1" for="node" attr.name="id" attr.type="integer"/>';
		str = str + '<key id="d2" for="node" attr.name="name" attr.type="string"/>';
		str = str + '<key id="d3" for="node" attr.name="x" attr.type="integer"/>';
		str = str + '<key id="d4" for="node" attr.name="y" attr.type="integer"/>';
		str = str + '<key id="d5" for="node" attr.name="radius" attr.type="integer"/>';
		str = str + '<key id="d6" for="node" attr.name="color" attr.type="string"/>';

		str = str + '<key id="d7" for="edge" attr.name="type" attr.type="string"/>';
		str = str + '<key id="d8" for="edge" attr.name="id" attr.type="integer"/>';
		str = str + '<key id="d9" for="edge" attr.name="brotherId" attr.type="integer"/>';
		str = str + '<key id="d10" for="edge" attr.name="weight" attr.type="string"/>';
		str = str + '<key id="d11" for="edge" attr.name="color" attr.type="string"/>';
		str = str + '<key id="d12" for="edge" attr.name="directed" attr.type="string"/>';
		str = str + '<key id="d13" for="edge" attr.name="weighted" attr.type="string"/>';
		str = str + '<graph>';
		
		for(var i = 0; i < knots.length; i++){
			str = str + '<node id="n' + i + '">';
			str = str +	'<data key="d0">' + knots[i].getType() + '</data>';
			str = str +	'<data key="d1">' + knots[i].getId() + '</data>';
			str = str +	'<data key="d2">' + knots[i].name + '</data>';
			str = str +	'<data key="d3">' + knots[i].x + '</data>';
			str = str +	'<data key="d4">' + knots[i].y + '</data>';
			str = str +	'<data key="d5">' + knots[i].r + '</data>';
			str = str +	'<data key="d6">' + knots[i].fillColor + '</data>';
			str = str + '</node>';
		}
		
		for(var i = 0; i < edges.length; i++){
			str = str + '<edge id="e' + i + '" source="n' + this.getKnotIndex(edges[i].start) + '" target="n' + this.getKnotIndex(edges[i].end) + '">';
			
			str = str +	'<data key="d7">' + edges[i].getType() + '</data>';
			str = str +	'<data key="d8">' + edges[i].getId() + '</data>';
			if(edges[i].getType() == 'halfEdge'){
				str = str +	'<data key="d9">' + edges[i].getBrotherId() + '</data>';
			}
			str = str +	'<data key="d10">' + edges[i].weight + '</data>';
			str = str +	'<data key="d11">' + edges[i].color + '</data>';
			str = str +	'<data key="d12">' + edges[i].isDirected() + '</data>';
			str = str +	'<data key="d13">' + edges[i].isWeighted() + '</data>';
			str = str + '</edge>';		
		}
		
		str = str + '</graph>';
		str = str + '</graphml>';
		
		return str;
	}
	
	//selectionToString writes its selected parts as a GraphML to a string 
	this.selectionToString = function(){		
		var str = '<graphml>';	
		str = str + '<key id="d0" for="node" attr.name="type" attr.type="string"/>';
		str = str + '<key id="d1" for="node" attr.name="id" attr.type="integer"/>';
		str = str + '<key id="d2" for="node" attr.name="name" attr.type="string"/>';
		str = str + '<key id="d3" for="node" attr.name="x" attr.type="integer"/>';
		str = str + '<key id="d4" for="node" attr.name="y" attr.type="integer"/>';
		str = str + '<key id="d5" for="node" attr.name="radius" attr.type="integer"/>';
		str = str + '<key id="d6" for="node" attr.name="color" attr.type="string"/>';

		str = str + '<key id="d7" for="edge" attr.name="type" attr.type="string"/>';
		str = str + '<key id="d8" for="edge" attr.name="id" attr.type="integer"/>';
		str = str + '<key id="d9" for="edge" attr.name="brotherId" attr.type="integer"/>';
		str = str + '<key id="d10" for="edge" attr.name="weight" attr.type="string"/>';
		str = str + '<key id="d11" for="edge" attr.name="color" attr.type="string"/>';
		str = str + '<key id="d12" for="edge" attr.name="directed" attr.type="string"/>';
		str = str + '<key id="d13" for="edge" attr.name="weighted" attr.type="string"/>';
		str = str + '<graph>';
		
		for(var i = 0; i < knots.length; i++){
			if(knots[i].isSelected()){
				str = str + '<node id="n' + i + '">';
				str = str +	'<data key="d0">' + knots[i].getType() + '</data>';
				str = str +	'<data key="d1">' + knots[i].getId() + '</data>';
				str = str +	'<data key="d2">' + knots[i].name + '</data>';
				str = str +	'<data key="d3">' + knots[i].x + '</data>';
				str = str +	'<data key="d4">' + knots[i].y + '</data>';
				str = str +	'<data key="d5">' + knots[i].r + '</data>';
				str = str +	'<data key="d6">' + knots[i].fillColor + '</data>';
				str = str + '</node>';
			}
		}
		
		for(var i = 0; i < edges.length; i++){
			if(edges[i].isSelected){
				str = str + '<edge id="e' + i + '" source="n' + this.getKnotIndex(edges[i].start) + '" target="n' + this.getKnotIndex(edges[i].end) + '">';
				
				str = str +	'<data key="d7">' + edges[i].getType() + '</data>';
				str = str +	'<data key="d8">' + edges[i].getId() + '</data>';
				if(edges[i].getType() == 'halfEdge'){
					str = str +	'<data key="d9">' + edges[i].getBrotherId() + '</data>';
				}
				str = str +	'<data key="d10">' + edges[i].weight + '</data>';
				str = str +	'<data key="d11">' + edges[i].color + '</data>';
				str = str +	'<data key="d12">' + edges[i].isDirected() + '</data>';
				str = str +	'<data key="d13">' + edges[i].isWeighted() + '</data>';
				str = str + '</edge>';	
			}
		}
		
		str = str + '</graph>';
		str = str + '</graphml>';
		
		return str;
	}
	
	this.insert = function(graphML){
		var gxmlDoc;		
		gxmlDoc = loadXMLString(graphML);
		output = graphML;
		var nodes = gxmlDoc.getElementsByTagName("node");
		for(var i = 0; i < nodes.length; i++){
			var datas	= nodes[i].childNodes;		
			var type	= datas[0].childNodes[0].nodeValue;	
			var id	 	= datas[1].childNodes[0].nodeValue;	
			var name 	= datas[2].childNodes[0].nodeValue;	
			var x 		= datas[3].childNodes[0].nodeValue;	
			var y		= datas[4].childNodes[0].nodeValue;	
			var r		= datas[5].childNodes[0].nodeValue;	
			var color	= datas[6].childNodes[0].nodeValue;	

			self.addKnot(Number(x), Number(y), Number(r), String(name), color);
		}
		
		var edges = gxmlDoc.getElementsByTagName("edge");
		for(var i = 0; i < edges.length; i++){		
			var attributes 	= edges[i].attributes;
			
			var startKnot 	= attributes['source'].nodeValue;
			startKnot 		= startKnot.substring(1,startKnot.length); // ohne das vorangestellte n, welches zum GraphML Standart gehört
			var endKnot 	= attributes['target'].nodeValue; 
			endKnot			= endKnot.substring(1,endKnot.length);// ohne das vorangestellte n
			
			var datas 		= edges[i].childNodes;
			var type	 	= datas[0].childNodes[0].nodeValue;
			var id	 		= datas[1].childNodes[0].nodeValue;
			if(type == 'halfEdge'){
				var brotherId	= datas[2].childNodes[0].nodeValue;
				var weight 		= datas[3].childNodes[0].nodeValue;
				var color 		= datas[4].childNodes[0].nodeValue;
				var directed 	= datas[5].childNodes[0].nodeValue == 'true';
				var weighted 	= datas[6].childNodes[0].nodeValue == 'true';
				graph.addHalfEdgeWithId(startKnot, endKnot, Number(id), Number(brotherId), weight, color, directed, weighted);			
				
			} else {
				var weight 		= datas[2].childNodes[0].nodeValue;
				var color 		= datas[3].childNodes[0].nodeValue;
				var directed 	= datas[4].childNodes[0].nodeValue == 'true';
				var weighted 	= datas[5].childNodes[0].nodeValue == 'true';
				graph.addEdgeWithId(startKnot, endKnot, Number(id), weight, color, directed, weighted);			
			}
			
		}
	}
	
	//clons the graph
	this.clone = function(){
		this.directed = directed;	// holds if the graph is directed or not
		this.weighted = weighted;	// holds if the graph is weighted or not
		this.knotRadius = knotRadius;	// holds an default radius for all knots 
			
		var ctx = renderctx;	// holds the rendercontext
		
		var knots = new Array;	// holds the knots
		var edges = new Array; 	// holds the edges
		
		empty = true;
		
		var lastNodeName = 0;
		this.intelligentEdge = true;
		var edgeWeightPositioning = -3;
		graphClone = new Graph(directed, weighted, knotRadius, ctx);
	}
	
	// returns true if the graph has no knots (in that case no edges too)
	this.isEmpty = function(){
		return empty;
	}
}

//-------------------------------------------------------------------------
//Conversion end
//-------------------------------------------------------------------------

//#########################################################################
// Graph end
//#########################################################################