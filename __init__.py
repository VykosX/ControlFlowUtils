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
    "Cycle": ControlFlowUtils.Cycle,
    "CycleEnd": ControlFlowUtils.CycleEnd,
    "CycleStart": ControlFlowUtils.CycleStart,
    "DataMonitor": ControlFlowUtils.DataMonitor,
    "CheckpointSelector": ControlFlowUtils.CheckpointSelector,
    "LoraSelector": ControlFlowUtils.LoraSelector,
    "VAESelector": ControlFlowUtils.VAESelector,
    "NullInput": ControlFlowUtils.NullInput,
    "NullOutput": ControlFlowUtils.NullOutput,
    "ImageResolutionAdjust": ControlFlowUtils.ImageResolutionAdjust,
    "ReadTextFile": ControlFlowUtils.ReadTextFile,
    "SaveTextFile": ControlFlowUtils.SaveTextFile,
    "Wait": ControlFlowUtils.DelayExecution,
    "GarbageCollector": ControlFlowUtils.GarbageCollector,
    "UnloadModels": ControlFlowUtils.UnloadModels,
    "IfConditionSelector": ControlFlowUtils.IfConditionSelector,
    "UniversalSwitch": ControlFlowUtils.UniversalSwitch,
    "HaltExecution": ControlFlowUtils.HaltExecution,
    "MemoryStorage": ControlFlowUtils.MemoryStorage
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Cycle": "🔄 Cycle",
    "CycleEnd": "⏪ Cycle End",
    "CycleStart": "⏩ Cycle Start",
    "DataMonitor": "👁‍🗨Data Monitor/Generator",
    "CheckpointSelector": "🏁 Checkpoint Selector",
    "LoraSelector": "🏴 LoRA Selector",
    "VAESelector": "🚩 VAE Selector",
    "NullInput": "🟦 Null Input",
    "NullOutput": "🔵 Null Output",
    "ImageResolutionAdjust": "🌄 Image Resolution Adjust",
    "ReadTextFile": "📄 Read Text File",
    "SaveTextFile": "💾 Save Text File",
    "Wait": "⌛ Wait",
    "GarbageCollector": "🗑 Garbage Collector",
    "UnloadModels": "❌ Unload Models",
    "IfConditionSelector": "🔀IF (Condition Selector)",
    "UniversalSwitch": "💠 Universal Switch",
    "HaltExecution": "🛑 Halt Execution",
    "MemoryStorage": "🗒️ Memory Storage",
}