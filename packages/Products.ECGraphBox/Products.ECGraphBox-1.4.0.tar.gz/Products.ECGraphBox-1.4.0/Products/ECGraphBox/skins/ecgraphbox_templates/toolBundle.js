/**
 * 
 */

function ToolBundle(name){
	this.name = name;
	this.omnipresentTools = new Array; // should hold all tools that are the hole time active (like the deleteTool)
	this.tools = new Array; // should hold all other tools 

	this.addOmnipresentTool = function(tool){
		this.omnipresentTools[tool.name] = tool;
	};
	
	this.addTool = function(tool){
		this.tools[tool.name] = tool;
	};
	
	this.omnipresentToolsUseOnClick = function(x, y, key){
		for(t in this.omnipresentTools){
			this.omnipresentTools[t].useOnClick(x, y, key);
		}
	};	
	
	this.omnipresentToolsUseOnDblClick = function(x, y, key){
		for(t in this.omnipresentTools){
			this.omnipresentTools[t].useOnDblClick(x, y, key);
		}
	};	
	
	this.omnipresentToolsUseOnMouseDown = function(x, y, key){
		for(t in this.omnipresentTools){
			this.omnipresentTools[t].useOnMouseDown(x, y, key);
		}
	};	
	
	this.omnipresentToolsUseOnDrag = function(x, y, dx, dy, key){
		for(t in this.omnipresentTools){
			this.omnipresentTools[t].useOnDrag(x, y, dx, dy, key);
		}
	};
	
	this.omnipresentToolsUseOnMouseUp = function(x, y, key){
		for(t in this.omnipresentTools){
			this.omnipresentTools[t].useOnMouseUp(x, y, key);
		}
	};
	
	this.omnipresentToolsUseOnScrol = function(x, y, key){
		for(t in this.omnipresentTools){
			this.omnipresentTools[t].useOnScrol(x, y, key);
		}
	};

	this.omnipresentToolsUseOnKeyDown = function(key){
		for(t in this.omnipresentTools){

			this.omnipresentTools[t].useOnKeyDown(key);
		}
	};
	
	this.omnipresentToolsUseOnKeyUp = function(key){
		for(t in this.omnipresentTools){
			this.omnipresentTools[t].useOnKeyUp(key);
		}
	};
}

