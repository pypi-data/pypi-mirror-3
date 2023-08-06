/**
 * 
 */

function Vector(x, y){
	var self = this;
	this.x = x;
	this.y = y;
	
	this.normalize = function(){
		var norm = Math.sqrt(Math.pow(this.x, 2) + Math.pow(this.y, 2));
	
		if(norm != 0){
			this.x /= norm;
			this.y /= norm;
		}
	};
	
	this.scale = function(s){
		this.x = this.x * s;
		this.y = this.y * s;
	};
	
	// returns the scalar product of the vector with another vector
	// gets a vector
	this.scalarProduct1v = function(v){
		result = this.x * v.x + this.y * v.y;
		return result;
	};
	
	// returns the scalar product of the vector with another vector
	// gets two coordinates	
	this.scalarProduct2c = function(x, y){
		result = this.x * x + this.y * y;
		return result;
	};
	
	this.subtract = function(v){
		var nx = this.x - v.x;
		var ny = this.y - v.y;
		result = new Vector(nx, ny);
		return result;
	};
	
	this.add = function(v){
		var nx = this.x + v.x;
		var ny = this.y + v.y;
		result = new Vector(nx, ny);
		return result;
	};
}