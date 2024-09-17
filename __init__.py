"""
@Author: VykosX
@Description: ControlFlowUtils Initializer
@Title: ControlFlowUtils
@Nickname: ControlFlowUtils
"""

WEB_DIRECTORY = "js"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

from . import Types
from . import ControlFlowUtils

NODE_CLASS_MAPPINGS = { 
	"DataMonitor": ControlFlowUtils.DataMonitor,
	"MemoryStorage": ControlFlowUtils.MemoryStorage,
	"StringOperation": ControlFlowUtils.StringOperation,
	"IfConditionSelector": ControlFlowUtils.IfConditionSelector,
	"UniversalSwitch": ControlFlowUtils.UniversalSwitch,
	"LoopOpen": ControlFlowUtils.LoopOpen,
	"LoopClose": ControlFlowUtils.LoopClose,
	"Cycle": ControlFlowUtils.Cycle,
	"CycleContinue": ControlFlowUtils.CycleContinue,
	"CycleEnd": ControlFlowUtils.CycleEnd,
	"NullOutput": ControlFlowUtils.NullOutput,
	"NullInput": ControlFlowUtils.NullInput,
	"SimpleToggle": ControlFlowUtils.SimpleToggle,
	"InvertCondition": ControlFlowUtils.InvertCondition,
	"Wait": ControlFlowUtils.DelayExecution,
	"HaltExecution": ControlFlowUtils.HaltExecution,
	"GarbageCollector": ControlFlowUtils.GarbageCollector,
	"UnloadModels": ControlFlowUtils.UnloadModels,
	"ImageResolutionAdjust": ControlFlowUtils.ImageResolutionAdjust,
	"FallbackImagePreviewer": ControlFlowUtils.FallbackImagePreviewer,
	"FallbackAnyBatch": ControlFlowUtils.FallbackAnyBatch,
	"FolderSearch": ControlFlowUtils.FolderSearch,
	"ReadTextFile": ControlFlowUtils.ReadTextFile,
	"SaveTextFile": ControlFlowUtils.SaveTextFile,
	"ModelSelector": ControlFlowUtils.ModelSelector,
	"LoraSelector": ControlFlowUtils.LoraSelector,
	"VAESelector": ControlFlowUtils.VAESelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
	"DataMonitor": "👁‍🗨Data Monitor ⁄ Generator ⁄ Converter",
	"MemoryStorage": "🗒️ Memory Storage",
	"StringOperation": "🔠 String ⁄ List Operations", 
	"IfConditionSelector": "🔀 IF (Condition Selector)",
	"UniversalSwitch": "💠 Universal Switch",
	"LoopOpen": "🔃 Loop Open",
	"LoopClose": "⏹️ Loop Close",
	"Cycle": "🔄 Cycle",
	"CycleContinue": "⏩ Cycle Continue",
	"CycleEnd": "⏪ Cycle Finish",
	"NullOutput": "🔵 Null Output",
	"NullInput": "🟦 Null Input",
	"SimpleToggle": "🔶 Simple Toggle",
	"InvertCondition": "🚫 NOT (Invert Condition)",
	"Wait": "⌛ Wait (Delay Execution)",
	"HaltExecution": "🛑 Halt Execution",
	"GarbageCollector": "🗑 Garbage Collector",
	"UnloadModels": "❌ Unload Models",
	"ImageResolutionAdjust": "🌄 Image Resolution Adjust",
	"FallbackImagePreviewer": "🖼️ Fallback Image Previewer",
	"FallbackAnyBatch": "🪟 Fallback Any Batch",
	"FolderSearch": "📁 Folder Search",
	"ReadTextFile": "📄 Read Text File",
	"SaveTextFile": "💾 Save Text File",
	"ModelSelector": "🏁 Model Selector",
	"LoraSelector": "🏴 LoRA Selector",
	"VAESelector": "🚩 VAE Selector",
}