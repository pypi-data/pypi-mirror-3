/**
 * 
 */


//-------------------------------------------------------------------------
//HalfEdges begin
//-------------------------------------------------------------------------
//"Wer Knoten kennt, der kennt auch Kanten"  <----- http://www.youtube.com/watch?v=6Q3eOUZY9Rc


function HalfEdge(s, e,sourceKnotRadius, targetKnotRadius, weight, broId, ctx){
	var self = this;
	
	var edgeWeightPositioning = -3; // how far shell the weight of an edge be from the edge	
	var selected = false; 			// holds wether the edge is selected or not
	var directed = true; 			// holds wether the edge is directed or not
	var weighted = true;			// holds the weight of the edge
	var targetKnotRadius = targetKnotRadius; // holds the radius of the target Knot (importend for right rendering of the edge)
	var sourceKnotRadius = sourceKnotRadius; // holds the radius of the target Knot (importend for right rendering of the edge)
	
	var ctx = ctx; 					// the rendercontext in which the edge will render itself
	
	this.start = s;					// holds the start knot 	Attention: it holds not the index of the knot in the array!
	this.end = e;					// holds the end knot 		Attention: it holds not the index of the knot in the array!
	this.weight = weight;			// holds the weight of the edge
	this.color = 'rgba(0,0,0,1)';
	
	var timeStamp = new Date();
	var id = timeStamp.getTime();
	var brotherId = broId; 			//id of the brother
	var type = 'halfEdge';
	
	

	//-----------------------------------------------
	//render helpvariables begin
	//-----------------------------------------------
	// this is needed to represent a normal equation 
	var normal = new Vector(s.y - e.y, e.x - s.x);	
	normal.normalize();
	var c = normal.scalarProduct1v(s);	
	var direction = new Vector(e.x - s.x, e.y - s.y); // holds direction and length of visible edge

	var d = new Vector(direction.x, direction.y);
	d.normalize();
	d.scale(sourceKnotRadius + targetKnotRadius);
	direction = direction.subtract(d);

	var n = new Vector(normal.x, normal.y);
	
	//midpoint between start and end
	var p = new Vector((this.start.x + this.end.x) / 2, (this.start.y + this.end.y) / 2);	

	// Parabel representation of the curve
	var a = 0;
	var b = 0;
	
	//Arrowvariables
	var arrowDirection = new Vector(1, 0);
	var arrowNormal = new Vector(0, 1);
	
	//visible Start and End of the curve
	var visibleHalfEdgeStart = new Vector(this.start.x, this.start.y);
	var visibleHalfEdgeEnd = new Vector(this.end.x, this.end.y);
	//-----------------------------------------------
	//render helpvariables end
	//-----------------------------------------------
	
	
	this.getId = function(){
		return id;
	};

	this.getBrotherId = function(){
		return brotherId;
	};
	
	this.getType = function(){
		return type;
	};
	
	//sets the Id of the halfedge
	//Attention: this method is only indented for remake edges of a saved graph
	this.setId = function(value){
		id = value;
	};
	
	//takes true or false
	this.setDirected = function(value){
		directed = value;
	};
	
	//takes true or false
	this.setWeighted = function(value){
		weighted = value;
	};
	
	this.setSelected = function(value){
		selected = value;
	};
	
	this.isDirected = function(){
		return directed;
	};
	
	this.isWeighted = function(){
		return weighted;
	};
	
	this.isSelected = function(){
		return selected;
	};
	

	//@TODO funktion aufräumen
	this.render = function(){		
		this.update(); // update the normal and direction
		
		ctx.beginPath();	
		if(selected){
			ctx.strokeStyle = 'rgba(100,150,255,1)';	
			ctx.fillStyle = 'rgba(100,150,255,1)';	
		} else {
			ctx.strokeStyle = this.color;
			ctx.fillStyle = this.color;
		}
		
		//draw maincurve begin
		n = new Vector(normal.x, normal.y);
		n.normalize();		
		var directionCV1CV2 = new Vector(p.x + 60*n.x - this.start.x, p.y + 60*n.y - this.start.y); // noch im alten
		directionCV1CV2.normalize();
		var directionCV2CV3 = new Vector(p.x + 60*n.x - this.end.x , p.y + 60*n.y - this.end.y); // noch im alten
		directionCV2CV3.normalize();
		
		visibleHalfEdgeStart = new Vector(this.start.x + sourceKnotRadius*directionCV1CV2.x, this.start.y + targetKnotRadius*directionCV1CV2.y);
		visibleHalfEdgeEnd  = new Vector(this.end.x + sourceKnotRadius*directionCV2CV3.x, this.end.y + targetKnotRadius*directionCV2CV3.y);
		ctx.bezierCurveTo(visibleHalfEdgeStart.x, visibleHalfEdgeStart.y, p.x + 60*n.x, p.y + 60*n.y, visibleHalfEdgeEnd.x, visibleHalfEdgeEnd.y);		
		ctx.stroke();
		//draw maincurve end

		
		// render the arrow begin
		arrowDirection = new Vector(visibleHalfEdgeEnd.x - (p.x + 60*n.x), visibleHalfEdgeEnd.y -(p.y + 60*n.y));
		arrowDirection.normalize();
		arrowDirection.scale(targetKnotRadius);
		arrowNormal = new Vector(arrowDirection.y *(-1), arrowDirection.x);
		arrowNormal.normalize();
		arrowNormal.scale(4);
		// render the arrow end
		
		
		//render the weight begin
		if(weighted){
			ctx.textBaseline  = 'middle';
			ctx.textAlign = 'center'; 
			ctx.font = '15pt Arial';
			ctx.fillStyle = 'rgba(0,0,0,1)';
			
			var dx = (this.end.x - this.start.x);
			var dy = (this.end.y - this.start.y);
			
			if(dx < 0){						
				edgeWeightPositioning = 3;
			} else {			
				edgeWeightPositioning = 2;
			}
			if(directed){
				ctx.fillText(this.weight, this.end.x + edgeWeightPositioning * targetKnotRadius * n.x - d.x, this.end.y  + edgeWeightPositioning* targetKnotRadius* n.y - d.y);				
			} else {	
				p = new Vector((this.start.x + this.end.x) / 2, (this.start.y + this.end.y) / 2);
				ctx.fillText(this.weight, p.x + 15*edgeWeightPositioning * n.x, p.y + 15*edgeWeightPositioning * n.y);							
			}			
		}
		//render the weight begin		
		
		if(directed){	
			// for rendering the arrow
			ctx.beginPath();	
			ctx.moveTo(visibleHalfEdgeEnd.x - arrowDirection.x + arrowNormal.x, visibleHalfEdgeEnd.y - arrowDirection.y  + arrowNormal.y);	
			ctx.lineTo(visibleHalfEdgeEnd.x, visibleHalfEdgeEnd.y);
			ctx.lineTo(visibleHalfEdgeEnd.x - arrowDirection.x - arrowNormal.x, visibleHalfEdgeEnd.y - arrowDirection.y  - arrowNormal.y);	
			ctx.fill();	
		} 

	};
		
	//@TODO funktion aufräumen
	this.isHit = function(x, y, maxDist){ 
		// calculate the function equation of the parable begin
		d = new Vector(this.end.x - this.start.x, this.end.y -this.start.y);
		var p3 = new Vector(Math.sqrt(d.scalarProduct1v(d)), 0); // im neuen Koord.
		d.normalize();
		
		var a1 = new Vector((p.x + 60*n.x - this.start.x) / 2, (p.y + 60*n.y - this.start.y) / 2); // noch im alten
		a1 = new Vector(a1.scalarProduct1v(d), a1.scalarProduct1v(n)); // im neuen Koord.
		var a2 = new Vector(a1.x * (-1), a1.y); // im neuen
		a2 = new Vector(p3.x + a2.x, p3.y + a2.y );
		var p2 = new Vector((a2.x - a1.x) /2, (a2.y - a1.y) / 2); // im neuen
		p2 = new Vector(a1.x + p2.x, a1.y +  p2.y);

		a = calculateA(p2.x, p2.y, p3.x, p3.y);
		b = calculateB(p2.x, p2.y, a);
		// calculate the function equation of the parable end
		
		
		var relPos = new Vector(x - this.start.x, y - this.start.y);
		//alert(relPos.x  +" / " + relPos.y);
		var normalizedDirection = new Vector(direction.x, direction.y);
		normalizedDirection.normalize();
		normal.normalize();
		var transPos = new Vector(relPos.scalarProduct1v(normalizedDirection), relPos.scalarProduct1v(normal)); // transformation in the coordinatesystem of the parable
		//transPos.normalize();
		//alert(transPos.x  +" / " + p3.x);
		var fy = a*(transPos.x * transPos.x) + b *transPos.x;
		var dy = transPos.y - fy;
		
		
		this.update();	
		dist = normal.scalarProduct2c(x, y) - c;
		d.normalize();
		d.scale(sourceKnotRadius);
		visibleHalfEdgeStart = new Vector(this.start.x, this.start.y);
		visibleHalfEdgeStart = visibleHalfEdgeStart.add(d);
		
		
		var ds = Math.sqrt(Math.pow((this.start.x - x), 2) + Math.pow((this.start.y - y), 2));
		var de = Math.sqrt(Math.pow((this.end.x - x), 2) + Math.pow((this.end.y - y), 2));
		
		if(direction.x == 0){
			var l = transPos.y / p3.y;
			
		} else {
			var l = transPos.x / p3.x;
		}
		return ((Math.abs(dy) <= maxDist) && (0 <= l) && (l <= 1) && (ds >= sourceKnotRadius) && (de >= targetKnotRadius));
	};

	//@TODO funktion aufräumen
	this.update = function(){
		normal = new Vector(this.end.y - this.start.y, this.start.x - this.end.x);
		normal.normalize();
		c = normal.scalarProduct1v(s);
		
		direction = new Vector(this.end.x - this.start.x, this.end.y - this.start.y);	
		
		d = new Vector(direction.x, direction.y);
		d.normalize();
		d.scale(sourceKnotRadius + targetKnotRadius);
		direction = direction.subtract(d);
		p = new Vector((this.start.x + this.end.x) / 2, (this.start.y + this.end.y) / 2);	
	};

	function calculateA(x1, y1, x2, y2){
	   var a = 0;
	   a = (y1 - (y2*x1)/x2) / ((x1*x1) - (x1*x2));
	   return a;
	}
	
	function calculateB(x1, y1, a){
	   var b = 0;
	   b = (y1 - a*(x1*x1)) / x1;
	   return b;
	}
}
//-------------------------------------------------------------------------
//HalfEdgex1 end
//-------------------------------------------------------------------------
