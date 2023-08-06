/**
 * 
 */

//#########################################################################
// EdgeDragger begin
//#########################################################################

// the edgedragger is a help tool for adding edges by dragging an edge out of a knot when crt is pressed
function EdgeDragger(renderctx){
	var self = this;
	this.startKnot = new Knot(0, 0, 20, -1, renderctx);
	this.endKnot = new Knot(0, 0,5, -1, renderctx);
	this.target = new Knot(0, 0,5, -1, renderctx);;
	
	this.isActiv = false;
	var ctx = renderctx;
	
	var a = new Vector(1,1); 
	var d = Math.sqrt(Math.pow(a.x, 2) + Math.pow(a.y, 2));
	a.normalize();
	a.scale(5);
	
	//setStart sets the startKnot of the edgedragger
	this.setStart = function(xs, ys){
		this.startKnot.x = xs;
		this.startKnot.y = ys;
	};
		
	//setEnd sets the endKnot of the edgedragger
	this.setEnd = function(xe, ye){
		this.endKnot.x = xe;
		this.endKnot.y = ye;
		
		a.x = xe - this.startKnot.x;
		a.y = ye - this.startKnot.y;
		d = Math.sqrt(Math.pow(a.x, 2) + Math.pow(a.y, 2));
		
		a.normalize();
		a.scale(5);
	};

	//hasValidTarget returns 1 if the current target of the edgeDragger is valid, 0 if not
	this.hasValidTarget = function(){
		if(this.endKnot.name > -1 && d > 20){
			return 1;
		} else {
			return 0;
		}		
	};
	
	//setTarget sets the target
	//t is a knot
	this.setTarget = function(t){
		this.target.x = t.x;
		this.target.y = t.y;
		this.target.r = t.r;
	};
	
	//render renders the edgeDragger
	this.render = function(){
		var d = Math.sqrt(Math.pow((this.endKnot.x -  this.startKnot.x), 2) + Math.pow((this.endKnot.y - this.startKnot.y), 2));
		if(this.isActiv){
			ctx.fillStyle = 'rgba(0,120,226,0.3)';	
			ctx.strokeStyle = 'rgba(0,130,226,0.6)';
			ctx.lineWidth = 2;	
			
			ctx.beginPath();	
			ctx.arc(this.startKnot.x, this.startKnot.y, this.startKnot.r, 0, 180, false);
			ctx.fill();
			ctx.stroke();
			
			if(d > 20){
				if(d > 25){
					ctx.beginPath();	
					ctx.moveTo(this.startKnot.x + 4*a.x, this.startKnot.y + 4*a.y);
					ctx.lineTo(this.endKnot.x - a.x, this.endKnot.y - a.y);		
					ctx.stroke();
				}
				
				if(this.hasValidTarget()  == 1){				
					ctx.beginPath();	
					ctx.arc(this.target.x, this.target.y, this.target.r, 0, 180, false);
					ctx.fill();
					ctx.stroke();
				}
				
				ctx.lineWidth = 1;				
				ctx.beginPath();
				ctx.arc(this.endKnot.x, this.endKnot.y, this.endKnot.r, 0, 180, false);
				ctx.fill();
				ctx.stroke();
				
			}					
		}
	};
}

//#########################################################################
// EdgeDragger end
//#########################################################################
