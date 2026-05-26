## Tool List

Below is the list of commands exposed by Wwise-MCP, along with example prompts you can give to your MCP client (i.e Claude).

---

### `connect_to_wwise`

**Description**  
Reconnects Wwise-MCP to the currently active Wwise Authoring session.

**Example prompts**

- “Connect to my Wwise project.”
- “Reconnect to the current Wwise session.”
- “Make sure you’re connected to Wwise before doing anything else.”

---

### `resolve_all_path_relationships_in_parent`

**Description**  
Builds a path-first index of all objects under a given parent path (subtree). This lets Claude “see” and navigate the structure of your Wwise project via paths.

**Example prompts**

- “Resolve all path relationships in `\Actor-Mixer Hierarchy`.”
- “Index everything under `\Events` so you can browse my events.”
- “Resolve all path relationships in `\Actor-Mixer Hierarchy\Default Work Unit`.”

---

### `create_objects`

**Description**  
Creates one or more Wwise objects (Actor-Mixers, Buses, Containers, Sounds, Work Units, etc.) given their names, types, and parent paths. If no parent paths are provided, the command can re-use `prev_response_objects` from the last call. 

**Note**: this does not create events as there are more considerations to account for during event creation. Event creation is handled by the `create_events` function (below). 

**Example prompts**

- “Create three child objects called `AM_Footsteps`, `AM_Weapons`, and `AM_Ambience` as ActorMixers under `\Actor-Mixer Hierarchy\Default Work Unit`.”
- “Using the objects returned from the previous call, create a `RandomSequenceContainer` named `UI_Clicks_Random` under each of them.”
- “Create a new bus called `SFX_Master` under `\Master-Mixer Hierarchy\Default Work Unit`.”

---

### `create_events`

**Description**  
Creates multiple Wwise Events in one batch from lists of source objects, destination parent paths, event types, and event names.

**Example prompts**

- “Create a `Play` event called `Play_Footsteps_Grass` for `\Actor-Mixer Hierarchy\Characters\Player\Footsteps_Grass` under `\Events\Default Work Unit\Footsteps`.”
- “Create four `Play` events for these sources: [list paths], and put all of them under `\Events\Default Work Unit\Weapons`.”
- “Batch-create ‘Play’ events for all the sounds you just listed and place them under `\Events\Default Work Unit\Imported`.”

---

### `create_game_objects`

**Description**  
Creates multiple game objects at once in the Wwise sound engine, optionally with initial 3D positions. 

**Note**: Ensure **Start Capture** is toggled before using this command.

**Example prompts**

- “Create five game objects named `RainEmitter_01` through `RainEmitter_05` around the origin at random positions within a radius of 10 units.”
- “Create a game object called `Player` at position (0, 0, 0) and another called `Campfire` at (10, 0, 2).”
- “Create three game objects for birds, spaced evenly along the X-axis from -5 to 5 at Y=0, Z=2.”

---

### `create_rtpcs`

**Description**  
Creates RTPCs in one batch under `\Game Parameters`. You can specify names, parent paths, and min/max ranges. If min/max aren’t specified, assume `0.0` to `100.0`.

**Example prompts**

- “Create RTPCs `Player_Health`, `Player_Stamina`, and `Environment_Density` under `\Game Parameters\Gameplay` with a range of 0 to 100.”
- “Create an RTPC named `Music_Intensity` under `\Game Parameters\Music` from 0.0 to 1.0.”
- “Batch-create RTPCs for `WindSpeed` and `RainIntensity` under `\Game Parameters\Weather` with default ranges.”

---

### `create_switch_groups`

**Description**  
Creates switch groups under `\Switches`. The group must exist before creating its switches.

**Example prompts**

- “Create a switch group `Footstep_Surface` under `\Switches\Default Work Unit`.”
- “Create switch groups `Weather_Type` and `TimeOfDay` under `\Switches\Environment`.”
- “Set up a switch group called `Weapon_Type` under `\Switches\Gameplay`.”

---

### `create_switches`

**Description**  
Creates switches under an existing switch group (whose path should start with `\Switches`).

**Example prompts**

- “Under `\Switches\Default Work Unit\Footstep_Surface`, create switches `Grass`, `Dirt`, `Stone`, and `Metal`.”
- “Add switches `Rain`, `Snow`, and `Wind` to the `Weather_Type` switch group.”
- “Create switches `Day`, `Night`, and `Dusk` under the `TimeOfDay` switch group.”

---

### `create_state_groups`

**Description**  
Creates state groups under `\States`. The group must exist before its child states.

**Example prompts**

- “Create a state group called `Game_State` under `\States\Default Work Unit`.”
- “Create state groups `Music_Mode` and `Combat_State` under `\States\Gameplay`.”
- “Add a state group `UI_Focus` under `\States\UI`.”

---

### `create_states`

**Description**  
Creates states under an existing state group (path should start with `\States` and represent the parent state group).

**Example prompts**

- “Under `\States\Default Work Unit\Game_State`, create states `MainMenu`, `Exploration`, and `Combat`.”
- “Add states `Calm`, `Tension`, and `BossFight` to the `Music_Mode` state group.”
- “Under `\States\UI\UI_Focus`, create states `Inventory`, `Map`, and `Dialogue`.”

---

### `move_object_by_path`

**Description**  
Moves a Wwise object from one path to another parent path. All child objects move with it.

**Example prompts**

- “Move `\Actor-Mixer Hierarchy\Default Work Unit\Temp` to `\Actor-Mixer Hierarchy\Default Work Unit\Archive`.”
- “Move the sound `\Actor-Mixer Hierarchy\SFX\Footsteps\Footstep_Stone` to `\Actor-Mixer Hierarchy\SFX\Footsteps\Legacy`.”
- “Re-parent all assets under `\Events\Old` to be under `\Events\Default Work Unit\Deprecated`.”

---

### `rename_objects`

**Description**  
Renames one or more Wwise objects, either by providing their paths or by using the most recent `prev_response_objects`.

**Example prompts**

- “Rename `\Actor-Mixer Hierarchy\Default Work Unit\AM_Temp` to `AM_Environment`.”
- “For the objects you just created, append `_Test` to each of their names.”
- “Rename these paths [list] to [new names] accordingly.”

---

### `import_audio_files`

**Description**  
Imports all audio files under a given file system folder (e.g. `C:\Audio`) into a specified Wwise parent object or path.

**Example prompts**

- “Import all audio files under `C:\GameAudio\Footsteps\Grass` into `\Actor-Mixer Hierarchy\Default Work Unit\Footsteps\Grass`.”
- **Note**: You do not have to specify the destination path if Wwise-MCP already resolved path relationships for that given path. "Import all audio files under `C:\GameAudio\Footsteps\Grass` into Grass container in footstesps under actor mixer."

---

### `list_all_event_names`

**Description**  
Lists the names of all events in the Wwise project.

**Example prompts**

- “List all event names in this project.”
- “Show me all existing Wwise events.”
- “Print a list of all events so we can reuse them instead of creating new ones.”

---

### `list_all_rtpc_names`

**Description**  
Lists the names of all RTPCs in the Wwise project.

**Example prompts**

- “List all RTPC names.”
- “Show me every RTPC currently defined in the project.”
- “List all RTPCs so I can decide which one to use for player health.”

---

### `list_all_switchgroups_and_switches`

**Description**  
Lists all switch groups and their switches, grouped in a dictionary-like structure.

**Example prompts**

- “List all switch groups and their switches.”
- “Show me a mapping of every switch group to its switches.”
- “Print all switch groups and the switches they contain.”

---

### `list_all_stategroups_and_states`

**Description**  
Lists all state groups and their states, grouped in a dictionary-like structure.

**Example prompts**

- “List all state groups and their states.”
- “Show me all state groups with the states inside each.”
- “Print a mapping of state groups to states.”

---

### `list_all_game_objects_in_wwise`

**Description**  
Lists all game objects currently registered in the Wwise session.

**Example prompts**

- “List all game objects in the current Wwise session.”
- “Show me all active game objects so I know what I can post events on.”
- “Print all registered game objects and their IDs.”

---

### `post_event`

**Description**  
Posts a Wwise event by name on a specified game object after an optional delay (milliseconds).  
If no game object is given, it posts to the global `Global` game object. If the game object doesn’t exist, it is created automatically.

**Arguments**

- `event_name: str` — Wwise event name to post.
- `game_obj_name: str` — Target game object name (use `"Global"` for 2D / ambience events).
- `delay_ms: int` — Delay before the soundengine posts the event. `0` means post immediately.
- `wait: bool = False` — Reply mode. `False` (default) fire-and-forget: returns as soon as the dispatcher enqueues the call. `True` synchronous: blocks on the WAAPI reply queue, which is useful for serializing a batch of posts and avoiding socket saturation under heavy load. When combined with `delay_ms > 0`, the reply timeout is auto-extended to cover the scheduled future dispatch, so delayed synchronous posts do not spuriously time out.

**Example prompts**

- “Post the `Play_Ambience_Forest` event on the `Global` game object immediately.”
- “Post `Play_Footsteps_Grass` on the `Player` game object with a delay of 500 ms.”
- “Trigger `Stop_All_Music` on `Global` right now.”
- “Post `Play_Stinger` on `Global` and wait for the WAAPI reply before issuing the next event (`wait=True`).”

---

### `set_rtpc`

**Description**  
Sets an RTPC value on a game object over a duration (in ms), from a start value to an end value.  
If no game object is given, applies the RTPC to the `Global` game object.

**Example prompts**

- “Set the RTPC `Music_Intensity` from 0 to 100 over 10 seconds on `Global`.”
- “Ramp `WindSpeed` from 20 to 80 over 5 seconds on the `Player` game object.”
- “Set `Player_Health` RTPC to 25 instantly on `Player`.”

---

### `set_state`

**Description**  
Sets a state by specifying the state group and state names.

**Example prompts**

- “Set `Game_State` to `Exploration`.”
- “Switch `Music_Mode` to `BossFight`.”
- “Set the state group `UI_Focus` to `Inventory`.”

---

### `set_switch`

**Description**  
Sets a switch by specifying the switch group and switch names, usually on a given game object.

**Example prompts**

- “On `Player`, set the switch `Footstep_Surface` to `Grass`.”
- “Set `Weather_Type` to `Rain` on `Global`.”
- “Change `TimeOfDay` to `Night` for the `Player` game object.”

---

### `move_game_obj`

**Description**  
Moves a game object from a start position to an end position over a duration (ms).  
If the game object doesn’t exist, it will be created.

**Example prompts**

- “Move the `Player` game object from (0, 0, 0) to (10, 0, 0) over 3 seconds.”
- “Animate `Drone_01` from (0, 5, 2) to (20, 5, 2) across 10 seconds.”
- “Create a `TempSource` game object at (0, 0, 2) and move it to (0, 0, 20) over 5 seconds.”

---

### `stop_all_sounds`

**Description**  
Stops all sounds on all game objects in the captured session.

**Example prompts**

- “Stop all sounds currently playing.”
- “Immediately silence everything in this Wwise session.”
- “Stop all audio on all game objects.”

---

### `include_in_soundbank`

**Description**  
Includes specified objects (events, work units, folders, etc.) into a soundbank by path.

**Arguments**

- `include_paths: list[str]` — Wwise object paths to include in the soundbank.
- `soundbank_path: str` — Target soundbank path.
- `filter: list[str] | None = None` — Optional inclusion filter. Allowed values: `"events"`, `"structures"`, `"media"`. At most 3 entries, each value may appear only once (per the WAAPI `setInclusions` schema). When omitted, defaults to `["events", "structures"]`, which maps to `Filter=3` in the resulting `.wwu`. Pass `["events", "structures", "media"]` (`Filter=7`) when audio media must travel with the SoundBank instead of being streamed.

**Example prompts**

- “Include `\Events\Default Work Unit\Footsteps` in the soundbank `\SoundBanks\Default Work Unit\Footsteps_SoundBank`.”
- “Add all events under `\Events\Weapons` to `\SoundBanks\Default Work Unit\Weapons_SB`.”
- “Include these event paths [list] in the `MainGame` soundbank.”
- “Include `\Events\Default Work Unit\Music` in `\SoundBanks\Default Work Unit\Music_SB` with media baked in (`filter=['events','structures','media']`).”

---

### `generate_soundbanks`

**Description**  
Generates soundbanks given lists of soundbank names, target platforms, and languages.  
If unsure, you can use `Windows` and `English(US)`, or call `get_project_info` to discover valid platforms and languages.

**Example prompts**

- “Generate the `MainGame` soundbank for platform `Windows` and language `English(US)`.”
- “Generate soundbanks `Footsteps_SB` and `Weapons_SB` for `Windows` and `English(US)`.”
- “Rebuild all soundbanks we’ve just included objects into for `Windows` / `English(US)`.”

---

### `get_project_info`

**Description**  
Retrieves Wwise project metadata, including available platforms and languages.

**Example prompts**

- “Get project info so we can see which platforms and languages are available.”
- “List all platforms and languages configured in this Wwise project.”
- “Show me the project metadata, including active platforms.”

---

### `get_all_audio_files_at_path_on_file_explorer`

**Description**  
Lists all audio files under a given folder in the file system (e.g. `C:\Audio`).

**Example prompts**

- “List all audio files under `C:\GameAudio\Imports`.”
- “Show me all WAV files inside `/Users/Me/Audio/Footsteps`.”
- “Gather all audio file paths under `D:\SFX\Weapons` so we can import them.”

---

### `set_object_property`

**Description**  
Sets a property value on a Wwise object given its path and property name. The value can be an int, bool, or string (depending on the property).

**Example prompts**

- “Set the `Volume` property of `\Actor-Mixer Hierarchy\SFX\Footsteps\Footstep_Stone` to -3 dB.”
- “Turn `Mute` on for `\Actor-Mixer Hierarchy\SFX\Ambience\City`.”
- “Set the `IsGlobal` property of this RTPC to `True`.”

---

### `add_effect_to_object`

**Description**  
Insert an Effect or Effect ShareSet reference into the `@Effects` list of a Bus, Actor-Mixer, or Sound via `ak.wwise.core.object.set`. WAAPI has no insert-at-index; supply the full ordered list with `list_mode='replaceAll'` if specific slot ordering is required.

**Arguments**

- `object_path: str` — Path or GUID of the host object (Bus / Actor-Mixer / Sound).
- `effect_ref: str` — Path or GUID of an existing Effect or ShareSet to insert.
- `list_mode: str = 'append'` — `'append'` adds a new EffectSlot at the end; `'replaceAll'` replaces the entire `@Effects` list with the supplied entry.

**Example prompts**

- “Append the `\Effects\Default Work Unit\Spatializers\SteamAudio` ShareSet to the `\Master-Mixer Hierarchy\Master Audio Bus\SFX` bus's effect chain.”
- “Replace all effects on `\Actor-Mixer Hierarchy\SFX\Ambience` with the `\Effects\Default Work Unit\Reverbs\RoomReverb` ShareSet (`list_mode='replaceAll'`).”

---

### `create_effect_share_set`

**Description**
Creates a new Effect ShareSet (Custom Effect) under a parent Work Unit or folder via `ak.wwise.core.object.set`. Plug-in `classId` values are defined by the Wwise plug-in (see WAAPI `wobjects_index`); the caller supplies the value. Pairs with `add_effect_to_object` (introduced in a separate PR) for attaching the new ShareSet to a Bus or Actor-Mixer; until that command lands in the same branch, attachment must be performed by other means.

**Arguments**

- `parent_path: str` — Project path of the parent Work Unit or folder (typically under `\Effects\Default Work Unit`).
- `name: str` — Name of the new ShareSet.
- `class_id: int` — Plug-in classId (WAAPI unsigned 32-bit range `[0, 0xFFFFFFFF]`).
- `properties: dict | None` — Optional initial property values; each key becomes an `@<Key>` accessor on the new Effect.
- `on_name_conflict: str = 'rename'` — One of `'fail' | 'rename' | 'replace' | 'merge'`.

**Returns**

The created ShareSet, unwrapped from the WAAPI response: `{"id": "<guid>", "name": "<resolved name>", "path": "<project path>", "type": "Effect"}` (fields requested via `options.return`). The raw WAAPI response nests the new ShareSet at `response["objects"][0]["children"][0]`; this wrapper unwraps it so the plan executor's `$last.id` / `$last.path` resolve directly to the new ShareSet.

**Example prompts**

- “Create a Steam Audio Spatializer Effect ShareSet named `SteamAudio_Spatializer` under `\Effects\Default Work Unit\Spatializers` with `class_id=<plug-in classId>`.”
- “Create a Wwise Reverb ShareSet named `RoomReverb` under `\Effects\Default Work Unit\Reverbs`.”

---

### `set_plugin_property`

**Description**
Set an Effect plug-in property via `ak.wwise.core.object.set` using the `@<PropertyName>` accessor. The older `setProperty` endpoint silently rejects plug-in-defined properties (Steam Audio Spatializer `Reflections` / `Pathing` / `AirAbsorption` / `Occlusion` / `Transmission`, Wwise Reverb plug-in params, etc.); this tool routes through `object.set` so those writes actually persist. Built-in object properties continue to be set via `set_object_property`.

**Arguments**

- `object_path: str` — Project path or GUID of the object whose property is being set.
- `property_name: str` — WAAPI property name *without* the leading `@` (e.g. `'Reflections'`). The wrapper adds the `@` prefix.
- `value: int | bool | float | str` — New value. `None` is rejected.
- `platform: str | None` — Optional platform unique name or GUID. When omitted, the change applies to all linked platforms.

**Example prompts**

- “Set the Steam Audio Spatializer `Reflections` toggle on the `\Effects\Default Work Unit\Spatializers\SteamAudio` ShareSet to `False`.”
- “Set the `AirAbsorption` plug-in property of the `SteamAudio_Spatializer` ShareSet to `True`.”

---

### `retrieve_selected_objs`

**Description**  
Retrieves whatever objects are currently selected in the Wwise Authoring UI.

**Example prompts**

- “Get the currently selected objects in Wwise.”
- “Use the objects I have selected in Wwise as the target for the next operation.”
- “Retrieve the selected objects and show me their paths.”

---

### `unregister_gameobject`

**Description**  
Unregisters (removes) a game object from the Wwise sound engine by name.

**Example prompts**

- “Unregister the `TempEmitter` game object.”
- “Remove all temporary debug game objects with names starting with `Debug_`.”
- “Unregister `RainEmitter_01` from the current session.”

---

### `toggle_layout`

**Description**  
Switches the current Wwise layout to a requested layout.  
Valid layouts: `Designer`, `Profiler`, `Soundbank`, `Mixer`, `Audio Object Profiler`, `Voice Profiler`, `Game Object Profiler`.

**Example prompts**

- “Switch Wwise to the `Profiler` layout.”
- “Toggle the layout to `Game Object Profiler` so I can inspect my game objects.”
- “Change to the `Soundbank` layout.”

---

### `get_all_property_name_and_valid_value_types`

**Description**  
Returns a help string listing WAAPI property identifiers and valid value types for a given Wwise object type.

**Example prompts**

- “Show me all valid property names and types for a Sound object.”
- “List the WAAPI properties and valid value types for an Event.”
- “Give me a reference of all properties I can set on a Bus.”

---
