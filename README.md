# ControlFlowUtils
_Custom nodes for ComfyUI to enable flow control with advanced loops, conditional branching, logic operations and several other nifty utilities to enhance your ComfyUI workflows._

### **Latest Release:** v0.0.5 Alpha (2024-09-17 - "We got loops now boys!")
---

# Quick Demonstration

Here is a sanple showcasing Looping in-place to generate a batch of images with configurable variations using a single Ksampler:

https://github.com/user-attachments/assets/d069fcea-35de-479e-8550-6aae1f41beb4

And here is a clip that showcases an alternate means of achieving progressive generations, utilizing Cycles to to perform iterations across multiple prompts and generate imahes with different models and resolutions:

https://github.com/user-attachments/assets/4f3e7f3e-58fe-45f8-9e12-219e28860939

Furthermore, here is a simpler demonstration of iterative processing in ComfyUI and preserving values across multiple queues with the nodes in this pack:

https://github.com/user-attachments/assets/c7cddfb5-6881-4fe8-858d-a644fb6ea9a3

---

# Included Nodes

These are the nodes currently implemented by this pack along with a basic description of their functionalities so you can have an idea of what this pack currently includes.
For more detailed information, click on the title of each node which will direct you to its entry in [Wiki](https://github.com/VykosX/ControlFlowUtils/wiki/).

## [Loops](https://github.com/VykosX/ControlFlowUtils/wiki/ControlFlowUtils-%E2%80%90-In-Depth-Node-Explanation#Loop_Open)

![chrome_K0J0DEnr2Y](https://github.com/user-attachments/assets/054b3d9b-0ee1-4ba4-93ac-85d5f38b99d8)
![chrome_BnY0MztAoS](https://github.com/user-attachments/assets/ab6e733f-83c7-4dc7-87f6-7ca6eb7a8801)

These two nodes make it possible to implement in-place looping in ComfyUI by utilizing the new Execution Model, in a simple but very powerful way. With the power of Loops, you are able to repeatedly execute a specific subset of notes in your workflow and automate all sorts of complex tasks!

## [Cycles](https://github.com/VykosX/ControlFlowUtils/wiki/ControlFlowUtils-%E2%80%90-In-Depth-Node-Explanation#Cycle)
![Cycle](https://github.com/user-attachments/assets/fe8ec278-3ef2-4cf0-a35d-e05543ee9e81)
![Cycle Continue](https://github.com/user-attachments/assets/7f24e7ec-fde1-43dd-b0b6-fb43359e016c)
![Cycle End](https://github.com/user-attachments/assets/8769de88-488e-4da2-8056-605bf60b41ff)

These three nodes in conjunction allow you to implement progressive tasks in ComfyUI by caching data to be processed through multiple successive prompts. Here is what a basic loop chain looks like:

![Minimum Cycle](https://github.com/user-attachments/assets/dbdbf9a7-6111-435f-b379-ff1fb7754cbf)

Simply replace the Null Output node with the Data of your choice and it will be sent along with the loop allowing you to process any data iteratively.

## [If Selectors](https://github.com/VykosX/ControlFlowUtils/wiki/ControlFlowUtils-%E2%80%90-In-Depth-Node-Explanation#IF_Condition_Selector)

![If Selector Expanded](https://github.com/user-attachments/assets/c5d8055e-5c68-4724-ade3-c52deb0a4041)

This node allows you to easily test for any condition of your choice, including custom programmable conditions to divert execution based on how the condition evaluates to True or False, allowing for dynamic branching under ComfyUI's new execution model.

## [Universal Switches](https://github.com/VykosX/ControlFlowUtils/wiki/ControlFlowUtils-%E2%80%90-In-Depth-Node-Explanation#Universal_Switch)

![Universal Switch Expanded](https://github.com/user-attachments/assets/dd2cd4dd-dbdc-4a2e-be43-e5ae3eb91677)

This node allows you to map one or multiple inputs to one or multiple outputs according to a specific programmable criteria of your choice. The uses for this node are many but principal among them is forwarding different models, samplers, etc to different sections of your workflow based on specific logical conditions, allowing for branching and dynamic paths when used in conjunction with the [IF Selector](https://github.com/VykosX/ControlFlowUtils/wiki/ControlFlowUtils-%E2%80%90-In-Depth-Node-Explanation#IF_Condition_Selector) node.

## [Halt Execution](https://github.com/VykosX/ControlFlowUtils/wiki/ControlFlowUtils-%E2%80%90-In-Depth-Node-Explanation#Halt_Execution)

![Halt Execution](https://github.com/user-attachments/assets/283909f2-8113-425a-ab16-0b78d4b6285e)

This node allows you to instantly cancel the prompt or simply to block execution past a certain point based on a specific condition. You can use it to have your workflow execute different sections based on conditions, allowing for very complex behaviors to be implemented or to abort out of certain operations prematurely.

## [Memory Storages](https://github.com/VykosX/ControlFlowUtils/wiki/ControlFlowUtils-%E2%80%90-In-Depth-Node-Explanation#Memory_Storage)

![Memory Storage](https://github.com/user-attachments/assets/e1033807-cb93-4f27-b65a-a9e9d99be98f)

Persistent variables for your ComfyUI, that last throughout the entire lifespan of your workflow, no matter how many executions you make. You can save anything in these nodes, text, images, models, whatever you wish, and have them available anywhere, anytime in your workflow. Use these nodes to transmit data between different parts of the workflow or even to cache data to perform different operations on every execution. For instance, you could have a first pass which generates an image, then stores it in an Memory Storage, then another execution retrieves that image and refines and upscales it, and a third pass can compose it with a background of your choice. Really, your creativity is the only limiting factor with what is possible now that you can save data to your heart's content!

## [Model Unloader](https://github.com/VykosX/ControlFlowUtils/wiki/ControlFlowUtils-%E2%80%90-In-Depth-Node-Explanation#Unload_Models)

![Unload Models](https://github.com/user-attachments/assets/136249f6-682b-4dc2-a7eb-565480da87e1)

Running out of VRAM is a thing of the past! Now you don't need to rely on ComfyUI to properly manage its memory allocation in order to run complex workflows with heavy models such as Flux. You can take charge of your workflow and forcefully unload models when they're no longer in use. Your Workflow uses many different models at different stages but they don't all need to be loaded to VRAM at once? You'll certainly want this node!

## [Garbage Collector](https://github.com/VykosX/ControlFlowUtils/wiki/ControlFlowUtils-%E2%80%90-In-Depth-Node-Explanation#Garbage_Collector)

![Garbage Collector](https://github.com/user-attachments/assets/f217979c-4d71-41e0-abab-377d9d1ee98a)

This one is for everyone with low RAM (16gb or less) systems that struggle with too much memory usage and keep having to cache or resort to page files which drastically slows down execution. This node will force ComfyUI, Torch and Python to garbage collect, as well as allow for full RAM clearing on Windows, to free up as much memory as possible for your image generation!

## [Data Monitor](https://github.com/VykosX/ControlFlowUtils/wiki/ControlFlowUtils-%E2%80%90-In-Depth-Node-Explanation#Data_Monitor)

![Data Monitor Expanded](https://github.com/user-attachments/assets/eefd1ed9-db39-4f9f-93ba-a10637b5c87e)

Your one stop shop for all things Data in ComfyUI. This node allows you to visualize the output of any nodes with full passthrough support, serves as a convenient textbox while allowing you to pick the type of the data you wish to convert your output to, supports advanced features including the ability to run advanced mathematical evaluations, data generations, conditions and straight up any valid python code in a safe and non-exploitable manner, and much, much more! For a full list of supported features, consult the wiki entry.

## [String/List Operations](https://github.com/VykosX/ControlFlowUtils/wiki/ControlFlowUtils-%E2%80%90-In-Depth-Node-Explanation#String_List_Operations)

![StringList Operations Expanded](https://github.com/user-attachments/assets/e532b300-2709-4639-937c-7dc58b92947b)

This node has you covered for essentially any kind of basic string or list data manipulation you may need to perform in your workflow. It's surprising how often these come up and how many nodes from dozens of different packs are typically needed to handle them. Well, now you can have everything in a single easy-to-use node and greatly simplify your workflows in the process!

## [Wait (Delay Execution)](https://github.com/VykosX/ControlFlowUtils/wiki/ControlFlowUtils-%E2%80%90-In-Depth-Node-Explanation#Wait_Delay_Execution)

![Wait](https://github.com/user-attachments/assets/62a722b6-2802-45bc-ba07-b5a410323f7a)

This node simply allows you to wait a preconfigured amount of seconds (or milliseconds) in between nodes. You can use to ensure you have enough time to clear your memory, to save resources to disk, or even group a bunch of these with 0 delay together to simply pad out a workflow and manipulate its execution order when you have multiple concurrent branches. Just a nifty little addition that has come in handy many times for me!

## [Image Resolution Adjust](https://github.com/VykosX/ControlFlowUtils/wiki/ControlFlowUtils-%E2%80%90-In-Depth-Node-Explanation#Image_Resolution_Adjust)

![Image Resolution Adjust](https://github.com/user-attachments/assets/c500d87e-2211-4adf-9d71-ad235d060856)

This node will dynamically adjust the sizes of your images for any aspect ratio of your choice by performing the calculations to maintain the ratio for you for any given width, height or scaling factor. A real timesaver, now you don't need to do the math with a bunch of nodes anymore, and you can even change the scaling dynamically!

## [Fallback Image Previews](https://github.com/VykosX/ControlFlowUtils/wiki/ControlFlowUtils-%E2%80%90-In-Depth-Node-Explanation#Fallback_Image_Previewer)

![chrome_KqSzQKxzCm](https://github.com/user-attachments/assets/36519780-e157-458f-b75f-05b6574c3dfe)

Image Previews in ComfyUI have one giant flaw. If you don't pass a valid image to them at any point in your workflow, they will stop your workflow dead in its tracks. This makes conditional branching for generating images at different parts of the workflow a nightmare to deal with. Well no mare. This smart node will silently ignore empty or invalid images or even generate a placeholder image if it's not supplied with a valid image instead!

## [Fallback Any Batch](https://github.com/VykosX/ControlFlowUtils/wiki/ControlFlowUtils-%E2%80%90-In-Depth-Node-Explanation#Fallback_Any_Batch)

![chrome_lfpCxBecAM](https://github.com/user-attachments/assets/fceabc36-9e06-4fad-9077-0a8495096148)

This node allows you to create batches with any kind of Data, whether they're images, latents or even primitive data types like strings, tuples and lists. It will dynamically adjust to the data you give it and all the inputs are optional, so you don't have to worry about missing nodes. Invaluable to use within loops and cycles when you're trying to combine multiple image generations but the first iteration of the loop only has the one image!

## [Folder Search](https://github.com/VykosX/ControlFlowUtils/wiki/ControlFlowUtils-%E2%80%90-In-Depth-Node-Explanation#Folder_Search)

![Folder Search](https://github.com/user-attachments/assets/9d3b1380-7222-4703-9eb0-e27cdfa4bd50)

Easily retrieve a list of files within a folder of your choice for processing within ComfyUI with many options to customize the searching operation, such as filtering by extension or path masks, retrieving folders and files by name, relative, or absolute paths, retrieving one file at a time or all at once and much much more!

## [File Reading and Writing](https://github.com/VykosX/ControlFlowUtils/wiki/ControlFlowUtils-%E2%80%90-In-Depth-Node-Explanation#ReadTextFile)
![Read Text File](https://github.com/user-attachments/assets/74b2b9cf-2719-4028-95a1-b2e3b6f08cfa) ![Save Text File](https://github.com/user-attachments/assets/f1935699-7b79-4bb9-9fac-072e313877b8)
These nodes allow you to easily read and write to text files anywhere in your system, allowing you to easily load in wildcards, lora triggers, save logs of your workflow execution or anything else you may need!

## Other Convenient Nodes

Check the [Wiki]([#wiki](https://github.com/VykosX/ControlFlowUtils/wiki/ControlFlowUtils-%E2%80%90-In-Depth-Node-Explanation#Null_Input)) page for a full description of these nodes! Attached are the images for some of the more niche however very useful nodes this pack includes for convenience. It's all about the little things!

![chrome_Z3KjElmcW7](https://github.com/user-attachments/assets/3e519181-bf1b-4a4b-bea4-43fcec5cad4e)
![Null

https://github.com/user-attachments/assets/3c3062ae-8275-49f7-bd84-170e65d11e2e

 Output](https://github.com/user-attachments/assets/99656fa2-fd48-42f8-aefc-7e563038c2d2)
![Simple Toggle](https://github.com/user-attachments/assets/c2d76549-4a1a-4d6c-a226-a8047f0d36f5)
![NOT](https://github.com/user-attachments/assets/883d8ed9-5585-4622-ae0a-544ef690c326)
![Model Selector](https://github.com/user-attachments/assets/41ca172a-8dc2-40af-97c9-1a9442ac5cb4)
![LoRA Selector](https://github.com/user-attachments/assets/43286fcb-1f4a-4699-a9a3-11c322c61615)
![VAE Selector](https://github.com/user-attachments/assets/e4ba2666-3d95-4945-b178-6ae21bbe7a90)

That's it for now. If you have any [issues](https://github.com/VykosX/ControlFlowUtils/issues) or [feedback](https://github.com/VykosX/ControlFlowUtils/discussions) feel free to leave a comment in the relevant section of this Github!


This node will be regularly updated with new features that to improve your ComfyUI logic and dynamic workflows even more. Next up, we'll be looking at in-place loops.

Stay tuned and happy Comfy'ing!!

---

# KNOWN ISSUES

- Currently the Memory Storages are a little TOO persistent. They will persist even if you load a new workflow. Make sure to clean them via a __MEM__STORAGE__CLEAR operation before switching workflows or restart ComfyUI if you have issues from this. I'm exploring potential solutions and the next release should have a fix for this.
