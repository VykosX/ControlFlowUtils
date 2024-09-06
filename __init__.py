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

any_type = Types.AnyType("*")

NODE_CLASS_MAPPINGS = { 
	"DataMonitor": ControlFlowUtils.DataMonitor,
	"MemoryStorage": ControlFlowUtils.MemoryStorage,
	"StringOperation": ControlFlowUtils.StringOperation,
	"IfConditionSelector": ControlFlowUtils.IfConditionSelector,
	"UniversalSwitch": ControlFlowUtils.UniversalSwitch,
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
	"FolderSearch": ControlFlowUtils.FolderSearch,
	"ReadTextFile": ControlFlowUtils.ReadTextFile,
	"SaveTextFile": ControlFlowUtils.SaveTextFile,
	"CheckpointSelector": ControlFlowUtils.CheckpointSelector,
	"LoraSelector": ControlFlowUtils.LoraSelector,
	"VAESelector": ControlFlowUtils.VAESelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
	"DataMonitor": "👁‍🗨Data Monitor ⁄ Generator ⁄ Converter",
	"MemoryStorage": "🗒️ Memory Storage",
	"StringOperation": "🔠 String ⁄ List Operations", 
	"IfConditionSelector": "🔀 IF (Condition Selector)",
	"UniversalSwitch": "💠 Universal Switch",
	"Cycle": "🔄 Cycle",
	"CycleContinue": "⏩ Cycle Continue",
	"CycleEnd": "⏪ Cycle End",
	"NullOutput": "🔵 Null Output",
	"NullInput": "🟦 Null Input",
	"SimpleToggle": "🔶 Simple Toggle",
	"InvertCondition": "🚫 NOT (Invert Condition)",
	"Wait": "⌛ Wait",
	"HaltExecution": "🛑 Halt Execution",
	"GarbageCollector": "🗑 Garbage Collector",
	"UnloadModels": "❌ Unload Models",
	"ImageResolutionAdjust": "🌄 Image Resolution Adjust",
	"FallbackImagePreviewer": "🖼️ Fallback Image Previewer",
	"FolderSearch": "📁 Folder Search",
	"ReadTextFile": "📄 Read Text File",
	"SaveTextFile": "💾 Save Text File",
	"CheckpointSelector": "🏁 Checkpoint Selector",
	"LoraSelector": "🏴 LoRA Selector",
	"VAESelector": "🚩 VAE Selector",
}