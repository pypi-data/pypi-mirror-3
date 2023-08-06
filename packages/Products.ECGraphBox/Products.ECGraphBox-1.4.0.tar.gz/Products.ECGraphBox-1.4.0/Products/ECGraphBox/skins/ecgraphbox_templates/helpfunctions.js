/**
 * 
 */

//#########################################################################
//xml Parse and Graphbuild Begin
//#########################################################################		

//makes a normal graph witch is optionally directed / weighted
//make 
function makeGraph(graphXml){	
	graph.clear();
	var nodes = graphXml.getElementsByTagName("node");
	for(var i = 0; i < nodes.length; i++){
		var datas	= nodes[i].childNodes;		
		var type	= datas[0].childNodes[0].nodeValue;	
		var id	 	= datas[1].childNodes[0].nodeValue;	
		var name 	= datas[2].childNodes[0].nodeValue;	
		var x 		= datas[3].childNodes[0].nodeValue;	
		var y		= datas[4].childNodes[0].nodeValue;	
		var r		= datas[5].childNodes[0].nodeValue;	
		var color	= datas[6].childNodes[0].nodeValue;	
		
		graph.addKnotWithId(Number(x), Number(y), r, Number(id), name, color);		
	}

	var edges = graphXml.getElementsByTagName("edge");
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
	update();
}


function saveGraph(){
	var submit = document.getElementById('answer');
	submit.value = graph.toString();
}

//test method 
function writeClipboard(){
	var submit = document.getElementById('answer');
	submit.value = clipboard.getData();
}

function saveNotes(){
	var submit = document.getElementById('answer');
	var notes = document.getElementById('ecgb_note');	
	var tempBegin = submit.value.substring(0, submit.value.length-10); // length of "</graphml>"
	var tempEnd = submit.value.substring(submit.value.length-10,submit.value.length); // length of "</graphml>"
	submit.value =  tempBegin + '<note>' + notes.value + '</note>';	
	submit.value += tempEnd;	
}

function ecgb_submit(){
	saveGraph();
	saveNotes();
}


function ecgb_displayNotes(graphXml){
	var notes = graphXml.getElementsByTagName('note');
	ecgb_noteTextarea.innerHTML = notes[0].childNodes[0].nodeValue;
	
}

// takes the sumitted xml document returns the GraphMl part that represent the Graph
function ecgb_getGraphMlFromSubmission(xmlDoc){
	return xmlDoc.getElementsByTagName('graph');
}

//takes the sumitted xml document and returns the Nots
function ecgb_getNotesFromSubmission(xmlDoc){
	return xmlDoc.getElementsByTagName('note');
		
}
//#########################################################################
//xml Parse and Graphbuild End
//#########################################################################