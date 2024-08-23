import { app } from "../../scripts/app.js";
import { api } from "../../../scripts/api.js";
import { $el } from "../../scripts/ui.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

// Let it be known that I barely know what I'm doing with Javascript, so any help would be greatly appreciated
//  ~ VykosX

app.registerExtension({
	name: "ControlFlowUtils",
	
    async setup(app) {
		
		api.addEventListener("VykosX.UnloadModels", ( {node_id} ) => {
			
			console.log ( "Attempting to unload models..." );
			
			fetch("/free", {
				method: "POST",
				body: JSON.stringify({ unload_models: true }),
				headers: { "Content-Type": "application/json" },
			  }).catch((error) => {
				console.error(error);
			  });
					
		});
		
		api.addEventListener("VykosX.ClearQueue", ( {} ) => {

			console.log ("Clearing queue...");
			
			//app.ui.queue.clear();
			
		});
		
		
  },
  
  beforeRegisterNodeDef(nodeType, nodeData, app) {
	  
    if (nodeData.name === "DataMonitor") {
      const onNodeCreated = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function () {
        const r = onNodeCreated?.apply(this, arguments);
        return r;
      };

      const onExecuted = nodeType.prototype.onExecuted;
      nodeType.prototype.onExecuted = function (message) {
        onExecuted?.apply(this, arguments);

        for (const widget of this.widgets) {
          if (widget.type === "customtext") {
            widget.value = message.text.join("");
          }
        }

        this.onResize?.(this.size);
      };
    }
  },
  
});
