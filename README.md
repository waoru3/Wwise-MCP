<p align="center">
  <img src="images/wwise_mcp_banner.png" width="100%" />
</p>
  
# Wwise-MCP (Model Context Protocol for Wwise)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Wwise](https://img.shields.io/badge/Wwise%20-2024.1%2B-blue.svg)](https://www.audiokinetic.com/en/wwise/)
[![GitHub release](https://img.shields.io/github/v/release/BilkentAudio/Wwise-MCP)](https://github.com/BilkentAudio/Wwise-MCP/releases)
[![Status](https://img.shields.io/badge/Status-Experimental-red)]()

</div>

Wwise-MCP is a Model Context Protocol (MCP) server that enables large language models (LLMs) to interact with the Wwise Authoring application. It exposes a set of tools built on a custom Python WAAPI library, allowing MCP clients such as Claude or Cursor to automate and compose complex, multi-step Wwise workflows.

[Watch the demo and installation guide on YouTube](https://www.youtube.com/watch?v=d7bVT4yrdmI)

# ⚠️ Experimental Notice

This project is currently in an **EXPERIMENTAL** state. 
It is still under active development and should not be used with Wwise projects intended for production at the moment. Please keep in mind:
- Breaking changes may occur without warning
- Features may be incomplete or unstable
- Documentation may be outdated or missing
- Production use is not recommended at this time
  
# Installation

## Prerequisites
- Install [Claude Desktop](https://www.claude.com/download) or [Cursor](https://cursor.com/download) or any MCP compatible AI platform
- Install [Wwise 2024.1+](https://www.audiokinetic.com/en/download/)
- Install the latest [Wwise-MCP.zip](https://github.com/BilkentAudio/Wwise-MCP/releases)

## Setup
- Once you have the above 3 components installed, configure your MCP Client's (i.e Claude's or Cursor's) json file to include the Wwise-MCP application.
```json
 {
    "mcpServers":
    {
         "wwise-mcp":
         {
           "command": "C:\\Your\\PathTo\\Wwise-MCP.exe",
           "args": []
         }
    }
 }
 ```
  https://github.com/user-attachments/assets/98141541-8286-4c1d-98f5-2052364bf4bb
- Refer to the [setup page](https://github.com/BilkentAudio/Wwise-MCP/tree/main/docs/setup) for detailed instructions on setting up with [Claude](https://github.com/BilkentAudio/Wwise-MCP/blob/main/docs/setup/Claude/ClaudeSetup.md) and [Cursor](https://github.com/BilkentAudio/Wwise-MCP/blob/main/docs/setup/Cursor/CursorSetup.md)

# ⚠️ macOS Security Blocker
- On macOS, you will most likely face an error on your first launch of Wwise-MCP after setup due to macOS security.
- To bypass it, open **Terminal** then run `chmod +x "/YourPathTo/Wwise-MCP-v1-0/macOS/Apple Silicon/Wwise-MCP"`
- Make sure to configure the above command to the path where you store your **version (Intel or Silicon)** of Wwise-MCP
- Relaunch your MCP Client (i.e Claude) once more. It may fail again. Navigate to **Privacy & Security** in **System Settings**
- There should be a `"Wwise-MCP" was blocked to protect your Mac` message. Select **Allow Anyway**.
- Relaunch your MCP Client (i.e Claude).

# Quickstart

1. **Connect to your Wwise project**  
   Always start with a prompt akin to **“Connect to my Wwise project”**.  
   This attaches Wwise-MCP to your currently open Wwise session.

2. **Let your MCP Client (i.e Claude) “see” your project structure**  
   Use the **“Resolve parent path”** command.  
   This builds an index of objects under a given Wwise path so Claude can cache and navigate your project by paths.
   A good place to begin is one of Wwise’s top-level roots, for example:
   - `\Actor-Mixer Hierarchy`, `\Containers (Wwise 2025)` 
   - `\Events`
   - `\Switches`, `\States`, `\Game Parameters`
  
   Example prompt:  
   > Resolve all path relationships in actor mixer.

3. Before using any game object–related prompts (e.g. “Post X event on 5 new game objects and spread them around 500 units from the origin”), make sure you’ve enabled “Start Capture” (red when enabled) in Wwise’s Game Object view.
   > <img src="https://github.com/BilkentAudio/Wwise-MCP/blob/main/images/quickstart/Quickstart_GameObject.png" alt="Quickstart_GameObject" width="1000">

# Features
- **Wwise Session Connection**: Connects to the active Wwise session so the agent can issue WAAPI commands to the appropriate wwise session.
- **Hierarchy Indexing**: Scans a parent path and builds a path-first index of the subtree for fast lookup and navigation.
- **Object Creation & Organization**: Creates actor-mixers, containers, buses, work units, soundbanks, folders, and more under specified parent paths, and can move or rename them in batches.
- **Event Authoring**: Creates multiple Wwise events in one batch from source objects and parent paths, and lists all existing event names.
- **Game Object Management**: Creates, moves, and unregisters game objects in batches, with full 3D positioning support and a global fallback object.
- **RTPC / Switch / State Setup**: Batch-creates RTPCs, switch groups, switches, state groups, and states, and exposes helpers to list and set them at runtime.
- **Audio Import & Discovery**: Imports folders of audio into Wwise under a target parent, and lists all audio files under a given file-system path.
- **Soundbank Configuration & Build**: Includes selected objects in soundbanks and generates soundbanks for specified platforms and languages using project metadata.
- **Runtime Audio Control**: Posts events with optional delays, sets RTPC ramps, switches and states, moves game objects over time, and stops all sounds in the captured session.
- **Layout & Property Utilities**: Toggles Wwise layouts, sets object properties by path, retrieves the current selection, and lists valid property names and value types.
- Refer to [Tools](https://github.com/BilkentAudio/Wwise-MCP/blob/main/docs/tools/ToolList.md) page for detailed explanation of each functionality.

# Directory Structure

- **docs/** - Wwise-MCP documentation
  - **setup/** - Instructions for installing and configuring Wwise-MCP and MCP clients ([Claude](https://github.com/BilkentAudio/Wwise-MCP/blob/main/docs/setup/Claude/ClaudeSetup.md) & [Cursor](https://github.com/BilkentAudio/Wwise-MCP/blob/main/docs/setup/Cursor/CursorSetup.md))
  - **tools/** - A list of all functionalities and example prompts

- **app/** - Python server. Instructions for setting up Python environment can be found in the [README](https://github.com/BilkentAudio/Wwise-MCP/blob/main/app/README.md)
  - **scripts/** - Python application source code 


# Developers
- Wwise-MCP consists of 3 primary Python modules
- The main entry point is wwise_mcp.py
- Be sure you are using python version 3.13+
- More info can be found [here](https://github.com/BilkentAudio/Wwise-MCP/blob/main/app/README.md)

# License
Apache 

# Author
Built by Bilkent Samsurya<br> 

Audio Programmer | AI-integrated Audio Tools | Wwise & Unreal Specialist

[Website](https://bilkentsam.com) •
[LinkedIn](https://www.linkedin.com/in/bilkentsamsurya) •
[Twitter/X](https://twitter.com/BilkentAudio)

# Feedback/Questions
Feel free to reach out to me at bilkentaudiodev@gmail.com

## Profiler tools (fork-divergent)

Ten WAAPI Profiler endpoints exposed for runtime voice-chain inspection,
Effect plug-in chain verification, and `.prof` capture export. All require
Wwise Authoring 2024.1+ running. The endpoints are restricted to
`userInterface` / `commandLine` execution contexts per the WAAPI schemas
(a Wwise Authoring context restriction, not a visible-window requirement).

**Critical prerequisite for voice contribution inspection:** call
`profiler_enable_data(['voices', 'voiceInspector'])` once per session
before any `profiler_get_voice_contributions` call. Without
`voiceInspector` the returned tree is empty.

| Command | Purpose |
|---|---|
| `profiler_start_capture()` | Begin capture |
| `profiler_stop_capture()` | End capture |
| `profiler_get_cursor_time(cursor='capture')` | Read 'capture' or 'user' cursor (ms) |
| `profiler_enable_data(data_types)` | Toggle Profiler data types (incl. `voiceInspector`) |
| `profiler_get_voices(time='capture', *, voice_pipeline_id=None, return_fields=None, timeout=5.0)` | Voices live at `time` with filterable return fields |
| `profiler_get_voice_contributions(voice_pipeline_id, *, time='capture', busses_pipeline_id=None, timeout=5.0)` | Volume/LPF/HPF contribution tree for one voice path |
| `profiler_get_audio_objects(time='capture', *, bus_pipeline_id=None, return_fields=None, timeout=5.0)` | Post-mix Audio Objects incl. `effectPluginName` + RMS/peak meters |
| `profiler_get_busses(time='capture', *, bus_pipeline_id=None, return_fields=None, timeout=5.0)` | Busses live at `time` |
| `profiler_get_rtpcs(time='capture', *, timeout=5.0)` | Active RTPCs (Game Parameters / LFO / Time / Envelope / MIDI) |
| `profiler_save_capture(file_path, *, timeout=5.0)` | Save current capture to `.prof` (absolute path) |

URI correction: the save endpoint is `ak.wwise.core.profiler.saveCapture`,
not `saveProfilerCapture` (which does not exist in the 2024.1 WAAPI index).
