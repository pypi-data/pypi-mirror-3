/**
 * 
 */


//#########################################################################
// Selectionrectangle begin
//#########################################################################


function SelectRect(renderctx){
	var self = this;
	this.xs = 10;
	this.ys = 10;
	this.xe = 100;
	this.ye = 100;
	
	this.isActiv = false;
	var ctx = renderctx;
	
	this.render = function(){
		if(self.isActiv){
			ctx.lineWidth = 1;
			ctx.strokeStyle = 'rgba(0,130,226,0.6)';	
			ctx.fillStyle = 'rgba(0,120,226,0.1)';	
			ctx.fillRect(self.xs, self.ys, (self.xe - self.xs), (self.ye - self.ys));
			ctx.strokeRect(self.xs, self.ys, (self.xe - self.xs), (self.ye - self.ys));
		}
	};
}

//#########################################################################
// Selectionrectangle end
//#########################################################################