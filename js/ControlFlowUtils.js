import { app } from "../../scripts/app.js";
import { api } from "../../../scripts/api.js";
import { $el } from "../../scripts/ui.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

// Let it be known that I barely know what I'm doing with Javascript, so any help would be greatly appreciated
//	~ VykosX

const stopAll = async function(interrupt){
	document.querySelector("div.comfyui-queue-mode input:first-child").click();
	
	await fetch("/queue", {
		method: "POST",
		headers: {
			"Accept": "application/json",
			"Content-Type": "application/json",
		  },
		body: JSON.stringify({ clear: true }),
	   }).catch(e => console.log("exception while clearing queue:",e));
	   
	   if (interrupt) {
		   
			console.log ("Interrupting prompt...")
			
		   await fetch("/api/interrupt", {
			  method: "POST",
		}).catch(e => console.log("exception while interrupting prompt:",e));
	   }
};
			
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
		
		api.addEventListener("VykosX.ClearQueue", ({detail}) => {

			console.log ("Clearing queue...");
			let { interrupt } = detail;
			stopAll(interrupt);
			
		});

  },
  
  beforeRegisterNodeDef(nodeType, nodeData, app) {
	
	//console.log ("NODE FOUND:",nodeData.name,nodeData.id);
	
	if (nodeData.name === "HaltExecution") {
			
		const onNodeCreated = nodeType.prototype.onNodeCreated;
		nodeType.prototype.onNodeCreated = function () {
			onNodeCreated ? onNodeCreated.apply(this, []) : undefined;
			this.showValueWidget = ComfyWidgets["STRING"](this, "Status", ["STRING", { multiline: true }], app).widget;
			this.showValueWidget.inputEl.readOnly = true;
			this.showValueWidget.serializeValue = async (node, index) => {
				return "";
			}
		};
		
		const onExecuted = nodeType.prototype.onExecuted;
		nodeType.prototype.onExecuted = function (message) {
			onExecuted === null || onExecuted === void 0 ? void 0 : onExecuted.apply(this, [message]);
			this.showValueWidget.value = message.text.join("");
		};
	}
	
	 if (nodeData.name === "MemoryStorage") {
			
		const onNodeCreated = nodeType.prototype.onNodeCreated;
		nodeType.prototype.onNodeCreated = function () {
			onNodeCreated ? onNodeCreated.apply(this, []) : undefined;
			this.showValueWidget = ComfyWidgets["STRING"](this, "Value", ["STRING", { multiline: true }], app).widget;
			this.showValueWidget.inputEl.readOnly = true;
			this.showValueWidget.serializeValue = async (node, index) => {
				return "";
			}
		};
		
		const onExecuted = nodeType.prototype.onExecuted;
		nodeType.prototype.onExecuted = function (message) {
			onExecuted === null || onExecuted === void 0 ? void 0 : onExecuted.apply(this, [message]);
			this.showValueWidget.value = "Value: " + message.text.join("");
		};
	}
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

// ALL SUBSEQUENT CODE BELONGS TO PYTHONGOSSSSSS AND HIS EXCELLENT COMFYUI-CUSTOM-SCRIPTS PACKAGE!

const PathHelper = {
	get(obj, path) {
		if (typeof path !== "string") {
			// Hardcoded value
			return path;
		}

		if (path[0] === '"' && path[path.length - 1] === '"') {
			// Hardcoded string
			return JSON.parse(path);
		}

		// Evaluate the path
		path = path.split(".").filter(Boolean);
		for (const p of path) {
			const k = isNaN(+p) ? p : +p;
			obj = obj[k];
		}

		return obj;
	},
	set(obj, path, value) {
		// https://stackoverflow.com/a/54733755
		if (Object(obj) !== obj) return obj; // When obj is not an object
		// If not yet an array, get the keys from the string-path
		if (!Array.isArray(path)) path = path.toString().match(/[^.[\]]+/g) || [];
		path.slice(0, -1).reduce(
			(
				a,
				c,
				i // Iterate all of them except the last one
			) =>
				Object(a[c]) === a[c] // Does the key exist and is its value an object?
					? // Yes: then follow that path
					  a[c]
					: // No: create the key. Is the next key a potential array-index?
					  (a[c] =
							Math.abs(path[i + 1]) >> 0 === +path[i + 1]
								? [] // Yes: assign a new array object
								: {}), // No: assign a new plain object
			obj
		)[path[path.length - 1]] = value; // Finally assign the value to the last key
		return obj; // Return the top-level object to allow chaining
	},
};

/***
	@typedef { {
		left: string;
		op: "eq" | "ne",
		right: string
	} } IfCondition 

	@typedef { {
		type: "if",
		condition: Array<IfCondition>,
		true?: Array<BindingCallback>,
		false?: Array<BindingCallback>
	} } IfCallback

	@typedef { {
		type: "fetch",
		url: string,
		then: Array<BindingCallback>
	} } FetchCallback 

	@typedef { {
		type: "set",
		target: string,
		value: string
	} } SetCallback 

	@typedef { {
		type: "validate-combo",
	} } ValidateComboCallback 

	@typedef { IfCallback | FetchCallback | SetCallback | ValidateComboCallback } BindingCallback 

	@typedef { {
		source: string,
		callback: Array<BindingCallback>
	} } Binding 
***/

/**
 * @param {IfCondition} condition
 */
function evaluateCondition(condition, state) {
	const left = PathHelper.get(state, condition.left);
	const right = PathHelper.get(state, condition.right);

	let r;
	if (condition.op === "eq") {
		r = left === right;
	} else {
		r = left !== right;
	}

	return r;
}

/**
 * @type { Record<BindingCallback["type"], (cb: any, state: Record<string, any>) => Promise<void>> }
 */
const callbacks = {
	/**
	 * @param {IfCallback} cb
	 */
	async if(cb, state) {
		// For now only support ANDs
		let success = true;
		for (const condition of cb.condition) {
			const r = evaluateCondition(condition, state);
			if (!r) {
				success = false;
				break;
			}
		}

		for (const m of cb[success + ""] ?? []) {
			await invokeCallback(m, state);
		}
	},
	/**
	 * @param {FetchCallback} cb
	 */
	async fetch(cb, state) {
		const url = cb.url.replace(/\{([^\}]+)\}/g, (m, v) => {
			return PathHelper.get(state, v);
		});
		const res = await (await api.fetchApi(url)).json();
		state["$result"] = res;
		for (const m of cb.then) {
			await invokeCallback(m, state);
		}
	},
	/**
	 * @param {SetCallback} cb
	 */
	async set(cb, state) {
		const value = PathHelper.get(state, cb.value);
		PathHelper.set(state, cb.target, value);
	},
	async "validate-combo"(cb, state) {
		const w = state["$this"];
		const valid = w.options.values.includes(w.value);
		if (!valid) {
			w.value = w.options.values[0];
		}
	},
};

async function invokeCallback(callback, state) {
	if (callback.type in callbacks) {
		// @ts-ignore
		await callbacks[callback.type](callback, state);
	} 
}

app.registerExtension({
	name: "vykosx.binding",
	beforeRegisterNodeDef(node, nodeData) {
		const hasBinding = (v) => {
			if (!v) return false;
			return Object.values(v).find((c) => c[1]?.["vykosx.binding"]);
		};
		const inputs = { ...nodeData.input?.required, ...nodeData.input?.optional };
		if (hasBinding(inputs)) {
			const onAdded = node.prototype.onAdded;
			node.prototype.onAdded = function () {
				const r = onAdded?.apply(this, arguments);

				for (const widget of this.widgets || []) {
					const bindings = inputs[widget.name][1]?.["vykosx.binding"];
					if (!bindings) continue;

					for (const binding of bindings) {
						
						const source = this.widgets.find((w) => w.name === binding.source);
						if (!source) {
					
							continue;
						}

						let lastValue;
						async function valueChanged() {
							const state = {
								$this: widget,
								$source: source,
								$node: node,
							};

							for (const callback of binding.callback) {
								await invokeCallback(callback, state);
							}

							app.graph.setDirtyCanvas(true, false);
						}

						const cb = source.callback;
						source.callback = function () {
							const v = cb?.apply(this, arguments) ?? source.value;
							if (v !== lastValue) {
								lastValue = v;
								valueChanged();
							}
							return v;
						};

						lastValue = source.value;
						valueChanged();
					}
				}

				return r;
			};
		}
	},
});

